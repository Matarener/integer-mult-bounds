# SPDX-License-Identifier: Apache-2.0
"""Exact attained ceiling for the rank-capped complex local mass, with the idle remainder integral.

`research/complex-local-word-ceiling` prices the selected complex local word under the coverage
law. Two relaxations sit in that model and in its rank-cap continuation:

  * the idle remainder of a call is placed in `idle/R` *fractional* rank-R children, because the
    per-unit cost `r^(-a) m^(a-1)` is decreasing in `r`; and
  * the local paid mass can be reshaped into `mass/s` *fractional* rank-s children to raise the
    ceiling with the coverage law, centre charge and outer guard all untouched.

Real packings use integer child multisets in both pools. This module computes the **attained
optimum over joint integer packings**: the local paid mass is delivered as integer children of
rank at most `cap`, the idle remainder as integer children of rank at most the halving guard `R`,
and the resulting per-call moment is minimised over both pools simultaneously.

For a saving `a`, the per-call moment is

    sum_r n_r (r/m)^(1-a)   over the local children (r <= cap)
  + sum_r n_r (r/m)^(1-a)   over the idle children (r <= R),

divided by `w = families/stages`. Two certified facts follow from the outward-rounded enclosures
of `ceiling.child_cost`, exactly as in the fractional parent:

  * `lower(a)` = (min local + min idle) over the lower enclosures is a certified lower bound on
    *every* joint integer packing's moment, so `lower(a)/w > 1` rejects the saving `a`.
  * the argmins together are one explicit feasible joint packing; its upper enclosure
    `upper(a)/w < 1` accepts `a`.

The two pools are minimised independently, which is exact: they share no mass.

Standard library only; exact rational arithmetic with outward rounding to 2^-PREC, re-using
`ceiling.py`'s logarithm, exponential and interval primitives. Nick Petalas, with AI assistance.
Apache-2.0.
"""
import sys
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

__all__ = ['best_hist', 'full_dp', 'hist_upper', 'moment_bounds', 'bracket', 'scaled_lower',
           'scaled_upper']

SCALE = 1 << C.PREC


def scaled(x):
    """Exact integer numerator of the dyadic rational x at 2^-PREC."""
    v = Q(x) * SCALE
    C.require(v.denominator == 1, 'value is not a multiple of 2^-PREC')
    return v.numerator


@lru_cache(maxsize=None)
def scaled_lower(r, m, a):
    """Certified lower enclosure of (r/m)^(1-a) at 2^-PREC, as an exact integer."""
    return scaled(C.child_cost(r, m, a)[0])


@lru_cache(maxsize=None)
def scaled_upper(r, m, a):
    """Certified upper enclosure of (r/m)^(1-a) at 2^-PREC, as an exact integer."""
    return scaled(C.child_cost(r, m, a)[1])


def full_dp(mass, cap, m, a):
    """Reference dynamic program: exact minimum over integer histograms of this mass and cap.

    Returns (certified_lower_scaled, histogram). The recurrence enumerates the whole feasible set:
        f[j] = min over 1 <= r <= min(cap, j) of f[j - r] + down_cost[r].
    """
    C.require(isinstance(mass, int) and mass >= 0, 'mass must be a non-negative integer')
    C.require(isinstance(cap, int) and 1 <= cap < m, 'child rank cap out of range')
    if mass == 0:
        return 0, {}
    cost = [0] + [scaled_lower(r, m, a) for r in range(1, cap + 1)]
    best = [None] * (mass + 1)
    back = [0] * (mass + 1)
    best[0] = 0
    for j in range(1, mass + 1):
        value, pick = None, 0
        for r in range(1, min(cap, j) + 1):
            prev = best[j - r]
            if prev is None:
                continue
            v = prev + cost[r]
            if value is None or v < value:
                value, pick = v, r
        best[j], back[j] = value, pick
    C.require(best[mass] is not None, 'no integer histogram of this mass and cap exists')
    return best[mass], recover(back, mass, cap)


def recover(back, mass, cap):
    hist = {}
    j = mass
    while j:
        r = back[j]
        C.require(1 <= r <= cap, 'dynamic program produced an out-of-range rank')
        hist[r] = hist.get(r, 0) + 1
        j -= r
    C.require(sum(r * n for r, n in hist.items()) == mass, 'recovered histogram does not conserve mass')
    return hist


def best_hist(mass, cap, m, a):
    """Attained minimum over integer histograms of total mass `mass` with ranks 1..cap.

    Returns `(certified_lower_scaled, histogram)`: the value bounds the optimum's moment sum over
    the lower enclosures from below, and the histogram is a feasible integer packing of exactly
    that mass with a certified upper enclosure of its own moment (`hist_upper`).
    """
    return full_dp(mass, cap, m, a)


def hist_upper(hist, m, a):
    """Certified upper-scaled enclosure of one explicit histogram's moment sum."""
    return sum(n * scaled_upper(r, m, a) for r, n in hist.items())


def moment_bounds(local_mass, local_cap, idle_mass, idle_cap, m, w, a):
    """Certified (lower, upper, local_hist, idle_hist) per-call moment enclosures at saving `a`.

    `lower` bounds every joint integer packing of the two pools from below; `upper` bounds the
    moment of the explicit packing the two argmins describe from above.
    """
    paid_lo, paid_h = best_hist(local_mass, local_cap, m, a)
    idle_lo, idle_h = best_hist(idle_mass, idle_cap, m, a)
    lower = Q(paid_lo + idle_lo) / SCALE / w
    upper = Q(hist_upper(paid_h, m, a) + hist_upper(idle_h, m, a)) / SCALE / w
    return lower, upper, paid_h, idle_h


def bracket(local_mass, local_cap, idle_mass, idle_cap, m, w, grid=Q(1, 10 ** 15)):
    """Grid bracket [a_lo, a_hi] for the attained joint integer ceiling of this cap class.

    `a_lo` is witnessed: an explicit joint integer packing has certified moment < 1 there.
    `a_hi` is rejected: the certified lower bound of every joint integer packing exceeds 1.
    """
    lo, hi = Q(0), Q(1, 20)
    _l, top_up, _, _ = moment_bounds(local_mass, local_cap, idle_mass, idle_cap, m, w, hi)
    bot_lo, _u, _, _ = moment_bounds(local_mass, local_cap, idle_mass, idle_cap, m, w, lo)
    C.require(top_up > 1 and bot_lo < 1, 'search window does not bracket one')
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        low, high, _, _ = moment_bounds(local_mass, local_cap, idle_mass, idle_cap, m, w, mid)
        if high < 1:
            lo = mid
        elif low > 1:
            hi = mid
        else:
            raise ValueError('enclosure too wide to separate the grid point')
    return lo, hi
