# SPDX-License-Identifier: Apache-2.0
"""Certified paid-mass-elimination budget for the selected complex local word.

Model (inherited unchanged from research/complex-local-word-ceiling/ceiling.py):

  * one call carries `w = families/stages` live data families; the coverage
    identity forces total rank mass `(m - unpaid) * w + centre` per call;
  * the selected word pays `local = {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`
    mass units per call; the remainder is idle/remainder mass;
  * idle children have rank at most `R`, fixed by the outer halving guard;
  * a rank-r child costs `(r/m)^(1-a)`.

This package adds one axis: a *favorable* elimination relaxation.  A proposal
may remove paid local mass and let the coverage law re-pack that mass as ideal
rank-R idle children.  The cost of realizing the removal is not charged.  The
saving per unit of removed mass for a rank-r child is

    r^(-a) * m^(a-1) - R^(-a) * m^(a-1)  > 0   for every r < R,

which is strictly larger for smaller r.  So the optimal relaxation removes the
lowest-rank paid children first.  Splitting a child fractionally is allowed, as
in the predecessor relaxation; the whole-child breakpoints are reported too.

For every target saving `a` the verifier certifies the smallest eliminated mass
fraction `phi(a)` whose relaxation moment is at most one, and the ceiling at
each whole-child breakpoint.  A target with no `phi <= 1` is not reachable by
this relaxation of this word.

This is a bound for the stated model, not a construction: it prices how much
paid local mass a decoder or helper-inventory proposal must remove to certify a
given saving, so proposals can be screened before any network is built.  It is
not a new kappa and says nothing about other local words, templates, coverage
laws, centre charges or outer recipes.
"""
import sys
from fractions import Fraction as Q

sys.path.insert(0, 'research/complex-local-word-ceiling')
from ceiling import child_cost, model  # noqa: E402

LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
GRID = Q(1, 10 ** 15)
TOL = Q(1, 10 ** 9)


def fail(why):
    raise SystemExit('FAIL_COMPLEX_PAID_MASS_BUDGET: ' + why)


def context():
    q = model(LOCAL, M, FAMILIES, STAGES, CENTRE)
    return q, Q(FAMILIES, STAGES)


def relax_eliminated(a, mu, q, w):
    """Enclosure of the per-call relaxation after removing `mu` mass units.

    The removed mass is taken from the lowest-rank paid children first and is
    re-packed as ideal rank-R idle children.
    """
    R = q['R']
    rem = Q(mu)
    if rem < 0 or rem > q['local_mass']:
        fail('removed mass outside [0, local_mass]')
    lo = hi = Q(0)
    for r in sorted(LOCAL):
        n = Q(LOCAL[r])
        take = min(r * n, rem)
        rem -= take
        c = child_cost(r, M, a)
        lo += (n - take / r) * c[0]
        hi += (n - take / r) * c[1]
    k = (q['idle_mass'] + Q(mu)) / R
    c = child_cost(R, M, a)
    return (lo + k * c[0]) / w, (hi + k * c[1]) / w


def ceiling(mu, q, w):
    """Certified bracket [a_lo, a_hi] of the ceiling after removing `mu`."""
    lo, hi = Q(0), Q(1, 20)
    if relax_eliminated(hi, mu, q, w)[0] <= 1:
        fail('search window too small')
    if relax_eliminated(lo, mu, q, w)[1] >= 1:
        fail('relaxation has no positive saving at this elimination')
    while hi - lo > GRID:
        mid = Q(int((lo + hi) / 2 / GRID)) * GRID
        if mid <= lo:
            mid = lo + GRID
        v = relax_eliminated(mid, mu, q, w)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            fail('enclosure too wide to separate a grid point')
    return lo, hi


def phi_for(a, q, w):
    """Smallest eliminated mass with relaxation moment <= 1, or None."""
    if relax_eliminated(a, Q(0), q, w)[1] <= 1:
        return Q(0)
    if relax_eliminated(a, q['local_mass'], q, w)[0] > 1:
        return None
    lo, hi = Q(0), q['local_mass']
    while hi - lo > TOL:
        mid = (lo + hi) / 2
        if relax_eliminated(a, mid, q, w)[1] <= 1:
            hi = mid
        else:
            lo = mid
    return hi


def decimal(x, places=12):
    """Fixed-point decimal string, truncated, for reporting only."""
    scale = 10 ** places
    n = int(Q(x) * scale)
    sign = '-' if n < 0 else ''
    n = abs(n)
    whole, frac = divmod(n, scale)
    return '%s%d.%0*d' % (sign, whole, places, frac)


