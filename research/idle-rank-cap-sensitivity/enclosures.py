# SPDX-License-Identifier: Apache-2.0
"""Exact rational enclosures for (r/m)^(1-a), written independently of the predecessor
packing-ceiling calculator.

Chain: ln k by the atanh sum (positive series, rational tail bound); e^{+x} by its
positive Taylor sum with a geometric tail bound; a is an exact rational on a binary
grid. Every step is directed-rounded toward the required side at 2^-PREC, so each
returned interval contains the true value. Standard library only.

Nick Petalas, with AI assistance. Apache-2.0.
"""
from fractions import Fraction as Q

PREC = 200
XMAX = Q(1, 16)


def down(x):
    return Q((x.numerator << PREC) // x.denominator, 1 << PREC)


def up(x):
    return -down(-x)


def atanh_bounds(t):
    """Enclosure of atanh(t), 0 < t <= 1/3, from its positive series."""
    if not (0 < t <= Q(1, 3)):
        raise ValueError('atanh domain')
    s, p, k = Q(0), t, 0
    while True:
        s += p / (2 * k + 1)
        p *= t * t
        k += 1
        tail = p / ((2 * k + 1) * (1 - t * t))
        if tail < Q(1, 1 << (PREC + 64)):
            return down(s), up(s + tail)


_LN = {1: (Q(0), Q(0))}


def ln_bounds(k):
    """Enclosure of ln k for integer k >= 1: ln k = ln(k-1) + 2 atanh(1/(2k-1))."""
    if k not in _LN:
        if k < 1:
            raise ValueError('ln domain')
        lo, hi = ln_bounds(k - 1)
        a, b = atanh_bounds(Q(1, 2 * k - 1))
        _LN[k] = (down(lo + 2 * a), up(hi + 2 * b))
    return _LN[k]


_FACT = [1]
for _i in range(1, 32):
    _FACT.append(_FACT[-1] * _i)


def exp_pos_bounds(x_lo, x_hi, order=8):
    """Enclosure of e^{x} for 0 <= x_lo <= x <= x_hi <= 1/16 (monotone increasing).

    Positive Taylor sum; the omitted tail is at most twice its first term, since every
    later ratio x/i is at most (1/16)/10 < 1/160.
    """
    if not (0 <= x_lo <= x_hi <= XMAX):
        raise ValueError('exp domain')

    def series(x, side):
        s, t = Q(0), Q(1)
        for j in range(order + 1):
            s += t
            t = t * x / (j + 1)
        err = 2 * t
        return s if side < 0 else s + err

    return series(x_lo, -1), series(x_hi, +1)


def ratio_ln(m, r):
    """Enclosure of ln(m/r) for integers m > r >= 1."""
    if r == m:
        return Q(0), Q(0)
    lm, um = ln_bounds(m)
    lr, ur = ln_bounds(r)
    return down(lm - ur), up(um - lr)


def term_bounds(r, m, a, L):
    """Enclosure of (r/m)^(1-a) = (r/m) e^{a ln(m/r)} for a >= 0."""
    if a < 0:
        raise ValueError('saving must be non-negative')
    e_lo, e_hi = exp_pos_bounds(a * L[0], a * L[1])
    return down(Q(r, m) * e_lo), up(Q(r, m) * e_hi)


def moment_bounds(H, m, W, a):
    """Enclosure of (1/W) sum_r n_r (r/m)^(1-a); H may carry fractional counts."""
    lo = hi = Q(0)
    for r, n in H.items():
        if not (1 <= r < m) or n < 0:
            raise ValueError('child profile')
        c = term_bounds(r, m, a, ratio_ln(m, r))
        lo += n * c[0]
        hi += n * c[1]
    return lo / W, hi / W


def endpoint(H, m, W, bits=40):
    """Certified bracket [a_lo, a_hi] on the unique root of moment(a) = 1.

    a_lo: largest binary-grid point whose certified upper moment is below 1.
    a_hi: the next grid point, whose certified lower moment is above 1.
    """
    D = 1 << bits

    def upper(k):
        return moment_bounds(H, m, W, Q(k, D))[1]

    def lower(k):
        return moment_bounds(H, m, W, Q(k, D))[0]

    hi_k = D // 200
    if lower(hi_k) <= 1:
        raise ValueError('search window too small')
    lo_k = 0
    if upper(lo_k) >= 1:
        raise ValueError('no positive saving')
    while hi_k - lo_k > 1:
        mid = (lo_k + hi_k) // 2
        if upper(mid) < 1:
            lo_k = mid
        elif lower(mid) > 1:
            hi_k = mid
        else:
            raise ValueError('enclosure too wide at grid point ' + str(mid))
    return Q(lo_k, D), Q(hi_k, D)


def kappa(a):
    return a / (1 + a)
