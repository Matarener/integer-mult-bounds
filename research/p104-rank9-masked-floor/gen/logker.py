"""Exact kernel of the monomial relation system N{t,a}N{s,a} = N{t,b}N{s,b} on Z (all relations, random projection
R*A keeps the rank w.h.p.; the kernel is then verified against every relation exactly).  Then: is every kernel vector
constant on every frame-sum quadruple?  (If yes, frame sums force N = 1/4 on the quadruples' pairs.)
usage: logker.py rep"""
import json, sys, time, numpy as np
from p104lib import *
T0 = time.time()
def log(*a): print('[%7.1fs]' % (time.time() - T0), *a, flush=True)
pr = 2**31 - 1
src = open('logsys.py').read()
exec(src[src.index('FR = '):src.index('for k in map')])
k = int(sys.argv[1])
m = int(reps[k]['mask']); Z = [i for i in range(N) if m >> i & 1]; Zs = set(Z)
import os
if os.environ.get('FRAMED') == '1':   # restrict Z to the lines lying in some frame inside Z
    _FZ0 = [f for f in FR if all(i in Zs for i in f)]
    _cov = set(i for f in _FZ0 for i in f); Z = [i for i in Z if i in _cov]; Zs = set(Z)
if os.environ.get('DROP'):   # remove the given lines from Z (e.g. the single line outside the span fixpoint)
    _dr = set(map(int, os.environ['DROP'].split(','))); Z = [i for i in Z if i not in _dr]; Zs = set(Z)
FZ = [f for f in FR if all(i in Zs for i in f)]
pairs = [(a, b) for a in Z for b in Z if a < b and not ORTH[a][b]]; pos = {p: j for j, p in enumerate(pairs)}
rel = set(); quads = set()
for F in FZ:
    Fs = set(F)
    for t in Z:
        if t in Fs: continue
        Tt = [f for f in F if not ORTH[t][f]]; quads.add(tuple(sorted(pos[P(t, f)] for f in Tt)))
        for s in Z:
            if s <= t or s in Fs or not ORTH[t][s]: continue
            com = [f for f in Tt if not ORTH[s][f]]
            if len(com) == 2:
                a, b = com; rel.add((pos[P(t, a)], pos[P(s, a)], pos[P(t, b)], pos[P(s, b)]))
n = len(pairs); A = np.zeros((len(rel), n), dtype=np.int64)
for i, (ta, sa, tb, sb) in enumerate(rel): A[i, ta] += 1; A[i, sa] += 1; A[i, tb] -= 1; A[i, sb] -= 1
rng = np.random.default_rng(0)
R = rng.integers(-1, 2, size=(n + 40, len(rel)), dtype=np.int64)
B = np.rint(R.astype(np.float64) @ A.astype(np.float64)).astype(np.int64) % pr
# reduced row echelon mod p -> kernel basis
M = B.copy(); r = 0; piv = []
for c in range(n):
    nzr = np.nonzero(M[r:, c])[0]
    if len(nzr) == 0: continue
    p_ = r + nzr[0]; M[[r, p_]] = M[[p_, r]]; inv = pow(int(M[r, c]), pr - 2, pr); M[r] = (M[r] * inv) % pr
    nz = np.nonzero(M[:, c])[0]; nz = nz[nz != r]
    if len(nz): M[nz] = (M[nz] - (M[nz, c][:, None] * M[r][None, :]) % pr) % pr
    piv.append(c); r += 1
    if r == M.shape[0]: break
free = [c for c in range(n) if c not in set(piv)]
ker = []
for fcol in free:
    v = np.zeros(n, dtype=np.int64); v[fcol] = 1
    for i, c in enumerate(piv): v[c] = (-M[i, fcol]) % pr
    ker.append(v)
ok = all(((A @ v) % pr == 0).all() for v in ker)
log('rep', k, 'unknowns', n, 'relations', len(rel), 'kernel dim', len(ker), 'verified on all relations', ok)
bad = 0
for q in quads:
    for v in ker:
        vals = {int(v[j]) for j in q}
        if len(vals) > 1: bad += 1; break
log('quadruples', len(quads), 'on which some kernel vector is non-constant', bad)
json.dump({'pairs': pairs, 'ker': [[int(x) for x in v] for v in ker]}, open('logker-r%d.json' % k, 'w'))
log('DONE')
