#!/usr/bin/env python3
"""Heuristic real-coefficient escape search for local plane-port decoders (evidence, not proof).

For a group D of matched planes, minimise  ||mask residual||^2 + lam * sum_k t_k * |u_k||v_k|  over real rank-one
terms u_k v_k^T whose plane supports are fixed per slot (L-BFGS, lam raised in steps), then prune by weight, refit
the survivors exactly by least squares and record the TRUE cost (sum of binary pairing tariffs of the actual
supports) whenever the refit is exact (max residual < 1e-9).  Fixed mask cells: diagonal 1; 0 inside a plane and
between non-orthogonal planes; entries between orthogonal planes are free.  A real solution space contains every
rational one, so a cost below 4|D| would be an escape for every denominator.  "No escape" is local-search evidence.

usage:  real_escape.py triples-open STARTS | quads-open N STARTS SEED | quads-degenerate N STARTS
        | c5 STARTS | groups "a,b,c;d,e,f,g" STARTS
"""
import gzip, io, itertools, json, random, sys, tarfile, time, multiprocessing as mp
from pathlib import Path
import numpy as np, scipy.optimize as so
ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MATCHING = ROOT / 'research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json'
TRI = ROOT / 'research/three-plane-rank-dual/CERTIFICATES.json'
QUAD = ROOT / 'research/four-plane-rank-dual/CERT-INDEX.bin.gz'
dot = lambda x, y: (x & y).bit_count() & 1
def lead(b): return 1 << (b.bit_length() - 1)
def reduce(basis, v):
    for b in basis:
        if v & lead(b): v ^= b
    return v
def add(basis, v):
    basis = list(basis); v = reduce(basis, v)
    if not v: return tuple(basis)
    L = lead(v); basis = [b ^ v if b & L else b for b in basis] + [v]
    return tuple(sorted(basis, reverse=True))
def span(vs):
    s = ()
    for v in vs: s = add(s, v)
    return s
def contains(s, v): return reduce(s, v) == 0
def pair_rank(A, B):
    """rank over F2 of the pairing matrix between bases A and B"""
    rows = [sum(dot(x, y) << k for k, y in enumerate(B)) for x in A]
    r = 0
    for bit in range(len(B)):
        piv = next((i for i in range(r, len(rows)) if rows[i] >> bit & 1), None)
        if piv is None: continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> bit & 1: rows[i] ^= rows[r]
        r += 1
    return r

with tarfile.open(ARCHIVE) as _a:
    labels = [r['q'] for r in json.loads(_a.extractfile(_a.getmember(MEMBER)).read())['recipes']]
