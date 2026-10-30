"""Portable exact changed-delivery gate for PR5569's owned lifetime738.

verify(word) returns a source-derived receipt. This is a necessary geometric
test for a single common-chart public replacement, not a supplier construction.
"""
from bisect import bisect_right
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def _span(basis):
    values = {0}
    for vector in basis:
        values |= {x ^ vector for x in values}
    need(len(values) == 1 << len(basis), 'independent frame basis')
    return sum(1 << x for x in values)


def _ops(word):
    """Certify that the normalized public transfer is invertible at every cut."""
    public = word['public']
    owned, effective, census = {}, [], Counter()
    for event in word['program']:
        op, role = event[:2]
        lowered = None
        if op == 'INIT':
            need(role >= public and role not in owned, 'fresh private lifetime')
            owned[role] = None
        elif op == 'COPY':
            need(role >= public and role in owned and owned[role] is None and event[2] < public,
                 'COPY of one public producer')
            coefficient = Q(event[-2])
            need(coefficient != 0, 'nonzero private COPY')
            owned[role] = (event[2], coefficient)
        elif op == 'CLEAR':
            need(role in owned, 'active private CLEAR')
            del owned[role]
        elif op == 'SCALE' and role >= public:
            need(role in owned and owned[role] is not None, 'scaled private copy')
            source, coefficient = owned[role]
            need(Q(event[-2]) != 0, 'nonzero private SCALE')
            owned[role] = source, coefficient * Q(event[-2])
        elif op in ('ADD', 'SCALE'):
            need(role < public, 'only scaled-copy private template')
            need(all(value is None or value[0] != role for value in owned.values()),
                 'copied producer remains unchanged throughout owned lifetime')
            if op == 'SCALE':
                need(Q(event[-2]) != 0, 'invertible public SCALE')
                lowered = ('SCALE', role, Q(event[-2]))
            else:
                source, coefficient = event[2], Q(event[-2])
                if source >= public:
                    need(source in owned and owned[source] is not None, 'live private source')
                    source, factor = owned[source]
                    coefficient *= factor
                    census['owned_to_public_shear'] += 1
                need(source != role and coefficient != 0, 'invertible public ADD')
                lowered = ('ADD', role, source, coefficient)
            census[op] += 1
        else:
            need(op == 'MOVE', 'known event type')
        effective.append(lowered)
    need(not owned, 'all owned lifetimes closed')
    return effective, dict(census)


def _windows(word):
    public = word['public']
    count = public + 8
    index = [[] for _ in range(count)]
    windows = [[] for _ in range(count)]
    chain = [[f] for f in word['initial']] + [[None] for _ in range(8)]
    for i, event in enumerate(word['program']):
        op, role = event[:2]
        if op == 'MOVE':
            need(chain[role][-1] == event[2], 'window source frame')
            chain[role].append(event[3])
            continue
        roles = (role,) if op in ('INIT', 'CLEAR', 'SCALE') else (role, event[2])
        for r in roles:
            index[r].append(i)
            windows[r].append(chain[r])
            chain[r] = [None if op == 'CLEAR' else event[-1]]
    for r in range(count):
        windows[r].append(chain[r])
    return index, windows


def _add(row, source, coefficient):
    for key, value in source.items():
        result = row.get(key, Q(0)) + coefficient * value
        if result:
            row[key] = result
        else:
            row.pop(key, None)


def _initial_value(effective, public):
    rows = [{r: Q(1)} for r in range(public)]
    for operation in effective[:13411]:
        if operation is None:
            continue
        if operation[0] == 'SCALE':
            rows[operation[1]] = {k: operation[2] * x for k, x in rows[operation[1]].items()}
        else:
            _, role, source, coefficient = operation
            _add(rows[role], rows[source], coefficient)
    return {key: -value / 2 for key, value in rows[133].items()}


