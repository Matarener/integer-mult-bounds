#!/usr/bin/env python3
"""Screen a binary query frame and proposed target axis sets.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Passing these necessary cuts does not certify an operator word or a price.
"""
import argparse
from itertools import combinations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    rows = list(rows)
    pivot = 0
    for bit in range(max(rows, default=0).bit_length()-1, -1, -1):
        chosen = next((i for i in range(pivot, len(rows)) if rows[i] >> bit & 1), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        for i in range(pivot+1, len(rows)):
            if rows[i] >> bit & 1:
                rows[i] ^= rows[pivot]
        pivot += 1
    return pivot


def audit(candidate):
    n, us, vs = candidate['n'], candidate['u'], candidate['v']
    require(type(n) is int and n > 0, 'n must be a positive integer')
    require(len(us) == len(vs) and len(us) > n, 'A query frame needs L>n terms')
    require(all(type(x) is int and 0 < x < (1 << n) for x in us+vs), 'Invalid query vector')
    require(all((u & v).bit_count() % 2 == 0 for u, v in zip(us, vs)), 'Non-nilpotent query')
    total = [0]*n
    for u, v in zip(us, vs):
        for j in range(n):
            if u >> j & 1:
                total[j] ^= v
    require(total == [1 << i for i in range(n)], 'Query frame does not sum to identity')
    gram = [sum(((v & u).bit_count() % 2) << i for i, u in enumerate(us)) for v in vs]
    axes, singles, failures = [], [], []
    for axis in candidate['axes']:
        calls, outputs = axis['calls'], axis['outputs']
        idles = axis.get('idle_terms', 0)
        require(len(calls) == len(set(calls)) and len(outputs) == len(set(outputs)), 'Duplicate index')
        require(all(type(i) is int and 0 <= i < len(us) for i in calls), 'Invalid call index')
        require(all(type(i) is int and 0 <= i < n for i in outputs), 'Invalid output index')
        require(type(idles) is int and idles >= 0, 'Invalid idle count')
        require(all(axis['name'] != a['name'] for a in axes), 'Duplicate axis name')
        block = [sum(((gram[i] >> j) & 1) << t for t, j in enumerate(calls)) for i in calls]
        block_rank = rank(block)
        capacity = 2*len(calls)+idles-block_rank
        deficit = 2*len(calls)+idles-len(outputs)
        singles.append({'axis': axis['name'], 'target_count': len(outputs),
                        'capacity': capacity, 'gram_rank': block_rank})
        if len(outputs) > capacity:
            failures.append({'kind': 'axis_capacity', 'axis': axis['name'],
                             'requested': len(outputs), 'maximum': capacity})
        axes.append({**axis, 'deficit': deficit})
    intersections = []
    for a, b in combinations(axes, 2):
        block = [sum(((gram[i] >> j) & 1) << t for t, j in enumerate(b['calls']))
                 for i in a['calls']]
        demand = max(0, rank(block)-a['deficit']-b['deficit'])
        actual = len(set(a['outputs']) & set(b['outputs']))
        intersections.append({'axes': [a['name'], b['name']], 'required': demand, 'actual': actual})
        if actual < demand:
            failures.append({'kind': 'axis_intersection', 'axes': [a['name'], b['name']],
                             'requested': actual, 'minimum': demand})
    return {'status': 'REJECT_NECESSARY_CUT' if failures else 'PASS_NECESSARY_CUTS_ONLY',
            'n': n, 'query_count': len(us), 'query_surplus': len(us)-n,
            'single_axis': singles, 'intersections': intersections, 'failures': failures,
            'limits': 'Assumes compatible full projectors and independent target jobs. Does not construct them or price helpers, native maps, scalar work or compiler costs.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    args = parser.parse_args()
    result = audit(json.loads(args.candidate.read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(bool(result['failures']))
