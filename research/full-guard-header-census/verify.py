#!/usr/bin/env python3
"""Independent literal census of five full-guard header laws: #4259, #4261, #4273, #4274, #4275.

A header G in GL_m(F_q) passes a request R when the leading principal minors of G R G^-1 of
orders 1..rank(R) are nonzero. Each family is put in a canonical basis (the PRs prove the counts
are basis-independent). This file enumerates complete headers in Python for the small cases,
checks the recorded runs of headers.c (local evidence) for GL_5(F_2), GL_4(F_3), GL_3(F_4) and
GL_3(F_5), and compares every count with the PRs' stated closed forms, transfer law and laminar
product, implemented here from their statements. No code from those PRs.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def field(q):
    if q == 4:
        def mul(a, b):
            p = 0
            for i in range(2):
                if b >> i & 1:
                    p ^= a << i
            return p ^ 7 if p & 4 else p
        return (lambda a, b: a ^ b), mul, (lambda a: a)
    return (lambda a, b: (a + b) % q), (lambda a, b: a * b % q), (lambda a: (-a) % q)

def gl(q, n):
    r = 1
    for i in range(n):
        r *= q**n - q**i
    return r

def pair_transfer(q, m):
    """#4261 Theorem 1: C(q, m) from the 2x2 partial-Gram walk; passing headers = C |GL_(m-2)|"""
    add, mul, neg = field(q)
    mats = list(product(range(q), repeat=4))
    det = lambda A: add(mul(A[0], A[3]), neg(mul(A[1], A[2])))
    def w(A):
        if not any(A):
            return 2 * q * q - 1
        return 0 if det(A) else q - 1
    sub = lambda B, A: tuple(add(b, neg(a)) for a, b in zip(A, B))
    S = [A for A in mats if A[0] != 1 and A[3] != 1]
    f = {A: int(not any(A)) for A in S}
    for _ in range(m - 1):
        f = {B: sum(f[A] * w(sub(B, A)) for A in S if f[A]) for B in S}
    C = sum(f[A] * w(sub((1, 0, 0, 1), A)) for A in S)
    return C * gl(q, m - 2)

def F(q, n, s):
    k = len(s)
    if not k:
        return Q(1)
    num = 1
    for si in s: num *= q**si - 1
    return Q(num * ((q - 1)**k * q**(n - sum(s)) - (-1)**k), q**k * (q**n - 1))

def O(q, n, s):
    r = Q(1)
    for t in range(max(s, default=0)):
        r *= F(q, n - t, tuple(si - t for si in s if si > t))
    return r

closed = {
    "4261_binary": lambda m: Q(9**(m-1) - 2 * 7**(m-1) + 5**(m-1), 4 * (2**m - 1) * (2**m - 2) * 2**(2*m - 4)),
    "4273_ternary": lambda m: Q(4 * (49**(m-1) - 2 * 25**(m-1) + 19**(m-1)), 9 * (3**m - 1) * (3**m - 3) * 3**(2*m - 4)),
    "4274_binary": lambda m: Q(9**(m-1) - 5**(m-1), 4 * (2**m - 1) * (2**m - 2) * 2**(2*m - 4)),
    "4275_k3_binary": lambda m: Q(27**(m-1) - 6*21**(m-1) + 6*19**(m-1) - 6*17**(m-1) + 16*15**(m-1) - 18*13**(m-1) + 9*11**(m-1) - 2*9**(m-1), 64 * (2**m-1) * (2**m-2) * (2**m-4) * 2**(3*m-9)) if m >= 3 else None,
    "4259_laminar": lambda q, m: O(q, m, (2,)) * O(q, 2, (1,)),
    "4259_split": lambda q, m: O(q, m, (2,)) * O(q, 2, (1, 1)),
    "single": lambda q, m: O(q, m, (m - 1,)),
}


