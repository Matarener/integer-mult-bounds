#!/usr/bin/env python3
"""Deterministic discovery; certificate replay never imports this module."""
import argparse
import itertools
import json
from pathlib import Path
from algebra import check_source, equation, gap_problem, require, rank

PACKAGE = Path(__file__).resolve().parent


def contradiction(columns, target):
    basis = {}
    for row in range(27 * 64):
        lhs, rhs = equation(columns, target, row)
        proof = 1 << row
        while lhs:
            pivot = lhs.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = lhs, rhs, proof
                break
            a, b, p = basis[pivot]
            lhs ^= a
            rhs ^= b
            proof ^= p
        if lhs == 0 and rhs:
            return [i for i in range(27 * 64) if proof >> i & 1]
    raise ValueError('Unexpected feasible gap: revise the claim')


def solve(columns, target):
    basis = {}
    for j, lhs in enumerate(columns):
        witness = 1 << j
        while lhs:
            pivot = lhs.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = lhs, witness
                break
            a, b = basis[pivot]
            lhs ^= a
            witness ^= b
    witness = 0
    while target:
        pivot = target.bit_length() - 1
        require(pivot in basis, 'Positive control is infeasible')
        a, b = basis[pivot]
        target ^= a
        witness ^= b
    return witness


def rectangular_multiply(a, b):
    return [__import__('functools').reduce(int.__xor__,
            (v for j,v in enumerate(b) if row >> j & 1), 0) for row in a]


def inverse4(rows):
    augmented = [v | (1 << (4+i)) for i,v in enumerate(rows)]
    for j in range(4):
        pivot = next((i for i in range(j,4) if augmented[i] >> j & 1), None)
        if pivot is None:
            return None
        augmented[j], augmented[pivot] = augmented[pivot], augmented[j]
        for i in range(4):
            if i != j and augmented[i] >> j & 1:
                augmented[i] ^= augmented[j]
    return [row >> 4 for row in augmented]


def decompose(matrix):
    # Full-rank factorization M=UV, followed by a zero-diagonal VU basis.
    independent = []
    for j in range(8):
        col = sum(((row >> j) & 1) << i for i,row in enumerate(matrix))
        if rank(independent+[col]) > len(independent):
            independent.append(col)
    require(len(independent) == 4, 'Expected rank-four burst')
    u = [sum(((col >> i) & 1) << j for j,col in enumerate(independent)) for i in range(8)]
    combinations = {}
    for mask in range(16):
        col = 0
        for j,v in enumerate(independent):
            if mask >> j & 1:
                col ^= v
        combinations[col] = mask
    coordinates = [combinations[sum(((row >> j)&1)<<i for i,row in enumerate(matrix))] for j in range(8)]
    v = [sum(((c >> i)&1)<<j for j,c in enumerate(coordinates)) for i in range(4)]
    # Seed 26 chooses a reproducible search order; acceptance uses only identities.
    import random
    row_order = list(range(1,16))
    random.Random(26).shuffle(row_order)
    for basis in itertools.permutations(row_order,4):
        inverse = inverse4(basis)
        if inverse is None:
            continue
        left = rectangular_multiply(u,basis)
        right = rectangular_multiply(inverse,v)
        components = [[right[k] if row >> k & 1 else 0 for row in left] for k in range(4)]
        if all(sum((m[i] >> i)&1 for i in range(8)) % 2 == 0 for m in components):
            return components
    raise ValueError('No rank-one square-zero decomposition found')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    calls = check_source(json.loads((PACKAGE/'SOURCE-WORD.json').read_text()))
    records = []
    for order in itertools.permutations(range(6)):
        for gap in range(7):
            columns, target = gap_problem(calls, order, gap)
            records.append({'order': order, 'gap': gap,
                            'xor_rows': contradiction(columns, target)})
    order = [1, 3, 2, 4, 0, 5]
    gaps = [2, 4]
    c0, target = gap_problem(calls, order, gaps[0])
    c1, _ = gap_problem(calls, order, gaps[1])
    solution = solve(c0+c1, target)
    matrices = [[(solution >> (64*g+8*i)) & 255 for i in range(8)] for g in range(2)]
    payload = {'schema': 1, 'records': records,
               'two_burst': {'order': order, 'gaps': gaps, 'matrices': matrices,
                             'rank_one_queries': [decompose(m) for m in matrices]}}
    args.output.write_text(json.dumps(payload, separators=(',', ':'))+'\n')
    print('GENERATED', len(records), 'contradictions')


if __name__ == '__main__':
    main()
