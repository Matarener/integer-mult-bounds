"""Change one contact on the PR5569 P104 word.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source word is by GamingPuzzled, DreamingOfClouds, thu-nmrc,
Ali Romman and the retained P104 contributors. See README.md.
"""
from copy import deepcopy


def need(ok, why):
    if not ok:
        raise ValueError(why)


def construct(source):
    word = deepcopy(source)
    old = source['program']
    expected = {
        9575: ['ADD', 228, 225, '1', 262],
        12591: ['ADD', 160, 451, '1/2', 3],
        12657: ['MOVE', 451, 3, 262, False],
        12658: ['ADD', 451, 228, '1', 262],
        12673: ['MOVE', 228, 262, 520, False],
        12674: ['ADD', 497, 228, '1', 520],
        14422: ['MOVE', 451, 262, 737, False],
        14424: ['ADD', 451, 732, '-4', 737],
    }
    need(len(old) == 25140, 'Exact source event count')
    need(all(old[i] == e for i, e in expected.items()), 'Exact source contacts')
    for r, start, stop, visits in (
            (228, 9576, 12674, [12658, 12673]),
            (451, 12592, 14424, [12657, 12658, 14422])):
        actual = []
        for i in range(start, stop):
            e = old[i]
            used = e[1:3] if e[0] in ('ADD', 'COPY') else e[1:2]
            if r in used:
                actual.append(i)
        need(actual == visits, 'No other contact in the changed interval')
    replacement = {
        12657: [['MOVE', 228, 262, 737, False],
                ['MOVE', 451, 3, 737, False]],
        12658: [['ADD', 451, 228, '1', 737]],
        12673: [['MOVE', 228, 737, 520, False]],
        14422: [],
    }
    word['program'] = [e for i, old_event in enumerate(old)
                       for e in replacement.get(i, [deepcopy(old_event)])]
    need(len(word['program']) == len(old), 'Same event count')
    return word
