#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate determinant/chart and minimum permutation-route checks.
No imports from the construction or verifier. Same assisted session, not human review.
"""
from itertools import combinations, permutations, product
import json
from math import gcd
from pathlib import Path


def check(ok, why):
    if not ok:
        raise ValueError(why)


def times(a,b,m):
    return [[sum(x*y for x,y in zip(row,column))%m for column in zip(*b)] for row in a]


def det(a,m):
    total=0
    for p in permutations(range(len(a))):
        sign=(-1)**sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))
        term=sign
        for i,j in enumerate(p):term*=a[i][j]
        total+=term
    return total%m


def inv_cramer(a,m):
    d=det(a,m)
    check(gcd(d,m)==1,'unit minor')
    n=len(a)
    return [[(-1)**(i+j)*det([[a[k][l] for l in range(n) if l!=i] for k in range(n) if k!=j],m)*pow(d,-1,m)%m for j in range(n)] for i in range(n)]


def rank_field(a,q):
    rows=[[x%q for x in row] for row in a];r=0
    for j in range(len(rows[0])):
        k=next((k for k in range(r,len(rows)) if rows[k][j]),None)
        if k is None:continue
        rows[r],rows[k]=rows[k],rows[r]
        z=pow(rows[r][j],-1,q);rows[r]=[x*z%q for x in rows[r]]
        for k in range(r+1,len(rows)):
            z=rows[k][j];rows[k]=[(x-z*y)%q for x,y in zip(rows[k],rows[r])]
        r+=1
    return r


def charts():
    accepted={}
    for n,m,q in [(3,3,3),(2,9,3)]:
        count=0
        for flat in product(range(m),repeat=n*n):
            matrix=[list(flat[n*i:n*i+n]) for i in range(n)]
            if times(matrix,matrix,m)!=matrix:continue
            r=rank_field(matrix,q)
            if not 0<r<n:continue
            minors=[(s,det([[matrix[i][j] for j in s] for i in s],m)) for s in combinations(range(n),r)]
            check(sum(d for _,d in minors)%m==1,'principal minor sum exactly one')
            s=next(s for s,d in minors if gcd(d,m)==1)
            order=list(s)+[i for i in range(n) if i not in s]
            qp=[[matrix[i][j] for j in order] for i in order]
            a=[row[:r] for row in qp[:r]];b=[row[r:] for row in qp[:r]];c=[row[:r] for row in qp[r:]]
            x=times(c,inv_cramer(a,m),m)
            t=[[int(i==j) for j in range(n)] for i in range(n)]
            for i in range(r):
                for j in range(n-r):t[i][r+j]=-b[i][j]%m
            for i in range(n-r):
                for j in range(r):t[r+i][j]=x[i][j]
                for j in range(n-r):t[r+i][r+j]=(int(i==j)-sum(x[i][k]*b[k][j] for k in range(r)))%m
            te=[[entry if j<r else 0 for j,entry in enumerate(row)] for row in t]
            check(times(qp,t,m)==te and det(t,m)==1,'Cramer chart intertwiner and determinant')
            count+=1
        accepted[f'{n}x{n}_mod{m}']=count
    return accepted


def transpositions(p):
    seen=set();cycles=0
    for i in range(len(p)):
        if i in seen:continue
        cycles+=1;j=i
        while j not in seen:seen.add(j);j=p[j]
    return len(p)-cycles


def routes():
    cases=0;perms=0
    for n in range(2,8):
        best={r:n for r in range(1,n)}
        for p in permutations(range(n)):
            perms+=1;cost=transpositions(p)
            for r in range(1,n):
                if min(p[:r])>max(p[r:]):best[r]=min(best[r],cost)
        for r,cost in best.items():
            check(cost==min(r,n-r),'optimal graph routing transpositions')
            for i in range(r):
                endpoint=n-r+i
                p=list(range(n));p[i],p[endpoint]=p[endpoint],p[i]
                check(all(p[k]<p[i] for k in range(i+1,endpoint+1)),'star route turns every arm')
            cases+=1
    return {'dimension_rank_cases':cases,'all_permutations':perms}


def diagonals():
    checked=0
    for m in [3,9,25,49,81]:
        for a in range(m):
            if gcd(a,m)!=1:continue
            word=[[[1,1],[0,1]],[[1,0],[a-1,1]],[[1,-pow(a,-1,m)],[0,1]],[[1,0],[-a*(a-1),1]]]
            result=[[1,0],[0,1]]
            for factor in word:result=times(result,factor,m)
            check(result==[[a,0],[0,pow(a,-1,m)]],'four shear diagonal')
            checked+=1
    return checked


def main():
    result=json.loads((Path(__file__).resolve().parent/'RESULT.json').read_bytes())
    # Count from stages, independently of the primary invoice implementation.
    m,r=64,7
    pivot=4*sum(3*len(range(i+1,m-r+i+1)) for i in range(r))
    graph=4*sum(1 for i in range(r) for j in range(r,m))*2
    diagonal=2*4*r
    adds=pivot+graph+diagonal
    swaps=2*(2*3*r)+4*2*r+2*(2*r)*2
    check(result['ambient64_invoice']=={'add':adds,'swap':swaps}=={'add':8036,'swap':196},'separate stage invoice')
    print('PASS_SEPARATE_PRINCIPAL_CHART_AND_ROUTING',json.dumps({'charts':charts(),'routes':routes(),'diagonal_units':diagonals(),'invoice':[adds,swaps]},sort_keys=True))

if __name__=='__main__':main()
