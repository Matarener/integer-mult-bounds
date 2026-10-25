#!/usr/bin/env python3
"""Source-kernel oracle, pattern geometry and direct E8 cosets; no primary import."""
from collections import Counter,defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from h6_inputs import authenticate,oracles,need,helper_terms_oracle


def canon(rows):
    result=set()
    for row in rows:
        row=tuple(row)
        if next(x for x in row if x)<0:row=tuple(-x for x in row)
        result.add(row)
    return sorted(result)


def pattern_shells():
    roots=[];pure=[]
    for i,j in combinations(range(8),2):
        for a,b in product((-2,2),repeat=2):
            row=[0]*8;row[i]=a;row[j]=b;roots.append(row)
    for signs in product((-1,1),repeat=8):
        if sum(signs)%4==0:roots.append(signs)
    for i in range(8):
        for sign in (-4,4):
            row=[0]*8;row[i]=sign;pure.append(row)
    for indices in combinations(range(8),4):
        for signs in product((-2,2),repeat=4):
            row=[0]*8
            for i,s in zip(indices,signs):row[i]=s
            pure.append(row)
    for i in range(8):
        for signs in product((-1,1),repeat=8):
            row=list(signs);row[i]*=3
            if sum(row)%4==0:pure.append(row)
    return canon(roots),canon(pure)


def coset(v):
    # v-w lies in2*(doubled E8) iff all differences are0 or2 mod4
    # simultaneously and the sum difference is0 mod8.
    r=tuple(x%4 for x in v);other=tuple((x+2)%4 for x in r)
    return min(r,other),sum(v)%8


def pairing(a,b):
    total=sum(map(lambda x:x[0]*x[1],zip(a,b)))
    need(total%4==0,'independent integral pairing');return total//4


def digest(x):
    return sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()


def check(receipt):
    authenticate();C,tariff=oracles();roots,pure=pattern_shells()
    need((len(roots),len(pure))==(120,1080),'independent complete E8 geometry')
    need(digest(roots)==receipt['root_points_sha256'] and digest(pure)==receipt['pure_points_sha256'],
         'recursive and pattern enumerations agree on every point')
    fibers=defaultdict(list)
    for i,v in enumerate(pure):fibers[coset(v)].append(i)
    need(len(fibers)==135 and set(map(len,fibers.values()))=={8},'independent direct-coset pure fibers')
    need(digest(sorted(sorted(g) for g in fibers.values()))==receipt['pure_fiber_partition_sha256'],
         'pairing-signature and direct lattice-coset partitions agree')
    root_keys={coset(v) for v in roots}
    need(len(root_keys|set(fibers)|{coset((0,)*8)})==256,'independent complete mod-two quotient')
    categories=Counter(abs(pairing(u,v)) for u in roots for v in roots)
    need(categories=={0:7560,1:6720,2:120},'independent root association totals')
    reps=[pure[g[0]] for g in fibers.values()]
    columns=[0]*120
    for group in fibers.values():
        row=[pairing(pure[group[0]],r)%2 for r in roots]
        need(sum(row)==64,'independent pure/root degree')
        for i,value in enumerate(row):columns[i]+=value
        for point in group:
            need([pairing(pure[point],r)%2 for r in roots]==row,'whole source coset has the same pairing signature')
    need(set(columns)=={72},'independent transposed root/pure degree')
    need(all(sum(pairing(v,w)%2 for w in reps)==64 for v in reps),'independent pure-label degree')
    ppc=Counter(abs(pairing(v,w)) for v in pure for w in pure)
    need(ppc[1]==1080*448 and ppc[3]==1080*64,'independent complete pure coefficient counts')
    p0,p1,p2=categories[0],categories[1],categories[2]
    rank1_mm=2*p0*p1;rank2_mm=2*p2*p1
    pure_cap_incidence=sum(columns)*120*2  #14400 source pairs each144 pure caps
    removed=rank1_mm+pure_cap_incidence
    D_removed=2*rank1_mm+8*pure_cap_incidence
    old_R=2*(rank1_mm+rank2_mm)+2*pure_cap_incidence+2*1080*(120*64+64)
    old_D=4*(rank1_mm+rank2_mm)+2*16*pure_cap_incidence+2*(ppc[1]+ppc[3])
    D5=2*rank2_mm+2*ppc[3]
    need(old_R==receipt['invoice']['old_helpers'] and old_D==receipt['invoice']['old_scatter_entries'],
         'independent complete baseline invoice')
    need(removed==receipt['invoice']['helpers_removed'] and D_removed==receipt['invoice']['scatter_entries_removed'],
         'independent complete capture/scatter reductions')
    need(D5==receipt['invoice']['abs5_over16_entries_old_and_new'],'independent retained5/16 count')
    for A in (-1,0,1,2):
        for B in (-1,0,1,2):
            matrix=[[C(A+(-1 if i^j else 1)*B,A==B==2 and i==j) for j in range(2)] for i in range(2)]
            ref=next(r for r in receipt['mixed_block_classes'] if r['A']==A and r['B']==B)
            need([[str(v) for v in row] for row in matrix]==ref['C'],'actual frozen kernel matches every factor class')
            determinant=matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0]
            r=0 if not any(any(row) for row in matrix) else 2 if determinant else 1
            need(r==ref['rank'],'independent exact minor ranks')
    fees={q:tariff(q) for q in (F(1),F(-1),F(1,16),F(-1,16),F(5,16),F(-5,16))}
    need(fees[F(1)]==fees[F(-1)]==4 and fees[F(1,16)]==fees[F(-1,16)]==8
         and fees[F(5,16)]==fees[F(-5,16)]==11,'actual frozen Horner tariff')
    old_fee=2*(fees[F(1,16)]*(old_D-D5)+fees[F(5,16)]*D5+fees[F(1)]*old_R)
    new_fee=old_fee-2*fees[F(1,16)]*D_removed
    need(new_fee==receipt['invoice']['new_compensation_component_primitives'],'independent scalar fee with source reads retained')
    helper_terms=helper_terms_oracle()
    for row in receipt['invoice']['conditional_hosted_helper_deltas']:
        terms,q,pad=helper_terms(row['stages'],[1,15,1],removed)
        by_rank=Counter()
        for mass,r in terms:by_rank[r]+=mass
        expected=Counter()
        for mass,r in row['mass_rank_terms_removed']:expected[r]+=F(mass)
        need(by_rank==expected and q==row['replication_q'] and pad==row['pad'],
             'unchanged source full-host stock/padding convention')
    return {'geometry_points':120+1080,'direct_cosets':256,'root_pair_entries':14400,
            'pure_pair_entries':1080**2,'frozen_kernel_classes':16,'source_tariffs':6,
            'helpers_removed':removed,'scatter_entries_removed':D_removed,'native_recipe_lowering':False}


if __name__=='__main__':
    data=check(json.loads((HERE/'CERTIFICATE.json').read_text()))
    print('PASS_INDEPENDENT_H6_PAIR_CAPTURE '+json.dumps(data,sort_keys=True))
