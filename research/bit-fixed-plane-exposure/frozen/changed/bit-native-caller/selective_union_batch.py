#!/usr/bin/env python3
"""Complete fixed-exposure union certificates across a pinned finite E list.

This is the auxiliary rank-mass objective, not an owner/moment theorem.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from selective_union_partition import HERE,RAW,FULL,old_word,dirty_factor,basis,dirty_cols,propagation,solve,need

def receipt(mode='roots',cap=8,write=False):
    raw=json.loads(gzip.decompress(RAW.read_bytes()));base=old_word(raw);dirty_factor(base,raw)
    Bs=[basis(raw['lines'][p]for p in f)for f in raw['frames']]
    full=json.loads(gzip.decompress(FULL.read_bytes()));hs=list(range(222,660));D=dirty_cols(base);cols=[D[h]for h in hs]
    if mode=='roots':todo=[('root'+str(i),basis([q]))for i,q in enumerate(full['lines'])]
    else:todo=[('frame'+str(i),B)for i,B in enumerate(Bs)if len(B)==2]
    need(len(todo)==(120 if mode=='roots' else 153),'complete fixed native plane census')
    runs=[]
    for i,(label,E)in enumerate(todo):
        labels,_=propagation(base,raw,E,Bs);masks=[labels[h]for h in hs]
        z=solve(cols,masks,len(E),cap)
        z.update({'plane':label,'E_basis':[[str(x)for x in row]for row in E],
                  'exposure_masks':[str(x)for x in masks],
                  'selected_physical_helpers':[hs[j]for j in z['selected_helper_indices']]})
        runs.append(z)
        if(i+1)%10==0 or i+1==len(todo):print(mode,'completed',i+1,'/',len(todo),'nonzero cuts',sum(v['optimum_auxiliary_profit']>0 for v in runs),flush=True)
    out={'status':'PASS_FINITE_NATIVE_PLANES_ALL_UNION_PARTITION_CERTIFICATES','no_new_kappa':True,
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','mode':mode,'resource_weight':cap,
         'source':{str(p):sha256(p.read_bytes()).hexdigest()for p in(RAW,FULL,HERE/'selective_boost_screen.py',HERE/'selective_union_partition.py')},
         'helper_order':hs,'semantic_dirty_columns':cols,'planes_tested':len(runs),'positive_cut_planes':[z['plane']for z in runs if z['optimum_auxiliary_profit']>0],
         'runs':runs,
         'exact_scope':'Each listed E is fixed. For every helper union S, the verified colored-D/resource partition bounds r*nullity(D_S)-lambda*exposure(S) by its unassigned count. A matching actual full-helper cut attains equality. This is all-subset, not all-E: exactly the listed120 rootlines or153 rank2 frames are covered.',
         'physical_scope':'Full semantic D kernel, fixed causal E-promotion, target/COPY rank1 exposure, PRIVATEZERO, unchanged A/B chronology. No quotient through cold targets is included.',
         'limits':['Auxiliary rank mass is not net deficit: helper stock width credit also decreases.','A kappa consequence requires an independent complete moment/owner benefit upper bound tied to lambda.','No literal joined-frame supplier, cold-target quotient repair, other E plane or changed chronology is certified here.'],
         'attribution':'Parent supplied matroid-union strategy and partition bound. Lane supplies semantic binding, exact independent/resource partitions and matching cuts.'}
    out=json.loads(json.dumps(out));p=HERE/f'SELECTIVE-UNION-{mode.upper()}-L{cap}.json'
    if write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved finite-plane union certificate differs')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--mode',choices=['roots','frames'],default='roots');ap.add_argument('--capacity',type=int,default=8);ap.add_argument('--write',action='store_true');a=ap.parse_args();o=receipt(a.mode,a.capacity,a.write)
    print(o['status'],'positive planes',o['positive_cut_planes'])
