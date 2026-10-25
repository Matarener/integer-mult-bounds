#!/usr/bin/env python3
"""Independent check of #4279's depth-four count-vector classification, m = 2..5, in a bounded box.

R(n) is the set of products of positive words with exactly n_l calls l in the lower unitriangular
group mod m (call l adds row l-1, with its diagonal 1, to row l). Its adjacent entries are n_l mod m,
so R(n) lives on the six other entries. R(n) = union_l g_l R(n - e_l). A count vector is attained for
residue c when I + c E[4][0] lies in R(n). This file runs that recursion in Python for m = 2, 3 and
checks the recorded runs of countdp.c (local evidence) for m = 4, 5, all with entries <= 3m.
No code from #4279.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
FREE = [(2, 0), (3, 0), (3, 1), (4, 0), (4, 1), (4, 2)]
P = {2: {(2, 4, 4, 2)}, 3: {(3, 3, 9, 3), (3, 6, 6, 3), (3, 9, 3, 3)}, 4: {(4, 4, 8, 4), (4, 8, 4, 4)},
     5: {(10, 5, 5, 5), (5, 10, 5, 5), (5, 5, 10, 5), (5, 5, 5, 10)}}   # #4279's stated P(m)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def attained(m, B):
    """{c: set of count vectors n in [0, B]^4 with I + c E[4][0] in R(n)}"""
    R = {(0, 0, 0, 0): {(0,) * 6}}
    for n in sorted(product(range(B + 1), repeat=4), key=sum)[1:]:
        out = set()
        for l in range(1, 5):
            if not n[l - 1]:
                continue
            p = tuple(v - (k == l - 1) for k, v in enumerate(n))
            adj = {k: p[k - 1] % m for k in range(1, 5)}
            for f in R[p]:
                a = dict(zip(FREE, f))
                for k in range(1, 5):
                    a[k, k - 1] = adj[k]
                for j in range(l - 1):
                    a[l, j] = (a[l, j] + a[l - 1, j]) % m
                out.add(tuple(a[cell] for cell in FREE))
        R[n] = out
    res = {}
    for c in range(1, m):
        t = tuple(c if cell == (4, 0) else 0 for cell in FREE)
        res[c] = {n for n, S in R.items() if all(v % m == 0 for v in n) and t in S}
    return res


def check_classification(m, B, by_c):
    box = [n for n in product(range(0, B + 1, m), repeat=4)]
    dominating = {n for n in box if any(all(a >= b for a, b in zip(n, p)) for p in P[m])}
    for c, S in by_c.items():
        minimal = {v for v in S if not any(w != v and all(a <= b for a, b in zip(w, v)) for w in S)}
        need(minimal == P[m], f"m={m} c={c}: minimal attained vectors are #4279's P(m)")
        need(S == dominating, f"m={m} c={c}: attained iff multiples of m dominating P(m)")


def main():
    # Python recursion for m = 2, 3
    python = {m: attained(m, 3 * m) for m in (2, 3)}
    for m, by_c in python.items():
        check_classification(m, 3 * m, by_c)

    # recorded runs of countdp.c for m = 4, 5 (and 2, 3 as cross-checks)
    text = (HERE / "evidence/COUNTDP-RUNS.txt").read_text()
    need(f"countdp.c (SHA256 {hashlib.sha256((HERE / 'countdp.c').read_bytes()).hexdigest()})" in text, "runs recorded for this countdp.c")
    runs = {}
    for line in text.splitlines():
        if line.startswith("M="):
            f = dict(kv.split("=") for kv in line.split())
            runs.setdefault((int(f["M"]), int(f["B"])), {}).setdefault(int(f["c"]), set()).add(tuple(map(int, f["n"].split(","))))
    need(set(runs) == {(m, 3 * m) for m in (2, 3, 4, 5)}, "runs for m = 2..5 at B = 3m")
    for m in (2, 3):
        need(runs[m, 3 * m] == python[m], f"C and Python agree at m={m}")
    for m in (4, 5):
        need(set(runs[m, 3 * m]) == set(range(1, m)), f"every residue recorded at m={m}")
        check_classification(m, 3 * m, runs[m, 3 * m])

    # the stated cheapest bills, from P(m), at random positive rational prices
    rng = random.Random(4279)
    for _ in range(2000):
        p = [Q(rng.randint(1, 50), rng.randint(1, 9)) for _ in range(4)]
        S = sum(p)
        bill = {m: min(sum(a * b for a, b in zip(v, p)) for v in P[m]) for m in P}
        need(bill[2] == 2 * S + 2 * (p[1] + p[2]) and bill[3] == 3 * S + 6 * min(p[1], p[2])
             and bill[4] == 4 * S + 4 * min(p[1], p[2]) and bill[5] == 5 * S + 5 * min(p), "cheapest bills")
    need({m: min(map(sum, P[m])) for m in P} == {2: 12, 3: 18, 4: 20, 5: 25}, "unit-price lengths 12, 18, 20, 25")

    print(json.dumps({
        "status": "PASS_DEPTH4_COUNT_VECTORS_CHECK",
        "box": "entries <= 3m",
        "python_m": [2, 3], "c_recorded_m": [2, 3, 4, 5],
        "P": {str(m): sorted(v) for m, v in P.items()},
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
