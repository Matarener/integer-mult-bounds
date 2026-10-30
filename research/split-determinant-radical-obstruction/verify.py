#!/usr/bin/env python3
"""Check the split-determinant counterexample and reachable controls.

Produced by Nick Petalas. Apache-2.0.
The all-field, arbitrary-length proof is in README.md. No predecessor is run.
"""

from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path


I = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
ZERO = ((0, 0, 0),) * 3
A = ((0, 1, 0), (0, 0, 1), (0, 0, 0))
B = ((0, 0, 0), (1, 0, 0), (0, -1, 0))
FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def matrix_product(left, right, q):
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(3)) % q
                       for j in range(3)) for i in range(3))


def row_product(row, matrix, q):
    return tuple(sum(row[i] * matrix[i][j] for i in range(3)) % q
                 for j in range(3))


def determinant_polynomial(matrices):
    """Expand det(X*M0+Y*M1+Z*M2) over Z, without substitutions."""
    need(len(matrices) == 3, "three coefficient matrices required")
    result = {}
    for perm in permutations(range(3)):
        inversions = sum(perm[i] > perm[j] for i in range(3)
                         for j in range(i + 1, 3))
        for choices in product(range(3), repeat=3):
            exponent = tuple(choices.count(i) for i in range(3))
            coefficient = (-1) ** inversions
            for row in range(3):
                coefficient *= matrices[choices[row]][row][perm[row]]
            result[exponent] = result.get(exponent, 0) + coefficient
    return {exponent: value for exponent, value in result.items() if value}


def check_obstruction():
    need(determinant_polynomial((I, A, B)) == {(3, 0, 0): 1},
         "new homogeneous determinant must equal X^3 over Z")
    census = []
    for q in (2, 3, 5, 7, 11):
        need(matrix_product(matrix_product(A, A, q), A, q) == ZERO,
             "A must be nilpotent")
        need(matrix_product(matrix_product(B, B, q), B, q) == ZERO,
             "B must be nilpotent")
        rows = 0
        a_rows = []
        b_rows = []
        for row in product(range(q), repeat=3):
            if row == (0, 0, 0):
                continue
            rows += 1
            for scalar in range(q):
                scaled = tuple(scalar * value % q for value in row)
                if row_product(row, A, q) == scaled:
                    a_rows.append((row, scalar))
                if row_product(row, B, q) == scaled:
                    b_rows.append((row, scalar))
        need(set(a_rows) == {((0, 0, t), 0) for t in range(1, q)},
             "A eigenrows must be precisely the third coordinate line")
        need(set(b_rows) == {((t, 0, 0), 0) for t in range(1, q)},
             "B eigenrows must be precisely the first coordinate line")
        need(not ({row for row, _ in a_rows} & {row for row, _ in b_rows}),
             "the new example must have no common left eigenrow")
        census.append({"q": q, "nonzero_rows": rows,
                       "A_eigenpairs": len(a_rows), "B_eigenpairs": len(b_rows),
                       "common_eigenrows": 0})
    return census


def ring_add(left, right):
    return tuple(a ^ b for a, b in zip(left, right, strict=True))


def ring_product(left, right):
    """Literal multiplication in F2[x,y,z]/(x,y,z)^2."""
    return (left[0] & right[0],) + tuple(
        (left[0] & right[i]) ^ (left[i] & right[0]) for i in range(1, 4))


def ring_matrix_product(left, right):
    rows = []
    for i in range(3):
        row = []
        for j in range(3):
            value = (0, 0, 0, 0)
            for k in range(3):
                value = ring_add(value, ring_product(left[i][k], right[k][j]))
            row.append(value)
        rows.append(tuple(row))
    return tuple(rows)


def ring_identity():
    return tuple(tuple((int(i == j), 0, 0, 0) for j in range(3))
                 for i in range(3))


def target_matrix(coefficient, slot):
    need(slot in (2, 3), "control uses the y or z generator")
    return tuple(tuple((0, int(i == j),
                        coefficient[i][j] % 2 if slot == 2 else 0,
                        coefficient[i][j] % 2 if slot == 3 else 0)
                       for j in range(3)) for i in range(3))


def replacement_factors(target, order):
    """Return literal legal factors I+(target_column-e_j)e_j^T."""
    factors = []
    for column in order:
        factor = tuple(tuple(target[i][j] if j == column else
                             (int(i == j), 0, 0, 0) for j in range(3))
                       for i in range(3))
        factors.append((column, factor))
    return tuple(factors)


def matrix_action(matrix, vector):
    image = []
    for row in matrix:
        value = (0, 0, 0, 0)
        for entry, coordinate in zip(row, vector, strict=True):
            value = ring_add(value, ring_product(entry, coordinate))
        image.append(value)
    return tuple(image)


def paid_action(column, factor, vector):
    """Execute v += u*(e_j^T v) without matrix multiplication."""
    old = vector[column]
    result = []
    for row in range(3):
        delta = ring_add(factor[row][column], (int(row == column), 0, 0, 0))
        result.append(ring_add(vector[row], ring_product(delta, old)))
    return tuple(result)


def check_reachable_controls():
    elements = tuple(product(range(2), repeat=4))
    comparisons = 0
    for coefficient, slot, order in ((A, 2, (0, 1, 2)), (B, 3, (2, 1, 0))):
        target = target_matrix(coefficient, slot)
        factors = replacement_factors(target, order)
        accumulated = ring_identity()
        for _, factor in factors:
            accumulated = ring_matrix_product(factor, accumulated)
        need(accumulated == target, "generator-deletion control must be reachable")
        reversed_product = ring_identity()
        for _, factor in reversed(factors):
            reversed_product = ring_matrix_product(factor, reversed_product)
        need(reversed_product != target, "chronology mutant must change the endpoint")
        for omitted in range(3):
            partial = ring_identity()
            for index, (_, factor) in enumerate(factors):
                if index != omitted:
                    partial = ring_matrix_product(factor, partial)
            need(partial != target, "every paid factor is necessary in this word")
        for vector in product(elements, repeat=3):
            result = vector
            for column, factor in factors:
                result = paid_action(column, factor, result)
            need(result == matrix_action(target, vector), "literal dirty-input action")
            comparisons += 1
    return comparisons


def check_controls():
    plus_b = ((0, 0, 0), (1, 0, 0), (0, 1, 0))
    need(determinant_polynomial((I, A, plus_b)) ==
         {(3, 0, 0): 1, (1, 1, 1): -2}, "odd-characteristic sign control")
    need(determinant_polynomial((I, A, ZERO)) == {(3, 0, 0): 1},
         "split determinant also occurs in a reachable control")
    x, y = (0, 1, 0, 0), (0, 0, 1, 0)
    need(ring_product(x, y) == (0, 0, 0, 0), "mixed radical products vanish")
    need(ring_product(x, x) == (0, 0, 0, 0), "radical squares vanish")


def receipt(census, comparisons):
    directory = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        path = directory / name
        need(path.stat().st_size <= 131072, "package file capacity exceeded")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return {"claim_type": "scoped algebraic proof with finite corroboration",
            "determinant_over_Z": "X^3", "fields": census,
            "dirty_input_action_comparisons": comparisons,
            "package_sha256": hashes}


def main():
    census = check_obstruction()
    comparisons = check_reachable_controls()
    check_controls()
    print(json.dumps(receipt(census, comparisons), sort_keys=True))
    print("PASS_SPLIT_DETERMINANT_RADICAL_OBSTRUCTION no_new_kappa")


if __name__ == "__main__":
    main()
