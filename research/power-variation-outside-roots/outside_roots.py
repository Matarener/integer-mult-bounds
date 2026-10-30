#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Spend the generalized Descartes budget on exact roots outside 0 < t < 1.

The merged general-rank certificate (scripts/compare_power_variation.py, PR5788)
bounds all real zeros of F(t) = sum c_r r^t by the number V of sign changes in
the rank-ordered coefficients. It subtracts endpoint roots at t = 0, 1 and
counts interior brackets; any remaining budget gives `inconclusive`. Roots at
t < 0 or t > 1 also consume that budget. This module certifies them with exact
rational values at integer exponents and the exact asymptotic signs

    sign F(t) = sign(c_min) as t -> -infinity,
    sign F(t) = sign(c_max) as t -> +infinity,

then runs the interior bracket count against the smaller remaining budget.
The shared script is imported unchanged. Proof: README.md.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
try:
    import compare_power_variation as V
    from compare_recursive_invoices import compare_invoices, load_invoice, require
finally:
    sys.path.pop(0)

MAX_REACH = 64


def exact_value(delta, k):
    """F(k) for an integer k, as an exact rational."""
    if k >= 0:
        return Q(sum(n * r**k for r, n in delta.items()))
    return sum((Q(n, r**-k) for r, n in delta.items()), Q(0))


def outside_witnesses(delta, endpoints, reach):
    """Disjoint certified roots in (-inf, 0) and (1, +inf).

    Each side is an ordered list of points with strict known signs: the
    asymptotic sign, the integers out to `reach`, and the adjacent endpoint
    when F is nonzero there. An exact zero at an integer point and each strict
    sign change between adjacent points certify one root. The open intervals
    and exact points are pairwise disjoint and avoid t = 0, 1.
    """
    ranks = list(delta)
    low, high = (1 if delta[ranks[0]] > 0 else -1), (1 if delta[ranks[-1]] > 0 else -1)
    left = [('-inf', low)] + [(-k, exact_value(delta, -k)) for k in range(reach, 0, -1)]
    right = [(k, exact_value(delta, k)) for k in range(2, reach + 1)] + [('+inf', high)]
    if not endpoints['0']:
        left.append((0, exact_value(delta, 0)))
    if not endpoints['1']:
        right.insert(0, (1, exact_value(delta, 1)))
    found = []
    for side in (left, right):
        previous = None
        for t, value in side:
            s = (value > 0) - (value < 0)
            if s == 0:
                found.append({'exact': str(t)})
                previous = None
                continue
            if previous is not None and previous[1] != s:
                found.append({'left': str(previous[0]), 'right': str(t)})
            previous = (t, s)
    return found


def classify(delta, bits=128, grid=64, reach=8):
    require(type(reach) is int and 1 <= reach <= MAX_REACH, 'reach must be an integer in1..64')
    require(type(bits) is int and 16 <= bits <= 256, 'bits must be an integer in16..256')
    require(type(grid) is int and 2 <= grid <= 256, 'grid must be an integer in2..256')
    delta = dict(sorted((int(r), n) for r, n in delta.items() if n))
    require(len(delta) <= 512, 'power comparison supports at most512 nonzero ranks')
    if not delta:
        return {'classification': 'equal', 'root_budget': 0, 'interior_roots': 0,
                'root_witnesses': [], 'outside_witnesses': []}
    signs = [1 if n > 0 else -1 for n in delta.values()]
    budget = sum(a != b for a, b in zip(signs, signs[1:]))
    endpoints = {str(t): V.endpoint_multiplicity(delta, t) for t in (0, 1)}
    outside = outside_witnesses(delta, endpoints, reach)
    remaining = budget - sum(endpoints.values()) - len(outside)
    require(remaining >= 0, 'outside and endpoint roots exceed the sign-variation budget')
    points = [Q(1, 2)] if not remaining else [Q(i, grid) for i in range(grid + 1)]
    values = [V.enclosure(delta, t, bits) for t in points]
    point_signs = [V.sign(v) for v in values]
    roots = []
    for i, t in enumerate(points):
        if 0 < t < 1 and point_signs[i] == 0:
            roots.append({'exact': V.witness(t, values[i])})
        if i and point_signs[i] in (-1, 1) and point_signs[i - 1] in (-1, 1):
            if point_signs[i] != point_signs[i - 1]:
                roots.append({'left': V.witness(points[i - 1], values[i - 1]),
                              'right': V.witness(t, values[i])})
    require(len(roots) <= remaining, 'root witnesses exceed the sign-variation budget')
    sample = next((V.witness(t, v) for t, v, s in zip(points, values, point_signs)
                   if 0 < t < 1 and s in (-1, 1)), None)
    complete = len(roots) == remaining and sample is not None
    classification = ('inconclusive' if not complete else 'crossing' if roots else
                      'uniformly_higher' if Q(sample['lower']) > 0 else 'uniformly_lower')
    return {'classification': classification, 'root_budget': budget,
            'endpoint_multiplicity_lower_bounds': endpoints,
            'outside_witnesses': outside, 'root_witnesses': roots,
            'interior_roots': len(roots) if complete else None,
            'interior_root_upper_bound': remaining,
            'all_interior_roots_simple': True if complete else None,
            'unspent_root_budget': remaining - len(roots), 'sample': sample,
            'grid': grid, 'bits': bits, 'reach': reach}


def compare(old, new, bits=128, grid=64, reach=8):
    source = compare_invoices(old, new)
    return {'schema': 'integer-mult-power-variation-outside/v1', 'contract': source['contract'],
            'quantity': source['quantity'], 'signed_net_delta': source['signed_net_delta'],
            'exponent_domain': '0 < t < 1',
            **classify(source['signed_net_delta'], bits, grid, reach),
            'scope': 'Declared invoice arithmetic only. No source, native, compiler or kappa admission.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old'); parser.add_argument('new')
    parser.add_argument('--bits', type=int, default=128)
    parser.add_argument('--grid', type=int, default=64)
    parser.add_argument('--reach', type=int, default=8)
    args = parser.parse_args()
    try:
        old, old_pin = load_invoice(args.old); new, new_pin = load_invoice(args.new)
        report = compare(old, new, args.bits, args.grid, args.reach)
        report['inputs'] = {'old': old_pin, 'new': new_pin}
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print('Power variation comparison failed: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
