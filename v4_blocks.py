# V4: clique LP + LOCAL BLOCK inequalities.
#
# Local block inequality.  For a plane set D let c(D) be the exact minimum cost of a local plane-port decoder on D
# (proved: c = 4 for one plane, 8 for every pair, 12 for 5,110 degenerate triples in 34 classes; CP-SAT, OPTIMAL/bound).
# Restricting any decoder M = sum_k u_k v_k^T to the ports of D gives a local decoder on D whose k-th term has planes
# (A_k & D, R_k & D), and tariff is monotone, so  sum_k tariff(A_k & D, R_k & D) >= c(D).
# Dual LP: max sum_Q lam_Q 2|Q| + sum_D mu_D c(D)
#          s.t. for every ordered span pair (W_A, W_R):  sum_{Q touched} lam_Q + sum_D mu_D tariff(A & D, R & D) <= tariff(W_A, W_R)
# Any feasible (lam, mu) gives  total tariff >= objective  (weak duality, same argument as before).
# Same 292 cliques as the old LP active set, for a fair comparison.  Exhaustive separation over all 39087^2 pairs
# (block part via exact one-hot x table factorisation), strict float64 certificate at the end.
import json, os, pickle, time
import numpy as np, scipy.optimize as so, scipy.sparse as sp
from v4lib import *
T0 = time.time(); MAX_ROUNDS = int(os.environ.get('V4_ROUNDS', '40'))
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

# ---- clique columns (0/1 touch) ----
res_old = json.load(open('v4_pilot_result.json'))
cliques = [tuple(sorted(c['X'])) for c in res_old['columns'] if c['kind'] == 'clique']
imask = np.array([sum(1 << v for v in ins) for ins in inside], dtype=np.uint64)
qm = np.array([sum(1 << v for v in Q) for Q in cliques], dtype=np.uint64)
Meet = np.zeros((n, len(cliques)), dtype=bool)
for a0 in range(0, n, 4000): Meet[a0:a0+4000] = (imask[a0:a0+4000, None] & qm[None, :]) != 0
KQ = len(cliques)

# ---- local block columns (table-valued consumption) ----
blocks = json.load(open('v4_local_blocks.json')); ND = len(blocks)
log('cliques', KQ, '| local blocks', ND, 'by size', {g: sum(1 for b in blocks if len(b['D']) == g) for g in (1, 2, 3)})
def sp_planes(ps): return span([v for i in ps for v in planes[i]])
tabs = []; offs = np.zeros(ND, dtype=np.int64); sizes = np.zeros(ND, dtype=np.int64); flat = []
for k, b in enumerate(blocks):
    D = b['D']; g = len(D); m = 1 << g
    spn = [sp_planes([D[i] for i in range(g) if x >> i & 1]) for x in range(m)]
    T = np.array([[pair_rank(spn[x], spn[y]) if x and y else 0 for y in range(m)] for x in range(m)], dtype=np.float64)
    tabs.append(T); offs[k] = len(flat); sizes[k] = m; flat.extend(T.ravel().tolist())
flat = np.array(flat)
# idx[x, k] = pattern of planes(span x) & D_k as a g-bit number
idx = np.zeros((n, ND), dtype=np.uint8)
for k, b in enumerate(blocks):
    for i, p in enumerate(b['D']): idx[:, k] |= (((imask >> np.uint64(p)) & np.uint64(1)).astype(np.uint8) << i)
log('block tables and pattern index ready')
cvals = np.array([b['c'] for b in blocks], dtype=float)
obj = np.concatenate([2.0 * np.array([len(Q) for Q in cliques]), cvals]); K = KQ + ND

def row_coeffs(a, r):
    cq = np.nonzero(Meet[a] & Meet[r])[0]
    vb = flat[offs + idx[a].astype(np.int64) * sizes + idx[r]]
    cb = np.nonzero(vb > 0)[0]
    return np.concatenate([cq, KQ + cb]).astype(np.int32), np.concatenate([np.ones(len(cq)), vb[cb]])

def block_G(act_b, mu, dtype):
    """(sum_m, n) matrix: row (k, x) at column r = mu_k * table_k[x, idx[r, k]]; built once per round"""
    if not len(act_b): return None
    return np.vstack([(mu[k] * tabs[k][:, idx[:, k]]).astype(dtype) for k in act_b])
def block_F(a0, a1, act_b, dtype):
    """(rows, sum_m) one-hot of the source pattern of each active block"""
    return np.hstack([(idx[a0:a1, k][:, None] == np.arange(sizes[k])[None, :]).astype(dtype) for k in act_b])
def V_block(a0, a1, act_b, G, dtype):
    return 0.0 if G is None else block_F(a0, a1, act_b, dtype) @ G

