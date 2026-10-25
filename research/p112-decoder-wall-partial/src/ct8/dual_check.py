#!/usr/bin/env python3
"""Stdlib check of an exact rational LP-dual certificate that a KFAM (4,4) set T has no decoder of F2-cost <= 7
(orbits 2 and 5).  usage: dual_check.py ORBIT dual.json

Model (CT8): terms p_k q_k^T over a char-0 field, supports R_k, A_k in the 8 lines of T, cost_k = rank_F2 B[R_k, A_k].
Valid rows (exact ranks over Q):  for any 0/1 matrix B' with B' = 1 on masked cells and the diagonal, and B' nonzero on the free
(B = 0) pairs only along an acyclic arc set,   sum_k rank_Q B'[R_k, A_k] >= rank(B' o M') = 8   (AGLB);
for B' = B restricted to S x S (a Lemma-B S-cut)  sum_k rank_Q B[R_k & S, A_k & S] >= |S|.
WLOG each term is a MAXIMAL rectangle of its F2 cost (ranks only grow).  The certificate is y >= 0 with  sum_i y_i a_ij <= c_j
for every maximal rectangle j of cost <= 7; then  cost = sum c_j x_j >= sum_i y_i b_i, which must exceed 7.
Everything is recomputed here: rectangles, ranks, row coefficients, the inequality (Fractions)."""
import sys, os, json, itertools
from fractions import Fraction as Fr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact import qrank, maxrects
HERE = os.path.dirname(os.path.abspath(__file__))
o = sys.argv[1]; cert = json.load(open(sys.argv[2]))
B = json.load(open(os.path.join(HERE, 'orbits.json')))[o]['B']
mx = maxrects(B, 7); print('orbit', o, 'maximal rectangles of F2-cost <= 7:', len(mx))
def sub(Bp, R, A): return qrank([[Bp[i][j] for j in range(8) if A >> j & 1] for i in range(8) if R >> i & 1])
def acyclic(arcs):
    adj = {i: [] for i in range(8)}
    for i, j in arcs: adj[i].append(j)
    st = {}
    def dfs(u):
        st[u] = 1
        for v in adj[u]:
            if st.get(v) == 1 or (v not in st and dfs(v)): return True
        st[u] = 2; return False
    return not any(u not in st and dfs(u) for u in range(8))
def lift(arcs):
    Bp = [[1 if B[i][j] else 0 for j in range(8)] for i in range(8)]
    for i, j in arcs: Bp[i][j] = 1
    return Bp
rows = []   # (y, B', S or None, rhs): coefficient of rectangle (R,A) is rank_Q B'[R&S, A&S] (S-cut) or rank_Q B'[R,A] (AGLB row)
for kind, val, y in cert['y']:
    y = Fr(y); assert y >= 0
    if kind == 'S': rows.append((y, lift([]), val, bin(val).count('1')))
    else:
        arcs = [tuple(a) for a in val]
        assert all(not B[i][j] and i != j for i, j in arcs) and acyclic(arcs), 'arc set must be acyclic and on free pairs'
        rows.append((y, lift(arcs), None, 8))
for R, A, c in mx:
    tot = sum(y * (sub(Bp, R & S, A & S) if S is not None else sub(Bp, R, A)) for y, Bp, S, rhs in rows)
    assert tot <= c, ('dual infeasible at rectangle', R, A, c, tot)
bound = sum(y * rhs for y, Bp, S, rhs in rows)
print('rows used', len(rows), ' dual objective y.b =', bound, '=', float(bound), '(need > 7); dual feasible on all', len(mx), 'rectangles')
assert bound > 7
print('DUAL_CERT_OK orbit', o, ': every decoder on T has cost >=', bound, '> 7, hence C(T) >= 8')
