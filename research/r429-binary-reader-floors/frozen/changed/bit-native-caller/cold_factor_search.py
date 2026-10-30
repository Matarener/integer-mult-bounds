#!/usr/bin/env python3
"""A finite constructive ten-term cold-factor probe around the target basis.

This searches an explicit source-extension set; it does not classify all
overcomplete factorizations. Apache-2.0. OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import gcd
from pathlib import Path
import argparse
import json
from cold_cosets import bits,bxor,inverse2,rank2,rankmod,need

HERE=Path(__file__).resolve().parent

def normal(v):
    g=gcd(*v);v=tuple(x//g for x in v)
    return tuple(-x for x in v)if next(x for x in v if x)<0 else v

def qrank(rows):
    B={}
    for row in rows:
        v=list(map(Q,row))
        for j,b in sorted(B.items()):
            f=v[j]
            if f:v=[x-f*y for x,y in zip(v,b)]
        j=next((j for j,x in enumerate(v)if x),None)
        if j is not None:
            f=v[j];B[j]=[x/f for x in v]
    return len(B)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    src=json.loads((HERE/'READOUT-FLOOR.json').read_text())
    cert=json.loads((HERE/'COLD-COSETS.json').read_text())
    nine=json.loads((HERE.parent/'cold-reader/NINE-TERM-FLOOR.json').read_text())
    R,K,roots,full=src['R'],src['K'],src['root_lines'],cert['full_E8_root_lines']
    target=nine['support_strata'][1]['rank7_rows'];masks=[r['mask']for r in target]
    T=[sum((masks[j]>>i&1)<<j for j in range(9))for i in range(9)]
    inv=inverse2(T);C=[bxor(R[j]for j in bits(row))for row in inv]
    B=[sum(((k&mask).bit_count()%2)<<p for p,k in enumerate(K))for mask in masks]
    M=[bxor(R[j]for j in bits(k))for k in K]
    need([bxor(C[j]for j in range(9)if B[j]>>p&1)for p in range(111)]==M,'literal target-special basis')
    proj=[]
    for row in target:
        n=row['normal'];nn=sum(x*x for x in n)
        proj.append([[nn*x-sum(a*b for a,b in zip(n,q))*y for x,y in zip(q,n)]for q in roots])
    need(all(rankmod(c,p,7)==7 for c,p in zip(C,proj)),'base target-special pairing cost63')
    normals={'E7':{normal(q)for q in full},'D7':set(),'E6A1':set()}
    for i,a in enumerate(full):
        for b in full[:i]:
            dot=sum(x*y for x,y in zip(a,b))
            if dot==0:
                for s in(-1,1):normals['D7'].add(normal([x+s*y for x,y in zip(a,b)]))
            elif abs(dot)==2:
                s=1 if dot>0 else -1
                normals['E6A1'].add(normal([2*x-s*y for x,y in zip(a,b)]))
                normals['E6A1'].add(normal([x-2*s*y for x,y in zip(a,b)]))
    need({k:len(v)for k,v in normals.items()}=={'E7':120,'D7':1080,'E6A1':3360},'three complete hyperplane families')
    candidates={1<<p for p in range(111)};stats={};flat_records=[]
    for name,vecs in normals.items():
        hist=Counter();tests=0
        for v in sorted(vecs):
            S=sum((not sum(a*b for a,b in zip(v,q)))<<p for p,q in enumerate(roots))
            need(rankmod(S,roots)<=7,'retained hyperplane has its explicit orthogonal normal')
            for i,(c,t)in enumerate(zip(C,target)):
                if sum(a*b for a,b in zip(v,t['normal'])):continue
                z=c&~S;dz=rankmod(z,roots)
                hist[dz]+=1;tests+=1
                if z and dz<=6:
                    candidates.add(z);flat_records.append([name,list(v),i,z,dz])
        stats[name]={'hyperplanes':len(vecs),'cold_source_tests':tests,'outside_rank_histogram':dict(sorted(hist.items()))}
    best=100;witnesses=[];bills=Counter();checked=0
    for z in sorted(candidates):
        dz=rankmod(z,roots);costs=[rankmod(c^z,p,7)for c,p in zip(C,proj)]
        chosen=[i for i,v in enumerate(costs)if v<7]
        # A nontrivial tenth target must differ from all nine basis columns.
        # At least two selected independent columns suffice and are necessary.
        for i in sorted((i for i in range(9)if i not in chosen),key=lambda i:costs[i]):
            if len(chosen)>=2:break
            chosen.append(i)
        lam=sum(1<<i for i in chosen)
        bill=dz+sum(costs[i]if lam>>i&1 else 7 for i in range(9))
        bills[bill]+=1;checked+=1
        if bill<best:best=bill;witnesses=[]
        if bill==best:
            b0=bxor(B[i]for i in bits(lam))
            cc=[c^(z if lam>>i&1 else 0)for i,c in enumerate(C)]+[z]
            bb=B+[b0]
            need([bxor(cc[j]for j in range(10)if bb[j]>>p&1)for p in range(111)]==M,'exact ten-factor correction identity')
            actual=qrank(roots[p]for p in bits(z))+sum(qrank(proj[i][p]for p in bits(cc[i]))for i in range(9))
            need(actual==bill,'exact rational candidate tariff')
            witnesses.append({'z':z,'z_geometric_rank':dz,'selected_source_updates_mask':lam,
                              'target_columns':bb,'source_rows':cc,'pairing_ranks':[v if lam>>i&1 else 7 for i,v in enumerate(costs)]+[dz],
                              'zero_or_duplicated_last_target':b0==0 or b0 in B})
    out={'status':'PASS_FINITE_TARGET_SPECIAL_COLD_EXTENSION_SEARCH','no_new_kappa':True,
         'scientific_pin':src['scientific_pin'],'sources':{str(HERE/f):sha256((HERE/f).read_bytes()).hexdigest()for f in('READOUT-FLOOR.json','COLD-COSETS.json')},
         'target_special_basis':B,'source_dual_basis':C,'hyperplane_families':stats,
         'candidate_rule':'All111 unit readouts and every nonzero outside piece C_i restricted to the complement of a cold E7,D7,E6A1 hyperplane, provided its source geometric rank<=6.',
         'candidate_count':checked,'canonical_candidates_sha256':sha256(json.dumps(sorted(candidates),separators=(',',':')).encode()).hexdigest(),
         'candidate_pairing_bill_histogram':dict(sorted(bills.items())),'best_pairing_tariff':best,'best_witnesses':witnesses,
         'source_extension_rule':'For fixed z select at least two updates C_i->C_i+z; add the tenth term (sum selected B_i) z^T. This is an exact binary identity. The search minimizes the nine updated pairing tariffs subject to at least two updates, then adds the source rank of z. The last target is distinct from the nine special basis directions and spans8, so this is its exact pairing rank.',
         'scope':['Only this explicit target-special basis and finite source-extension set. No exhaustive all-factor or all-z statement.',
                  'Native gathering, immutable COPY/ERASE, cold target cuts and dirt restoration are unconstructed.',
                  'The ten-factor necessary floor55 is a separate broader screen; this search claims only its saved finite result.']}
    out=json.loads(json.dumps(out));path=HERE/'COLD-FACTOR-SEARCH.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'saved finite cold-factor search differs')
    print(out['status']);print('candidates',checked,'best optimistic source-update tariff',best)

if __name__=='__main__':main()
