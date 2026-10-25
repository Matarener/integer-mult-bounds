#!/usr/bin/env python3
"""Separate literal Gaussian-integer matrix replay; no producer imports."""
import itertools
from fractions import Fraction as Q

Z=(0,0);ONE=(1,0);I=(0,1)
def need(ok,msg):
    if not ok:raise ValueError(msg)
def add(x,y):return x[0]+y[0],x[1]+y[1]
def mul(x,y):return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def neg(x):return -x[0],-x[1]
def zero(n):return [[Z for _ in range(n)] for _ in range(n)]
def eye(n):
    a=zero(n)
    for i in range(n):a[i][i]=ONE
    return a
def mm(a,b):
    n=len(a);out=zero(n)
    for i in range(n):
        for k in range(n):
            if a[i][k]!=Z:
                for j in range(n):
                    if b[k][j]!=Z:out[i][j]=add(out[i][j],mul(a[i][k],b[k][j]))
    return out
def sub(a,b):return [[add(x,neg(y)) for x,y in zip(r,s)] for r,s in zip(a,b)]
def upper(a):
    n=len(a);out=eye(2*n)
    for i in range(n):out[i][n:]=a[i]
    return out
def lower(a):
    n=len(a);out=eye(2*n)
    for i in range(n):out[n+i][:n]=a[i]
    return out
def blockdiag(a,b):
    n=len(a);out=zero(2*n)
    for i in range(n):out[i][:n]=a[i];out[n+i][n:]=b[i]
    return out

def main():
    # Rational rank-one Gram with the SAME minimal polynomial A(A-13I)=0.
    v=[1,2,2,2];n=16;A=zero(n);B=zero(n)
    for i,j,k,l in itertools.product(range(4),repeat=4):
        if j==l:A[4*i+j][4*k+l]=(v[i]*v[k],0)
        if i==k:B[4*i+j][4*k+l]=(v[j]*v[l],0)
    E=eye(n);T=zero(n);K=zero(n)
    for j in range(n):T[j][j]=ONE if j%3==0 else I;K[j][j]=ONE if j%3==0 else neg(I)
    need(mm(A,T)!=mm(T,A) and mm(B,T)!=mm(T,B),'varying physical charts')
    M=mm(upper([[neg(x) for x in r] for r in B]),lower(A))
    J=zero(2*n)
    for j in range(n):J[j][n+j]=(-1,0);J[n+j][j]=ONE
    G=blockdiag(E,K);Gi=blockdiag(E,T)
    raw=mm(G,M);target=mm(G,J)
    factors=[upper(mm(sub(A,E),T)),lower(K),upper(mm(sub(B,E),T))]
    correction=mm(mm(factors[0],factors[1]),factors[2])
    need(mm(correction,raw)==target,'old literal Gaussian columns')
    scalar=mm(mm(upper(sub(A,E)),lower(E)),upper(sub(B,E)))
    staged=mm(mm(blockdiag(E,K),scalar),blockdiag(E,T))
    need(staged==correction,'new full-chart path equals old3N on every column')
    need(mm(staged,raw)==target,'same tagged physical input and endpoint')
    need(mm(scalar,blockdiag(E,T))!=staged,'missing post-drop fault')
    need(mm(blockdiag(E,K),scalar)!=staged,'missing pre-lift fault')
    # Simulate donor rescaling explicitly: half, coefficient doubled ADD, restore.
    def word_upper(state,q,restore=True):
        out=[list(r) for r in state]
        for j in range(n):
            donor=n+j;out[donor]=[(Q(a,2),Q(b,2)) for a,b in out[donor]]
            for i in range(n):
                c=q[i][j];twice=(2*c[0],2*c[1])
                if c!=Z:out[i]=[add(x,mul(twice,y)) for x,y in zip(out[i],out[donor])]
            if restore:out[donor]=[(2*a,2*b) for a,b in out[donor]]
        return out
    start=blockdiag(E,T)
    run=word_upper(start,sub(B,E));run=mm(lower(E),run);run=word_upper(run,sub(A,E));run=mm(blockdiag(E,K),run)
    need(run==staged,'literal donor restoration word')
    bad=word_upper(start,sub(B,E),False);bad=mm(lower(E),bad);bad=word_upper(bad,sub(A,E));bad=mm(blockdiag(E,K),bad)
    need(bad!=staged,'unrestored donor fault')
    # Independent compensator by undoing raw shears then applying target.
    inverse=mm(lower([[neg(x) for x in r] for r in A]),upper(B))
    need(correction==mm(mm(target,inverse),Gi),'independent inverse construction')
    # Extended all-role operator fixes arbitrary dirty columns, no cleared helpers.
    helpers=8;extended=eye(2*n+helpers)
    for i in range(2*n):extended[i][:2*n]=correction[i]
    need(all(extended[i][j]==(ONE if i==j else Z) for i in range(2*n,2*n+helpers) for j in range(2*n+helpers)),'dirty returns')
    need(all(extended[i][j]==Z for i in range(2*n) for j in range(2*n,2*n+helpers)),'dirty isolation')
    need(mm(factors[0],factors[2])!=correction,'missing middle fails')
    wrong=upper(mm(T,sub(B,E)))
    need(mm(mm(factors[0],factors[1]),wrong)!=correction,'wrong physical order fails')
    need(mm(correction,M)!=target,'missing chart preparation fails')
    # One/two arbitrary triangular layers have an identity diagonal block.
    for x,y in itertools.product((upper(A),lower(A)),(upper(B),lower(B))):
        q=mm(x,y)
        tl=[r[:n] for r in q[:n]];br=[r[n:] for r in q[n:]]
        need(tl==E or br==E,'two layer invariant')
    # Literal C_u recipes on all eight addresses for all seven nonzero3-bit u.
    def perm(mapping):
        out=zero(8)
        for j,k in enumerate(mapping):out[k][j]=ONE
        return out
    def cu(u,inverse=False):
        out=zero(8);a=(Q(1,2),Q(-1 if inverse else 1,2));b=(Q(1,2),Q(1 if inverse else -1,2))
        for j in range(8):out[j][j]=a;out[j^u][j]=b
        return out
    for u in range(1,8):
        p=(u&-u).bit_length()-1;e=1<<p
        P=perm([x^((u^e) if x&e else 0) for x in range(8)])
        X=perm([x^u for x in range(8)])
        forward=mm(mm(P,cu(e)),P);inverse=mm(X,forward)
        need(forward==cu(u) and inverse==cu(u,True),'phase-exact positive-child recipes')
        need(mm(forward,inverse)==eye(8),'two boundary directions cancel')
        bad=[[mul(I,z) for z in row] for row in inverse]
        need(bad!=cu(u,True),'global phase fault')
    print('PASS independent: 32 matched Gaussian columns,8dirty; literal rescaling;56native columns;phasefaults')
if __name__=='__main__':main()
