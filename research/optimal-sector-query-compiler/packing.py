#!/usr/bin/env python3
"""Compile exact dyadic Gaussian queries over ordinary Boolean sectors.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Sector packing follows Dugongue PR5578 T6. The Smith routine is retained
from Ali Romman PR5615 with its original header.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def need(test, message):
    if not test:
        raise ValueError(message)


def load_smith():
    path = HERE / 'vendor/capacity.py'
    need(sha256(path.read_bytes()).hexdigest()
         == '1cd82b0beab7983d955cfc1d1e562af490f90bcaad6e3ec7d07e0c5a33608834',
         'Smith source bytes')
    spec = importlib.util.spec_from_file_location('retained_smith', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.smith


smith = load_smith()


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def inverse(matrix):
    n = len(matrix)
    data = [list(map(Q, row)) + identity for row, identity in zip(matrix, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if data[i][j]), None)
        need(pivot is not None, 'Invertible Smith factor')
        data[pivot], data[j] = data[j], data[pivot]
        value = data[j][j]
        data[j] = [x / value for x in data[j]]
        for i in range(n):
            if i != j:
                value = data[i][j]
                data[i] = [x - value * y for x, y in zip(data[i], data[j])]
    return [row[n:] for row in data]


def rank_factor(matrix):
    m, n = len(matrix), len(matrix[0])
    denominator = max(x.denominator for row in matrix for x in row)
    integer = [[int(denominator * x) for x in row] for row in matrix]
    left, diagonal, right = smith(integer)
    li, ri = inverse(left), inverse(right)
    need(all(x.denominator == 1 for z in (li, ri) for row in z for x in row),
         'Unimodular Smith factors')
    rank = sum(diagonal[i][i] != 0 for i in range(min(m, n)))
    u = [[li[i][k] * Q(diagonal[k][k], denominator) for k in range(rank)]
         for i in range(m)]
    v = ri[:rank]
    need(all(sum(u[i][k] * v[k][j] for k in range(rank)) == matrix[i][j]
             for i in range(m) for j in range(n)), 'Exact factorization')
    return u, v, rank


def sign(mask, sector):
    return -1 if (mask & sector).bit_count() % 2 else 1


def validate(even, odd):
    count = len(even)
    need(count >= 2 and count & (count - 1) == 0 and len(odd) == count,
         'Power-of-two sector count, at least two')
    m, n = len(even[0]), len(even[0][0]) if even[0] else 0
    need(m > 0 and n > 0, 'Nonempty matrix')
    result = []
    for parts in (even, odd):
        converted = []
        for matrix in parts:
            need(len(matrix) == m and all(len(row) == n for row in matrix), 'Matrix shape')
            values = [[Q(x) for x in row] for row in matrix]
            need(all(x.denominator & (x.denominator - 1) == 0
                     for row in values for x in row), 'Dyadic coefficients')
            converted.append(values)
        result.append(converted)
    return result[0], result[1], count, m, n


def compile_map(even, odd):
    """Return a word for sum_mask (A_mask + B_mask Q) J_mask."""
    even, odd, count, m, n = validate(even, odd)
    factors = []
    for sector in range(count):
        matrix = [[sum(sign(mask, sector) * odd[mask][i][j]
                       for mask in range(count)) for j in range(n)] for i in range(m)]
        factors.append(rank_factor(matrix))
    queries = max(r for _, _, r in factors)
    u_parts, v_parts = [], []
    for mask in range(count):
        u_parts.append([[sum(sign(mask, sector) *
                            (factors[sector][0][i][k] if k < factors[sector][2] else 0)
                            for sector in range(count)) / Q(count)
                        for k in range(queries)] for i in range(m)])
        v_parts.append([[sum(sign(mask, sector) *
                            (factors[sector][1][k][j] if k < factors[sector][2] else 0)
                            for sector in range(count)) / Q(count)
                        for j in range(n)] for k in range(queries)])
    outputs = list(range(n, n + m))
    work = list(range(n + m, n + m + queries))
    program = [['CLEAR', r] for r in outputs + work]

    def add_matrix(parts, destinations, sources):
        for mask, matrix in enumerate(parts):
            for i, row in enumerate(matrix):
                for j, coefficient in enumerate(row):
                    if coefficient:
                        program.append(['ADD', destinations[i], sources[j], str(coefficient), mask])

    add_matrix(even, outputs, list(range(n)))
    add_matrix(v_parts, work, list(range(n)))
    program.extend(['QUERY', r] for r in work)
    add_matrix(u_parts, outputs, work)
    program.extend(['CLEAR', r] for r in work)
    coefficients = [Q(event[3]) for event in program if event[0] == 'ADD']
    need(all(x.denominator & (x.denominator - 1) == 0 for x in coefficients),
         'Emitted dyadic coefficients')
    return {'schema': 'boolean-sector-query-word/v1', 'generators': count.bit_length() - 1,
            'input_fields': n, 'output_fields': m, 'query_count': queries,
            'sector_ranks': [r for _, _, r in factors],
            'owned_fields_including_outputs': m + queries,
            'ordinary_adds': len(coefficients), 'ordinary_clears': m + 2 * queries,
            'max_coefficient_numerator_bits': max((abs(x.numerator).bit_length() for x in coefficients), default=0),
            'max_coefficient_denominator_bits': max((x.denominator.bit_length() - 1 for x in coefficients), default=0),
            'output_registers': outputs, 'work_registers': work, 'program': program}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text())
    word = compile_map(source['even'], source['odd'])
    with args.output.open('x') as stream:
        json.dump(word, stream, indent=2)
        stream.write('\n')
    print('EMITTED_SECTOR_QUERY_WORD', word['query_count'], word['ordinary_adds'])


if __name__ == '__main__':
    main()
