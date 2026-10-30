# Root-normal case: y a root (E7 hyperplane).  For each of the 120 lines y and every plane pair, classify by
# position of A_i relative to H_y = {b(u, ybar) = 1} and report min |N(y) \ (L1 u L2)| per case.  Apache-2.0.
import sys, pickle, collections, itertools, numpy as np, time
import _paths
from lbz import *
from labels import cls, full
full = (1 << v) - 1
print('START rootcase', flush=True)
D = pickle.load(open('pairs_exact.pkl', 'rb')); P = D['planes']
Lm = [full ^ (cls[a] | cls[b] | cls[c]) for a, b, c in P]
# class model: find (x, eps) for each class: O_c = {t : (PV[t].x/4 + eps) odd}
vecs = set()
for a in E8L:
    vecs.add(a)
    for b in E8L: vecs.add(tuple(p + q for p, q in zip(a, b)))
def par(t, x): return (idot(PV[t], x) // 4) % 2
model = {}
for c in range(1, 512):
    for x in vecs:
        m0 = sum(1 << t for t in range(v) if par(t, x) == 1)
        if m0 == cls[c]: model[c] = (x, 0); break
        if full ^ m0 == cls[c]: model[c] = (x, 1); break
assert len(model) == 511
def mod2(x): return tuple(((a // 2) % 2) for a in x)   # doubled coords: E8/2E8 test via dot parity instead
M64 = (1 << 64) - 1
LLO = np.array([x & M64 for x in Lm], dtype=np.uint64); LHI = np.array([x >> 64 for x in Lm], dtype=np.uint64)
pcnt = lambda a: np.bitwise_count(a).astype(np.int64)
stat = collections.defaultdict(lambda: [10 ** 9, 0])
T = time.time()
for yi, y in enumerate(E8L):
    N = sum(1 << t for t in range(v) if idot(PV[t], y) != 0); nN = bin(N).count('1')
    Hy = sum(1 << t for t in range(v) if (idot(PV[t], y) // 4) % 2 == 1)   # ports with r.y odd
    yport = any(PV[t] == y or PV[t] == tuple(-a for a in y) for t in range(v))
    nlo, nhi = np.uint64(N & M64), np.uint64(N >> 64)
    cov = pcnt(LLO & nlo) + pcnt(LHI & nhi)
    cand = np.nonzero(cov >= nN - 12 - 36)[0]
    # position of each candidate plane: inside H_y (L subset Hy-ports and A inside H_y) etc. use ports: L subset Hy?
    for ii, i in enumerate(cand):
        js = cand[ii + 1:]
        if len(js) == 0: continue
        left = pcnt(nlo & ~LLO[i] & ~LLO[js]) + pcnt(nhi & ~LHI[i] & ~LHI[js])
        for k in np.nonzero(left <= 12)[0]:
            j = js[k]
            ov = bin(Lm[i] & Lm[j]).count('1')
            pos = tuple(sorted(int((Lm[x] & ~Hy) == 0) for x in (i, j)))
            key = (yport, pos, ov > 0)
            st = stat[key]; st[0] = min(st[0], int(left[k])); st[1] += 1
    if yi % 10 == 0: print('y', yi, 'port' if yport else 'nonport', '|N|', nN, 'cand', len(cand), round(time.time() - T), 's', flush=True)
for k, s in sorted(stat.items()):
    print('y port' if k[0] else 'y nonport', 'L-inside-H_y flags', k[1], 'overlap' if k[2] else 'disjoint', 'pairs with |N minus union| <= 12:', s[1], 'min uncovered', s[0])
