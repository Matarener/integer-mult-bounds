#!/usr/bin/env python3
"""Source-bound nine-term cold-target pairing-rank floor.

The tariff is optimistic and does not certify reader construction.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'bit-native-caller/READOUT-FLOOR.json'

def need(v,m):
    if not v:raise ValueError(m)

def rank_mod(rows,p=3):
    basis={}
    for row in rows:
        a=[x%p for x in row]
        for j,b in sorted(basis.items()):
            c=a[j];a=[(x-c*y)%p for x,y in zip(a,b)]
        j=next((j for j,x in enumerate(a)if x),None)
        if j is not None:
            c=pow(a[j],-1,p);basis[j]=[(x*c)%p for x in a]
            if len(basis)==8:return 8
    return len(basis)

def null_line(rows):
    a=[list(map(Q,r))for r in rows];pivot=[];j=0
    for c in range(8):
        at=next((i for i in range(j,len(a))if a[i][c]),None)
        if at is None:continue
        a[at],a[j]=a[j],a[at];z=a[j][c];a[j]=[v/z for v in a[j]]
        for i in range(len(a)):
            if i!=j:
                z=a[i][c];a[i]=[v-z*w for v,w in zip(a[i],a[j])]
        pivot.append(c);j+=1
    need(len(pivot)==7,'exact rank7 null line')
    f=next(c for c in range(8)if c not in pivot)
    v=[Q(int(c==f))for c in range(8)]
    for i,c in enumerate(pivot):v[c]=-a[i][f]
    den=math.lcm(*(x.denominator for x in v));v=[int(x*den)for x in v]
    g=math.gcd(*v);v=[x//g for x in v]
    if next(x for x in v if x)<0:v=[-x for x in v]
    need(all(sum(x*y for x,y in zip(r,v))==0 for r in rows),'exact orthogonality certificate')
    return v

def span(rows):
    result=[0]
    for r in rows:result += [x^r for x in result]
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    src=json.loads(SOURCE.read_text());R,K,roots=src['R'],src['K'],src['root_lines']
    need(len(R)==9 and len(K)==len(roots)==111,'source dimensions')
    rcode=span(R);kcode=[sum(((k&mask).bit_count()%2)<<j for j,k in enumerate(K))for mask in range(512)]
    need(len(set(rcode))==len(set(kcode))==512,'both exact code spaces rank9')
    records=[];special=[]
    for name,code in(('source',rcode),('target',kcode)):
        census=Counter();rows=[]
        for mask,word in enumerate(code[1:],1):
            support=[roots[j]for j in range(111)if word>>j&1]
            r=rank_mod(support);need(r in(7,8),'modular support rank')
            census[r]+=1
            if r==7:rows.append({'mask':mask,'normal':null_line(support)})
        need(census==Counter({7:9,8:502}),'complete two-sided support stratification')
        special.append(rows);records.append({'side':name,'rank_histogram':dict(census),'rank7_rows':rows})
    need([r['mask']for r in special[0]]==[1<<j for j in range(9)],'source special labels are original readers')
    source_normals=[r['normal']for r in special[0]]
    match=[source_normals.index(row['normal'])for row in special[1]]
    need(sorted(match)==list(range(9)),'same nine normal labels on both sides')
    pairs=[]
    for i,a in enumerate(special[0]):
        for j,b in enumerate(special[1]):
            pairing=(b['mask']>>i)&1
            dot=sum(x*y for x,y in zip(a['normal'],b['normal']))
            tariff=6 if dot==0 else 7
            if match[j]==i:need(pairing==1 and tariff==7,'same-label dual pairing is1 with tariff7')
            if pairing:need(tariff==(7 if match[j]==i else 6),'matched distinct specials are orthogonal')
            pairs.append({'source_label':i,'target_label':match[j],'binary_dual_pairing':pairing,'rational_pairing_rank':tariff})
    # Independent complete combinatorial check of the counting proof. This is
    # a relaxation: it need not construct a completion of each partial dual set.
    feasible=0;best=-1;witnesses=[]
    for A in range(512):
        for B in range(512):
            used=0;coincident=0;bad=0;ok=True
            for j,row in enumerate(special[1]):
                if not(B>>j&1):continue
                support=A&row['mask']
                if support.bit_count()>1 or used&support:ok=False;break
                used|=support;coincident+=bool(support)
                bad+=bool(support>>match[j]&1)
            if not ok or A.bit_count()+B.bit_count()-coincident>9:continue
            feasible+=1;score=A.bit_count()+B.bit_count()-bad
            need(score<=9,'dual-set saving bound')
            if score>best:best=score;witnesses=[]
            if score==best:witnesses.append([A,B])
    need(feasible==3050 and best==9 and len(witnesses)==2,'finite combinatorial cross-check')
    need(all(p['rational_pairing_rank']==7 for p in pairs if p['source_label']==p['target_label']),
         'same-normal terms cannot be misbilled at6')
    out={'status':'PASS_EVERY_NINE_TERM_COLD_TARGET_FACTOR_HAS_PAIRING_RANK_SUM_GE63',
         'scientific_pin':src['scientific_pin'],'source':str(SOURCE),'source_sha256':sha256(SOURCE.read_bytes()).hexdigest(),
         'source_provenance':src['sources'],'support_strata':records,'target_to_source_normal_labels':match,
         'all81_special_pair_tariffs':pairs,'partial_dual_set_relaxations':feasible,
         'max_total_saving_from72':best,'attaining_special_choices':witnesses,
         'model':'Exactly9 binary outer-product terms for K R. Each term is charged the rational pairing rank between the root spans of its source and target supports. This grants a best possible cold contact U intersect V-perp and all other costs zero.',
         'proof':'Any9-term factorization is K T times T^-1 R. Both code spaces have9 hyperplane special directions and502 full-span directions. Count source-special a and target-special b, with c same-normal paired terms: tariff=72-a-b+c. A normal selected on both sides must occupy the same factor because their binary pairing is1; hence a+b-c is the size of a union of at most9 labels. Tariff>=63. T=I attains this optimistic tariff.',
         'limits':['No native reader or global caller admission.','More than9 terms can leave the retained code spaces and are not excluded.','Only this stated pairing-rank tariff, not a universal shared-circuit lower bound.','No new kappa.'],
         'attribution':'Root derived the two-sided native contact tariff and exact support/nullspace certificates. BIT lane independently derived the same floor and supplied the short same-normal duality counting proof. Underlying R/K, E8 and R429 ancestry is in the pinned source receipt.'}
    out=json.loads(json.dumps(out));path=HERE/'NINE-TERM-FLOOR.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'receipt differs')
    print(out['status']);print('1022 nonzero support ranks;81 exact tariffs;3050 dual-set checks;floor63')

if __name__=='__main__':main()
