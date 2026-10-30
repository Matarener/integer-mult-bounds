# Largest |L(Z) u L(Z')| over all plane pairs (only planes with |L| >= 20 can reach 44): 66. PROOF.md 4, "why not by hand". Apache-2.0.
import sys, pickle, collections, numpy as np, time
import _paths
from labels import *
D = pickle.load(open('pairs_exact.pkl', 'rb')); P = D['planes']
Lm = [full ^ (cls[a] | cls[b] | cls[c]) for a, b, c in P]; sz = [bin(x).count('1') for x in Lm]
idx = [i for i in range(len(P)) if sz[i] >= 20]
M64 = (1 << 64) - 1
lo = np.array([Lm[i] & M64 for i in idx], dtype=np.uint64); hi = np.array([Lm[i] >> 64 for i in idx], dtype=np.uint64)
hist = collections.Counter(); T = time.time(); last = T
for a in range(len(idx)):
    u = np.bitwise_count(lo[a] | lo[a + 1:]).astype(np.int64) + np.bitwise_count(hi[a] | hi[a + 1:]).astype(np.int64)
    vals, cnts = np.unique(u[u >= 44], return_counts=True)
    for x, c in zip(vals, cnts): hist[int(x)] += int(c)
    if time.time() - last > 30: print('HEARTBEAT', a, len(idx), max(hist) if hist else 0, flush=True); last = time.time()
print('union size hist (>=44) over plane pairs with |L| >= 20:', sorted(hist.items()), round(time.time() - T), 's', flush=True)
