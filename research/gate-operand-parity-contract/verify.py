#!/usr/bin/env python3
"""Gate-operand parity contract: when do the symbolic checker's gate operator and
the exporter's sequential-ADD lowering agree?

Two pinned operators act on one gate `(d, srcs)` over registers 0..n-1:

- Sym (pinned xcheck_p.py `run`): `acc = XOR(val[s] for s in srcs)` reading
  pre-gate values, then `val[d] ^= acc`.
- Exp (pinned export_records.py `run`): one `ADD(d, s)` per listed source,
  replayed sequentially over current values: `val[d] ^= val[s]` per step.

Both are linear maps over F2^n (no constant term), so agreement on the register
basis is functional agreement for every valuation. This verifier:

1. simulates both operators on the basis valuation and on additive probes,
2. checks them against an independent coefficient-level algebraic prediction,
3. exhaustively classifies gates on n = 6 registers, source lists of length
   0..4 (9330 (d, srcs) pairs; dest-free subset 4686) and an extended
   length 0..5 domain (55986 pairs),
4. compares four candidate export-time guards for soundness and over-rejection,
5. scans the pinned selected tuned word's full gate inventory (blast radius),
6. binds the two operators' decisive source lines and file hashes.

No new kappa, no production adoption, no native backend, no frozen file change.
Standard library only. Read-only: writes nothing.
"""
import gzip
import hashlib
import json
import sys
from collections import Counter

WORD_PATH = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER_PATH = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER_PATH = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
WORD_SHA256 = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
CHECKER_SHA256 = "af3decc877e27c00001cf56f50c6c09566e8e101297ab34c7860aed96a06d80e"
EXPORTER_SHA256 = "8a5999601f917dbb492bb9ae9a344611f18cc7cedc53dc3c76496a369e530eb3"
EXPECTED_TOTAL_GATES = 5472
EXPECTED_V = 111
EXPECTED_R = 439
# Cross-check constant published by the gate-operand-export-parity package
# (PR 3696): destination-free agreement count on the same n=6, L<=4 domain.
EXPECTED_PRIOR_DEST_FREE = 4686
N = 6
MAX_LEN_MAIN = 4
MAX_LEN_EXT = 5


def need(cond, msg):
    if not cond:
        raise SystemExit("FAIL: " + msg)


def sym_final(d, srcs, x):
    """Symbolic checker operator: accumulate pre-gate XOR, then write once."""
    acc = 0
    for s in srcs:
        acc ^= x[s]
    y = list(x)
    y[d] ^= acc
    return y


def exp_final(d, srcs, x):
    """Exporter operator: one sequential ADD(d, s) per source, re-reading values."""
    y = list(x)
    for s in srcs:
        y[d] ^= y[s]
    return y


def basis(n):
    return [1 << r for r in range(n)]


def agree_sim(d, srcs, n):
    """Functional agreement measured on the register basis (both maps linear)."""
    x = basis(n)
    return sym_final(d, srcs, x)[d] == exp_final(d, srcs, x)[d]


def predict_agree(d, srcs):
    """Independent algebraic prediction (coefficient argument, all n).

    With m = multiplicity of d and k = index of its last occurrence:
    Sym's d-coefficient is 1 ^ (m mod 2); Exp's is 0 once d occurs (the last
    self-ADD annihilates the destination). Sym's r-coefficient (r != d) is
    occ(r) mod 2; Exp's is (occ(r) ^ pre_k(r)) mod 2, where pre_k counts
    occurrences of r before position k. Agreement forces m odd and every
    pre_k count even.
    """
    m = srcs.count(d)
    if m == 0:
        return True
    k = len(srcs) - 1 - srcs[::-1].index(d)
    pre = Counter(srcs[:k])
    if m % 2 == 0:
        return False
    return all(c % 2 == 0 for c in pre.values())


def linear_probe(d, srcs, n, trials=24):
    """Control: both operators must be linear on F2^n (f(0) = 0, additive)."""
    z = [0] * n
    rng = 123456789
    for _ in range(trials):
        x = [(rng >> (r % 7)) & 1 for r in range(n)]
        w = [((rng >> (r % 5)) & 1) ^ ((rng >> (r % 3)) & 1) for r in range(n)]
        xz = [a ^ b for a, b in zip(x, w)]
        for op in (sym_final, exp_final):
            fx, fw, fxz = op(d, srcs, x), op(d, srcs, w), op(d, srcs, xz)
            need(op(d, srcs, z) == z, "operator has a constant term: %s" % op.__name__)
            need(all((a ^ b) == c for a, b, c in zip(fx, fw, fxz)),
                 "operator not additive: %s on gate (%d, %s)" % (op.__name__, d, srcs))
        rng = (rng * 1103515245 + 12345) & 0xFFFFFFFF


