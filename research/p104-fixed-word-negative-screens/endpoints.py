"""Exact, finite endpoint-combination screen on the authenticated PR6030 word.

Prepared by Jonathan Capalbo (jon314159), with OpenAI Codex assistance.
Apache-2.0. PR5827 supplies the earlier endpoint-resynthesis mechanism;
PR6030 and its retained authors supply the unchanged scalar word.
"""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(target, source, coefficient):
    for key, value in tuple(source.items()):
        result = target.get(key, Q(0)) + coefficient * value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def encode(row):
    return {str(key): str(value) for key, value in sorted(row.items())}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def binary_span(basis):
    values = {0}
    for value in basis:
        need(type(value) is int and 0 < value < 512 and value not in values,
             'Independent binary frame basis')
        values |= {x ^ value for x in tuple(values)}
    return frozenset(values)


def initial_state(word):
    public = word['public']
    count = public + word['owned_fields']
    return ([{r: Q(1)} if r < public else {} for r in range(count)],
            list(word['initial']) + [None] * word['owned_fields'])


def advance(rows, levels, event, public):
    """Exact scalar semantics; MOVE only changes the current canonical chart."""
    op, r = event[:2]
    if op == 'MOVE':
        need(levels[r] == event[2] and levels[r] is not None, 'MOVE source chart')
        need(event[4] == (r >= public), 'MOVE ownership')
        levels[r] = event[3]
    elif op == 'INIT':
        need(r >= public and levels[r] is None, 'Owned INIT')
        rows[r] = {}
        levels[r] = event[2]
    elif op == 'CLEAR':
        need(r >= public and levels[r] == event[2] and levels[r] is not None, 'Owned CLEAR')
        rows[r] = {}
        levels[r] = None
    else:
        coefficient, frame = Q(event[-2]), event[-1]
        need(coefficient and levels[r] == frame and frame is not None, 'Scalar destination')
        if op == 'SCALE':
            rows[r] = {key: coefficient * value for key, value in rows[r].items()}
        else:
            s = event[2]
            need(s != r and levels[s] == frame, 'Scalar common chart')
            if op == 'COPY':
                need(r >= public and not rows[r], 'COPY into owned zero')
            else:
                need(op == 'ADD', 'Scalar opcode')
            add(rows[r], rows[s], coefficient)


def finish(word, rows, levels):
    public, live = word['public'], set(word['live'])
    for r, row in enumerate(rows):
        expected = {r: Q(1)} if r < public else {}
        if r - 112 in live:
            expected[r - 112] = Q(1)
        need(row == expected, 'Complete scalar endpoint at role ' + str(r))
    need(levels[:public] == word['final'] and all(x is None for x in levels[public:]),
         'Complete final charts and owned lifetimes')
    return {'arbitrary_public_columns': public, 'final_roles_checked': len(rows),
            'final_scalar_rows_sha256': digest([encode(row) for row in rows]),
            'final_frames_checked': True}


def span_solve(target, generators, fast=True):
    """Rational elimination with unique labels and direct substitution checks.

    A nonzero reduced residue proves nonmembership: it has no coordinate at any
    echelon pivot, whereas every nonzero row-span vector has a pivot coordinate.
    """
    source = dict(generators)
    need(len(source) == len(generators), 'Distinct donor-version labels')
    if fast:
        support = set().union(*(set(row) for _, row in generators)) if generators else set()
        missing = set(target) - support
        if missing:
            coordinate = min(missing)
            return {'in_span': False, 'kind': 'missing_coordinate',
                    'coordinate': coordinate, 'target_coefficient': str(target[coordinate]),
                    'rank': None, 'witness': None, 'witness_dyadic': None}
    pivots = {}
    for label, original in generators:
        row, combination = dict(original), {label: Q(1)}
        while row:
            pivot = min(row)
            if pivot not in pivots:
                scale = row[pivot]
                pivots[pivot] = ({key: value / scale for key, value in row.items()},
                                 {key: value / scale for key, value in combination.items()})
                break
            base, coefficients = pivots[pivot]
            scale = -row[pivot]
            add(row, base, scale)
            add(combination, coefficients, scale)
    residue, combination = dict(target), {}
    for pivot, (base, coefficients) in sorted(pivots.items()):
        if pivot in residue:
            scale = residue[pivot]
            add(residue, base, -scale)
            add(combination, coefficients, scale)
    reconstructed = {}
    for label, coefficient in combination.items():
        add(reconstructed, source[label], coefficient)
    add(reconstructed, residue, Q(1))
    need(reconstructed == target, 'Exact elimination substitution')
    need(all(pivot not in residue for pivot in pivots), 'Reduced residue avoids every pivot')
    return {'in_span': not residue, 'kind': 'in_span' if not residue else 'rational_span_exclusion',
            'rank': len(pivots), 'residue': encode(residue), 'reduction': encode(combination),
            'witness': encode(combination) if not residue else None,
            'witness_dyadic': all(q.denominator & (q.denominator - 1) == 0
                                  for q in combination.values()) if not residue else None}


