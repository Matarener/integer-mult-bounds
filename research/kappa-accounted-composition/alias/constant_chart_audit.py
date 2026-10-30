#!/usr/bin/env python3
"""Independent exact audit of the selected-register alias controller.

This file has no native-word dependencies. It checks a constant-owner active
channel with K=1,L=13, retaining all original data and cache input columns.
It is not a physical construction or a productive-cache credit certificate.
Apache-2.0; substantial OpenAI assistance.
"""
from fractions import Fraction as Q
from math import gcd, lcm
from pathlib import Path
import argparse
import hashlib
import json


def rref(rows):
    a = [[Q(x) for x in row] for row in rows]
    if not a:
        return a, []
    pivots = []
    for col in range(len(a[0])):
        k = len(pivots)
        j = next((j for j in range(k, len(a)) if a[j][col]), None)
        if j is None:
            continue
        a[k], a[j] = a[j], a[k]
        q = a[k][col]
        a[k] = [x/q for x in a[k]]
        for j in range(len(a)):
            if j != k and a[j][col]:
                q = a[j][col]
                a[j] = [x-q*y for x, y in zip(a[j], a[k])]
        pivots.append(col)
        if len(pivots) == len(a):
            break
    return a, pivots


def rank(rows):
    return len(rref(rows)[1])


def nullspace(rows):
    a, pivots = rref(rows)
    n = len(rows[0])
    out = []
    for free in range(n):
        if free in pivots:
            continue
        v = [Q(0)]*n
        v[free] = Q(1)
        for j, p in enumerate(pivots):
            v[p] = -a[j][free]
        denominator = lcm(*(x.denominator for x in v))
        v = [int(x*denominator) for x in v]
        divisor = gcd(*v)
        out.append([x//divisor for x in v])
    return out


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def audit(p):
    n = 5*p+1
    identity = [[int(i == j) for j in range(n)] for i in range(n)]
    s = [row[:] for row in identity]
    cache = 4*p
    schedule = []

    def add(target, source, q):
        s[target] = [x+q*y for x, y in zip(s[target], s[source])]

    def signed_swap(a, b):
        add(a, b, 1)
        add(b, a, -1)
        add(a, b, 1)

    def forward(pair):
        nonlocal cache
        a, b, c, e = range(4*pair, 4*pair+4)
        # Literal H shear: H=[[-12,-1],[143,12]].
        add(c, a, -12)
        add(c, b, -1)
        add(e, a, 143)
        add(e, b, 12)
        # Form v, translate U by d-v, then exchange raw A and P.
        add(b, a, 13)
        add(a, cache, 1)
        add(a, b, -1)
        signed_swap(b, cache)
        s[cache] = [-x for x in s[cache]]
        schedule.append(['F', pair, cache-4*p])
        cache += 1

    def backward(pair):
        a, b, c, e = range(4*pair, 4*pair+4)
        # The native prefix normalizes b to the Y frame and returns it.
        add(e, c, 13)
        signed_swap(b, e)
        add(e, c, -13)
        # Literal negative H shear after the prefix.
        add(a, c, 12)
        add(a, e, 1)
        add(b, c, -143)
        add(b, e, -12)
        schedule.append(['B', pair])

    def bridge(source, target, q):
        for k in (0, 1):
            add(4*target+k, 4*source+k, q)
        for k in (2, 3):
            add(4*source+k, 4*target+k, -q)
        schedule.append(['bridge', source, target, q])

    forward(0)
    backward(0)
    for pair in range(1, p):
        bridge(pair, pair-1, 1)
        forward(pair-1)
        bridge(pair, pair-1, -1)
        backward(pair)
    forward(p-1)
    for pair in reversed(range(p-1)):
        bridge(pair, pair+1, 1)
    for pair in range(p):
        for k in (0, 1):
            a, b = 4*pair+k, 4*pair+k+2
            s[a], s[b] = s[b], [-x for x in s[a]]
    assert cache == n
    observations, errors = [], []
    for pair in range(p):
        observations += [s[4*pair+1], s[4*pair+3], s[4*pair+2]]
        for k in (0, 2):
            errors.append([x-y for x, y in zip(s[4*pair+k], identity[4*pair+k])])
    observations += s[4*p:]
    witnesses = []
    for v in nullspace(observations):
        e = [dot(row, v) for row in errors]
        if any(e):
            assert not any(dot(row, v) for row in observations)
            witnesses.append({'initial_state': v, 'ordinary_errors': e})
    full_rank = rank(s)
    observed = rank(observations)
    gap = rank(observations+errors)-observed
    assert full_rank == n and gap == p-1
    assert bool(witnesses) == bool(gap)
    return {
        'pairs': p, 'dimension': n, 'whole_matrix': s,
        'whole_rank': full_rank, 'all_initial_columns_retained': True,
        'input_order': [f'{bank}{pair}_{kind}' for pair in range(p)
                        for bank, kind in [('X','U'),('X','A'),('Y','U'),('Y','A')]]
                       +[f'd{j}' for j in range(p+1)],
        'schedule': schedule,
        'observations': 'All final selected A, all F caches, and all completed ordinary Y.',
        'observation_rank': observed, 'ordinary_error_gap_per_channel': gap,
        'ordinary_error_gap_eight_channels': 8*gap,
        'zero_observation_nonzero_error_witnesses': witnesses,
        'max_abs_endpoint_coefficient': max(abs(x) for row in s for x in row),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).with_name('CONSTANT-CHART-AUDIT.json'))
    args = parser.parse_args()
    result = {
        'schema': 'independent-alias-constant-chart/1',
        'status': 'PASS_EXACT_INVERTIBILITY_AND_SCOPED_OBSERVER_GAP',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cases': [audit(p) for p in range(1,6)],
        'scope': 'Exact constant-owner scalar active-channel model K=1,L=13. Native phase maps, changing owner charts, cache restoration and global output-credit assignment are not established by this receipt.',
        'new_kappa_claimed': False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])
    for case in result['cases']:
        print('p',case['pairs'],'rank',case['whole_rank'],'gap',case['ordinary_error_gap_per_channel'])


if __name__ == '__main__':
    main()