rows = sorted(set(map(tuple, pickle.load(open('v4_pilot_state.pkl', 'rb'))['rows'])))
full = [i for i in range(n) if len(inside[i]) == NP][0]; rows = sorted(set(rows) | {(full, full)})
log('initial rows (old LP rows):', len(rows))
hist = []
for it in range(MAX_ROUNDS):
    t0 = time.time()
    data = [row_coeffs(a, r) for a, r in rows]
    ip = np.zeros(len(data) + 1, dtype=np.int64); ip[1:] = np.cumsum([len(c) for c, _ in data])
    A = sp.csr_matrix((np.concatenate([v for _, v in data]), np.concatenate([c for c, _ in data]), ip), shape=(len(rows), K)); del data
    rhs = np.array([float(tarm[a, r]) for a, r in rows])
    res = so.linprog(-obj, A_ub=A, b_ub=rhs, bounds=(0, None), method='highs'); assert res.status == 0, res.message
    x = res.x; val = -res.fun; lam, mu = x[:KQ], x[KQ:]
    aq = np.nonzero(lam > 1e-12)[0]; ab = np.nonzero(mu > 1e-12)[0]
    MQ = Meet[:, aq].astype(np.float32); QW = (MQ * lam[aq].astype(np.float32)).T.copy(); G = block_G(ab, mu, np.float32)
    cand = []; nviol = 0; worst = 0.0
    for a0 in range(0, n, B):
        V = MQ[a0:a0+B] @ QW + V_block(a0, a0 + B, ab, G, np.float32)
        ex = V - tarm[a0:a0+B].astype(np.float32)
        ia, ir = np.nonzero(ex > 1e-6); nviol += len(ia)
        if len(ia):
            e = ex[ia, ir]; worst = max(worst, float(e.max()))
            order = np.lexsort((-e, ia)); last = -1; cnt = 0
            for k in order:
                if ia[k] != last: last, cnt = ia[k], 0
                if cnt < 2: cand.append((float(e[k]), a0 + int(ia[k]), int(ir[k]))); cnt += 1
        if a0 == 0: log('  separation started (round %d): LP %.4f, active cliques %d, active blocks %d' % (it, val, len(aq), len(ab)))
    cand.sort(reverse=True); add = [(a, r) for _, a, r in cand[:1500]]
    rows = sorted(set(rows) | set(add))
    byg = {g: round(float(sum(mu[k] * cvals[k] for k in ab if len(blocks[k]['D']) == g)), 3) for g in (1, 2, 3)}
    log('  G rows %d' % (0 if G is None else G.shape[0]))
    hist.append({'round': it, 'LB_LP': round(val, 4), 'clique_part': round(float(lam @ obj[:KQ]), 3), 'block_part_by_size': byg,
                 'violations': nviol, 'worst_excess': round(worst, 5), 'added': len(add), 'rows': len(rows), 'sec': round(time.time() - t0, 1)})
    log(hist[-1]); json.dump(hist, open('v4_blocks.progress.json', 'w'))
    last = (lam.copy(), mu.copy())
    if not add: break
# strict certificate
lam, mu = last; lam = np.where(lam > 1e-12, lam, 0.0); mu = np.where(mu > 1e-12, mu, 0.0)
aq = np.nonzero(lam > 0)[0]; ab = np.nonzero(mu > 0)[0]
MQ = Meet[:, aq].astype(np.float64); QW = (MQ * lam[aq]).T.copy(); G = block_G(ab, mu, np.float64); smin = 1.0
for a0 in range(0, n, B):
    V = MQ[a0:a0+B] @ QW + V_block(a0, a0 + B, ab, G, np.float64); tar = tarm[a0:a0+B].astype(np.float64)
    assert not ((tar == 0) & (V > 1e-9)).any(), 'tariff-0 pair charged'
    pos = V > 0
    if pos.any(): smin = min(smin, float((tar[pos] / V[pos]).min()))
s = smin * (1 - 1e-9); LB = float(s * (lam @ obj[:KQ] + mu @ cvals))
json.dump({'LB_strict': LB, 'scale': s, 'rounds': len(hist), 'old_LB_same_cliques': res_old['LB_strict'],
           'cliques': [{'Q': list(cliques[q]), 'lam': float(lam[q] * s)} for q in aq],
           'blocks': [{'D': blocks[k]['D'], 'c': blocks[k]['c'], 'mu': float(mu[k] * s)} for k in ab]},
          open('v4_blocks_result.json', 'w'), indent=0)
log('DONE strict LB (cliques + local blocks) %.4f   vs old clique-only LB %.4f' % (LB, res_old['LB_strict']))
