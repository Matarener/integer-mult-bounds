# V4 quick test of the plane-refined clique inequalities.
#
# For a clique Q (pairwise non-orthogonal planes) the decoder restricted to Q's ports is the identity.  For a plane i in Q
# the submatrix (all ports of Q) x (2 ports of i) has rank 2, so at least 2 terms have plane i on the READER side and a
# SOURCE plane in Q.  Symmetrically (2 ports of i) x (all ports of Q): at least 2 terms have i on the SOURCE side and a
# READER plane in Q.  Columns (Q, i, side), value 2.  Summing over i in Q gives back the old clique inequality.
# Dual LP: max sum 2*lam  s.t. for every ordered span pair (W_A, W_R): sum of lam over touched columns <= tariff(W_A, W_R).
# Same cliques as the old LP's active set (292 cliques, strict LB 129.99) -> a fair comparison.
# Rows: start from the old LP's rows, then exhaustive separation over all 39087^2 pairs; strict float64 certificate.
import json, os, pickle, sys, time
import numpy as np, scipy.optimize as so, scipy.sparse as sp
from v4lib import *
T0 = time.time(); MAX_ROUNDS = int(os.environ.get('V4_ROUNDS', '40')); TL = float(os.environ.get('V4_TIME_LIMIT_SEC', '1e9'))
def log(*a): print(time.strftime('%H:%M:%S'), '%6.0fs' % (time.time() - T0), *a, flush=True)
d = pickle.load(open('v4_spans.pkl', 'rb')); spans, inside = d['spans'], d['inside']; n = len(spans)
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
z = np.load('v4_masks.npz'); M, P, dimA = z['M'], z['P'], z['dimA'].astype(np.int16)
TF = 'v4_tariff.u8'; B = 100
if not os.path.exists(TF + '.done'):
    tarm = np.memmap(TF, dtype=np.uint8, mode='w+', shape=(n, n))
    for a0 in range(0, n, B):
        inter = np.bitwise_count(M[a0:a0+B, None, :] & P[None, :, :]).sum(axis=2)
        tarm[a0:a0+B] = (dimA[a0:a0+B, None] - np.round(np.log2(inter)).astype(np.int16)).astype(np.uint8)
        if (a0 // B) % 50 == 0: log('tariff rows', a0 + B, '/', n)
    tarm.flush(); del tarm; open(TF + '.done', 'w').write('ok')
tarm = np.memmap(TF, dtype=np.uint8, mode='r', shape=(n, n))
for a, r in [(0, 0), (5, 77), (n - 1, n - 2), (1234, 30000)]: assert int(tarm[a, r]) == pair_rank(spans[a], spans[r])
log('tariff matrix ready')

res_old = json.load(open('v4_pilot_result.json'))
cliques = [tuple(sorted(c['X'])) for c in res_old['columns'] if c['kind'] == 'clique']
log('cliques from the old LP active set:', len(cliques), 'old strict LB', res_old['LB_strict'])
cols = [(Q, i, s) for Q in cliques for i in Q for s in ('R', 'A')] + [(Q, -1, 'C') for Q in cliques]   # C = old clique column
K = len(cols); log('refined columns (clique, plane, side):', K)
imask = np.array([sum(1 << v for v in ins) for ins in inside], dtype=np.uint64)
qm = np.array([sum(1 << v for v in Q) for Q, _, _ in cols], dtype=np.uint64)
im = np.array([(1 << i) if i >= 0 else 0 for _, i, _ in cols], dtype=np.uint64)
isR = np.array([s == 'R' for _, _, s in cols]); isA = np.array([s == 'A' for _, _, s in cols]); isC = np.array([s == 'C' for _, _, s in cols])
# Meet[x, c] = planes(span x) meets Q_c ; Has[x, c] = plane i_c in planes(span x)
Meet = np.zeros((n, K), dtype=bool); Has = np.zeros((n, K), dtype=bool)
for a0 in range(0, n, 2000):
    Meet[a0:a0+2000] = (imask[a0:a0+2000, None] & qm[None, :]) != 0
    Has[a0:a0+2000] = (imask[a0:a0+2000, None] & im[None, :]) != 0
log('membership matrices ready')
def touch_row(a, r):   # columns touched by a term of type (W_a source, W_r reader)
    return np.nonzero((isR & Has[r] & Meet[a]) | (isA & Has[a] & Meet[r]) | (isC & Meet[a] & Meet[r]))[0].astype(np.int32)
rows = sorted(set(map(tuple, pickle.load(open('v4_pilot_state.pkl', 'rb'))['rows'])))
full = [i for i in range(n) if len(inside[i]) == NP][0]; rows = sorted(set(rows) | {(full, full)})
log('initial rows (old LP rows):', len(rows))
obj = np.array([2.0 * len(Q) if sd == 'C' else 2.0 for Q, _, sd in cols]); hist = []
for it in range(MAX_ROUNDS):
    if time.time() - T0 > TL: log('time limit'); break
    t0 = time.time()
    cl = [touch_row(a, r) for a, r in rows]
    ip = np.zeros(len(cl) + 1, dtype=np.int64); ip[1:] = np.cumsum([len(c) for c in cl])
    A = sp.csr_matrix((np.ones(ip[-1]), np.concatenate(cl), ip), shape=(len(cl), K))
    rhs = np.array([float(tarm[a, r]) for a, r in rows])
    res = so.linprog(-obj, A_ub=A, b_ub=rhs, bounds=(0, None), method='highs'); assert res.status == 0
    lam = res.x; val = -res.fun; act = np.nonzero(lam > 1e-12)[0]
    # exhaustive separation: V[a, r] = sum_c lam_c * (isR_c Meet[a,c] Has[r,c] + isA_c Has[a,c] Meet[r,c])
    LR = (lam * isR)[act]; LA = (lam * isA)[act]; LC = (lam * isC)[act]
    MeetA = Meet[:, act].astype(np.float32); HasA = Has[:, act].astype(np.float32)
    RW = (HasA * LR).T.copy(); AW = (MeetA * LA).T.copy(); CW = (MeetA * LC).T.copy()
    cand = []; nviol = 0; worst = 0.0
    for a0 in range(0, n, B):
        V = MeetA[a0:a0+B] @ RW + HasA[a0:a0+B] @ AW + MeetA[a0:a0+B] @ CW
        ex = V - tarm[a0:a0+B].astype(np.float32)
        ia, ir = np.nonzero(ex > 1e-6); nviol += len(ia)
        if len(ia):
            e = ex[ia, ir]; worst = max(worst, float(e.max()))
            order = np.lexsort((-e, ia)); last = -1; cnt = 0
            for k in order:
                if ia[k] != last: last, cnt = ia[k], 0
                if cnt < 2: cand.append((float(e[k]), a0 + int(ia[k]), int(ir[k]))); cnt += 1
    cand.sort(reverse=True); add = [(a, r) for _, a, r in cand[:1500]]
    rows = sorted(set(rows) | set(add))
    kinds = {k: round(float((lam * m) @ obj), 3) for k, m in (('clique', isC), ('plane_R', isR), ('plane_A', isA))}
    hist.append({'round': it, 'LB_LP': round(val, 4), 'value_by_kind': kinds, 'violations': nviol, 'worst_excess': round(worst, 5), 'added': len(add),
                 'rows': len(rows), 'active_cols': int(len(act)), 'sec': round(time.time() - t0, 1)})
    log(hist[-1]); json.dump(hist, open('v4_refined.progress.json', 'w'))
    last_lam = lam
    if not add: break
# strict certificate
lam = np.where(last_lam > 1e-12, last_lam, 0.0); act = np.nonzero(lam > 0)[0]
LR = (lam * isR)[act]; LA = (lam * isA)[act]; LC = (lam * isC)[act]
MeetA = Meet[:, act].astype(np.float64); HasA = Has[:, act].astype(np.float64)
RW = (HasA * LR).T.copy(); AW = (MeetA * LA).T.copy(); CW = (MeetA * LC).T.copy(); smin = 1.0
for a0 in range(0, n, B):
    V = MeetA[a0:a0+B] @ RW + HasA[a0:a0+B] @ AW + MeetA[a0:a0+B] @ CW; tar = tarm[a0:a0+B].astype(np.float64)
    assert not ((tar == 0) & (V > 1e-12)).any(), 'tariff-0 pair touched'
    pos = V > 0
    if pos.any(): smin = min(smin, float((tar[pos] / V[pos]).min()))
s = smin * (1 - 1e-9); LB = float(s * (lam @ obj))
json.dump({'LB_strict': LB, 'LB_LP_last': hist[-1]['LB_LP'], 'scale': s, 'rounds': len(hist), 'old_LB_same_cliques': res_old['LB_strict'],
           'columns': [{'Q': list(cols[c][0]), 'i': cols[c][1], 'side': cols[c][2], 'lam': float(lam[c] * s)} for c in act]},
          open('v4_refined_result.json', 'w'), indent=0)
log('DONE strict LB (plane-refined, same %d cliques) %.4f   vs old clique LB %.4f' % (len(cliques), LB, res_old['LB_strict']))
