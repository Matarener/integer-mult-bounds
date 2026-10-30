# SPDX-License-Identifier: Apache-2.0
"""Exact small rational matrices. Ali Romman with OpenAI Codex assistance."""
from fractions import Fraction as Q


def need(test, message):
    if not test:
        raise ValueError(message)


def matrix(rows):
    return tuple(tuple(Q(x) for x in row) for row in rows)


def eye(n=8):
    return matrix([[int(i==j) for j in range(n)] for i in range(n)])


def transpose(a):
    return tuple(zip(*a))


def product(a,b):
    return tuple(tuple(sum(x*y for x,y in zip(row,col)) for col in zip(*b)) for row in a)


def difference(a,b):
    return tuple(tuple(x-y for x,y in zip(row,col)) for row,col in zip(a,b))


def scale(a,k):
    return tuple(tuple(k*x for x in row) for row in a)


def inverse(a):
    n=len(a); rows=[list(row)+list(e) for row,e in zip(a,eye(n))]
    for j in range(n):
        pivot=next((i for i in range(j,n) if rows[i][j]),None)
        need(pivot is not None,'nonsingular basis')
        rows[j],rows[pivot]=rows[pivot],rows[j]
        value=rows[j][j]; rows[j]=[x/value for x in rows[j]]
        for i in range(n):
            if i!=j:
                value=rows[i][j]; rows[i]=[x-value*y for x,y in zip(rows[i],rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def row_basis(a):
    rows=[list(row) for row in a]; used=0
    for j in range(len(rows[0])):
        pivot=next((i for i in range(used,len(rows)) if rows[i][j]),None)
        if pivot is None:
            continue
        rows[used],rows[pivot]=rows[pivot],rows[used]
        value=rows[used][j]; rows[used]=[x/value for x in rows[used]]
        for i in range(len(rows)):
            if i!=used:
                value=rows[i][j]; rows[i]=[x-value*y for x,y in zip(rows[i],rows[used])]
        used+=1
    return tuple(tuple(row) for row in rows[:used])


def diagonal(rank):
    return matrix([[int(i==j and i<rank) for j in range(8)] for i in range(8)])


def physical(p):
    """Lift an eight-coordinate projector to the sixteen paired addresses."""
    h=[list(row) for row in eye(16)]
    for i in range(8):
        for j in range(8):
            h[i][j]-=p[i][j]; h[i][15-j]+=p[i][j]
            h[15-i][j]+=p[i][j]; h[15-i][15-j]-=p[i][j]
    return tuple(tuple(row) for row in h)
