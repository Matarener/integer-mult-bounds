#!/usr/bin/env python3
"""Exact primal/cut certificates for fixed-E helper exposure unions.

Objective r*nullity(D_S)-lambda*|exposure(S)| is auxiliary rank mass,
not a complete native deficit or rate. All semantic/native limits are saved.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import deque
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from selective_boost_screen import dirty_cols,propagation
from old_kernel_boost import old_word,dirty_factor
from global_kernel_boost import RAW,basis,eye
from physical_code import bits,rank2
from cold_cosets import need

HERE=Path(__file__).resolve().parent
FULL=Path('/Users/ross/git/math/integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz')

def span_table(nodes,cols,n):
    B={}
    for node in sorted(nodes):
        z=cols[node%n];a=1<<node
        while z:
            j=z.bit_length()-1
            if j not in B:B[j]=(z,a);break
            v,c=B[j];z^=v;a^=c
        need(z!=0,'D partition color remains independent')
    return B

def reduce_col(col,B):
    z=col;a=0
    while z:
        j=z.bit_length()-1
        if j not in B:return z,a
        v,c=B[j];z^=v;a^=c
    return z,a

def solve(cols,masks,r,cap):
    n=len(cols);nodes=n*r;components=[set()for _ in range(r+120)];owner=[-1]*nodes
    def validate():
        seen=set()
        for comp,S in enumerate(components):
            need(not seen&S,'partition owners disjoint');seen|=S
            if comp<r:
                need(all(x//n==comp for x in S),'D color binding')
                span_table(S,cols,n)
            else:
                t=comp-r;need(len(S)<=cap and all((masks[x%n]>>t)&1 for x in S),'native resource incidence/capacity')
            need(all(owner[x]==comp for x in S),'owner array matches partition')
        need(seen=={x for x,a in enumerate(owner)if a>=0},'all assigned nodes covered')
    def search(starts):
        Bs=[span_table(components[c],cols,n)for c in range(r)]
        prev={x:None for x in starts};q=deque(starts)
        while q:
            x=q.popleft();color=x//n;z,circuit=reduce_col(cols[x%n],Bs[color])
            if z:return (x,color),prev
            for y in bits(circuit):
                if y not in prev:prev[y]=(x,color);q.append(y)
            for t in bits(masks[x%n]):
                comp=r+t;S=components[comp]
                if len(S)<cap:return (x,comp),prev
                for y in sorted(S):
                    if y not in prev:prev[y]=(x,comp);q.append(y)
        return None,prev
    for root in range(nodes):
        if owner[root]>=0:continue
        sink,prev=search([root])
        if sink is None:continue
        x,comp=sink
        while True:
            old=owner[x]
            if old>=0:components[old].remove(x)
            components[comp].add(x);owner[x]=comp
            if prev[x]is None:break
            x,comp=prev[x]
        validate()
    unassigned=[x for x,a in enumerate(owner)if a<0]
    sink,reachable=search(unassigned)
    need(sink is None,'maximum partition has no residual augmenting path')
    selected=sorted({x%n for x in reachable});mask=0
    for h in selected:mask|=masks[h]
    rank=rank2([cols[h]for h in selected]);nullity=len(selected)-rank
    profit=r*nullity-cap*mask.bit_count();gap=len(unassigned)
    # The partition is an all-subset upper bound profit<=gap. This actual
    # full-helper cut attains gap, independently certifying exact optimality.
    need(profit==gap,'actual full-helper cut attains partition upper bound')
    validate()
    return {'entrance_rank':r,'resource_weight':cap,'optimum_auxiliary_profit':profit,
            'selected_helper_indices':selected,'selected_helper_count':len(selected),'D_rank':rank,'kernel_dimension':nullity,
            'exposure_mask':str(mask),'target_exposure':(mask&((1<<111)-1)).bit_count(),'COPY_exposure':(mask>>111).bit_count(),
            'ground_color_copies':nodes,'assigned_color_copies':nodes-gap,'unassigned_color_copies':unassigned,
            'partition_D_colors':[sorted(S)for S in components[:r]],
            'partition_resource_slots':{str(i):sorted(S)for i,S in enumerate(components[r:])if S},
            'dual_reachable_color_copies':sorted(reachable)}

def receipt(plane,weights,write=False):
    raw=json.loads(gzip.decompress(RAW.read_bytes()));base=old_word(raw);dirty_factor(base,raw)
    Bs=[basis(raw['lines'][p]for p in f)for f in raw['frames']]
    if plane.startswith('root'):
        full=json.loads(gzip.decompress(FULL.read_bytes()));E=basis([full['lines'][int(plane[4:])]])
    elif plane.startswith('frame'):E=Bs[int(plane[5:])]
    elif plane.startswith('coordinate'):E=[eye(8)[i]for i in range(int(plane[10:]))]
    else:raise ValueError('unknown plane')
    r=len(E);labels,upper=propagation(base,raw,E,Bs);hs=list(range(222,660));D=dirty_cols(base)
    cols=[D[h]for h in hs];masks=[labels[h]for h in hs]
    runs=[solve(cols,masks,r,w)for w in weights]
    for z in runs:z['selected_physical_helpers']=[hs[i]for i in z['selected_helper_indices']]
    out={'status':'PASS_EXACT_FIXED_EXPOSURE_UNION_PRIMAL_CUT_CERTIFICATES','no_new_kappa':True,
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','plane':plane,'E_basis':[[str(v)for v in row]for row in E],
         'source':{str(p):sha256(p.read_bytes()).hexdigest()for p in(RAW,FULL,HERE/'selective_boost_screen.py')},
         'helper_order':hs,'dirty_columns':cols,'exposure_masks':[str(x)for x in masks],'runs':runs,
         'objective':'r*(|S|-rank_F2(D_S))-lambda*popcount(OR_(h in S) exposure[h])',
         'exactness':'A partition of colored helpers into r independent D sets and resource slots of capacity lambda proves profit(S)<=unassigned for every S. The emitted full-helper cut attains equality. Every independence, capacity, incidence, ownership and equality predicate is checked explicitly.',
         'physical_model':'Original semantic D, fixed causal common-E promotion, copied private fields keptZERO. Target caps and copied-total sources not containingE each expose one native rank; helper kernel entrances have rankr. Every selected helper, including pivots, is promoted toE for the basis change. Native literal word and full histogram are not inferred.',
         'limits':['This auxiliary rank-mass objective is not net coverage deficit: narrower helper stock loses the same rank credit.','A kappa screen needs an independently proved full moment/owner benefit bound per changed helper and complete source/target/COPY bill.','No cold-target quotient compensation is included; full semantic D_S is used.','No claim against reordered words, other E planes, ADDRESS-dependent kernels or changed private cuts.'],
         'attribution':'Pinned R438 word and fixed-exposure causal propagation are prior lane work; primal/cut partition implementation is new. Parent supplied the matroid-union strategy and all-subset partition proof.'}
    out=json.loads(json.dumps(out));p=HERE/f'SELECTIVE-UNION-{plane}.json'
    if write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved union partition differs')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plane',default='root77');ap.add_argument('--weights',default='1,2,4,5,6,7,8,16,32');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    o=receipt(a.plane,[int(w)for w in a.weights.split(',')],a.write)
    print(o['status'],a.plane)
    for z in o['runs']:print('lambda',z['resource_weight'],'profit',z['optimum_auxiliary_profit'],'kernel',z['kernel_dimension'],'exposure',z['target_exposure'],z['COPY_exposure'],'helpers',z['selected_helper_count'])
