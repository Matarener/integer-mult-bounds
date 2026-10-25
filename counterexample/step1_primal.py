# Step 1: primal of the clique LP = fractional "skeleton" of a cheap decoder.
# min sum_r t_r x_r  s.t. for every clique Q: sum_{r touches Q on both sides} x_r >= 2|Q|,  x >= 0,
# over the span pairs r = (A, R) kept by the column-generation run (v4_cg2_state.pkl).
import sys, pickle, random, json, time
sys.path.insert(0, r'D:\Math\imb-v4')
import os; os.chdir(r'D:\Math\imb-v4')
import numpy as np, scipy.optimize as so, scipy.sparse as sp
from v4lib import *
d = pickle.load(open('v4_spans.pkl', 'rb')); spans, inside = d['spans'], d['inside']
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
orth = [[all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
random.seed(1); cl = set()
for i in range(NP): cl.add(frozenset([i]))
for i in range(NP):
    for j in range(i+1, NP):
        if not orth[i][j]: cl.add(frozenset([i, j]))
for _ in range(1500):
    order = list(range(NP)); random.shuffle(order); Q = []
    for v in order:
        if all(not orth[v][u] for u in Q): Q.append(v)
    cl.add(frozenset(Q))
cl = sorted(cl, key=lambda Q: (len(Q), sorted(Q)))
rows = pickle.load(open('v4_cg2_state.pkl', 'rb'))['rows']
ins = [set(x) for x in inside]
t = np.array([pair_rank(spans[a], spans[r]) for a, r in rows], float)
Tm = sp.lil_matrix((len(rows), len(cl)))
for i, (a, r) in enumerate(rows):
    for k, Q in enumerate(cl):
        if ins[a] & Q and ins[r] & Q: Tm[i, k] = 1
Tm = Tm.tocsr(); obj = np.array([2.0 * len(Q) for Q in cl])
res = so.linprog(-obj, A_ub=Tm, b_ub=t, bounds=(0, None), method='highs')
print('LP value', -res.fun, 'rows', len(rows), 'cliques', len(cl))
x = -res.ineqlin.marginals
sup = [(x[i], t[i], rows[i]) for i in np.argsort(-x) if x[i] > 1e-7]
print('primal support', len(sup), 'sum t*x', sum(a * b for a, b, _ in sup), 'sum x', sum(a for a, _, _ in sup))
out = []
for xi, ti, (a, r) in sup:
    out.append({'x': xi, 't': int(ti), 'A': sorted(ins[a]), 'R': sorted(ins[r]), 'dimA': len(spans[a]), 'dimR': len(spans[r])})
json.dump(out, open(r'D:\Math\counterexample\step1_primal.json', 'w'), indent=0)
from collections import Counter
print('tariff histogram (weighted x):', sorted(Counter({k: 0 for k in []}).items()))
h = Counter(); hx = Counter()
for o in out: h[o['t']] += 1; hx[o['t']] += o['x']
print('by tariff: count', dict(sorted(h.items())), 'x mass', {k: round(v, 2) for k, v in sorted(hx.items())})
print('|A|,|R| of top 15:'); [print(round(o['x'], 3), o['t'], len(o['A']), len(o['R']), o['A'][:12], o['R'][:12]) for o in out[:15]]
