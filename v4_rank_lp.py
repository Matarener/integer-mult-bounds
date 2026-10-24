# V4 path 2: strengthen the clique-dual LP lower bound on the plane-port decoder tariff.
#
# Model (as in v4_dual_lb.py / v4_cg2.py): decoder M = sum_k u_k v_k^T on 112 ports, port p in plane E(p);
# M_pp = 1, M_pq = 0 when E(p), E(q) are non-orthogonal (incl. same plane), free when orthogonal.
# Term k touches a plane set X if its source planes meet X and its reader planes meet X.
# For any plane set X: #terms touching X >= rank M[X,X] >= r(X) := min-rank of the partial matrix on X's ports.
# Dual LP: max sum_X lam_X r(X)  s.t.  for every ordered span pair (W_A, W_R): sum_{X touched} lam_X <= tariff.
#
# Columns X:
#  (a) cliques Q of the non-orthogonality graph, r(Q) = 2|Q| (identity block);
#  (b) S u K, S an odd hole/antihole core of the non-orthogonality graph, K a clique all of whose planes are
#      non-orthogonal to every plane of S: M[X,X] = diag(M[S,S], I) (forced zeros), so r(X) = r(S) + 2|K|.
#      r(S) is computed exactly by SAT (rank <= k decomposition M = U V over F2).
# Column generation: exact MILP pricing over all cliques, and over all K for each core (parallel, 4 workers).
# Row generation: exhaustive separation over all 39,087^2 ordered pairs.  Final float64 certificate over all pairs.
import json, os, pickle, sys, time, itertools, multiprocessing as mp
import numpy as np, scipy.optimize as so, scipy.sparse as sp
from v4lib import *

T_START = time.time(); TIME_LIMIT = float(os.environ.get('V4_TIME_LIMIT_SEC', '1e12'))
def log(*a): print(time.strftime('%H:%M:%S'), '%6.0fs' % (time.time() - T_START), *a, flush=True)
def ram():
    if os.name == 'nt': return -1.0
    mi = dict((l.split(':')[0], int(l.split()[1])) for l in open('/proc/meminfo'))
    return round(100.0 * (1 - mi['MemAvailable'] / mi['MemTotal']), 1)

labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
NON = [[i != j and not ORTH[i][j] for j in range(NP)] for i in range(NP)]
nbr = [sum(1 << j for j in range(NP) if NON[i][j]) for i in range(NP)]

# ---------------- cores: odd holes / antiholes of the non-orthogonality graph -----------------
def induced_cycles(adj, L):
    """all induced cycles of length L in graph adj (list of sets), each once (min vertex first, then smaller nbr)."""
    out = []
    def ext(path, pset):
        v = path[-1]
        if len(path) == L:
            if path[0] in adj[v] and path[1] < path[-1]: out.append(tuple(path))
            return
        for w in adj[v]:
            if w <= path[0] or w in pset: continue
            # chordless: w adjacent only to v among path (and to path[0] only if closing at last step)
            bad = False
            for u in path[:-1]:
                if w in adj[u] and not (u == path[0] and len(path) == L - 1): bad = True; break
            if bad: continue
            ext(path + [w], pset | {w})
    for s in range(len(adj)):
        ext([s], {s})
    return out
adjN = [set(j for j in range(NP) if NON[i][j]) for i in range(NP)]
adjO = [set(j for j in range(NP) if ORTH[i][j]) for i in range(NP)]
cores = []
for L in (5, 7, 9):
    h = induced_cycles(adjN, L); cores += [('hole', L, c) for c in h]; log('odd holes length', L, ':', len(h))
    if L > 5:
        a = induced_cycles(adjO, L); cores += [('antihole', L, c) for c in a]; log('odd antiholes length', L, ':', len(a))

def omega_of(S):
    S = list(S); best = 0
    for r in range(len(S), 0, -1):
        for c in itertools.combinations(S, r):
            if all(NON[a][b] for a, b in itertools.combinations(c, 2)): return r
    return 0

