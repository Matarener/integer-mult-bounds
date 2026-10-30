#!/usr/bin/env python3
"""Separate exact rational audit of two complex P104 rank-seven witnesses.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas (PR6183) retains the deflation construction and Matarener
(PR6166) the cited D8 coordinate identification and omitted-root data.
No primary or predecessor executable code is imported.
"""

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

ZERO = (F(0), F(0))
SOURCE_SHA256 = '9ddfcf087912e02c46722d5a82eea5f1221a4a33d5037a0d90d392dfcd3c06d4'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plus(x, y):
    return x[0] + y[0], x[1] + y[1]


def minus(x, y):
    return x[0] - y[0], x[1] - y[1]


def times(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def scale(x, scalar):
    return x[0] * scalar, x[1] * scalar


def conjugate(x):
    return x[0], -x[1]


def squared(x):
    return x[0] ** 2 + x[1] ** 2


def divide(x, y):
    require(y != ZERO, 'nonzero Gaussian pivot')
    return scale(times(x, conjugate(y)), 1 / squared(y))


def gaussian_dot(row, column):
    answer = ZERO
    for x, y in zip(row, column, strict=True):
        answer = plus(answer, times(x, y))
    return answer


def matrix_product(a, b):
    columns = list(zip(*b, strict=True))
    return [[gaussian_dot(row, col) for col in columns] for row in a]


def matrix_rank(matrix):
    rows = [row[:] for row in matrix]
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col] != ZERO), None)
        if pivot is None:
            continue
        rows[pivot], rows[rank] = rows[rank], rows[pivot]
        divisor = rows[rank][col]
        rows[rank] = [divide(x, divisor) for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            if rows[i][col] != ZERO:
                multiplier = rows[i][col]
                rows[i] = [minus(x, times(multiplier, y))
                           for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
        if rank == min(len(rows), len(rows[0])):
            break
    return rank


def root_rows():
    source = Path(__file__).resolve().parents[1] / 'p104-contractive-gram-deflation/MISSING.json'
    raw = source.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'pinned root-data bytes')
    omitted = set()
    for signs in json.loads(raw)['signs']:
        require(len(signs) == 8 and set(signs) <= {'+', '-'}, 'root signs')
        row = tuple(1 if c == '+' else -1 for c in signs)
        omitted.add(row if row[0] == 1 else tuple(-x for x in row))
    shell = {(1, *tail) for tail in itertools.product((1, -1), repeat=7)
             if tail.count(-1) % 2 == 1}
    require(len(omitted) == 16 and omitted <= shell, 'sixteen distinct odd omitted lines')
    # Half-spin rows first; this ordering is deliberately independent of port labels.
    rows = sorted(shell - omitted)
    for i, j in itertools.combinations(range(8), 2):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            rows.append(tuple(row))
    require(len(rows) == len(set(rows)) == 104, '104 distinct retained lines')
    require(all(sum(x * x for x in row) == 8 for row in rows), 'doubled root norms')
    return rows


def frame_indices(rows):
    indices = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            indices.append(rows.index(tuple(row)))
    gram = [[sum(x * y for x, y in zip(rows[i], rows[j], strict=True))
             for j in indices] for i in indices]
    require(gram == [[8 * (i == j) for j in range(8)] for i in range(8)],
            'invertible orthogonal root submatrix')
    return indices


def projector(z, norm):
    return [[minus((F(i == j), F(0)), scale(times(x, conjugate(y)), F(1, norm)))
             for j, y in enumerate(z)] for i, x in enumerate(z)]


def literal_gram_candidate(rows, d):
    # Multiply S D first, then by S^T/8. No outer-residual formula is used here.
    left = []
    for row in rows:
        new = []
        for j in range(8):
            value = ZERO
            for i in range(8):
                value = plus(value, scale(d[i][j], row[i]))
            new.append(value)
        left.append(new)
    candidate = []
    for row in left:
        new = []
        for source in rows:
            value = ZERO
            for x, coefficient in zip(row, source, strict=True):
                value = plus(value, scale(x, coefficient))
            new.append(scale(value, F(1, 8)))
        candidate.append(new)
    return candidate


def check_witness(rows, indices, integer_pairs, expected_norm, expected_max, expected_error):
    z = [(F(a), F(b)) for a, b in integer_pairs]
    norm = sum(squared(x) for x in z)
    require(norm == expected_norm, 'exact vector norm')
    d = projector(z, norm)
    require(all(d[i][j] == conjugate(d[j][i]) for i in range(8) for j in range(8)), 'Hermitian D')
    require(matrix_product(d, d) == d, 'projector idempotence')
    require(all(gaussian_dot(row, z) == ZERO for row in d), 'projector kernel')
    require(matrix_rank(d) == 7, 'complex projector rank seven')
    real_d = [[(x[0], F(0)) for x in row] for row in d]
    require(matrix_rank(real_d) == 8, 'real part has rank eight')
    values = [gaussian_dot([(F(x), F(0)) for x in row], z) for row in rows]
    maximum = max(squared(x) for x in values)
    require(maximum == expected_max, 'exact doubled-root maximum')
    candidate = literal_gram_candidate(rows, d)
    minor = [[candidate[i][j] for j in indices] for i in indices]
    require(matrix_rank(minor) == 7, 'rank-seven full candidate via nonsingular-root minor')
    require(matrix_rank([[(x[0], F(0)) for x in row] for row in minor]) == 8,
            'real candidate has rank eight')
    error_squared, entries = F(0), 0
    for i, left in enumerate(rows):
        for j, right in enumerate(rows):
            gram = (F(sum(x * y for x, y in zip(left, right, strict=True)), 8), F(0))
            error = minus(gram, candidate[i][j])
            outer = scale(times(values[i], conjugate(values[j])), F(1, 8 * norm))
            require(error == outer, 'literal full-matrix residual')
            require(candidate[i][j] == conjugate(candidate[j][i]), 'Hermitian C')
            error_squared = max(error_squared, squared(error))
            entries += 1
    require(error_squared == expected_error ** 2, 'attained exact coefficient error')
    require(maximum / (8 * norm) == expected_error < F(1, 4), 'strict real-bound separation')
    bad = projector(z, norm + 1)
    require(matrix_product(bad, bad) != bad, 'wrong-norm projector control')
    wrong_conjugation = [[minus((F(i == j), F(0)), scale(times(x, y), F(1, norm)))
                         for j, y in enumerate(z)] for i, x in enumerate(z)]
    require(any(wrong_conjugation[i][j] != conjugate(wrong_conjugation[j][i])
                for i in range(8) for j in range(8)), 'missing-conjugation Hermitian control')
    require(matrix_product(wrong_conjugation, wrong_conjugation) != wrong_conjugation,
            'missing-conjugation projector control')
    return {'norm': str(norm), 'max_doubled_root_squared': str(maximum),
            'max_entry_error': str(expected_error), 'gap_below_quarter': str(F(1, 4) - expected_error),
            'literal_residual_entries': entries, 'complex_rank': 7,
            'real_part_rank': 8, 'projector_controls': 2}


def main():
    rows = root_rows()
    indices = frame_indices(rows)
    fixtures = [
        ([(5,-5),(3,9),(5,-5),(7,0),(5,-5),(-1,-4),(-7,0),(-7,0)],
         404, 800, F(25,101)),
        ([(14,-10),(6,23),(14,-10),(17,3),(14,-10),(-3,-10),(-17,-3),(-17,-3)],
         2456, 4820, F(1205,4912)),
    ]
    results = [check_witness(rows, indices, *fixture) for fixture in fixtures]
    print('PASS_INDEPENDENT_COMPLEX_RANK_SEVEN ' + json.dumps({
        'root_lines': len(rows), 'source_sha256': SOURCE_SHA256, 'witnesses': results}, sort_keys=True))


if __name__ == '__main__':
    main()
