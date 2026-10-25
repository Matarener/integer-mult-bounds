# Step 2: can the LP skeleton be realized as an exact REAL decoder of the full strict 112-port mask?
# Menu = skeleton term types (A, R) from step1c (COPIES each) + all single-plane diagonal types ({i},{i})
# (2 copies; these alone give the classic 224) + optionally single cross types ({i},{j}).
# Minimise ||residual on fixed cells||^2 + lam * sum_k t_k |u_k||v_k| (L-BFGS, lam raised), prune by weight,
# refit exactly with a sparse analytic Jacobian (least_squares, lsmr), record TRUE cost of actual supports.
# usage: step2_global.py STARTS SEED [copies] [cross 0/1]
import sys, json, time, itertools
import numpy as np, scipy.optimize as so, scipy.sparse as sp
sys.path.insert(0, sys.argv[5] if len(sys.argv) > 5 else r'D:\Math\imb-v4pr\research\plane-port-global-rank-dual\search')
sys.argv_saved = list(sys.argv); sys.argv = sys.argv[:1]
import real_escape as RE
sys.argv = sys.argv_saved
NP, ORTH, tar = RE.NP, RE.ORTH, RE.tar
T0 = time.time()
def L(*a): print('%6.0fs' % (time.time() - T0), *a, flush=True)
starts, seed = int(sys.argv[1]), int(sys.argv[2])
COPIES = int(sys.argv[3]) if len(sys.argv) > 3 else 2
CROSS = int(sys.argv[4]) if len(sys.argv) > 4 else 0
skel = json.load(open('step1c_skeleton.json'))
types = {}
for o in skel: types[(tuple(o['A']), tuple(o['R']))] = o['t']
for i in range(NP): types[((i,), (i,))] = 2
if CROSS:
    for i in range(NP):
        for j in range(NP):
            if i != j and not ORTH[i][j]: types[((i,), (j,))] = tar([i], [j])
