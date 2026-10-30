"""Distribute one scalar update over an interval without a target read.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from collections import defaultdict
from hashlib import sha256
import json
from sources import need


def add(dst, src, coefficient):
    for column, value in src.items():
        value = dst.get(column, Q(0)) + coefficient * value
        if value:
            dst[column] = value
        else:
            dst.pop(column, None)


def identity(word, witness):
    role = witness['role']
    start, stop = witness['start'], witness['stop']
    removed = witness['removed_event']
    need(0 <= role < word['public'] and 0 <= start <= removed < stop <= len(word['program']),
         'One public target and a bounded interval')
    old = word['program'][removed]
    need(old[0] == 'ADD' and old[1] == role, 'One removed target update')
    terms = defaultdict(list)
    for term in witness['inserts']:
        need(start <= term['cut'] <= stop and term['source'] != role,
             'Replacement source and cut are in scope')
        terms[term['cut']].append(term)
    rows = [{r: Q(1)} for r in range(word['public'] + word['owned_fields'])]
    frames = word['initial'][:] + [None] * word['owned_fields']
    total, expected, observations = {}, {}, []
    for index in range(stop + 1):
        for term in terms.get(index, []):
            source, frame, coefficient = term['source'], term['frame'], Q(term['coefficient'])
            need(coefficient and frames[role] == frames[source] == frame,
                 'Each replacement has an actual common frame')
            add(total, rows[source], coefficient)
            observations.append([index, source, frame, len(rows[source])])
        if index == stop:
            break
        event = word['program'][index]
        op, target = event[:2]
        if start <= index < stop:
            need(not (op in ('ADD', 'COPY') and event[2] == role),
                 'No original instruction reads the changed target')
            need(not (target == role and op in ('SCALE', 'COPY', 'INIT', 'CLEAR')),
                 'The changed target has only additive writes and native moves')
        if index == removed:
            add(expected, rows[event[2]], Q(event[-2]))
        if op == 'MOVE':
            frames[target] = event[3]
        elif op in ('INIT', 'CLEAR'):
            rows[target] = {}
            frames[target] = event[2] if op == 'INIT' else None
        elif op == 'SCALE':
            rows[target] = {j: Q(event[-2]) * value for j, value in rows[target].items()}
        elif op == 'COPY':
            rows[target] = {j: Q(event[-2]) * value for j, value in rows[event[2]].items()}
        else:
            need(op == 'ADD', 'Known scalar instruction')
            add(rows[target], rows[event[2]], Q(event[-2]))
    need(total == expected and expected, 'Exact distributed source functional')
    encoded = [[j, str(value)] for j, value in sorted(expected.items())]
    return {'start': start, 'stop': stop, 'removed_event': removed, 'role': role,
            'source_coefficients': len(expected), 'observations': observations,
            'source_sha256': sha256(json.dumps(encoded, separators=(',', ':')).encode()).hexdigest()}


def construct(source, witness):
    receipt = identity(source, witness)
    role = witness['role']
    a, b, c = witness['old_frames']
    first, last = witness['removed_move'], witness['merged_move']
    need(source['program'][first] == ['MOVE', role, a, b, False]
         and source['program'][last] == ['MOVE', role, b, c, False],
         'Exact two source transports')
    need(first < witness['removed_event'] < last, 'Removed contact lies between the transports')
    inserts = defaultdict(list)
    for term in witness['inserts']:
        inserts[term['cut']].append(['ADD', role, term['source'], term['coefficient'], term['frame']])
    word = deepcopy(source)
    program = []
    for index, event in enumerate(source['program']):
        program.extend(deepcopy(inserts.get(index, [])))
        if index in (first, witness['removed_event']):
            continue
        program.append(['MOVE', role, a, c, False] if index == last else deepcopy(event))
    program.extend(deepcopy(inserts.get(len(source['program']), [])))
    word['program'] = program
    word['schema'] = 'p104-temporal-updates/1'
    return word, receipt
