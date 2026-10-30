"""Exact two-role dyadic completion optimizer; no numerical eigenvalues."""

from fractions import Fraction


MAX_BITS = 64


class Completion:
    __slots__ = ("exponent", "q", "matrix")

    def __init__(self, exponent: int, q: Fraction, matrix: tuple):
        self.exponent = exponent
        self.q = q
        self.matrix = matrix


def power_two(exponent: int) -> Fraction:
    if not isinstance(exponent, int) or isinstance(exponent, bool):
        raise ValueError("integer exponent required")
    if not -260 <= exponent <= 260:
        raise ValueError("exponent outside executable range")
    if exponent >= 0:
        return Fraction(1 << exponent)
    return Fraction(1, 1 << -exponent)


def pair(values: tuple) -> tuple[Fraction, Fraction]:
    if not isinstance(values, (tuple, list)) or len(values) != 2:
        raise ValueError("exactly two coordinates required")
    result = []
    for value in values:
        if not isinstance(value, (int, Fraction)) or isinstance(value, bool):
            raise ValueError("integer or Fraction coordinates required")
        coordinate = Fraction(value)
        denominator = coordinate.denominator
        if denominator & (denominator - 1):
            raise ValueError("coordinates must be dyadic")
        if abs(coordinate.numerator).bit_length() > MAX_BITS:
            raise ValueError("numerator exceeds executable bound")
        if denominator.bit_length() - 1 > MAX_BITS:
            raise ValueError("denominator exceeds executable bound")
        result.append(coordinate)
    return result[0], result[1]


def optimal_completions(a: tuple, b: tuple) -> tuple[Completion, ...]:
    """Return positive-determinant representatives at every optimal exponent.

    The opposite sign of the second column gives all negative-determinant
    minimizers. The proof has no bit-size limit; this executable does.
    """
    row, column = pair(a), pair(b)
    if sum(row[i] * column[i] for i in range(2)) != 1:
        raise ValueError("the prescribed row and column must pair to one")
    aa = sum(x * x for x in row)
    bb = sum(x * x for x in column)
    ratio = bb / aa
    exponent = ratio.numerator.bit_length() - ratio.denominator.bit_length()
    if ratio < power_two(exponent):
        exponent -= 1
    first = exponent // 2
    candidates = []
    for k in (first, first + 1):
        scale = power_two(k)
        matrix = ((column[0], -scale * row[1]),
                  (column[1], scale * row[0]))
        q = aa * scale + bb / scale
        candidates.append(Completion(k, q, matrix))
    minimum = min(item.q for item in candidates)
    result = tuple(item for item in candidates if item.q == minimum)
    if not result or minimum < 2:
        raise ArithmeticError("invalid completion invariant")
    return result
