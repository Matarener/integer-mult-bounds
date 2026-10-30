"""Exact fixed-width borrowing for strict factor-two compatible-row padding.

Nick Petalas. Apache-2.0. The covering-constrained predecessor is PR3486.
"""

MAX_E = (1 << 64) - 1
MAX_DEPTH = 4096
MAX_DIGITS = 1 << 24


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high, message):
    require(type(value) is int and low <= value <= high, message)


def depth(n, dimension, rank):
    integer(n, 0, MAX_E, "body capacity")
    integer(dimension, 2, 64, "dimension capacity")
    integer(rank, 1, dimension - 1, "strict child contraction")
    for result in range(MAX_DEPTH + 1):
        if n < dimension:
            return result
        n = rank * (n // dimension)
    raise ValueError("depth capacity exhausted")


def validate(e, width, dimension, rank, thresholds):
    integer(e, 1, MAX_E, "original width capacity")
    integer(width, 1, MAX_E, "fixed atom width capacity")
    maximum = depth(e // width, dimension, rank)
    require(type(thresholds) is tuple, "immutable threshold table")
    require(len(thresholds) == maximum + 1, "complete threshold table")
    require(thresholds[0] == 0, "leaf reserve threshold")
    previous = 0
    for threshold in thresholds:
        integer(threshold, previous, MAX_DIGITS, "monotone integer threshold")
        previous = threshold


def select(e, width, dimension, rank, thresholds):
    """Return (k,n,ell,d), or None; thresholds[d]=min{j:2*q**j>S_d}.

    The caller certifies these exact thresholds. Validation checks their shape,
    capacity and monotonicity, not an omitted stock or callee premise.
    """
    validate(e, width, dimension, rank, thresholds)
    high = min((e - 1) // 2, e - dimension * width)
    if high < 0:
        return None
    if high < thresholds[depth((e - high) // width, dimension, rank)]:
        return None
    low = 0
    for _ in range(e.bit_length() + 1):
        if low == high:
            n, ell = divmod(e - low, width)
            d = depth(n, dimension, rank)
            require(2 * low < e and n >= dimension, "geometric return invariant")
            require(low >= thresholds[d], "strict padding return invariant")
            return low, n, ell, d
        middle = (low + high) // 2
        if middle >= thresholds[depth((e - middle) // width, dimension, rank)]:
            high = middle
        else:
            low = middle + 1
    raise ValueError("bisection capacity exhausted")


def digit_table(q, factor, compatibility, maximum, covering=False):
    integer(q, 2, 257, "toy radix capacity")
    integer(factor, 1, 256, "toy level factor capacity")
    integer(compatibility, 1, 64, "toy compatibility capacity")
    integer(maximum, 0, 128, "toy depth capacity")
    require(type(covering) is bool, "explicit threshold policy")
    result = [0]
    stock = compatibility
    for _ in range(maximum):
        stock *= factor
        power = 1
        for k in range(stock.bit_length() + 1):
            if (power >= stock) if covering else (2 * power > stock):
                result.append(k)
                break
            power *= q
        else:
            raise ValueError("stock threshold capacity exhausted")
    return tuple(result)


def selected_tables(width, maximum):
    """Certify strict and covering GL64 digits using exact product bounds."""
    integer(width, 1, 32, "selected atom width capacity")
    integer(maximum, 0, 128, "selected depth capacity")
    q = (1 << 127) - 1
    strict, covering = [0], [0]
    for d in range(1, maximum + 1):
        coefficient = 9475 * 28416**d
        for table, multiplier in ((strict, 2), (covering, 1)):
            power = 1
            for j in range(coefficient.bit_length() + 1):
                if multiplier * power > coefficient:
                    break
                power *= q
            require(j > 0, "positive coefficient exponent")
            require(
                coefficient * (q - 1 - d) > multiplier * (power // q) * (q - 1),
                "strict lower product certificate",
            )
            table.append(4096 * width * d + j)
    return tuple(strict), tuple(covering)