pairs = json.loads(MATCHING.read_text())['matching']
planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
def sp(D): return span([v for i in D for v in planes[i]])
def tar(A, R): return pair_rank(sp(A), sp(R)) if A and R else 0
COPIES = 2
def search(D, starts, seed):
    global COPIES
    COPIES = 2 if len(D) <= 5 else 1
    t0 = time.time()
    def L(*a): print('[%s %5.0fs]' % (','.join(map(str, D)), time.time() - t0), *a, flush=True)
    rng = np.random.default_rng(seed); g = len(D); m = 2 * g
    fixed = [(p, q, float(p == q)) for p in range(m) for q in range(m) if p == q or p // 2 == q // 2 or not ORTH[D[p // 2]][D[q // 2]]]
    P = np.array([f[0] for f in fixed]); Q = np.array([f[1] for f in fixed]); T = np.array([f[2] for f in fixed])
    subsets = [tuple(i for i in range(g) if x >> i & 1) for x in range(1, 1 << g)]
    if g >= 5:   # keep the type list tractable: small sides, the whole group, and complements of single planes
        full = tuple(range(g)); co = [tuple(j for j in range(g) if j != i) for i in range(g)]
        subsets = [S for S in subsets if len(S) <= 2] + [full] + co
    types = [(A, R, tar([D[i] for i in A], [D[i] for i in R])) for A in subsets for R in subsets]
    types = [t for t in types if t[2] > 0] * COPIES
    K = len(types)
    L('start: %d term slots (%d types x %d copies), %d fixed mask cells, %d starts' % (K, K // COPIES, COPIES, len(fixed), starts))
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
        resid = float(np.abs((U.T @ V)[P, Q] - T).max())
        order = [k for k in np.argsort(-wts) if wts[k] > 1e-6]
        # smallest prefix (by weight) whose exact refit works; try a few prefix sizes
        for n_keep in range(4, len(order) + 1):
            active = order[:n_keep]
            if sum(cost[k] for k in active) >= (best[0] if best else 1e9): break
            res, Ka = refit(active)
            y0 = np.concatenate([U[active].ravel(), V[active].ravel()])
            try:
                r = so.least_squares(res, y0, method='trf', max_nfev=1500)
            except (np.linalg.LinAlgError, ValueError) as e:   # e.g. "SVD did not converge" on a degenerate refit
                L('start %d: refit of %d terms failed (%s), skipping prefix' % (s + 1, Ka, e)); continue
            if np.abs(r.fun).max() < 1e-9:
                Ua = r.x[:Ka*m].reshape(Ka, m) * MU[active]; Va = r.x[Ka*m:].reshape(Ka, m) * MV[active]
                true = 0
                for k in range(Ka):
                    A = tuple(sorted({p // 2 for p in range(m) if abs(Ua[k, p]) > 1e-9})); R = tuple(sorted({p // 2 for p in range(m) if abs(Va[k, p]) > 1e-9}))
                    true += tar([D[i] for i in A], [D[i] for i in R])
                improved = best is None or true < best[0]
                if improved:
                    best = (true, [(types[k][0], types[k][1]) for k in active])
                L('start %d: exact decoder with %d terms, nominal %d, true cost %d%s' % (s + 1, Ka, int(sum(cost[k] for k in active)), true, '  NEW BEST' if improved else ''))
                break
        else:
            L('start %d: no exact refit (max residual after relaxation %.2e, nonzero terms %d)' % (s + 1, resid, len(order)))
    L('done: best exact real decoder cost', best[0] if best else None)
    return best

def _run(a):
    D, st, sd = a
    return D, search(D, st, sd)

def open_triples():
    """one example per open class of research/three-plane-rank-dual (classes without an all-field certificate)"""
    return [tuple(c['example']) for c in json.loads(TRI.read_text())['classes'] if 'f2_minimum_mass' in c]

def open_quads():
    idx = gzip.decompress(QUAD.read_bytes())
    return [q for n, q in enumerate(itertools.combinations(range(NP), 4)) if (idx[2 * n] | idx[2 * n + 1] << 8) == 0]

def degenerate_quads(n):
    """the n quadruples with the smallest whole-group tariff t(D, D), ties broken by more non-orthogonal pairs"""
    cand = [(tar(D, D), -sum(not ORTH[a][b] for a, b in itertools.combinations(D, 2)), D)
            for D in itertools.combinations(range(NP), 4)]
    return [D for _, _, D in sorted(cand)[:n]]

def c5_groups():
    """the induced 5-cycles of the non-orthogonality graph, each also extended by its 1 and 2 most degenerate planes"""
    non = [[i != j and not ORTH[i][j] for j in range(NP)] for i in range(NP)]
    holes = sorted(S for S in itertools.combinations(range(NP), 5) if all(sum(non[a][b] for b in S) == 2 for a in S))
    out = []
    for H in holes:
        out.append(H); cur = list(H)
        for _ in range(2):
            best = min((x for x in range(NP) if x not in cur), key=lambda x: (tar(cur + [x], cur + [x]), x))
            cur = cur + [best]; out.append(tuple(cur))
    return holes, out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'triples-open':
        groups, starts = open_triples(), int(sys.argv[2])
    elif mode == 'quads-open':
        n, starts, seed = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        oq = open_quads(); print('open quadruples', len(oq), flush=True)
        groups = random.Random(seed).sample(oq, n)
    elif mode == 'quads-degenerate':
        groups, starts = degenerate_quads(int(sys.argv[2])), int(sys.argv[3])
    elif mode == 'c5':
        holes, groups = c5_groups(); starts = int(sys.argv[2]); print('induced C5s', len(holes), 'groups', len(groups), flush=True)
    else:
        groups = [tuple(int(x) for x in g.split(',')) for g in sys.argv[2].split(';')]; starts = int(sys.argv[3])
    t0 = time.time()
    with mp.get_context('spawn').Pool(4) as pool:
        for D, best in pool.imap_unordered(_run, [(D, starts, i) for i, D in enumerate(groups)]):
            base = 4 * len(D); tag = 'ESCAPE' if best and best[0] < base else 'no escape'
            print('RESULT group', D, 'baseline', base, 'best exact real decoder cost', best[0] if best else None, '->', tag,
                  '%.0fs' % (time.time() - t0), flush=True)
            if best and best[0] < base: print('   terms:', best[1], flush=True)
