"""Change three coupled charts on the PR5565 P104 cascade.

DreamingOfClouds supplied the event-lattice search used for discovery.
Ali Romman prepared this composition and exact certificate with substantial
OpenAI Codex assistance. Apache-2.0. See SOURCES.json and README.md.
"""
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def construct(source):
    declaration = json.loads(Path(__file__).with_name('CHANGES.json').read_text())
    changes = declaration['changes']
    need(len(changes) == 4 and len(source['program']) == 25133,
         'Exact source and edit counts')
    word = deepcopy(source)
    need(len(source['frames']) == 1089, 'Exact source frame count')
    word['frames'].extend(declaration['frames'])
    old, new = source['program'], word['program']
    for change in changes:
        if 'event' in change:
            i = change['event']
            need(old[i] == change['old'], 'Exact source event')
            new[i][-1] = change['new_frame']
        else:
            key, r = change['endpoint'], change['register']
            need(source[key][r] == change['old_frame'], 'Exact source endpoint')
            word[key][r] = change['new_frame']
    anchors = {r: [(-1, source['initial'][r], word['initial'][r])]
               for r in range(source['public'])}
    moves = defaultdict(list)
    for i, event in enumerate(old):
        op, r = event[:2]
        if op == 'MOVE':
            moves[r].append(i)
        elif op in ('ADD', 'COPY', 'SCALE'):
            registers = event[1:3] if op != 'SCALE' else event[1:2]
            for r in registers:
                if r in anchors:
                    anchors[r].append((i, event[-1], new[i][-1]))
    remove, before = set(), defaultdict(list)
    for r, visits in anchors.items():
        visits.append((len(old), source['final'][r], word['final'][r]))
        for (i, a, x), (j, b, y) in zip(visits, visits[1:]):
            if (a, b) == (x, y):
                continue
            remove.update(k for k in moves[r] if i < k < j)
            if x != y:
                before[j].append(['MOVE', r, x, y, False])
    program = []
    for i, event in enumerate(new):
        program.extend(before[i])
        if i not in remove:
            program.append(event)
    program.extend(before[len(old)])
    word['program'] = program
    need(len(program) == 25132, 'One fewer paid transport')
    return word
