# Rigorous pipeline. Rows: Lemma-B S-cuts (0/1 lift on S×S) + AGLB rows (B' = 1 on masked/diag, 1 on an acyclic set of free arcs, 0 other free).
# All ranks EXACT (exact.qrank, Hadamard-certified mod 2^61-1), F2 costs exact, maximal rects exact.
# (1) LP dual -> rational y -> exact reduced-cost fixing (valid for any y>=0):  c.x >= y.b + sum r_j x_j,  r = c - A^T y.
# (2) exhaustive DFS over the surviving rects (multisets, total cost <= 7) with exact row checks.
import sys, time, pickle, itertools
from fractions import Fraction as Fr
import numpy as np, networkx as nx
import os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact import *
from scipy.optimize import linprog
o = int(sys.argv[1]); fam = sys.argv[2]; budget = int(sys.argv[3]) if len(sys.argv) > 3 else 7   # fam: 'S' or 'SA' (S-cuts + AGLB)
B = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orbits.json')))[str(o)]['B']
t0 = time.time(); mx = maxrects(B, budget); n = len(mx); c = [cc for _, _, cc in mx]
rows = []; rhs = []
for S in range(1, 256):
    rows.append([subrank(B, R & S, A & S) for R, A, _ in mx]); rhs.append(bin(S).count('1'))
nS = len(rows)
if 'A' in fam:
    edges = [(i, j) for i in range(8) for j in range(i + 1, 8) if not B[i][j]]
    for ch in itertools.product([0, 1, 2], repeat=len(edges)):
        G = nx.DiGraph(); G.add_nodes_from(range(8))
        for (i, j), v in zip(edges, ch):
            if v == 1: G.add_edge(i, j)
            if v == 2: G.add_edge(j, i)
        if not nx.is_directed_acyclic_graph(G): continue
        Bp = [[1 if B[i][j] else 0 for j in range(8)] for i in range(8)]
        for (i, j), v in zip(edges, ch):
            if v == 1: Bp[i][j] = 1
            if v == 2: Bp[j][i] = 1
        rows.append([subrank(Bp, R, A) for R, A, _ in mx]); rhs.append(8)
if 'T' in fam:   # AGLB rows from linear orders on each side's free cliques (or no arcs)
    sides = [list(range(4)), list(range(4, 8))]
    def ords(sd): return [None] + list(itertools.permutations(sd))
    for o1 in ords(sides[0]):
        for o2 in ords(sides[1]):
            Bp = [[1 if B[i][j] else 0 for j in range(8)] for i in range(8)]
            for od in (o1, o2):
                if od is None: continue
                pos = {v: k for k, v in enumerate(od)}
                for i in od:
                    for j in od:
                        if i != j and not B[i][j] and pos[i] < pos[j]: Bp[i][j] = 1
            rows.append([subrank(Bp, R, A) for R, A, _ in mx]); rhs.append(8)
