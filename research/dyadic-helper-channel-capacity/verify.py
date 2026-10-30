"""Check Smith certificates with independent determinantal divisors.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from itertools import product as tuples, permutations, combinations
from math import gcd, prod
from random import Random
from pathlib import Path
import hashlib
import json
from capacity import capacity, kernel, product, eye, need

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def det(a):
    n=len(a)
    return sum((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))*
               prod(a[i][p[i]] for i in range(n)) for p in permutations(range(n)))


def check(a, c=None):
    c=capacity(a) if c is None else c
    m,n=len(a),len(a[0])
    need(abs(det(c['U']))==abs(det(c['V']))==1,'Unimodular certificate')
    scaled=[[int(c['denominator']*Q(x)) for x in row] for row in a]
    need(product(product(c['U'],scaled),c['V'])==c['S'],'Smith identity')
    need(all(c['S'][i][j]==0 for i in range(m) for j in range(n) if i!=j),
         'Diagonal certificate')
    factors=c['factors']
    need(all(x>0 for x in factors) and all(y%x==0 for x,y in zip(factors,factors[1:])),
         'Positive divisibility chain')
    g=1
    for k in range(1,min(m,n)+1):
        divisor=0
        for rows in combinations(range(m),k):
            for cols in combinations(range(n),k):
                divisor=gcd(divisor,det([[scaled[i][j] for j in cols] for i in rows]))
        g=g*factors[k-1] if k<=len(factors) else 0
        need(divisor==g,'Independent gcd of every minor')
    t=c['capacity']
    if t:
        need(product(product(c['left'],a),c['right'])==eye(t),'Constructive unit block')
    need(all(x & (x-1)==0 for x in factors[:t]),'Dyadic unit block')
    need(t==len(factors) or factors[t] & (factors[t]-1),'Nonunit obstruction')
    return c


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())['files']
    for pin in pins:
        if pin['usage']=='input':
            need(hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],
                 'Pinned caller proof')
    exhaustive=0
    for entries in tuples(range(-3,4),repeat=4):
        check([list(entries[:2]),list(entries[2:])])
        exhaustive+=1
    rng=Random(5611)
    wider=0
    for m in range(1,6):
        for n in range(1,6):
            for _ in range(3):
                a=[[Q(rng.randint(-10,10),2**rng.randrange(4)) for _ in range(n)] for _ in range(m)]
                check(a)
                wider+=1
    # Four elementary ADDs give a unimodular causal prefix.
    a=[[1,0,1],[0,1,2],[1,2,6]]
    b=[[2,2,-1],[2,5,-2],[-1,-2,1]]
    need(product(a,b)==eye(3) and product(b,a)==eye(3),'Exact complete identity word')
    left=kernel([[a[0][2],a[1][2]]],2)
    right=kernel([[b[2][0],b[2][1]]],2)
    pairing=product([list(row) for row in zip(*left)],right)
    causal=check(pairing)
    need(causal['rational_rank']==1 and causal['capacity']==0 and causal['factors']==[5],
         'Rational cut rank overcounts dyadic channels')
    joint=check([[3,0],[0,5]])
    need(joint['capacity']==1 and joint['factors']==[1,15],'Joint pairing exceeds entry test')
    lifted=check([[Q(5,8)]])
    need(lifted['capacity']==0,'A power of two does not remove the odd obstruction')
    need(check([[8,0],[0,0]])['capacity']==1,'Rank-deficient positive control')
    controls=0
    for bad in [[[Q(1,3)]],[[1,2],[3]]]:
        try:capacity(bad)
        except ValueError:controls+=1
        else:raise ValueError('Invalid matrix accepted')
    for field in ['capacity','factors','U']:
        bad=capacity([[3,0],[0,5]])
        if field=='capacity':bad[field]=2
        elif field=='factors':bad[field]=[1,1]
        else:bad[field][0][0]+=1
        try:check([[3,0],[0,5]],bad)
        except ValueError:controls+=1
        else:raise ValueError('False capacity certificate accepted')
    result=dict(exhaustive_2_by_2=exhaustive,rectangular_dyadic=wider,
                causal_pairing=pairing,causal_rational_rank=1,causal_capacity=0,
                joint_factors=joint['factors'],joint_capacity=1,rejected_inputs=controls)
    need(result==json.loads((HERE/'RESULT.json').read_text()),'Committed receipt')
    print(json.dumps(result,sort_keys=True))
    print('PASS_DYADIC_HELPER_CHANNEL_CAPACITY')


if __name__=='__main__':main()
