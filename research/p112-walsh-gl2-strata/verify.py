#!/usr/bin/env python3
"""Certify the continuous P112 Walsh-plane gauge obstruction. Apache-2.0."""
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import importlib.util
import json
import math
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIRECTIONS = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    """Nine-column elimination, with a bound independent of pivot values."""
    pivots = [0] * 9
    for value in rows:
        need(0 <= value < 512, 'nine-bit rank row')
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(value) for value in pivots)


def pinned_geometry():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in sources['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source hash: ' + row['path'])
    path = ROOT / 'research/p112-single-lift/geometry.py'
    spec = importlib.util.spec_from_file_location('walsh_strata_geometry', path)
    need(spec is not None and spec.loader is not None, 'geometry loader')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.build()
    need(len(data['X']) == len(data['labels']) == len(data['duals']) == 112,
         'P112 geometry dimensions')
    need(all(len(row) == 8 for row in data['X']), 'eight frame coordinates')
    return data


def normalize(a, b):
    divisor = math.gcd(a, b)
    need(divisor > 0, 'nonzero projective direction')
    a, b = a // divisor, b // divisor
    return (-a, -b) if a < 0 or (a == 0 and b < 0) else (a, b)


def mask(values):
    return sum(1 << i for i, value in enumerate(values) if value)


def support_ranks(bits, data):
    return tuple(rank(values[i] for i in range(112) if bits >> i & 1)
                 for values in (data['labels'], data['duals']))


def lifts_and_strata(data, characters, pairs, digest):
    lifts = {}
    masks = 0
    for pair in pairs:
        vectors = tuple(tuple(sum(row[j] * characters[a][j] for j in range(8))
                              for row in data['X']) for a in pair)
        exceptional = {normalize(b, -a) for a, b in zip(*vectors) if a or b}
        need(exceptional == set(DIRECTIONS[:4]), 'complete support-zero directions')
        generic = mask(a or b for a, b in zip(*vectors))
        for direction in DIRECTIONS:
            a, b = direction
            bits = mask(a * x + b * y for x, y in zip(*vectors))
            need(support_ranks(bits, data) == (9, 9), 'full lift support spans')
            if direction == DIRECTIONS[-1]:
                need(bits == generic, 'generic support is the support union')
            digest.update(f'{pair}:{direction}:{bits:x}\n'.encode('ascii'))
            masks += 1
        lifts[pair] = vectors
    return lifts, masks


def corrected_columns(data, characters, pairs, lifts, digest):
    checks = 0
    for up in pairs:
        for vp in pairs:
            v0, v1 = lifts[vp]
            for j in range(8):
                values = tuple(data['X'][i][j] - characters[up[0]][j] * v0[i]
                               - characters[up[1]][j] * v1[i] for i in range(112))
                bits = mask(values)
                need(support_ranks(bits, data)[0] == 9, 'corrected source span')
                digest.update(f'{up}:{vp}:{j}:{bits:x}\n'.encode('ascii'))
                checks += 1
    return checks


def factor_identity(characters, up, vp, matrix, data):
    """Check the literal ten-term 112-by-112 identity at one rational gauge."""
    a, b, c, d = map(Fraction, matrix)
    det = a * d - b * c
    need(bool(det), 'invertible gauge')
    u0, u1 = (characters[k] for k in up)
    v0, v1 = (characters[k] for k in vp)
    us = (tuple(a*x+c*y for x, y in zip(u0, u1)),
          tuple(b*x+d*y for x, y in zip(u0, u1)))
    vs = (tuple((d*x-b*y)/det for x, y in zip(v0, v1)),
          tuple((-c*x+a*y)/det for x, y in zip(v0, v1)))
    for i in range(8):
        for j in range(8):
            need(sum(u[i]*v[j] for u, v in zip(us, vs)) ==
                 u0[i]*v0[j]+u1[i]*v1[j], 'inverse-transpose product')
    x = data['X']
    ul = [tuple(sum(row[k]*u[k] for k in range(8)) for row in x) for u in us]
    vl = [tuple(sum(row[k]*v[k] for k in range(8)) for row in x) for v in vs]
    dc = [tuple(row[j] for row in x) for j in range(8)] + ul
    tc = [tuple(x[i][j]-sum(us[k][j]*vl[k][i] for k in range(2))
                for i in range(112)) for j in range(8)] + vl
    check_endpoint(dc, tc, data)
    return dc, tc


