"""Small exact linear algebra for the new two-coset fixtures.

Produced by Nick Petalas. SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    """Exact row rank; callers supply at most 80 rows and 30 columns."""
    need(len(rows) <= 80, "row limit")
    width = len(rows[0]) if rows else 0
    need(width <= 30 and all(len(r) == width for r in rows), "matrix shape")
    work = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for column in range(width):
        found = next((i for i in range(pivot, len(work)) if work[i][column]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        divisor = work[pivot][column]
        work[pivot] = [x / divisor for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            coefficient = work[i][column]
            work[i] = [x - coefficient * y for x, y in zip(work[i], work[pivot])]
        pivot += 1
    return pivot


def apply(rows, vector):
    need(all(len(row) == len(vector) for row in rows), "operator shape")
    return [sum(x * y for x, y in zip(row, vector)) for row in rows]
