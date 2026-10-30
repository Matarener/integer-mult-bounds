# Singular-D pair table: for every 2-dim orbit rep R (as in the repo's cnt104b.py) and every useful plane W, the bound
# lbz(C(R) & C(W)) (lbz.py) when it is <= 7.  Vectorised over W; only the listed flats can certify <= 7 (|X| >= 32).
# Writes cnt_P104z.pkl {'lb22': {(R, W): value}}.  Logs every orbit (counts) and every pair found.  Apache-2.0.
import sys, os, time, pickle, itertools, numpy as np
from collections import Counter
from lbz import *
T0 = time.time()
print('START cnt104z flats', len(BIG), flush=True)
full = (1 << v) - 1; ks = sorted(cls)
sub2 = sorted({tuple(sorted((a, b, a ^ b))) for a in ks for b in ks if a < b})
def C(W):
    x = 0
    for c in W: x |= cls[c]
    return x
D = pickle.load(open('orbits_P104.pkl', 'rb'))
inv = {cls[c]: c for c in cls}
def img(O, p):
    r = 0
    for t in range(v):
        if O >> t & 1: r |= 1 << p[t]
    return r
cperm = [{c: inv[img(cls[c], p)] for c in ks} for p in D['perms']]
seen = {}; orb2 = []
for W in sub2:
    if W in seen: continue
    seen[W] = len(orb2); orb = [W]; st = [W]
    while st:
        x = st.pop()
        for cp in cperm:
            y = tuple(sorted(cp[c] for c in x))
            if y not in seen: seen[y] = len(orb2); orb.append(y); st.append(y)
    orb2.append(orb)
import m9lib_surv
surv = m9lib_surv.surv
print('2-dim subspaces', len(sub2), 'orbits', len(orb2), 'survivors', len(surv), flush=True)
useful = [W for W in sub2 if any(c not in surv for c in W) and C(W) != full]
CW = [C(W) for W in useful]
WLO = np.array([x & M64 for x in CW], dtype=np.uint64); WHI = np.array([x >> 64 for x in CW], dtype=np.uint64)
F7 = [i for i, (m, r) in enumerate(BIG) if r <= 7 and bin(m).count('1') >= 28]
FLO = BLO[F7]; FHI = BHI[F7]; FRK = BRK[F7]; FCNT = np.array([bin(BIG[i][0]).count('1') for i in F7])
print('flats usable for <= 7 (rank <= 7, >= 28 ports)', len(F7), flush=True)
lb22 = {}; last = time.time()
for oi, o in enumerate(orb2):
    R = o[0]
    if all(c in surv for c in R) or C(R) == full: continue
    cr = C(R); xlo = WLO & np.uint64(cr & M64); xhi = WHI & np.uint64(cr >> 64)
    xs = popc(xlo) + popc(xhi)
    assert xs.min() >= 28
    found = {}
    BS = 256
    for i in range(0, len(F7), BS):
        flo = FLO[i:i + BS]; fhi = FHI[i:i + BS]
        out = popc(xlo[:, None] & ~flo[None, :]) + popc(xhi[:, None] & ~fhi[None, :])
        wi, fi = np.nonzero(out <= 4)
        for a, b in zip(wi, fi):
            X = CW[a] & cr; m = BIG[F7[i + b]][0]; r = int(FRK[i + b])
            S = X & ~m
            if all(NO[p] >> q & 1 for p, q in itertools.combinations(bits(S), 2)):
                if r < found.get(a, 9): found[a] = r
        if time.time() - last > 40: print('HEARTBEAT', round(time.time() - T0), 'orbit', oi, 'flat chunk', i, flush=True); last = time.time()
    for a, r in found.items():
        lb22[R, useful[a]] = r
        print('PAIR', oi, R, useful[a], 'lbz', r, '|X|', int(xs[a]), flush=True)
    print('orbit', oi, 'rep', R, '|C|', pc(cr), 'pairs with lbz <= 7:', len(found), 'hist', sorted(Counter(found.values()).items()), round(time.time() - T0), flush=True)
    pickle.dump({'lb22': lb22, 'orb2': orb2}, open('cnt_P104z.pkl', 'wb'))
print('DONE cnt104z pairs', len(lb22), round(time.time() - T0), flush=True)
