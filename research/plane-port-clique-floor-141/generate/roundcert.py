"""Round the best LP solution to an exact integer certificate (certificate generator)."""
import json, sys
from fractions import Fraction
import numpy as np
from geom import load, CACHE

SCALE = 2 ** 20
inside, T, orth = load()
n = len(T)
w = np.load(CACHE / 'best_w.npy'); cols = json.loads((CACHE / 'best_cols.json').read_text())
shrink = Fraction(1) - Fraction(1, 10 ** 6)
while True:
    W = [int(Fraction(float(x)) * SCALE * shrink) for x in w]           # floor
    keep = [(c, k) for c, k in zip(cols, W) if k > 0]
    q = np.zeros((len(keep), 56), np.int32)
    for i, (c, k) in enumerate(keep):
        q[i, c] = 1
    wk = np.array([k for _, k in keep], dtype=np.float64)
    touch = ((inside.astype(np.int32) @ q.T) > 0).astype(np.float64)
    TW = (touch * wk).T.copy()
    worst = None
    for b0 in range(0, n, 2048):
        L = np.rint(touch[b0:b0 + 2048] @ TW).astype(np.int64)
        m = int((T[b0:b0 + 2048].astype(np.int64) * SCALE - L).min())
        worst = m if worst is None else min(worst, m)
    LB = Fraction(sum(k * 2 * len(c) for c, k in keep), SCALE)
    print('shrink', float(shrink), 'columns', len(keep), 'min slack', worst, 'bound', float(LB), flush=True)
    if worst >= 0:
        break
    shrink *= Fraction(999, 1000)
out = {'schema': 'plane-port-clique-floor-141/certificate/1', 'scale': SCALE,
       'lower_bound_num': LB.numerator, 'lower_bound_den': LB.denominator,
       'columns': [{'clique': sorted(int(i) for i in c), 'w': k} for c, k in sorted(keep, key=lambda t: (len(t[0]), sorted(t[0])))]}
s = '{' + ', '.join('"%s": %s' % (k, json.dumps(v)) for k, v in out.items() if k != 'columns')
s += ', "columns": [\n' + ',\n'.join(json.dumps(c, separators=(',', ':')) for c in out['columns']) + '\n]}\n'
(CACHE / 'CERTIFICATE.json').write_text(s)
print('bound', LB, float(LB))
