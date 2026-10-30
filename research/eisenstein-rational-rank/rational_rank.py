"""Exact rational rank using primitive integer rows.

Produced by Nick Petalas. Apache-2.0. Row-content elimination is classical.
"""

from fractions import Fraction
from math import gcd, lcm

MAX_DIMENSION = 96
MAX_INPUT_BITS = 128
MAX_ROW_BITS = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def primitive(row):
    require(all(abs(x).bit_length() <= MAX_ROW_BITS for x in row),
            "integer row exceeds bit capacity")
    content = gcd(*row)
    return [x // content for x in row] if content > 1 else row


def integer_rows(matrix):
    require(isinstance(matrix, (list, tuple)), "matrix must be a sequence")
    require(len(matrix) <= MAX_DIMENSION, "too many rows")
    width = len(matrix[0]) if matrix else 0
    require(width <= MAX_DIMENSION, "too many columns")
    rows = []
    for row in matrix:
        require(isinstance(row, (list, tuple)) and len(row) == width, "ragged matrix")
        denominator = 1
        for value in row:
            require(type(value) in (int, Fraction), "entries must be exact rationals")
            require(max(abs(value.numerator).bit_length(), value.denominator.bit_length())
                    <= MAX_INPUT_BITS, "rational entry exceeds bit capacity")
            denominator = lcm(denominator, value.denominator)
            require(denominator.bit_length() <= MAX_ROW_BITS, "row denominator too large")
        rows.append(primitive([x.numerator * (denominator // x.denominator) for x in row]))
    return rows, width


def rank(matrix):
    """Return Q-rank without changing the input; reject capacity exhaustion."""
    rows, width = integer_rows(matrix)
    pivot = 0
    for column in range(width):
        found = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        leading = rows[pivot][column]
        require(leading != 0, "zero pivot")
        for i in range(pivot + 1, len(rows)):
            factor = rows[i][column]
            if factor:
                tail = [leading * x - factor * y
                        for x, y in zip(rows[i][column + 1:], rows[pivot][column + 1:])]
                rows[i] = [0] * (column + 1) + primitive(tail)
        pivot += 1
        if pivot == len(rows):
            break
    return pivot
