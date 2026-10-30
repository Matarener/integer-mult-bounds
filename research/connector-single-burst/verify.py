#!/usr/bin/env python3
"""Check complete coverage and literal XOR proofs, without a search solver.

Prepared for theon199 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('burst_algebra', PACKAGE/'algebra.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def reject(function, label):
    try:
        function()
    except ValueError:
        return label
    raise ValueError('Negative control accepted: '+label)


def authenticate(raw, expected):
    a.require(hashlib.sha256(raw).hexdigest() == expected, 'Source digest mismatch')


def coverage(records):
    wanted = [(list(order), gap) for order in itertools.permutations(range(6)) for gap in range(7)]
    a.require([(r['order'], r['gap']) for r in records] == wanted, 'Incomplete/reordered coverage')


def check_positive(calls, data):
    order, gaps, matrices = data['order'], data['gaps'], data['matrices']
    a.require(sorted(order) == list(range(6)) and len(gaps) == len(matrices) == 2, 'Positive inventory')
    a.require(0 <= gaps[0] < gaps[1] <= 6, 'Positive gap positions')
    extra = list(calls[:6])
    indices = []
    for gap in range(7):
        if gap in gaps:
            matrix = matrices[gaps.index(gap)]
            a.require(len(matrix) == 8 and all(type(x) is int and 0 <= x < 256 for x in matrix), 'Positive matrix encoding')
            indices.append(len(extra))
            extra.append({'stage': 3, 'p': list(a.ZERO), 'r': matrix})
        if gap < 6:
            indices.append(order[gap])
    wanted = a.expected(calls)
    a.require(a.replay(extra, indices) == (wanted, wanted), 'Two-burst full identity')
    # Realize each burst by four rank-one square-zero maps, then replay all 14 calls.
    query_groups = data['rank_one_queries']
    a.require(len(query_groups) == 2, 'Query group inventory')
    extra = list(calls[:6])
    indices = []
    for gap in range(7):
        if gap in gaps:
            k = gaps.index(gap)
            a.require(len(query_groups[k]) == 4, 'Four queries per burst')
            total = a.ZERO
            for query in query_groups[k]:
                a.require(len(query) == 8 and all(type(x) is int and 0 <= x < 256 for x in query), 'Query encoding')
                a.require(a.rank(query) == 1 and a.multiply(query,query) == a.ZERO, 'Rank-one square-zero query')
                total = a.add(total,query)
                indices.append(len(extra))
                extra.append({'stage':3, 'p':list(a.ZERO), 'r':query})
            a.require(total == tuple(matrices[k]), 'Burst decomposition')
        if gap < 6:
            indices.append(order[gap])
    a.require(a.replay(extra,indices) == (wanted,wanted), 'Emitted fourteen-call identity')
    return {'rank_one_square_zero_queries': 8, 'occupied_gaps': 2,
            'full_calls': 6, 'fields': 8,
            'ranks': [a.rank(m) for m in matrices],
            'square_ranks': [a.rank(a.multiply(m,m)) for m in matrices]}


def main():
    source = (PACKAGE/'SOURCE-WORD.json').read_bytes()
    pins = json.loads((PACKAGE/'SOURCES.json').read_text())
    authenticate(source, pins['source']['sha256'])
    calls = a.check_source(json.loads(source))
    tariff_bytes = (PACKAGE/'P104-TARIFF-SOURCE.json').read_bytes()
    authenticate(tariff_bytes, pins['tariff']['sha256'])
    tariff = json.loads(tariff_bytes)['local']
    profile = {int(r): -6*c for r,c in tariff['paid'].items()}
    for r,c in tariff['helpers'].items():
        profile[int(r)] = profile.get(int(r),0) + 6*c
    for r,c in ((25,208),(9,624),(1,-832)):
        profile[r] = profile.get(r,0) + c
    profile = {r:c for r,c in profile.items() if c}
    linear = sum(r*c for r,c in profile.items())
    a.require(linear == -336, 'Optimistic complete linear margin')
    a.require(min(r for r,c in profile.items() if c>0) == 8 and
              max(r for r,c in profile.items() if c<0) == 7, 'All-concave price separation')
    data = json.loads((PACKAGE/'CERTIFICATES.json').read_text())
    a.require(data['schema'] == 1, 'Certificate schema')
    records = data['records']
    coverage(records)
    maximum_rows = maximum_degree = 0
    for record in records:
        columns, target = a.gap_problem(calls, record['order'], record['gap'])
        a.check_dual(columns, target, record['xor_rows'])
        maximum_rows = max(maximum_rows, len(record['xor_rows']))
        maximum_degree = max(maximum_degree, *(sum(a.EXPONENTS[r//64]) for r in record['xor_rows']))
    positive = check_positive(calls, data['two_burst'])
    first = records[0]
    columns, target = a.gap_problem(calls, first['order'], first['gap'])
    bad_rows = list(first['xor_rows'])
    remove = next(i for i,r in enumerate(bad_rows) if a.equation(columns,target,r) != (0,0))
    del bad_rows[remove]
    broken = json.loads(json.dumps(data['two_burst']))
    broken['matrices'][0][0] ^= 1
    deleted = json.loads(source)
    deleted['calls'][6]['r'] = [0]*8
    controls = [
        reject(lambda: authenticate(source+b' ', pins['source']['sha256']), 'source byte mutation'),
        reject(lambda: coverage(records[:-1]), 'missing order/gap'),
        reject(lambda: a.check_dual(columns,target,bad_rows), 'deleted dual term'),
        reject(lambda: a.check_dual(columns,target,[1728]), 'out-of-domain coefficient'),
        reject(lambda: check_positive(calls,broken), 'damaged two-burst identity'),
        reject(lambda: a.check_source(deleted), 'deleted original query'),
    ]
    # Dropping a thin map can preserve the pure stage word; the e part must reject.
    changed = json.loads(source)
    changed['calls'][6]['r'] = [0]*8
    base, eps = a.replay(changed['calls'],changed['order'])
    a.require(base == a.expected(calls) and eps != base, 'Full e-coefficient control')
    result = {'status': 'PASS_SINGLE_BURST_OBSTRUCTION', 'full_orders': 720,
              'gaps_per_order': 7, 'dual_certificates': len(records),
              'field': 'every characteristic-two field, constant connector matrices',
              'max_dual_rows': maximum_rows, 'max_dual_stage_degree': maximum_degree,
              'two_burst_schedule': positive, 'negative_controls': controls,
              'optimistic_P104_price': {'signed_profile': {str(r):c for r,c in sorted(profile.items())}, 'linear_margin': linear, 'all_concave_moments_rejected': True},
              'pure_stage_only_false_positive_rejected': True,
              'new_kappa': False}
    if '--write-result' in sys.argv:
        (PACKAGE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        a.require(result == json.loads((PACKAGE/'RESULT.json').read_text()), 'Result mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
