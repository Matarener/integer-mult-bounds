"""Gaussian E8 (60 lines, w = 4): every decoder on the pattern has sum_j beta_j >= 40 (x_K >= 2/3).

Argument.  C ranges over the 640 twelve-line sets of pairwise K-non-orthogonal lines.  On C x C the pattern forces
B[C,C] = I_12 (diagonal 1, all off-diagonal pairs non-orthogonal), and each total contributes a rank-1 F2 matrix there,
so at least 12 totals hit C on both sides (R_j & C != {} and A_j & C != {}).  Summing: sum_j hit(R_j, A_j) >= 12*640.
For fixed spans X = span R_j, Y = span A_j the hit count is largest for R = lines(X), A = lines(Y) (flats), and this
script shows hit(X, Y) <= 192 * rank(X, Y) for all 2271^2 flat pairs, rank = K-rank of the pairing (Theorem C cost).
Hence sum_j beta_j >= 12*640/192 = 40.  Binding pair: X = 6-line 2-flat containing l, Y = the 15-line hyperplane l^perp
(pairing rank 1, 192 hits).  Mixing all clique sizes, singletons, non-orthogonal pairs and the whole set in an LP over
uniform orbit weights does not improve 40 (gauss_lp3.py in the work dir).
Ranks: exact integer pairing matrices, rank mod p = 2^31-1 (a certified lower bound on the rank over Q)."""
import sys, itertools; sys.path.insert(0, sys.path[0])
from lines import *
from flats import flats
import networkx as nx

def main():
    W = views(); S = W['Gauss']; J = W['_J']; v = S.v
    F = flats(S); fl = sorted(F.items(), key=lambda t: (t[1], len(t[0]), sorted(t[0])))
    n = len(fl); assert n == 2271
    g = nx.Graph([(i, j) for i in range(v) for j in range(i+1, v) if S.NO[i, j]])
    C = [c for c in nx.find_cliques(g) if len(c) == 12]
    assert len(C) == 640 and all(S.NO[a, b] for c in C for a, b in itertools.combinations(c, 2))
    Lo = np.zeros((n, v), np.int64)
    for i, (f, d) in enumerate(fl): Lo[i, sorted(f)] = 1
    inc = np.zeros((v, len(C)), np.int64)
    for k, c in enumerate(C): inc[c, k] = 1
    meet = (Lo @ inc > 0).astype(np.int64); hits = meet @ meet.T          # exact integers
    # exact integer bases (vectors r_T, J r_T), pairing ranks by batched elimination mod p = 2^31-1
    # (rank mod p <= rank over Q, so these are certified LOWER bounds; the claim only needs lower bounds)
    def ibasis(f):
        rows = []
        for T in sorted(f):
            for x in (S.reps[T], J @ S.reps[T]):
                if rank_q(rows + [x]) > len(rows): rows.append(x)
        return np.array(rows, np.int64)
    Bs = [ibasis(f) for f, d in fl]
    assert all(len(b) == 2 * d for b, (f, d) in zip(Bs, fl))
    P = 2147483647
    def modrank(A):
        A = A % P; N, r, c = A.shape; used = np.zeros((N, r), bool); idx = np.arange(N)
        for col in range(c):
            cand = (A[:, :, col] != 0) & ~used; has = cand.any(1)
            if not has.any(): continue
            pr = cand.argmax(1); it = idx[has]; prow = A[it, pr[has]]
            inv = np.array([pow(int(x), P - 2, P) for x in prow[:, col]], np.int64) if len(it) < 64 else modinv(prow[:, col])
            prow = (prow * inv[:, None]) % P
            fac = A[it, :, col].copy(); fac[np.arange(len(it)), pr[has]] = 0
            A[it] = (A[it] - (fac[:, :, None] * prow[:, None, :]) % P) % P
            used[it, pr[has]] = True
        return used.sum(1)
    def modinv(x):
        res = np.ones_like(x); base = x % P; e = P - 2
        while e:
            if e & 1: res = (res * base) % P
            base = (base * base) % P; e >>= 1
        return res
    R = np.zeros((n, n), np.int64)
    groups = {}
    for i, b in enumerate(Bs): groups.setdefault(len(b), []).append(i)
    for da, ia in groups.items():
        A = np.stack([Bs[i] for i in ia])
        for db, ib in groups.items():
            Bm = np.stack([Bs[i] for i in ib])
            M = np.einsum('aik,bjk->abij', A, Bm).reshape(-1, da, db)
            r = modrank(M).reshape(len(ia), len(ib)); assert (r % 2 == 0).all()
            R[np.ix_(ia, ib)] = r // 2
    import pickle; pickle.dump({'fl':fl,'R':R,'hits':hits,'C':C},open('hits_table.pkl','wb'))
    print(f'PASS gauss.ranks: certified (mod p) pairing-rank lower bounds for all {n}x{n} flat pairs, histogram {np.bincount(R.flatten()).tolist()}')
    assert (hits <= 192 * R).all()
    worst = np.argwhere((hits == 192 * R) & (R > 0))
    print('PASS gauss.hits: hit(X,Y) <= 192 * rank(X,Y) on every flat pair (exact hits, certified ranks)')
    a, b = worst[0]
    print(f'      binding example: |X| = {len(fl[a][0])} (dim {fl[a][1]}), |Y| = {len(fl[b][0])} (dim {fl[b][1]}), rank {R[a,b]}, hits {hits[a,b]}; {len(worst)} binding pairs')
    print('RESULT gauss: every decoder has sum_j beta_j >= 12*640/192 = 40  =>  x_K >= 2/3 (threshold to exclude: 43)')

if __name__ == '__main__':
    main()