def controls():
    a, b = {0: Q(1)}, {1: Q(1)}
    result = span_solve({0: Q(1), 1: Q(2)}, [('a', a), ('b', b)])
    need(result['in_span'] and result['witness'] == {'a': '1', 'b': '2'}, 'Two-source positive')
    need(not span_solve(b, [('a', a)])['in_span'], 'Missing-coordinate negative')
    need(not span_solve(a, [('ab', {0: Q(1), 1: Q(1)})])['in_span'], 'Correlated-span negative')
    before, after = ('before:start:0:4', {0: Q(1), 1: Q(1)}), ('after:start:9:4', b)
    need(not span_solve(a, [before])['in_span'] and not span_solve(a, [after])['in_span'],
         'Each endpoint alone fails the cancellation control')
    combined = span_solve(a, [before, after])
    need(combined['in_span'] and combined['witness'] == {before[0]: '1', after[0]: '-1'},
         'Cross-bank cancellation with the same role in two versions')
    try:
        span_solve(a, [('role4', before[1]), ('role4', after[1])])
    except ValueError as error:
        need(str(error) == 'Distinct donor-version labels', 'Expected duplicate-label failure')
    else:
        raise ValueError('Duplicate donor-version labels accepted')
    # Capture the two actual versions of a donor in a tiny scalar trace.
    rows, levels = [dict(a), dict(b), {2: Q(1)}], [0, 0, 0]
    original = dict(rows[0])
    net = {}
    add(net, rows[0], Q(2))
    advance(rows, levels, ['ADD', 2, 0, '2', 0], 3)
    advance(rows, levels, ['ADD', 0, 1, '1', 0], 3)
    add(net, rows[0], Q(-1))
    advance(rows, levels, ['ADD', 2, 0, '-1', 0], 3)
    need(original == a and net == {0: Q(1), 1: Q(-1)}, 'Original donor versions and ADD coefficients')
    need(not span_solve(a, [('latest', rows[0])])['in_span'], 'Stale donor version rejected')
    need(span_solve(a, [('captured', original)])['in_span'], 'Captured donor version accepted')
    return {'two_source_positive': True, 'missing_coordinate_negative': True,
            'correlated_span_negative': True, 'cross_bank_cancellation_positive': True,
            'same_role_distinct_side_labels': True, 'duplicate_labels_rejected': True,
            'original_donor_versions_and_coefficients': True, 'stale_donor_version_rejected': True}


def enumerate_pairs(word):
    program = word['program']
    contacts, moves = defaultdict(list), defaultdict(list)
    for i, event in enumerate(program):
        op, r = event[:2]
        contacts[r].append((i, 'move' if op == 'MOVE' else 'incoming' if op == 'ADD' else 'other'))
        if op == 'MOVE':
            moves[r].append(i)
        if op in ('ADD', 'COPY'):
            contacts[event[2]].append((i, 'read'))
    census = Counter({'adjacent_role_move_pairs': 0, 'excluded_intermediate_contacts': 0,
                      'incoming_only_pairs': 0, 'empty_contact_pairs': 0})
    pairs, event_pair, requests = [], {}, defaultdict(list)
    for r in sorted(moves):
        cc = sorted(contacts[r])
        indices = [i for i, kind in cc]
        for first, second in zip(moves[r], moves[r][1:]):
            census['adjacent_role_move_pairs'] += 1
            interior = [(i, kind) for i, kind in cc if first < i < second]
            if any(kind != 'incoming' for i, kind in interior):
                census['excluded_intermediate_contacts'] += 1
                continue
            census['incoming_only_pairs' if interior else 'empty_contact_pairs'] += 1
            j = len(pairs)
            p, q = bisect_left(indices, first), bisect_right(indices, second)
            left = indices[p - 1] + 1 if p else 0
            right = indices[q] if q < len(indices) else len(program)
            a, b = program[first][2:4]
            b2, c = program[second][2:4]
            need(b == b2 and program[first][4] == program[second][4], 'Adjacent MOVE itinerary')
            incoming = [i for i, kind in interior]
            pairs.append({'pair_index': j, 'role': r, 'move_events': [first, second],
                          'frames': [a, b, c], 'private': program[first][4],
                          'incoming_events': incoming,
                          'windows': {'before': [left, first], 'after': [second + 1, right]}})
            for i in incoming:
                need(i not in event_pair, 'Unique receiver interval for each incoming ADD')
                event_pair[i] = j
            for side, lo, hi, frame in [('before', left, first, a), ('after', second + 1, right, c)]:
                need(not any(lo <= i < hi for i in indices), 'Untouched endpoint window')
                requests[lo].append((j, side, hi, frame))
    return dict(census), pairs, event_pair, requests


