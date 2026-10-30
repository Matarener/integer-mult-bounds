#!/usr/bin/env python3
"""Exact PR3734 invoice reconstruction and conditional consumer budgets.

The attached rollout retains PR3734's literal published profile and two exact
outer-engine hashes, subsequently compared with the retrieved live package.
This script audits that numerical record. It does not itself replay the now
available physical owner allocation or admit a changed word.

SPDX-License-Identifier: Apache-2.0
Substantial OpenAI Codex assistance under user direction, October 2026.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

if not __debug__:
    raise RuntimeError("Assertions must be enabled")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENGINE = ROOT / "research/complex-local-word-ceiling/ceiling.py"
sp = importlib.util.spec_from_file_location("retained_ceiling", ENGINE)
C = importlib.util.module_from_spec(sp)
sp.loader.exec_module(C)

M, T, W, CALLS = 73, 360, 322560, 3240
BASE = {1: 7990332, 2: 2349000, 3: 748971, 4: 330480,
        5: 69479, 8: 25920, 32: 1, 48: 137911}
LOCAL = {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}
WIDTHS = {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}
BIT = {1: 381024, 2: 400416, 3: 22752, 4: 26880,
       5: 29376, 6: 17376, 7: 26784, 42: 288}
BASE_LO = Q("0.001730448360207635461740")
TARGET = Q("0.001730578437266246818740")
BIT_LO = Q("0.001733427039589844234749")
R437_REPORTED = Q("0.001736628253427115480286")
GRID = Q(1, 10**24)


def decimal(q, digits=65):
    with localcontext() as ctx:
        ctx.prec = digits
        return str(Decimal(q.numerator) / Decimal(q.denominator))


def interval(lo, hi):
    assert lo <= hi
    return {"rational": [str(lo), str(hi)],
            "decimal": [decimal(lo), decimal(hi)]}


@lru_cache(None)
def cost(r, m, a):
    return C.child_cost(r, m, a)


def weighted(terms, m, a):
    """Outward interval for sum of signed rational multiples of child costs."""
    lo = hi = Q(0)
    for rank, multiplicity in terms.items():
        v = cost(rank, m, a)
        if multiplicity >= 0:
            lo += multiplicity * v[0]
            hi += multiplicity * v[1]
        else:
            lo += multiplicity * v[1]
            hi += multiplicity * v[0]
    return C.down(lo), C.up(hi)


def moment(profile, m, w, a, bad=False):
    lo, hi = weighted(profile, m, a)
    lo /= w
    hi /= w
    if bad:
        # PR589's retained complete fallback: m^a * 32 m (#children)/(10^16 W).
        p = Q(32 * m * sum(profile.values()), 10**16 * w)
        c1 = cost(1, m, a)
        lo += p * m * c1[0]
        hi += p * m * c1[1]
    return C.down(lo), C.up(hi)


def residual(profile, a, m=M, w=W, bad=False):
    lo, hi = moment(profile, m, w, a, bad)
    return interval(lo - 1, hi - 1)


def root_bracket(profile, m=M, w=W, bad=False):
    """Decimal proposes the bracket; rational enclosures prove both signs."""
    with localcontext() as ctx:
        ctx.prec = 85
        terms = [(Decimal(r*n)/Decimal(m*w), (Decimal(m)/r).ln())
                 for r, n in profile.items() if n]
        fallback = (Decimal(32*m*sum(profile.values())) / Decimal(10**16*w)
                    if bad else Decimal(0))
        lm = Decimal(m).ln()
        lo, hi = Decimal(0), Decimal("0.05")
        for _ in range(250):
            a = (lo + hi) / 2
            v = sum(p*(a*l).exp() for p, l in terms) + fallback*(a*lm).exp()
            if v < 1:
                lo = a
            else:
                hi = a
        q = int(lo * 10**24)
    lower, upper = Q(q, 10**24), Q(q+1, 10**24)
    ml = moment(profile, m, w, lower, bad)
    mu = moment(profile, m, w, upper, bad)
    assert ml[1] < 1 < mu[0]
    return {"lower": str(lower), "upper": str(upper),
            "decimal": [decimal(lower), decimal(upper)],
            "lower_residual": interval(ml[0]-1, ml[1]-1),
            "upper_residual": interval(mu[0]-1, mu[1]-1)}


def quotient_positive(num, den):
    assert num[0] > 0 and den[0] > 0
    return num[0]/den[1], num[1]/den[0]


def consumer_budget(a):
    """Assume every call saves 8 H8 and pays 8 H1; all inherited costs remain.

    The resulting allowance prices *additional* complete terminal work per
    nine-stage replica. It includes the baseline's deficit at the same a.
    The hypothesis supplies no legal implementation of that terminal work.
    """
    existing = weighted(BASE, M, a)
    saving = weighted({8: 72, 1: -72}, M, a)
    budget = ((W-existing[1])/T + saving[0],
              (W-existing[0])/T + saving[1])
    c1, c7, c8 = (cost(r, M, a) for r in (1, 7, 8))
    assert budget[0] > 0
    h1_units = quotient_positive(budget, c1)
    allowed_h7 = quotient_positive(budget, c7)
    allowed_h8 = quotient_positive(budget, c8)
    out = {"a": str(a), "baseline_residual": residual(BASE, a),
           "maximum_added_H1_per_replica": interval(*h1_units),
           "maximum_added_H7_per_replica": interval(*allowed_h7),
           "maximum_added_H8_per_replica": interval(*allowed_h8),
           "maximum_average_H1_units_at_69_75_fields": interval(
               h1_units[0]/Q(279, 4), h1_units[1]/Q(279, 4)),
           "conditional_terminal_controls": {}}
    changed = dict(BASE)
    changed[8] -= 8*CALLS
    changed[1] += 8*CALLS
    for name, rank, fields in [
            ("70_H8_fields", 8, 70), ("71_H7_fields", 7, 71),
            ("72_H7_fields", 7, 72), ("70_H7_fields", 7, 70),
            ("trace_lower_69_75_H8_fields", 8, Q(279, 4))]:
        h = Counter(changed)
        h[rank] += fields*T
        v = moment(h, M, W, a)
        out["conditional_terminal_controls"][name] = {
            "moment_minus_one": interval(v[0]-1, v[1]-1),
            "passes_invoice": v[1] < 1,
            "construction_status": "hypothetical invoice only"}
    one_call = weighted({8: 8, 1: -8}, M, a)
    # Minimum number of wholly changed calls if every consumer cost is zero.
    delta = (existing[0]-W, existing[1]-W)
    if delta[0] > 0:
        out["free_consumer_minimum_changed_calls"] = interval(
            *quotient_positive(delta, one_call))
    return out


def reconstruct_outer():
    """Run the two byte-matching published engines with reconstructed data."""
    work = HERE / "reconstructed-outer"
    (work/"new").mkdir(exist_ok=True)
    data = {"geometry": {"dimension": M, "replicas": T},
            "outer_refinement": {"endpoint_digits": 24},
            "expected": {"complex_lower": str(BASE_LO),
                         "global_profile": BASE, "live": W,
                         "kappa": "0.001730418899766071163804"}}
    b = BASE_LO - Q(1, 10**104)
    bj = {"b": str(b), "b_above_endpoint": str(BASE_LO+GRID),
          "live": W, "profile": BASE}
    (work/"new/SPEC.json").write_text(json.dumps(data, indent=2)+"\n")
    (work/"CLAIM.json").write_text(json.dumps({
        "status": "reconstructed arithmetic input, not a supplier admission",
        "source": "PR3734 proof as retained in attached rollout",
        "complex_lower": str(BASE_LO)}, indent=2)+"\n")
    (work/"outer/B.json").write_text(json.dumps(bj, indent=2)+"\n")
    runs = []
    for name in ["check_ledger.py", "independent_check.py"]:
        result = subprocess.run([sys.executable, "-B", str(work/"outer"/name)],
                                text=True, capture_output=True)
        (work/f"{name}.log").write_text(result.stdout+result.stderr)
        assert result.returncode == 0, result.stderr
        runs.append({"engine": name, "exit_code": result.returncode,
                     "sha256": hashlib.sha256((work/"outer"/name).read_bytes()).hexdigest()})
    ledger = json.loads((work/"outer/LEDGER.json").read_text())
    row = ledger["rows"]["struct_boundary_radix_union"]
    got = Q(row["kappa"]["rational"])
    expected = BASE_LO-Q(1, 10**46)-Q(1, 10**70)
    assert got == expected
    independent = json.loads((work/"outer/INDEPENDENT.json").read_text())
    assert Q(independent["rows"]["struct_boundary_radix_union"]["kappa"]) == expected
    return {"status": "both exact inherited engines pass reconstructed arithmetic",
            "source_binding": "engine bytes match PR3734 hashes captured in rollout line 601",
            "data_binding": "reconstructed, not recovered original SPEC/B bytes",
            "kappa": str(got), "kappa_decimal": decimal(got, 110),
            "strict_checks": len(row["strict_checks"]),
            "rejection_controls": len(ledger["rejecting_controls"]["struct_boundary_radix_union"]),
            "runs": runs}


def main():
    assert W == 896*T and CALLS == 9*T
    assert sum(WIDTHS.values()) == 408
    assert CALLS*sum(WIDTHS.values()) == 1321920
    assert sum(r*n for r, n in LOCAL.items()) == 5134
    idle = Counter(BASE)
    idle.subtract({r: CALLS*n for r, n in LOCAL.items()})
    assert dict(sorted((r,n) for r,n in idle.items() if n)) == {
        1: 84732, 3: 23211, 5: 4679, 32: 1, 48: 137911}
    assert sum(r*n for r,n in BASE.items()) == 23431680
    assert sum(r*n for r,n in BASE.items()) == 72*W+64*CALLS
    base_root = root_bracket(BASE)
    assert Q(base_root["lower"]) == BASE_LO
    bit_root = root_bracket(BIT, 64, 28416, True)
    assert Q(bit_root["lower"]) == BIT_LO
    assert moment(BASE, M, W, TARGET)[0] > 1
    changed = dict(BASE)
    changed[8] = 0
    changed[1] += 8*CALLS
    optimistic_root = root_bracket({r:n for r,n in changed.items() if n})
    out = {
        "status": "PASS_EXACT_INVOICE_RECONSTRUCTION_AND_CONDITIONAL_BUDGETS",
        "scope": "Arithmetic only; actual PR3734 sources were separately compared after retrieval, but this executable does not replay owners or admit a changed consumer",
        "sources": {
            "PR3734_head": "fa041037a3374eaa08feeca0b26a5d6893194147",
            "PR3682_head": "431e6c6023ef352c41696469de7fb614cd4ded8c",
            "PR3653_head": "607a09ff441c79b215a8127a81f4cc70021d0d9b",
            "PR3647_R437_head": "36ff441479ff9c7e70d83f0becccd44da50effb8",
            "PR3700_R437_audit_head": "aa0bd9fbc8700506b1fafcc55bca9bd32aced7d9",
            "interval_engine": str(ENGINE.relative_to(ROOT)),
            "interval_engine_sha256": hashlib.sha256(ENGINE.read_bytes()).hexdigest()},
        "PR3734": {"m": M, "replicas": T, "calls": CALLS, "live_families": W,
                   "physical_families_reported": 323069, "profile": BASE,
                   "local_profile": LOCAL, "width_inventory": WIDTHS,
                   "idle_profile": {r:n for r,n in sorted(idle.items()) if n},
                   "root": base_root},
        "target": {"a": str(TARGET),
                   "source_status": "PR3734 explicitly calls this an unattainable ideal packing diagnostic, not its achieved bound",
                   "above_actual_root_lower": str(TARGET-BASE_LO),
                   "baseline_moment_minus_one": residual(BASE, TARGET)},
        "bit": {"selected_profile_root": bit_root,
                "selected_profile_at_target": residual(BIT, TARGET, 64, 28416, True),
                "modern_complex_only_limit": str(BIT_LO),
                "maximum_gain_over_target": str(BIT_LO-TARGET),
                "maximum_percent_over_target": decimal(100*(BIT_LO/TARGET-1)),
                "R437_reported_limit": str(R437_REPORTED),
                "R437_status": "arithmetic use of reported audited endpoint; full R437 profile unavailable here",
                "R437_maximum_gain_over_target": str(R437_REPORTED-TARGET),
                "R437_maximum_percent_over_target": decimal(100*(R437_REPORTED/TARGET-1))},
        "zero_cost_consumer_optimistic_root": optimistic_root,
        "consumer_budgets": {"target": consumer_budget(TARGET),
                             "retained_bit_limit": consumer_budget(BIT_LO),
                             "reported_R437_limit": consumer_budget(R437_REPORTED)},
        "outer_reconstruction": reconstruct_outer(),
        "unrun_obligations": [
            "PR3734 literal source/native/helper-owner replay (actual source now available, not run by this arithmetic executable)",
            "eight intrinsic inverse-C_p repairs on modern native event sequences",
            "changed routed consumer and complete information/state contract",
            "changed cleanup, storage, precision and physical ownership costs",
            "full supplier admission and all-size/analytic theorem obligations"]}
    (HERE/"RESULT.json").write_text(json.dumps(out, indent=2)+"\n")
    print(out["status"])
    print("PR3734 root bracket:", *base_root["decimal"])
    print("Target baseline residual:", out["target"]["baseline_moment_minus_one"]["decimal"])
    print("Bit limit:", decimal(BIT_LO), "; target headroom:", decimal(BIT_LO-TARGET))
    print("Optimistic zero-consumer root:", *optimistic_root["decimal"])
    for name, budget in out["consumer_budgets"].items():
        print(name, "maximum H8:", budget["maximum_added_H8_per_replica"]["decimal"],
              "maximum H7:", budget["maximum_added_H7_per_replica"]["decimal"])
    print("Outer checks:", out["outer_reconstruction"]["strict_checks"],
          "; controls:", out["outer_reconstruction"]["rejection_controls"])


if __name__ == "__main__":
    main()
