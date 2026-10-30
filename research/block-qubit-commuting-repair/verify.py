#!/usr/bin/env python3
"""Finite exact corroboration of the common-block theorem; writes no files."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def zero(n):
    require(type(n) is int and 1 <= n <= 20, 'matrix capacity')
    return [[F(0) for _ in range(n)] for _ in range(n)]


def identity(n):
    a = zero(n)
    for i in range(n):
        a[i][i] = F(1)
    return a


def transpose(a):
    return [list(row) for row in zip(*a, strict=True)]


def multiply(a, b):
    n = len(a)
    require(1 <= n <= 20 and len(b) == n, 'product capacity')
    require(all(len(row) == n for row in a + b), 'square matrices')
    columns = transpose(b)
    return [[sum(x*y for x, y in zip(row, col, strict=True))
             for col in columns] for row in a]


def subtract(a, b):
    return [[x-y for x, y in zip(row, col, strict=True)]
            for row, col in zip(a, b, strict=True)]


def norm2(a):
    # Interleaved realification doubles both trace and dimension.
    return sum(x*x for row in a for x in row) / len(a)


def pauli(k):
    require(k in (0, 1, 2), 'Pauli index')
    a = zero(4)
    if k == 0:
        for i, j in ((0, 2), (1, 3), (2, 0), (3, 1)):
            a[i][j] = F(1)
    elif k == 1:
        for i, j, sign in ((0, 3, 1), (1, 2, -1), (2, 1, -1), (3, 0, 1)):
            a[i][j] = F(sign)
    else:
        for i in range(4):
            a[i][i] = F(1 if i < 2 else -1)
    return a


def direct_sum(blocks):
    a = zero(sum(len(b) for b in blocks))
    offset = 0
    for b in blocks:
        for i, row in enumerate(b):
            for j, x in enumerate(row):
                a[offset+i][offset+j] = x
        offset += len(b)
    return a


def source(specs, singles, padded=False):
    require(1 <= len(specs) <= 3 and 0 <= singles <= 2, 'fixture domain')
    original, repaired = [], []
    for k in range(3):
        old, new = [], []
        for radii, shifts in specs:
            require(all(abs(a)+abs(r) <= 1 for a, r in zip(shifts, radii)),
                    'input contraction')
            squares = tuple(r*r for r in radii)
            winner = squares.index(max(squares))
            p = pauli(k)
            old.append([[shifts[k]*(i == j)+radii[k]*p[i][j]
                         for j in range(4)] for i in range(4)])
            new.append([[shifts[k]*(i == j)+(radii[k]*p[i][j] if k == winner else 0)
                         for j in range(4)] for i in range(4)])
        scalar = F(0) if padded else F(k-1, 7)
        old.extend([[[scalar, F(0)], [F(0), scalar]]] * singles)
        new.extend([[[scalar, F(0)], [F(0), scalar]]] * singles)
        original.append(direct_sum(old))
        repaired.append(direct_sum(new))
    return original, repaired


def aggregate(m, singles, errors, deltas, reported=None):
    require(type(m) is int and type(singles) is int, 'integer block counts')
    require(0 <= m <= 4 and 0 <= singles <= 4 and 2*m+singles > 0, 'block domain')
    require(len(errors) == len(deltas) == m, 'block count')
    require(all(e >= 0 and q >= 3*e*e for e, q in zip(errors, deltas)),
            'cited local inequality')
    alpha = F(2, 2*m+singles)
    weight = m*alpha
    error = alpha*sum(errors)
    delta = alpha*sum(deltas)
    if reported is not None:
        require(reported == (weight, error, delta), 'global normalization')
    gap = alpha**2 * (m*sum(q-3*e*e for e, q in zip(errors, deltas))
                     + 3*sum((a-b)**2 for a, b in combinations(errors, 2)))
    require(weight*delta-3*error**2 == gap >= 0, 'weighted gap identity')
    return weight, error, delta


def check_aggregation():
    states = tuple((F(e, 8), 3*F(e, 8)**2+F(slack, 4))
                   for e in (0, 1, 4, 8) for slack in (0, 1))
    count = 0
    for m in range(5):
        for choices in product(states, repeat=m):
            errors = tuple(e for e, _ in choices)
            deltas = tuple(q for _, q in choices)
            for singles in range(5):
                if 2*m+singles > 0:
                    aggregate(m, singles, errors, deltas)
                    count += 1
    return count


def check_literal():
    radii = ((F(1, 4),)*3, (F(1, 2), F(1, 3), F(1, 4)),
             (F(1, 2), F(0), F(0)), (F(0),)*3)
    shifts = (F(1, 10), F(-1, 9), F(1, 8))
    count = 0
    for m in range(1, 3):
        for chosen in product(radii, repeat=m):
            errors = tuple(sum(r*r for r in rs)-max(r*r for r in rs) for rs in chosen)
            deltas = tuple(4*sum(a*a*b*b for a, b in combinations(rs, 2)) for rs in chosen)
            for singles in range(3):
                original, repaired = source(tuple((rs, shifts) for rs in chosen), singles)
                error = sum(norm2(subtract(a, b)) for a, b in zip(original, repaired))
                delta = sum(norm2(subtract(multiply(a, b), multiply(b, a)))
                            for a, b in combinations(original, 2))
                for a, b in combinations(repaired, 2):
                    require(multiply(a, b) == multiply(b, a), 'commuting direct sum')
                for a in original+repaired:
                    require(a == transpose(a), 'Hermitian realification')
                weight = F(2*m, 2*m+singles)
                aggregate(m, singles, errors, deltas, (weight, error, delta))
                count += 1
    return count


def unitary_basis(d, pair=None, phase=False):
    u = identity(2*d)
    if pair is None:
        return u
    p, q = pair
    require(0 <= p < q < d, 'basis pair')
    c, s = F(3, 5), F(4, 5)
    if phase:
        u[2*p][2*p], u[2*p][2*p+1] = c, -s
        u[2*p+1][2*p], u[2*p+1][2*p+1] = s, c
    for row in u:
        for t in range(2):
            x, y = row[2*p+t], row[2*q+t]
            row[2*p+t], row[2*q+t] = c*x+s*y, -s*x+c*y
    return u


def validate_basis(u):
    require(len(u) % 2 == 0, 'complex dimension')
    require(multiply(transpose(u), u) == identity(len(u)), 'unitary basis')
    for row in range(0, len(u), 2):
        for col in range(0, len(u), 2):
            require(u[row][col] == u[row+1][col+1]
                    and u[row+1][col] == -u[row][col+1], 'complex structure')


def quadratic(a, v):
    return sum(v[i]*sum(x*y for x, y in zip(row, v, strict=True))
               for i, row in enumerate(a))


def check_mixed_basis(original, u, m, r):
    validate_basis(u)
    d = len(u)//2
    occupancy, capture = F(0), F(0)
    for k in range(d):
        v = [row[2*k] for row in u]
        t = sum(x*x for x in v[:4*m])
        nx = sum(v[4*j]**2+v[4*j+1]**2 for j in range(m))
        ny = sum(v[4*j+2]**2+v[4*j+3]**2 for j in range(m))
        re = sum(v[4*j]*v[4*j+2]+v[4*j+1]*v[4*j+3] for j in range(m))
        im = sum(v[4*j]*v[4*j+3]-v[4*j+1]*v[4*j+2] for j in range(m))
        gram = nx*ny-re*re-im*im
        diagonal = tuple(quadratic(a, v) for a in original)
        bloch2 = sum(x*x for x in diagonal)/(r*r)
        require(gram >= 0 and bloch2 == t*t-4*gram <= t*t <= t, 'column bound')
        require(all(abs(x) <= 1 for x in diagonal), 'diagonal contractions')
        occupancy += t
        capture += sum(x*x for x in diagonal)
    require(occupancy == 2*m and capture <= 2*m*r*r, 'all-basis capture bound')
    weight = F(2*m, d)
    candidate_error = sum(norm2(a) for a in original)-capture/d
    require(candidate_error >= 2*weight*r*r, 'unrestricted repair lower bound')
    return candidate_error


def check_sharpness():
    witnesses, bases = 0, 0
    for m in range(1, 4):
        for singles in range(3):
            d = 2*m+singles
            for r in (F(1, 8), F(1, 4), F(1, 2)):
                original, repaired = source((((r,)*3, (F(0),)*3),)*m, singles, True)
                weight = F(2*m, d)
                error = sum(norm2(subtract(a, b)) for a, b in zip(original, repaired))
                require(error == 2*weight*r*r, 'attaining repair')
                delta = sum(norm2(subtract(multiply(a, b), multiply(b, a)))
                            for a, b in combinations(original, 2))
                require(delta == 12*weight*r**4, 'sharp commutator normalization')
                require(3*error**2 == weight*delta, 'sharp constant')
                require(check_mixed_basis(original, identity(2*d), m, r) == error,
                        'common-basis attainment')
                bases += 1
                for pair in combinations(range(d), 2):
                    for phase in (False, True):
                        u = unitary_basis(d, pair, phase)
                        check_mixed_basis(original, u, m, r)
                        bases += 1
                witnesses += 1
    return witnesses, bases


def check_controls():
    count = 0
    for case in range(8):
        try:
            if case == 0:
                aggregate(0, 0, (), ())
            elif case == 1:
                aggregate(2, 0, (F(1),), (F(3),))
            elif case == 2:
                aggregate(1, 1, (F(-1),), (F(3),))
            elif case == 3:
                aggregate(1, 1, (F(1),), (F(2),))
            elif case == 4:
                aggregate(1, 1, (F(1),), (F(3),), (F(1), F(2, 3), F(2)))
            elif case == 5:
                aggregate(1, 1, (F(1),), (F(3),), (F(2, 3), F(2, 3), F(3)))
            elif case == 6:
                bad = identity(4)
                bad[0][0] = F(2)
                validate_basis(bad)
            else:
                bad = identity(4)
                bad[0], bad[2] = bad[2], bad[0]
                validate_basis(bad)
        except ValueError:
            count += 1
        else:
            raise ValueError('accepted negative control '+str(case))
    return count


def receipt(results):
    package = Path(__file__).resolve().parent
    names = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    hashes = {}
    for name in names:
        path = package/name
        require(path.is_file() and path.stat().st_size <= 100_000, 'package capacity')
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    sources = json.loads((package/'SOURCES.json').read_text())
    require(len(sources['files']) <= 8, 'source capacity')
    for row in sources['files']:
        if row['usage'] == 'input':
            path = package.parents[1]/row['path']
            require(path.is_file() and path.stat().st_size <= 1_000_000, 'input capacity')
            require(sha256(path.read_bytes()).hexdigest() == row['sha256'], 'input pin')
    output = {'status': 'PASS_BLOCK_QUBIT_COMMUTING_REPAIR', **results, 'sha256': hashes}
    print(json.dumps(output, sort_keys=True))


if __name__ == '__main__':
    count = check_aggregation()
    literal = check_literal()
    witnesses, bases = check_sharpness()
    controls = check_controls()
    receipt({'weighted_profiles': count, 'literal_direct_sums': literal,
             'sharp_witnesses': witnesses, 'mixed_bases': bases, 'controls': controls})
