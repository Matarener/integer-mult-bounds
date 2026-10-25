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
PACKAGE = HERE.parent / 'kappa-next-regime'
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


def moment(profile, a, w):
    lo = hi = F(0)
    terms = [(int(r), F(n)) for r, n in profile.items()]
    terms.append((1, F(32*64**2*sum(profile.values()), 10**16)))
    for r, n in terms:
        l, u = log_box(F(64, r))
        p, q = exp_box(a*l, a*u)
        lo += n*r*p
        hi += n*r*q
    return lo/(64*w), hi/(64*w)


def decimal(x):
    with localcontext() as c:
        c.prec = 40
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def main():
    claim = json.loads((PACKAGE/'CLAIM.json').read_text())
    invoice = json.loads((PACKAGE/'COMPLETE-WORD-INVOICE.json').read_text())
    profile = claim['profile']
    need(profile == invoice['profile'], 'claim/invoice profile equality')
    need(sum(profile.values()) == claim['paid_requests'] == 988155, 'request count')
    mass = sum(int(r)*n for r, n in profile.items())
    need(mass == claim['rank_mass'] == 1977885, 'rank mass')
    need(64*invoice['W']-mass == claim['raw_deficit'] == 11235, 'raw deficit')
    lower, upper = F(claim['bit_root_lower']), F(claim['bit_root_upper'])
    need(lower == F(invoice['bit_lower']) and upper == F(invoice['bit_upper']), 'endpoints')
    need(upper-lower == F(1, 10**24), 'bracket width')
    lbox, ubox = moment(profile, lower, invoice['W']), moment(profile, upper, invoice['W'])
    need(lbox[1] < 1 < ubox[0], 'strict moment bracket')
    for fresh, retained in zip((lbox, ubox), invoice['second_engine_signs']):
        need(F(retained['lower']) <= fresh[0] <= fresh[1] <= F(retained['upper']), 'independent interval inside retained bounds')
    loss = F(1, 10**46)+F(1, 10**70)
    kappa = lower-loss
    target = F(claim['target']['displayed_endpoint'])
    need(F(claim['outer_loss']) == loss and F(claim['kappa']) == kappa, 'headline arithmetic')
    need(F(claim['kappa_decimal']) == kappa, 'headline decimal')
    need(F(claim['gain_over_target']) == kappa-target > 0, 'target gain')
    need(F(claim['packing_increment'])+F(claim['word_increment']) == lower-target, 'increment split')
    prefix = 2**90 * 49347**25 * 1113510**20
    chosen = invoice['coefficient_envelopes']['five_replica_block_upper_bound']
    need(prefix == int(chosen['prefix']) and prefix.bit_length() == 882, 'prefix integer')
    need(prefix.bit_length() <= chosen['charged_prefix_bits'] == 896, 'prefix charge')
    need(int(chosen['two_level_coefficient']).bit_length() == chosen['two_level_bits'] == 1803, 'two-level bit length')
    need(chosen['two_level_bits'] <= chosen['charged_two_level_bits'] == 1856, 'two-level charge')
    need(2*max(map(int, profile))**2 < 64**2, 'strict halving')
    need(F(claim['complex_root_lower']) > upper, 'claimed complex headroom only')
    result = dict(status='PASS_INDEPENDENT_INVOICE_ARITHMETIC',
        scope='Exact supplied-profile price and integer checks; no word, tariff applicability, complex operator or outer theorem admission.',
        lower_moment_minus_one=[decimal(x-1) for x in lbox],
        upper_moment_minus_one=[decimal(x-1) for x in ubox],
        exact_lower_moment_interval=[str(x) for x in lbox],
        exact_upper_moment_interval=[str(x) for x in ubox],
        gain_over_target=str(kappa-target), relative_gain_percent=decimal((kappa-target)/target*100))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
