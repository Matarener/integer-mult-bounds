#!/usr/bin/env python3
"""Check the simple-graph theorem fixtures and an exact positive control."""
import argparse
from copy import deepcopy
from hashlib import sha256
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def apply(rows, vector):
    return sum(((row & vector).bit_count() & 1) << a for a, row in enumerate(rows))


def rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            bit = vector.bit_length() - 1
            if bit in pivots:
                vector ^= pivots[bit]
            else:
                pivots[bit] = vector
                break
    return len(pivots)


def supports(edges, order):
    fields = [tuple(edge) for edge in edges]
    for vertex in order:
        fields += [(vertex,)] * (4 - sum(vertex in edge for edge in edges))
    return [tuple(j for j, field in enumerate(fields) if vertex in field) for vertex in order]


def prefix_labels(supports_, n):
    return [[sum((1 << k) for k in range(i) if a in supports_[k]) for a in range(n)]
            for i in range(len(supports_))]


def simple_last_diagonal(supports_):
    need(all(len(s) == 4 for s in supports_), 'Each support must have rank four')
    need(all(len(set(a) & set(b)) <= 1 for a, b in itertools.combinations(supports_, 2)),
         'The simple-graph support hypothesis fails')
    n = max(max(s) for s in supports_) + 1
    need(all(sum(a in s for s in supports_) <= 2 for a in range(n)),
         'A coordinate has more than two owners')
    prefix = prefix_labels(supports_, n)
    last = len(supports_) - 1
    checked = 0
    for a, b in itertools.permutations(supports_[last], 2):
        earlier = [i for i in range(last) if b in supports_[i]]
        if earlier:
            i = earlier[0]
            need(prefix[i][a] ^ prefix[i][b] != prefix[last][a] ^ prefix[last][b],
                 'An off-diagonal last coefficient can cancel')
        checked += 1
    return checked


def check_chains(case):
    n = case['active_fields']
    rows = case['R_rows']
    need(len(rows) == len(case['supports']) == len(case['native_chains']), 'Stage counts differ')
    for matrix, support, chain in zip(rows, case['supports'], case['native_chains']):
        mask = sum(1 << a for a in support)
        need(len(support) == 4 and len(matrix) == n, 'The native call shape differs')
        need(all(row & ~mask == 0 for row in matrix), 'A column lies outside its native support')
        u, w, basis = chain['u'], chain['w'], chain['basis']
        need(u != 0 and not (u | w) & ~mask, 'The native main chain has a bad support')
        need(apply(matrix, u) == 0 and apply(matrix, w) == u, 'The native main chain fails')
        need(basis[:2] == [u, w] and len(basis) == rank(basis) == 4,
             'The native roles do not form an independent basis')
        need(all(not vector & ~mask for vector in basis), 'A role lies outside its native support')
        need([apply(matrix, z) ^ z for z in basis[2:]] == chain['early_q_column_updates'],
             'The early helper-column update differs')


def literal_product(case, flags=None):
    n = case['active_fields']
    flags = [1] * n if flags is None else flags
    state = [[{0} if a == b else set() for b in range(n)] for a in range(n)]
    for i, (rows, support) in enumerate(zip(case['R_rows'], case['supports'])):
        stage = [[set() for _ in range(n)] for _ in range(n)]
        for a in range(n):
            d = (1 << (i + 1)) if a in support else 0
            stage[a][a].add(d)
            for b in range(n):
                if rows[a] >> b & 1:
                    stage[a][b].add(d | 1)
        out = [[set() for _ in range(n)] for _ in range(n)]
        for a, b, c in itertools.product(range(n), repeat=3):
            for left in stage[a][b]:
                for right in state[b][c]:
                    if left & right & 1:
                        continue
                    term = left ^ right
                    if term in out[a][c]:
                        out[a][c].remove(term)
                    else:
                        out[a][c].add(term)
        state = out
    for a, b in itertools.product(range(n), repeat=2):
        d = sum(1 << (i + 1) for i, support in enumerate(case['supports']) if a in support)
        expected = ({d, d | 1} if flags[a] else {d}) if a == b else set()
        need(state[a][b] == expected, 'The literal stage product has a wrong endpoint')
    return state


