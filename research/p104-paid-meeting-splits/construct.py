"""Create paid intermediate meetings and independent helper targets.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The helper basis identity follows PR5599/5609. PR5718 supplies the source word.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(word):
    return sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def add(row, source, coefficient):
    for key, value in source.items():
        result = row.get(key, Q(0)) + coefficient*value
        if result:
            row[key] = result
        else:
            row.pop(key, None)


def matrix_at_cut(word, cut, reverse=False):
    size = word['public'] + word['owned_fields']
    rows = [{r: Q(1)} for r in range(size)]
    events = reversed(word['program'][cut:]) if reverse else word['program'][:cut]
    for event in events:
        op, target = event[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            rows[target] = {}
        elif op == 'SCALE':
            rows[target] = {r: Q(event[-2])*x for r, x in rows[target].items()}
        elif reverse:
            add(rows[event[2]], rows[target], Q(event[-2]))
            if op == 'COPY':
                rows[target] = {}
        else:
            if op == 'COPY':
                rows[target] = {}
            add(rows[target], rows[event[2]], Q(event[-2]))
    return rows


def combination(rows, coefficients):
    result = {}
    for role, coefficient in coefficients.items():
        add(result, rows[role], coefficient)
    return result


def fractions(record):
    return {int(role): Q(value) for role, value in record.items()}


def encoded(row):
    return {str(role): str(value) for role, value in sorted(row.items())}


def dyadic_unit(value):
    a, b = abs(value.numerator), value.denominator
    return a > 0 and a & (a-1) == 0 and b & (b-1) == 0


def inverse(event):
    result = event.copy()
    result[-2] = str(1/Q(event[-2]) if event[0] == 'SCALE' else -Q(event[-2]))
    return result


def split(word, cut, frame, plan):
    """Check the exact cut identities, then replace one independent coordinate."""
    public = word['public']
    pivot = plan['pivot']
    a, b = fractions(plan['retirement']), fractions(plan['injection'])
    rows = matrix_at_cut(word, cut)
    columns = matrix_at_cut(word, cut, reverse=True)
    c, d = combination(rows, a), combination(columns, b)
    main = set(word['live']) | {r+112 for r in word['live']}
    need(c and d and all(r < public and r not in main and word['initial'][r] == 3
                        and word['final'][r] == 127 for r in set(c) | set(d)),
         'Both boundary vectors use only full independent helpers')
    need(sum(x*b.get(r, 0) for r, x in a.items()) == 1, 'Unit cut pairing')
    need(sum(x*d.get(r, 0) for r, x in c.items()) == 1, 'Unit boundary pairing')
    need(all(sum(x*d.get(r, 0) for r, x in row.items()) == b.get(i, 0)
             for i, row in enumerate(rows)), 'The prefix sends d to b')
    need(encoded(c) == plan['input'] and encoded(d) == plan['output'],
         'Exact retained boundary functionals')
    need(dyadic_unit(d.get(pivot, Q(0))) and dyadic_unit(a.get(pivot, Q(0))),
         'Both basis pivots are dyadic units')

    before = [['ADD', pivot, r, str(-q), 3] for r, q in sorted(c.items()) if r != pivot]
    if d[pivot] != 1:
        before.append(['SCALE', pivot, str(d[pivot]), 3])
    before += [['ADD', r, pivot, str(q/d[pivot]), 3]
               for r, q in sorted(d.items()) if r != pivot]
    forward = []
    if a[pivot] != 1:
        forward.append(['SCALE', pivot, str(a[pivot]), frame])
    forward += [['ADD', pivot, r, str(q), frame] for r, q in sorted(a.items()) if r != pivot]
    forward += [['ADD', r, pivot, str(-q), frame] for r, q in sorted(b.items()) if r != pivot]
    backward = [inverse(e) for e in reversed(forward)]
    after = [inverse(e) for e in reversed(before)]
    for event in after:
        event[-1] = 127

    def rename(event, continuation):
        event = event.copy()
        for at in (1, 2) if event[0] in ('ADD', 'COPY') else (1,):
            role = event[at]
            event[at] = public if continuation and role == pivot else role+1 if role >= public else role
        return event

    program = [rename(e, False) for e in before + word['program'][:cut] + forward]
    program += [rename(e, True) for e in backward]
    next_cut = len(program)
    program += [rename(e, True) for e in word['program'][cut:] + after]
    result = deepcopy(word)
    result.update(public=public+1, program=program, schema='p104-paid-meeting-splits/1')
    result['initial'].append(frame)
    result['final'].append(127)
    result['final'][pivot] = frame
    receipt = dict(cut=cut, next_cut=next_cut, frame=frame, pivot=pivot, fresh=public,
                   input=encoded(c), output=encoded(d), retirement=encoded(a), injection=encoded(b),
                   basis_operations=len(before)+len(forward)+len(backward)+len(after))
    return result, next_cut, receipt


def construct(source, plan):
    need(digest(source) == plan['source_word_sha256'], 'Pinned canonical PR5718 word')
    word = deepcopy(source)
    receipts = []
    for meeting in plan['meetings']:
        cut, frame = meeting['cut'], meeting['frame']
        partials = []
        for move in meeting['moves']:
            index, expected = move['event'], move['event_value']
            need(index >= cut and word['program'][index] == expected, 'Pinned future native query')
            role = expected[1]
            need(not any(role in (e[1:3] if e[0] in ('ADD', 'COPY') else e[1:2])
                         for e in word['program'][cut:index]), 'No field access before the advanced query')
            partials.append(['MOVE', role, expected[2], frame, expected[4]])
            word['program'][index][2] = frame
        word['program'][cut:cut] = partials
        cut += len(partials)
        steps = []
        for step in meeting['splits']:
            word, cut, receipt = split(word, cut, frame, step)
            steps.append(receipt)
        receipts.append(dict(frame=frame, added_queries=len(partials), steps=steps))
    need(word['public'] == source['public']+sum(len(x['splits']) for x in plan['meetings']),
         'One new independent input per split')
    return word, dict(source_word_sha256=digest(source), word_sha256=digest(word), meetings=receipts)
