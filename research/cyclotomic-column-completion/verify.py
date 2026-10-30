#!/usr/bin/env python3
"""Exact finite corroboration of one-column cyclotomic completion.

Produced by Nick Petalas. Apache-2.0. No predecessor code is imported.
"""

import hashlib
import itertools
import json
from pathlib import Path


MAX_ORDER = 30
MAX_ROWS = 16
PACKAGE_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def divide_exact(numerator, denominator):
    """Monic integer polynomial division, coefficients in ascending order."""
    work = list(numerator)
    degree = len(denominator) - 1
    quotient = [0] * max(1, len(work) - degree)
    for top in range(len(work) - 1, degree - 1, -1):
        coefficient = work[top]
        quotient[top - degree] = coefficient
        for j in range(degree + 1):
            work[top - degree + j] -= coefficient * denominator[j]
    require(not any(work), "inexact polynomial division")
    return tuple(quotient)


def cyclotomics(limit):
    require(2 <= limit <= MAX_ORDER, "cyclotomic order outside capacity")
    polynomials = [()] * (limit + 1)
    for order in range(1, limit + 1):
        polynomial = (-1,) + (0,) * (order - 1) + (1,)
        for divisor in range(1, order):
            if order % divisor == 0:
                polynomial = divide_exact(polynomial, polynomials[divisor])
        polynomials[order] = polynomial
    return tuple(polynomials)


def roots(order):
    polynomial = cyclotomics(order)[order]
    degree = len(polynomial) - 1
    powers = []
    current = (1,) + (0,) * (degree - 1)
    for _ in range(order):
        powers.append(current)
        work = [0] + list(current)
        leading = work.pop()
        current = tuple(work[j] - leading * polynomial[j]
                        for j in range(degree))
    require(current == powers[0], "root order did not close")
    require(len(set(powers)) == order, "root order collapsed")
    return tuple(powers)


def sum_phases(phases, powers):
    degree = len(powers[0])
    total = [0] * degree
    for phase in phases:
        root = powers[phase % len(powers)]
        for j in range(degree):
            total[j] += root[j]
    return tuple(total)


def valid_columns(matrix, powers):
    rows = len(matrix)
    cols = len(matrix[0])
    zero = (0,) * len(powers[0])
    for first in range(cols):
        for second in range(first):
            phases = (matrix[i][first] - matrix[i][second]
                      for i in range(rows))
            if sum_phases(phases, powers) != zero:
                return False
    return True


def complete(matrix, alphabet):
    require(type(alphabet) is int and 2 <= alphabet <= 15,
            "alphabet outside capacity")
    require(2 <= len(matrix) <= MAX_ROWS, "row count outside capacity")
    rows = len(matrix)
    require(all(len(row) == rows - 1 for row in matrix), "wrong input shape")
    require(all(type(x) is int and 0 <= x < alphabet
                for row in matrix for x in row), "invalid phase code")
    conductor = alphabet if alphabet % 2 == 0 else 2 * alphabet
    powers = roots(conductor)
    scale = conductor // alphabet
    embedded = tuple(tuple(scale * x for x in row) for row in matrix)
    require(valid_columns(embedded, powers), "nonorthogonal input")
    recovered = [0]
    for i in range(1, rows):
        phases = (embedded[i][j] - embedded[0][j] for j in range(rows - 1))
        entry = tuple(-x for x in sum_phases(phases, powers))
        require(entry in powers, "missing entry escaped cyclotomic roots")
        recovered.append(powers.index(entry))
    result = tuple(embedded[i] + (recovered[i],) for i in range(rows))
    require(valid_columns(result, powers), "completed Gram failed")
    require(valid_columns(tuple(zip(*result)), powers),
            "completed row Gram failed")
    return result, conductor


def same_alphabet_required(alphabet, rows):
    if alphabet % 2 == 0:
        return True
    for prime in (3, 5, 7, 11, 13):
        for exponent in range(1, 4):
            if alphabet == prime ** exponent:
                return rows >= 3
    return False


def check_case(matrix, alphabet, counters):
    completed, conductor = complete(matrix, alphabet)
    scale = conductor // alphabet
    require(all(completed[i][:-1] == tuple(scale * x for x in matrix[i])
                for i in range(len(matrix))), "input changed")
    if same_alphabet_required(alphabet, len(matrix)):
        require(all(row[-1] % scale == 0 for row in completed),
                "same-alphabet theorem failed")
        counters["same_alphabet_cases"] += 1
    counters["completed_cases"] += 1
    counters["recovered_entries"] += len(matrix)
    return completed


