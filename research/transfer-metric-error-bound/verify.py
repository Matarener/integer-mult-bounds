#!/usr/bin/env python3
"""Check transfer certificates against literal endpoint matrices and controls."""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product,combinations
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from certificate import check,eye,mul,sub,scale,transpose,psd


def require(value,message):
    if not value: raise ValueError(message)


def encode(x):
    if isinstance(x,dict): return {k:encode(v) for k,v in x.items()}
    if isinstance(x,list): return [encode(y) for y in x]
    if isinstance(x,Q): return str(x)
    return x


def det(a):
    a=[list(r) for r in a]; out=Q(1)
    for k in range(len(a)):
        pivot=next((i for i in range(k,len(a)) if a[i][k]),None)
        if pivot is None: return Q(0)
        if pivot!=k: a[pivot],a[k]=a[k],a[pivot]; out=-out
        out*=a[k][k]
        for i in range(k+1,len(a)):
            factor=a[i][k]/a[k][k]
            for j in range(k+1,len(a)): a[i][j]-=factor*a[k][j]
    return out


def principal_psd(a):
    return all(det([[a[i][j] for j in ids] for i in ids])>=0
               for k in range(1,len(a)+1) for ids in combinations(range(len(a)),k))


def endpoint(T,F,B,f):
    d=len(T); words=list(product(range(d),repeat=f)); p=len(F); q=len(B[0])
    out=[[Q(0) for _ in range(q*len(words))] for _ in range(p*len(words))]
    for yi,y in enumerate(words):
        for xi,x in enumerate(words):
            a=F
            for yy,xx in zip(y,x): a=mul(a,T[yy][xx])
            a=mul(a,B)
            for i in range(p):
                for j in range(q): out[i*len(words)+yi][j*len(words)+xi]=a[i][j]
    return out


def fixture(T,F,B,P,a,b,c):
    return encode(dict(transfer_dimension=len(P),local_dimension=len(T),transitions=T,
        left=F,right=B,metric=P,left_bound=a,right_bound=b,squared_rate=c))


def main():
    certificates=endpoints=psd_controls=0
    zero=scale(Q(0),eye(2)); Z=[[Q(1),Q(0)],[Q(0),Q(-1)]]
    for epsilon in (Q(1),Q(1,3),Q(1,16)):
        T=[[eye(2),zero],[zero,Z]]; F=[[epsilon/2,-epsilon/2]]; B=[[Q(1)],[Q(1)]]
        data=fixture(T,F,B,eye(2),epsilon**2/2,Q(2),Q(1)); check(data); certificates+=1
        for f in range(1,6):
            E=endpoint(T,F,B,f); n=len(E)
            expected=[[epsilon if i==j and i.bit_count()%2 else Q(0) for j in range(n)] for i in range(n)]
            require(E==expected,'literal parity endpoint')
            require(mul(E,E)==scale(epsilon,E),'attaining projector')
            endpoints+=1
    R=[[Q(3,5),Q(-4,5)],[Q(4,5),Q(3,5)]]
    S=[[Q(2),Q(0)],[Q(0),Q(1)]]; Si=[[Q(1,2),Q(0)],[Q(0),Q(1)]]
    for rate in (Q(1),Q(1,2),Q(2,3)):
        T=[[scale(rate,mul(Si,mul(R,S))),zero],[zero,scale(rate,Z)]]
        data=fixture(T,S,Si,mul(transpose(S),S),Q(1),Q(1),rate**2); check(data); certificates+=1
        for f in range(1,5):
            E=endpoint(T,S,Si,f)
            require(mul(transpose(E),E)==scale(rate**(2*f),eye(len(E))),'literal noncommuting unitary lift')
            endpoints+=1
    # The source slow-phase example has a uniform bound of two.
    for N in (1,7,101):
        c=Q(N*N-1,N*N+1); s=Q(2*N,N*N+1)
        rotation=[[c,-s],[s,c]]
        local=[[Q(0) for _ in range(4)] for _ in range(4)]
        for i in range(2):
            for j in range(2): local[i][j]=rotation[i][j]; local[i+2][j+2]=Q(i==j)
        F=[[Q(1),Q(0),Q(-1),Q(0)],[Q(0),Q(1),Q(0),Q(-1)]]
        B=transpose([[Q(1),Q(0),Q(1),Q(0)],[Q(0),Q(1),Q(0),Q(1)]])
        check(fixture([[local]],F,B,eye(4),Q(2),Q(2),Q(1))); certificates+=1
        for f in range(1,10):
            E=endpoint([[local]],F,B,f); gap=sub(scale(Q(4),eye(2)),mul(transpose(E),E))
            require(principal_psd(gap),'slow-phase uniform bound')
            endpoints+=1
    for a,b,c in product(range(-2,3),repeat=3):
        m=[[Q(a),Q(b)],[Q(b),Q(c)]]
        require(psd(m)==principal_psd(m),'independent principal minors')
        psd_controls+=1
    good=fixture([[eye(2),zero],[zero,Z]],[[Q(1),Q(0)]],[[Q(1)],[Q(0)]],eye(2),Q(1),Q(1),Q(1))
    mutants=[]
    for key,value in [('squared_rate','1/4'),('metric',[[1,0],[0,0]]),
                      ('metric',[[1,0],[0,-1]]),('left',[[2,0]]),('right',[[2],[0]]),
                      ('squared_rate','2'),('left_bound',1.0),('transitions',[])]:
        bad=deepcopy(good); bad[key]=value; mutants.append(bad)
    for values in ([[1,1],[0,0]],[[1,0],[1,0]]):
        T=[[[[Q(values[y][x])]] for x in range(2)] for y in range(2)]
        mutants.append(fixture(T,[[Q(1)]],[[Q(1)]],[[Q(1)]],Q(1),Q(1),Q(1)))
    for bad in mutants:
        try: check(bad)
        except (ValueError,IndexError): pass
        else: raise ValueError('invalid certificate accepted')
    print('PASS_TRANSFER_METRIC_ERROR_BOUND '+json.dumps(dict(certificates=certificates,
        literal_endpoints=endpoints,independent_psd_cases=psd_controls,rejecting_controls=len(mutants)),sort_keys=True))


if __name__=='__main__': main()
