"""Opt-in fixed-point Taylor bounds for the pinned ceiling exponential.

The engine in research/complex-local-word-ceiling/ceiling.py stays on disk.
Its SHA-256 is an input pin of other packages, so this module never writes it.
"""
from fractions import Fraction as Q


def series(value, upper, prec, max_terms=None):
    """Outward enclosure of exp(value) at denominator 2^prec.

    Each term is an integer multiple of 2^-(prec+48). The upper sum includes
    the same geometric tail shape as the pinned series, 2*t*y/(k+1), rounded
    away from zero. max_terms is only for the truncated negative control.
    """
    scale = prec + 48
    if value == 0:
        coefficient = 0
    elif upper:
        coefficient = -((-value.numerator << scale) // value.denominator)
    else:
        coefficient = (value.numerator << scale) // value.denominator
    unit = 1 << scale
    total = unit
    term = unit
    step = 0
    stop = scale + scale - (prec + 8)
    limit = 10_000 if max_terms is None else max_terms
    while step < limit:
        step += 1
        numerator = term * coefficient
        denominator = step << scale
        if upper:
            term = (numerator + denominator - 1) // denominator
        else:
            term = numerator // denominator
        total += term
        if coefficient == 0 or term * coefficient < 1 << stop or step == limit:
            shift = scale - prec
            if upper:
                tail = 2 * term * coefficient
                tail_den = (step + 1) << scale
                total += (tail + tail_den - 1) // tail_den
                return Q((total + (1 << shift) - 1) >> shift, 1 << prec)
            return Q(total >> shift, 1 << prec)
    raise RuntimeError("exponential series did not finish")


def bounds(low, high, prec, require):
    """Same argument contract as the pinned exp: 0 <= low <= high <= 1/2."""
    require(0 <= low <= high <= Q(1, 2), "exp range")
    return series(low, False, prec), series(high, True, prec)