def census(n, max_len):
    """Exhaustive (d, srcs) classification: simulate vs algebraic prediction."""
    rows = []
    for d in range(n):
        for length in range(max_len + 1):
            for i in range(n ** length):
                srcs, t = [], i
                for _ in range(length):
                    srcs.append(t % n)
                    t //= n
                sim = agree_sim(d, srcs, n)
                pred = predict_agree(d, srcs)
                need(sim == pred,
                     "simulation and algebraic prediction disagree on (%d, %s)" % (d, srcs))
                rows.append((d, tuple(srcs), sim))
    return rows


def guard_report(rows, name, accept):
    accepted = [r for r in rows if accept(r[0], r[1])]
    divergent_admitted = [r for r in accepted if not r[2]]
    agreeing_rejected = [r for r in rows if r[2] and not accept(r[0], r[1])]
    smallest = min(agreeing_rejected, key=lambda r: (len(r[1]), r[1])) if agreeing_rejected else None
    dest_free_rejected = [r for r in agreeing_rejected if r[0] not in r[1] and r[1]]
    smallest_df = (min(dest_free_rejected, key=lambda r: (len(r[1]), r[1]))
                   if dest_free_rejected else None)
    return {
        "guard": name,
        "accepted": len(accepted),
        "divergent_admitted": len(divergent_admitted),
        "agreeing_rejected": len(agreeing_rejected),
        "smallest_agreeing_rejected": None if smallest is None else [smallest[0], list(smallest[1])],
        "smallest_agreeing_dest_free_rejected":
            None if smallest_df is None else [smallest_df[0], list(smallest_df[1])],        "sound": len(divergent_admitted) == 0,
    }


def guard_full_distinct(d, srcs):
    return srcs and len({d, *srcs}) == len(srcs) + 1


def guard_distinct_only(d, srcs):
    return len({d, *srcs}) == len(srcs) + 1


def guard_dest_free(d, srcs):
    return d not in srcs


def guard_srcs_simple(d, srcs):
    return len(set(srcs)) == len(srcs)


def bind_source_lines():
    with open(CHECKER_PATH, "rb") as f:
        checker = f.read()
    with open(EXPORTER_PATH, "rb") as f:
        exporter = f.read()
    need(hashlib.sha256(checker).hexdigest() == CHECKER_SHA256, "checker hash mismatch")
    need(hashlib.sha256(exporter).hexdigest() == EXPORTER_SHA256, "exporter hash mismatch")
    text = checker.decode()
    need("len(set(regs)) == len(regs) and srcs" in text, "checker operand contract line not found")
    need("acc ^= val[s]" in text and "val[d] ^= acc" in text, "checker accumulate-then-write lines not found")
    etext = exporter.decode()
    need("for s in srcs: rec.append((1,d,s,1,f,ph))" in etext, "exporter per-source ADD line not found")
    return True


