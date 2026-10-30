# Lemma P, side facts: |L(Z)| histogram and (|L|, |L'|, overlap, union) of every compatible pair (needs pairs_exact.pkl). Apache-2.0.
import pickle, collections, sys, numpy as np, time
import _paths
from labels import *
D = pickle.load(open('pairs_exact.pkl', 'rb')); P = D['planes']; E = D['pairs']
Lm = [full ^ (cls[a] | cls[b] | cls[c]) for a, b, c in P]; sz = [bin(x).count('1') for x in Lm]
print('plane |L| hist', sorted(collections.Counter(sz).items()), flush=True)
print('compatible pair (|L1|,|L2|,|L1&L2|,|union|)', sorted(collections.Counter(tuple(sorted((sz[i], sz[j]))) + (bin(Lm[i] & Lm[j]).count('1'), bin(Lm[i] | Lm[j]).count('1')) for i, j in E).items()), flush=True)
