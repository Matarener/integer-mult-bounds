"""Exact integer recovery with a fixed binary sketch and an exact sum.

Produced by Nick Petalas. Apache-2.0.
The executable domain is bounded; PROOF.md has no dimension/magnitude bound.
"""

from fractions import Fraction

MAX_DIMENSION = 64
MAX_BITS = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_integer(value, name):
    require(type(value) is int, name + " must be an integer")
    require(value.bit_length() <= MAX_BITS, name + " exceeds bit limit")
    return value


def checked_fraction(value, name):
    require(type(value) in (int, Fraction), name + " must be exact")
    value = Fraction(value)
    checked_integer(value.numerator, name + " numerator")
    checked_integer(value.denominator, name + " denominator")
    return value


def sketch(values, rows):
    """Internal exact parity evaluation after boundary validation."""
    bits = sum((value & 1) << i for i, value in enumerate(values))
    return tuple((bits & row).bit_count() & 1 for row in rows)


def unique_binary_solution(rows, right, dimension):
    """Eliminate at most 65 equations in at most 64 binary unknowns."""
    equations = list(zip(rows, right))
    pivot_rows = []
    for column in range(dimension):
        candidates = [i for i in range(len(pivot_rows), len(equations))
                      if equations[i][0] & (1 << column)]
        require(bool(candidates), "Parity and sum do not determine all parities")
        pivot = len(pivot_rows)
        other = candidates[0]
        equations[pivot], equations[other] = equations[other], equations[pivot]
        mask, value = equations[pivot]
        for i, (old_mask, old_value) in enumerate(equations):
            if i != pivot and old_mask & (1 << column):
                equations[i] = (old_mask ^ mask, old_value ^ value)
        pivot_rows.append(pivot)
    require(all(mask or not value for mask, value in equations),
            "Inconsistent parity equations")
    assert all(equations[i][0] == 1 << i for i in range(dimension))
    return tuple(equations[i][1] for i in range(dimension))


def decode(observations, rows, tags, total, radius):
    """Return the unique promised vector, or reject an invalid contract.

    Fixed rows are N-bit masks. The promise is |y_i-c_i| <= radius < 1.
    For radius >= 1/2, the augmented parity matrix must have full rank.
    """
    dimension = len(observations)
    require(2 <= dimension <= MAX_DIMENSION, "Dimension outside 2..64")
    require(len(rows) <= MAX_DIMENSION and len(rows) == len(tags),
            "Sketch size outside contract")
    total = checked_integer(total, "Sum")
    radius = checked_fraction(radius, "Radius")
    require(0 <= radius < 1, "Radius outside [0,1)")
    exact = tuple(checked_fraction(y, "Observation") for y in observations)
    for row in rows:
        checked_integer(row, "Row")
        require(0 <= row < 1 << dimension, "Row outside dimension")
    require(all(type(tag) is int and tag in (0, 1) for tag in tags),
            "Tags must be binary integers")
    if radius < Fraction(1, 2):
        result = tuple((y + Fraction(1, 2)).__floor__() for y in exact)
    else:
        parity = unique_binary_solution(
            [*rows, (1 << dimension) - 1], [*tags, total & 1], dimension)
        result = tuple(2 * ((y - bit + 1) / 2).__floor__() + bit
                       for y, bit in zip(exact, parity))
    require(all(abs(y - value) <= radius for y, value in zip(exact, result)),
            "No vector meets the radius promise")
    require(sum(result) == total, "Recovered sum disagrees")
    require(sketch(result, rows) == tuple(tags), "Recovered sketch disagrees")
    return result
