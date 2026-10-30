#!/usr/bin/env python3
"""Independent dense binary and exact Gaussian operator checks; no producer imports."""
from collections import deque
from fractions import Fraction as Q
from pathlib import Path
import json


def need(ok,message):
    if not ok:raise ValueError(message)
def eye(d):return tuple(tuple(int(i==j) for j in range(d)) for i in range(d))
def product(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(a)))%2 for j in range(len(a))) for i in range(len(a)))
def gf_rank(rows):
    a=[list(r) for r in rows];r=0
    for j in range(len(a[0]) if a else 0):
        pivot=next((i for i in range(r,len(a)) if a[i][j]),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r]
        for i in range(len(a)):
            if i!=r and a[i][j]:a[i]=[x^y for x,y in zip(a[i],a[r])]
        r+=1
    return r

def phi(a):
    n=len(a)//2
    return gf_rank([row[n:] for row in a[:n]])
def inv(a):
    d=len(a);x=[list(row)+list(unit) for row,unit in zip(a,eye(d))]
    for j in range(d):
        i=next(i for i in range(j,d) if x[i][j]);x[i],x[j]=x[j],x[i]
        for i in range(d):
            if i!=j and x[i][j]:x[i]=[a^b for a,b in zip(x[i],x[j])]
    return tuple(tuple(row[d:]) for row in x)

def group2():
    gens=[]
    for k in range(2):
        h=[list(r) for r in eye(4)];h[k],h[2+k]=h[2+k],h[k];gens.append(tuple(map(tuple,h)))
        s=[list(r) for r in eye(4)];s[2+k][k]=1;gens.append(tuple(map(tuple,s)))
    c=[list(r) for r in eye(4)];c[1][0]=1;c[2][3]=1;gens.append(tuple(map(tuple,c)))
    seen={eye(4)};queue=deque(seen)
    while queue:
        a=queue.popleft()
        for g in gens:
            b=product(g,a)
            if b not in seen:seen.add(b);queue.append(b)
    need(len(seen)==720,'Sp4 group size')
    return sorted(seen),gens

# Exact Gaussian rationals, avoiding numerical state-vector comparisons.
z=(Q(0),Q(0));one=(Q(1),Q(0));ii=(Q(0),Q(1))
def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[0],-a[1]
def times(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def adj(a):return tuple(tuple((a[j][i][0],-a[j][i][1]) for j in range(len(a))) for i in range(len(a)))
def gm(a,b):
    out=[]
    for i in range(len(a)):
        row=[]
        for j in range(len(a)):
            s=z
            for k in range(len(a)):s=add(s,times(a[i][k],b[k][j]))
            row.append(s)
        out.append(tuple(row))
    return tuple(out)
def pauli(n,x,y):return tuple(tuple((Q((-1)**((y&j).bit_count()&1)),Q(0)) if i==j^x else z for j in range(1<<n)) for i in range(1<<n))
def cgate(n,q,sign):
    a=(Q(1,2),Q(sign,2));b=(Q(1,2),Q(-sign,2))
    return tuple(tuple(add(a if i==j else z,b if i==j^q else z) for j in range(1<<n)) for i in range(1<<n))
def tableau(u,n):
    columns=[];phases=(one,ii,neg(one),neg(ii))
    for bit in range(2*n):
        p=pauli(n,1<<bit if bit<n else 0,1<<(bit-n) if bit>=n else 0)
        v=gm(gm(u,p),adj(u));matches=[]
        for x in range(1<<n):
            for y in range(1<<n):
                p=pauli(n,x,y)
                for phase in phases:
                    if v==tuple(tuple(times(phase,t) for t in row) for row in p):matches.append((x,y))
        need(len(matches)==1,'exact Pauli conjugation')
        x,y=matches[0];columns.append(x|(y<<n))
    return tuple(tuple((columns[j]>>i)&1 for j in range(2*n)) for i in range(2*n))

def main():
    g,gens=group2();triangles=0
    for a in g:
        ra=phi(a)
        need(phi(inv(a))==ra,'inverse width')
        for b in g:
            # Independently multiply just the upper-right block.
            block=[[sum(a[i][k]*b[k][j] for k in range(4))%2 for j in (2,3)] for i in (0,1)]
            need(gf_rank(block)<=ra+phi(b),'native-width triangle');triangles+=1
    C=eye(4);C=[list(r) for r in C];C[0][2]=1;C=tuple(map(tuple,C))
    F=[list(r) for r in eye(4)];F[0][2]=F[1][3]=1;F=tuple(map(tuple,F))
    K=product(F,inv(C));need(phi(K)==1,'two-bit intrinsic complement')
    translations=0
    for l in g:
        for r in (eye(4),gens[0],gens[-1]):
            start=product(product(l,C),r);finish=product(product(l,F),r)
            need(abs(phi(finish)-phi(start))<=1,'matched intrinsic bound');translations+=1
    # Both orientations and all two-bit nonzero rotations are checked as exact operators.
    operators=0
    for q in (1,2,3):
        for sign in (-1,1):
            t=tableau(cgate(2,q,sign),2)
            expected=[list(row) for row in eye(4)]
            for i in range(2):
                for j in range(2):expected[i][2+j]=((q>>i)&1)*((q>>j)&1)
            need(t==tuple(map(tuple,expected)),'Gaussian Cq symplectic action');operators+=1
    result=json.loads((Path(__file__).parent/'RESULT.json').read_text())
    c=result['counterexample'];matrix=lambda cols:tuple(tuple((cols[j]>>i)&1 for j in range(18)) for i in range(18))
    native=matrix(c['relative_columns']);translated=matrix(c['translated_relative_columns'])
    need(phi(native)==8 and gf_rank([[native[i][j]^int(i==j) for j in range(18)] for i in range(18)])==10,'actual canonical cocycle')
    need(phi(translated)==9,'actual translated counterexample')
    source=matrix(c['canonical_source_columns']);q=386
    rot=[list(row) for row in eye(18)]
    for i in range(9):
        for j in range(9):rot[i][9+j]=((q>>i)&1)*((q>>j)&1)
    rot=tuple(map(tuple,rot));h=[list(row) for row in eye(18)];h[1],h[10]=h[10],h[1];h=tuple(map(tuple,h))
    full=[list(row) for row in eye(18)]
    for i in range(9):full[i][9+i]=1
    full=tuple(map(tuple,full));adapter=product(source,inv(rot))
    need(phi(adapter)==0 and phi(product(product(h,adapter),h))==2,'independent adapter repricing')
    need(phi(product(product(h,product(full,inv(rot))),h))==8,'independent intrinsic repair')

    need(result['intrinsic_total_bound']==104*8+104*8+72*9==2312,'old endpoint sum')
    need(result['changed_full_Y_endpoint_bound']==104*8+104*9+72*9==2416,'changed endpoint reopening control')
    print(f'PASS_INDEPENDENT_PROGRESS: {triangles} Sp4 products; {translations} translations; {operators} exact Gaussian operators')
if __name__=='__main__':main()
