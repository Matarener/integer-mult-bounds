"""Check the vector engine against explicit dense matrix products.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product

import audit as A
from evidence import need


def rejected(function, label):
    try:
        function()
    except ValueError:
        return label
    raise ValueError('Accepted negative control: ' + label)


def dense_matrix(events, width):
    matrix = [[Q(int(i == j)) for j in range(width)] for i in range(width)]
    for op, target, source, q in events:
        elementary = [[Q(int(i == j)) for j in range(width)] for i in range(width)]
        if op in ('INIT', 'CLEAR', 'COPY'):
            elementary[target] = [Q(0)] * width
        if op == 'SCALE':
            elementary[target][target] = q
        elif op in ('ADD', 'COPY'):
            elementary[target][source] += q
        matrix = [[sum(elementary[i][k] * matrix[k][j] for k in range(width))
                   for j in range(width)] for i in range(width)]
    return matrix


def vector_oracle():
    alphabet = []
    for target in range(2):
        alphabet += [(op, target, None, None) for op in ('INIT', 'CLEAR')]
        for q in (Q(-2), Q(1, 2)):
            alphabet += [('SCALE', target, None, q),
                         ('ADD', target, 1 - target, q),
                         ('COPY', target, 1 - target, q)]
    cases = 0
    for length in range(4):
        for events in product(alphabet, repeat=length):
            matrix = dense_matrix(events, 2)
            for i in range(2):
                e = {i: Q(1)}
                need(A.push(e, events) == {j: matrix[j][i] for j in range(2) if matrix[j][i]},
                     'Independent dense column oracle')
                need(A.pull(e, events) == {j: matrix[i][j] for j in range(2) if matrix[i][j]},
                     'Independent dense row oracle')
            cases += 1
    return {'programs': cases, 'rows_and_columns': 4 * cases,
            'alphabet': len(alphabet), 'maximum_length': 3}


def commutation_counterexample():
    # The three cut identities alone do not imply identity on a helper pivot.
    e = {0: Q(1)}
    a, b = e, {0: Q(1), 1: Q(1)}
    suffix = [('SCALE', 1, None, Q(-1)), ('ADD', 1, 0, Q(2))]
    c, d = A.pull(a, []), A.push(b, suffix)
    need(A.dot(a, b) == A.dot(c, d) == 1 and A.push(d, []) == b,
         'Counterexample passes the three short cut identities')
    need(A.pull(c, suffix) == c and A.push(d, suffix) == d,
         'Counterexample even fixes both boundary modes')
    need(A.push(e, suffix) != e, 'Counterexample fails the pivot column')
    boundary, middle = A.bases(0, 0, a, b, c, d)
    value = A.push(e, A.operations(boundary + middle))
    need(value == e, 'The original pivot reaches the cut')
    value.pop(0)  # The new independent input is zero.
    value = A.push(value, A.operations(A.inverse(middle)))
    value = A.push(value, suffix)
    value = A.push(value, A.operations(A.inverse(boundary)))
    expected = A.push(e, suffix)
    need(value.get(1, 0) == 0 and expected[1] == 2,
         'The continuing output differs despite the short identities')
    return {'input': [1, 0], 'new_input': 0, 'expected_continuing_output': 2,
            'actual_continuing_output': 0, 'missing_obligation': 'Identity pivot column'}


def source_controls(data, snapshots, local):
    controls = []
    for number, (word, cut, frame, plan) in enumerate(snapshots):
        for field in ('input', 'retirement', 'injection'):
            bad = deepcopy(plan)
            key = next(iter(bad[field]))
            bad[field][key] = str(Q(bad[field][key]) + 1)
            controls.append(rejected(lambda: A.check_cut(word, cut, frame, bad),
                                     f'frame105 step{number + 1}: changed {field}'))
        controls.append(rejected(lambda: A.check_cut(word, cut, 3, plan),
                                 f'frame105 step{number + 1}: false physical cut frame'))
    word = data['word']
    bad = deepcopy(word)
    removed = bad['program'].pop(0)
    need(removed[0] == 'ADD', 'Actual input-basis control')
    controls.append(rejected(lambda: A.check_column(bad, removed[2]), 'Removed actual input basis operation'))
    bad = deepcopy(word)
    index = next(i for i, e in enumerate(bad['program']) if e[0] == 'MOVE')
    bad['program'].pop(index)
    controls.append(rejected(lambda: A.chronology(bad), 'Removed actual paid query'))
    # A write just before COPY is erased by COPY. Endpoints alone miss this fault.
    bad = deepcopy(word)
    index = next(i for i, e in enumerate(bad['program']) if e[0] == 'COPY')
    event = bad['program'][index]
    row = A.pull({event[2]: Q(1)}, A.operations(bad['program'][:index]))
    source = next(iter(row))
    bad['program'].insert(index, ['ADD', event[1], event[2], '1', event[-1]])
    need(A.push({source: Q(1)}, A.operations(bad['program']))
         == A.push({source: Q(1)}, A.operations(word['program'])),
         'The COPY fault preserves the tested final column')
    controls.append(rejected(lambda: A.check_column(bad, source), 'Nonzero COPY target with unchanged endpoint'))
    expected = data['result']['complete_cost']
    for kind in ('paid', 'helpers'):
        changed = deepcopy(local)
        changed[kind][1] += -1 if kind == 'paid' else 1
        actual = A.invoice(changed, data['controller'])
        target = 'paid' if kind == 'paid' else 'targets'
        controls.append(rejected(lambda: need(
            {str(k): v for k, v in actual[target].items()} == expected[target], 'Exact complete invoice'),
            'Missing paid child' if kind == 'paid' else 'Invented productive target'))
    for opcode in ('LOCAL', 'QUERY_SHEAR', 'IDLE'):
        changed = deepcopy(data['controller'])
        at = next(i for i, e in enumerate(changed['physical_events']) if e[0] == opcode)
        changed['physical_events'].pop(at)
        controls.append(rejected(lambda: A.invoice(local, changed), 'Missing physical ' + opcode))
    return controls
