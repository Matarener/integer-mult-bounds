# Numerical check of the rank argument "every plane-port decoder costs >= 224".
# For a term (u, v): C(u,v) = X_u^T Y_v, X_u = [labels of plane(p) for p in supp u] (2 columns per port, zeros elsewhere),
# Y_v likewise.  Claim 1: rank C(u,v) <= tariff(u,v).  Claim 2: sum_k C(u_k,v_k) = blockdiag(plane Grams) for any exact decoder.
import json, random, numpy as np
from v4lib import *
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes); NPORT = 112
E = [0] * NPORT
for i, (a, b) in enumerate(pairs): E[a] = i; E[b] = i
vec = lambda x: np.array([(x >> t) & 1 for t in range(9)], dtype=np.uint8)
PL = [np.stack([vec(planes[E[p]][0]), vec(planes[E[p]][1])], axis=1) for p in range(NPORT)]   # 9x2 per port
def X(w):
    out = np.zeros((9, 2 * NPORT), dtype=np.uint8)
    for p in range(NPORT):
        if w >> p & 1: out[:, 2*p:2*p+2] = PL[p]
    return out
def rank2(A):
    A = A.copy() % 2; r = 0; rows, cols = A.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i, c]), None)
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]
        for i in range(rows):
            if i != r and A[i, c]: A[i] ^= A[r]
        r += 1
    return r
def pmask(w): return sorted({E[p] for p in range(NPORT) if w >> p & 1})
def tariff(U, V): return pair_rank(span([x for i in pmask(U) for x in planes[i]]), span([x for i in pmask(V) for x in planes[i]]))
random.seed(1); worst = 0
for _ in range(400):   # claim 1 on random terms
    U = random.getrandbits(NPORT) & random.getrandbits(NPORT) & random.getrandbits(NPORT); V = random.getrandbits(NPORT) & random.getrandbits(NPORT)
    if not U or not V: continue
    r = rank2((X(U).T.astype(int) @ X(V).astype(int)) % 2); t = tariff(U, V)
    assert r <= t, (r, t); worst = max(worst, r - t)
print('claim 1 holds on 400 random terms (max rank - tariff =', worst, ')')
for f in ['v4_repaired_decoder.json', 'kaggle-wide/v4_realize_best.json']:
    d = json.load(open(f)); T = [(int(a, 16), int(b, 16)) for a, b in d['terms']]
    if f.endswith('best.json'): continue
    S = np.zeros((2 * NPORT, 2 * NPORT), dtype=int); tot_r = 0; tot_t = 0
    for U, V in T:
        C = (X(U).T.astype(int) @ X(V).astype(int)) % 2; S = (S + C) % 2; tot_r += rank2(C); tot_t += tariff(U, V)
    BD = np.zeros_like(S)
    for p in range(NPORT): BD[2*p:2*p+2, 2*p:2*p+2] = (PL[p].T.astype(int) @ PL[p].astype(int)) % 2
    print(f, ': sum C == blockdiag(plane Grams):', bool((S == BD).all()), '| rank of sum', rank2(S), '| sum of ranks', tot_r, '| total tariff', tot_t)
