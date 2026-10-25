#!/usr/bin/env python3
"""Signed exact free-warp replay and restricted dirty-response correction.

SOURCE, TARGET, wrapped inputs and every non-TARGET output are protected.
Only unwrapped zero-entrance/full-exit helper inputs can supply new twisted
TARGET corrections. This is separate from the independent native checker.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from commute_birth import F


def add(row, other, coefficient):
    for key, value in tuple(other.items()):
        value = row.get(key, Q(0)) + coefficient * value
        if value:
            row[key] = value
        else:
            row.pop(key, None)


def execute(rows, event):
    kind, d = event[:2]
    if kind == 'add':
        add(rows[d], rows[event[2]], Q(event[3], event[4]))
    elif kind == 'scale':
        coefficient = Q(event[2], event[3])
        rows[d] = {key: coefficient * value for key, value in rows[d].items() if coefficient * value}
    elif kind == 'warp':
        op = event[2]
        rows[d] = {(var, word[1:] if word and word[0] == -op else (op,) + word): value
                   for (var, word), value in rows[d].items()}
    else:
        raise ValueError(kind)


def replay(word, source_only=False):
    live = set(range(704)) - set(word['removed'])
    rows = {r: {(r, ()): Q(1)} if not source_only or r < 112 else {} for r in live}
    for term in word['initial_corrections']:
        s = term['source']
        assert not 112 <= s < 224
        if not source_only or s < 112:
            add(rows[term['target']], {(s, tuple(term['operator_word'])): Q(1)}, Q(term['coefficient']))
    for event in word['precondition'] + word['compensation'] + word['A']:
        execute(rows, event)
    captures = {r: dict(rows[r]) for r in word['centers']}
    for event in word['cut']:
        execute(rows, event)
    for event in F.expand(word)['B'] + word['restore']:
        execute(rows, event)
    for r in word['helper_final']:
        rows[704 + int(r)] = {}
    for event in word['cleanup']:
        execute(rows, event)
    return rows, captures


def expected(word, source_only=False):
    live = set(range(704)) - set(word['removed'])
    out = {r: {(r, ()): Q(1)} if not source_only or r < 112 else {} for r in live}
    for r in range(112, 224):
        out[r][r - 112, ()] = Q(1)
    for r in word['helper_final']:
        out[704 + int(r)] = {}
    return out


def repair(word):
    """Add the exact negative output error before the fixed TARGET map."""
    allowed = set(range(224, 704)) - set(word['removed']) - set(map(int, word['start_extra'])) - set(map(int, word['helper_final']))
    # Every TARGET input propagates through the same fixed TARGET-only word.
    for section in ('precondition', 'compensation', 'A', 'B', 'restore', 'cleanup'):
        assert all(not (e[0] == 'add' and 112 <= e[2] < 224 and not 112 <= e[1] < 224)
                   for e in word[section])
    F.derive_cleanup(word)
    rows, _ = replay(word)
    want = expected(word)
    corrections = []
    for r, row in rows.items():
        error = dict(row)
        add(error, want[r], Q(-1))
        if not error:
            continue
        if not 112 <= r < 224:
            raise ValueError(('non_TARGET_output_changed', r, len(error)))
        for (source, operators), value in sorted(error.items()):
            if source not in allowed:
                raise ValueError(('protected_input_changed', r, source, operators))
            assert value.denominator & (value.denominator - 1) == 0
            corrections.append({'target': r, 'source': source, 'operator_word': list(operators), 'coefficient': str(-value)})
    word['initial_corrections'] += corrections
    rows, _ = replay(word)
    assert rows == want, 'new initial corrections must produce exact all-input identity'
    return {'new_initial_corrections': len(corrections),
            'allowed_zero_frame_full_exit_helpers': len(allowed),
            'all_independent_live_inputs': len(want) - len(word['helper_final']),
            'all_zero_buffers_restored': len(word['helper_final']),
            'exact_free_operator_identity': True}
