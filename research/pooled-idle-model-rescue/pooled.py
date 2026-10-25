# SPDX-License-Identifier: Apache-2.0
"""Pooled per-replica idle model for the selected complex local word.

Two questions this module answers that a per-call model cannot.

1. CONVERT #1685's PROVED integer optimum into a ceiling. `research/idle-packing-stability`
   proves the unrestricted integer idle optimum `{51:4647, 27:1}` for idle mass 237024 at
   replica scale, then explicitly declines to state the ceiling that optimum implies. This
   module supplies it.

2. WHICH MODEL PRICES THE SELECTED RECORD. `research/complex-local-word-ceiling` and the
   integrality work of PR #3729 both price one CALL at a time: `w = families / stages`
   live families per call, and the call's own idle mass. PR #1685 prices a whole REPLICA:
   `W = 2 * 4 * 112 * 16 = 14336` live families over `N = 144` calls. The two give different
   ceilings for the same word, because a call's idle mass need not be an integer while the
   replica's is.

The pooled model is the weaker relaxation of the two in the sense that matters here: it
allows more freedom (children may be shared across the 144 calls of a replica), so its
ceiling is at least as large. It is therefore the model under which a *packing* claim is
most likely to survive, and the one a candidate supplier should be screened against before
effort is spent.

Exact rational intervals are imported from `research/complex-local-word-ceiling/ceiling.py`
(Douglas Colkitt, Apache-2.0) rather than reimplemented. The idle closed form is #1685's.
No floating point enters a bracket. Apache-2.0.
"""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    'credited_ceiling', _ROOT / 'research/complex-local-word-ceiling/ceiling.py')
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

require = C.require
down, up = C.down, C.up


def optimal_idle_histogram(mass, R):
    """Exact integer minimiser of idle cost for integer mass `mass` under integer cap `R`.

    #1685's closed form: as many rank-`R` children as fit, plus at most one remainder child.
    Restated here, not claimed as new; `verify.py` re-checks it by dynamic programming.
    """
    require(isinstance(mass, int) and mass >= 0, 'idle mass domain')
    require(isinstance(R, int) and R >= 1, 'idle rank cap domain')
    q, s = divmod(mass, R)
    hist = {}
    if q:
        hist[R] = q
    if s:
        hist[s] = 1
    require(sum(r * n for r, n in hist.items()) == mass, 'idle mass mismatch')
    require(all(1 <= r <= R for r in hist), 'idle rank outside cap')
    return hist


def replica_model(local, m, live_families_per_call, calls, centre_per_call, unpaid=1, R=None):
    """Per-replica coverage-law quantities under PR1012's identity.

    `local` is the paid child profile of ONE call; each of the `calls` calls carries it, so
    the replica's paid local mass is `calls * sum(r n_r)`. The covered mass is
    `calls * ((m - unpaid) * w + centre_per_call)` with `w = live_families_per_call`, i.e.
    the incumbent's per-call identity applied `calls` times. The residual is the POOLED idle
    mass, over `calls * w` live families. Raises if that residual is not a non-negative
    integer, because a replica's child multiset cannot have non-integral rank mass.
    """
    R = C.max_idle_rank(m) if R is None else R
    require(2 * R * R < m * m, 'idle rank cap violates the outer halving guard')
    require(isinstance(calls, int) and calls >= 1, 'call count domain')
    require(all(0 < r < m for r in local) and all(n >= 0 for n in local.values()), 'local profile')
    require(1 <= unpaid < m, 'unpaid coordinates per family')
    w = Q(live_families_per_call)
    total = calls * ((m - unpaid) * w + centre_per_call)
    local_mass = calls * sum(r * Q(n) for r, n in local.items())
    idle = total - local_mass
    require(idle >= 0, 'local word pays more mass than the coverage law allows')
    require(idle.denominator == 1, 'pooled idle mass is not an integer; no integer packing exists')
    return dict(R=R, w=w, W=calls * w, calls=calls, total_mass=total,
                local_mass=local_mass, idle_mass=idle, unpaid=unpaid)


def histogram_moment(hist, m, W, a):
    """Enclosure of the moment of one complete histogram over `W` live families."""
    require(0 <= a < 1, 'saving domain')
    lo = hi = Q(0)
    for r, n in hist.items():
        c = C.child_cost(r, m, a)
        lo, hi = lo + Q(n) * c[0], hi + Q(n) * c[1]
    return down(lo / W), up(hi / W)


def pooled_ceiling(local, m, live_families_per_call, calls, centre_per_call, grid=Q(1, 10 ** 15),
                   unpaid=1, R=None):
    """Certified grid bracket [a_lo, a_hi] for the POOLED per-replica integer model.

    `a_hi` is the ceiling: no integer idle histogram pooled across the replica's calls
    reaches a saving >= a_hi, for this local word, template, coverage law and outer recipe.
    """
    q = replica_model(local, m, live_families_per_call, calls, centre_per_call, unpaid, R)
    opt = optimal_idle_histogram(int(q['idle_mass']), q['R'])

    def moment(a):
        hist = {r: q['calls'] * n for r, n in local.items()}
        for r, n in opt.items():
            hist[r] = hist.get(r, 0) + n
        return histogram_moment(hist, m, q['W'], a)

    lo, hi = Q(0), Q(1, 20)
    require(moment(hi)[0] > 1, 'pooled search window too small')
    require(moment(lo)[1] < 1, 'pooled integer packing has no positive saving')
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        v = moment(mid)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise ValueError('enclosure too wide to separate the grid point')
    return lo, hi, opt, q