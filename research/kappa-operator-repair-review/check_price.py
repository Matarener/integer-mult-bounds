#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact arithmetic check of the supplied invoice, not its derivation.

Uses positive atanh and exponential series with explicit geometric tail bounds.
No submitted price implementation is imported. Substantial OpenAI assistance.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / 'kappa-operator-repair'
Q = 10**65


def need(ok, message):
    if not ok:
        raise ValueError(message)


def down(x):
    return F(x.numerator * Q // x.denominator, Q)


def up(x):
    return -down(-x)


def log_box(x):
    need(x >= 1, 'positive log domain')
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def series(z):
        total, power = F(0), z
        for j in range(80):
            total += 2 * power / (2*j+1)
            power *= z*z
        # Remaining denominators are at least 161.
        tail = 2 * power / (161 * (1-z*z))
        return total, total + tail

    a, b = series((x-1)/(x+1))
    c, d = series(F(1, 3))
    return down(a+k*c), up(b+k*d)


def exp_box(lo, hi):
    need(0 <= lo <= hi < 1, 'exp tail domain')

    def series(x):
        total = term = F(1)
        for j in range(1, 31):
            term = term*x/j
            total += term
        first = term*x/31
        # Every ratio after the first omitted term is <= x/32.
        return total, total + first/(1-x/32)

    return down(series(lo)[0]), up(series(hi)[1])


def moment(profile, a, m, w):
    lo = hi = F(0)
    for r, n in profile.items():
        r = int(r)
        l, u = log_box(F(m, r))
        p, q = exp_box(a*l, a*u)
        lo += n*r*p
        hi += n*r*q
    return lo/(m*w), hi/(m*w)


def main():
    claim = json.loads((PACKAGE/'late-staged-composition/CLAIM.json').read_text())
    supplier = claim['complex_supplier']
    profile = supplier['profile']
    lower, upper = F(supplier['lower']), F(supplier['upper'])
    need(upper-lower == F(1,10**24), 'exact bracket width')
    need(sum(int(r)*n for r,n in profile.items()) == 23431680, 'rank mass')
    lo, hi = moment(profile, lower, 73, 322560), moment(profile, upper, 73, 322560)
    need(lo[1] < 1 < hi[0], 'independent strict complex root bracket')
    loss = F(1,10**46)+F(1,10**70)
    previous = F(supplier['previous_valid_lower'])
    kappa = claim['conditional_kappa']
    need(lower < F(claim['bit_supplier']['lower']), 'complex binding')
    need(lower < F(claim['bit_supplier']['inherited_outer_replay_uses_sufficient_bit_lower']), 'sufficient outer BIT endpoint')
    need(F(kappa['value']) == lower-loss == F(kappa['decimal']), 'outer headline')
    need(F(kappa['gain_over_previous_valid']) == lower-previous, 'gain between equal-loss conditional headlines')
    need(lower-loss < F('.001736738651088946052684') < F('.001745'), 'historical benchmark and target remain unmet')
    print(json.dumps(dict(status='PASS_INDEPENDENT_REPAIRED_COMPLEX_ARITHMETIC',
        lower_moment_interval=list(map(str,lo)), upper_moment_interval=list(map(str,hi)),
        conditional_kappa=str(lower-loss), gain_over_equal_loss_previous=str(lower-previous),
        profile_mass=23431680,
        scope='Exact supplied-profile price and comparison arithmetic; does not prove native interfaces, retained BIT, or all-size outer hypotheses.'),indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
