"""Construct the R22 reorder+reframe word from PR5678's P104 word.

Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic) via Claude Code. Apache-2.0.

Helper 473 starts on the empty chart 3 instead of the one-dimensional chart 594.
Its read into 213 commutes ahead of the T/T-commuting ADD 213 += 2*706, so it runs on
chart 3; 473 then waits on chart 3 and takes the update from 100 on the
three-dimensional chart 716 instead of 718, so 100 never moves 716 -> 718.
Helper 733 moves 597 -> 772 (dim 1 -> 4) before its read into 585 instead of 597 -> 794 (dim 6),
so 585 += -4*733 runs on chart 772 instead of 597 and 438 += -4*733 on 772 instead of 794.
Each edit replaces one exact, unique run of events.
"""
from copy import deepcopy

HELPER, OLD_START, NEW_START = 473, 594, 3

EDITS = [
    ([['MOVE', 213, 3, 594, False], ['ADD', 213, 706, '2', 594]], []),
    ([['ADD', 213, 473, '1/2', 594]],
     [['ADD', 213, 473, '1/2', 3], ['MOVE', 213, 3, 594, False], ['ADD', 213, 706, '2', 594]]),
    ([['MOVE', 100, 716, 718, False]], []),
    ([['MOVE', 473, 594, 718, False]], [['MOVE', 473, 3, 716, False]]),
    ([['ADD', 473, 100, '1', 718]], [['ADD', 473, 100, '1', 716]]),
    ([['MOVE', 473, 718, 719, False]], [['MOVE', 473, 716, 719, False]]),
    ([['MOVE', 100, 718, 783, False]], [['MOVE', 100, 716, 783, False]]),
    ([['MOVE', 585, 3, 597, False], ['ADD', 585, 733, '-4', 597], ['MOVE', 585, 597, 772, False]],
     [['MOVE', 585, 3, 772, False], ['MOVE', 733, 597, 772, False], ['ADD', 585, 733, '-4', 772]]),
    ([['MOVE', 438, 772, 794, False], ['MOVE', 733, 597, 794, False], ['ADD', 438, 733, '-4', 794]],
     [['ADD', 438, 733, '-4', 772], ['MOVE', 438, 772, 794, False]]),
    ([['MOVE', 733, 794, 127, False]], [['MOVE', 733, 772, 127, False]]),
]


def locate(program, run):
    hits = [i for i in range(len(program) - len(run) + 1) if program[i:i+len(run)] == run]
    assert len(hits) == 1, ('unique source run', run, hits)
    return hits[0]


def construct(base, schema='p104-r22-reframe/1'):
    word = deepcopy(base)
    assert word['initial'][HELPER] == OLD_START, 'Source helper start'
    word['initial'][HELPER] = NEW_START
    program = word['program']
    spots = sorted(((locate(program, old), old, new) for old, new in EDITS), reverse=True)
    for i, old, new in spots:
        program[i:i+len(old)] = deepcopy(new)
    word['schema'] = schema
    return word
