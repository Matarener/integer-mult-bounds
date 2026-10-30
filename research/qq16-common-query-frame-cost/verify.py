#!/usr/bin/env python3
"""Exact source phase certificate and quantified common-frame cost arithmetic."""
import argparse
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from query_frame_sources import loaded,need
from phase_gram import canonical,certificate,rank,outer,xor,lifted_bound


def small_rank_lemmas():
    cases=0
    for n in range(1,5):
        positions=[(i,j) for i in range(n) for j in range(i,n)]
        for mask in range(1<<len(positions)):
            A=[0]*n
            for bit,(i,j) in enumerate(positions):
                if mask>>bit&1:
                    A[i]^=1<<j
                    if i!=j:A[j]^=1<<i
            r=rank(A)
            for q in range(1,1<<n):
                d=rank(xor(A,outer(q,n)))
                need(abs(d-r)<=1,'rank-one update inequality')
                inside=rank((*A,q))==r
                if not inside:need(d==r+1,'symmetric rank update outside image')
                if r==1:
                    u=next(row for row in A if row)
                    need(tuple(A)==outer(u,n),'symmetric rank-one square')
                    need(d==(0 if u==q else 2),'rank-one cancellation classification')
                cases+=1
    return cases


def intersection_lemmas():
    cases=0
    for n in range(1,4):
        positions=[(i,j) for i in range(n) for j in range(i,n)]
        matrices=[]
        for mask in range(1<<len(positions)):
            A=[0]*n
            for bit,(i,j) in enumerate(positions):
                if mask>>bit&1:
                    A[i]^=1<<j
                    if i!=j:A[j]^=1<<i
            matrices.append(tuple(A))
        for A in matrices:
            for B in matrices:
                r,t=rank(A),rank(B)
                overlap=r+t-rank((*A,*B))
                need(rank(xor(A,B))>=r+t-2*overlap,'symmetric image-intersection rank inequality')
                cases+=1
    return cases


def plane_mixing_fixture(receipt):
    # One genuinely nonuniform rank-one change mixing two distinct plane directions.
    u,v=receipt['records'][0][2],receipt['records'][1][2]
    def lift(q,plane):
        return sum(((q>>i)&1)<<(2*i+plane) for i in range(73))
    w=lift(u,0)^lift(v,1)
    Delta=outer(w,146)
    defects=[]
    for row in receipt['records']:
        q=row[2]
        B=xor(outer(lift(q,0),146),outer(lift(q,1),146))
        defects.append(rank(xor(Delta,B)))
    need(rank(Delta)==1 and set(defects)=={3},'plane-mixing perturbation fixture')
    return {'lambda':2,'Delta_rank':1,'defect_rank':3,'branches':len(defects),
            'rank_sum':sum(defects),'rank_sum_lower':104*2+80}


def compute():
    L,(P,R,routes,labels,_),pins=loaded()
    result=certificate(L,P,R,routes,labels)
    result['lifted_bound']=lifted_bound(result,read_json(HERE/'PARTITION.json'))
    result['source_pins']=pins
    result['small_rank_lemma_cases']=small_rank_lemmas()
    result['rank_intersection_cases']=intersection_lemmas()
    result['plane_mixing_fixture']=plane_mixing_fixture(result)
    return result


def read_json(path):
    def unique(pairs):
        out={}
        for k,v in pairs:
            need(k not in out,'unique receipt keys')
            out[k]=v
        return out
    return json.loads(path.read_text(),object_pairs_hook=unique)


def validate(actual,expected):
    need(canonical(actual)==canonical(expected),'complete typed phase certificate')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    target=HERE/'CERTIFICATE.json'
    if args.write:need(not target.exists(),'refuse certificate overwrite')
    result=compute()
    if args.write:
        need(not target.exists(),'refuse certificate overwrite')
        target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:validate(result,read_json(target))
    print('PASS_QQ16_COMMON_QUERY_FRAME_COST ports=104 groups=12 all_lambda_frame_gate=PASS')


if __name__=='__main__':main()