print('orbit', o, 'rects', n, 'rows', len(rows), '(S-cuts', nS, ')', round(time.time() - t0), 's', flush=True)
A = np.array(rows, dtype=np.int64); b = np.array(rhs, dtype=np.int64); cv = np.array(c, dtype=np.int64)
alive = np.ones(n, bool); ub = np.array([budget // cc for cc in c])
for rnd in range(20):
    idx = np.nonzero(alive)[0]
    res = linprog(cv[idx].astype(float), A_ub=-A[:, idx].astype(float), b_ub=-b.astype(float), bounds=[(0, int(ub[j])) for j in idx], method='highs')
    if res.status == 2:
        print('LP infeasible on survivors (need Farkas); falling to DFS'); break
    y = [Fr(v).limit_denominator(10**7) if v > 1e-12 else Fr(0) for v in -res.ineqlin.marginals]
    nz = [i for i, v in enumerate(y) if v]
    yb = sum(y[i] * int(b[i]) for i in nz)
    r = {j: Fr(int(cv[j])) - sum(y[i] * int(A[i, j]) for i in nz) for j in idx}
    L = yb + sum(min(Fr(0), r[j]) * int(ub[j]) for j in idx)
    print(f' round {rnd}: LP {res.fun:.5f}  certified base bound {float(L):.5f}  alive {len(idx)}', flush=True)
    if L > budget: print('CERTIFIED INFEASIBLE by LP dual (rational y), round', rnd); alive[:] = False; break
    changed = False
    for j in idx:
        rj = r[j]; Lj = L - min(Fr(0), rj) * int(ub[j])     # bound excluding j's own negative part
        if rj > 0 and Lj + rj > budget: alive[j] = False; changed = True
        elif rj > 0:
            k = int((budget - Lj) // rj)   # x_j <= k
            if k < ub[j]: ub[j] = max(k, 0); changed = True
            if ub[j] == 0: alive[j] = False
    if not changed: break
idx = [int(j) for j in np.nonzero(alive)[0]]
pickle.dump((mx, A, b, c, idx, ub), open(f'rows_{o}_{fam}_{budget}.pkl', 'wb'))
if len(sys.argv) > 4 and sys.argv[4] == 'stop': sys.exit(0)
print('survivors after exact reduced-cost fixing', len(idx), round(time.time() - t0), 's', flush=True)
# exhaustive DFS over multisets of survivors with CERTIFIED LP bounding at every node (any y>=0 gives a valid bound).
idx.sort(key=lambda j: -c[j]); Ai = A[:, idx].astype(np.int64); ci = np.array([c[j] for j in idx], dtype=np.int64); ubi = np.array([ub[j] for j in idx])
sols = []; nodes = [0]; pruned_lp = [0]
def lpbound(start, rem, acc):
    d = b - acc; act = d > 0
    if not act.any(): return None
    vars_ = np.arange(start, len(idx))
    if len(vars_) == 0: return Fr(10**9)
    Asub = Ai[np.ix_(act, vars_)]; dsub = d[act]
    if (Asub.sum(1) == 0).any(): return Fr(10**9)          # a row with deficit and no allowed contributor
    res = linprog(ci[vars_].astype(float), A_ub=-Asub.astype(float), b_ub=-dsub.astype(float), bounds=(0, None), method='highs')
    if res.status != 0: return Fr(0)
    y = [Fr(v).limit_denominator(10**6) if v > 1e-12 else Fr(0) for v in -res.ineqlin.marginals]
    nz = [i for i, v in enumerate(y) if v]
    bd = sum(y[i] * int(dsub[i]) for i in nz)
    for jj, j in enumerate(vars_):
        r = Fr(int(ci[j])) - sum(y[i] * int(Asub[i, jj]) for i in nz)
        if r < 0: bd += r * int(min(ubi[j], rem // ci[j]))
    return bd
def rec(start, rem, acc, ch):
    nodes[0] += 1
    if (acc >= b).all(): sols.append(list(ch)); return
    if rem == 0: return
    bd = lpbound(start, rem, acc)
    if bd is not None and bd > rem: pruned_lp[0] += 1; return
    for k in range(start, len(idx)):
        if ci[k] <= rem and ch.count(k) < ubi[k]:
            ch.append(k); rec(k, rem - int(ci[k]), acc + Ai[:, k], ch); ch.pop()
    if nodes[0] % 500 == 0: print('  nodes', nodes[0], 'sols', len(sols), round(time.time() - t0), flush=True)
rec(0, budget, np.zeros(len(b), dtype=np.int64), [])
print('DFS nodes', nodes[0], 'LP-pruned', pruned_lp[0], 'feasible multisets', len(sols), round(time.time() - t0), 's', flush=True)
for s in sols[:5]: print('  ', [mx[idx[k]] for k in s])
pickle.dump((mx, idx, sols), open(f'certify_{o}_{fam}_{budget}.pkl', 'wb'))