def rejected(name, operation):
    try:
        operation()
    except ValueError as error:
        return {'name': name, 'result': 'REJECT', 'reason': str(error)}
    raise ValueError('A negative control passed: ' + name)


def run():
    k4 = list(itertools.combinations(range(4), 2))
    fixture_count = 0
    coefficient_count = 0
    for edges in (k4, [e for e in k4 if e != (0, 1)]):
        for order in itertools.permutations(range(4)):
            coefficient_count += simple_last_diagonal(supports(edges, order))
            fixture_count += 1
    diagonal_cases = 0
    for mask in range(16):
        matrix = [(1 << i) if mask >> i & 1 else 0 for i in range(4)]
        for u, w in itertools.product(range(1, 16), range(16)):
            need(apply(matrix, u) != 0 or apply(matrix, w) != u,
                 'A diagonal matrix contains a nonzero main Jordan chain')
            diagonal_cases += 1
    control = json.loads((PACKAGE / 'CONTROL.json').read_text())['results'][0]
    check_chains(control)
    literal_product(control)
    rows = control['R_rows']
    need([a ^ b for a, b in zip(*rows)] == [1 << i for i in range(4)],
         'The two q coefficients do not sum to the identity')
    paid = {int(r): n for r, n in control['paid_profile'].items()}
    targets = {int(r): n for r, n in control['target_profile'].items()}
    need(paid == {1:2646, 2:2684, 3:158, 4:88, 5:204, 6:22, 7:38},
         'The declared two-FULL invoice differs')
    need(targets == {8:434, 15:444}, 'The complete target debit differs')
    surplus = sum(r*n for r, n in targets.items()) - sum(r*n for r, n in paid.items())
    need(surplus == -126 and max(paid) < min(targets), 'The positive control price gate differs')
    bad_word = deepcopy(control)
    bad_word['R_rows'][0][0] ^= 1
    bad_chain = deepcopy(control)
    bad_chain['native_chains'][0]['u'] = 0
    controls = [
        rejected('changed_q_coefficient', lambda: literal_product(bad_word)),
        rejected('missing_target_Q', lambda: literal_product(control, [0,1,1,1])),
        rejected('zero_main_chain', lambda: check_chains(bad_chain)),
        rejected('parallel_edges_outside_simple_graph', lambda: simple_last_diagonal(control['supports'])),
    ]
    evidence = json.loads((PACKAGE / 'solver-evidence/MANIFEST.json').read_text())
    totals = {}
    for name, row in evidence['files'].items():
        raw = (PACKAGE / 'solver-evidence' / name).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'A frozen solver receipt changed')
        cases = json.loads(raw)['results']
        need(len(cases) == row['cases'] and all(c['status'] == 'unsat' for c in cases),
             'The recorded solver outcomes differ')
        for case in cases:
            expected = supports(case['edges'], case['order'])
            need([list(s) for s in expected] == case['supports'], 'A recorded support differs')
        totals[name] = len(cases)
    need(sum(totals.values()) == 80, 'The recorded solver case count differs')
    return {
        'schema_version': 1,
        'status': 'PASS_BIT_SIMPLE_GRAPH_OBSTRUCTION',
        'simple_graph_order_fixtures': fixture_count,
        'last_off_diagonal_coefficients_checked': coefficient_count,
        'diagonal_chain_cases': diagonal_cases,
        'positive_control': {'literal_stage_product':'PASS', 'native_chains':'PASS',
                             'early_helper_columns':'PASS', 'rank_surplus':surplus},
        'negative_controls': controls,
        'solver_evidence': {'recorded_cases':totals, 'integrity':'PASS',
                            'unsat_reproved':False, 'solver_run':False,
                            'scope':'The frozen statuses depend on the recorded Z3 solver. The standard-library checks do not prove those UNSAT claims.'},
        'new_kappa': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    expected = PACKAGE / 'RESULT.json'
    if expected.exists() and json.loads(expected.read_text()) != result:
        raise ValueError('The exact retained result differs')
    if args.output:
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_BIT_SIMPLE_GRAPH_OBSTRUCTION fixtures=48 diagonal_cases=3840 control=PASS solver_run=false new_kappa=false')


if __name__ == '__main__':
    main()
