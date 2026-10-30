#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the fixed PR5756 tail envelope with rational intervals.

Ali Romman with OpenAI Codex assistance. Compiler credit: Jacob Alan Sussman,
zxv and Cao Yifan. Invoice credit: Joel Pulikkan and the retained P104 chain.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(test, message):
    if not test:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source hash: ' + row['path'])


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    values = [x*y for x in a for y in b]
    return min(values), max(values)


def divide(a, b):
    need(b[0] > 0, 'positive denominator')
    return mul(a, (1/b[1], 1/b[0]))


@lru_cache(maxsize=16384)
def power(rank, exponent):
    integer = exponent.numerator // exponent.denominator
    fraction = exponent - integer
    factor = Q(rank)**integer
    return (factor, factor) if not fraction else mul((factor, factor), POWER(rank, fraction))


def log_series(x):
    need(1 <= x <= 2, 'normalized logarithm')
    z = (x-1)/(x+1)
    value = 2*sum(z**(2*j+1)/Q(2*j+1) for j in range(80))
    tail = 2*z**161/(161*(1-z*z))
    return value, value+tail


@lru_cache(maxsize=256)
def log_rank(rank):
    k = rank.bit_length()-1
    return add(mul((Q(k),)*2, log_series(Q(2))), log_series(Q(rank, 2**k)))


def moment(histogram, exponent):
    result = (Q(0), Q(0))
    for rank, count in histogram.items():
        result = add(result, mul((Q(count),)*2, power(rank, exponent)))
    return result


class Tails:
    def __init__(self, source):
        self.C = Q(source['strictification']['tested'])
        need(0 < self.C < Q(1, 2), 'saving interval')
        self.T = {int(r): n for r, n in source['targets'].items()}
        self.P = {int(r): n for r, n in source['paid'].items()}
        need(all(type(n) is int and n > 0 for h in (self.T, self.P) for n in h.values()),
             'positive integer counts')
        need(sum(self.T.values()) == source['productive_fields'] == 13390, 'complete target count')
        need(sum(self.P.values()) == source['paid_calls'] == 66852, 'complete paid count')
        need(sum(r*n for r,n in self.T.items())-sum(r*n for r,n in self.P.items()) == 760,
             'complete rank surplus')
        self.target = moment(self.T, 1-self.C)

    def gamma(self, c, u):
        return divide(moment(self.P, 1-self.C+u), mul(power(c, u), self.target))

    def derivative(self, c, u):
        total = (Q(0), Q(0))
        cl = log_rank(c)
        for r, n in self.P.items():
            rl = log_rank(r)
            logarithm = rl[0]-cl[1], rl[1]-cl[0]
            total = add(total, mul(mul((Q(n),)*2, power(r, 1-self.C+u)), logarithm))
        return divide(total, mul(power(c, u), self.target))

    def delta(self, c, b):
        n = Q(sum(self.T.values())*b)
        return divide((n, n), mul(power(c, self.C), self.target))


def root(function, left, right, rising, width=Q(1, 10**12)):
    """Retain strict opposite signs at both ends."""
    def sign(x):
        low, high = function(x)
        need(low > 0 or high < 0, 'unresolved root sign')
        return low > 0
    need(sign(left) != rising and sign(right) == rising, 'root bracket')
    while right-left > width:
        middle = (left+right)/2
        if sign(middle) == rising:
            right = middle
        else:
            left = middle
    return left, right


def minimum(tails, c):
    left, right = root(lambda u: tails.derivative(c,u), Q(0), Q(1), True)
    low = tails.gamma(c,left)[0] + tails.derivative(c,left)[0]*(right-left)
    high = tails.gamma(c,(left+right)/2)[1]
    need(low <= high, 'minimum enclosure')
    return (left, right), (low, high)


def display(interval):
    scale = 10**15
    lo = (interval[0]*scale).__floor__()
    hi = (interval[1]*scale).__ceil__()
    return {'lower': str(Q(lo,scale)), 'upper': str(Q(hi,scale))}


