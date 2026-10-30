#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check outside-domain root witnesses against an independent factored oracle.

Every fixture is F(t) = prod_i (q_i a_i^t - p_i) with prime bases a_i and
positive rational thresholds p_i/q_i. Its real roots are known in closed form,
t_i = log(p_i/q_i)/log(a_i), so the oracle needs no root finding. The oracle
uses exact integer tests for interior membership, integer roots and the sign at
t = 1/2; floating logarithms only separate distinct non-integer roots, and any
near-coincidence between different exact keys is excluded and counted.
"""
from fractions import Fraction as Q
from itertools import combinations_with_replacement
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import outside_roots as O
sys.path.pop(0)
V = O.V


def check(condition, message):
    """Fail closed under -O as well; assert statements would be stripped."""
    if not condition:
        raise SystemExit('FAIL ' + repr(message))

BASES = (2, 3, 5)
THRESHOLDS = tuple(Q(x) for x in ('1/3', '1/2', '3/4', '1', '4/3', '3/2', '2', '5/2',
                                  '3', '4', '9/2', '5', '7', '9', '25'))


def expand(factors):
    poly = {1: 1}
    for a, theta in factors:
        p, q = theta.numerator, theta.denominator
        out = {}
        for r, n in poly.items():
            out[r * a] = out.get(r * a, 0) + n * q
            out[r] = out.get(r, 0) - n * p
        poly = {r: n for r, n in out.items() if n}
    return poly


def integer_root(a, theta):
    """Return m when theta = a^m exactly, else None."""
    for m in range(-8, 9):
        if theta == Q(a)**m:
            return m
    return None


def truth(factors):
    """Interior root keys with multiplicities, and the sign at t = 1/2."""
    roots, sign_half = {}, 1
    for a, theta in factors:
        m = integer_root(a, theta)
        key = ('int', m) if m is not None else ('log', a, theta)
        roots[key] = roots.get(key, 0) + 1
        p, q = theta.numerator, theta.denominator
        sign_half *= (q * q * a > p * p) - (q * q * a < p * p)
    located = {k: (k[1] if k[0] == 'int' else math.log(k[2]) / math.log(k[1])) for k in roots}
    keys = sorted(located, key=located.get)
    ambiguous = any(abs(located[x] - located[y]) < 1e-9 for x, y in zip(keys, keys[1:]))
    interior = {k: n for k, n in roots.items() if 0 < located[k] < 1 and
                not (k[0] == 'int')}
    # Interior membership is exact: 0 < log(theta)/log(a) < 1 iff 1 < theta < a.
    for k in interior:
        check(1 < k[2] < k[1], '1 < k[2] < k[1]')
    return interior, located, sign_half, ambiguous


def consistent(report, factors):
    """True when a certificate agrees with the oracle; inconclusive is always sound."""
    interior, located, sign_half, _ = truth(factors)
    kind = report['classification']
    if kind == 'inconclusive':
        return True
    if any(n > 1 for n in interior.values()):
        return False
    if kind in ('uniformly_higher', 'uniformly_lower'):
        return not interior and sign_half == (1 if kind == 'uniformly_higher' else -1)
    if kind != 'crossing' or len(report['root_witnesses']) != len(interior):
        return False
    points = sorted(located[k] for k in interior)
    for witness, point in zip(report['root_witnesses'], points):
        if 'exact' in witness:
            if abs(float(Q(witness['exact']['t'])) - point) > 1e-12:
                return False
        elif not float(Q(witness['left']['t'])) < point < float(Q(witness['right']['t'])):
            return False
    return True


def fixtures():
    factors = [(a, theta) for a in BASES for theta in THRESHOLDS]
    for size in (1, 2, 3):
        for combo in combinations_with_replacement(factors, size):
            if size == 3 and len({a for a, _ in combo}) < 3:
                continue
            yield combo


def census(classify):
    stats = {'cases': 0, 'ambiguous': 0, 'old_certified': 0, 'new_certified': 0,
             'newly_settled': 0, 'false': 0, 'budget_errors': 0, 'regressions': 0,
             'outside_used': 0}
    for combo in fixtures():
        if truth(combo)[3]:
            stats['ambiguous'] += 1
            continue
        delta = expand(combo)
        stats['cases'] += 1
        old = V.classify(delta, grid=32)
        try:
            new = classify(delta, grid=32)
        except ValueError:
            stats['budget_errors'] += 1
            continue
        check(consistent(old, combo), ('predecessor certificate disagrees', combo))
        stats['false'] += not consistent(new, combo)
        stats['old_certified'] += old['classification'] != 'inconclusive'
        stats['new_certified'] += new['classification'] != 'inconclusive'
        stats['outside_used'] += bool(new.get('outside_witnesses'))
        stats['regressions'] += (old['classification'] != 'inconclusive' and
                                 new['classification'] != old['classification'])
        stats['newly_settled'] += (old['classification'] == 'inconclusive' and
                                   new['classification'] != 'inconclusive')
    return stats


def mutant(swap_asymptotes=False, keep_zero_endpoints=False):
    """A deliberately wrong copy of outside_witnesses for failure controls."""
    def witnesses(delta, endpoints, reach):
        ranks = list(delta)
        low, high = (1 if delta[ranks[0]] > 0 else -1), (1 if delta[ranks[-1]] > 0 else -1)
        if swap_asymptotes:
            low, high = high, low
        left = [('-inf', low)] + [(-k, O.exact_value(delta, -k)) for k in range(reach, 0, -1)]
        right = [(k, O.exact_value(delta, k)) for k in range(2, reach + 1)] + [('+inf', high)]
        if keep_zero_endpoints or not endpoints['0']:
            left.append((0, O.exact_value(delta, 0)))
        if keep_zero_endpoints or not endpoints['1']:
            right.insert(0, (1, O.exact_value(delta, 1)))
        found = []
        for side in (left, right):
            previous = None
            for t, value in side:
                s = (value > 0) - (value < 0)
                if s == 0:
                    found.append({'exact': str(t)}); previous = None; continue
                if previous is not None and previous[1] != s:
                    found.append({'left': str(previous[0]), 'right': str(t)})
                previous = (t, s)
        return found
    return witnesses


def main():
    for delta, expected, outside in [
            ({1: 4, 2: -8, 3: -1, 6: 2}, 'uniformly_lower', [{'exact': '-1'}, {'left': '1', 'right': '2'}]),
            ({1: 15, 2: -20, 3: -3, 6: 4}, 'uniformly_lower',
             [{'left': '-1', 'right': '0'}, {'left': '1', 'right': '2'}])]:
        check(V.classify(delta)['classification'] == 'inconclusive', "V.classify(delta)['classification'] == 'inconclusive'")
        report = O.classify(delta)
        check(report['classification'] == expected and report['outside_witnesses'] == outside, report)
        check(report['unspent_root_budget'] == 0, "report['unspent_root_budget'] == 0")
    print('PASS_MOTIVATING_FIXTURES 2 predecessor-inconclusive -> uniformly_lower')

    stats = census(O.classify)
    print('census', stats)
    check(stats['false'] == stats['budget_errors'] == stats['regressions'] == stats['ambiguous'] == 0, "stats['false'] == stats['budget_errors'] == stats['regressions'] == stats['ambiguous'] == 0")
    check(stats['newly_settled'] > 0, "stats['newly_settled'] > 0")
    print('PASS_FACTORED_ORACLE_CENSUS')

    original = O.outside_witnesses
    try:
        for name, options in (('swap_asymptotes', {'swap_asymptotes': True}),
                              ('count_zero_endpoints', {'keep_zero_endpoints': True})):
            O.outside_witnesses = mutant(**options)
            bad = census(O.classify)
            failures = {k: bad[k] for k in ('false', 'budget_errors', 'regressions')}
            check(sum(failures.values()) > 0, (name, bad))
            print('PASS_CONTROL_REJECTED', name, failures)
    finally:
        O.outside_witnesses = original
    print('PASS_POWER_VARIATION_OUTSIDE_ROOTS')


if __name__ == '__main__':
    main()
