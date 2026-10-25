"""Move one P104 contact to the full frame.

The two-operand transport identity is standard. The source is PR5544,
PR2305, David Arias's coalesced word and Cinna Davis's private reuse.
Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
import local as L


def construct(source):
    word = deepcopy(source)
    old = source['program']
    expected = {
        16798: ['MOVE', 345, 739, 240, False],
        16799: ['ADD', 341, 345, '-1', 240],
        16800: ['SCALE', 341, '-1', 240],
        17061: ['MOVE', 341, 240, 127, False],
        17067: ['MOVE', 345, 240, 127, False],
    }
    L.need(all(old[i] == e for i,e in expected.items()), 'Exact source contact')
    L.need(source['frames'][739] == [30,70,429], 'Source three-plane')
    L.need(source['frames'][240] == [13,19,70,416], 'Source four-plane')
    L.need(source['frames'][127] == [1,2,4,8,16,32,64,128,256], 'Full frame')
    for role, end in ((341,17061),(345,17067)):
        touched = []
        for i in range(16798,end):
            e = old[i]
            used = e[1:3] if e[0] in ('ADD','COPY') else e[1:2]
            if role in used:
                touched.append(i)
        L.need(touched == ([16799,16800] if role == 341 else [16798,16799]),
               'No intervening read or write')
    replacement = {
        16798: [['MOVE',341,240,127,False], ['MOVE',345,739,127,False]],
        16799: [['ADD',341,345,'-1',127]],
        16800: [['SCALE',341,'-1',127]],
        17061: [],
        17067: [],
    }
    word['program'] = [e for i,old_event in enumerate(old)
                       for e in replacement.get(i,[deepcopy(old_event)])]
    # Scalar coefficients and their order are equal in both words.
    def scalars(program):
        return [e[:-1] for e in program if e[0] != 'MOVE']
    L.need(scalars(word['program']) == scalars(old), 'Same scalar and owned word')
    L.need(len(word['program']) == len(old)-1 == 25310, 'One fewer paid event')
    return word
