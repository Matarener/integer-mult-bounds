# V4 plane-port decoder: clique-dual LP lower bound with cutting planes, resumable, RAM-guarded.
# Dual LP: max sum_Q lam_Q 2|Q|  s.t. for every ordered pair (W_A, W_R) of plane-generated spans:
#   sum_{Q : Q meets planes(W_A) and planes(W_R)} lam_Q <= tariff(W_A, W_R) = dim W_A - dim(W_A & W_R^perp).
# Any lam satisfying ALL pairs gives a valid lower bound C >= sum lam_Q 2|Q| (weak duality, see v4_dual_lb.py).
# Loop: solve LP on current rows -> exhaustive separation over all 39087^2 pairs -> add up to 1500 most violated.
# Final certificate: exact float64 recheck over all pairs, lam scaled by min(1, tariff/value) -> strict LB.
import ctypes, json, os, pickle, random, sys, time
import numpy as np, scipy.optimize as so, scipy.sparse as sp
from v4lib import *

RAM_GUARD = 88.0
def ram():
    if os.name == 'nt':
        class MS(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong), ('ullTotalPhys', ctypes.c_ulonglong),
                        ('ullAvailPhys', ctypes.c_ulonglong), ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                        ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong), ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
        m = MS(); m.dwLength = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return 100.0 * (1 - m.ullAvailPhys / m.ullTotalPhys)
    mi = dict((l.split(':')[0], int(l.split()[1])) for l in open('/proc/meminfo'))
    return 100.0 * (1 - mi['MemAvailable'] / mi['MemTotal'])
TIME_LIMIT = float(os.environ.get('V4_TIME_LIMIT_SEC', '1e12')); T_START = time.time()
def guard(where):
    r = ram()
    if r >= RAM_GUARD:
        print(f'RAM GUARD {r:.1f}% >= {RAM_GUARD}% at {where}: state saved, stopping', flush=True); sys.exit(3)
    return r
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

d = pickle.load(open('v4_spans.pkl', 'rb')); spans, inside = d['spans'], d['inside']; n = len(spans)
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
cl = sorted(cl, key=lambda Q: (len(Q), sorted(Q))); K = len(cl)
for Q in cl: assert all(not orth[a][b] for a in Q for b in Q if a != b)
log('spans', n, 'cliques', K, 'RAM %.1f%%' % ram())
z = np.load('v4_masks.npz'); M, P, dimA = z['M'], z['P'], z['dimA'].astype(np.int16)

