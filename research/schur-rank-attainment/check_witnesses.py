"""Independent exact check of literal matrices. Imports no generation code.
SHIN09-git, substantial OpenAI Codex assistance. Apache-2.0.
Can read one fixture list on stdin; normal library use accepts the same records.
"""
from fractions import Fraction
import json
import sys


def require(ok,msg):
    if not ok:
        raise ValueError(msg)


def norm(x,p):
    return x%p if p else Fraction(x)


def matrix(raw,p):
    require(isinstance(raw,list) and raw and all(isinstance(row,list) for row in raw),"matrix list")
    n=len(raw)
    require(all(len(row)==n for row in raw),"square fixture")
    require(all(type(x) is int if p else type(x) is str for row in raw for x in row),"exact scalar encoding")
    if p:
        require(all(0<=x<p for row in raw for x in row),"noncanonical field scalar")
    return [[norm(x,p) for x in row] for row in raw]


def times(a,b,p):
    if not a:
        return []
    return [[norm(sum(a[i][k]*b[k][j] for k in range(len(b))),p)
             for j in range(len(b[0]))] for i in range(len(a))]


def minus(a,b,p):
    return [[norm(x-y,p) for x,y in zip(row,col)] for row,col in zip(a,b)]


def rank(a,p):
    # Column streaming, using independently normalized pivot vectors.
    piv={}
    for column in zip(*a):
        v=list(column)
        for i,u in sorted(piv.items()):
            z=v[i]
            v=[norm(x-z*y,p) for x,y in zip(v,u)]
        i=next((i for i,x in enumerate(v) if x),None)
        if i is not None:
            scale=pow(v[i],-1,p) if p else Fraction(1,1)/v[i]
            piv[i]=[norm(x*scale,p) for x in v]
    return len(piv)


def inv(a,p):
    n=len(a)
    e=[[norm(int(i==j),p) for j in range(n)] for i in range(n)]
    x=[row[:] for row in a]
    for c in range(n):
        j=next((j for j in range(c,n) if x[j][c]),None)
        require(j is not None,"singular leading block")
        x[c],x[j]=x[j],x[c]
        e[c],e[j]=e[j],e[c]
        scale=pow(x[c][c],-1,p) if p else 1/x[c][c]
        x[c]=[norm(v*scale,p) for v in x[c]]
        e[c]=[norm(v*scale,p) for v in e[c]]
        for i in range(n):
            if i==c:
                continue
            z=x[i][c]
            x[i]=[norm(v-z*w,p) for v,w in zip(x[i],x[c])]
            e[i]=[norm(v-z*w,p) for v,w in zip(e[i],e[c])]
    return e


def slice_(a,r0,r1,c0,c1):
    return [row[c0:c1] for row in a[r0:r1]]


def check(rec):
    p=rec["field"]
    require(type(p) is int and p in (0,2,3,5,7,11),"unsupported fixture field")
    d,n,rho=rec["d"],rec["n"],rec["rho"]
    require(all(type(x) is int for x in (d,n,rho)) and 1<=d<=n and 0<=rho<=2*d,"fixture dimensions/rank")
    A,B,H,P,Q=(matrix(rec[k],p) for k in ("A","B","H","P","Q"))
    require(all(len(x)==d for x in (A,B,H)) and len(P)==len(Q)==n,"declared dimensions")
    ai,bi=inv(A,p),inv(B,p)
    pq=times(P,Q,p)
    require(times(P,P,p)==P,"P idempotence")
    require(times(Q,Q,p)==Q,"Q idempotence")
    require(pq==times(Q,P,p),"P Q commutation")
    require(slice_(P,0,d,0,d)==A and slice_(Q,0,d,0,d)==B and slice_(pq,0,d,0,d)==H,"prescribed A B H")
    if n==d:
        actual=0
    else:
        S=minus(slice_(P,d,n,d,n),times(times(slice_(P,d,n,0,d),ai,p),slice_(P,0,d,d,n),p),p)
        Z=minus(slice_(Q,d,n,d,n),times(times(slice_(Q,d,n,0,d),bi,p),slice_(Q,0,d,d,n),p),p)
        actual=rank(minus(times(S,Z,p),times(Z,S,p),p),p)
    require(actual==rho,"literal Schur commutator rank")
    return actual


if __name__=="__main__":
    records=json.load(sys.stdin)
    for record in records:
        check(record)
    print("PASS_INDEPENDENT_LITERAL_WITNESSES",len(records))
