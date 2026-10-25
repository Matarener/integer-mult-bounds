# (generator, needs scipy) solve the CT8 row LP for an orbit, rationalise the dual, write dual.json.  usage: mkdual.py ORBIT out.json
import sys, os, json, itertools
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact import qrank, maxrects
o = sys.argv[1]; B = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orbits.json')))[o]['B']
mx = maxrects(B, 7)
def sub(Bp, R, A): return qrank([[Bp[i][j] for j in range(8) if A >> j & 1] for i in range(8) if R >> i & 1])
keys = []; rows = []; rhs = []
for S in range(1, 256):
    Bp = [[B[i][j] if (S >> i & 1 and S >> j & 1) else 0 for j in range(8)] for i in range(8)]
    keys.append(('S', S)); rows.append([sub(Bp, R & S, A & S) for R, A, c in mx]); rhs.append(bin(S).count('1'))
edges = [(i, j) for i in range(8) for j in range(i + 1, 8) if not B[i][j]]
import networkx as nx
for ch in itertools.product([0, 1, 2], repeat=len(edges)):
    arcs = [(i, j) if v == 1 else (j, i) for (i, j), v in zip(edges, ch) if v]
    if not arcs: continue
    G = nx.DiGraph(); G.add_nodes_from(range(8)); G.add_edges_from(arcs)
    if not nx.is_directed_acyclic_graph(G): continue
    Bp = [[1 if B[i][j] else 0 for j in range(8)] for i in range(8)]
    for i, j in arcs: Bp[i][j] = 1
    keys.append(('A', sorted(arcs))); rows.append([sub(Bp, R, A) for R, A, c in mx]); rhs.append(8)
A = np.array(rows, dtype=float); b = np.array(rhs, dtype=float); c = np.array([cc for _, _, cc in mx], dtype=float)
# dual: max b.y s.t. A^T y <= c, y >= 0
res = linprog(-b, A_ub=A.T, b_ub=c, bounds=(0, None), method='highs')
print('LP dual value', -res.fun)
for den in (10, 100, 1000, 10**4, 10**6):
    y = [Fr(v).limit_denominator(den) if v > 1e-9 else Fr(0) for v in res.x]
    ok = all(sum(y[i] * int(rows[i][j]) for i in range(len(rows)) if y[i]) <= mx[j][2] for j in range(len(mx)))
    val = sum(y[i] * rhs[i] for i in range(len(rows)))
    print('den', den, 'feasible', ok, 'value', val)
    if ok and val > 7: break
json.dump({'orbit': int(o), 'y': [[keys[i][0], keys[i][1], str(y[i])] for i in range(len(rows)) if y[i]]}, open(sys.argv[2], 'w'))
