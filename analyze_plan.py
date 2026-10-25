# Which term types carry the LP's fractional decoder plan (primal y) on the 292 active cliques?
import json, pickle, collections, numpy as np, scipy.optimize as so, scipy.sparse as sp
from v4lib import *
d = pickle.load(open('v4_spans.pkl', 'rb')); spans, inside = d['spans'], d['inside']; n = len(spans)
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
res_old = json.load(open('v4_pilot_result.json'))
Qs = [tuple(sorted(c['X'])) for c in res_old['columns']]
rows = sorted(set(map(tuple, pickle.load(open('v4_pilot_state.pkl', 'rb'))['rows'])))
im = np.array([sum(1 << v for v in ins) for ins in inside], dtype=np.uint64)
qm = np.array([sum(1 << v for v in Q) for Q in Qs], dtype=np.uint64)
ra = im[[a for a, r in rows]]; rr = im[[r for a, r in rows]]
T = ((ra[:, None] & qm[None, :]) != 0) & ((rr[:, None] & qm[None, :]) != 0)
tar = np.array([pair_rank(spans[a], spans[r]) for a, r in rows], dtype=float)
obj = np.array([2.0 * len(Q) for Q in Qs])
res = so.linprog(-obj, A_ub=sp.csr_matrix(T.astype(float)), b_ub=tar, bounds=(0, None), method='highs')
lam = res.x; y = -res.ineqlin.marginals
print('LP on 292 cliques:', round(-res.fun, 4), ' primal cost', round(float(y @ tar), 4))
sup = [t for t in np.argsort(-y) if y[t] > 1e-7]
def nA(t): return len(inside[rows[t][0]])
def nR(t): return len(inside[rows[t][1]])
print('support term types:', len(sup))
g = collections.defaultdict(lambda: [0, 0.0, 0.0])
for t in sup:
    key = (int(tar[t]), 'A=all' if nA(t) == NP else ('A>=20' if nA(t) >= 20 else 'A<20'), 'R=all' if nR(t) == NP else ('R=1' if nR(t) == 1 else ('R<=3' if nR(t) <= 3 else 'R>3')))
    g[key][0] += 1; g[key][1] += y[t]; g[key][2] += y[t] * tar[t]
print('\n(tariff, source size, reader size): count, total weight y, cost share')
for k, v in sorted(g.items(), key=lambda kv: -kv[1][2]): print(k, v[0], round(v[1], 3), round(v[2], 2))
act = np.nonzero(lam > 1e-9)[0]
print('\nactive cliques', len(act), 'sizes', sorted(collections.Counter(len(Qs[q]) for q in act).items()))
print('\ntop 15 term types by cost share:')
for t in sorted(sup, key=lambda t: -y[t] * tar[t])[:15]:
    A, R = inside[rows[t][0]], inside[rows[t][1]]
    print('  y=%.3f tariff=%d |A|=%d |R|=%d  touches %d active cliques  R=%s' % (y[t], tar[t], len(A), len(R), int(T[t, act].sum()), R if len(R) <= 6 else '...'))
# per-plane: how much reader weight lands on each plane via single-reader terms
pr = collections.Counter()
for t in sup:
    R = inside[rows[t][1]]
    if len(R) == 1: pr[R[0]] += y[t]
print('\nsingle-reader weight per plane (top 10):', [(p, round(w, 2)) for p, w in pr.most_common(10)], ' planes with any:', len(pr))
