#!/usr/bin/env python3
"""Check necessary native tariffs from equal-column cuts.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path


def profile(value):
    if type(value) is not dict:
        raise ValueError("a profile must be an object")
    result = {}
    for key, count in value.items():
        if type(key) is not str or not key.isdecimal() or str(int(key)) != key:
            raise ValueError("ranks must be canonical nonnegative integer strings")
        if type(count) is not int or count < 0:
            raise ValueError("counts must be nonnegative integers")
        if int(key) and count:
            result[int(key)] = count
    return result


def tariff(counts, k):
    return sum((count * (1 - Fraction(1, 1 << (k * rank)))
                for rank, count in counts.items()), Fraction(0))


def audit(data):
    paid, targets = profile(data['paid']), profile(data['targets'])
    width = data.get('width')
    if width is not None and (type(width) is not int or width < 1):
        raise ValueError("width must be a positive integer")
    coefficients = {0: sum(paid.values()) - sum(targets.values())}
    for rank in paid.keys() | targets.keys():
        coefficients[rank] = targets.get(rank, 0) - paid.get(rank, 0)
    coefficients = {r: a for r, a in sorted(coefficients.items()) if a}
    result = {
        'schema': 'native-equality-cut/v1',
        'scope': 'necessary conditions; no native admission or kappa claim',
        'width': width,
        'polynomial': {str(r): a for r, a in coefficients.items()},
        'checks': [],
    }
    if not coefficients:
        result.update(status='PASS_NECESSARY_EQUALITY_CUTS', tail='identically zero')
        return result
    first = next(iter(coefficients))
    lead = coefficients[first]
    remainder = sum(abs(a) for r, a in coefficients.items() if r > first)
    cutoff = 1
    while abs(lead) * (1 << cutoff) <= remainder:
        cutoff += 1
    result['tail'] = {
        'first_degree': first, 'leading_coefficient': lead,
        'remaining_absolute_sum': remainder, 'certified_from_k': cutoff,
        'strict_sign': 1 if lead > 0 else -1,
    }
    limit = cutoff if width is None else min(cutoff, width // 2)
    for k in range(1, limit + 1):
        p, t = tariff(paid, k), tariff(targets, k)
        result['checks'].append({'k': k, 'paid': str(p), 'targets': str(t),
                                 'paid_minus_targets': str(p - t)})
        if p < t:
            result.update(status='FAIL_NECESSARY_EQUALITY_CUTS', witness={
                'k': k, 'minimum_width': 2 * k,
                'normalized_rank_deficit': str(t - p),
                'ideal_endpoint_operator_error_lower_bound': 1,
            })
            return result
    result['status'] = ('PASS_NECESSARY_EQUALITY_CUTS' if limit
                        else 'NO_EQUALITY_CUT_AT_THIS_WIDTH')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('invoice', type=Path)
    args = parser.parse_args()
    try:
        result = audit(json.loads(args.invoice.read_text(encoding='utf-8')))
    except (KeyError, TypeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result['status'] == 'FAIL_NECESSARY_EQUALITY_CUTS' else 0


if __name__ == '__main__':
    raise SystemExit(main())
