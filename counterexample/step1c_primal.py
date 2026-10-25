# Step 1c: primal skeleton on the near-tight pairs with the 443 certificate cliques as constraints.
import json, numpy as np, scipy.optimize as so, scipy.sparse as sp
from collections import Counter
d = json.load(open('step1b_tight.json')); ins = [set(x) for x in d['inside']]; P = d['pairs']
cert = json.load(open(r'D:\Math\imb-v4pr\research\plane-port-global-rank-dual\CERTIFICATE.json'))
cl = [set(c['clique']) for c in cert['columns']]
rows = [(a, r, t) for a, r, t, s in P]
A = sp.lil_matrix((len(cl), len(rows)))
for j, (a, r, t) in enumerate(rows):
    for k, Q in enumerate(cl):
        if ins[a] & Q and ins[r] & Q: A[k, j] = 1
c = np.array([t for _, _, t in rows], float); b = np.array([2.0 * len(Q) for Q in cl])
res = so.linprog(c, A_ub=-A.tocsr(), b_ub=-b, bounds=(0, None), method='highs')
print('primal value', res.fun, 'near-tight pairs', len(rows), 'cliques', len(cl))
x = res.x; sup = [j for j in np.argsort(-x) if x[j] > 1e-7]
out = [{'x': float(x[j]), 't': rows[j][2], 'A': sorted(ins[rows[j][0]]), 'R': sorted(ins[rows[j][1]])} for j in sup]
json.dump(out, open('step1c_skeleton.json', 'w'), indent=0)
h = Counter(); hx = Counter()
for o in out: h[o['t']] += 1; hx[o['t']] += o['x']
print('support', len(out), 'sum x', round(sum(o['x'] for o in out), 3))
print('by tariff: count', dict(sorted(h.items())), 'x mass', {k: round(v, 2) for k, v in sorted(hx.items())})
diag = sum(o['x'] for o in out if set(o['A']) & set(o['R']))
print('x mass of terms with A and R sharing a plane:', round(diag, 2))
for o in out[:20]: print(round(o['x'], 3), 't', o['t'], '|A|', len(o['A']), '|R|', len(o['R']), 'shared', len(set(o['A']) & set(o['R'])))
