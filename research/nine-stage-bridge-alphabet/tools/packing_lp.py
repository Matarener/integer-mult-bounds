#!/usr/bin/env python3
"""Relaxed packing price of an idle alphabet (planning numbers only; needs numpy and scipy).

Model: the fixed-supplier packing LP of research/staged-width-t488 (PR3633 ceiling/PROOF.md):
helpers of widths 4..9 with per-call inventory {4:26,5:2,6:18,7:52,8:97,9:213}, nine calls per replica,
whole helpers packed into idle children; the remainder of each child is one idle child (split 51+rest if
above the halving guard). Local profile of the retimed T488 supplier (PR3653) {1:2437,2:724,3:226,4:102,
5:20,8:8} per call. Every alphabet entry stands for 224 children per replica (112 ports, two sides).
The incumbent alphabet reproduces the PR3653 root 0.0017304189. Chronology and owner windows are ignored.

  python3 -B tools/packing_lp.py 8,8,8,16,16,32,32,48,48 8,8,8,8,16,32,40,48,48
"""
import sys
import numpy as np
from scipy.optimize import linprog

WID = [4, 5, 6, 7, 8, 9]
INV = {4: 26, 5: 2, 6: 18, 7: 52, 8: 97, 9: 213}
LOCAL = {1: 2437, 2: 724, 3: 226, 4: 102, 5: 20, 8: 8}
CALLS = 9
_P = {}


def patterns(C):
    if C not in _P:
        out = []

        def rec(i, left, cnt):
            if i == len(WID):
                out.append((tuple(cnt), left)); return
            for k in range(left // WID[i] + 1):
                rec(i + 1, left - k * WID[i], cnt + [k])
        rec(0, C, []); _P[C] = out
    return _P[C]


def rem_cost(r, a):
    return 0.0 if r == 0 else (r ** (1 - a) if r <= 51 else 51 ** (1 - a) + rem_cost(r - 51, a))


def norm(bins, a):
    caps = sorted(bins); cols, cost = [], []
    for ci, C in enumerate(caps):
        for cnt, idle in patterns(C):
            col = [0] * len(caps); col[ci] = 1; cols.append(col + list(cnt)); cost.append(rem_cost(idle, a))
    A = np.array(cols, float).T; b = [bins[C] for C in caps] + [CALLS * INV[w] for w in WID]
    f = linprog(cost, A_eq=A, b_eq=b, bounds=(0, None), method='highs').fun
    return (CALLS * sum(n * r ** (1 - a) for r, n in LOCAL.items()) + f) / (896 * 73 ** (1 - a))


def root(alphabet):
    bins = {}
    for c in alphabet:
        bins[c] = bins.get(c, 0) + 224
    lo, hi = 0.0, 0.004
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if norm(bins, mid) < 1 else (lo, mid)
    return lo


if __name__ == '__main__':
    base = root((8, 8, 8, 16, 16, 32, 32, 48, 48))
    for arg in sys.argv[1:]:
        al = tuple(map(int, arg.split(',')))
        r = root(al)
        print(f'{al}: relaxed root {r:.10f} ({(r / base - 1) * 100:+.3f}% vs incumbent alphabet)')
