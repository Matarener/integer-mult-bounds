#!/usr/bin/env python3
"""Check recognition against independent orbits and literal transporters.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import sys
import json
from itertools import product
sys.path.insert(0, str(Path(__file__).resolve().parent))
from recognize import require, rank, inverse, matvec, identity, transpose, evaluate, recognize, rref


def quotient(p, polynomial):
    n = len(polynomial) - 1
    require(polynomial[-1] == 1, 'monic fixture')
    powers = []
    for k in range(2 * n - 1):
        v = [0] * max(n, k + 1)
        v[k] = 1
        for j in range(len(v) - 1, n - 1, -1):
            c = v[j]
            for i in range(n + 1):
                v[j - n + i] = (v[j - n + i] - c * polynomial[i]) % p
        powers.append(v[:n])
    return [[powers[i + j] for j in range(n)] for i in range(n)]


def direct_sum(tables):
    n = sum(map(len, tables))
    out = [[[0] * n for _ in range(n)] for _ in range(n)]
    offset = 0
    for table in tables:
        d = len(table)
        for i, j, k in product(range(d), repeat=3):
            out[offset + i][offset + j][offset + k] = table[i][j][k]
        offset += d
    return out


def change(t, P, Q, R, p):
    Pi, Qi = transpose(inverse(P, p)), transpose(inverse(Q, p))
    return [[matvec(R, evaluate(t, u, v, p), p) for v in Qi] for u in Pi]


def tensor_key(t):
    return tuple(x for row in t for v in row for x in v)


def check_certificate(t, c, p):
    n = len(t)
    a = c['table']
    U, V, W = (c[k] for k in ('U', 'V', 'W'))
    require(all(rank(x, p) == n for x in (U, V, W)), 'transporter singular')
    for i, j in product(range(n), repeat=2):
        got = evaluate(t, [r[i] for r in U], [r[j] for r in V], p)
        require(got == matvec(W, a[i][j], p), 'transporter identity')
        require(a[i][j] == a[j][i], 'commutative table')
        for k in range(n):
            left = evaluate(a, a[i][j], identity(n)[k], p)
            right = evaluate(a, identity(n)[i], a[j][k], p)
            require(left == right, 'associative table')
    equations = [[a[i][j][k] for i in range(n)] + [int(j == k)]
                 for j, k in product(range(n), repeat=2)]
    reduced, pivots = rref(equations, p)
    require(pivots == list(range(n)), 'unit equations')
    unit = [reduced[i][-1] for i in range(n)]
    columns = []
    for x in identity(n):
        v = unit
        for _ in range(p):
            v = evaluate(a, v, x, p)
        columns.append(v)
    require(rank(columns, p) == n, 'reduced table')
    return n * n


def gl(n, p):
    out = []
    for v in product(range(p), repeat=n * n):
        a = [list(v[i * n:(i + 1) * n]) for i in range(n)]
        if rank(a, p) == n:
            out.append(a)
    return out


def full_binary_census():
    G = gl(2, 2)
    split = direct_sum([quotient(2, [0, 1])] * 2)
    field = quotient(2, [1, 1, 1])
    expected = set()
    for t in (split, field):
        for P, Q, R in product(G, repeat=3):
            expected.add(tensor_key(change(t, P, Q, R, 2)))
    got = set()
    rejects = {}
    identities = 0
    for flat in product(range(2), repeat=8):
        t = [[list(flat[(i * 2 + j) * 2:(i * 2 + j + 1) * 2]) for j in range(2)] for i in range(2)]
        c, reason = recognize(t, 2)
        if c is not None:
            got.add(flat)
            identities += check_certificate(t, c, 2)
        else:
            rejects[reason] = rejects.get(reason, 0) + 1
    require(got == expected, 'complete binary tensor orbit classification')
    return len(got), identities, rejects


def changed_fixtures(p):
    base = quotient(p, [0, 1])
    quad = quotient(p, {2: [1, 1, 1], 3: [1, 0, 1], 5: [2, 0, 1]}[p])
    contexts = [(base, [1]), (direct_sum([base] * 3), [1, 1, 1]), (quad, [2]),
                (direct_sum([quad, base]), [1, 2]), (direct_sum([quad] * 2), [2, 2])]
    identities = 0
    for t, degrees in contexts:
        n = len(t)
        for trial in range(4):
            maps = []
            for salt in range(3):
                a = identity(n)
                if n > 1:
                    for step in range(n + trial + 1):
                        i = (step + salt) % n
                        j = (i + 1) % n
                        a[i] = [(x + (salt + trial + 1) * y) % p for x, y in zip(a[i], a[j])]
                    a = a[1:] + a[:1]
                maps.append(a)
            transformed = change(t, *maps, p)
            c, reason = recognize(transformed, p)
            require(c is not None and c['degrees'] == degrees, 'transformed fixture')
            identities += check_certificate(transformed, c, p)
    return identities


def negative_controls():
    controls = 0
    for p in (2, 3, 5):
        c, reason = recognize(quotient(p, [0, 0, 1]), p)
        require(c is None and reason == 'nilpotent nucleus', 'nilpotent rejection')
        controls += 1
        t = [[[0] * 4 for _ in range(4)] for _ in range(4)]
        for i, j, k, l in product(range(2), repeat=4):
            if j == k:
                t[2 * i + j][2 * k + l][2 * i + l] = 1
        c, reason = recognize(t, p)
        require(c is None and reason == 'noncommutative nucleus', 'matrix algebra rejection')
        controls += 1
    original = direct_sum([quotient(3, [0, 1])] * 2)
    c, _ = recognize(original, 3)
    for name in ('U', 'V', 'W'):
        for i, j in product(range(2), repeat=2):
            corrupt = {**c, name: [r[:] for r in c[name]]}
            corrupt[name][i][j] = (corrupt[name][i][j] + 1) % 3
            try:
                check_certificate(original, corrupt, 3)
            except ValueError:
                controls += 1
            else:
                raise ValueError('corrupt transporter accepted')
    for t, p in [([], 2), ([[[0]]], 4), ([[[2]]], 2)]:
        try:
            recognize(t, p)
        except ValueError:
            controls += 1
        else:
            raise ValueError('unsupported input accepted')
    return controls


def main():
    binary, identities, rejects = full_binary_census()
    accepted = binary
    tensors = 256
    for p in (2, 3, 5):
        for scalar in range(p):
            c, reason = recognize([[[scalar]]], p)
            tensors += 1
            require((c is not None) == (scalar != 0), 'one-dimensional recognition')
            if c is not None:
                identities += check_certificate([[[scalar]]], c, p)
                accepted += 1
        identities += changed_fixtures(p)
        tensors += 20
        accepted += 20
    print('PASS_ETALE_TENSOR_RECOGNITION ' + json.dumps(dict(tensors=tensors, accepted=accepted,
        basis_product_identities=identities, complete_binary_domain=dict(total=256, accepted=binary),
        rejections=rejects, changed_presentations=60, controls=negative_controls()), sort_keys=True))


if __name__ == '__main__':
    main()