def main():
    q, w = context()
    # 0. The inherited quantities.
    if q['local_mass'] != 5586 or q['idle_mass'] != 1646:
        fail('inherited mass budget changed')
    if q['R'] != 51:
        fail('inherited idle rank cap changed')

    # 1. phi = 0 reproduces the predecessor's certified ceiling exactly.
    lo0, hi0 = ceiling(Q(0), q, w)
    if not (lo0 <= Q('0.001690054109089') and Q('0.001690054109088') <= hi0):
        fail('predecessor ceiling not reproduced')
    if hi0 - lo0 > GRID:
        fail('predecessor ceiling bracket too wide')

    # 2. Whole-child breakpoints: the physical curve.
    order = sorted(LOCAL)
    cum, breaks = 0, []
    for r in order:
        cum += r * LOCAL[r]
        breaks.append((r, cum))
    points = [(0, 'none')] + [(mass, 'through rank %d' % r) for r, mass in breaks]
    table = []
    for mu, label in points:
        blo, bhi = ceiling(Q(mu), q, w)
        if bhi - blo > GRID:
            fail('breakpoint bracket too wide')
        table.append((mu, label, blo, bhi))

    # 3. Strict monotonicity across the whole-child curve.
    for (m0, _, _, h0), (m1, _, l1, _) in zip(table, table[1:]):
        if not (h0 < l1):
            fail('ceiling not strictly increasing at breakpoints %s -> %s' % (m0, m1))

    # 4. The lowest-rank-first rule is optimal: removing a unit of mass from a
    #    larger rank never beats removing it from a smaller one.  Check the
    #    per-unit saving ordering directly at several exponents.
    for a in (Q(1, 1000), Q(1, 500), Q(1, 100), Q(1, 20)):
        save = {}
        for r in order:
            save[r] = child_cost(r, M, a)[0] / r - child_cost(q['R'], M, a)[1] / q['R']
        ordered = [save[r] for r in order]
        if not all(x > 0 for x in ordered):
            fail('non-positive saving for r < R at a=%s' % a)
        if not all(x > y for x, y in zip(ordered, ordered[1:])):
            fail('saving ordering violated at a=%s' % a)

    # 5. Controls: a rank-reversed elimination at half the paid mass costs more
    #    than the lowest-rank-first elimination of the same mass.
    half = q['local_mass'] / 2
    def relax_reversed(a, mu):
        R = q['R']
        rem = Q(mu)
        lo = hi = Q(0)
        for r in sorted(LOCAL, reverse=True):
            n = Q(LOCAL[r])
            take = min(r * n, rem)
            rem -= take
            c = child_cost(r, M, a)
            lo += (n - take / r) * c[0]
            hi += (n - take / r) * c[1]
        k = (q['idle_mass'] + Q(mu)) / R
        c = child_cost(R, M, a)
        return (lo + k * c[0]) / w, (hi + k * c[1]) / w
    probe = Q('0.003')
    if not (relax_reversed(probe, half)[0] > relax_eliminated(probe, half, q, w)[1]):
        fail('rank-reversed control did not cost more')

    # 6. phi = 1 reproduces the pure-idle closed form.
    lo1, hi1 = ceiling(q['local_mass'], q, w)
    for a in (Q(0), Q(1, 1000), Q(1, 200)):
        beta = child_cost(q['R'], M, a)
        k = q['total_mass'] / q['R']
        want = (k * beta[0] / w, k * beta[1] / w)
        got = relax_eliminated(a, q['local_mass'], q, w)
        if not (got[0] >= want[0] and got[1] <= want[1]):
            fail('full-elimination moment is not the closed form at a=%s' % a)

    # 7. Targets: the two decision points plus a monotone sample.
    targets = [
        ('selected endpoint', Q(167546, 10 ** 8)),
        ('complex ceiling', Q('0.001690054109089')),
        ('bit primitive budget', Q('0.00173343')),
        ('round target 0.002', Q(1, 500)),
        ('planning target 1/99', Q(1, 99)),
    ]
    screen = []
    for name, a in targets:
        p = phi_for(a, q, w)
        screen.append((name, a, p))
    if screen[0][2] != 0:
        fail('selected endpoint should need no elimination')
    if screen[2][2] is None or not (0 < screen[2][2] < q['local_mass'] / 2):
        fail('bit-budget crossing not in the first half of the paid mass')
    if screen[3][2] is None or not (0 < screen[3][2] < q['local_mass']):
        fail('round-target crossing outside the paid mass')
    if screen[4][2] is None or not (Q(9, 10) * q['local_mass'] < screen[4][2] < q['local_mass']):
        fail('1/99 crossing not in the last tenth of the paid mass')
    # phi is non-decreasing in the target.
    phis = [p for _, _, p in screen if p is not None]
    if not all(x < y for x, y in zip(phis, phis[1:])):
        fail('phi not increasing across the targets')

    # 8. An unreachable control target above the full-elimination ceiling.
    above = hi1 + Q(1, 1000)
    if phi_for(above, q, w) is not None:
        fail('unreachable control target reported as reachable')

    # 9. Two independent invariants of the reported fractions.
    if q['total_mass'] != q['local_mass'] + q['idle_mass']:
        fail('mass budget does not add up')
    if sum(LOCAL.values()) != 3494:
        fail('paid child count changed')

    lines = ['PASS_COMPLEX_PAID_MASS_BUDGET']
    lines.append('inherited ceiling=%s..%s' % (decimal(lo0), decimal(hi0)))
    lines.append('full-elimination ceiling=%s..%s' % (decimal(lo1), decimal(hi1)))
    lines.append('whole-child curve (removed mass, ceiling):')
    for mu, label, blo, bhi in table:
        lines.append('  %5d  phi=%s  %s..%s  %s'
                     % (mu, decimal(Q(mu, 5586), 9), decimal(blo), decimal(bhi), label))
    lines.append('screens (target, minimum eliminated mass fraction):')
    for name, a, p in screen:
        lines.append('  %-24s a=%s  phi=%s  mass=%s'
                     % (name, decimal(a, 12), 'unreachable' if p is None
                        else decimal(p / q['local_mass'], 9),
                        'unreachable' if p is None else decimal(p, 9)))
    lines.append('controls=9 no_new_kappa')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
