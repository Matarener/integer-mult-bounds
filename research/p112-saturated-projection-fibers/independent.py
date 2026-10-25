#!/usr/bin/env python3
"""Independent exact implementation: permutation determinants and pivot quotients.
Chris R / Clear1nsight with OpenAI Codex assistance. Apache-2.0.
No import from verify.py or any predecessor verifier.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, permutations, product
import json
from math import gcd
from pathlib import Path
HERE=Path(__file__).resolve().parent

def check(ok,why):
    if not ok:raise ValueError(why)

def canon(v):
    g=gcd(*v)
    if not g:return tuple(v)
    if next(x for x in v if x)<0:g=-g
    return tuple(x//g for x in v)

def rref(rows):
    a=[[Fraction(x) for x in r]for r in rows];p=0
    for c in range(len(a[0])):
        k=next((k for k in range(p,len(a))if a[k][c]),None)
        if k is None:continue
        a[p],a[k]=a[k],a[p];d=a[p][c];a[p]=[x/d for x in a[p]]
        for j in range(len(a)):
            if j!=p:
                d=a[j][c];a[j]=[x-d*y for x,y in zip(a[j],a[p])]
        p+=1
        if p==len(a):break
    return tuple(tuple(r)for r in a[:p])

def det(a):
    n=len(a);out=0
    for p in permutations(range(n)):
        sign=(-1)**sum(p[i]>p[j]for i in range(n)for j in range(i+1,n));v=sign
        for i in range(n):v*=a[i][p[i]]
        out+=v
    return out

def root_shell():
    roots=[]
    for i,j in combinations(range(8),2):
        for s in (-2,2):
            r=[0]*8;r[i]=2;r[j]=s;roots.append(tuple(r))
    for tail in product((-1,1),repeat=7):
        r=(1,)+tail
        if sum(x==-1 for x in r)%2==0:roots.append(r)
    return sorted(roots)

def gram_certificate():
    records=[];positive=0;hist=Counter()
    for off in product((-1,0,1),repeat=6):
        g=[[2*(i==j)for j in range(4)]for i in range(4)]
        for (i,j),x in zip(combinations(range(4),2),off):g[i][j]=g[j][i]=x
        if any(det([r[:k]for r in g[:k]])<=0 for k in range(1,5)):continue
        positive+=1;d=det(g)
        cof=[[(-1)**(i+j)*det([[g[a][b]for b in range(4)if b!=j]for a in range(4)if a!=i])for j in range(4)]for i in range(4)]
        candidates=[]
        for k in product(range(-2,3),repeat=4):
            if next((x for x in k if x),0)>0 and sum(k[i]*cof[j][i]*k[j]for i in range(4)for j in range(4))==2*d:candidates.append(k)
        check(len(candidates)<=12,'rank4 bound')
        if len(candidates)<11:continue
        spans={}
        for tri in combinations(range(len(candidates)),3):
            key=rref([candidates[i]for i in tri])
            if len(key)==3:spans[key]=spans.get(key,0)|sum(1<<i for i in tri)
        check(max(m.bit_count()for m in spans.values())==6,'all rank3 candidate closures')
        six=sorted(m for m in spans.values()if m.bit_count()==6)
        counts=Counter((x&y).bit_count()for x,y in combinations(six,2))
        check(len(six)==12 and min(counts)==2,'saturated intersections')
        hist.update(counts);records.append([list(off),len(candidates),six,dict(sorted(counts.items()))])
    check(positive==393 and len(records)==105 and hist=={2:1890,3:5040},'Gram census')
    return sha256(json.dumps(records,separators=(',',':'),sort_keys=True).encode()).hexdigest()

def quotient_certificate(roots):
    records=[]
    for i,j in combinations(range(120),2):
        a,b=roots[i],roots[j]
        if sum(x*y for x,y in zip(a,b)):continue
        p,q=next((p,q)for p,q in combinations(range(8),2)if a[p]*b[q]-a[q]*b[p])
        d=a[p]*b[q]-a[q]*b[p];groups={};zeros=[]
        for t,r in enumerate(roots):
            x=r[p]*b[q]-r[q]*b[p];y=a[p]*r[q]-a[q]*r[p]
            v=tuple(d*r[k]-x*a[k]-y*b[k]for k in range(8))
            if not any(v):zeros.append(t);continue
            key=canon(v);groups[key]=groups.get(key,0)|(1<<t)
        masks=sorted(groups.values())
        check(Counter(m.bit_count()for m in masks)=={1:30,2:32,4:6}and zeros==[i,j],'quotient partition')
        records.append([i,j,masks])
    check(len(records)==3780,'orthogonal plane completeness')
    return sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest()

def main():
    expected=json.loads((HERE/'RESULT.json').read_text());roots=root_shell()
    check(expected['caller']['contradiction_margin']==2 and expected['uniform_support_floor']==178,'caller margin receipt')
    check(len(roots)==120 and all(sum(x*x for x in r)==8 for r in roots),'independent shell')
    check(gram_certificate()==expected['saturated_pair']['certificate_digest'],'Gram receipt')
    check(quotient_certificate(roots)==expected['orthogonal_kernel']['partition_digest'],'quotient receipt')
    w=[2,2,5]+[6]*8;cap={2:2,3:4,4:8,5:12,6:20};dh=[0,53,78,92,100,106,109]
    check(all(sum(cap[x]for x in w[:len(w)-6+lev])>=dh[lev]for lev in range(1,7)),'independent historical feasibility')
    check(sum(cap[x]for x in w[:5])==56>=53,'old basis cutoff does not apply')
    check(sum(cap[x]for x in w[:6])==76<78,'exact quotient witness')
    check(sum(cap[x]for x in w)==176 and sum(x-2 for x in w)==35<36,'caller charges')
    floors=[2*(112-s)-u for s,u in [(0,46),(1,35),(2,34),(3,33)]]
    check(floors==[178,187,186,185]and min(floors)>176,'incidence contradiction')
    # Separate exhaustive multiset check of the tiny convex-capacity corollary.
    rows=[]
    for n in range(12):
        eligible=[w for w in combinations_with_replacement(range(2,7),n)if sum(x-2 for x in w)<=35]
        maximum=max(sum(cap[x]for x in w)for w in eligible)
        best=[w for w in eligible if sum(cap[x]for x in w)==maximum]
        check(len(best)==1,'unique sorted extremizer')
        rows.append({'pieces':n,'maximum_capacity':maximum,'maximizer':list(best[0])})
    check(rows==expected['capacity_corollary']['maxima_by_length'],'capacity DP versus exhaustive multisets')
    check(rows[-1]['maximum_capacity']==176 and rows[-1]['maximizer']==[2,2,5]+[6]*8,'extremal literal caller')
    print('PASS_INDEPENDENT_SATURATED_FIBERS Gram105 quotient_planes3780 floor178 margin2')
if __name__=='__main__':main()
