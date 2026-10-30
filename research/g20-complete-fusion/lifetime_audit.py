"""Check whole-zero storage and prior same-frame rows of the completed word."""
from hashlib import sha256
import json
import gzip
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import fusion as F


def main():
    word, owned, _, _ = F.baseline()
    _, hits = F.discover()
    rows = [1 << i for i in range(660)]
    available = {c['helper']: set(owned) for c in hits}
    intervals = {c['helper']: [c['capture'], c['indices'][0]] for c in hits}
    for ix, event in enumerate(word):
        for helper, (start, end) in intervals.items():
            if start <= ix <= end:
                available[helper] -= {h for h in owned if rows[h]}
        op, dest = event[:2]
        if op == 'ADD':
            rows[dest] ^= rows[event[2]]
        elif op == 'ERASE':
            rows[dest] = 0
    F.need(all(v == {658} for v in available.values()), 'Exactly one reusable whole-zero bank')
    F.need(max(a for a,b in intervals.values()) <= min(b for a,b in intervals.values()), 'Three snapshot lifetimes overlap')
    completed = json.load(gzip.open(F.R/'WORD.json.gz', 'rt'))
    rows = [1 << i for i in range(len(completed['start']))]
    frames = completed['start'][:]
    bases = {}
    def add(dest):
        if frames[dest] is None:
            return
        row = rows[dest]
        basis = bases.setdefault(frames[dest], {})
        while row:
            pivot = (row & -row).bit_length()-1
            if pivot not in basis:
                basis[pivot] = row
                return
            row ^= basis[pivot]
    for dest in range(len(rows)):
        add(dest)
    queries = 0
    digest = sha256()
    for ix, event in enumerate(completed['records']):
        op, dest = event[:2]
        if op == 'Q' and rows[dest]:
            queries += 1
            row = rows[dest]
            for pivot, value in sorted(bases.get(event[3], {}).items()):
                if row >> pivot & 1:
                    row ^= value
            F.need(row != 0, 'Query row has no earlier same-frame reconstruction')
            digest.update((str(ix)+':'+hex(row)+'\n').encode())
        if op == 'ADD':
            rows[dest] ^= rows[event[2]]
        elif op == 'ERASE':
            rows[dest] = 0
            frames[dest] = event[2]
        elif op == 'INIT':
            frames[dest] = event[2]
        else:
            frames[dest] = event[3]
        add(dest)
    result = {'status':'PASS_COMPLETE_G20_STORAGE_AND_HISTORY',
              'original_owned':sorted(owned), 'intervals':intervals,
              'whole_zero_candidates':{k:sorted(v) for k,v in available.items()},
              'new_banks_for_direct_copy_schedule':2,
              'paid_queries_checked':queries,
              'historical_span_rank_sum':sum(map(len,bases.values())),
              'query_reconstruction_hits':0,'nonzero_residual_sha256':digest.hexdigest(),
              'scope':'Direct snapshots with unchanged producers; no claim about changed words, encodings or paid frame conversions.'}
    F.put('LIFETIME-AUDIT.json', result)
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