def dephased_census(rows, alphabet, counters):
    """All dephased 3x2 or 4x3 inputs, with no equivalence deduplication."""
    require(rows in (3, 4), "unsupported census shape")
    powers = roots(alphabet if alphabet % 2 == 0 else 2 * alphabet)
    scale = len(powers) // alphabet
    zero = (0,) * len(powers[0])
    columns = []
    for tail in itertools.product(range(alphabet), repeat=rows - 1):
        counters["candidate_columns"] += 1
        column = (0,) + tail
        if sum_phases((scale * x for x in column), powers) == zero:
            columns.append(column)
    require(len(columns) <= 1000, "census column capacity exceeded")
    count = 0
    choices = (((column,) for column in columns) if rows == 3
               else itertools.product(columns, repeat=2))
    for selected in choices:
        counters["candidate_inputs"] += 1
        all_columns = ((0,) * rows,) + selected
        matrix = tuple(tuple(column[i] for column in all_columns)
                       for i in range(rows))
        embedded = tuple(tuple(scale * x for x in row) for row in matrix)
        if valid_columns(embedded, powers):
            check_case(matrix, alphabet, counters)
            count += 1
    return count


def fourier_tensor(factors, alphabet):
    require(2 <= len(factors) <= 4, "tensor capacity exceeded")
    indices = tuple(itertools.product(*(range(x) for x in factors)))
    require(len(indices) <= MAX_ROWS, "tensor row capacity exceeded")
    require(all(alphabet % x == 0 for x in factors), "incompatible tensor")
    return tuple(tuple(sum(a * b * (alphabet // factor)
                           for a, b, factor in zip(row, col, factors)) % alphabet
                       for col in indices) for row in indices)


def fixtures(counters):
    configurations = (((2, 2), 2), ((2, 3), 6), ((2, 2, 2), 4),
                      ((3, 3), 3), ((3, 3), 9), ((2, 2, 3), 6),
                      ((3, 5), 15))
    for factors, alphabet in configurations:
        full = fourier_tensor(factors, alphabet)
        for erased in range(len(full)):
            for gauge in range(3):
                row_order = tuple(reversed(range(len(full))))
                kept = tuple(j for j in range(len(full)) if j != erased)
                matrix = tuple(tuple((full[i][j] + gauge * (i + 2 * j)) % alphabet
                                     for j in reversed(kept)) for i in row_order)
                completed = check_case(matrix, alphabet, counters)
                scale = (alphabet if alphabet % 2 == 0 else 2 * alphabet) // alphabet
                expected = tuple(scale * ((full[i][erased] + gauge * i
                                 - full[row_order[0]][erased] - gauge * row_order[0]) % alphabet)
                                 for i in row_order)
                require(tuple(row[-1] for row in completed) == expected,
                        "independent erased-column oracle disagrees")
    for phase in range(8):
        full = ((0, 0, 0, 0), (0, 4, phase, (phase + 4) % 8),
                (0, 0, 4, 4), (0, 4, (phase + 4) % 8, phase))
        for erased in range(4):
            matrix = tuple(tuple(row[j] for j in range(4) if j != erased)
                           for row in full)
            check_case(matrix, 8, counters)


def expect_rejection(matrix, alphabet):
    try:
        complete(matrix, alphabet)
    except ValueError:
        return
    raise ValueError("invalid input was accepted")


def controls(counters):
    invalid = (((), 4), (((0, 0), (0, 0)), 4),
               (((0,), (4,)), 4), (((0,), (-1,)), 4),
               (((0,), (True,)), 4), (((0,), (0,)), 1),
               (((0,), (0,)), 16), (((0, 0),) * 3, 4),
               (((0,) * 16,) * 17, 4))
    for matrix, alphabet in invalid:
        expect_rejection(matrix, alphabet)
        counters["rejection_controls"] += 1
    for alphabet in (3, 5, 9, 15):
        completed = check_case(((0,), (0,)), alphabet, counters)
        require(completed == ((0, 0), (0, alphabet)), "odd sign boundary lost")
        counters["odd_two_row_boundaries"] += 1
    powers = roots(8)
    matrix = ((0, 0, 0), (0, 4, 1), (0, 0, 4), (0, 4, 5))
    result, _ = complete(matrix, 8)
    for row in range(1, 4):
        mutant = tuple(r[:-1] + ((r[-1] + (1 if i == row else 0)) % 8,)
                       for i, r in enumerate(result))
        require(not valid_columns(mutant, powers), "mutant escaped Gram oracle")
        counters["output_mutation_controls"] += 1


def main():
    counters = dict.fromkeys(("completed_cases", "same_alphabet_cases",
        "recovered_entries", "candidate_columns", "candidate_inputs",
        "rejection_controls", "odd_two_row_boundaries", "output_mutation_controls"), 0)
    census = {}
    for rows, alphabet in ((3, 3), (3, 6), (3, 9), (3, 15),
                           (4, 2), (4, 4), (4, 6), (4, 8), (4, 10), (4, 12)):
        census[f"{rows}x{rows-1}:mu{alphabet}"] = dephased_census(rows, alphabet, counters)
    fixtures(counters)
    controls(counters)
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        path = package / name
        require(path.stat().st_size <= 1024 * 1024, "package file capacity exceeded")
        data = path.read_bytes()
        hashes[name] = hashlib.sha256(data).hexdigest()
    print(json.dumps({"status": "PASS_CYCLOTOMIC_COLUMN_COMPLETION",
                      "counts": counters, "dephased_census": census,
                      "package_sha256": hashes}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
