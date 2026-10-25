"""Exact bounds for projective Clifford tensor Gram matrices.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction


def gaussian_binomial(dimension, rank):
    """Count binary subspaces of the specified rank."""
    if not 0 <= rank <= dimension:
        return 0
    value = Fraction(1)
    for j in range(rank):
        value *= Fraction((1 << (dimension-j))-1, (1 << (rank-j))-1)
    if value.denominator != 1:
        raise ArithmeticError("Nonintegral subspace count")
    return value.numerator


def overlap_counts(axes, *, clifford=False):
    """Return exact stabilizer counts or upper bounds for Clifford counts.

    For Clifford maps, axes is the number of input axes. For stabilizer
    states, axes is the number of state axes, including both Choi halves.
    """
    if type(axes) is not int or axes < 0:
        raise ValueError("Axes must be a nonnegative integer")
    dimension = 2*axes if clifford else axes
    counts = [gaussian_binomial(dimension, k)*(1 << (k*(k+3)//2))
              for k in range(dimension+1)]
    if clifford and dimension:
        counts[1] //= 2
    return counts


def row_bound(axes, width, *, clifford=False):
    """Bound the absolute off-diagonal sum at an even tensor width."""
    if type(width) is not int or width <= 0 or width % 2:
        raise ValueError("The exact rational row bound needs a positive even width")
    counts = overlap_counts(axes, clifford=clifford)
    return sum((Fraction(count, 1 << (k*width//2))
                for k, count in enumerate(counts) if k), Fraction())


def decision_widths(axes):
    if type(axes) is not int or axes < 0:
        raise ValueError("Axes must be a nonnegative integer")
    start = 4*axes+4 if axes else 1
    return list(range(start, start+4))


def pointwise_bound(axes, width, *, clifford=False):
    """Give a rational lower Gram bound at the requested width.

    Odd widths use the preceding even-width estimate. A nonpositive lower
    bound gives no decision. It does not prove dependence.
    """
    if type(axes) is not int or axes < 0:
        raise ValueError("Axes must be a nonnegative integer")
    if type(width) is not int or width <= 0:
        raise ValueError("Width must be a positive integer")
    if axes == 0:
        return Fraction(1)
    if width == 1:
        return Fraction(1)-sum(overlap_counts(axes, clifford=clifford)[1:])
    return Fraction(1)-row_bound(axes, width-width % 2, clifford=clifford)