TL = [(A, R, t) for (A, R), t in types.items() for _ in range(COPIES if ((len(A) > 1 or len(R) > 1) or A == R) else 1)]
K = len(TL); m = 2 * NP
fixed = [(p, q, float(p == q)) for p in range(m) for q in range(m) if p == q or p // 2 == q // 2 or not ORTH[p // 2][q // 2]]
P = np.array([f[0] for f in fixed]); Q = np.array([f[1] for f in fixed]); T = np.array([f[2] for f in fixed])
MU = np.zeros((K, m)); MV = np.zeros((K, m))
for k, (A, R, t) in enumerate(TL):
    for i in A: MU[k, 2*i:2*i+2] = 1
    for i in R: MV[k, 2*i:2*i+2] = 1
cost = np.array([t for _, _, t in TL], float)
L('slots', K, 'types', len(types), 'fixed cells', len(fixed), 'copies', COPIES, 'cross', CROSS)
def unpack(x): return x[:K*m].reshape(K, m) * MU, x[K*m:].reshape(K, m) * MV
def f(x, lam):
    U, V = unpack(x); Mx = U.T @ V; r = Mx[P, Q] - T
    nu = (U*U).sum(1); nv = (V*V).sum(1); w = np.sqrt(nu*nv + 1e-8)
    GM = np.zeros((m, m)); np.add.at(GM, (P, Q), 2*r)
    gU = V @ GM.T + lam * (cost*nv/w)[:, None] * U; gV = U @ GM + lam * (cost*nu/w)[:, None] * V
    return (r*r).sum() + lam*(cost*w).sum(), np.concatenate([(gU*MU).ravel(), (gV*MV).ravel()])
def refit(active, U, V):
    # variables: u_k[p] for p in supp MU[k], v_k[q] for q in supp MV[k]
    uidx = [np.flatnonzero(MU[k]) for k in active]; vidx = [np.flatnonzero(MV[k]) for k in active]
    off = np.cumsum([0] + [len(a) + len(b) for a, b in zip(uidx, vidx)])
    cell = {(p, q): c for c, (p, q) in enumerate(zip(P, Q))}
    rowsJ, colsJ, kind = [], [], []   # entry: d r_c / d u_k[p] = v_k[q]  or  d/d v_k[q] = u_k[p]
    for j, k in enumerate(active):
        for a, p in enumerate(uidx[j]):
            for b, q in enumerate(vidx[j]):
                c = cell.get((p, q))
                if c is None: continue
                rowsJ += [c, c]; colsJ += [off[j] + a, off[j] + len(uidx[j]) + b]
                kind += [(off[j] + len(uidx[j]) + b), (off[j] + a)]   # value source index
    rowsJ = np.array(rowsJ); colsJ = np.array(colsJ); kind = np.array(kind)
    # residual via the same entries: r_c = sum over (u*v) pairs; every (c, u, v) appears once in pairs of entries
    pu = colsJ[0::2]; pv = colsJ[1::2]; pc = rowsJ[0::2]
    y0 = np.concatenate([np.concatenate([U[k, uidx[j]], V[k, vidx[j]]]) for j, k in enumerate(active)])
    def res(y):
        r = -T.copy(); np.add.at(r, pc, y[pu] * y[pv]); return r
    def jac(y): return sp.csr_matrix((y[kind], (rowsJ, colsJ)), shape=(len(T), len(y0)))
    out = so.least_squares(res, y0, jac=jac, method='trf', tr_solver='lsmr', max_nfev=300, xtol=1e-15, ftol=1e-15, gtol=1e-15)
    y = out.x; err = float(np.abs(res(y)).max())
    true = 0
    for j, k in enumerate(active):
        uu = y[off[j]:off[j] + len(uidx[j])]; vv = y[off[j] + len(uidx[j]):off[j+1]]
        A = sorted({p // 2 for p, val in zip(uidx[j], uu) if abs(val) > 1e-9}); R = sorted({q // 2 for q, val in zip(vidx[j], vv) if abs(val) > 1e-9})
        true += tar(A, R) if A and R else 0
    return err, true
rng = np.random.default_rng(seed); best = None
for s in range(starts):
    x = rng.normal(scale=0.5, size=2*K*m)
    for lam in (0.0, 0.001, 0.003, 0.01, 0.02, 0.05):
        x = so.minimize(f, x, args=(lam,), jac=True, method='L-BFGS-B', options={'maxiter': 4000}).x
    U, V = unpack(x); wts = np.sqrt((U*U).sum(1) * (V*V).sum(1))
    r = (U.T @ V)[P, Q] - T
    # reweighted sparsification: repeatedly drop tiny terms and re-solve with lam = 0 on the survivors
    alive = wts > 1e-3 * wts.max()
    for rnd in range(6):
        MUa = MU * alive[:, None]; MVa = MV * alive[:, None]
        def g(z, lam):
            U_, V_ = z[:K*m].reshape(K, m) * MUa, z[K*m:].reshape(K, m) * MVa; Mx = U_.T @ V_; r_ = Mx[P, Q] - T
            nu = (U_*U_).sum(1); nv = (V_*V_).sum(1); w = np.sqrt(nu*nv + 1e-8)
            GM = np.zeros((m, m)); np.add.at(GM, (P, Q), 2*r_)
            gU = V_ @ GM.T + lam*(cost*nv/w)[:, None]*U_; gV = U_ @ GM + lam*(cost*nu/w)[:, None]*V_
            return (r_*r_).sum() + lam*(cost*w*alive).sum(), np.concatenate([(gU*MUa).ravel(), (gV*MVa).ravel()])
        x = so.minimize(g, x, args=(0.002,), jac=True, method='L-BFGS-B', options={'maxiter': 4000}).x
        x = so.minimize(g, x, args=(0.0,), jac=True, method='L-BFGS-B', options={'maxiter': 4000, 'ftol': 1e-16, 'gtol': 1e-12}).x
        U, V = x[:K*m].reshape(K, m) * MUa, x[K*m:].reshape(K, m) * MVa
        wts = np.sqrt((U*U).sum(1) * (V*V).sum(1)); r = (U.T @ V)[P, Q] - T
        new_alive = alive & (wts > 0.02 * np.median(wts[alive]))
        L('  round %d: alive %d, resid %.2e, nominal %d' % (rnd, alive.sum(), np.abs(r).max(), int(cost[alive].sum())))
        if new_alive.sum() == alive.sum(): break
        alive = new_alive
    active = [k for k in np.flatnonzero(alive)]
    try:
        err, true = refit(active, U, V)
    except Exception as e:
        L('refit failed', e); continue
    if err < 1e-9:
        if best is None or true < best[0]: best = (true, [TL[k][:2] for k in active])
        L('start %d: EXACT decoder, %d terms, true cost %d%s' % (s+1, len(active), true, '  NEW BEST' if best[0] == true else ''))
    else:
        L('start %d: refit residual %.2e (not exact), %d terms, nominal %d' % (s+1, err, len(active), int(cost[active].sum())))
L('BEST exact real decoder cost', best[0] if best else None, '(baseline 224)')
if best: json.dump({'cost': best[0], 'terms': best[1]}, open('step2_best_seed%d.json' % seed, 'w'))
