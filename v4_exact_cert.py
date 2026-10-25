# Exact certificate for the clique-dual lower bound (valid over ANY field, so also for scalar decoders with even
# denominators).  Weights lam_Q are rounded DOWN to integers w_Q / 2^20.  Feasibility  sum_{Q touched} w_Q <= 2^20 * tariff
# is checked for all 39087^2 ordered span pairs.  All quantities are integers < 2^53, so float64 BLAS products are exact.
import json, os, pickle, time
from fractions import Fraction
import numpy as np
from v4lib import *
T0 = time.time(); SCALE = 1 << 20
def log(*a): print(time.strftime('%H:%M:%S'), '%5.0fs' % (time.time() - T0), *a, flush=True)
d = pickle.load(open('v4_spans.pkl', 'rb')); spans, inside = d['spans'], d['inside']; n = len(spans)
z = np.load('v4_masks.npz'); M, P, dimA = z['M'], z['P'], z['dimA'].astype(np.int16)
tarm = np.zeros((n, n), dtype=np.uint8); B = 100
for a0 in range(0, n, B):
    inter = np.bitwise_count(M[a0:a0+B, None, :] & P[None, :, :]).sum(axis=2)
    tarm[a0:a0+B] = (dimA[a0:a0+B, None] - np.round(np.log2(inter)).astype(np.int16)).astype(np.uint8)
    if (a0 // B) % 100 == 0: log('tariff rows', a0 + B, '/', n)
for a, r in [(0, 0), (5, 77), (n - 1, n - 2), (1234, 30000), (39000, 17)]: assert int(tarm[a, r]) == pair_rank(spans[a], spans[r])
res = json.load(open('v4_cert_float.json'))
cols = [(sorted(c['X']), c['value'], c['lam']) for c in res['columns'] if c['lam'] > 0]
assert all(c[1] == 2 * len(c[0]) for c in cols), 'only clique columns expected'
w = np.array([int(np.floor(lam * SCALE)) for _, _, lam in cols], dtype=np.int64)
keep = w > 0; cols = [c for c, k in zip(cols, keep) if k]; w = w[keep]
log('columns', len(cols), 'weight sum', int(w.sum()))
imask = np.array([sum(1 << v for v in ins) for ins in inside], dtype=np.uint64)
qm = np.array([sum(1 << v for v in X) for X, _, _ in cols], dtype=np.uint64)
Tm = ((imask[:, None] & qm[None, :]) != 0).astype(np.float64)
TW = (Tm * w.astype(np.float64)).T.copy()
worst = -10**18; viol = 0
for a0 in range(0, n, B):
    V = Tm[a0:a0+B] @ TW                                    # exact integers
    lim = tarm[a0:a0+B].astype(np.float64) * SCALE
    ex = V - lim; worst = max(worst, float(ex.max())); viol += int((ex > 0).sum())
    if (a0 // B) % 100 == 0: log('rows checked', a0 + B, '/', n, 'violations so far', viol)
LB = Fraction(int(sum(int(wi) * 2 * len(X) for wi, (X, _, _) in zip(w, cols))), SCALE)
ok = viol == 0
log('EXACT CHECK', 'PASSED' if ok else 'FAILED', '| violations', viol, '| max(sum - 2^20*tariff) =', worst)
log('certified lower bound (exact) =', LB, '=', float(LB))
json.dump({'scale': SCALE, 'passed': ok, 'lower_bound_num': LB.numerator, 'lower_bound_den': LB.denominator,
           'lower_bound_float': float(LB), 'columns': [{'clique': X, 'w': int(wi)} for wi, (X, _, _) in zip(w, cols)]},
          open('v4_exact_certificate.json', 'w'), indent=0)
