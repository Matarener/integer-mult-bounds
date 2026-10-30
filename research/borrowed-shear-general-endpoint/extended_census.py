#!/usr/bin/env python3
"""Opt-in NumPy census over F2 (default n=3, q=2): exact minima for every diag(T, I_q).

Not registered in VERIFY.json; run with an interpreter that has NumPy.
"""
import itertools, sys
import numpy as np
from collections import Counter
n, q = map(int, sys.argv[1:3]) if len(sys.argv) > 2 else (3, 2); m = n + q; M = (1 << m) - 1
def pack(cols): return sum(c << (i*m) for i, c in enumerate(cols))
I = pack([1 << i for i in range(m)])
gens = []  # (kind, matrix) kind 'G': for x-col j list of z-cols a ; 'S': for z-col a list of x-cols i
for vals in itertools.product((0,1), repeat=q*n):
    if not any(vals): continue
    gens.append(('G', [[a for a in range(q) if vals[a*n+j]] for j in range(n)]))
    gens.append(('S', [[i for i in range(n) if vals[a*n+i]] for a in range(q)]))
dist = np.full(1 << (m*m), 255, dtype=np.uint8); dist[I] = 0
front = np.array([I], dtype=np.uint64); d = 0
while front.size:
    d += 1
    cols = [(front >> np.uint64(c*m)) & np.uint64(M) for c in range(m)]
    new = []
    for kind, spec in gens:
        nc = list(cols)
        if kind == 'G':
            for j in range(n):
                for a in spec[j]: nc[j] = nc[j] ^ cols[n+a]
        else:
            for a in range(q):
                for i in spec[a]: nc[n+a] = nc[n+a] ^ cols[i]
        v = nc[0].copy()
        for c in range(1, m): v |= nc[c] << np.uint64(c*m)
        new.append(v)
    cand = np.unique(np.concatenate(new))
    cand = cand[dist[cand] == 255]
    dist[cand] = d; front = cand
def rank2(rows):
    rows = list(rows); r = 0
    for bit in range(n):
        piv = next((i for i in range(r, len(rows)) if rows[i] >> bit & 1), None)
        if piv is None: continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> bit & 1: rows[i] ^= rows[r]
        r += 1
    return r
def matmul(A, B):  # row bitmask matrices n x n: row i bit j
    return [ (lambda ri: __import__('functools').reduce(lambda acc, k: acc ^ (B[k] if ri >> k & 1 else 0), range(n), 0))(A[i]) for i in range(n)]
stats = Counter()
for Tbits in range(1 << (n*n)):
    Trows = [(Tbits >> (i*n)) & ((1 << n) - 1) for i in range(n)]
    # column j of full matrix: bits i of rows
    cols = [sum(((Trows[i] >> j) & 1) << i for i in range(n)) for j in range(n)] + [1 << (n+a) for a in range(q)]
    dd = int(dist[pack(cols)])
    if dd == 255: continue
    N = [Trows[i] ^ (1 << i) for i in range(n)]
    r = rank2(N); P = N; nil = None
    for e in range(1, n+2):
        if not any(P): nil = e; break
        P = matmul(P, N)
    N2 = matmul(N, N)
    stats[(r, rank2(N2), nil, dd)] += 1
bad = 0
for (r, r2, nil, dd), cnt in sorted(stats.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or 99, kv[0][3])):
    base = 2 * (-(-r // q)) + 2 if r else 0
    want = base if r2 == 0 else max(base, 6)
    bad += cnt * (dd != want)
    print("r=%d rank((T-I)^2)=%d nilpotency_index=%s minimum=%d tariff=%d : %d" % (r, r2, nil, dd, want, cnt))
print("group_order", int((dist != 255).sum()), "endpoints", sum(stats.values()), "mismatches", bad)
if bad:
    raise SystemExit("FAIL: tariff mismatch")
print("PASS_EXTENDED_CENSUS")
