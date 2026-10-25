#!/usr/bin/env python3
"""Separate literal Gaussian-integer matrix replay; no producer imports."""
import itertools

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
    need(mm(correction,raw)==target,'all literal Gaussian columns')
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
    # No floating point, imported verifier or pending Git object.
    print('PASS independent: 32 Gaussian columns, 8 arbitrary dirty columns, 3 physical faults')
if __name__=='__main__':main()