def _covector_step(value, operation):
    """If x' = E x, fixed value c*x has coordinates c*E^-1 in x'."""
    if operation is None:
        return
    role = operation[1]
    if operation[0] == 'SCALE':
        if role in value:
            value[role] /= operation[2]
    elif value.get(role):
        source, coefficient = operation[2:]
        updated = value.get(source, Q(0)) - coefficient * value[role]
        if updated:
            value[source] = updated
        else:
            value.pop(source, None)


def _pair_witness(bounds, masks):
    upper = (1 << 512) - 1
    for _, high in bounds.values():
        upper &= masks[high]
    for role, (low, _) in bounds.items():
        missing = masks[low] & ~upper
        if missing:
            vector = (missing & -missing).bit_length() - 1
            other, high = next((r, high) for r, (_, high) in bounds.items()
                               if not (masks[high] >> vector & 1))
            return [role, other, low, high, vector]
    return None


def _check_pair(pair, bounds, masks):
    left, right, low, high, vector = pair
    need(left in bounds and right in bounds, 'pair roles are necessary support or recipient')
    need(bounds[left][0] == low and bounds[right][1] == high, 'pair binds actual windows')
    need(masks[low] >> vector & 1 and not (masks[high] >> vector & 1), 'separating pair vector')


def _compute(word):
    P = word['program']
    need(word['public'] == 735 and len(P) == 25140, 'pinned word shape')
    need(P[13408] == ['INIT', 738, 591] and P[13409] == ['COPY', 738, 133, '1', 591]
         and P[13410] == ['SCALE', 738, '-1/2', 591]
         and P[13423] == ['CLEAR', 738, 597], 'owned738 source binding')
    target_events = [(13412, 159, '-1'), (13414, 203, '2'), (13417, 148, '2'),
                     (13420, 710, '1'), (13422, 734, '1')]
    effective, census = _ops(word)
    index, windows = _windows(word)
    masks = [_span(frame) for frame in word['frames']]
    frames = word['frames']
    deliveries = []
    for event, role, coefficient in target_events:
        need(P[event][:4] == ['ADD', role, 738, coefficient], 'actual delivery binding')
        slot = index[role].index(event)
        low, high = windows[role][slot][0], windows[role][slot + 1][-1]
        previous = index[role][slot - 1] if slot else -1
        following = index[role][slot + 1] if slot + 1 < len(index[role]) else len(P)
        # Sum of lower recipient and mandatory owned terminal span.
        joined = {0}
        for vector in frames[low] + frames[597]:
            joined |= {x ^ vector for x in joined}
        ceiling = masks[high] & masks[591]
        need(all(ceiling >> vector & 1 for vector in joined), 'source delivery route feasible')
        deliveries.append({'recipient': role, 'event': event, 'previous_contact': previous,
                           'next_contact': following, 'lower_frame': low, 'upper_frame': high,
                           'minimum_dimension': len(joined).bit_length() - 1,
                           'maximum_dimension': ceiling.bit_count().bit_length() - 1})
    need([(x['minimum_dimension'], x['maximum_dimension']) for x in deliveries]
         == [(7, 7), (6, 6), (3, 4), (1, 1), (1, 1)], 'complete delivery dimension alternatives')
    owned_profiles = []
    for middle in (3, 4):
        dims = [8, 7, 6, middle, 1]
        owned_profiles.append(Counter(a - b for a, b in zip(dims, dims[1:])))
    need(owned_profiles == [Counter({1: 2, 2: 1, 3: 1})] * 2, 'both owned alternatives have identical invoice')
    middle_delivery = deliveries[2]
    lower_dim = len(frames[middle_delivery['lower_frame']])
    upper_dim = len(frames[middle_delivery['upper_frame']])
    need((lower_dim, upper_dim) == (2, 5), 'recipient148 neighboring dimensions')
    need(Counter([3-lower_dim, upper_dim-3]) == Counter([4-lower_dim, upper_dim-4]),
         'recipient148 alternate invoice is equal')
    initial = _initial_value(effective, word['public'])
    value = dict(initial)
    counts = {x['recipient']: 0 for x in deliveries}
    examples, witnesses = {}, []
    for boundary, operation in enumerate(effective[:max(x['next_contact'] for x in deliveries)]):
        _covector_step(value, operation)
        if boundary in (13376, 13410):
            need(value == {133: Q(-1, 2)}, 'unique value coordinates at producer birth and private COPY')
        for d in deliveries:
            role = d['recipient']
            if not d['previous_contact'] <= boundary < d['next_contact']:
                continue
            need(value.get(role, Q(0)) == 0, 'recipient is not needed to represent copied value')
            bounds = {role: (d['lower_frame'], d['upper_frame'])}
            for donor in sorted(value):
                chain = windows[donor][bisect_right(index[donor], boundary)]
                bounds[donor] = chain[0], chain[-1]
            pair = _pair_witness(bounds, masks)
            need(pair is not None, 'every public multipartner replacement lacks a common chart')
            _check_pair(pair, bounds, masks)
            counts[role] += 1
            witnesses.append([boundary, role, pair])
            if role not in examples:
                examples[role] = {'boundary': boundary, 'pair': pair, 'support_size': len(value),
                                  'bounds': [[r, a, b] for r, (a, b) in sorted(bounds.items())]}
    result = {'status': 'PASS_OWNED738_DELIVERY_OBSTRUCTION',
              'effective_public_operations': census,
              'delivery_windows': deliveries,
              'owned_paid_histogram_both_alternatives': {'1': 2, '2': 1, '3': 1},
              'public148_paid_histogram_both_alternatives': {'1': 1, '2': 1},
              'public_replacement_boundaries': {str(r): n for r, n in counts.items()},
              'all_public_replacement_boundaries': len(witnesses),
              'witnesses_sha256': sha256(json.dumps(witnesses, separators=(',', ':')).encode()).hexdigest(),
              'initial_value_support': len(initial),
              'pair_examples': {str(r): value for r, value in examples.items()},
              'new_bound': False}
    return result, effective, initial, masks


