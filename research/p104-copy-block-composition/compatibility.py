"""Check every R22 scalar transfer and preservation of retained copy values.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The R22 edit list and retained-copy construction keep their original credit.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
from sources import sources, need
from construct import construct, digest


def matrix(events, fields):
    rows = {r: [Q(x == r) for x in fields] for r in fields}
    for event in events:
        if event[0] == 'ADD':
            _, dst, src, value, frame = event
            rows[dst] = [x+Q(value)*y for x, y in zip(rows[dst], rows[src])]
        elif event[0] == 'SCALE':
            _, dst, value, frame = event
            rows[dst] = [Q(value)*x for x in rows[dst]]
        else:
            need(event[0] == 'MOVE', 'No COPY or lifetime boundary inside an edit')
    return [[str(x) for x in rows[r]] for r in fields]


def run():
    with sources() as (parent, root):
        source = json.loads(gzip.decompress((parent/'WORD.json.gz').read_bytes()))
        word, spots = construct(source)
        retained = json.loads(gzip.decompress((HERE/'WORD.json.gz').read_bytes()))
        need(word == retained, 'Exact composed word')
        need(spots == json.loads((HERE/'HUNKS.json').read_bytes()), 'Exact literal edit positions')
        edits = json.loads((HERE/'source/R22-EDITS.json').read_bytes())
        witnesses = []
        for i, (old, new) in enumerate(edits['program']):
            fields = sorted({r for e in old+new if e[0] in ('ADD', 'SCALE')
                             for r in (e[1:3] if e[0] == 'ADD' else [e[1]])})
            a, b = matrix(old, fields), matrix(new, fields)
            need(a == b, 'Same exact scalar transfer for source edit '+str(i))
            witnesses.append(dict(edit=i, fields=fields, matrix=a))
        bad = deepcopy(edits['program'][0][1])
        first = next(e for e in bad if e[0] == 'ADD')
        first[3] = str(Q(first[3])+1)
        need(matrix(bad, witnesses[0]['fields']) != witnesses[0]['matrix'],
             'Reject one wrong scalar coefficient in the first edit')
        old_events = [e for e in source['program'] if e[0] in ('INIT', 'COPY', 'CLEAR')]
        new_events = [e for e in word['program'] if e[0] in ('INIT', 'COPY', 'CLEAR')]
        need(old_events == new_events, 'Every copied source and lifetime event remains in order')
        copies = [e for e in old_events if e[0] == 'COPY' and source['public']+9 <= e[1] < source['public']+22]
        need(len(copies) == 13, 'All thirteen retained native copies')
        return dict(status='PASS_R22_SCALAR_TRANSFERS_AND_ALL_13_COPY_VALUES',
                    word_sha256=digest(word), edits=witnesses, retained_copies=copies,
                    all_copy_events=[e for e in old_events if e[0] == 'COPY'],
                    second_block_scalar_transfer_sha256=spots['second_block']['scalar_transfer_sha256'],
                    second_block_contacts=len(spots['second_block']['changed_scalar_source_indices']),
                    proof='Disjoint equal R22 scalar transfers and no internal COPY preserve all external COPY values. The second block changes only scalar frames and preserves every scalar coefficient and order. Native frames and phases are checked by the complete verifier.',
                    wrong_scalar_coefficient_rejected=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='copy-block-compatibility-') as cache:
        sys.pycache_prefix = cache
        result = run()
    path = HERE/'COMPATIBILITY.json'
    if args.write:
        path.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == result, 'Exact compatibility certificate')
    print(result['status'])


if __name__ == '__main__':
    main()
