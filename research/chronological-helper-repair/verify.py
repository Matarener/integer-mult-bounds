#!/usr/bin/env python3
"""Exact finite corroboration; the all-field proof is in PROOF.md.

Produced by Nick Petalas. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

MAX_DIM = 6
MAX_SIDE = 2 * MAX_DIM


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(value, prime):
    return Fraction(value) if prime == 0 else value % prime


def identity(size):
    require(1 <= size <= MAX_SIDE, "identity size")
    return [[int(i == j) for j in range(size)] for i in range(size)]


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left, right, prime):
    require(1 <= len(left) <= MAX_SIDE, "left size")
    require(len(left[0]) == len(right), "product shape")
    require(1 <= len(right[0]) <= MAX_SIDE, "right size")
    columns = transpose(right)
    return [[scalar(sum(x * y for x, y in zip(row, col, strict=True)), prime)
             for col in columns] for row in left]


def combine(left, right, prime, sign=1):
    require(len(left) == len(right), "sum shape")
    return [[scalar(x + sign * y, prime) for x, y in zip(a, b, strict=True)]
            for a, b in zip(left, right, strict=True)]


def rref(matrix, prime):
    require(1 <= len(matrix) <= MAX_SIDE, "row count")
    width = len(matrix[0])
    require(1 <= width <= MAX_SIDE, "column count")
    require(all(len(row) == width for row in matrix), "ragged matrix")
    result = [[scalar(x, prime) for x in row] for row in matrix]
    pivots = []
    for col in range(width):
        choices = [i for i in range(len(pivots), len(result)) if result[i][col]]
        if not choices:
            continue
        pivot = len(pivots)
        other = choices[0]
        result[pivot], result[other] = result[other], result[pivot]
        value = result[pivot][col]
        reciprocal = 1 / value if prime == 0 else pow(value, -1, prime)
        result[pivot] = [scalar(x * reciprocal, prime) for x in result[pivot]]
        for row in range(len(result)):
            if row != pivot:
                value = result[row][col]
                result[row] = [scalar(x - value * y, prime) for x, y in
                               zip(result[row], result[pivot], strict=True)]
        pivots.append(col)
        if len(pivots) == len(result):
            break
    return result, pivots


def rank(matrix, prime):
    _, pivots = rref(matrix, prime)
    return len(pivots)


def inverse(matrix, prime):
    size = len(matrix)
    require(size <= MAX_DIM and all(len(row) == size for row in matrix), "inverse shape")
    augmented = [row + unit for row, unit in zip(matrix, identity(size), strict=True)]
    reduced, pivots = rref(augmented, prime)
    require(pivots == list(range(size)), "singular matrix")
    result = [row[size:] for row in reduced]
    require(multiply(matrix, result, prime) == identity(size), "inverse residual")
    return result


def validate_case(c, k, prime):
    require(prime in (0, 2, 3, 5, 7), "field")
    size = len(c)
    require(1 <= size <= MAX_DIM and len(k) == size, "case size")
    require(all(len(row) == size for row in c + k), "case shape")
    require(all(type(x) in (int, Fraction) for row in c + k for x in row), "coefficient type")
    require(all(abs(Fraction(x).numerator).bit_length() <= 32 and
                Fraction(x).denominator.bit_length() <= 32 for row in c + k for x in row),
            "coefficient bound")
    require(prime == 0 or all(type(x) is int for row in c + k for x in row),
            "finite-field coefficients")
    require(all(scalar(k[i][i], prime) == 1 for i in range(size)), "unit diagonal")
    return inverse(c, prime)


def direct_replay(c, d, prime):
    """Execute changing live charts and literal extract/replace events."""
    size = len(c)
    state = [row + [0] * size for row in identity(size)]
    prefix = identity(size)
    early = []
    for cut in range(size):
        segment = identity(size)
        if size > 1:
            segment[cut][(cut + 1) % size] = cut + 1
        prefix = multiply(segment, prefix, prime)
        state = multiply(segment, state, prime)
        a = multiply([c[cut]], inverse(prefix, prime), prime)
        b = multiply(prefix, [[row[cut]] for row in d], prime)
        require(multiply(a, b, prime) == [[1]], "literal cut normalization")
        returned = multiply(a, state, prime)[0]
        incoming = [int(j == size + cut) for j in range(2 * size)]
        delta = [scalar(x - y, prime) for x, y in zip(incoming, returned, strict=True)]
        for row in range(size):
            state[row] = [scalar(x + b[row][0] * y, prime)
                          for x, y in zip(state[row], delta, strict=True)]
        early.append(returned)
    return early, multiply(inverse(prefix, prime), state, prime)


def rank_one_factors(matrix, prime):
    """Return a minimal outer-product decomposition, with a residual check."""
    _, columns = rref(matrix, prime)
    if not columns:
        return []
    basis = [[row[j] for j in columns] for row in matrix]
    _, rows = rref(transpose(basis), prime)
    minor = [basis[i] for i in rows]
    weights = multiply(inverse(minor, prime), [matrix[i] for i in rows], prime)
    factors = list(zip(transpose(basis), weights, strict=True))
    reconstructed = [[0] * len(matrix) for _ in matrix]
    for column, row in factors:
        term = [[scalar(x * y, prime) for y in row] for x in column]
        reconstructed = combine(reconstructed, term, prime)
    require(reconstructed == matrix, "rank factorization residual")
    return factors


def check_case(c, k, prime):
    cinv = validate_case(c, k, prime)
    size = len(c)
    lower = [[scalar(k[i][j], prime) if j < i else 0
              for j in range(size)] for i in range(size)]
    upper = [[scalar(k[i][j], prime) if i < j else 0
              for j in range(size)] for i in range(size)]
    d = multiply(cinv, k, prime)
    early, final = direct_replay(c, d, prime)
    a = inverse(combine(identity(size), lower, prime), prime)
    expected_early = multiply(a, [x + y for x, y in zip(c, lower, strict=True)], prime)
    incoming = [[0] * size + row for row in identity(size)]
    expected_final = multiply(cinv, combine(
        multiply(combine(identity(size), upper, prime), incoming, prime),
        multiply(upper, early, prime), prime, -1), prime)
    require(early == expected_early and final == expected_final, "causal formula")
    require(rank([row[size:] for row in early], prime) == rank(lower, prime),
            "early new-input rank")
    require(rank([row[:size] for row in final], prime) == rank(upper, prime),
            "final old-input rank")
    require(rank(early + final, prime) == 2 * size, "complete reversible endpoint")
    if rank(lower, prime) == 0:
        require(early == [row + [0] * size for row in c], "independent early targets")
        factors = rank_one_factors(upper, prime)
        for column, row in factors:
            delivered = multiply([row], early, prime)[0]
            vector = multiply(cinv, [[x] for x in column], prime)
            correction = [[scalar(x[0] * y, prime) for y in delivered] for x in vector]
            final = combine(final, correction, prime)
        normalizer = multiply(inverse(combine(identity(size), upper, prime), prime), c, prime)
        require(multiply(normalizer, final, prime) == incoming, "attaining repair")
        require(len(factors) == rank(upper, prime), "repair rank units")
    return int(rank(lower, prime) == 0)


def unit_diagonal_cases(size, prime):
    positions = [(i, j) for i in range(size) for j in range(size) if i != j]
    for values in product(range(prime), repeat=len(positions)):
        matrix = identity(size)
        for (i, j), value in zip(positions, values, strict=True):
            matrix[i][j] = value
        yield matrix


def finite_checks():
    counts = {"binary_basis_pairings": 0, "ternary_pairings": 0,
              "quinary_pairings": 0, "independent_early_repairs": 0}
    for entries in product(range(2), repeat=9):
        c = [list(entries[3 * i:3 * i + 3]) for i in range(3)]
        if rank(c, 2) != 3:
            continue
        for k in unit_diagonal_cases(3, 2):
            counts["independent_early_repairs"] += check_case(c, k, 2)
            counts["binary_basis_pairings"] += 1
    for prime, size, label in ((3, 3, "ternary_pairings"), (5, 2, "quinary_pairings")):
        for k in unit_diagonal_cases(size, prime):
            counts["independent_early_repairs"] += check_case(identity(size), k, prime)
            counts[label] += 1
    return counts


def rational_checks():
    cases = repairs = 0
    for size in range(1, MAX_DIM + 1):
        c = identity(size)
        for i in range(size - 1):
            c[i][i + 1] = Fraction(i + 1, 2)
        for seed in range(12):
            k = [[Fraction(1) if i == j else Fraction(
                ((i + 2) * (j + 3) + seed) % 7 - 3, 2 ** (seed % 3))
                  for j in range(size)] for i in range(size)]
            if seed % 2 == 0:
                k = [[0 if j < i else x for j, x in enumerate(row)]
                     for i, row in enumerate(k)]
            repairs += check_case(c, k, 0)
            cases += 1
    return {"rational_cases": cases, "rational_repairs": repairs}


def sharp_family_checks():
    cases = 0
    for prime in (0, 2, 3, 5, 7):
        for size in range(2, MAX_DIM + 1):
            k = identity(size)
            for i in range(size - 1):
                k[i][i + 1] = 1
            require(check_case(identity(size), k, prime) == 1, "sharp family")
            _, final = direct_replay(identity(size), k, prime)
            require(rank([row[:size] for row in final], prime) == size - 1,
                    "sharp spill k-1")
            cases += 1
    target = [[0, 1, 0], [0, 0, 1], [0, 0, 0]]
    rejected = 0
    for v in product(range(2), repeat=3):
        for w in product(range(2), repeat=3):
            require([[x * y for y in w] for x in v] != target, "one-unit false repair")
            rejected += 1
    return {"sharp_family_cases": cases, "rank_one_repairs_rejected": rejected}


def rejection_checks():
    invalid = [([], [], 0), ([[1]], [[0]], 0), ([[0]], [[1]], 0),
               ([[1]], [[1]], 4), ([[1, 0]], [[1]], 0),
               ([[1]], [[1], [1]], 0), ([[1]], [[Fraction(1)]], 2),
               ([[1]], [[2 ** 40]], 0)]
    for c, k, prime in invalid:
        try:
            validate_case(c, k, prime)
        except ValueError:
            continue
        raise ValueError("invalid fixture accepted")
    c = identity(3)
    k = [[1, 2, 0], [3, 1, 1], [1, 4, 1]]
    early, final = direct_replay(c, k, 0)
    old_only = [row + [0] * 3 for row in c]
    incoming = [[0] * 3 + row for row in c]
    require(early != old_only, "lower spill control")
    require(final != incoming, "upper spill control")
    reversed_early, reversed_final = direct_replay(c, transpose(k), 0)
    require(early != reversed_early and final != reversed_final, "time order control")
    require(direct_replay(c, c, 0) == (old_only, incoming), "biorthogonal control")
    return {"invalid_cases_rejected": len(invalid), "semantic_controls": 4}


def main():
    counts = {}
    for report in (finite_checks(), rational_checks(), sharp_family_checks(), rejection_checks()):
        counts.update(report)
    package = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(path.stat().st_size <= 1024 * 1024, "receipt file size")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    print("PASS_CHRONOLOGICAL_HELPER_REPAIR " + json.dumps(counts, sort_keys=True))
    print(json.dumps({"schema": "chronological-helper-repair/v1", "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