def run(word):
    """Return deterministic finite-screen evidence; input authentication is external."""
    control_results = controls()
    program, public = word['program'], word['public']
    census, pairs, event_pair, requests = enumerate_pairs(word)
    need(census == {'adjacent_role_move_pairs': 2664, 'excluded_intermediate_contacts': 1900,
                    'incoming_only_pairs': 764, 'empty_contact_pairs': 0}, 'Pinned complete pair census')
    desired = [{} for pair in pairs]
    arrivals = defaultdict(list)
    rows, levels = initial_state(word)
    for i, event in enumerate(program):
        if i in event_pair:
            add(desired[event_pair[i]], rows[event[2]], Q(event[3]))
        if event[0] == 'MOVE':
            arrivals[event[3]].append((i + 1, event[1], dict(rows[event[1]])))
        advance(rows, levels, event, public)
    replay = finish(word, rows, levels)
    arrival_times = {frame: [slot for slot, r, row in values] for frame, values in arrivals.items()}
    banks, records = defaultdict(dict), []
    counts = Counter({'windows_collected': 0, 'pairs_tested': 0, 'missing_coordinate': 0,
                      'rational_span_exclusion': 0, 'candidates': 0})
    rows, levels = initial_state(word)
    for slot in range(len(program) + 1):
        for j, side, hi, frame in requests.get(slot, []):
            receiver = pairs[j]['role']
            need(levels[receiver] == frame, 'Receiver endpoint chart')
            generators = [(side + ':start:' + str(slot) + ':' + str(r), dict(rows[r]))
                          for r, current in enumerate(levels) if current == frame and r != receiver]
            times, values = arrival_times.get(frame, []), arrivals.get(frame, [])
            for arrival, r, row in values[bisect_right(times, slot):bisect_right(times, hi)]:
                if r != receiver:
                    generators.append((side + ':arrival:' + str(arrival) + ':' + str(r), row))
            banks[j][side] = generators
            counts['windows_collected'] += 1
            if len(banks[j]) == 2:
                generators = banks[j]['before'] + banks[j]['after']
                result = span_solve(desired[j], generators)
                counts['pairs_tested'] += 1
                counts['candidates' if result['in_span'] else result['kind']] += 1
                records.append({'pair': pairs[j], 'generator_count': len(generators),
                                'net_contribution_sha256': digest(encode(desired[j])),
                                'generators_sha256': digest([[name, encode(row)] for name, row in generators]),
                                'result': result})
                del banks[j]
        if slot < len(program):
            advance(rows, levels, program[slot], public)
    need(not banks and len(records) == len(pairs), 'Every endpoint pair tested completely')
    need(counts == {'windows_collected': 1528, 'pairs_tested': 764, 'missing_coordinate': 693,
                    'rational_span_exclusion': 71, 'candidates': 0}, 'Pinned exact negative endpoint result')
    need(finish(word, rows, levels) == replay, 'Both scalar replay passes agree')
    return {'status': 'PASS_ENDPOINT_COMBINATION_SCREEN', 'census': census, 'counts': dict(counts),
            'replay': replay, 'controls': control_results,
            'pairs': sorted(records, key=lambda item: item['pair']['pair_index']),
            'scope': 'All 764 incoming-ADD-only adjacent MOVE intervals of the pinned word. '
                     'The coefficient-weighted original net contribution fails the rational sum of both full '
                     'endpoint-window accumulated spans, with the receiver excluded. No receiver scaling, '
                     'changed other-role program, new lifetime, target change or global optimum is claimed.'}
