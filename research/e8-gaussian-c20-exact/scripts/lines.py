"""Self-contained exact construction of the E8 root lines over Q(i), Q(omega) and the Hurwitz quaternions.

Real model: the 240 E8 roots in doubled standard coordinates (norm 8; <r,s> in {0,+-4,+-8}).
 * Gaussian view : J = left multiplication by i on R^8 = H^2 (coords 1,i,j,k per block); J preserves E8.
   Hermitian Gram  hG(x,y) = (<x,y> + i <x,Jy>)/4  in Z[i]  (diag 2).
 * Eisenstein view: rho = fixed-point-free order-3 isometry of E8 (product of Coxeter elements of 4 orthogonal A2's).
   Sesquilinear Gram  hE(x,y) = (<x,y> - w <x,rho y>)/4  in Z[w]  (w^2+w+1=0; diag 2+w, a unit at 2).
 * Hurwitz view  : left multiplication by i, j, k; quaternionic lines of real dim 4.
Elements of Z[i] / Z[w] are stored as integer pairs (a, b) = a + b*i / a + b*w.
Everything is exact integer arithmetic; asserts check every structural claim used downstream.
"""
import itertools
from fractions import Fraction
import numpy as np


def e8_roots():
    R = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                r = [0] * 8; r[i], r[j] = si, sj; R.append(r)
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            R.append(list(s))
    R = np.array(R, dtype=np.int64)
    assert len(R) == 240 and set((R * R).sum(1)) == {8}
    return R


def rank_q(rows):
    """exact rank over Q of an integer matrix (fraction-free Gaussian elimination)."""
    M = [list(map(int, r)) for r in rows]
    if not M:
        return 0
    n, m = len(M), len(M[0]); r = 0
    for c in range(m):
        p = next((i for i in range(r, n) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        for i in range(r + 1, n):
            if M[i][c]:
                f, g = M[i][c], M[r][c]
                M[i] = [g * a - f * b for a, b in zip(M[i], M[r])]
        r += 1
        if r == n:
            break
    return r


def left_quat():
    Li = np.array([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]])
    Lj = np.array([[0, 0, -1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, -1, 0, 0]])
    Lk = Li @ Lj
    blk = lambda M: np.kron(np.eye(2, dtype=np.int64), M).astype(np.int64)
    return blk(Li), blk(Lj), blk(Lk)


def a2_rotation(roots):
    """rho, an order-3 fixed-point-free isometry preserving E8 (returned as an exact integer matrix 4*rho)."""
    chosen = []
    for a in roots:
        if len(chosen) == 4:
            break
        if any(np.dot(a, x) != 0 for p in chosen for x in p):
            continue
        for b in roots:
            if np.dot(a, b) == -4 and all(np.dot(a, x) == 0 and np.dot(b, x) == 0 for p in chosen for x in p):
                chosen.append((a, b)); break
    assert len(chosen) == 4
    g = np.eye(8, dtype=object)
    for a, b in chosen:
        sa = np.eye(8, dtype=object) * 8 - 2 * np.outer(a, a).astype(object)
        sb = np.eye(8, dtype=object) * 8 - 2 * np.outer(b, b).astype(object)
        g = g.dot(sa).dot(sb)
    D = 8 ** 8 // 4
    assert all(x % D == 0 for x in g.flatten())
    g = (g // D).astype(np.int64)
    I = np.eye(8, dtype=np.int64)
    assert (g @ g @ g == 64 * I).all() and (g @ g + 4 * g + 16 * I == 0).all()
    return g


def lines_over(roots, ops):
    """group roots into A-lines, A spanned by the integer matrices ops (identity first; ops may be scaled by 4).
    Returns representatives (first root met of each line, in root order)."""
    S = {tuple(r) for r in roots}
    reps, seen = [], set()
    for r in roots:
        if tuple(r) in seen:
            continue
        span = [B @ r for B in ops]
        assert rank_q(span) == len(ops)
        reps.append(r)
        members = [s for s in roots if rank_q(span + [s]) == len(ops)]
        for s in members:
            seen.add(tuple(s))
    return np.array(reps)


class View:
    """name, reps (v x 8), ops (real matrices spanning A, scaled so that ops[i] @ root is a root times scale[i])."""
    def __init__(self, name, reps, ops, d):
        self.name, self.reps, self.ops, self.d = name, reps, ops, d
        self.v = len(reps)
        NO = np.zeros((self.v, self.v), bool)
        for B in ops:
            NO |= (reps @ B @ reps.T) != 0
        np.fill_diagonal(NO, False)
        self.NO = NO  # A-non-orthogonal pairs (the decoder pattern forces B_TS = 0 there)
        self.w = self.arank(range(self.v))

    def arank(self, idx):
        rows = [B @ self.reps[i] for i in idx for B in self.ops]
        r = rank_q(rows) if rows else 0
        assert r % self.d == 0
        return r // self.d

    def pair_rank(self, R, A):
        """A-rank of the pairing span(R) x span(A) = real rank of the real Gram block / dim A (Theorem C cost)."""
        BR = [B @ self.reps[i] for i in R for B in self.ops]
        BA = [B @ self.reps[i] for i in A for B in self.ops]
        if not BR or not BA:
            return 0
        M = [[int(x @ y) for y in BA] for x in BR]
        r = rank_q(M); assert r % self.d == 0
        return r // self.d


def views():
    roots = e8_roots(); I8 = np.eye(8, dtype=np.int64)
    Li, Lj, Lk = left_quat()
    S = {tuple(r) for r in roots}
    for M in (Li, Lj, Lk):
        assert all(tuple(M @ r) in S for r in roots)
    g = a2_rotation(roots)  # 4*rho
    assert all(tuple(g @ r // 4) in S and ((g @ r) % 4 == 0).all() for r in roots)
    rho = g  # 4*rho (exact integer matrix); ranks are scale-free
    out = {}
    out['Gauss'] = View('Gauss', lines_over(roots, [I8, Li]), [I8, Li], 2)
    out['Eisen'] = View('Eisen', lines_over(roots, [I8, rho]), [I8, rho], 2)
    out['Hurwitz'] = View('Hurwitz', lines_over(roots, [I8, Li, Lj, Lk]), [I8, Li, Lj, Lk], 4)
    out['_J'], out['_rho'] = Li, rho
    return out


def gauss_gram(V, J):
    """hG(r_T, r_S) = (<r_T,r_S> + i<r_T, J r_S>)/4 as integer pairs (a, b)."""
    A = V @ V.T; Bm = V @ J @ V.T
    assert (A % 4 == 0).all() and (Bm % 4 == 0).all()
    return A // 4, Bm // 4


def eisen_gram(V, rho4):
    """hE(r_T, r_S) = (<r_T,r_S> - w<r_T, rho r_S>)/4 as integer pairs (a, b) = a + b w  (rho4 = 4*rho)."""
    A = V @ V.T; Bm = V @ rho4 @ V.T
    assert (A % 4 == 0).all() and (Bm % 16 == 0).all()
    return A // 4, -(Bm // 16)


if __name__ == '__main__':
    W = views()
    for nm in ('Gauss', 'Eisen', 'Hurwitz'):
        S = W[nm]
        print(nm, 'v', S.v, 'w', S.w, 'nonorth degree', sorted(set(S.NO.sum(1))))
