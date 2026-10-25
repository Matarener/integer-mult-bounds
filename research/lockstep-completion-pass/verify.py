#!/usr/bin/env python3
"""Literal completion/splitting pass and nested owned-bank lifetimes in the lockstep compiler.

Standard library only.  Exit status 0 means every check passed; a JSON summary is printed
and compared with RESULT.json (regenerate with --write-result).  See README.md / PROOF.md.
"""
import json
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import counts as C  # noqa: E402
import executor as E  # noqa: E402

BINDINGS = {
    "research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md": [
        "Process a class in word order. At round `j`, suspend every unit of that",
        "One owned `C0` per recursion depth is therefore insufficient in general.",
        "or even per compiled unit instance. Retain each bank until its unit clears",
        "movement and erasure remain in the fixed scalar cost. A smaller reuse",
        "allocation requires its own lifetime proof.",
    ],
    "research/higher-moment-strictification/vendor/p7-TENSOR.md": [
        "has finished, apply the positive transform on axes K,...,L-1. The disjoint",
        "Replace each paid rank R>J by consecutive",
        "jobs on disjoint axes of ranks J,...,J,r where R=qJ+r and 0<=r<J.",
        "T = {5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224},",
        "P = {1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}.",
    ],
    "research/higher-moment-strictification/README.md": [
        "Never combine two different paid positions of the same suspended U copy.",
        "Take `C=0.00268648`, `c=10`, `b=15`, `u=3/10` and `v=150`.",
    ],
    "research/net-tax-rank-compiler/PROOF.md": [
        "T'_t-P'_t = T_t^v-P_t^v - sum_R tau(R) - sum_(K<L) E(K).       (1)",
    ],
    "research/lockstep-live-role-audit/live_roles.py": [
        "I1  units that are live in the same class hold pairwise distinct fields",
    ],
}

P7_T = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
P7_P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
P7_C = Fraction(268648, 10 ** 8)
BUDGET = 3_000_000

# event-level cases: (rule after the pass, N).  Full width is executed where the width is small
# (then the formula must match exactly); otherwise two lockstep copies run in partial mode and
# the formula is evaluated in the same partial mode.
def cases():
    out = [(E.toy(), n) for n in (7, 12, 16, 28)]
    roles, rounds = E.overlapping_toy()
    out += [(E.complete_and_split(E.RawRule("overlapping toy", roles, rounds), J=4, L=5), n) for n in (40, 64)]
    for seed in (0, 1):
        roles, rounds, nm = E.p7_shaped(seed)
        out.append((E.complete_and_split(E.RawRule(nm, roles, rounds), J=10, L=15), 1815))
    for seed, adv in ((0, None), (1, "centre"), (2, "one_owner")):
        roles, rounds, owned, nm = E.selected_shaped(seed, adversarial=adv)
        out.append((E.complete_and_split(E.RawRule(nm, roles, rounds, owned), J=20, L=21), 3045))
    # multi-generation regression with path-dependent class sizes and exit ranks (#5443 review)
    out += [(E.complete_and_split(E.RawRule("two ranks", (("a", 3), ("b", 5)), ((1, "C0"), (2, "C0"))), J=2, L=3), n)
            for n in (45, 69)]
    return out


def need(ok, msg):
    if not ok:
        raise SystemExit("FAIL: " + msg)


def selected_profile():
    inv = json.loads((ROOT / "research/coupled-helper-neutral-completion/reports/expected/invoice.json").read_text(encoding="utf-8"))
    fund = json.loads((ROOT / "research/coupled-helper-neutral-completion/reports/expected/funding.json").read_text(encoding="utf-8"))
    T = {int(k): v for k, v in inv["histograms"]["productive"].items()}
    P = {int(k): v for k, v in inv["histograms"]["paid"].items()}
    need(sum(T.values()) == 10928 and sum(P.values()) == 64260, "selected histogram totals")
    tup = fund["tuple"]
    need((tup["ambient"], tup["cutoff"], tup["floor"], tup["tensor_power"]) == (145, 20, 21, 1024), "selected compiler tuple")
    kappa = Fraction(fund["kappa"])
    return T, P, kappa


def histogram_section(name, T, P, c, b, Cs, powers=(1, 2, 3)):
    rows = {}
    for v in powers:
        Tv, Pv = C.product_histograms(Counter(T), Counter(P), v)
        J, L = c ** v, b ** v
        T2, P2, rec = C.pass_histograms(Tv, Pv, J, L)
        left, right = C.gap_identity(Tv, Pv, J, L, 1 - Cs)
        need(abs(left - right) < Fraction(1, 10 ** 40), f"{name} v={v}: net-tax identity (1)")
        need(C.mass(T2) - C.mass(P2) == C.mass(Tv) - C.mass(Pv), f"{name} v={v}: rank-one surplus preserved")
        need(C.mass(T2) - C.mass(Tv) == C.mass(P2) - C.mass(Pv) == sum(cnt * (L - k) for k, cnt in Tv.items() if k < L),
             f"{name} v={v}: completion adds equal target and paid mass")
        need(max(P2) <= J < L <= min(T2), f"{name} v={v}: separated after the pass")
        rows[f"v={v}"] = {"J": J, "L": L, "target_ranks_before_after": [len(Tv), len(T2)],
                          "paid_ranks_before_after": [len(Pv), len(P2)],
                          "rank_one_surplus": str(C.mass(T2) - C.mass(P2)),
                          "gap_t_moment": str(left)[:40], **{k: str(v_) for k, v_ in rec.items()}}
    return rows


