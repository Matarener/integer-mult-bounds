#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify invoice order on closed exponent intervals with arbitrary ranks.

Use compare_power_polynomial.py for a complete common-base classification.
This tool returns a bounded cover and retains every unresolved interval.
Ali Romman with substantial OpenAI Codex assistance. Retain the signed-invoice
and integer-power engine credits. See recursive-interval-comparison.md.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import compare_invoices, load_invoice, require
    from evaluate_recursive_power import parse_exponent, power_bounds
finally:
    sys.path.pop(0)


def endpoint(text):
    return Q(text) if text in ('0', '1') else parse_exponent(text)


def log_bounds(rank, bits):
    """Bound log(rank) by an atanh series after binary range reduction."""
    require(type(rank) is int and 1 <= rank <= 10**9, 'invalid logarithm rank')
    require(type(bits) is int and 16 <= bits <= 256, 'bits must be in 16..256')
    scale = 1 << bits
    def series(z):
        total, power = Q(0), z
        count = bits // 3 + 2
        for j in range(count):
            total += 2 * power / (2 * j + 1)
            power *= z * z
        return total, total + 2 * power / ((2 * count + 1) * (1 - z * z))
    k = rank.bit_length() - 1
    a, b = series(Q(rank - 2**k, rank + 2**k))
    c, d = series(Q(1, 3))
    lower, upper = (a + k * c) * scale, (b + k * d) * scale
    return Q(lower.numerator // lower.denominator, scale), Q(-(-upper.numerator // upper.denominator), scale)


class Kernel:
    def __init__(self, delta, bits):
        self.delta = {int(r): c for r, c in delta.items()}
        self.bits = bits
        self.logs = {r: log_bounds(r, bits) for r in self.delta}
        self.power = lru_cache(maxsize=8192)(self._power)

    def _power(self, rank, exponent):
        if exponent in (0, 1):
            return (Q(rank**int(exponent)),) * 2
        return power_bounds(rank, exponent, self.bits)

    def direct(self, left, right):
        lo = hi = dlo = dhi = Q(0)
        for rank, count in self.delta.items():
            a = self.power(rank, left)[0]
            b = self.power(rank, right)[1]
            c, d = self.logs[rank]
            if count > 0:
                lo += count * a; hi += count * b
                dlo += count * a * c; dhi += count * b * d
            else:
                lo += count * b; hi += count * a
                dlo += count * b * d; dhi += count * a * c
        return (lo, hi), (dlo, dhi)

    def bounds(self, left, right):
        direct, derivative = self.direct(left, right)
        a, b = self.direct(left, left)[0]
        c, d = self.direct(right, right)[0]
        u, v = derivative
        width = right - left
        # Integrate the derivative enclosure from each endpoint.
        lower = max(direct[0], a + min(0, u * width), c - max(0, v * width))
        upper = min(direct[1], b + max(0, v * width), d - min(0, u * width))
        return (lower, upper), derivative, (a, b), (c, d)


def cover(old, new, left=Q(0), right=Q(1), bits=128, max_boxes=255, max_depth=24):
    invoice = compare_invoices(old, new)
    require(isinstance(left, Q) and isinstance(right, Q) and 0 <= left < right <= 1,
            'need rational 0 <= left < right <= 1')
    require(type(bits) is int and 16 <= bits <= 256, 'bits must be in 16..256')
    require(type(max_boxes) is int and 1 <= max_boxes <= 2047, 'max_boxes must be in 1..2047')
    require(type(max_depth) is int and 0 <= max_depth <= 40, 'max_depth must be in 0..40')
    require(len(invoice['signed_net_delta']) <= 64, 'at most 64 nonzero ranks are supported')
    engine = Kernel(invoice['signed_net_delta'], bits)
    pending, result, evaluated, allocated = [(left, right, 0)], [], 0, 1
    pair = lambda values: {'lower': str(values[0]), 'upper': str(values[1])}
    while pending:
        a, b, depth = pending.pop()
        values, derivative, va, vb = engine.bounds(a, b)
        evaluated += 1
        state = ('new_cost_lower' if values[1] < 0 else 'new_cost_higher' if values[0] > 0
                 else 'equal' if values == (0, 0) else None)
        if state is None and depth < max_depth and allocated + 2 <= max_boxes:
            middle = (a + b) / 2
            pending += [(middle, b, depth + 1), (a, middle, depth + 1)]
            allocated += 2
            continue
        if state is None:
            crosses = (va[1] < 0 and vb[0] > 0) or (va[0] > 0 and vb[1] < 0)
            monotone = derivative[0] > 0 or derivative[1] < 0
            state = 'single_crossing' if crosses and monotone else 'unresolved'
        result.append({'left': str(a), 'right': str(b), 'classification': state,
                       'difference': pair(values), 'derivative': pair(derivative),
                       'left_value': pair(va), 'right_value': pair(vb)})
    result.sort(key=lambda cell: Q(cell['left']))
    return {'schema': 'integer-mult-recursive-interval-cover/v1', 'contract': invoice['contract'],
            'quantity': invoice['quantity'], 'signed_net_delta': invoice['signed_net_delta'],
            'domain': [str(left), str(right)], 'bits': bits, 'evaluated_boxes': evaluated,
            'limits': {'max_boxes': max_boxes, 'max_depth': max_depth}, 'cells': result,
            'resolved_everywhere': all(c['classification'] != 'unresolved' for c in result),
            'scope': 'Exact declared-invoice arithmetic. Closed cells cover the whole requested domain. '
                     'A single_crossing cell has exactly one root in its interior. Unresolved cells '
                     'can contain any number of roots. No source, physical, compiler or kappa admission.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old'); parser.add_argument('new')
    parser.add_argument('--left', default='0'); parser.add_argument('--right', default='1')
    parser.add_argument('--bits', type=int, default=128)
    parser.add_argument('--max-boxes', type=int, default=255)
    parser.add_argument('--max-depth', type=int, default=24)
    args = parser.parse_args(argv)
    try:
        old, a = load_invoice(args.old); new, b = load_invoice(args.new)
        result = cover(old, new, endpoint(args.left), endpoint(args.right), args.bits,
                       args.max_boxes, args.max_depth)
        result['inputs'] = {'old': a, 'new': b}
    except (OSError, ValueError, TypeError, RecursionError, ZeroDivisionError) as exc:
        print(json.dumps({'status': 'INVALID_INTERVAL_COMPARISON', 'error': str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