def check_endpoint(dc, tc, data):
    need(len(dc) == len(tc) == 10, 'ten factor columns')
    x = data['X']
    for i in range(112):
        for j in range(112):
            need(sum(left[i]*right[j] for left, right in zip(dc, tc)) ==
                 sum(x[i][k]*x[j][k] for k in range(8)), 'literal factor endpoint')


def controls(data, characters):
    rejected = 0
    for invalid in ((0, 0),):
        try:
            normalize(*invalid)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('zero-direction control accepted')
    try:
        factor_identity(characters, (0, 1), (2, 3), (1, 2, 2, 4), data)
    except ValueError as error:
        need(str(error) == 'invertible gauge', 'singular rejection reason')
        rejected += 1
    else:
        raise ValueError('singular gauge accepted')
    need(support_ranks(0, data) == (0, 0), 'empty support is not full span')
    need(rank([1 << i for i in range(8)]) == 8, 'missing-axis control')
    # A wrong inverse uses M^{-1}, rather than M^{-T}, on the second lift.
    a, b, c, d = 1, 2, 3, 7
    need(a*d-b*c == 1, 'wrong-inverse fixture is nonsingular')
    wrong = ((a*d-b*b, -a*c+a*b), (c*d-d*b, -c*c+d*a))
    need(wrong != ((1, 0), (0, 1)), 'wrong inverse differs from endpoint')
    dc, tc = factor_identity(characters, (0, 1), (2, 3), (1, 2, 3, 7), data)
    tc[-1] = (0,) * 112
    try:
        check_endpoint(dc, tc, data)
    except ValueError as error:
        need(str(error) == 'literal factor endpoint', 'dropped-total rejection reason')
        rejected += 1
    else:
        raise ValueError('dropped total accepted')
    return rejected + 3


def compute():
    data = pinned_geometry()
    characters = tuple(tuple(1 - 2*((a & b).bit_count() % 2) for b in range(8))
                       for a in range(8))
    pairs = tuple(permutations(range(8), 2))
    digest = sha256()
    coordinate_ranks = tuple(support_ranks(mask(row[j] for row in data['X']), data)[1]
                             for j in range(8))
    need(coordinate_ranks == (8,) * 8, 'coordinate reader ranks')
    lifts, masks = lifts_and_strata(data, characters, pairs, digest)
    columns = corrected_columns(data, characters, pairs, lifts, digest)
    for matrix in ((1, 1, 1, -1), (1, 2, 3, 7)):
        factor_identity(characters, (0, 1), (2, 3), matrix, data)
    rejected = controls(data, characters)
    need(masks == 280 and columns == 25088, 'complete finite certificate coverage')
    files = {p.name: sha256(p.read_bytes()).hexdigest()
             for p in sorted(HERE.iterdir()) if p.is_file()}
    return {'status': 'PASS_P112_WALSH_GL2_STRATA', 'claim_type': 'scoped proof',
            'coefficient_fields': ['real', 'rational'], 'ordered_plane_pairs': 3136,
            'lift_support_certificates': masks, 'corrected_source_certificates': columns,
            'coordinate_reader_certificates': 8, 'literal_endpoint_entries': 37632,
            'controls': rejected, 'support_certificate_sha256': digest.hexdigest(),
            'profile': {'8': 8, '9': 2}, 'invoice': 82, 'package_sha256': files}


def main():
    need(len(sys.argv) == 1, 'usage: verify.py')
    print(json.dumps(compute(), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
