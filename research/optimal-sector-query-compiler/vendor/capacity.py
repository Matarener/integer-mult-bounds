"""Compute exact unit-channel capacity over Z[1/2].

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def need(test, message):
    if not test:
        raise ValueError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def smith(matrix):
    """Return U, S, V with U M V = S in integer Smith form."""
    a = [list(row) for row in matrix]
    m, n = len(a), len(a[0]) if a else 0
    need(all(len(row) == n and all(type(x) is int for x in row) for row in a),
         'Rectangular integer matrix')
    u, v = eye(m), eye(n)

    def row_add(i, j, q):
        a[i] = [x+q*y for x,y in zip(a[i],a[j])]
        u[i] = [x+q*y for x,y in zip(u[i],u[j])]

    def col_add(i, j, q):
        for z in (a, v):
            for row in z:
                row[i] += q*row[j]

    def row_swap(i, j):
        a[i],a[j] = a[j],a[i]
        u[i],u[j] = u[j],u[i]

    def col_swap(i, j):
        for z in (a, v):
            for row in z:
                row[i],row[j] = row[j],row[i]

    for k in range(min(m,n)):
        positions = [(abs(a[i][j]),i,j) for i in range(k,m)
                     for j in range(k,n) if a[i][j]]
        if not positions:
            break
        _,i,j = min(positions)
        row_swap(k,i)
        col_swap(k,j)
        while True:
            changed = False
            for i in range(k+1,m):
                if a[i][k]:
                    row_add(i,k,-(a[i][k]//a[k][k]))
                    if a[i][k]:
                        row_swap(i,k)
                    changed = True
                    break
            if changed:
                continue
            for j in range(k+1,n):
                if a[k][j]:
                    col_add(j,k,-(a[k][j]//a[k][k]))
                    if a[k][j]:
                        col_swap(j,k)
                    changed = True
                    break
            if changed:
                continue
            bad = next(((i,j) for i in range(k+1,m) for j in range(k+1,n)
                        if a[i][j] % a[k][k]), None)
            if bad is None:
                break
            row_add(k,bad[0],1)
        if a[k][k] < 0:
            a[k] = [-x for x in a[k]]
            u[k] = [-x for x in u[k]]
    return u,a,v


def capacity(pairing):
    q = [[Q(x) for x in row] for row in pairing]
    d = max((x.denominator for row in q for x in row), default=1)
    need(all(x.denominator & (x.denominator-1) == 0 for row in q for x in row),
         'Dyadic pairing')
    a = [[int(d*x) for x in row] for row in q]
    u,s,v = smith(a)
    factors = [s[i][i] for i in range(min(len(s),len(v))) if s[i][i]]
    rank = len(factors)
    count = next((i for i,x in enumerate(factors) if x & (x-1)),rank)
    left = [[Q(d*x,factors[i]) for x in u[i]] for i in range(count)]
    right = [row[:count] for row in v]
    return dict(capacity=count, rational_rank=rank, denominator=d,
                factors=factors, U=u, S=s, V=v, left=left, right=right)


def kernel(matrix, columns):
    """Return a full dyadic kernel basis as columns."""
    if not matrix:
        return eye(columns)
    q = [[Q(x) for x in row] for row in matrix]
    d = max(x.denominator for row in q for x in row)
    need(all(x.denominator & (x.denominator-1) == 0 for row in q for x in row),
         'Dyadic constraint matrix')
    _,s,v = smith([[int(d*x) for x in row] for row in q])
    rank = sum(s[i][i] != 0 for i in range(min(len(s),columns)))
    return [row[rank:] for row in v]
