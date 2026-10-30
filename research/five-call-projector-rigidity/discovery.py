"""Prepare the complete compatible-projector census over an odd prime.

The compiled search checks only the query-character condition. A surviving
triple still needs endpoint projectors and the required stage powers.
"""
import argparse
from itertools import product
import json
from pathlib import Path


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mm(a, b, p):
    return [[sum(x*y for x, y in zip(row, col)) % p
             for col in zip(*b)] for row in a]


def inv(a, p):
    n = len(a)
    a = [r[:] + s for r, s in zip(a, eye(n))]
    for j in range(n):
        k = next(i for i in range(j, n) if a[i][j] % p)
        a[j], a[k] = a[k], a[j]
        z = pow(a[j][j], -1, p)
        a[j] = [x*z % p for x in a[j]]
        for i in range(n):
            if i != j:
                z = a[i][j]
                a[i] = [(x-z*y) % p for x, y in zip(a[i], a[j])]
    return [r[n:] for r in a]


def data(p, mask=0):
    n = 4
    ident = eye(n)
    us = [[int(i == j) for i in range(n)] for j in range(n)] + [[-1, 1, -1, 1]]
    vs = [[0 if i == j else (1 if i > j else -1) for j in range(n)] for i in range(n+1)]
    queries = [[[a*b % p for b in v] for a in u] for u, v in zip(us, vs)]
    ts = [[[(ident[i][j]-2*q[i][j]) % p for j in range(n)] for i in range(n)] for q in queries]
    endpoint = ident
    for t in ts:
        endpoint = mm(t, endpoint, p)
    if endpoint != [[-a % p for a in row] for row in ident]:
        raise ValueError('The skew-simplex endpoint fails')
    choices = []
    for site in range(1, 4):
        u, v = us[site], vs[site]
        pivot = next(j for j, a in enumerate(v) if a)
        a = [int(j == pivot)*pow(v[pivot] % p, -1, p) % p for j in range(n)]
        cols = [u, a]
        for j in range(n):
            if j not in (site, pivot):
                cols.append([(int(k == j)-v[j]*a[k]) % p for k in range(n)])
        basis = list(map(list, zip(*cols)))
        inverse = inv(basis, p)
        family = []
        for a0, a1, b0, b1 in product(range(p), repeat=4):
            core = [[1, -a0*b0-a1*b1, b0, b1], [0, 1, 0, 0],
                    [0, a0, 0, 0], [0, a1, 0, 0]]
            proj = mm(mm(basis, core, p), inverse, p)
            q = queries[site]
            if mm(proj, proj, p) != proj or mm(proj, q, p) != q or mm(q, proj, p) != q:
                raise ValueError('A compatible projector fails')
            if mask >> site & 1:
                proj = [[(ident[i][j]-proj[i][j]) % p for j in range(n)] for i in range(n)]
            family.append(proj)
        if len({tuple(x for row in a for x in row) for a in family}) != p**4:
            raise ValueError('The projector chart is not injective')
        choices.append(family)
    return ts, choices


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prime', type=int, choices=(3, 5, 7, 11), required=True)
    parser.add_argument('--mask', type=int, default=0)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ts, choices = data(args.prime, args.mask)
    with args.output.open('w') as f:
        f.write(f'{args.prime} {args.prime**4}\n')
        for a in ts + [a for family in choices for a in family]:
            f.write(' '.join(str(x) for row in a for x in row)+'\n')
    print(json.dumps({'prime':args.prime, 'mask':args.mask, 'per_site':args.prime**4}))
