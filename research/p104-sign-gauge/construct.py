#!/usr/bin/env python3
"""Scalar sign gauges for the frozen P104 word; no native phase edits.

Charan / theon199 with substantial OpenAI Codex assistance. Apache-2.0.
Sign normalization precedents: Ross Richardson #919 and Scratch-net #1153.
"""
from copy import deepcopy
from fractions import Fraction


def normalize(word):
    """Return the complete word and source-cut -> candidate-cut map.

    Invariant: original[r] = signs[r] * emitted[r]. MOVE is any linear map
    on that whole role. INIT/CLEAR have the inherited owned-erasure meaning.
    All boundary corrections are explicit; no input sign is assumed free.
    """
    result = deepcopy(word)
    signs = [1] * (word['public'] + 8)
    events, cuts = [], []
    for event in word['program']:
        e = event.copy()
        op, r = e[:2]
        if op == 'SCALE':
            q = Fraction(e[-2])
            if q == 0:
                raise ValueError('Zero SCALE is not invertible')
            if q < 0:
                signs[r] *= -1
            q = abs(q)
            if q != 1:
                e[-2] = str(q)
                events.append(e)
        elif op == 'ADD':
            e[-2] = str(Fraction(e[-2]) * signs[r] * signs[e[2]])
            events.append(e)
        elif op == 'COPY':
            # Destination is owned and cleared; retain the coefficient itself.
            signs[r] = signs[e[2]]
            events.append(e)
        elif op in ('INIT', 'CLEAR'):
            signs[r] = 1
            events.append(e)
        elif op == 'MOVE':
            events.append(e)
        else:
            raise ValueError(f'Unsupported opcode: {op}')
        cuts.append(len(events))
    for r in range(word['public']):
        if signs[r] == -1:
            events.append(['SCALE', r, '-1', word['final'][r]])
    result['program'] = events
    return result, cuts
