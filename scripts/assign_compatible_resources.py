#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct a minimum-cost injective assignment or a Hall shortage witness.

Classical Hungarian primal-dual algorithm and Hall's theorem. Prepared for
Ali Romman with substantial OpenAI Codex assistance.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


def read(path):
    with Path(path).open('rb') as f: raw = f.read(1024**2 + 1)
    require(len(raw) <= 1024**2, 'Input exceeds 1 MiB')
    return json.loads(raw, object_pairs_hook=_pairs, parse_int=_integer,
                      parse_float=_not_integer, parse_constant=_not_integer), sha256(raw).hexdigest()


def validate(value):
    require(type(value) is dict and value.keys() == {'schema', 'costs'}
            and value['schema'] == 'compatible-assignment/v1', 'Invalid assignment problem')
    costs = value['costs']
    require(type(costs) is list and 1 <= len(costs) <= 128, 'Use 1..128 required consumers')
    require(type(costs[0]) is list and len(costs[0]) <= 256, 'At most 256 resources')
    m = len(costs[0])
    for row in costs:
        require(type(row) is list and len(row) == m, 'Cost matrix must be rectangular')
        require(all(c is None or type(c) is int and 0 <= c <= 10**12 for c in row),
                'Costs must be null or integers in 0..10^12')
    return costs


def shortage(costs, rows):
    neighbors = sorted({j for i in rows for j, c in enumerate(costs[i]) if c is not None})
    return {'schema': 'compatible-assignment-certificate/v1', 'status': 'infeasible',
            'rows': sorted(rows), 'neighbors': neighbors}


def assign(value):
    costs = validate(value); n, m = len(costs), len(costs[0])
    if n > m:
        result = shortage(costs, range(n)); verify(value, result); return result
    u, v, p, way = [0]*(n+1), [0]*(m+1), [0]*(m+1), [0]*(m+1)
    for i in range(1, n+1):
        p[0] = i; j0 = 0; slack = [None]*(m+1); used = [False]*(m+1)
        while True:
            used[j0] = True; i0 = p[j0]; delta = None; j1 = None
            for j in range(1, m+1):
                if used[j]: continue
                cost = costs[i0-1][j-1]
                if cost is not None:
                    cur = cost-u[i0]-v[j]
                    if slack[j] is None or cur < slack[j]: slack[j], way[j] = cur, j0
                if slack[j] is not None and (delta is None or slack[j] < delta):
                    delta, j1 = slack[j], j
            if delta is None:
                result = shortage(costs, {p[j]-1 for j in range(m+1) if used[j]})
                verify(value, result); return result
            for j in range(m+1):
                if used[j]: u[p[j]] += delta; v[j] -= delta
                elif slack[j] is not None: slack[j] -= delta
            j0 = j1
            if p[j0] == 0: break
        while j0:
            j1 = way[j0]; p[j0] = p[j1]; j0 = j1
    assignment = [None]*n
    for j in range(1, m+1):
        if p[j]: assignment[p[j]-1] = j-1
    result = {'schema': 'compatible-assignment-certificate/v1', 'status': 'optimal',
              'assignment': assignment, 'cost': sum(costs[i][j] for i, j in enumerate(assignment)),
              'row_dual': u[1:], 'column_dual': v[1:]}
    verify(value, result)
    return result


def verify(value, result):
    """Check primal/dual equality or Hall deficiency, without running a matcher."""
    costs = validate(value); n, m = len(costs), len(costs[0])
    require(type(result) is dict and result.get('schema') == 'compatible-assignment-certificate/v1',
            'Invalid certificate')
    if result.get('status') == 'infeasible':
        rows = result.get('rows')
        require(type(rows) is list and rows and all(type(i) is int and 0 <= i < n for i in rows)
                and len(rows) == len(set(rows)), 'Invalid Hall row set')
        neighbors = sorted({j for i in rows for j, c in enumerate(costs[i]) if c is not None})
        require(result.get('neighbors') == neighbors and len(neighbors) < len(rows), 'No Hall deficiency')
        return True
    require(result.get('status') == 'optimal', 'Invalid status')
    assignment, u, v = result.get('assignment'), result.get('row_dual'), result.get('column_dual')
    require(type(assignment) is list and len(assignment) == n
            and all(type(j) is int and 0 <= j < m for j in assignment)
            and len(set(assignment)) == n, 'Assignment is not injective and complete')
    require(type(u) is list and len(u) == n and all(type(x) is int for x in u), 'Invalid row dual')
    require(type(v) is list and len(v) == m and all(type(x) is int and x <= 0 for x in v), 'Invalid column dual')
    for i, row in enumerate(costs):
        require(row[assignment[i]] is not None, 'Forbidden assignment')
        for j, cost in enumerate(row):
            require(cost is None or u[i]+v[j] <= cost, 'Infeasible dual')
    total = sum(costs[i][j] for i, j in enumerate(assignment))
    require(type(result.get('cost')) is int and result['cost'] == total == sum(u)+sum(v),
            'Primal and dual costs differ')
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem'); parser.add_argument('--check')
    args = parser.parse_args(argv)
    try:
        value, digest = read(args.problem)
        if args.check:
            result, _ = read(args.check)
            require(type(result) is dict and result.get('input_sha256') == digest, 'Problem bytes changed')
            verify(value, result); print('PASS_COMPATIBLE_ASSIGNMENT')
        else:
            result = assign(value); result['input_sha256'] = digest
            print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(str(exc), file=sys.stderr); return 2
    return 0


if __name__ == '__main__': raise SystemExit(main())
