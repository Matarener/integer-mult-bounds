# Lemma P (PROOF.md 4, Step 3), first half: exact compatibility of big terms with d = 2 (planes Z of the label space).
# R_j is inside L(Z_j) = ports whose label lies in Z_j^perp.  A set J of bigs needs: the ports outside the union of
# the L(Z_j) lie, up to <= 4 pairwise non-orthogonal ports, in a flat of rank <= 9 - |J| (exact Gram rank in the
# B-form, PR6188 Case II step 3).  We compute all compatible plane pairs and the largest compatible families (cliq.py).  Apache-2.0.
import sys, time, itertools, numpy as np
import _paths
T0 = time.time()
print('START planes', flush=True)
from lbz import *
from labels import cls, full          # loads P104, flats (BIG), lbz, NO
print('flats loaded', len(BIG), round(time.time() - T0), 's', flush=True)
full = (1 << v) - 1
planes = []
for a in range(1, 512):
    for b in range(a + 1, 512):
        if (a ^ b) > b: planes.append((a, b, a ^ b))
Lm = [full ^ (cls[a] | cls[b] | cls[c]) for a, b, c in planes]
print('planes', len(planes), 'max |L|', max(bin(x).count('1') for x in Lm), flush=True)
M64 = (1 << 64) - 1
LLO = np.array([x & M64 for x in Lm], dtype=np.uint64); LHI = np.array([x >> 64 for x in Lm], dtype=np.uint64)
pcnt = lambda a: np.bitwise_count(a).astype(np.int64)
pairs = set(); last = time.time()
H7 = [(m, r) for m, r in BIG if r <= 7]
for hi, (m, r) in enumerate(H7):
    N = full ^ m; nN = bin(N).count('1')
    if nN > 76: continue
    nlo, nhi = np.uint64(N & M64), np.uint64(N >> 64)
    cov = pcnt(LLO & nlo) + pcnt(LHI & nhi)
    cand = np.nonzero(cov >= nN - 4 - 36)[0]
    for ii, i in enumerate(cand):
        js = cand[ii + 1:]
        if len(js) == 0: continue
        rest_lo = nlo & ~LLO[i]; rest_hi = nhi & ~LHI[i]
        left = pcnt(rest_lo & ~LLO[js]) + pcnt(rest_hi & ~LHI[js])
        for j in js[left <= 4]:
            S = N & ~Lm[i] & ~Lm[j]
            if all(NO[a] >> b & 1 for a, b in itertools.combinations(bits(S), 2)): pairs.add((int(i), int(j)))
    if time.time() - last > 30:
        print('HEARTBEAT flat', hi, '/', len(H7), 'pairs', len(pairs), round(time.time() - T0), 's', flush=True); last = time.time()
print('compatible plane pairs', len(pairs), round(time.time() - T0), 's', flush=True)
import pickle
pickle.dump({'planes': planes, 'pairs': sorted(pairs)}, open('pairs_exact.pkl', 'wb'))