def _rejected(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def verify(word):
    """Authenticate the scientific input externally, then recompute this gate."""
    result, effective, initial, masks = _compute(word)
    changed_producer = json.loads(json.dumps(word))
    changed_producer['program'][13412][1] = 133
    zero_scale = json.loads(json.dumps(word))
    scale_event = next(e for e in zero_scale['program'] if e[0] == 'SCALE' and e[1] < word['public'])
    scale_event[-2] = '0'
    example = next(iter(result['pair_examples'].values()))
    bounds = {r: (a, b) for r, a, b in example['bounds']}
    bad_pair = example['pair'][:-1] + [0]
    def altered_functional():
        value = dict(initial)
        value[0] = value.get(0, Q(0)) + 1
        for operation in effective[:13411]:
            _covector_step(value, operation)
        need(value == {133: Q(-1, 2)}, 'target functional matches private copy')
    controls = {
        'copied_public_producer_changed': _rejected(lambda: _ops(changed_producer)),
        'singular_public_scale': _rejected(lambda: _ops(zero_scale)),
        'altered_target_functional': _rejected(altered_functional),
        'zero_separating_vector': _rejected(lambda: _check_pair(bad_pair, bounds, masks)),
    }
    need(all(controls.values()), 'owned738 semantic mutation controls')
    # Minimal algebraic positive control for the covector direction.
    value = {0: Q(1)}
    _covector_step(value, ('ADD', 0, 1, Q(2)))
    need(value == {0: Q(1), 1: Q(-2)}, 'inverse elementary-row covector control')
    result['corruption_controls'] = controls
    result['covector_positive_control'] = 'D=x0 before x0+=2*x1 becomes x0-2*x1 afterward'
    return result
