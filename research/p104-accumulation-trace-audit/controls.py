"""Independent dense controls and deliberate trace/accounting faults."""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import audit as A


def dense(word):
    n = word['public'] + word['owned_fields']
    matrix = [[Q(i == j) for j in range(n)] for i in range(n)]
    for event in word['program']:
        op, d = event[:2]
        if op in ('INIT', 'CLEAR'):
            matrix[d] = [Q(0)] * n
        elif op in ('ADD', 'COPY'):
            q, s = Q(event[-2]), event[2]
            matrix[d] = [(x if op == 'ADD' else Q(0)) + q*y
                         for x, y in zip(matrix[d], matrix[s])]
        elif op == 'SCALE':
            matrix[d] = [Q(event[-2])*x for x in matrix[d]]
    return matrix


def fixture(a, b, scale, source):
    before = {'public': 4, 'owned_fields': 0, 'program': [
        ['ADD', 0, 1, str(a), 1], ['SCALE', 1, str(scale), 1],
        ['ADD', 3, 2, '1/2', 1], ['ADD', 0, source, str(b), 1]]}
    after = {'public': 4, 'owned_fields': 1, 'program': [
        ['INIT', 4, 1], ['ADD', 4, 1, str(a), 1],
        ['SCALE', 1, str(scale), 1], ['ADD', 3, 2, '1/2', 1],
        ['ADD', 4, source, str(b), 1], ['MOVE', 4, 1, 0, True],
        ['ADD', 0, 4, '1', 0], ['CLEAR', 4, 0]]}
    return before, after


def run(before, after, result, counted):
    cases = 0
    for a, b, scale, src in product([Q(-2), Q(-1, 2), Q(1, 2), Q(1), Q(2)],
                                    [Q(-2), Q(-1, 2), Q(1, 2), Q(1), Q(2)],
                                    [Q(-2), Q(-1), Q(1, 2), Q(2)], [1, 2]):
        x, y = fixture(a, b, scale, src)
        A.trace(x, y)
        old, new = dense(x), dense(y)
        A.need(all(new[i][:4] == old[i] and not new[i][4] for i in range(4))
               and not any(new[4]), 'Separate dense input-column oracle')
        cases += 1
    rejected = []

    def reject(label, call, reason):
        try:
            call()
        except ValueError as error:
            A.need(reason in str(error), label + ': wrong rejection ' + str(error))
            rejected.append(label)
        else:
            raise ValueError('Accepted mutation: ' + label)

    # The final endpoint can agree although an intermediate source read is wrong.
    x, y = fixture(Q(1), Q(1), Q(1), 2)
    pair = [['ADD', 3, 0, '1', 1], ['ADD', 3, 0, '-1', 1]]
    x['program'][1:1] = deepcopy(pair)
    y['program'][2:2] = deepcopy(pair)
    old, new = dense(x), dense(y)
    A.need(all(new[i][:4] == old[i] for i in range(4)) and not any(new[4]),
           'Endpoint-preserving early-read counterexample')
    reject('endpoint_preserving_early_read', lambda: A.trace(x, y), 'No observation')
    blocks = A.groups(before, after)
    slot = min(blocks)
    group = blocks[slot]
    mutations = []
    for key in ('move', 'delivery', 'clear'):
        word = deepcopy(after)
        del word['program'][group[key]]
        mutations.append(('missing_' + key, word))
    word = deepcopy(after)
    word['program'][group['delivery']][-2] = '-1'
    mutations.append(('delivery_sign', word))
    for label, word in mutations:
        reject(label, lambda w=word: A.trace(before, w),
               'unit delivery' if label == 'delivery_sign' else 'Complete pending-sum lifetime')
    word = deepcopy(after)
    word['program'][group['adds'][0]][-2] = '2'
    reject('changed_component', lambda: A.trace(before, word), 'original scalar sequence')
    word = deepcopy(after)
    word['program'][group['adds'][0]][2] += 1
    reject('changed_source', lambda: A.trace(before, word), 'original scalar sequence')
    word = deepcopy(after)
    word['owned_fields'] -= 1
    reject('missing_owned_slot', lambda: A.inventory(word), 'Actual destination')
    word = deepcopy(after)
    word['program'].insert(0, ['CLEAR', 0, word['initial'][0]])
    reject('public_erasure', lambda: A.inventory(word), 'Owned return')
    word = deepcopy(after)
    word['program'][group['move']][4] = False
    reject('owned_query_direction', lambda: A.inventory(word), 'query source and ownership')
    for label, field, rank, delta in [('old_target_credit', 'targets', '8', 36),
                                     ('missing_paid_call', 'paid', '1', -1)]:
        receipt = deepcopy(result)
        receipt['complete_cost'][field][rank] += delta
        reject(label, lambda r=receipt: A.billing(after, counted, r),
               'Full target invoice' if field == 'targets' else 'Full paid invoice')
    receipt = deepcopy(result)
    receipt['complete_cost']['nonrecursive']['local_routes'] -= 4000
    reject('unfunded_owned_return', lambda: A.billing(after, counted, receipt), 'Positive source tariff')
    return {'dense_oracle_program_pairs': cases, 'semantic_rejections': rejected,
            'endpoint_preserving_counterexample': 'An early read and its later cancellation preserve the endpoint but fail the trace.'}
