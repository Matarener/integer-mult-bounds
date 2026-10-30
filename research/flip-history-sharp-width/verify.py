#!/usr/bin/env python3
"""Check the sharp bit-flip threshold over exact Gaussian rationals.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from itertools import product
import json


def z(a=0,b=0): return (F(a),F(b))
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def neg(a): return (-a[0],-a[1])
def sub(a,b): return add(a,neg(b))
def mul(a,b): return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def inv(a):
    norm=a[0]*a[0]+a[1]*a[1]
    return (a[0]/norm,-a[1]/norm)
def power(a,n):
    out=z(1)
    for _ in range(n): out=mul(out,a)
    return out

def require(condition,message):
    if not condition: raise ValueError(message)


def rank(rows):
    basis={}
    for row in rows:
        row=list(row)
        for k,b in sorted(basis.items()):
            c=row[k]; row=[sub(x,mul(c,y)) for x,y in zip(row,b)]
        pivot=next((i for i,x in enumerate(row) if x!=z()),None)
        if pivot is not None:
            c=inv(row[pivot]); basis[pivot]=[mul(x,c) for x in row]
    return len(basis)


def kron(a,b):
    return [[mul(a[i][j],b[k][l]) for j in range(len(a)) for l in range(len(b))]
            for i in range(len(a)) for k in range(len(b))]


def lifted(a,b,f):
    h=[[a,b],[b,a]]; out=[[z(1)]]
    for _ in range(f): out=kron(out,h)
    return out


def plus_rows(h):
    n=len(h)
    e=[[z(F(int(i==j)+int((i^(n-1))==j),2)) for j in range(n)] for i in range(n)]
    eh=[[mul(z(F(1,2)),add(h[i][j],h[i^(n-1)][j])) for j in range(n)] for i in range(n)]
    return [x for row in e for x in row],[x for row in eh for x in row]


def block(row,i,q):
    return [x if j==i else z() for j in range(q) for x in row]


def main():
    pairs=[(z(a),z(b)) for a,b in product(range(-3,4),repeat=2)
           if a*b*(a*a-b*b)!=0]
    pairs += [(z(F(1,2),F(1,2)),z(F(1,2),F(-1,2))),
              (z(1,1),z(0,1)),(z(1,2),z(2,-1)),(z(2),z(0,1))]
    literal=owners=scalar_checks=0
    for a,b in pairs:
        lp,lm=add(a,b),sub(a,b)
        require(mul(mul(a,b),mul(lp,lm))!=z(),'invalid fixture')
        for f in range(1,6):
            h=lifted(a,b,f); e,eh=plus_rows(h)
            require(rank([e,eh])==(1 if f==1 else 2),'literal character span')
            n=1<<f
            eigen0=power(lp,f)
            for i in range(n):
                total=z()
                for j in range(n): total=add(total,h[i][j])
                require(total==eigen0,'literal zero-weight eigenvector')
            if f>=2:
                eigen2=mul(power(lp,f-2),power(lm,2))
                for i in range(n):
                    total=z()
                    for j in range(n): total=add(total,mul(h[i][j],z((-1)**((j&3).bit_count()))))
                    require(total==mul(eigen2,z((-1)**((i&3).bit_count()))),'literal two-weight eigenvector')
            if f<=3:
                for q in range(1,5):
                    rows=[block(e,i,q) for i in range(q)]
                    targets=[block(eh,i,q) for i in range(q)]
                    require(rank(rows+targets)-rank(rows)==(0 if f==1 else q),'distinct-owner quotient')
                    owners+=1
            literal+=1
        for f in range(2,65):
            difference=sub(power(lp,f),mul(power(lp,f-2),power(lm,2)))
            require(difference==mul(z(4),mul(mul(a,b),power(lp,f-2))) and difference!=z(),
                    'character separation')
            scalar_checks+=1
    for a,b in [(z(2),z()),(z(),z(2))]:
        for f in range(1,6):
            e,eh=plus_rows(lifted(a,b,f)); require(rank([e,eh])==1,'ordinary target control')
    e,eh=plus_rows(lifted(z(2),z(1),2))
    require(rank([e,eh,eh])-rank([e])==1,'duplicate owner must not count twice')
    require(rank([e,eh,eh])-rank([e,eh])==0,'cached target removes charge')
    require(rank(plus_rows(lifted(z(2),z(1),1)))==1,'width one is free')
    print('PASS_FLIP_HISTORY_SHARP_WIDTH '+json.dumps({'parameter_pairs':len(pairs),
        'literal_tensors':literal,'owner_cases':owners,'character_checks':scalar_checks,
        'boundary_controls':13},sort_keys=True))


if __name__=='__main__': main()
