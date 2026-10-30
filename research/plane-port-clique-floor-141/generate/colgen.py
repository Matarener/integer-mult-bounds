"""Row-and-column generation for the clique programme of PR5560 (certificate generator; needs scipy for HiGHS).

max sum_c 2|Q_c| w_c  s.t.  sum_{c touched by (a,r)} w_c <= T[a,r]  for all ordered span pairs.
"""
import json, sys, time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog
from geom import load, ROOT, CACHE

T0 = time.time()
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
ITERS = int(sys.argv[2]) if len(sys.argv) > 2 else 40
STOP = 140.0                     # stop at the first point certified above this value


def log(*a):
    print('%6.0fs' % (time.time() - T0), *a, flush=True)


inside, T, orth = load()
n = len(T)
Tf = T.astype(np.float32)
INS = inside.astype(np.float32)
log('spans', n)

cert = json.loads((ROOT / 'research/plane-port-global-rank-dual/CERTIFICATE.json').read_text())
cols = {tuple(sorted(c['clique'])) for c in cert['columns']}
cols |= {(i,) for i in range(56)}
cols = sorted(cols)


def qmat(cs):
    q = np.zeros((len(cs), 56), np.float32)
    for k, c in enumerate(cs):
        q[k, list(c)] = 1
    return q


def separate(cs, w, top=4000):
    """max ratio load/T over all rows, and the most violated pairs"""
    keep = w > 1e-12
    q = qmat([c for c, k in zip(cs, keep) if k]); wk = w[keep].astype(np.float32)
    touch = ((INS @ q.T) > 0).astype(np.float32)
    TW = (touch * wk).T.copy()
    worst = 0.0; cand = []
    B = 4096
    for b0 in range(0, n, B):
        L = touch[b0:b0 + B] @ TW
        t = Tf[b0:b0 + B]
        ratio = np.where(t > 0, L / np.maximum(t, 1), np.where(L > 1e-6, np.inf, 0))
        worst = max(worst, float(ratio.max()))
        viol = L - t
        idx = np.argpartition(viol.ravel(), -top)[-top:]
        v = viol.ravel()[idx]
        sel = idx[v > 1e-7]
        for f, vv in zip(sel, viol.ravel()[sel]):
            cand.append((float(vv), b0 + f // n, f % n))
    cand.sort(reverse=True)
    return worst, [(a, r) for _, a, r in cand[:top]]


def price(rows, y, ntry=400, keepn=200):
    """local search for cliques with positive reduced profit 2|Q| - sum y [touch]"""
    act = y > 1e-9
    if not act.any():
        return []
    ra = np.array([a for (a, r), k in zip(rows, act) if k]); rr = np.array([r for (a, r), k in zip(rows, act) if k])
    yy = y[act]
    A = inside[ra]; R = inside[rr]                       # K x 56 bool
    compat = ~orth
    found = {}
    for _ in range(ntry):
        q = np.zeros(56, bool)
        order = rng.permutation(56)
        q[order[0]] = True
        while True:
            ta = (A & q).any(1); tr = (R & q).any(1)
            base = 2 * q.sum() - yy @ (ta & tr)
            # add moves
            ok = compat[q].all(0) & ~q
            nta = ta[:, None] | A; ntr = tr[:, None] | R
            gain_add = 2 * q.sum() + 2 - yy @ (nta & ntr)
            gain_add = np.where(ok, gain_add, -np.inf)
            # remove moves (recompute)
            best_rm = -np.inf; brm = -1
            for i in np.flatnonzero(q):
                q2 = q.copy(); q2[i] = False
                if not q2.any():
                    continue
                g = 2 * q2.sum() - yy @ ((A & q2).any(1) & (R & q2).any(1))
                if g > best_rm:
                    best_rm, brm = g, i
            i = int(np.argmax(gain_add + rng.random(56) * 1e-9))
            if gain_add[i] > base + 1e-9 and gain_add[i] >= best_rm:
                q[i] = True
            elif best_rm > base + 1e-9:
                q[brm] = False
            else:
                break
        if base > 1e-7:
            found[tuple(np.flatnonzero(q))] = base
    return sorted(found, key=found.get, reverse=True)[:keepn]


def master(cs, rows):
    q = qmat(cs).astype(bool)
    ra = np.array([a for a, r in rows]); rr = np.array([r for a, r in rows])
    M = ((inside[ra].astype(np.int32) @ q.T.astype(np.int32)) > 0) & ((inside[rr].astype(np.int32) @ q.T.astype(np.int32)) > 0)
    c = -2 * q.sum(1).astype(float)
    res = linprog(c, A_ub=sp.csr_matrix(M.astype(float)), b_ub=T[ra, rr].astype(float), bounds=(0, None), method='highs')
    assert res.status == 0, res.message
    return res.x, -res.ineqlin.marginals, -res.fun


# initial rows: separation of the certificate weights scaled to be loose
w0 = np.zeros(len(cols))
cmap = {c: k for k, c in enumerate(cols)}
for c in cert['columns']:
    w0[cmap[tuple(sorted(c['clique']))]] = c['w'] / cert['scale']
rows = set()
_, rws = separate(cols, w0 * 1.3, top=20000)
rows |= set(rws)
rows = sorted(rows)
best = 0
for it in range(ITERS):
    w, y, val = master(cols, rows)
    worst, rws = separate(cols, w)
    cert_val = val / max(worst, 1.0)
    if cert_val > best:
        best = cert_val
        np.save(CACHE / 'best_w.npy', w); (CACHE / 'best_cols.json').write_text(json.dumps([list(map(int, c)) for c in cols]))
    newrows = [r for r in rws if r not in set(rows)]
    newcols = [c for c in price(rows, y) if c not in cmap]
    log('it', it, 'rows', len(rows), 'cols', len(cols), 'LP', round(val, 4), 'maxratio', round(worst, 5),
        'certified~', round(cert_val, 4), 'best', round(best, 4), '+rows', len(newrows), '+cols', len(newcols))
    if best > STOP or (not newrows and not newcols):
        break
    rows = sorted(set(rows) | set(newrows))
    for c in newcols:
        cmap[c] = len(cols); cols.append(c)
log('done best', best)