def minrank_core(S, budget=200000):
    """lower bound on the min-rank over F2 of the partial matrix on the 2|S| ports of plane set S.
    k runs up from 2*omega(S); 'rank <= k' is tested by SAT (M = U V).  UNSAT proves r > k.  If the solver runs out of
    its conflict budget at some k, we return k as a (still valid) lower bound and flag it as not exact."""
    from pysat.solvers import Glucose4
    S = list(S); m = 2 * len(S)
    plane_of = [S[p // 2] for p in range(m)]
    fixed = {}
    for p in range(m):
        for q in range(m):
            if p == q: fixed[p, q] = 1
            elif plane_of[p] == plane_of[q] or NON[plane_of[p]][plane_of[q]]: fixed[p, q] = 0
    lo = 2 * omega_of(S)
    for k in range(lo, m + 1):
        cnt = [0]
        def new(): cnt[0] += 1; return cnt[0]
        U = [[new() for _ in range(k)] for _ in range(m)]; V = [[new() for _ in range(m)] for _ in range(k)]
        cls = []
        for (p, q), t in fixed.items():
            gs = []
            for j in range(k):
                g = new(); a, b = U[p][j], V[j][q]
                cls += [[-g, a], [-g, b], [g, -a, -b]]; gs.append(g)
            x = gs[0]
            for g in gs[1:]:
                y = new(); cls += [[-y, x, g], [-y, -x, -g], [y, -x, g], [y, x, -g]]; x = y
            cls.append([x] if t else [-x])
        with Glucose4(bootstrap_with=cls) as s:
            s.conf_budget(budget); r = s.solve_limited()
        if r is True: return k, lo, True
        if r is None: return k, lo, False      # r(S) >= k proven (all smaller k were UNSAT)
    return m, lo, True

# ---------------- spans, tariff matrix, rows -----------------
d = pickle.load(open('v4_spans.pkl', 'rb')); spans, inside = d['spans'], d['inside']; n = len(spans)
imask = np.array([sum(1 << v for v in ins) for ins in inside], dtype=np.uint64)
z = np.load('v4_masks.npz'); M, P, dimA = z['M'], z['P'], z['dimA'].astype(np.int16)
TF, TFD = 'v4_tariff.u8', 'v4_tariff.done.json'; B = 100
done = json.load(open(TFD))['rows'] if os.path.exists(TFD) else 0
tarm = np.memmap(TF, dtype=np.uint8, mode='r+' if os.path.exists(TF) else 'w+', shape=(n, n))
if done < n:
    log('building tariff matrix from row', done)
    for a0 in range(done, n, B):
        inter = np.bitwise_count(M[a0:a0+B, None, :] & P[None, :, :]).sum(axis=2)
        tarm[a0:a0+B] = (dimA[a0:a0+B, None] - np.round(np.log2(inter)).astype(np.int16)).astype(np.uint8)
        if (a0 // B) % 50 == 0: tarm.flush(); json.dump({'rows': a0 + B}, open(TFD, 'w')); log('tariff rows', a0 + B, 'RAM', ram())
    tarm.flush(); json.dump({'rows': n}, open(TFD, 'w'))
del tarm; tarm = np.memmap(TF, dtype=np.uint8, mode='r', shape=(n, n))
for a, r in [(0, 0), (5, 77), (n - 1, n - 2), (1234, 30000), (39000, 17)]:
    assert int(tarm[a, r]) == pair_rank(spans[a], spans[r])
log('tariff matrix ready')

# ---------------- column store -----------------
cols = {}   # frozenset X -> (value, kind)
def add_col(X, val, kind):
    X = frozenset(X)
    if X not in cols or cols[X][0] < val: cols[X] = (float(val), kind); return True
    return False
for i in range(NP): add_col([i], 2, 'clique')
for i in range(NP):
    for j in range(i + 1, NP):
        if NON[i][j]: add_col([i, j], 4, 'clique')
ST = 'v4_rank_state.pkl'
if os.path.exists(ST):
    st = pickle.load(open(ST, 'rb')); rowsT, hist = st['rows'], st['hist']
    for X, (v, k) in st['cols'].items(): add_col(X, v, k)
    core_info = st['core_info']; log('resumed', len(rowsT), 'rows', len(cols), 'cols', len(hist), 'iters')
else:
    hist = []
    st0 = pickle.load(open('v4_cg2_state.pkl', 'rb')); rowsT = sorted(set(map(tuple, st0['rows'])))
    log('rows from v4_cg2 state:', len(rowsT))
    res = [None] * len(cores); t0 = time.time()
    with mp.Pool(4) as pool:
        for k, (idx, rv) in enumerate(pool.imap_unordered(_mr_idx, list(enumerate(c for _, _, c in cores)))):
            res[idx] = rv
            if k % 10 == 0 or k == len(cores) - 1:
                log('core min-rank SAT %d / %d done, last: %s %s r>=%d 2omega=%d exact=%s (%.0fs)' % (k + 1, len(cores), cores[idx][0] + str(cores[idx][1]), list(cores[idx][2]), rv[0], rv[1], rv[2], time.time() - t0))
    core_info = []
    for (kind, L, c), (r, lo, exact) in zip(cores, res):
        core_info.append({'kind': kind, 'L': L, 'S': list(c), 'r': r, 'two_omega': lo, 'exact': exact})
    json.dump(core_info, open('v4_rank_cores.json', 'w'), indent=0)
    from collections import Counter
    log('core min-ranks (kind, L, r, 2omega): count', dict(Counter((x['kind'], x['L'], x['r'], x['two_omega'], x['exact']) for x in core_info)))
gain_cores = [x for x in core_info if x['r'] > x['two_omega']]
log('cores with rank gain over cliques:', len(gain_cores))
for x in gain_cores: add_col(x['S'], x['r'], 'core')

# seed big cliques (greedy) so the LP starts near the clique optimum
import random; random.seed(7)
for _ in range(500):
    order = list(range(NP)); random.shuffle(order); Q = []
    for v in order:
        if all(NON[v][u] for u in Q): Q.append(v)
    add_col(Q, 2 * len(Q), 'clique')

# ---------------- pricing MILP -----------------
def price(args):
    """max val(X) - sum_t y_t touch_t(X) over X = S u K (S fixed core, K clique of common non-orth nbrs), or cliques if S empty."""
    S, rS, rowsA, rowsR, y, tl = args
    S = list(S)
    allowed = [i for i in range(NP) if i not in S and all(NON[i][s] for s in S)]
    na, nt = len(allowed), len(y)
    pos = {v: k for k, v in enumerate(allowed)}
    # variables: z (na, binary), a (nt), b (nt), s (nt) continuous [0,1]
    nv = na + 3 * nt
    c = np.zeros(nv); c[:na] = -2.0; c[na + 2 * nt:] = y
    rows, colsI, vals, lo, hi = [], [], [], [], []
    rr = 0
    def con(entries, l, h):
        nonlocal rr
        for j, v in entries: rows.append(rr); colsI.append(j); vals.append(v)
        lo.append(l); hi.append(h); rr += 1
    for i, j in itertools.combinations(allowed, 2):
        if ORTH[i][j]: con([(pos[i], 1), (pos[j], 1)], -np.inf, 1)
    Sset = set(S); const = rS
    for t in range(nt):
        A, R = rowsA[t], rowsR[t]
        fa, fr = bool(A & Sset), bool(R & Sset)
        ai, bi, si = na + t, na + nt + t, na + 2 * nt + t
        if fa: con([(ai, 1)], 1, 1)
        else:
            for v in A:
                if v in pos: con([(ai, 1), (pos[v], -1)], 0, np.inf)
        if fr: con([(bi, 1)], 1, 1)
        else:
            for v in R:
                if v in pos: con([(bi, 1), (pos[v], -1)], 0, np.inf)
        con([(si, 1), (ai, -1), (bi, -1)], -1, np.inf)
    A_ = sp.csr_matrix((vals, (rows, colsI)), shape=(rr, nv))
    integ = np.zeros(nv); integ[:na] = 1
    res = so.milp(c, constraints=so.LinearConstraint(A_, lo, hi), integrality=integ, bounds=so.Bounds(0, 1),
                  options={'time_limit': tl, 'disp': False})
    if res.x is None: return None
    K = [allowed[k] for k in range(na) if res.x[k] > 0.5]
    X = S + K
    val = rS + 2 * len(K)
    return {'X': X, 'val': val, 'profit_est': float(-res.fun + rS) if res.fun is not None else None,
            'optimal': res.status == 0, 'gap': getattr(res, 'mip_gap', None)}

# ---------------- main loop -----------------
def build(colsL):
    xm = np.array([sum(1 << v for v in X) for X, _ in colsL], dtype=np.uint64)
    out = np.zeros((n, len(xm)), dtype=np.uint8)
    for a0 in range(0, n, 2000): out[a0:a0+2000] = (imask[a0:a0+2000, None] & xm[None, :]) != 0
    return out
lam = None
for it in range(len(hist), 300):
    if time.time() - T_START > TIME_LIMIT: log('time limit reached'); break
    t0 = time.time()
    colsL = sorted(cols.items(), key=lambda kv: (len(kv[0]), sorted(kv[0])))
    K = len(colsL); Tm = build(colsL); obj = np.array([v for _, (v, _) in colsL])
    cl_ = [np.nonzero(Tm[a] & Tm[r])[0].astype(np.int32) for a, r in rowsT]
    ip = np.zeros(len(cl_) + 1, dtype=np.int64); ip[1:] = np.cumsum([len(c) for c in cl_])
    A = sp.csr_matrix((np.ones(ip[-1]), np.concatenate(cl_), ip), shape=(len(cl_), K)); del cl_
    rhs = np.array([float(tarm[a, r]) for a, r in rowsT])
    res = so.linprog(-obj, A_ub=A, b_ub=rhs, bounds=(0, None), method='highs'); assert res.status == 0, res.message
    lam = res.x; val = -res.fun; y = -res.ineqlin.marginals; slack = res.ineqlin.residual
    tlp = time.time() - t0
    # ---- column pricing (parallel)
    sup = np.nonzero(y > 1e-9)[0]
    rA = [frozenset(inside[rowsT[t][0]]) for t in sup]; rR = [frozenset(inside[rowsT[t][1]]) for t in sup]; yy = y[sup]
    # cheap rounds price cliques only; cores are priced when rows and cliques have settled (or every 5th round)
    core_round = (it % 5 == 4) or (hist and hist[-1]['added_rows'] == 0 and hist[-1]['new_cols'] == 0) or (hist and hist[-1]['added_rows'] < 50)
    jobs = [((), 0, rA, rR, yy, 600)] + ([(tuple(x['S']), x['r'], rA, rR, yy, 60) for x in gain_cores] if core_round else [])
    with mp.Pool(4) as pool: pr = pool.map(price, jobs)
    newc = 0; nonopt = 0; best_profit = 0.0
    for p in pr:
        if p is None: nonopt += 1; continue
        if not p['optimal']: nonopt += 1
        Xm = sum(1 << v for v in p['X'])
        touch = ((imask[[rowsT[t][0] for t in sup]] & np.uint64(Xm)) != 0) & ((imask[[rowsT[t][1] for t in sup]] & np.uint64(Xm)) != 0)
        profit = p['val'] - float(yy[touch].sum())
        best_profit = max(best_profit, profit)
        if profit > 1e-6 and add_col(p['X'], p['val'], 'core+K' if len(p['X']) and p['val'] != 2 * len(p['X']) else 'clique'): newc += 1
    tpr = time.time() - t0 - tlp
    # ---- row separation (exhaustive)
    act = np.nonzero(lam > 1e-12)[0]
    TW = (Tm[:, act].astype(np.float32) * lam[act].astype(np.float32)).T.copy(); Ta = Tm[:, act].astype(np.float32)
    cand = []; nviol = 0; worst = 0.0
    for a0 in range(0, n, B):
        ex = Ta[a0:a0+B] @ TW - tarm[a0:a0+B].astype(np.float32)
        ia, ir = np.nonzero(ex > 1e-6); nviol += len(ia)
        if len(ia):
            e = ex[ia, ir]; worst = max(worst, float(e.max()))
            order = np.lexsort((-e, ia)); last = -1; cnt = 0
            for k in order:
                if ia[k] != last: last, cnt = ia[k], 0
                if cnt < 2: cand.append((float(e[k]), a0 + int(ia[k]), int(ir[k]))); cnt += 1
    cand.sort(reverse=True); add_ = [(a, r) for _, a, r in cand[:1500]]
    pruned = 0
    if A.nnz > 14_000_000:
        keep = [t for t, s in zip(rowsT, slack) if s <= 1e-7]; pruned = len(rowsT) - len(keep); rowsT = keep
    rowsT = sorted(set(rowsT) | set(add_))
    kinds = {}
    for q in act: kinds[colsL[q][1][1]] = round(kinds.get(colsL[q][1][1], 0) + lam[q] * obj[q], 3)
    hist.append({'iter': it, 'core_round': bool(core_round), 'LB_LP': round(val, 6), 'value_by_kind': kinds, 'new_cols': newc, 'pricing_nonoptimal': nonopt,
                 'best_profit': round(best_profit, 6), 'violations': nviol, 'worst_excess': round(worst, 6),
                 'added_rows': len(add_), 'pruned': pruned, 'rows': len(rowsT), 'cols': len(cols), 'nnz': int(A.nnz),
                 'lp_sec': round(tlp, 1), 'pricing_sec': round(tpr, 1), 'sec': round(time.time() - t0, 1), 'ram': ram()})
    log(hist[-1])
    pickle.dump({'rows': rowsT, 'hist': hist, 'cols': dict(cols), 'core_info': core_info}, open(ST + '.tmp', 'wb')); os.replace(ST + '.tmp', ST)
    json.dump(hist, open('v4_rank.progress.json', 'w'), indent=0)
    last_cols, last_lam = colsL, lam
    if not add_ and newc == 0 and core_round: break

# ---------------- strict certificate -----------------
colsL, lam = last_cols, np.where(last_lam > 1e-12, last_lam, 0.0)
Tm = build(colsL); obj = np.array([v for _, (v, _) in colsL])
log('certifying over all', n, 'x', n, 'pairs')
for rnd in range(6):
    act = np.nonzero(lam > 0)[0]
    TW = (Tm[:, act].astype(np.float64) * lam[act]).T.copy(); Ta = Tm[:, act].astype(np.float64)
    smin = 1.0; bad = set()
    for a0 in range(0, n, B):
        V = Ta[a0:a0+B] @ TW; tar = tarm[a0:a0+B].astype(np.float64)
        z0 = (tar == 0) & (V > 0)
        for ia, ir in zip(*np.nonzero(z0)): bad |= set(act[np.nonzero(Tm[a0 + ia, act] & Tm[ir, act])[0]].tolist())
        ok = (V > 0) & ~z0
        if ok.any(): smin = min(smin, float((tar[ok] / V[ok]).min()))
    if not bad: break
    assert rnd < 5; log('zeroing columns touched by tariff-0 pairs:', len(bad)); lam[list(bad)] = 0.0
s = smin * (1 - 1e-9); LB = float(s * (lam @ obj))
out = {'LB_strict': LB, 'LB_LP_last': hist[-1]['LB_LP'] if hist else None, 'scale': s, 'iterations': len(hist),
       'converged': bool(hist) and hist[-1]['added_rows'] == 0 and hist[-1]['new_cols'] == 0,
       'pricing_all_optimal_last': bool(hist) and hist[-1]['pricing_nonoptimal'] == 0,
       'columns': [{'X': sorted(X), 'value': v, 'kind': k, 'lam': float(lam[q] * s)} for q, (X, (v, k)) in enumerate(colsL) if lam[q] > 0]}
json.dump(out, open('v4_rank_result.json', 'w'), indent=1)
log('DONE strict LB %.4f  converged=%s  pricing optimal=%s' % (LB, out['converged'], out['pricing_all_optimal_last']))
