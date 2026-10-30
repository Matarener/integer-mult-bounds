"""Apply the exact PR5739 edits to the PR5751 word.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The edit list and block construction are by Joel Pulikkan (GamingPuzzled),
with Claude Opus 5.5 assistance. The boundary split is by flyingviper. Paid meetings are by Ali Romman
with substantial OpenAI Codex assistance, PR5751.
"""
from copy import deepcopy
import json
from pathlib import Path
from sources import need

HERE = Path(__file__).resolve().parent


def construct(base):
    edits = json.loads((HERE/'source/pr5739/EDITS.json').read_bytes())
    word = deepcopy(base)
    need(len(word['frames']) == 1090, 'Exact source frame count')
    word['frames'] += deepcopy(edits['frames'])
    for key in ('initial', 'final'):
        for register, (old, new) in edits[key].items():
            need(word[key][int(register)] == old, 'Exact source helper endpoint')
            word[key][int(register)] = new
    program = word['program']
    spots = []
    for old, new in edits['program']:
        hits = [i for i in range(len(program)-len(old)+1) if program[i:i+len(old)] == old]
        need(len(hits) == 1, 'One exact source block')
        spots.append((hits[0], old, new))
    spots.sort()
    for (i, old, _), (j, _, _) in zip(spots, spots[1:]):
        need(i+len(old) <= j, 'Disjoint source blocks')
    for i, old, new in reversed(spots):
        program[i:i+len(old)] = deepcopy(new)
    word['schema'] = 'p104-split-block-composition/1'
    return word, [{'index': i, 'old_length': len(old), 'new_length': len(new)} for i, old, new in spots]


def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x^v for x in tuple(out)}
    return frozenset(out)


def interval(word):
    """List every subspace between the required input and output spaces."""
    frame = 1090
    incoming = [e[2] for e in word['program'] if e[0] == 'MOVE' and e[3] == frame]
    outgoing = [e[3] for e in word['program'] if e[0] == 'MOVE' and e[2] == frame]
    need(len(incoming) == len(outgoing) == 8, 'Exact block boundary transport count')
    lower = span(v for f in incoming for v in word['frames'][f])
    upper = frozenset.intersection(*(span(word['frames'][f]) for f in outgoing))
    need(len(lower) == 16 and len(upper) == 256 and lower < upper, 'Exact rank-four to rank-eight interval')
    seen, todo = {lower}, [lower]
    while todo:
        space = todo.pop()
        for v in upper-space:
            extended = space | {x^v for x in space}
            if extended not in seen:
                seen.add(extended)
                todo.append(extended)
    counts = {d: sum(len(s) == 2**d for s in seen) for d in range(4,9)}
    need(counts == {4:1,5:15,6:35,7:15,8:1}, 'All subspaces of the four-dimensional quotient')
    need(span(word['frames'][frame]) == lower, 'Published rank-four frame attains the forced lower space')
    need(all(len(word['frames'][f]) == 3 for f in incoming), 'Eight rank-three input charts')
    need(sorted(len(word['frames'][f]) for f in outgoing) == [8]+[9]*7, 'One rank-eight and seven rank-nine output charts')
    need(word['initial'][741] == frame and word['final'][405] == frame, 'Both changed helper endpoints')
    need(len(word['frames'][word['final'][741]]) == 9 and len(word['frames'][word['initial'][405]]) == 0, 'Helper target ranks depend only on the new chart rank')
    return {'lower': sorted(lower), 'upper': sorted(upper), 'subspaces_by_rank': counts,
            'subspaces': [sorted(s) for s in sorted(seen,key=lambda s:(len(s),sorted(s)))],
            'paid_formula': '8 H_(d-3) + 7 H_(9-d) + H_(8-d), with H_0 = 0',
            'target_formula': 'H_d + H_(9-d)'}
