#!/usr/bin/env python3
"""Summarize bounded discovery and prevent double-counting overlapping variants.

This file binds search nominations and their scope, not the native proof of
the selected construction. Apache-2.0.
"""
import json,gzip
from pathlib import Path
from hashlib import sha256

HERE=Path(__file__).resolve().parent
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def main():
    result=read(HERE/'joint-transpose-B/RESULT.json');variants=result['candidates']
    assert len(variants)==4 and [r['index'] for r in variants]==[172,174,175,179]
    source=HERE.parents[2]/'research/kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43base.json.gz'
    word=read(source);by={}
    for pos,*_ in word['warps']:by[pos]=by.get(pos,0)+1
    position_map={};expanded=0
    for p in range(len(word['B'])+1):
        expanded+=by.get(p,0)
        if p<len(word['B']):position_map[expanded]=p;expanded+=1
    sets=[];details=[]
    for row in variants:
        raw={p[k] for p in row['chosen'] for k in ('keep','drop')}
        original={position_map[expanded-1-i] for i in raw}
        sets.append(original)
        assert row['optimization']['delta']=={'1':-1,'2':-1,'3':1}
        candidate=HERE/'joint-transpose-B'/row['word'];actual=read(candidate)
        assert actual['report']['local_profile']=={'1':2439,'2':724,'3':225,'4':102,'5':20,'8':8}
        details.append(dict(index=row['index'],original_B_preimages=sorted(original),
            delta={'1':-1,'2':-1,'3':1},B_scalar_delta=len(actual['B'])-len(word['B']),
            word=candidate.relative_to(HERE).as_posix(),word_sha256=sha256(candidate.read_bytes()).hexdigest()))
    shared=set.intersection(*sets);assert shared=={692,693}
    nominated=next(r for r in variants if r['index']==175)
    selected=read(HERE/'candidate/BORROW-WORD-43base.json.gz')
    assert selected==read(HERE/'joint-transpose-B'/nominated['word'])
    receipt=dict(status='PASS_BOUNDED_DISCOVERY_SCOPE_AND_OVERLAPPING_VARIANT_CHECK',
        selected_variant=175,shared_original_B_preimages=sorted(shared),variants=details,
        additive_claim_rejected='All four alternatives replace the same receiver pair and remove the same single rank-2 stop on one receiver. Their individual deltas cannot be counted as four disjoint savings.',
        completed_searches={name:read(HERE/name/'RESULT.json') for name in ('fanout-base','permanent-base','joint-B','joint-restore','joint-permanent-A','joint-transpose-B','joint-transpose-restore')},
        interrupted_A_search=dict(status='PARTIAL_INTERRUPTED_AFTER_SUCCESSFUL_PRODUCTION_CANDIDATE_SELECTED',
            last_reported_attempted=1850,last_reported_feasible=1848,last_reported_infeasible=2,
            emitted_candidates=0,observed_prefix_indices=[0,1849],
            replay_prefix_command='python3 -B research/kappa-adaptive-continuation/native-alternatives/joint_fanout_search.py --word SOURCE_WORD --section A --out FRESH_OUTPUT --limit 1850',
            scope='The ongoing discovery process was interrupted after the complete native candidate passed. Its last reported counters are preserved; later unreported work is excluded. This is not an exhaustive A search.'),
        positive_control=dict(receipt='positive-control/LOCAL-AUDIT.json',
            status=read(HERE/'positive-control/LOCAL-AUDIT.json')['status'],
            exact_inputs=632,providers_tested=1,mechanism='Known PR2979 receiver consumers of the shared covector X40-2X54'))
    (HERE/'DISCOVERY.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(receipt['status'],'selected=175 shared_B=692,693')

if __name__=='__main__':main()