def arithmetic_controls():
    count = 0
    for base in range(1, 9):
        for denominator in range(1, 6):
            for numerator in range(-5, 11):
                low, high = power(base**denominator, Q(numerator,denominator))
                need(low <= Q(base)**numerator <= high, 'exact rational power control')
                count += 1
    with localcontext() as context:
        context.prec = 100
        def dec(q):
            return Decimal(q.numerator)/Decimal(q.denominator)
        for r in range(1, 81):
            low, high = power(r, Q(173,127))
            value = (Decimal(r).ln()*dec(Q(173,127))).exp()
            need(dec(low)-Decimal('1e-90') <= value <= dec(high)+Decimal('1e-90'),
                 'independent Decimal power control')
            low, high = log_rank(r)
            need(dec(low)-Decimal('1e-90') <= Decimal(r).ln() <= dec(high)+Decimal('1e-90'),
                 'independent Decimal logarithm control')
    return {'exact_powers': count, 'decimal_powers': 80, 'decimal_logs': 80}


def run():
    authenticate()
    global POWER
    sys.path.insert(0, str(ROOT/'scripts'))
    try:
        from evaluate_recursive_power import power_bounds
    finally:
        sys.path.pop(0)
    POWER = power_bounds
    source = json.loads((HERE/'inputs/RESULT.json').read_text())['complete_cost']
    tails = Tails(source)
    limit = power(2, Q(-1,32))
    m15, g15 = minimum(tails,15)
    m16, g16 = minimum(tails,16)
    need(g15[0] > limit[1], 'all offsets at cutoff15 fail')
    need(tails.delta(17,18)[0] > limit[1], 'all cutoffs at least17 fail')
    need(tails.delta(16,18)[0] > limit[1], 'all floors at least18 fail at cutoff16')
    need(tails.delta(16,17)[1] < g16[0] < g16[1] < limit[0], 'cutoff16 floor17 optimum')
    need(16**64 < 17**63, 'completion ordering capacity')
    def difference(u):
        gamma = tails.gamma(16,u)
        return gamma[0]-limit[1], gamma[1]-limit[0]
    lower = root(difference,Q(0),Q(1,7),False)
    upper = root(difference,Q(1,7),Q(1),True)
    decay = Q(125,128)
    need(tails.gamma(16,Q(1,7))[1] < decay and tails.delta(16,17)[1] < decay
         and decay**128 < Q(1,16), 'source passing point')
    need(tails.gamma(16,Q(1,5))[0] > decay, 'source offset failure')
    alpha = divide(moment(tails.P,1-tails.C),tails.target)
    need(alpha[1] < 1-Q(1,10**12), 'source reserve')
    need(tails.gamma(16,Q(1,5))[0] > limit[1], 'old offset fails for every permitted decay')
    alternate = Q(489,500)
    need(tails.gamma(16,Q(1,10))[0] > decay and tails.gamma(16,Q(1,10))[1] < alternate
         and tails.delta(16,17)[1] < alternate and alternate**128 < Q(1,16),
         'changed decay admits an offset rejected by the source decay')
    failures = 0
    for label, rank in (('targets','9'), ('paid','1')):
        bad = json.loads(json.dumps(source)); bad[label][rank] -= 1
        try:
            Tails(bad)
        except ValueError:
            failures += 1
        else:
            raise ValueError('missing count accepted')
    result = {'source_head':'a1b338e5d9271b541f2a198f4fc19cefc565feed',
              'tested_saving':str(tails.C),'paid_calls':66852,'target_count':13390,
              'unique_integer_cutoff_floor':[16,17], 'maximum_decay': display(limit),
              'cutoff15_minimum':display(g15), 'cutoff15_minimizer':display(m15),
              'cutoff17_completion_lower':display(tails.delta(17,18)),
              'floor18_completion_lower':display(tails.delta(16,18)),
              'offset_interval_lower_root':display(lower),'offset_interval_upper_root':display(upper),
              'best_offset':display(m16),'best_decay_infimum':display(g16),
              'completion_at_16_17':display(tails.delta(16,17)),
              'offset_one_fifth_gamma':display(tails.gamma(16,Q(1,5))),
              'controls':dict(arithmetic_controls(), missing_count_rejections=failures)}
    return result


if __name__ == '__main__':
    result = run()
    if '--emit' not in sys.argv:
        need(result == json.loads((HERE/'RESULT.json').read_text()), 'result receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
    if '--emit' not in sys.argv:
        print('PASS_P104_TAIL_FEASIBLE_ENVELOPE')
