# Real-valued sparse search for cheap local decoders on a plane triple (escape test for even denominators).
# All term types (A, R) (nonempty plane subsets of the triple, tariff > 0) are present, COPIES copies each.
# Minimise ||residual on fixed mask entries||^2 + lam * sum_k tariff_k * sqrt(|u_k|^2 |v_k|^2 + eps)  (L-BFGS),
# raising lam; then prune terms with negligible weight, refit the survivors by least squares and record the true cost
# (sum of tariffs of the surviving supports) whenever the refit is exact.  Baseline is 12 (= 4 per plane).
import itertools, json, sys, time, numpy as np, scipy.optimize as so
from v4lib import *
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
def sp(D): return span([v for i in D for v in planes[i]])
def tar(A, R): return pair_rank(sp(A), sp(R)) if A and R else 0
COPIES = 2
def search(D, starts, seed):
    rng = np.random.default_rng(seed); g = len(D); m = 2 * g
    fixed = [(p, q, float(p == q)) for p in range(m) for q in range(m) if p == q or p // 2 == q // 2 or not ORTH[D[p // 2]][D[q // 2]]]
    P = np.array([f[0] for f in fixed]); Q = np.array([f[1] for f in fixed]); T = np.array([f[2] for f in fixed])
    subsets = [tuple(i for i in range(g) if x >> i & 1) for x in range(1, 1 << g)]
    types = [(A, R, tar([D[i] for i in A], [D[i] for i in R])) for A in subsets for R in subsets]
    types = [t for t in types if t[2] > 0] * COPIES
    K = len(types)
    MU = np.array([[1.0 if p // 2 in A else 0.0 for p in range(m)] for A, R, c in types])
    MV = np.array([[1.0 if p // 2 in R else 0.0 for p in range(m)] for A, R, c in types])
    cost = np.array([c for A, R, c in types], dtype=float)
    def unpack(x): return x[:K*m].reshape(K, m) * MU, x[K*m:].reshape(K, m) * MV
    def f(x, lam):
        U, V = unpack(x); M = U.T @ V; r = M[P, Q] - T
        nu = (U * U).sum(1); nv = (V * V).sum(1); w = np.sqrt(nu * nv + 1e-8)
        val = (r * r).sum() + lam * (cost * w).sum()
        GM = np.zeros((m, m)); np.add.at(GM, (P, Q), 2 * r)
        gU = (V @ GM.T) + lam * (cost * nv / w)[:, None] * U
        gV = (U @ GM) + lam * (cost * nu / w)[:, None] * V
        return val, np.concatenate([(gU * MU).ravel(), (gV * MV).ravel()])
    def refit(active):
        idx = np.array(active); Ka = len(idx)
        def res(y):
            U = y[:Ka*m].reshape(Ka, m) * MU[idx]; V = y[Ka*m:].reshape(Ka, m) * MV[idx]
            return (U.T @ V)[P, Q] - T
        return res, Ka
    best = None
    for s in range(starts):
        x = rng.normal(scale=0.7, size=2 * K * m)
        for lam in (0.0, 0.001, 0.003, 0.01, 0.02, 0.05):
            x = so.minimize(f, x, args=(lam,), jac=True, method='L-BFGS-B', options={'maxiter': 3000}).x
        U, V = unpack(x); wts = np.sqrt((U * U).sum(1) * (V * V).sum(1))
        order = [k for k in np.argsort(-wts) if wts[k] > 1e-6]
        # smallest prefix (by weight) whose exact refit works; try a few prefix sizes
        for n_keep in range(4, len(order) + 1):
            active = order[:n_keep]
            if sum(cost[k] for k in active) >= (best[0] if best else 1e9): break
            res, Ka = refit(active)
            y0 = np.concatenate([U[active].ravel(), V[active].ravel()])
            r = so.least_squares(res, y0, method='trf', max_nfev=1500)
            if np.abs(r.fun).max() < 1e-9:
                Ua = r.x[:Ka*m].reshape(Ka, m) * MU[active]; Va = r.x[Ka*m:].reshape(Ka, m) * MV[active]
                true = 0
                for k in range(Ka):
                    A = tuple(sorted({p // 2 for p in range(m) if abs(Ua[k, p]) > 1e-9})); R = tuple(sorted({p // 2 for p in range(m) if abs(Va[k, p]) > 1e-9}))
                    true += tar([D[i] for i in A], [D[i] for i in R])
                if best is None or true < best[0]:
                    best = (true, [(types[k][0], types[k][1]) for k in active])
                break
    return best
def _run(a):
    D, st, sd = a
    return D, search(D, st, sd)

if __name__ == '__main__':
    import multiprocessing as mp
    starts = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    reps = [tuple(sorted(c[0])) for c in json.load(open('tri_classes.json'))]
    if len(sys.argv) > 2: reps = reps[:int(sys.argv[2])]
    t0 = time.time()
    with mp.get_context('spawn').Pool(4) as pool:
        for D, best in pool.imap_unordered(_run, [(D, starts, i) for i, D in enumerate(reps)]):
            tag = 'ESCAPE' if best and best[0] < 12 else 'no escape'
            print('triple', D, 'best exact real decoder cost', best[0] if best else None, '->', tag, '%.0fs' % (time.time() - t0), flush=True)
            if best and best[0] < 12: print('   terms:', best[1], flush=True)
