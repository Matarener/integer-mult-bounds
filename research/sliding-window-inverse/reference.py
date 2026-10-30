# SPDX-License-Identifier: Apache-2.0
"""Separate forward-elimination/back-substitution oracle, no cache imports."""
from fractions import Fraction as F

def solve(A,b):
    n=len(A);M=[list(map(F,row))+[F(b[i])] for i,row in enumerate(A)]
    for k in range(n):
        pivot=next(i for i in range(k,n) if M[i][k]);M[k],M[pivot]=M[pivot],M[k]
        for i in range(k+1,n):
            f=M[i][k]/M[k][k]
            for j in range(k,n+1):M[i][j]-=f*M[k][j]
    x=[F(0)]*n
    for i in range(n-1,-1,-1):x[i]=(M[i][n]-sum((M[i][j]*x[j] for j in range(i+1,n)),F(0)))/M[i][i]
    return x

def inverse(A):
    n=len(A);cols=[solve(A,[F(i==j) for i in range(n)]) for j in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]

def determinant(A):
    if not A:return F(1)
    return sum(((-1)**j*A[0][j]*determinant([r[:j]+r[j+1:] for r in A[1:]]) for j in range(len(A))),F(0))
