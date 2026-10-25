#!/usr/bin/env python3
"""Exact shortest depth-five chain connectors for the eleven (m, c) that #4281 left open, 5 <= m <= 8.

Calls l and k commute when |l - k| >= 2, so a word's interval counts (Lemma 1 of #4281) depend only on
the subword of calls 2, 3, 4 and on how many calls 2 precede each call 1 and how many calls 4 precede
each call 5. residues.c (and the port `reachable` below) enumerates exactly that data for one call-count
vector and returns every reachable residue c. This file:
  1. cross-checks the port against an exhaustive BFS at m = 2 and #4281's BFS minima at m = 2, 3;
  2. checks the recorded complete residues.c runs (local evidence) that give the lower bounds;
  3. verifies every witness by the unitriangular product and a literal noncommuting replay;
  4. assembles the exact minima. No code from #4281.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
PR4281_WITNESSES = "ea320e9f069de8864952ad4b5e492875c1102bd1d12074f606b8aad2b54fe254"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def correct(word, m, c):
    x = [[int(i == j) for j in range(6)] for i in range(6)]
    for ch in word:
        l = int(ch)
        x[l] = [(a + b) % m for a, b in zip(x[l], x[l - 1])]
    return all(x[i][j] == (c % m if (i, j) == (5, 0) else 0) for i in range(6) for j in range(i))


def literal(word, m, c, rng):
    mul = lambda a, b: [[sum(a[i][k] * b[k][j] for k in range(2)) % m for j in range(2)] for i in range(2)]
    app = lambda a, v: [sum(a[i][k] * v[k] for k in range(2)) % m for i in range(2)]
    B = {l: [[rng.randrange(m) for _ in range(2)] for _ in range(2)] for l in range(1, 6)}
    z0 = [[rng.randrange(m) for _ in range(2)] for _ in range(6)]
    z = [v[:] for v in z0]
    for ch in word:
        l = int(ch)
        z[l] = [(a + b) % m for a, b in zip(z[l], app(B[l], z[l - 1]))]
    chain = mul(B[5], mul(B[4], mul(B[3], mul(B[2], B[1]))))
    gain = app(chain, z0[0])
    return z[:5] == z0[:5] and z[5] == [(a + c * b) % m for a, b in zip(z0[5], gain)]


def multisets(size, top):
    def rec(i, lo, cur):
        if i == size:
            yield tuple(cur)
            return
        for a in range(lo, top + 1):
            cur.append(a)
            yield from rec(i + 1, a, cur)
            cur.pop()
    yield from rec(0, 0, [])


def reachable(m, n):
    """every c in 1..m-1 reachable with exact call counts n = (n1..n5); port of residues.c"""
    n1, n2, n3, n4, n5 = n
    found = set()

    def middles(r2, r3, r4, cur):
        if not (r2 or r3 or r4):
            yield cur
            return
        for x, r in ((2, r2), (3, r3), (4, r4)):
            if r:
                cur.append(x)
                yield from middles(r2 - (x == 2), r3 - (x == 3), r4 - (x == 4), cur)
                cur.pop()
    for M in middles(n2, n3, n4, []):
        threes, c2, c4 = [], 0, 0
        for x in M:
            if x == 2:
                c2 += 1
            elif x == 3:
                threes.append((c2, c4))
            else:
                c4 += 1
        if sum(k2 for k2, _ in threes) % m or sum(n4 - k4 for _, k4 in threes) % m or sum(k2 * (n4 - k4) for k2, k4 in threes) % m:
            continue
        f3 = [sum(max(0, k2 - a) for k2, _ in threes) for a in range(n2 + 1)]
        f4 = [sum(max(0, k2 - a) * (n4 - k4) for k2, k4 in threes) for a in range(n2 + 1)]
        g3 = [sum(max(0, b - k4) for _, k4 in threes) for b in range(n4 + 1)]
        g2 = [sum(k2 * max(0, b - k4) for k2, k4 in threes) for b in range(n4 + 1)]
        h = [[sum(max(0, k2 - a) * max(0, b - k4) for k2, k4 in threes) for b in range(n4 + 1)] for a in range(n2 + 1)]
        H = {tuple(sum(h[a][b] for a in A) % m for b in range(n4 + 1)) for A in multisets(n1, n2)
             if not (sum(n2 - a for a in A) % m or sum(f3[a] for a in A) % m or sum(f4[a] for a in A) % m)}
        if not H:
            continue
        F = [Bv for Bv in multisets(n5, n4) if not (sum(Bv) % m or sum(g3[b] for b in Bv) % m or sum(g2[b] for b in Bv) % m)]
        found |= {sum(Hv[b] for b in Bv) % m for Hv in H for Bv in F}
    return found - {0}


def bfs_minima(m):
    """exact shortest positive words to every I + c E[5][0] in UT6(Z/m), by BFS"""
    rows = [(i, j) for i in range(1, 6) for j in range(i)]
    pos = {cell: k for k, cell in enumerate(rows)}

    def step(s, l):
        d = [(s // m ** k) % m for k in range(15)]
        for j in range(l - 1):
            d[pos[l, j]] = (d[pos[l, j]] + d[pos[l - 1, j]]) % m
        d[pos[l, l - 1]] = (d[pos[l, l - 1]] + 1) % m
        return sum(v * m ** k for k, v in enumerate(d))
    targets = {c * m ** pos[5, 0]: c for c in range(1, m)}
    seen, frontier, dist, found = {0}, [0], 0, {}
    while frontier and len(found) < m - 1:
        dist += 1
        nxt = []
        for s in frontier:
            for l in range(1, 6):
                r = step(s, l)
                if r not in seen:
                    seen.add(r)
                    nxt.append(r)
                    if r in targets:
                        found[targets[r]] = dist
        frontier = nxt
    return found


def minima_from_decider(m, kmax):
    best = {}
    for k in range(5, kmax + 1):
        for v in product(range(1, k + 1), repeat=5):
            if sum(v) == k:
                for c in reachable(m, [x * m for x in v]):
                    best.setdefault(c, k * m)
    return best


def main():
    rng = random.Random(4281)
    # 1. the decomposition against exhaustive search: Python at m = 2 (all lengths to 16) and m = 3 (to 21)
    need(bfs_minima(2) == {1: 16}, "BFS at m = 2")
    need(minima_from_decider(2, 8) == {1: 16}, "decider at m = 2 agrees with BFS (16)")
    need(minima_from_decider(3, 7) == {}, "decider at m = 3: nothing below 24, as #4281's BFS says")

    # 2. recorded complete runs: the lower bounds
    text = (HERE / "evidence/RESIDUE-RUNS.txt").read_text()
    need(f"residues.c (SHA256 {hashlib.sha256((HERE / 'residues.c').read_bytes()).hexdigest()})" in text, "runs recorded for this residues.c")
    runs = {}
    for line in text.splitlines():
        if line.startswith("M="):
            f = dict(kv.split("=", 1) for kv in line.split() if "=" in kv)
            need("COMPLETE" in line, f"run is complete: {line[:40]}")
            runs[int(f["M"]), tuple(map(int, f["counts"].split(",")))] = {int(x) for x in f["reachable"].split(",") if x}
    lower = {}
    for m, k in ((5, 5), (5, 6), (6, 5), (7, 5)):
        vecs = [tuple(x * m for x in v) for v in product(range(1, k + 1), repeat=5) if sum(v) == k]
        need(all((m, v) in runs for v in vecs), f"every count vector of length {k * m} at m = {m} recorded")
        lower[m, k * m] = set().union(*(runs[m, v] for v in vecs))
    need(lower[5, 25] == {1} and lower[5, 30] == {1, 2}, "m = 5: only c = 1 at 25 calls, only c = 1, 2 at 30")
    need(lower[6, 30] == {1, 3}, "m = 6: only c = 1, 3 at 30 calls")
    need(lower[7, 35] == {1, 2, 3, 4, 5}, "m = 7: every c but 6 at 35 calls")
    # recorded cross-check of the C build against BFS minima: m = 3 to 24 calls, m = 4 to 28
    cross, ctext = {}, (HERE / "evidence/CROSSCHECK-RUNS.txt").read_text()
    need(f"residues.c (SHA256 {hashlib.sha256((HERE / 'residues.c').read_bytes()).hexdigest()})" in ctext, "cross-check recorded for this residues.c")
    for line in ctext.splitlines():
        if line.startswith("M="):
            f = dict(kv.split("=", 1) for kv in line.split() if "=" in kv)
            need("COMPLETE" in line, "cross-check run is complete")
            n = tuple(map(int, f["counts"].split(",")))
            for c in (int(x) for x in f["reachable"].split(",") if x):
                key = (int(f["M"]), c)
                cross[key] = min(cross.get(key, 10**9), sum(n))
    need(sum(line.startswith("M=") for line in (HERE / "evidence/CROSSCHECK-RUNS.txt").read_text().splitlines()) == 56 + 21,
         "every count vector of length <= 24 at m = 3 and <= 28 at m = 4 recorded")
    need(cross == {(3, 1): 24, (3, 2): 24, (4, 1): 28, (4, 2): 24, (4, 3): 28}, "C decider minima equal #4281's BFS at m = 3, 4")

    # 3. witnesses: the eleven open pairs, and #4281's own rows for the floors already found
    W = json.loads((HERE / "WITNESSES.json").read_text())["witnesses"]
    raw = (HERE / "vendor/pr4281-witnesses.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PR4281_WITNESSES, "vendored #4281 witnesses")
    old = json.loads(raw)["witnesses"]
    open_pairs = {(m, c) for m in range(5, 9) for c in range(1, m) if str(c) not in old.get(str(m), {})}
    need(len(open_pairs) == 11 and open_pairs == {(int(m), int(c)) for m, row in W.items() for c in row}, "exactly #4281's eleven open pairs")
    for m_s, row in W.items():
        for c_s, w in row.items():
            m, c = int(m_s), int(c_s)
            need(correct(w, m, c) and all(literal(w, m, c, rng) for _ in range(3)), f"witness ({m},{c})")
            need(len(w) % m == 0 and all(w.count(str(l)) % m == 0 for l in range(1, 6)), f"witness ({m},{c}) call counts")

    # 4. exact minima: lower bound from the complete runs, upper bound from the witness
    minima = {}
    for (m, c) in sorted(open_pairs):
        L = len(W[str(m)][str(c)])
        for (mm, total), reach in lower.items():
            if mm == m and total < L:
                need(c not in reach, f"({m},{c}) unreachable at {total}")
        need(L == 5 * m or (m, L - m) in lower, f"({m},{c}): every shorter multiple of m is excluded")
        minima[f"{m},{c}"] = L
    need(minima == {"5,2": 30, "5,3": 35, "5,4": 35, "6,1": 30, "6,2": 36, "6,4": 36, "6,5": 36,
                    "7,5": 35, "7,6": 42, "8,5": 40, "8,7": 40}, "the decided table")
    print(json.dumps({"status": "PASS_DEPTH5_CONNECTOR_RESIDUES", "exact_minima": minima, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
