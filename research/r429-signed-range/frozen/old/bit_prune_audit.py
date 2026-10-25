#!/usr/bin/env python3
"""Independent deletion of unread R438 factory leaves, complete651-column audit.

The discarded physical families are not retained with wrong endpoint frames.
Every surviving record is the literal projected support-code signed word.
Apache-2.0; substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bit_cap_copy_local as cap
import bit_signed_audit as scalar
import bit_raw_defect as algebra

HERE = Path(__file__).resolve().parent
need = cap.need


def projected(program):
    dead = [h for h in range(222,660)
            if all(not(op == 1 and s == h or op in (2,3) and d == h)
                   for op,d,s,c,f,p in program['records'])]
    need(dead == list(range(471,480)),'unread physical helper classification')
    dead_set = set(dead)
    keep = [p for p in range(660) if p not in dead_set]
    mapping = {old:new for new,old in enumerate(keep)}
    mapping[660] = len(keep)
    records = []
    removed = Counter()
    for op,d,s,c,f,p in program['records']:
        if d in dead_set:
            need(op in (0,1),'discarded helper has an owned snapshot role')
            if op == 0:
                removed[f] += 1
            continue
        need(op == 0 or s not in dead_set,'remaining record reads discarded input')
        records.append([op,mapping[d],s if op == 0 else mapping[s],c,f,p])
    return keep,records,dict(sorted(removed.items()))


def execute(word,keep,records,backward=False,initial=None):
    n = len(keep)
    rows = ([{i:1} for i in range(n)]+[{}]) if initial is None else [r.copy() for r in initial]
    frames = [word['final' if backward else 'start'][i] for i in keep]+[None]
    dims = [cap.rank(word['lines'][j] for j in f) for f in word['frames']]
    masks = [sum(1 << j for j in f) for f in word['frames']]
    opened,copies,prefix = None,0,1
    profile,counts = Counter(),Counter()
    for op,d,s,c,f,p in reversed(records) if backward else records:
        counts[op] += 1
        if op == 0:
            old,new = (c,s) if backward else (s,c)
            lo,hi = (new,old) if backward else (old,new)
            need(frames[d] == old and not masks[lo] & ~masks[hi] and dims[hi]-dims[lo] == f > 0,'projected MOVE frame/rank')
            frames[d] = new
            profile[f] += 1
        elif op == 1:
            need(d < n and d != s and frames[d] == frames[s] == f and d != opened,'projected common-frame ADD or snapshot source mutation')
            rows[d] = scalar.add(rows[d],rows[s],-c if backward else c)
            prefix = max(prefix,sum(abs(v) for v in rows[d].values()))
        elif op == (3 if backward else 2):
            need(opened is None and s == n and not rows[n] and frames[n] is None,'projected fresh private field')
            need(d < 111 and frames[d] == c == 1 and not masks[f] & ~masks[c] and dims[c]-dims[f] == 1,'projected actual source cap COPY')
            rows[n],frames[n],opened = rows[d].copy(),f,d
            profile[1] += 1
            copies += 1
        else:
            need(op == (2 if backward else 3) and opened == d and s == n and rows[n] == rows[d] and frames[d] == c and frames[n] == f,'projected immutable snapshot ERASE')
            rows[n],frames[n],opened = {},None,None
    need(opened is None and not rows[n] and frames[n] is None and copies == 3,'projected private endpoint')
    need(frames[:n] == [word['start' if backward else 'final'][i] for i in keep],'retained physical endpoint frames')
    need(profile == Counter({1:1298,2:1342,3:79,4:44,5:93,6:11,7:9}),'projected paid profile')
    need(counts == Counter({0:2873,1:13223,2:3,3:3}),'projected literal record counts')
    return rows,{'prefix_row_l1':prefix,'profile':dict(sorted(profile.items())),
                 'rank_mass':sum(k*v for k,v in profile.items()),'copies':copies,
                 'counts':dict(sorted(counts.items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    packed = (HERE/'BIT-SUPPORT-INPUT-WORD.json.gz').read_bytes()
    need(sha256(packed).hexdigest() == '6e4e79c3d4fc9f8d01e3c2429d6794c057214f5bae9f8ab86c03d549f01922f1','frozen support-code word pin')
    program = json.loads(gzip.decompress(packed))
    raw = cap.RAW.read_bytes()
    need(sha256(raw).hexdigest() == cap.RAW_SHA,'raw R438 source pin')
    word = json.loads(gzip.decompress(raw))
    keep,records,removed = projected(program)
    need(len(keep) == 651 and removed == {1:27,5:9},'physical family/paid removal')
    frozen = json.loads((HERE/'BIT-THREE-ROW-INPUT.json').read_bytes())['matrices']
    w = frozen['K'][:]
    for p in (0,1,2):
        w[p] = 0
    a = [r ^ (1 << p) for p,r in enumerate(algebra.product(w,frozen['R']))]
    ainv = algebra.inverse(a)
    code_records,code_rows,code_prefix,code_norm = scalar.code(records)
    need(len(code_records) == 1499 and scalar.parity(code_rows[0]) == a and scalar.parity(code_rows[1]) == ainv,'projected exact source code')
    receipts,outputs = [],[]
    for backward in (False,True):
        rows,receipt = execute(word,keep,records,backward)
        need(rows[:111] == code_rows[int(backward)],'source has dirt/target dependence')
        expected = [1 << p for p in range(651)]+[0]
        for p in range(111):
            expected[p] = ainv[p] if backward else a[p]
            expected[111+p] ^= (1 << p) if backward else a[p]
            need(rows[111+p].get(111+p) == 1 and all(j < 111 or j == 111+p or j >= 222 for j in rows[111+p]),'integer target self block')
            need(all(not c & 1 for j,c in rows[111+p].items() if j >= 222),'integer odd helper leakage')
        need(scalar.parity(rows) == expected,'all651 arbitrary binary input columns')
        for h in range(222,651):
            need(rows[h] == {h:1},'all429 arbitrary dirty helpers restored over Z')
        outputs.append(rows)
        receipts.append(receipt)
    roundtrip,_ = execute(word,keep,records,True,outputs[0])
    need(roundtrip == [{i:1} for i in range(651)]+[{}],'full651-column integer roundtrip')
    # A surviving target read of a removed leaf would invalidate the structural
    # proof before any projected algebra could be evaluated.
    bad = dict(program)
    bad['records'] = program['records']+[[1,111,471,1,0,99]]
    try:
        projected(bad)
    except ValueError as error:
        control = str(error)
    else:
        raise ValueError('restored dead-leaf read mutation escaped')
    receipt = {'status':'PASS_INDEPENDENT_NINE_DEAD_HELPER_REMOVAL_651_COLUMNS_LOCAL_ONLY',
               'input_support_word_sha256':sha256(gzip.decompress(packed)).hexdigest(),
               'projected_records_sha256':sha256(cap.canonical(records)).hexdigest(),
               'projected_start_sha256':sha256(cap.canonical([word['start'][p] for p in keep])).hexdigest(),
               'projected_final_sha256':sha256(cap.canonical([word['final'][p] for p in keep])).hexdigest(),
               'discarded_old_physical_families':list(range(471,480)),
               'retained_old_physical_families':keep,'new_public_families':651,'new_dirty_helpers':429,
               'removed_profile':removed,'removed_rank_mass':72,
               'saved_rank_mass_from_R438':132,'remaining_profile_mass':4989,
               'forward':receipts[0],'literal_inverse':receipts[1],
               'all651_integer_roundtrip':True,'source_code_exact_prefix':code_prefix,
               'source_code_endpoint_norm':code_norm,'negative_control':control,
               'owner_scope':'Restricting an old legal owner assignment to surviving helper occurrences preserves all old owner windows; no stronger rehosting or terminal-child allocation is asserted.',
               'limits':['the nine physical families are deleted, so their former0-to-FULL endpoints are no longer requested',
                         'exact native cap identities inherited from separately audited actual111 root projectors',
                         'terminal decoder, new stock recurrence, rounded child errors, source/tape work and joint kappa admission remain open']}
    path = HERE/'BIT-PRUNE-AUDIT.json'
    if args.write:
        path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == json.loads(cap.canonical(receipt)),'complete pruned local receipt differs')
    print(receipt['status'])
    print('helpers429; localmass4989; saving132; exact prefixes',receipts[0]['prefix_row_l1'],receipts[1]['prefix_row_l1'])


if __name__ == '__main__':
    main()
