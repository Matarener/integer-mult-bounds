#!/usr/bin/env python3
"""Independent rational corroboration of the eight-column rank obstruction.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
No primary or predecessor executable code is imported.
"""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return sum((a * b for a, b in zip(x, y, strict=True)), F(0))


def transpose(matrix):
    return [list(column) for column in zip(*matrix, strict=True)]


def multiply(a, b):
    columns = transpose(b)
    return [[dot(row, column) for column in columns] for row in a]


def rank(matrix):
    a = [list(map(F, row)) for row in matrix]
    pivot = 0
    for column in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][column]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        denominator = a[pivot][column]
        a[pivot] = [value / denominator for value in a[pivot]]
        for row in range(pivot + 1, len(a)):
            scale = a[row][column]
            if scale:
                a[row] = [x - scale * y for x, y in zip(a[row], a[pivot], strict=True)]
        pivot += 1
        if pivot == min(len(a), len(a[0])):
            break
    return pivot


def roots(path):
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() ==
         '9ddfcf087912e02c46722d5a82eea5f1221a4a33d5037a0d90d392dfcd3c06d4',
         'pinned omitted-root source bytes')
    data = json.loads(raw)
    omitted = {tuple(F(1 if c == '+' else -1, 2) for c in s) for s in data['signs']}
    omitted = {q if q[0] > 0 else tuple(-x for x in q) for q in omitted}
    need(len(omitted) == 16, 'sixteen distinct omitted lines')
    shell = {tuple(F(x, 2) for x in (1, *tail))
             for tail in itertools.product((1, -1), repeat=7) if tail.count(-1) % 2}
    need(omitted <= shell, 'omitted parity and coordinates')
    ordinary = []
    for i, j in itertools.combinations(range(8), 2):
        for sign in (1, -1):
            row = [F(0)] * 8
            row[i], row[j] = F(1), F(sign)
            ordinary.append(tuple(row))
    retained = ordinary + sorted(shell - omitted)
    need(len(retained) == 104, '104 roots')
    return retained, sorted(omitted)


def frame_indices(retained):
    indices = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            row = [F(0)] * 8
            row[i], row[i + 1] = F(1), F(sign)
            indices.append(retained.index(tuple(row)))
    return indices


def vector_checks(retained, frame):
    vectors = [[F(((k + 3) * (i + 5) ** 2) % 29 - 14, (i + k) % 5 + 1)
                for i in range(8)] for k in range(137)]
    vectors += [[F(int(i % 2 == parity)) for i in range(8)] for parity in (0, 1)]
    vectors += [[F(int(i == j)) for i in range(8)] for j in range(8)]
    tight = 0
    for z in vectors:
        a = [dot(row, z) / 2 for row in frame]
        need([dot(column, a) for column in transpose(frame)] == z, 'frame inverse')
        ordered = sorted(map(abs, z), reverse=True)
        h = sum(ordered[:2])
        mass = sum(map(abs, a))
        paired = sum(max(abs(z[i]), abs(z[i + 1])) for i in range(0, 8, 2))
        need(mass == paired and mass <= sum(ordered[:4]) <= 2 * h, 'real pair norm bound')
        need(max(abs(dot(r, z)) for r in retained[:56]) == h, 'D8 support function')
        # A second, unrelated decomposition also bounds the D8 atomic mass.
        layer_mass = ordered[0] + sum(ordered[2:]) / 2
        need(layer_mass <= 2 * h, 'layer decomposition bound')
        tight += int(mass == 2 * h)
    return len(vectors), tight


def candidate(retained, indices, target, d, left=None, right=None):
    left = retained if left is None else left
    right = retained if right is None else right
    c = [[x / 2 for x in row] for row in multiply(multiply(left, d), transpose(right))]
    minor = [[c[i][j] for j in indices] for i in indices]
    need(rank(d) == 7 and rank(minor) == 7, 'rank-seven factor and witness minor')
    error = max(abs(x - y) for row, other in zip(target, c, strict=True)
                for x, y in zip(row, other, strict=True))
    need(error >= F(1, 4), 'rank-seven error floor')
    return error, c


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--missing', type=Path)
    args = parser.parse_args()
    source = args.missing or Path(__file__).resolve().parents[1] / 'p104-contractive-gram-deflation/MISSING.json'
    r, omitted = roots(source)
    j = frame_indices(r)
    u = [r[i] for i in j]
    need(multiply(u, transpose(u)) == [[F(2 * (i == k)) for k in range(8)] for i in range(8)], 'orthogonal frame')
    count, tight = vector_checks(r, u)
    target = [[x / 2 for x in row] for row in multiply(r, transpose(r))]
    for q in omitted:
        d = [[F(i == k) - q[i] * q[k] / 2 for k in range(8)] for i in range(8)]
        need(multiply(d, d) == d, 'projector identity')
        error, unused = candidate(r, j, target, d)
        need(error == F(1, 4), 'attaining exact quarter')
    q = omitted[0]
    w = [q[0], -q[1], *([F(0)] * 6)]
    d = [[F(i == k) - q[i] * (q[k] + w[k]) / 2 for k in range(8)] for i in range(8)]
    need(d != transpose(d) and multiply(d, d) == d, 'oblique projector')
    oblique, unused = candidate(r, j, target, d)
    d = [[F(i == k) - q[i] * q[k] / 2 for k in range(8)] for i in range(8)]
    outside = next(i for i in range(len(r)) if i not in j)
    left, right = [list(row) for row in r], [list(row) for row in r]
    left[outside][0] += 1
    right[outside][1] -= 1
    unrestricted, c = candidate(r, j, target, d, left, right)
    recovered = multiply(multiply(transpose(u), [[c[i][k] for k in j] for i in j]), u)
    recovered = [[x / 2 for x in row] for row in recovered]
    carrier = [[x / 2 for x in row] for row in multiply(multiply(r, recovered), transpose(r))]
    need(c != carrier, 'candidate outside fixed carrier factorization')
    print('PASS_INDEPENDENT_RANK_SEVEN_ERROR ' + json.dumps({
        'rational_vectors': count, 'sharp_norm_vectors': tight,
        'attaining_projectors': len(omitted), 'literal_matrix_entries': (len(omitted) + 2) * len(r) ** 2,
        'oblique_error': str(oblique), 'outside_carrier_error': str(unrestricted)}, sort_keys=True))


if __name__ == '__main__':
    main()
