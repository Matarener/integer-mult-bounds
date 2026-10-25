"""Bounded exact certificates for the selected BIT stock envelope."""

from fractions import Fraction
from hashlib import sha256

MAX_DEPTH = 262144
MAX_BITS = 200000
COEFFICIENT = 6741
DEPTH_NUMERATOR = 599
DEPTH_DENOMINATOR = 364


def need(condition, message):
    if not condition:
        raise ValueError(message)


def depth(width):
    need(type(width) is int and width >= 0, "nonnegative integer width")
    need(width.bit_length() <= MAX_BITS, "width exceeds replay capacity")
    for count in range(2 * width.bit_length() + 1):
        if width < 64:
            return count
        width = 42 * (width // 64)
    raise ValueError("depth contraction budget exhausted")


def threshold(level):
    need(type(level) is int and 1 <= level <= MAX_DEPTH, "bounded positive depth")
    width = 64
    for _ in range(level - 1):
        width = 64 * ((width + 41) // 42)
    need(width.bit_length() <= MAX_BITS, "threshold exceeds replay capacity")
    return width


def upper_certificate(coefficient=COEFFICIENT, numerator=DEPTH_NUMERATOR):
    need(type(coefficient) is int and 1 <= coefficient <= 10000, "integer coefficient")
    need(type(numerator) is int and 1 <= numerator <= 1000, "bounded depth numerator")
    power = 5 * numerator - DEPTH_DENOMINATOR
    need(power >= 0 and (1 << power) > 21**numerator, "strict depth contraction")
    stock_rate = Fraction(numerator * 327709, DEPTH_DENOMINATOR * 80)
    need(stock_rate < coefficient, "stock envelope coefficient is too small")
    return {
        "depth_numerator": numerator,
        "depth_denominator": DEPTH_DENOMINATOR,
        "integer_power": power,
        "stock_rate_numerator": stock_rate.numerator,
        "stock_rate_denominator": stock_rate.denominator,
        "margin_numerator": (coefficient - stock_rate).numerator,
        "margin_denominator": (coefficient - stock_rate).denominator,
    }


def finite_depth_checks(limit=131072):
    need(type(limit) is int and 64 <= limit <= 131072, "finite width capacity")
    table = [0] * (limit + 1)
    first = [threshold(level) for level in range(1, 33)]
    for width in range(limit + 1):
        if width >= 64:
            table[width] = 1 + max(table[rank * (width // 64)] for rank in range(1, 43))
        inverse = sum(cut <= width for cut in first)
        need(table[width] == inverse, "all-child depth differs from inverse staircase")
    for level, cut in enumerate(first, 1):
        need(depth(cut) == level and depth(cut - 1) == level - 1, "threshold boundary")
    return {"widths": limit + 1, "threshold_boundaries": len(first)}


def separating_witness():
    width = threshold(MAX_DEPTH)
    bits = width.bit_length()
    need(depth(width) == MAX_DEPTH, "large witness depth")
    lower = 4096 * MAX_DEPTH
    upper = 6740 * bits
    conventional_upper = 6740 * (bits + 1)
    need(lower > conventional_upper, "coefficient 6740 must fail on the actual threshold")
    encoded = width.to_bytes((bits + 7) // 8, "big")
    return {
        "depth": MAX_DEPTH,
        "atom_width": 1,
        "width_bits": bits,
        "width_big_endian_sha256": sha256(encoded).hexdigest(),
        "strict_log_stock_lower": lower,
        "strict_6740_log_width_upper": upper,
        "strict_failure_margin": lower - upper,
        "strict_conventional_upper": conventional_upper,
        "strict_conventional_failure_margin": lower - conventional_upper,
        "prime_scope": "every prime q > 2^80",
    }


def certificate():
    need(28416 * 9475 == 269241600, "actual common packet factor")
    need(269241600 < 1 << 29 and 28416 > 2, "packet logarithm bounds")
    need(9475 > 1, "reduced reserve is positive")
    return {
        "status": "PASS_SELECTED_STOCK_SHARP_INTEGER",
        "coefficient": COEFFICIENT,
        "upper": upper_certificate(),
        "finite": finite_depth_checks(),
        "separating_witness": separating_witness(),
        "scope": "original and current-guard BIT stocks; integer coefficient only",
    }
