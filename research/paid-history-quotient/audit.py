#!/usr/bin/env python3
"""Compute an exact lower bound for a finite paid-history interface.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path


def scalar(value):
    if type(value) not in (int, str):
        raise ValueError("use integers or rational strings")
    return Q(value)


def matrix(value, rows, columns):
    if not isinstance(value, list) or len(value) != rows:
        raise ValueError("invalid row count")
    if any(not isinstance(row, list) or len(row) != columns for row in value):
        raise ValueError("invalid column count")
    return tuple(tuple(scalar(x) for x in row) for row in value)


def identity(d):
    return tuple(tuple(Q(i == j) for j in range(d)) for i in range(d))


def multiply(a, b):
    return tuple(tuple(sum(x * y for x, y in zip(row, col))
                       for col in zip(*b)) for row in a)


def flat(a):
    return tuple(x for row in a for x in row)


class Span:
    def __init__(self):
        self.rows = {}

    def add(self, vector):
        row = list(vector)
        for pivot, basis in sorted(self.rows.items()):
            c = row[pivot]
            row = [x - c * y for x, y in zip(row, basis)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is None:
            return False
        c = row[pivot]
        self.rows[pivot] = tuple(x / c for x in row)
        return True

    def __len__(self):
        return len(self.rows)


def algebra(d, generators):
    basis, span = [identity(d)], Span()
    span.add(flat(basis[0]))
    index = 0
    while index < len(basis):
        for generator in generators:
            product = multiply(generator, basis[index])
            if span.add(flat(product)):
                basis.append(product)
        index += 1
    return basis


def audit(data):
    d = data['dimension']
    if type(d) is not int or d < 1:
        raise ValueError("dimension must be a positive integer")
    names = data['inputs']
    if (not isinstance(names, list) or not names
            or any(not isinstance(x, str) or not x for x in names)
            or len(set(names)) != len(names)):
        raise ValueError("input versions must have distinct nonempty names")
    generators = [matrix(x, d, d) for x in data['ordinary_generators']]
    initial = [matrix(x, d, d * len(names)) for x in data['initial']]
    targets = [matrix(x, d, d * len(names)) for x in data['targets']]
    ordinary = algebra(d, generators)
    span = Span()
    for row in initial:
        for a in ordinary:
            span.add(flat(multiply(a, row)))
    initial_rank = len(span)
    for row in targets:
        for a in ordinary:
            span.add(flat(multiply(a, row)))
    delta = len(span) - initial_rank
    return {'ordinary_dimension': len(ordinary), 'initial_dimension': initial_rank,
            'joint_dimension': len(span), 'target_quotient_dimension': delta,
            'additional_return_lower_bound': (delta + len(ordinary) - 1) // len(ordinary),
            'targets_in_initial_ordinary_closure': delta == 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        result = audit(json.loads(args.input.read_text(encoding='utf-8')))
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
