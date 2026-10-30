"""Separate dense Gaussian-integer arithmetic for the shared event extraction.

This does not independently reconstruct the source allocation.  The primary
engine interprets retained row operations; this oracle multiplies explicit
8-by-8 operation matrices and compares every complete column record.
Prepared by ToikY with substantial OpenAI Codex assistance, Apache-2.0.
"""

import copy
import hashlib
import json


Z = (0, 0)
U = (1, 0)
UNITS = (U, (0, 1), (-1, 0), (0, -1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ident():
    return [[U if i == j else Z for j in range(8)] for i in range(8)]


def product(a, b):
    """Ordinary dense matrix multiplication over Z[i], without row helpers."""
    out = [[Z for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for k in range(8):
            x, y = a[i][k]
            if (x, y) == Z:
                continue
            for j in range(8):
                v, w = b[k][j]
                r, s = out[i][j]
                out[i][j] = (r + x*v - y*w, s + x*w + y*v)
    return out


def phase(stream, exponent):
    a = ident()
    a[stream][stream] = UNITS[exponent % 4]
    return a


def operation(event, character):
    kind = event['kind']
    if kind == 'phase':
        exponent = sum(coef * ((character & axis).bit_count() % 2)
                       for coef, axis in event['terms'])
        return phase(event['stream'], exponent)
    if kind == 'shear':
        a = ident()
        require(event['dst'] != event['src'], 'distinct shear streams')
        a[event['dst']][event['src']] = (event['coefficient'], 0)
        return a
    if kind == 'signed_swap':
        a = ident()
        left, right = event['left'], event['right']
        a[left][left] = a[right][right] = Z
        a[left][right], a[right][left] = U, (-1, 0)
        return a
    raise ValueError('unknown primitive operation')


def replay(events, character):
    a = ident()
    for event in events:
        a = product(operation(event, character), a)
    return a


def as_columns(a):
    return [[list(a[i][j]) for i in range(8)] for j in range(8)]


def cut_program(fixture):
    events = copy.deepcopy(fixture['primitive_events'])
    matches = [event for event in events
               if event['kind'] == 'phase'
               and event['provenance']['source_kind'] == 'idle_cover_sweep'
               and event['provenance'].get('child') == fixture['child']]
    require(len(matches) == 1, 'one actual cut event')
    event = matches[0]
    require(event['stream'] == fixture['stream'], 'literal cut stream')
    prefix = [[1, axis] for axis in fixture['removed_axes']]
    require(len(prefix) == 24 and event['terms'][:24] == prefix,
            'exact ordered removed axes')
    require(event['terms'][24:48] == [[1, axis] for axis in fixture['retained_axes']],
            'exact remaining axes')
    # Keep every later term, including the separate translation term.
    event['terms'] = event['terms'][24:]
    return events


def side_and_read_controls():
    c = phase(0, 1)
    ci = phase(0, -1)
    g = ident()
    g[1][0] = U
    require(product(product(g, c), ci) == g, 'input correction positive')
    require(product(ci, product(g, c)) != g, 'wrong output correction rejected')
    require(product(product(c, g), ci) != g, 'earlier read invalidates head')
    require(UNITS[(1+1) % 4] != UNITS[(1 ^ 1) % 4], 'XOR shortcut rejected')
    return {'input_side_positive': True, 'wrong_output_side_rejected': True,
            'earlier_read_rejected': True, 'integer_phase_sum_not_XOR': True}


def check(receipt):
    fixtures = receipt['fixtures'] + ([receipt['negative_control']]
                                    if receipt['negative_control'] is not None else [])
    checked, entries, active, failed = 0, 0, 0, 0
    summaries = []
    for fixture in fixtures:
        events = fixture['primitive_events']
        changed = cut_program(fixture)
        digest = hashlib.sha256(json.dumps(events, sort_keys=True,
                                          separators=(',', ':')).encode()).hexdigest()
        failures = []
        for row in fixture['checks']:
            chi = row['character']
            baseline = replay(events, chi)
            unit = UNITS[chi.bit_count() % 4]
            expected_base = [[unit if i == j else Z for j in range(8)] for i in range(8)]
            require(baseline == expected_base, 'separate dense baseline')
            exponent = -sum((chi & axis).bit_count() % 2 for axis in fixture['removed_axes'])
            require(exponent % 4 == row['omitted_phase_mod4'], 'separate removed phase')
            actual = replay(changed, chi)
            expected = product(baseline, phase(fixture['stream'], exponent))
            require(as_columns(actual) == row['actual_columns'], 'all actual columns agree')
            require(as_columns(expected) == row['expected_columns'], 'all expected columns agree')
            require((actual == expected) is row['matches_input_correction'], 'equality outcome agrees')
            if actual != expected:
                failures.append(chi)
                failed += 1
            if exponent % 4:
                active += 1
                wrong = product(baseline, phase((fixture['stream']+1) % 8, exponent))
                require(wrong != expected, 'wrong input stream discriminates')
            checked += 1
            entries += 64
        if fixture['outcome'] == 'head_cut_passed':
            require(not failures and fixture['is_first_touch_head'], 'head positive guard')
        else:
            require(failures and fixture['witness_character'] == failures[0],
                    'actual nonhead/counterexample witness')
        summaries.append({'owner': fixture['owner'], 'port': fixture['port'],
                          'child': fixture['child'], 'events': len(events),
                          'event_sha256': digest, 'characters': len(fixture['checks']),
                          'mismatch_characters': failures})
    require(active > 0, 'active nontrivial cut coverage')
    return {'schema_version': 1, 'arithmetic': 'separate explicit dense Z[i] matrices',
            'source_projection': 'shared primary extraction; not independently reconstructed',
            'full_8x8_comparisons': checked, 'matrix_entries_compared': entries,
            'active_phase_cases': active, 'observed_cut_mismatches': failed,
            'fixtures': summaries, 'controls': side_and_read_controls()}