# tariff matrix on disk (n x n uint8), built once, resumable by row blocks
TF, TFD = 'v4_tariff.u8', 'v4_tariff.done.json'
B = 100
done = json.load(open(TFD))['rows'] if os.path.exists(TFD) else 0
tarm = np.memmap(TF, dtype=np.uint8, mode='r+' if os.path.exists(TF) else 'w+', shape=(n, n))
if done < n:
    log('building tariff matrix from row', done); t0 = time.time()
    for a0 in range(done, n, B):
        inter = np.bitwise_count(M[a0:a0+B, None, :] & P[None, :, :]).sum(axis=2)
        tarm[a0:a0+B] = (dimA[a0:a0+B, None] - np.round(np.log2(inter)).astype(np.int16)).astype(np.uint8)
        if (a0 // B) % 40 == 0:
            tarm.flush(); json.dump({'rows': a0 + B}, open(TFD, 'w'))
            log('tariff rows', a0 + B, '/', n, '%.0fs' % (time.time() - t0), 'RAM %.1f%%' % guard('tariff'))
    tarm.flush(); json.dump({'rows': n}, open(TFD, 'w'))
del tarm
tarm = np.memmap(TF, dtype=np.uint8, mode='r', shape=(n, n))
# sanity: tariff symmetric relation check on a sample vs exact pair_rank
for a, r in [(0, 0), (5, 77), (n - 1, n - 2), (1234, 30000), (39000, 17)]:
    assert int(tarm[a, r]) == pair_rank(spans[a], spans[r]), (a, r)
log('tariff matrix ready + spot-checked against pair_rank')

T = np.zeros((n, K), dtype=np.uint8)
insets = [set(x) for x in inside]
for q, Q in enumerate(cl):
    for i in range(n):
        if insets[i] & Q: T[i, q] = 1
log('touch matrix ready')

ST = 'v4_cg2_state.pkl'
if os.path.exists(ST):
    st = pickle.load(open(ST, 'rb')); rowsT, hist = st['rows'], st['hist']; log('resumed: rows', len(rowsT), 'iters', len(hist))
else:
    tr = [int(tarm[i, i]) for i in range(n)]
    im = [sum(1 << v for v in ins) for ins in inside]
    bestI = {}
    for i in range(n):
        if im[i] and (im[i] not in bestI or tr[i] < tr[bestI[im[i]]]): bestI[im[i]] = i
    keptm, rowsT = [], set()
    for i in sorted(bestI.values(), key=lambda i: (tr[i], -len(inside[i]))):
        if any((im[i] & k) == im[i] for k in keptm): continue
        keptm.append(im[i]); rowsT.add((i, i))
    single = [i for i, ins in enumerate(inside) if len(ins) == 1 and dimA[i] == 2]
    for a in single:
        for b in single: rowsT.add((a, b))
    rowsT = sorted(rowsT); hist = []
    log('initial rows', len(rowsT))
obj = np.array([2.0 * len(Q) for Q in cl])
NNZ_CAP = 14_000_000
def solve(rowsT):
    cols = [np.nonzero(T[a] & T[r])[0].astype(np.int32) for a, r in rowsT]
    indptr = np.zeros(len(cols) + 1, dtype=np.int64); indptr[1:] = np.cumsum([len(c) for c in cols])
    A = sp.csr_matrix((np.ones(indptr[-1]), np.concatenate(cols), indptr), shape=(len(cols), K)); del cols
    rhs = np.array([float(tarm[a, r]) for a, r in rowsT])
    guard('before LP')
    res = so.linprog(-obj, A_ub=A, b_ub=rhs, bounds=(0, None), method='highs')
    assert res.status == 0, res.message
    return res, A.nnz

for it in range(len(hist), 400):
    if time.time() - T_START > TIME_LIMIT:
        log('time limit reached, state saved; certifying current lam'); break
    t0 = time.time()
    res, nnz = solve(rowsT)
    lam = res.x; val = -res.fun; slack = res.ineqlin.residual
    tlp = time.time() - t0
    act = np.nonzero(lam > 1e-12)[0]
    TW = (T[:, act].astype(np.float32) * lam[act].astype(np.float32)).T.copy(); Ta = T[:, act].astype(np.float32)
    cand = []; nviol = 0; worst = 0.0
    for a0 in range(0, n, B):
        V = Ta[a0:a0+B] @ TW
        ex = V - tarm[a0:a0+B].astype(np.float32)
        ia, ir = np.nonzero(ex > 1e-6); nviol += len(ia)
        if len(ia):
            worst = max(worst, float(ex[ia, ir].max()))
            e = ex[ia, ir]
            # keep up to 2 best per source row
            order = np.lexsort((-e, ia)); last = -1; cnt = 0
            for k in order:
                if ia[k] != last: last, cnt = ia[k], 0
                if cnt < 2: cand.append((float(e[k]), a0 + int(ia[k]), int(ir[k]))); cnt += 1
        if (a0 // B) % 100 == 0: guard('separation')
    cand.sort(reverse=True); add_ = [(a, r) for _, a, r in cand[:1500]]
    # prune slack rows if the LP got large (cutting-plane rows are recoverable by separation)
    pruned = 0
    if nnz > NNZ_CAP:
        keep = [t for t, s in zip(rowsT, slack) if s <= 1e-7]; pruned = len(rowsT) - len(keep); rowsT = keep
    rowsT = sorted(set(rowsT) | set(add_))
    hist.append({'iter': it, 'LB_LP': val, 'violations': nviol, 'worst_excess': worst, 'added': len(add_), 'pruned': pruned,
                 'rows_next': len(rowsT), 'nnz': int(nnz), 'active_cliques': int(len(act)), 'lp_sec': round(tlp, 1),
                 'sec': round(time.time() - t0, 1), 'ram': round(ram(), 1)})
    log(hist[-1])
    pickle.dump({'rows': rowsT, 'hist': hist}, open(ST + '.tmp', 'wb')); os.replace(ST + '.tmp', ST)
    json.dump(hist, open('v4_cg2.progress.json', 'w'), indent=0)
    np.save('v4_cg2_lam_last.npy', lam)
    if not add_: break

# strict certificate in float64 over all pairs
log('certifying lam over all', n, 'x', n, 'pairs (float64)')
lam = np.where(lam > 1e-12, lam, 0.0)
for rnd in range(5):
    act = np.nonzero(lam > 0)[0]
    TW = (T[:, act].astype(np.float64) * lam[act]).T.copy(); Ta = T[:, act].astype(np.float64)
    smin = 1.0; bad = set()
    for a0 in range(0, n, B):
        V = Ta[a0:a0+B] @ TW; tar = tarm[a0:a0+B].astype(np.float64)
        z0 = (tar == 0) & (V > 0)
        if z0.any():
            for ia, ir in zip(*np.nonzero(z0)):
                bad |= set(act[np.nonzero(T[a0 + ia, act] & T[ir, act])[0]].tolist())
        pos = V > 0
        if pos.any(): smin = min(smin, float((tar[pos & ~z0] / V[pos & ~z0]).min()) if (pos & ~z0).any() else 1.0)
    if not bad: break
    assert rnd < 4, 'tariff-0 cleanup did not converge'
    log('zeroing cliques touched by tariff-0 pairs:', len(bad)); lam[list(bad)] = 0.0
s = smin * (1 - 1e-9)
LB = float(s * (lam @ obj))
out = {'LB_strict': LB, 'LB_LP_last': float(val), 'scale': s, 'iterations': len(hist), 'converged': not add_,
       'lam': {','.join(map(str, sorted(cl[q]))): float(lam[q] * s) for q in np.nonzero(lam > 0)[0]}}
json.dump(out, open('v4_cg2_result.json', 'w'), indent=1)
log('DONE strict LB %.4f (LP %.4f, scale %.9f), converged=%s' % (LB, val, s, not add_))
log('budget to tie incumbent 160-164; best known construction 224')
