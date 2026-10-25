"""Exact bounded atanh and exponential enclosures, independent of source code."""

from fractions import Fraction as Q
from functools import lru_cache


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unit_log(x):
    require(Q(1) <= x <= 2, "unit log domain")
    z = (x - 1) / (x + 1)
    power, total = z, Q(0)
    for j in range(96):
        total += power / (2 * j + 1)
        power *= z * z
    return 2 * total, 2 * total + 2 * power / (193 * (1 - z * z))


@lru_cache(maxsize=32)
def logarithm(x):
    require(Q(1) <= x <= 73, "bounded logarithm domain")
    factor = 0
    for _ in range(7):
        if x <= 2:
            break
        x /= 2
        factor += 1
    require(x <= 2, "binary reduction exhausted")
    low, high = unit_log(x)
    two_low, two_high = unit_log(Q(2))
    return low + factor * two_low, high + factor * two_high


def exponential(x):
    require(0 <= x < Q(1, 10), "small exponential domain")
    term = total = Q(1)
    for j in range(1, 25):
        term *= x / j
        total += term
    first = term * x / 25
    return total, total + first / (1 - x / 26)


def profile(raw, dimension):
    require(type(raw) is dict and 0 < len(raw) <= 16, "profile object")
    parsed = {}
    for key, count in raw.items():
        require(type(key) is str and key.isascii() and key.isdecimal(), "rank")
        rank = int(key)
        require(str(rank) == key and 0 < rank < dimension, "canonical rank")
        require(type(count) is int and 0 < count <= 10**7, "integer count")
        parsed[rank] = count
    return parsed


def moment(histogram, dimension, live, saving, surcharge=False):
    require(type(live) is int and 0 < live <= 10**6, "live count")
    require(0 <= saving <= Q(1, 100), "saving domain")
    low = high = Q(0)
    for rank, count in histogram.items():
        logs = logarithm(Q(dimension, rank))
        weight = Q(rank * count, dimension * live)
        low += weight * exponential(saving * logs[0])[0]
        high += weight * exponential(saving * logs[1])[1]
    if surcharge:
        logs = logarithm(Q(dimension))
        weight = Q(32 * dimension * sum(histogram.values()), 10**16 * live)
        low += weight * exponential(saving * logs[0])[0]
        high += weight * exponential(saving * logs[1])[1]
    return low, high


def dyadic(bounds):
    scale = 1 << 160
    low, high = bounds
    return [str(Q(low.numerator * scale // low.denominator, scale)),
            str(Q(-(-high.numerator * scale // high.denominator), scale))]
