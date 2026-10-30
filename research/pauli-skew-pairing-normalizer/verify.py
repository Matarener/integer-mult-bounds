#!/usr/bin/env python3
"""Exact Pauli pairing normalization. Produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(size):
    need(type(size) is int and 1 <= size <= 24, "Matrix capacity")
    return [[Q(i == j) for j in range(size)] for i in range(size)]


def multiply(left, right):
    size = len(left)
    need(1 <= size <= 24 and len(right) == size, "Matrix size")
    need(all(len(row) == size for row in left + right), "Square matrices")
    result = [[Q(0) for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for k in range(size):
            if left[i][k]:
                for j in range(size):
                    result[i][j] += left[i][k] * right[k][j]
    return result


def apply(matrix, vector):
    need(len(matrix) == len(vector), "Vector size")
    return [sum(a * b for a, b in zip(row, vector, strict=True))
            for row in matrix]


def paulis(width, a, b, sx, sz):
    need(type(width) is int and 1 <= width <= 3, "Address width capacity")
    size = 1 << width
    need(0 < a < size and 0 < b < size and (a & b).bit_count() % 2,
         "Anticommuting labels")
    need(sx in (-1, 1) and sz in (-1, 1), "Pauli signs")
    x = [[Q(sx * (i == (j ^ a))) for j in range(size)] for i in range(size)]
    z = [[Q(sz * (-1) ** ((b & i).bit_count() % 2) * (i == j))
          for j in range(size)] for i in range(size)]
    return x, z


def negate(matrix):
    return [[-value for value in row] for row in matrix]


def block_matrix(blocks):
    need(len(blocks) == 3 and all(len(row) == 3 for row in blocks),
         "Three-bank block layout")
    size = len(blocks[0][0])
    need(1 <= size <= 8, "Block capacity")
    return [[blocks[i // size][j // size][i % size][j % size]
             for j in range(3 * size)] for i in range(3 * size)]


def pairing_and_inverse(x, z):
    size = len(x)
    unit = identity(size)
    zero = [[Q(0) for _ in range(size)] for _ in range(size)]
    j = multiply(x, z)
    pairing = block_matrix([[zero, unit, x],
                            [negate(unit), zero, z],
                            [negate(x), negate(z), zero]])
    numerator = block_matrix([[negate(j), negate(unit), negate(x)],
                              [unit, negate(j), negate(z)],
                              [x, z, j]])
    inverse = [[value / 2 for value in row] for row in numerator]
    return pairing, inverse


def normalize(vector, x, z, fault=None):
    """Four binary gates, one halving, then invertible bank relabelings."""
    size = len(x)
    need(len(vector) == 3 * size, "Three input banks")
    banks = [list(vector[i * size:(i + 1) * size]) for i in range(3)]
    za = apply(z, banks[0])
    banks[2] = [a + b for a, b in zip(banks[2], za, strict=True)]
    xb = apply(x, banks[1])
    if fault != "omit_second_add":
        banks[2] = [a - b for a, b in zip(banks[2], xb, strict=True)]
    if fault == "wrong_order":
        banks[2] = apply(z, apply(x, banks[2]))
    else:
        banks[2] = apply(x, apply(z, banks[2]))
    if fault != "omit_half":
        banks[2] = [value / 2 for value in banks[2]]
    xc = apply(x, banks[2])
    banks[0] = [a - b for a, b in zip(banks[0], xc, strict=True)]
    zc = apply(z, banks[2])
    banks[1] = [a - b for a, b in zip(banks[1], zc, strict=True)]
    if fault != "omit_swap":
        banks[0], banks[1] = banks[1], banks[0]
    banks[0] = [-value for value in banks[0]]
    return [value for bank in banks for value in bank]


def check_case(width, a, b, sx, sz):
    x, z = paulis(width, a, b, sx, sz)
    size = len(x)
    unit = identity(size)
    need(multiply(x, x) == multiply(z, z) == unit, "Pauli involutions")
    need(multiply(x, z) == negate(multiply(z, x)), "Exact anticommutation")
    pairing, inverse = pairing_and_inverse(x, z)
    need(multiply(pairing, inverse) == identity(3 * size), "Right inverse")
    need(multiply(inverse, pairing) == identity(3 * size), "Left inverse")
    for column in range(3 * size):
        basis = [Q(i == column) for i in range(3 * size)]
        need(normalize(basis, x, z) == apply(inverse, basis),
             "Literal circuit equals the separate closed inverse")
        need(normalize(apply(pairing, basis), x, z) == basis,
             "All-input forward/inverse composition")
    need(all(any(inverse[i * size + r][j * size + c]
                 for r in range(size) for c in range(size))
             for i in range(3) for j in range(3)), "Nine nonzero blocks")
    need(any(value.denominator == 2 for row in inverse for value in row),
         "An actual one-bit denominator is necessary")
    return 3 * size


def support_enumeration(bank_count):
    need(type(bank_count) is int and 3 <= bank_count <= 6, "Bank capacity")
    states = {tuple(sorted([1, 2, 4] + [0] * (bank_count - 3)))}
    trace = []
    for depth in range(4):
        maximum = max(state.count(7) for state in states)
        need(maximum <= max(0, depth - 1), "Three-gate support lower bound")
        trace.append({"adds": depth, "states": len(states),
                      "max_full_support_banks": maximum})
        if depth < 3:
            following = set()
            for state in states:
                for destination in range(bank_count):
                    for source in range(bank_count):
                        if source != destination:
                            changed = list(state)
                            changed[destination] |= changed[source]
                            following.add(tuple(sorted(changed)))
            need(len(following) <= 8 ** bank_count, "Support state capacity")
            states = following
    return trace


def determinant3(a, b):
    matrix = [[0, 1, a], [-1, 0, b], [-a, -b, 0]]
    return sum(matrix[0][i]
               * (matrix[1][(i + 1) % 3] * matrix[2][(i + 2) % 3]
                  - matrix[1][(i + 2) % 3] * matrix[2][(i + 1) % 3])
               for i in range(3))


def rejecting_controls():
    rejected = []
    for label, arguments in [
        ("zero label", (1, 0, 1, 1, 1)),
        ("commuting labels", (2, 1, 2, 1, 1)),
        ("bad sign", (1, 1, 1, 0, 1)),
        ("excess address width", (4, 1, 1, 1, 1)),
    ]:
        try:
            paulis(*arguments)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("Accepted invalid Pauli boundary: " + label)
    x, z = paulis(1, 1, 1, 1, 1)
    _, inverse = pairing_and_inverse(x, z)
    for fault in ("omit_second_add", "wrong_order", "omit_half", "omit_swap"):
        differences = 0
        for column in range(6):
            basis = [Q(i == column) for i in range(6)]
            differences += normalize(basis, x, z, fault) != apply(inverse, basis)
        need(differences > 0, "Mutation must fail: " + fault)
        rejected.append(fault)
    try:
        identity(25)
    except ValueError:
        rejected.append("excess matrix size")
    else:
        raise ValueError("Accepted excess matrix size")
    return rejected


def receipt():
    cases, columns = 0, 0
    for width in range(1, 4):
        size = 1 << width
        for a in range(1, size):
            for b in range(1, size):
                if (a & b).bit_count() % 2:
                    for sx, sz in product((-1, 1), repeat=2):
                        columns += check_case(width, a, b, sx, sz)
                        cases += 1
    scalar_cases = 0
    for a in range(-4, 5):
        for b in range(-4, 5):
            need(determinant3(a, b) == 0, "Commuting scalar skew fixture")
            scalar_cases += 1
    need((cases, columns, scalar_cases) == (140, 3000, 81), "Complete fixture domain")
    files = sorted(path for path in Path(__file__).resolve().parent.iterdir()
                   if path.is_file())
    need(5 <= len(files) <= 8, "Package file capacity")
    return {"status": "PASS_PAULI_SKEW_PAIRING_NORMALIZER",
            "pauli_cases": cases, "basis_columns": columns,
            "scalar_cases": scalar_cases,
            "support_traces": {str(n): support_enumeration(n) for n in range(3, 7)},
            "rejected_controls": rejecting_controls(),
            "optimal_cross_bank_adds": 4, "optimal_bank_halvings": 1,
            "files_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in files}}


def main():
    need(len(sys.argv) == 1, "No command-line arguments")
    print(json.dumps(receipt(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
