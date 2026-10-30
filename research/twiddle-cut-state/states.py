"""Exact residual-state counts for source-layout synthetic twiddle cuts.

Nick Petalas. Apache-2.0.
"""

from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(d, h, low, bottom):
    require(all(type(x) is int for x in (d, h, low, bottom)), 'integer parameters required')
    require(0 <= d <= 256 and 0 <= low <= bottom <= h <= 256, 'parameter limit')


def constants(active, h, low, bottom):
    """Number of reachable constants for a fixed branch vector of this weight."""
    validate(active, h, low, bottom)
    width, stride, high = 1 << low, 1 << bottom, 1 << (h - bottom)
    modulus = 1 << (h + 1)
    tail = active * (width - 1)
    if tail < stride - 1:
        bands = min(2 * high, active * (high - 1) + 1)
        return bands * (tail + 1)
    endpoint = active * ((high - 1) * stride + width - 1)
    return min(modulus, endpoint + 1)


def count_states(d, h, low, bottom):
    """Count suffix functions, including the no-relevant-suffix case."""
    validate(d, h, low, bottom)
    if h == 0 or d == 0:
        return 1
    if bottom == low:
        return min(1 << (h + 1), d * ((1 << h) - 1) + 1)
    return sum(comb(d, active) * constants(active, h, low, bottom)
               for active in range(d + 1))


def bit_bound(d, h, low, bottom):
    return (count_states(d, h, low, bottom) - 1).bit_length()


def no_low_prefix(d, h, bottom):
    """Simplified closed form when no low bits have already been extracted."""
    validate(d, h, 0, bottom)
    require(1 <= bottom <= h and d >= 1, 'nonempty suffix and participants required')
    high = 1 << (h - bottom)
    if high == 1:
        return 1 << d
    return (1 + d * high + comb(d, 2) * (2 * high - 1)
            + ((1 << d) - 1 - d - comb(d, 2)) * 2 * high)


def source_cut(ell, width, long_axes, h):
    """Return physical cut extent, effective low-prefix width and chunk bottom."""
    require(type(ell) is int and 2 <= ell <= 256, 'ell limit')
    require(type(width) is int and 1 <= width < ell, 'width limit')
    require(type(long_axes) is tuple and 1 <= len(long_axes) <= 64
            and all(type(x) is bool for x in long_axes), 'axis limit')
    require(type(h) is int and 0 <= h < ell, 'round limit')
    axes, tops = len(long_axes), sum(long_axes)
    low = (ell - 1) % width
    if h == ell - 1:
        return tops, 0, h
    if h < low:
        return tops + axes * (low - h), 0, h
    bottom = low + ((h - low) // width) * width
    chunks = (ell - 1 - bottom) // width
    return tops + axes * low + axes * width * chunks, low, bottom
