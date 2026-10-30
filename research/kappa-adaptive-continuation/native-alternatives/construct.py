#!/usr/bin/env python3
"""Literal width-preserving receiver sharing on PR3734's helper544 releases.

The discovery is the transpose of the exact dirty-source covector rewrite
credited to Nick Petalas (rank7-shared-restore-fanin), applied to dataisfire's
staged544 producer-return word and its cited construction lineage.
The assignment search uses the rank7-joint-frame-optimum graph method.
Substantial OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations
import argparse,gzip,json
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from fanout_search import read,expand,trace,derive_cleanup

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
DEFAULT=REPO/'research/kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/words'
OLD=[['add',672,544,1,2,[414,51]],['add',676,544,-1,2,[414,51]]]
NEW=[['add',672,676,1,1,[51]],OLD[1],['add',672,676,-1,1,[413,72,48,3]]]
DELTA={1:-1,2:-1,3:1}
PROFILE={1:2439,2:724,3:225,4:102,5:20,8:8}
WIDTHS={4:26,5:2,6:18,7:53,8:96,9:213}

def scalar_matrix(events):
    roles=(544,672,676);rows={r:{r:Fraction(1)} for r in roles}
    for e in events:
        assert e[0]=='add' and e[1] in roles and e[2] in roles
        for r,c in tuple(rows[e[2]].items()):
            q=rows[e[1]].get(r,0)+Fraction(e[3],e[4])*c
            if q:rows[e[1]][r]=q
            else:rows[e[1]].pop(r,None)
    return [[str(rows[r].get(c,0)) for c in roles] for r in roles]

def construct(w):
    assert w['B'][692:694]==OLD,'exact original event preimages'
    assert {int(r):n for r,n in w['report']['width_inventory'].items()}==WIDTHS
    assert {int(r):n for r,n in w['report']['local_profile'].items()}=={1:2440,2:725,3:224,4:102,5:20,8:8}
    assert scalar_matrix(OLD)==scalar_matrix(NEW)
    out=deepcopy(w);out['B'][692:694]=deepcopy(NEW)
    for warp in out['warps']:
        if warp[0]>=694:warp[0]+=1
    derive_cleanup(out)
    out['report']['local_profile']={str(r):n for r,n in PROFILE.items()}
    sb,fb,cb,_,_,pb=trace(w,expand(w));sn,fn,cn,_,_,pn=trace(out,expand(out))
    assert sb==sn and fb==fn
    deltas={}
    for r in pb:
        d=pn[r].copy();d.subtract(pb[r]);d={k:n for k,n in d.items() if n}
        if d:deltas[r]=d
    assert deltas=={672:DELTA},deltas
    unchanged=[k for k in w if k not in ('B','warps','cleanup','report')]
    assert all(w[k]==out[k] for k in unchanged)
    assert sum(r*n for r,n in PROFILE.items())==5134
    return out,dict(original_B_slice=[692,694],original_events=OLD,new_events=NEW,
        warp_position_rule='B_pos >= 694 increases by 1; warp operators, lenders and frames are identical',
        per_register_native_delta=deltas,local_profile=PROFILE,width_inventory=WIDTHS,
        helpers=408,private_buffers=91,independent_inputs=632,
        old_672_frames=[list(x[2]) for x in cb[672] if x[1]=='frame'],
        new_672_frames=[list(x[2]) for x in cn[672] if x[1]=='frame'],
        exact_three_register_matrix=scalar_matrix(NEW),
        unchanged_fields=unchanged,
        status='PASS_LITERAL_CONSTRUCTION_AND_EXACT_DIRTY_THREE_REGISTER_IDENTITY')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-dir',type=Path,default=DEFAULT);ap.add_argument('--out',type=Path,default=HERE/'candidate')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);providers={};words=[]
    for tag in ('base','extra'):
        source=a.source_dir/f'BORROW-WORD-43{tag}.json.gz';old=read(source);word,rec=construct(old)
        payload=json.dumps(word,sort_keys=True,separators=(',',':')).encode();path=a.out/f'BORROW-WORD-43{tag}.json.gz';path.write_bytes(gzip.compress(payload,mtime=0))
        rec.update(source_file=source.name,source_sha256=sha256(source.read_bytes()).hexdigest(),source_payload_sha256=sha256(json.dumps(old,sort_keys=True,separators=(',',':')).encode()).hexdigest(),word=path.name,word_sha256=sha256(path.read_bytes()).hexdigest(),word_payload_sha256=sha256(payload).hexdigest())
        providers[tag]=rec;words.append(word)
    assert words[0]['report']['local_profile']==words[1]['report']['local_profile']
    assert words[0]['report']['width_inventory']==words[1]['report']['width_inventory']
    result=dict(status='PASS_BOTH_PROVIDER_LITERAL_RECEIVER_SHARING',providers=providers,
        constructor_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        obligations='Run independent all-column/native replay on both emitted words, then bind the complete invoice and original owner allocation.')
    (a.out/'CONSTRUCTION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(result['status'],PROFILE,WIDTHS)

if __name__=='__main__':main()
