#!/usr/bin/env python3
"""Search coordinated six-axis placements with an exact integer operator.

This broadens isolated transfers to every six-of-twenty placement for one
standard coordinate axis in each of the eight later coordinate blocks.
Discovery permits a final per-stream translation (a sign at that mode).
Every candidate needs a complete character/native/hosting proof and invoice.
NumPy int64 is used only with an explicit 2^27 absolute-entry bound.
Operator semantics: Nick Petalas / PR3187, Matarener / PR3296. New bounded
coordinated search with OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
AUDIT=HERE.parent/'operator-audit/checkout/research'
sys.path.insert(0,str(AUDIT/'rank7-idle-star-stream-obstruction'))
import source as S
import algebra as A


def rotate(rows,exponent):
    e=exponent%4
    if e==0:return
    if e==2:rows*=-1;return
    a=rows[...,0].copy();b=rows[...,1].copy()
    rows[...,0]=-b if e==1 else b
    rows[...,1]=a if e==1 else -a


def run(template,recipe,patterns,selected_bit,character):
    n=len(patterns);out=np.zeros((n,8,8,2),dtype=np.int64)
    for i in range(8):out[:,i,i,0]=1
    local={e['stage']:e for e in template['recipe'] if e['kind']=='local'}
    axis=1<<selected_bit;qbit=A.dot(character,recipe['q'])
    events=[e for e in template['execution_schedule'] if e['kind'] not in ('bank_padding_cover_sweep','translate_every_live_family')]
    bound=1
    def phase(s,e):rotate(out[:,s],e)
    def shear(d,s,c):
        nonlocal bound
        out[:,d]+=c*out[:,s];bound*=2
        assert bound<=1<<27
    for event in events:
        kind=event['kind']
        if kind=='local_cover_sweep':
            stage=event['stage'];l=local[stage];x,y=2*l['pair'],2*l['pair']+1
            for side,stream in enumerate((x,y)):
                before=(1-side)*qbit if stage==0 else (character&((1<<(9+8*(stage-1)))-1)).bit_count()-side*qbit
                phase(stream,-before)
            if l['reverse']:shear(x,y,-1)
            else:shear(y,x,1)
            for side,stream in enumerate((x,y)):
                after=(character&((1<<(9+8*stage))-1)).bit_count()-side*qbit
                phase(stream,after)
        elif kind=='idle_cover_sweep':
            for side,child in enumerate(event['child_indices']):
                entry=recipe['idle_children'][child];stream=2*event['pair']+side
                ex=sum(A.dot(character,int(v)) for v in entry['orthogonal_axes'] if int(v)!=axis)
                ex+=2*A.dot(character,int(entry['translation_after']))
                phase(stream,ex)
                if A.dot(character,axis):
                    selected=patterns[:,child]
                    rows=out[selected,stream].copy();rotate(rows,1);out[selected,stream]=rows
        elif kind=='bridge':
            d,s,c=event['dst'],event['src'],event['coefficient']
            shear(2*d,2*s,c);shear(2*s+1,2*d+1,-c)
        elif kind=='terminal_Y_translations':
            for p in event['pairs']:phase(2*p+1,2*qbit)
        elif kind=='terminal':
            for p in range(event['pairs']):
                x=out[:,2*p].copy();out[:,2*p]=out[:,2*p+1];out[:,2*p+1]=-x
        else:raise AssertionError(kind)
    assert int(np.abs(out).max())<=bound
    rotate(out,-character.bit_count())
    diagonal=out[:,np.arange(8),np.arange(8)].copy()
    for i in range(8):out[:,i,i]=0
    match=(out==0).all(axis=(1,2,3))&(diagonal[:,:,1]==0).all(axis=1)&(np.abs(diagonal[:,:,0])==1).all(axis=1)
    return match,diagonal[:,:,0],bound


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=HERE/'PHASE-PATTERNS.json')
    args=ap.parse_args()
    ctx=S.load_context();template=ctx['template'];recipe=ctx['recipe']
    placements=list(itertools.combinations(range(20),6))
    patterns=np.zeros((len(placements),20),dtype=bool)
    for i,p in enumerate(placements):patterns[i,list(p)]=True
    cases=[]
    for bit in (9,17,25,33,41,49,57,65):
        baseline=tuple(c for c,e in enumerate(recipe['idle_children']) if (1<<bit) in map(int,e['orthogonal_axes']))
        assert len(baseline)==6
        match,signs,bound=run(template,recipe,patterns,bit,1<<bit)
        ids=np.flatnonzero(match);first_count=len(ids)
        if len(ids):
            keep,other_signs,_=run(template,recipe,patterns[ids],bit,(1<<bit)|1)
            # A correction using only the selected coordinate must agree in
            # the second tested mode, whose q parity is one.
            keep &= (other_signs==signs[ids]).all(axis=1)
            ids=ids[keep]
        kept=[{'placement':list(placements[i]),'final_translation_signs':list(map(int,signs[i]))} for i in ids]
        assert any(tuple(x['placement'])==baseline for x in kept)
        rec={'axis_bit':bit,'baseline_placement':list(baseline),'placements_enumerated':len(placements),
            'pass_selected_mode_up_to_translation':first_count,'pass_both_q_modes_with_same_translation':len(kept),
            'candidates':kept,'integer_absolute_entry_bound':bound}
        cases.append(rec)
        print('COORDINATED_AXIS',bit,'patterns',len(placements),'q0_pass',first_count,'both_q_pass',len(kept),flush=True)
    paths=[Path(__file__),Path(S.__file__),Path(A.__file__),S.ROOT/(S.MAIN+'vendor/TEMPLATE.json.gz'),S.ROOT/S.PHASES]
    result={'status':'EXACT_BOUNDED_COORDINATED_AXIS_DISCOVERY_NOT_NATIVE_ADMISSION',
        'changed_premise':'Every six-of-twenty placement, including slots where the original axis was absent and final per-stream translations, instead of the PR3190 donor/receiver rule.',
        'scope':'One standard-coordinate axis at a time, unchanged total axis multiplicity six and original data-event chronology. Selected character and selected-character plus bit0 tested exactly; no claim of exhaustive multi-axis or changed-controller coverage.',
        'axis_patterns_enumerated':sum(x['placements_enumerated'] for x in cases),
        'cases':cases,'new_kappa':False,
        'source_pins':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':main()
