# Can a REAL (hence possibly dyadic) decoder on a small plane group beat 4 per plane?
# Group D (g planes, 2g ports).  Terms: s "diagonal" terms (u, v supported on all ports of D, cost = tariff(D, D)),
# plus cross terms (u on plane i, v on plane j, i != j, cost = pair_rank(plane i, plane j)).
# Solve sum u v^T = target on the fixed mask entries by nonlinear least squares from many random starts.
import itertools, sys, numpy as np, scipy.optimize as so
from v4lib import *
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
def sp(D): return span([v for i in D for v in planes[i]])
def tar(A, R): return pair_rank(sp(A), sp(R))
rng = np.random.default_rng(0)
def attempt(D, s, cross, tries=300):
    g = len(D); m = 2 * g
    fixed = [(p, q, float(p == q)) for p in range(m) for q in range(m) if p == q or p // 2 == q // 2 or not ORTH[D[p // 2]][D[q // 2]]]
    masks = [(np.ones(m), np.ones(m))] * s
    for i, j in cross:
        a = np.zeros(m); a[2*i:2*i+2] = 1; b = np.zeros(m); b[2*j:2*j+2] = 1; masks.append((a, b))
    K = len(masks); P = np.array([p for p, q, t in fixed]); Q = np.array([q for p, q, t in fixed]); T = np.array([t for p, q, t in fixed])
    def res(x):
        U = x[:K*m].reshape(K, m) * np.array([a for a, b in masks]); V = x[K*m:].reshape(K, m) * np.array([b for a, b in masks])
        M = U.T @ V
        return M[P, Q] - T
    best = 1e9
    for _ in range(tries):
        r = so.least_squares(res, rng.normal(size=2*K*m), method='trf', max_nfev=3000)
        best = min(best, float(np.abs(r.fun).max()))
        if best < 1e-10: return best
    return best
# the most degenerate triples: lowest tariff(D, D)
import json
reps = {tuple(sorted(c[0])) for c in json.load(open('tri_classes.json'))}
tri = sorted({(tar(D, D), D) for D in reps} | {(tar(D, D), D) for D in itertools.combinations(range(NP), 3) if tar(D, D) <= 3})
print('triples to test:', len(tri), flush=True)
found = []
for tD, D in tri:
    g = 3; crossable = [(i, j) for i in range(g) for j in range(g) if i != j]
    ccost = {(i, j): tar([D[i]], [D[j]]) for i, j in crossable}
    for s in range(2, 6):
        for t in range(1, 7):
            for cr in itertools.combinations_with_replacement(crossable, t):
                cost = s * tD + sum(ccost[c] for c in cr)
                if cost >= 12 or s + t < 6: continue
                b = attempt(list(D), s, list(cr), tries=60)
                if b < 1e-8:
                    print('FOUND real decoder on', D, 'tariff(D,D)', tD, 's', s, 'cross', cr, 'cost', cost, 'residual', b, flush=True); found.append((D, s, cr, cost))
    print('triple', D, 'tariff(D,D)', tD, 'done', flush=True)
print('total found', len(found))
