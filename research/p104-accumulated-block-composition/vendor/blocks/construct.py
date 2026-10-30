"""Compose Joel Pulikkan's exact R22 block with the released native copies.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The two source constructions retain their authorship and notices.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from sources import need

HERE = Path(__file__).resolve().parent


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def construct(source):
    edits = json.loads((HERE/'source/R22-EDITS.json').read_bytes())
    word = deepcopy(source)
    need(len(word['frames']) == 1092 and len(edits['frames']) == 1,
         'Exact source chart inventories')
    need(word['frames'][1090] == edits['frames'][0], 'Existing chart has the exact R22 basis')
    for kind in ('initial', 'final'):
        for label, (old, new) in edits[kind].items():
            need(word[kind][int(label)] == old and new == 1090, 'Exact helper endpoint join')
            word[kind][int(label)] = new
    program, spots = word['program'], []
    for index, (old, new) in enumerate(edits['program']):
        hits = [i for i in range(len(program)-len(old)+1) if program[i:i+len(old)] == old]
        need(len(hits) == 1, 'One exact R22 source run: '+str(index))
        spots.append((hits[0], old, new))
    spots.sort()
    need(len(spots) == 8, 'All eight source edits')
    for (i, old, _), (j, _, _) in zip(spots, spots[1:]):
        need(i+len(old) <= j, 'Disjoint source runs')
    for i, old, new in reversed(spots):
        program[i:i+len(old)] = deepcopy(new)
    preserve = lambda w: [e for e in w['program'] if e[0] in ('INIT', 'COPY', 'CLEAR')]
    need(preserve(word) == preserve(source), 'Every owned lifetime and COPY event is retained in order')
    need(word['owned_fields'] == source['owned_fields'] == 25, 'No extra owned label')
    word['schema'] = 'p104-copy-block-composition/1'
    witness = [dict(source_index=i, old_length=len(old), new_length=len(new),
                    old_sha256=digest(old), new_sha256=digest(new)) for i, old, new in spots]
    from second_block import extend
    word, second = extend(word)
    need(preserve(word) == preserve(source), 'Both blocks retain every owned lifetime and COPY event')
    return word, dict(R22=witness, second_block=second)