def census(q, m):
    """the counts headers.c prints, by a separate Python enumeration"""
    add, mul, neg = field(q)
    inv = {a: next(b for b in range(q) if mul(a, b) == 1) for a in range(1, q)}
    I = [[int(i == j) for j in range(m)] for i in range(m)]

    def matmul(x, y):
        out = []
        for i in range(m):
            row = []
            for j in range(m):
                s = 0
                for k in range(m):
                    s = add(s, mul(x[i][k], y[k][j]))
                row.append(s)
            out.append(row)
        return out

    def inverse(g):
        a = [row[:] + I[i][:] for i, row in enumerate(g)]
        for c in range(m):
            p = next((r for r in range(c, m) if a[r][c]), None)
            if p is None:
                return None
            a[c], a[p] = a[p], a[c]
            iv = inv[a[c][c]]
            a[c] = [mul(x, iv) for x in a[c]]
            for r in range(m):
                if r != c and a[r][c]:
                    f = neg(a[r][c])
                    a[r] = [add(x, mul(f, y)) for x, y in zip(a[r], a[c])]
        return [row[m:] for row in a]

    def passes(g, gi, r, rank):
        a = matmul(matmul(g, r), gi)
        for k in range(rank):
            if not a[k][k]:
                return False
            iv = inv[a[k][k]]
            for i in range(k + 1, m):
                if a[i][k]:
                    f = neg(mul(a[i][k], iv))
                    a[i] = [add(x, mul(f, y)) for x, y in zip(a[i], a[k])]
        return True

    def proj(cells):
        return [[int((i, j) in cells) for j in range(m)] for i in range(m)]

    def minus(r):
        return [[add(I[i][j], neg(r[i][j])) for j in range(m)] for i in range(m)]
    req = {f"P{t}": (minus(proj({(t, t)})), m - 1) for t in range(min(m, 4))}
    req["W"] = (minus(proj({(0, 0), (0, 1)})), m - 1)
    req["e1"], req["e2"], req["E12"] = (proj({(0, 0)}), 1), (proj({(1, 1)}), 1), (proj({(0, 0), (1, 1)}), 2)
    fam = {"one": ["P0"], "pair": ["P0", "P1"], "oneway": ["W", "P1"], "k3": ["P0", "P1", "P2"],
           "k4": ["P0", "P1", "P2", "P3"], "laminar": ["E12", "e1"], "split": ["E12", "e1", "e2"]}
    out = dict.fromkeys(["GL"] + list(fam), 0)
    for flat in product(range(q), repeat=m * m):
        g = [list(flat[i * m:(i + 1) * m]) for i in range(m)]
        gi = inverse(g)
        if gi is None:
            continue
        out["GL"] += 1
        memo = {}
        for name, members in fam.items():
            if all(x in req for x in members) and all(memo.setdefault(x, passes(g, gi, *req[x])) for x in members):
                out[name] += 1
    return out


def predictions(q, m, row):
    G = row["GL"]
    checks = {"GL": G == gl(q, m), "4261_transfer": pair_transfer(q, m) == row["pair"],
              "single": Q(row["one"], G) == closed["single"](q, m),
              "4259_laminar": Q(row["laminar"], G) == closed["4259_laminar"](q, m),
              "4259_split": Q(row["split"], G) == closed["4259_split"](q, m)}
    if q == 2:
        checks["4261_binary"] = Q(row["pair"], G) == closed["4261_binary"](m)
        checks["4274_binary"] = Q(row["oneway"], G) == closed["4274_binary"](m)
        if m >= 3:
            checks["4275_k3"] = Q(row["k3"], G) == closed["4275_k3_binary"](m)
        checks["4275_threshold"] = (row["k3"] > 0) == (m >= 4) and (m < 4 or (row["k4"] > 0) == (m >= 5))
        checks["4259_binary_obstruction"] = row["split"] == 0
    if q == 3:
        checks["4273_ternary"] = Q(row["pair"], G) == closed["4273_ternary"](m)
    return checks


def main():
    stated = {(2, 3, "pair"): Q(1, 84), (2, 4, "pair"): Q(1, 80), (2, 2, "oneway"): Q(1, 6), (2, 3, "oneway"): Q(1, 12),
              (2, 4, "oneway"): Q(151, 3360), (3, 3, "pair"): Q(14, 117), (3, 4, "pair"): Q(1727, 21060),
              (2, 4, "k3"): Q(1, 1680), (3, 3, "laminar"): Q(343, 1404)}
    small = {(q, m): census(q, m) for q, m in [(2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (4, 2), (5, 2)]}
    text = (HERE / "evidence/HEADER-RUNS.txt").read_text()
    need(f"headers.c (SHA256 {hashlib.sha256((HERE / 'headers.c').read_bytes()).hexdigest()})" in text, "runs recorded for this headers.c")
    runs = {}
    for line in text.splitlines():
        if line.startswith("q="):
            f = {k: int(v) for k, v in (kv.split("=") for kv in line.split())}
            runs[f.pop("q"), f.pop("m")] = f
    need(set(runs) == set(small) | {(4, 3), (5, 3), (2, 5), (3, 4)}, "recorded cases")
    for key, row in small.items():
        need(row == runs[key], f"Python and C censuses agree at q,m = {key}")
    for (q, m), row in sorted(runs.items()):
        for name, ok in predictions(q, m, row).items():
            need(ok, f"{name} at q={q}, m={m}")
    for (q, m, fam), frac in stated.items():
        need(Q(runs[q, m][fam], runs[q, m]["GL"]) == frac, f"stated value {frac} at q={q}, m={m}, {fam}")
    need(runs[3, 3]["k3"] == 480 and runs[2, 4]["k3"] == 12 and runs[2, 5]["k4"] == 48, "#4275's 480 and 12; 48 four-request headers at GL_5(F_2)")
    print(json.dumps({
        "status": "PASS_FULL_GUARD_HEADER_CENSUS",
        "python_cases": sorted(f"q{q}m{m}" for q, m in small),
        "c_cases_beyond_authors": ["q2m5", "q3m4", "q4m3", "q5m3"],
        "headers_enumerated": sum(r["GL"] for r in runs.values()),
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
