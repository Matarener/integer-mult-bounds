# SPDX-License-Identifier: Apache-2.0
"""Rank-shape ceilings for the selected complex local word.

Exact interval arithmetic is reused unchanged from the sibling package
`research/complex-local-word-ceiling/ceiling.py` (PR lineage: static44 / PR525 /
PR643 / PR1012). Nothing here re-implements or relaxes that arithmetic.

Definitions (all exact, all inputs explicit)
--------------------------------------------
Per call the selected word pays `local` units of rank mass on ranks <= 8 and the
coverage law (PR1012) fixes the rest of the call at `idle_mass`. The sibling
ceiling model puts every idle unit into fractional rank-`R` children, `R = 51`
being the outer halving guard for `m = 73`. Its per-call relaxation is

    relax_H(a) = ( sum_r n_r (r/m)^(1-a) + (idle/R) (R/m)^(1-a) ) / w .

Two ceilings are reported for each integer rank cap `s >= 1`, both restricting
only the *local word's* paid children to ranks <= s and leaving the coverage law,
the centre charge, `w` and the idle treatment untouched:

    frac_s : replace the local profile by the single fractional child
             `{s: local_mass / s}`. This is the ideal relaxation: `ceil_frac_s`
             is an upper bound for the cap-`s` class, because per-unit-mass cost
             r^(1-a)/r = m^(a-1) r^(-a) is non-increasing in r.

    int_s  : the exact integer histogram `greedy(local_mass, s)` that delivers
             `local_mass` in children of rank <= s. Every count is an integer, so
             this one is *realisable as a child count*; it is a lower bound for
             the cap-`s` class.

    int_s <= cap_s <= frac_s   is therefore an exact sandwich with no search
    over histograms. `dp_histograms` provides an independent check of whether the
    greedy histogram is the exact integer optimum; it is a *check*, not part of
    the certified result, because interval comparisons in the dynamic program
    are only decided when the compared enclosures are disjoint.
"""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

GRID = Q(1, 10 ** 15)   # same grid as the sibling package, so base ceilings compare exactly


def require(ok, why):
    if not ok:
        raise ValueError(why)


def greedy(mass, cap):
    """Largest-rank-first decomposition of an integer mass into ranks <= cap.

    Returns {rank: count} with all counts integers and sum_r count*r == mass.
    """
    require(mass >= 0 and cap >= 1, 'greedy domain')
    hist, left = {}, int(mass)
    for r in range(cap, 0, -1):
        n, left = divmod(left, r)
        if n:
            hist[r] = n
    require(left == 0, 'greedy left mass')
    require(all(1 <= r <= cap for r in hist) and sum(r * n for r, n in hist.items()) == mass, 'greedy mass')
    return hist


def cap_ceiling(local, m, families, stages, centre, unpaid=1):
    """Certified grid ceiling of a (possibly fractional) per-call local profile."""
    return C.ceiling(local, m, families, stages, centre, grid=GRID, unpaid=unpaid)[1]


def frac_profile(local_mass, cap):
    """The ideal fractional relaxation at rank cap."""
    return {cap: Q(local_mass, cap)}


def dp_histograms(mass, caps, m, R, a):
    """Independent exact-enclosure dynamic program over integer child counts.

    Minimises the *lower* enclosure of sum_r n_r p_r(a), the excess price of a
    local rank-r child over ideal idle mass, and returns
    `{cap: (histogram, ambiguous_comparisons)}`. `ambiguous` counts dynamic-program
    comparisons whose candidate enclosures overlap. Where it is 0 every comparison
    was decided by disjoint enclosures and the histogram is the exact integer
    optimum; otherwise the result is a certified-feasible histogram that may not
    be optimal, which is why this is a check on the sandwich and not part of it.

    One unbounded-coin pass serves every cap in `caps`: the rank loop runs once in
    increasing order, so the shared table *is* the cap-`s` dynamic program at the
    end of step `s`. Each requested cap is backtracked and its table dropped
    immediately.
    """
    caps = sorted(set(caps))
    require(1 <= min(caps) and max(caps) < m and mass >= 0, 'dp domain')
    require(Q(mass).denominator == 1, 'dp mass is not an integer')
    mass = int(mass)
    cR = C.child_cost(R, m, a)
    lo_p, hi_p = {}, {}
    for r in range(1, max(caps) + 1):
        c = C.child_cost(r, m, a)
        lo_p[r] = c[0] - r * cR[1] / R
        hi_p[r] = c[1] - r * cR[0] / R
    best = [None] * (mass + 1)          # best[t] = (lo, hi, rank chosen at t)
    best[0] = (Q(0), Q(0), 0)
    ambiguous = 0
    out, wanted = {}, set(caps)
    for r in range(1, max(caps) + 1):
        for t in range(r, mass + 1):
            take = best[t - r]
            cand = (take[0] + lo_p[r], take[1] + hi_p[r], r)
            cur = best[t]
            if cur is None:
                best[t] = cand
            elif cand[1] < cur[0]:
                best[t] = cand
            elif not cur[1] < cand[0]:
                ambiguous += 1
                best[t] = cand if cand[0] < cur[0] else cur
        if r in wanted:
            hist, t = {}, mass
            while t > 0:
                k = best[t][2]
                require(k >= 1, 'dp backtrack')
                hist[k] = hist.get(k, 0) + 1
                t -= k
            require(sum(k * v for k, v in hist.items()) == mass, 'dp mass')
            out[r] = (hist, ambiguous)
    return out