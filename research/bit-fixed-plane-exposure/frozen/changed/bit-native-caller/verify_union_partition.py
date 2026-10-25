#!/usr/bin/env python3
"""Independent primal/cut checker: no augmenting-path code is imported.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from selective_boost_screen import propagation,dirty_cols
from old_kernel_boost import old_word,dirty_factor
from global_kernel_boost import RAW,basis

HERE=Path(__file__).resolve().parent
FULL=Path('/Users/ross/git/math/integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz')

def check(p,m):
    if not p:raise RuntimeError(m)

def rank(values):
    piv={}
    for value in values:
        z=value
        while z:
            p=z.bit_length()-1
            if p in piv:z^=piv[p]
            else:piv[p]=z;break
    return len(piv)

def primal(run,D,masks):
    n=len(D);r=run['entrance_rank'];w=run['resource_weight'];seen=set()
    check(run['ground_color_copies']==r*n,'groundset size')
    for color,nodes in enumerate(run['partition_D_colors']):
        S=set(nodes);check(len(S)==len(nodes)and not seen&S,'D partition repeated node')
        check(all(0<=x<r*n and x//n==color for x in S),'D color/ground binding')
        check(rank([D[x%n]for x in nodes])==len(nodes),'independent D color')
        seen|=S
    check(len(run['partition_D_colors'])==r,'all D colors present')
    for resource,nodes in run['partition_resource_slots'].items():
        t=int(resource);S=set(nodes)
        check(0<=t<120 and len(S)==len(nodes)and not seen&S,'resource partition repeated node')
        check(len(nodes)<=w and all(0<=x<r*n and(masks[x%n]>>t)&1 for x in nodes),'resource incidence/capacity')
        seen|=S
    U=set(range(r*n))-seen
    check(sorted(U)==run['unassigned_color_copies']and len(seen)==run['assigned_color_copies'],'unassigned complement')
    S=run['selected_helper_indices'];check(len(S)==len(set(S))and all(0<=x<n for x in S),'actual full-helper cut')
    cost=0
    for h in S:cost|=masks[h]
    k=len(S)-rank([D[h]for h in S]);profit=r*k-w*cost.bit_count()
    check(str(cost)==run['exposure_mask']and k==run['kernel_dimension'],'actual cut kernel/exposure')
    check(profit==len(U)==run['optimum_auxiliary_profit'],'matching primal/cut bound')
    return len(U)

def verify(path):
    data=json.loads(path.read_bytes())
    for p,h in data['source'].items():check(sha256(Path(p).read_bytes()).hexdigest()==h,'source hash '+p)
    check(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','R438 scientific input pin')
    raw=json.loads(gzip.decompress(RAW.read_bytes()));full=json.loads(gzip.decompress(FULL.read_bytes()))
    base=old_word(raw);dirty_factor(base,raw);Bs=[basis(raw['lines'][p]for p in f)for f in raw['frames']]
    hs=data['helper_order'];check(hs==list(range(222,660)),'all438 physical helper roles')
    dc=dirty_cols(base);D=[dc[h]for h in hs]
    check(D==data['semantic_dirty_columns'],'semantic dirty column binding')
    seenplanes=set()
    for run in data['runs']:
        name=run['plane'];check(name not in seenplanes,'plane repeated');seenplanes.add(name)
        if name.startswith('root'):E=basis([full['lines'][int(name[4:])]])
        else:E=Bs[int(name[5:])]
        check([[str(x)for x in row]for row in E]==run['E_basis'],'actual E basis')
        check(run['entrance_rank']==len(E)and run['resource_weight']==data['resource_weight'],'physical E rank and common resource weight')
        labels,_=propagation(base,raw,E,Bs);masks=[labels[h]for h in hs]
        check([str(x)for x in masks]==run['exposure_masks'],'actual causal exposure binding')
        check(primal(run,D,masks)==0,'zero-optimum all-union certificate')
    expected={f'root{i}'for i in range(120)}if data['mode']=='roots'else{f'frame{i}'for i,B in enumerate(Bs)if len(B)==2}
    check(seenplanes==expected and len(seenplanes)==data['planes_tested'],'complete finite plane census')
    # A duplicated owner must be rejected even if all claimed counts remain.
    bad=deepcopy(data['runs'][0]);color=next(i for i,S in enumerate(bad['partition_D_colors'])if S)
    bad['partition_D_colors'][color].append(bad['partition_D_colors'][color][0])
    masks=[int(x)for x in bad['exposure_masks']]
    rejected=False
    try:primal(bad,D,masks)
    except RuntimeError:rejected=True
    check(rejected,'destructive duplicate-owner control')
    return data['planes_tested']

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('receipt',nargs='?',default='SELECTIVE-UNION-ROOTS-L8.json');a=ap.parse_args()
    count=verify(HERE/a.receipt);print('PASS_INDEPENDENT_ALL_UNION_PRIMAL_CUT_CHECK',count,'planes; duplicate-owner control rejected')
