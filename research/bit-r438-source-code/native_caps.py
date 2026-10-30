"""Independent exact rational E8 cap ADDRESS identities; no controller."""
from fractions import Fraction as Q
from hashlib import sha256
import json

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def rank(rows):
    basis = {}
    for row in rows:
        row = list(map(Q, row))
        for j, old in sorted(basis.items()):
            c = row[j]
            row = [x-c*y for x,y in zip(row,old)]
        j = next((j for j,x in enumerate(row) if x), None)
        if j is not None:
            c = row[j]
            basis[j] = [x/c for x in row]
    return len(basis)

def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]

def multiply(a, b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]

def exchange(u):
    c = [[Q(i == j)-u[i][j] for j in range(8)] for i in range(8)]
    return [c[i]+u[i] for i in range(8)]+[u[i]+c[i] for i in range(8)]

def address_identities(word):
    ident = identity(8)
    out = []
    for p, q in enumerate(word['lines']):
        need(sum(x*x for x in q) == 4, 'actual E8 root norm')
        start = [word['lines'][j] for j in word['frames'][word['start'][p]]]
        cap = [word['lines'][j] for j in word['frames'][word['final'][111+p]]]
        need(rank(start) == 1 and all(all(4*x == sum(a*b for a,b in zip(row,q))*y
             for x,y in zip(row,q)) for row in start), 'actual entrance is not P_p')
        need(rank(cap) == 7 and all(sum(x*y for x,y in zip(row,q)) == 0 for row in cap),
             'actual target cap is not K_p')
        proj = [[Q(x*y,4) for y in q] for x in q]
        complement = [[ident[i][j]-proj[i][j] for j in range(8)] for i in range(8)]
        need(multiply(proj,proj) == proj and rank(proj) == 1, 'actual P_p projector')
        need(multiply(exchange(ident),exchange(proj)) == exchange(complement),
             'D_I D_P differs from D_K')
        need(multiply(exchange(proj),exchange(proj)) == identity(16), 'D_P squared differs from I')
        encoded = [[[v.numerator,v.denominator] for v in row] for row in proj]
        out.append(sha256(canonical(encoded)).hexdigest())
    need(len(out) == 111, 'actual punctured root count')
    return out