def scan_selected_word():
    with gzip.open(WORD_PATH, "rt") as f:
        c = json.load(f)
    with open(WORD_PATH, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    need(digest == WORD_SHA256, "pinned word hash mismatch")
    need(c["v"] == EXPECTED_V and c["R"] == EXPECTED_R, "word v/R mismatch")
    total = distinct_ok = dest_free = srcs_simple = 0
    worst = None
    for name in ("D", "A", "B", "C"):
        for f_, d, srcs in c[name]:
            total += 1
            ok = guard_full_distinct(d, srcs)
            distinct_ok += ok
            dest_free += d not in srcs
            srcs_simple += guard_srcs_simple(d, srcs)
            if worst is None or len(srcs) < len(worst[2]):
                worst = (name, (d, list(srcs)), list(srcs))
    need(total == EXPECTED_TOTAL_GATES, "selected gate inventory mismatch: %d" % total)
    simple_rows = all(len(set(row)) == len(row) for row in c["scatter"])
    return {
        "gates_total": total,
        "gates_distinct_operands": distinct_ok,
        "gates_dest_free": dest_free,
        "gates_srcs_simple": srcs_simple,
        "v": c["v"],
        "R": c["R"],
        "scatter_rows_simple": simple_rows,
        "scatter_rows": len(c["scatter"]),
        "scatter_terms": sum(len(r) for r in c["scatter"]),
        "retained_totals": len(c["ret"]),
    }


def main():
    bind_source_lines()
    linear_probe(0, [1, 2, 1], N)
    linear_probe(3, [3, 0, 0, 3, 5], N)

    rows = census(N, MAX_LEN_MAIN)
    dest_free_rows = [r for r in rows if r[0] not in r[1]]
    need(len(dest_free_rows) == EXPECTED_PRIOR_DEST_FREE,
         "dest-free domain count %d does not match the published census %d"
         % (len(dest_free_rows), EXPECTED_PRIOR_DEST_FREE))
    need(all(r[2] for r in dest_free_rows), "a destination-free gate diverges")
    divergent = [r for r in rows if not r[2]]
    agreeing_dest_in = [r for r in rows if r[2] and r[0] in r[1]]

    ext = census(N, MAX_LEN_EXT)
    ext_dest_free = [r for r in ext if r[0] not in r[1]]
    need(all(r[2] for r in ext_dest_free), "extended domain: a destination-free gate diverges")
    ext_divergent = [r for r in ext if not r[2]]

    guards = [
        guard_report(rows, "checker_contract", guard_full_distinct),
        guard_report(rows, "distinct_only", guard_distinct_only),
        guard_report(rows, "dest_free", guard_dest_free),
        guard_report(rows, "srcs_simple_transplant", guard_srcs_simple),
        guard_report(rows, "exact", predict_agree),
    ]
    need(guards[0]["sound"] and guards[1]["sound"] and guards[2]["sound"] and guards[4]["sound"],
         "a soundness expectation failed")
    need(not guards[3]["sound"], "transplanted srcs-simple guard unexpectedly sound")
    need(guards[4]["agreeing_rejected"] == 0, "exact guard rejects an agreeing gate")
    need(guards[0]["agreeing_rejected"] > 0, "checker contract unexpectedly rejects nothing agreeing")
    smallest = guards[0]["smallest_agreeing_rejected"]
    need(smallest == [smallest[0], []],
         "smallest agreeing checker-rejected gate is not the empty source list")
    smallest_df = guards[0]["smallest_agreeing_dest_free_rejected"]
    need(smallest_df is not None and len(smallest_df[1]) == 2
         and smallest_df[1][0] == smallest_df[1][1] and smallest_df[1][0] != smallest_df[0],
         "smallest agreeing dest-free checker-rejected gate is not the [a,a] duplicate pair")

    word = scan_selected_word()
    need(word["gates_distinct_operands"] == word["gates_total"],
         "selected word carries a non-distinct-operand gate")
    need(word["scatter_rows_simple"], "selected word scatter rows are not simple supports")

    result = {
        "domain_n": N,
        "domain_max_len": MAX_LEN_MAIN,
        "domain_pairs": len(rows),
        "dest_free_pairs": len(dest_free_rows),
        "dest_free_agree": len(dest_free_rows),
        "dest_in_pairs": len(rows) - len(dest_free_rows),
        "divergent_pairs": len(divergent),
        "agreeing_dest_in_pairs": len(agreeing_dest_in),
        "extended_pairs": len(ext),
        "extended_divergent": len(ext_divergent),
        "guards": guards,
        "selected_word": word,
        "no_new_kappa": True,
    }
    print(json.dumps(result, sort_keys=True))
    print("PASS_GATE_OPERAND_PARITY_CONTRACT "
          "domain={domain_pairs} dest_free_agree={dest_free_pairs} "
          "dest_in={dest_in_pairs} divergent={divergent_pairs} "
          "agreeing_dest_in={agreeing_dest_in_pairs} "
          "checker_sound=true checker_over_rejects={over} "
          "transplant_admits={tp} exact_over_rejects=0 "
          "selected_gates={sg} selected_distinct={sd} no_new_kappa".format(
              domain_pairs=len(rows),
              dest_free_pairs=len(dest_free_rows),
              dest_in_pairs=len(rows) - len(dest_free_rows),
              divergent_pairs=len(divergent),
              agreeing_dest_in_pairs=len(agreeing_dest_in),
              over=guards[0]["agreeing_rejected"],
              tp=guards[3]["divergent_admitted"],
              sg=word["gates_total"],
              sd=word["gates_distinct_operands"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
