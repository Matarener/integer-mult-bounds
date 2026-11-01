"""Rank certificates for RankNine.certOK (T3.3/T3.4).  For lines W (roots in A8 coordinates) plus the all-ones
vector and a pivot set piv, find integer rows N_j (over a basis subset X of W) and No_j (over ones) and D with
  sum_t N_j[t] rho_{X t} + No_j * 1 = D e_j   on every non-pivot coordinate,  for every non-pivot j.
Exists iff rank of (rho(W) + 1) restricted to the non-pivot coordinates is 9 - |piv|."""
import sys
from fractions import Fraction
from math import lcm
sys.path.insert(0, '.')
from p104lib import P, RT
ONES = (1,) * 9
def rootv(x): return RT[P[x]]
def cert(W, piv):
    """W: list of line indices; piv: list of pivot coordinates. Returns (X, N, No, D, pm) or None."""
    free = [i for i in range(9) if i not in piv]; n = len(free)
    vecs = [('l', x, [Fraction(rootv(x)[i]) for i in free]) for x in W] + [('o', None, [Fraction(1)] * n)]
    # greedy basis of the row space (restricted to free coordinates)
    basis = []; ech = []   # ech: reduced rows with pivot column
    for tag, x, v in vecs:
        r = v[:]
        for (pc, er) in ech:
            if r[pc]:
                f = r[pc] / er[pc]; r = [a - f * b for a, b in zip(r, er)]
        nz = [i for i in range(n) if r[i]]
        if nz:
            ech.append((nz[0], r)); basis.append((tag, x, v))
        if len(basis) == n: break
    if len(basis) < n: return None
    # solve: coefficients a (len n) with sum_k a_k basis_k = e_j  ->  a = e_j^T B^{-1}, B rows = basis vectors
    Bm = [b[2][:] for b in basis]
    # invert Bm (n x n) by Gauss-Jordan
    A = [Bm[r][:] + [Fraction(int(r == c)) for c in range(n)] for r in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c]); A[c], A[p] = A[p], A[c]
        pv = A[c][c]; A[c] = [a / pv for a in A[c]]
        for r in range(n):
            if r != c and A[r][c]:
                f = A[r][c]; A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    Inv = [row[n:] for row in A]   # Bm Inv = I  ->  rows: we need a with a Bm = e_j  ->  a = e_j Inv
    rows = {}
    for jj, j in enumerate(free):
        rows[j] = [Inv[k][jj] for k in range(n)]   # a_k = (Inv)_{k? }  -- verify below
    # a Bm = e_j : a_k = Inv[j-th row]?  Bm^{-1} = Inv, so e_j Bm^{-1} Bm = e_j, a = row jj of Inv
    rows = {j: Inv[jj][:] for jj, j in enumerate(free)}
    D = 1
    for a in rows.values():
        for q in a: D = lcm(D, q.denominator)
    X = [x for tag, x, v in basis if tag == 'l']
    io = [k for k, b in enumerate(basis) if b[0] == 'o']
    il = [k for k, b in enumerate(basis) if b[0] == 'l']
    N = [[0] * len(X) for _ in range(9)]; No = [0] * 9
    for j, a in rows.items():
        N[j] = [int(a[k] * D) for k in il]
        No[j] = int(a[io[0]] * D) if io else 0
    pm = sum(1 << i for i in piv)
    assert check(X, N, No, D, pm)
    return X, N, No, D, pm
def check(X, N, No, D, pm):   # RankNine.certOK
    if D == 0: return False
    for j in range(9):
        if pm >> j & 1: continue
        for i in range(9):
            if pm >> i & 1: continue
            v = sum(N[j][t] * rootv(X[t])[i] for t in range(len(X))) + No[j]
            if v != (D if i == j else 0): return False
    return True
