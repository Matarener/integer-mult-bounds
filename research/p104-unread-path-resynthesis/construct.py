"""Replace one unread path by its exact endpoint-frame updates.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json
from sources import need


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def transfer(events, roles):
    """Compute the transfer on arbitrary values at the four entry fields."""
    rows = {r: [Q(r == s) for s in roles] for r in roles}
    for e in events:
        if e[0] == 'MOVE':
            continue
        need(e[0] == 'ADD', 'The local identity uses only ADD and MOVE')
        _, r, s, q, _ = e
        rows[r] = [a+Q(q)*b for a, b in zip(rows[r], rows[s])]
    return [[str(v) for v in rows[r]] for r in roles]


def construct(source, plan):
    old = [['MOVE', 773, 1031, 597, True], ['ADD', 709, 773, '1', 597],
           ['MOVE', 733, 3, 597, False], ['ADD', 733, 773, '1', 597],
           ['MOVE', 695, 3, 597, False], ['ADD', 695, 733, '1', 597],
           ['MOVE', 695, 597, 1031, False]]
    new = [['ADD', 695, 733, '1', 3], ['MOVE', 695, 3, 1031, False],
           ['ADD', 695, 773, '1', 1031]] + old[:4]
    need(plan == {'start': 13815, 'old': old, 'new': new}, 'Exact seven-event plan')
    program = source['program']
    hits = [i for i in range(len(program)-len(old)+1) if program[i:i+len(old)] == old]
    need(hits == [plan['start']], 'One exact source interval')
    roles = [695, 709, 733, 773]
    matrix = transfer(old, roles)
    need(matrix == transfer(new, roles), 'All coefficients of the four-field transfer')
    word = deepcopy(source)
    word['program'][plan['start']:plan['start']+len(old)] = deepcopy(new)
    need(word['initial'] == source['initial'] and word['final'] == source['final'],
         'Every public boundary is unchanged')
    owned = lambda w: [e for e in w['program'] if e[1] >= w['public']]
    need(owned(word) == owned(source), 'Every owned event is unchanged')
    need(len(word['program']) == len(source['program']) == 25984, 'Fixed event count')
    return word, {'start': plan['start'], 'roles': roles, 'transfer': matrix,
                  'source_word_sha256': digest(source), 'word_sha256': digest(word),
                  'old_events_sha256': digest(old), 'new_events_sha256': digest(new)}
