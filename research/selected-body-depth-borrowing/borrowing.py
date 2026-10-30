"""Exact borrowing thresholds for a fixed atom width and stock digit table.

Nick Petalas. Apache-2.0.
"""

from dataclasses import dataclass

MAX_E = (1 << 32) - 1
MAX_WIDTH = 32
MAX_DIMENSION = 64
MAX_DEPTH = MAX_DIMENSION * MAX_E.bit_length()
MAX_DIGITS = 1 << 22


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high, label):
    need(type(value) is int and low <= value <= high, label)


def depth(n, dimension, rank):
    integer(n, 0, MAX_E, "body width capacity")
    integer(dimension, 2, MAX_DIMENSION, "dimension capacity")
    integer(rank, 1, dimension - 1, "strict child contraction")
    for result in range(MAX_DEPTH + 1):
        if n < dimension:
            return result
        n = rank * (n // dimension)
    raise ValueError("depth capacity exhausted")


def table_check(e, width, dimension, rank, digits):
    integer(e, 1, MAX_E, "original width capacity")
    integer(width, 1, MAX_WIDTH, "atom width capacity")
    maximum = depth(e // width, dimension, rank)
    need(type(digits) is tuple and len(digits) == maximum + 1, "complete depth table")
    need(digits[0] == 0, "leaf reserve is one")
    previous = 0
    for value in digits:
        integer(value, previous, MAX_DIGITS, "monotone integer stock digits")
        previous = value


@dataclass(frozen=True)
class Plan:
    borrowed: int
    body: int
    remainder: int
    depth: int
    required_digits: int


def select(e, width, dimension, rank, digits):
    """Return the least admitted borrowing, or None when no fitted plan exists.

    digits[d] must be the EXACT least j with q**j >= S_d. This function
    validates shape and monotonicity; the caller supplies its mathematical
    stock certificate. It does not authenticate a callee or execute a payload.
    """
    table_check(e, width, dimension, rank, digits)
    upper = min((e - 1) // 2, e - dimension * width)
    if upper < 0 or upper < digits[depth((e - upper) // width, dimension, rank)]:
        return None
    lower = -1
    for _ in range(e.bit_length() + 1):
        if upper - lower == 1:
            body, remainder = divmod(e - upper, width)
            actual_depth = depth(body, dimension, rank)
            need(2 * upper < e and body >= dimension, "fitted return invariant")
            need(upper >= digits[actual_depth], "stock return invariant")
            return Plan(upper, body, remainder, actual_depth, digits[actual_depth])
        middle = (lower + upper) // 2
        if middle >= digits[depth((e - middle) // width, dimension, rank)]:
            upper = middle
        else:
            lower = middle
    raise ValueError("bisection capacity exhausted")


def ceil_log(q, stock):
    integer(q, 2, (1 << 127) - 1, "radix capacity")
    integer(stock, 1, (1 << 8192) - 1, "stock certificate capacity")
    low, high = -1, stock.bit_length()
    for _ in range(stock.bit_length().bit_length() + 1):
        if high - low == 1:
            return high
        middle = (low + high) // 2
        if q**middle >= stock:
            high = middle
        else:
            low = middle
    raise ValueError("logarithm capacity exhausted")


def selected_digits(width, maximum):
    """Certify the exact GL64 one-factor digits without materializing its stock.

    The written proof bounds P=prod(1-q**(-i)), not a floating logarithm.
    Failure of the lower certificate rejects rather than rounding a guess.
    """
    integer(width, 1, MAX_WIDTH, "selected atom width capacity")
    integer(maximum, 0, 128, "selected depth capacity")
    q = (1 << 127) - 1
    result = [0]
    for d in range(1, maximum + 1):
        coefficient = 9475 * 28416**d
        need(coefficient.bit_length() <= 8192, "coefficient capacity")
        overhead = ceil_log(q, coefficient)
        need(
            coefficient * (q - 1 - d) > q ** (overhead - 1) * (q - 1),
            "strict lower stock certificate",
        )
        result.append(4096 * width * d + overhead)
    return tuple(result)