def count_section(name, T, P, c, b, ranks, banks_per_unit=1):
    HR = C.passed_hist_rule(name, Counter(T), Counter(P), c, b, owned_banks=banks_per_unit)
    cc = C.Counts(HR)
    rows = {}
    for n in ranks:
        B, a, Pn, cost = cc.compile(n)
        F = cc.flow(n)
        tot, pk = cc.banks(n)
        rec = cc.records(n)
        need(pk <= tot, "peak at most total")
        rows[str(n)] = {"generations": F.G, "width_B_digits": len(str(B)), "P_over_B": float(Fraction(Pn, B)),
                        "units_per_copy": F.units_total, "peak_units_per_copy": F.peak_units,
                        "classes_per_copy": F.classes_total,
                        "banks_total_digits": len(str(tot)), "banks_peak_digits": len(str(pk)),
                        "total_over_peak": float(Fraction(tot, pk)),
                        "unit_instances_digits": len(str(rec["unit_instances"])),
                        "adapter_records_digits": len(str(rec["adapter_records"])),
                        "sha_of_exact": C.digest({"B": B, "a": a, "P": Pn, "total": tot, "peak": pk, **rec})}
    return {"passed_rule": {"types": HR.types, "W": HR.W, "rounds": HR.rounds_count,
                            "paid": dict(sorted(HR.paid.items())), **HR.pass_counts()}, "ranks": rows}


def main():
    write = "--write-result" in sys.argv
    t0 = time.time()
    for path, needles in BINDINGS.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for s in needles:
            need(s in text, f"binding in {path}: {s}")
    # 1. counting compilers agree (histogram-level vs #4691 unit-level) and reproduce the receipt
    rec = json.loads((ROOT / "research/kappa-rebuild/transfer-audit/FINITE-DAG-AUDIT.json").read_text())
    t40 = next(r for r in rec["synthetic_rule_tests"] if r["rank"] == 40)
    B, a, P, _ = C.Counts(E.toy()).compile(40)
    need((B, P) == (t40["width"], t40["leaves"]), "toy rank 40 width/leaves equal FINITE-DAG-AUDIT")
    sys.path.insert(0, str(ROOT / "research/lockstep-live-role-audit"))
    import live_roles as L  # noqa: E402
    for rule, ns in ((E.toy(), (4, 7, 12, 16, 28, 40, 64)), (L.bit_shaped(0), (50, 400, 3200))):
        r2 = rule if isinstance(rule, E.Rule) else E.Rule(rule.name, rule.roles, rule.rounds, rule.owned)
        for n in ns:
            need(C.Counts(r2).compile(n) == L.Compiler(rule).compile(n), f"counting parity {rule.name} N={n}")
    # 2. the pass on the complete profiles: identity (1), surplus, separation, record counts
    ST, SP, kappa = selected_profile()
    hist = {"p7 (c=10, b=15, C=0.00268648)": histogram_section("p7", P7_T, P7_P, 10, 15, P7_C),
            "selected #5413 (c=20, b=21, C=kappa)": histogram_section("selected", ST, SP, 20, 21, kappa)}
    # 3. event-level execution with the LIFO bank allocator; peak and records equal the formula
    rows = {}
    for rule, n in cases():
        try:
            r = E.audit(rule, n, owned_policy="stack", budget=BUDGET)
        except E.Violation as e:
            raise SystemExit(f"FAIL {rule.name} N={n}: {e}")
        cc = C.Counts(rule, executed=lambda m, cost: cost <= BUDGET)
        k = None if r["full_width_executed"] else r["executed_tree_copies"]
        tot, pk = cc.banks(n, copies=k)
        recs = cc.records(n, copies=k)
        need((r["peak_banks"], r["total_bank_allocations"]) == (pk, tot), f"{rule.name} N={n}: peak/total banks equal the formula")
        for key in ("adapter_records", "relocation_records", "piece_jobs", "completion_jobs", "orig_jobs", "bank_init_scans", "bank_erase_scans"):
            need(r.get(key, 0) == recs.get(key, 0), f"{rule.name} N={n}: {key} executed {r.get(key, 0)} != formula {recs.get(key, 0)}")
        need(r["units"] == recs["unit_instances"], f"{rule.name} N={n}: unit instances")
        rows[f"{rule.name} | N={n}"] = {k2: r.get(k2, 0) for k2 in ("generations", "width_B_log10", "executed_tree_copies", "full_width_executed",
                                                          "events", "peak_banks", "total_bank_allocations", "units",
                                                          "adapter_records", "relocation_records", "completion_jobs", "piece_jobs")}
    # 4. complete-profile counts at small top ranks
    cnt = {"p7 v=1 (J=10, L=15)": count_section("p7 v=1", P7_T, P7_P, 10, 15, (1815,)),
           "selected v=1 (J=20, L=21)": count_section("selected v=1", ST, SP, 20, 21, (3045,))}
    out = {"status": "PASS", "bindings": sum(map(len, BINDINGS.values())), "histograms": hist,
           "executed": rows, "counts": cnt}
    path = HERE / "RESULT.json"
    out = json.loads(json.dumps(out))      # JSON-normal form: tuples become lists, keys become strings
    if write:
        path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    else:
        stored = json.loads(path.read_text(encoding="utf-8"))
        need(stored == out, "RESULT.json differs from the fresh computation")
    print(json.dumps({**out, "seconds": round(time.time() - t0, 1)}, indent=1))


if __name__ == "__main__":
    main()
