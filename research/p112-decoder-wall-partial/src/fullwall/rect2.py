# MAXIMAL rectangles (R,A) of P112 (all costs 1..9) up to Aut x transpose.  Scope: monotone rows only (support enlargement WLOG).
# X = span R: label-closed orbit rep (xorb.pkl), dim x.  A = labels whose functional on X lies in Z, Z a c-dim subspace of X* spanned
# by label images (c = cost exactly).  WLOG x <= (9+c)/2 (transpose).  Keep only closed (maximal) pairs; canonicalise by pynauty.
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from base import *
from subsp import rref
import time, pynauty
reps=pickle.load(open(HERE+'/xorb.pkl','rb'))
FL=[sum(1<<i for i,F in enumerate(FRM) if F>>t&1) for t in range(n)]
def hitmask(Rm,Am):
    a=0;b=0
    for t in range(n):
        if Rm>>t&1: a|=FL[t]
        if Am>>t&1: b|=FL[t]
    return a&b
def spanred(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return b
def inspan(b,v):
    for x in b: v=min(v,v^x)
    return v==0
def closure(Rm,Am):
    while True:
        br=spanred([ROW[r]&Am for r in range(n) if Rm>>r&1])
        R2=sum(1<<t for t in range(n) if inspan(br,ROW[t]&Am))
        bc=spanred([ROW[a]&R2 for a in range(n) if Am>>a&1])
        A2=sum(1<<t for t in range(n) if inspan(bc,ROW[t]&R2))
        if R2==Rm and A2==Am: return Rm,Am
        Rm,Am=R2,A2
ADJ={i:[j for j in range(n) if j!=i and Bd[i,j]] for i in range(n)}
def colours(Rm,Am):
    cl=[set(),set(),set(),set()]
    for t in range(n): cl[(Rm>>t&1)*2+(Am>>t&1)].add(t)
    return [c for c in cl]   # order fixed: rest, A only, R only, both  (empty classes kept)
def cert(Rm,Am):
    g=pynauty.Graph(n,adjacency_dict=ADJ,vertex_coloring=[c for c in colours(Rm,Am)])
    return pynauty.certificate(g)
def stab(Rm,Am):
    g=pynauty.Graph(n,adjacency_dict=ADJ,vertex_coloring=[c for c in colours(Rm,Am)])
    _,a,b,_,_=pynauty.autgrp(g); return round(a*10**b)
def subspaces(vecs,x,c):
    """all c-dim subspaces of F2^x spanned by vectors from vecs (returns set of rref tuples)"""
    if c<=x-c:
        level={()}
        for d in range(c):
            level={Z2 for Z in level for v in vecs for Z2 in [rref(list(Z)+[v])] if len(Z2)==d+1}
        return level
    # complement: Z = annihilator (std dot) of a (x-c)-dim subspace W of F2^x; keep if spanned by vecs inside
    out=set(); level={()}
    for d in range(x-c):
        level={W2 for W in level for w in range(1,1<<x) for W2 in [rref(list(W)+[w])] if len(W2)==d+1}
    for W in level:
        inside=[v for v in vecs if all(bin(v&w).count('1')%2==0 for w in W)]
        Z=rref(inside)
        if len(Z)==c: out.add(Z)
    return out
if __name__=='__main__':
    AUT=172032; t0=time.time(); seen={}; raw=0
    for x in range(1,10):
        for B,Rm0 in reps[x]:
            B=list(B)
            img=[sum(form(b,LAB[a])<<i for i,b in enumerate(B)) for a in range(n)]
            vecs=sorted(set(v for v in img if v))
            for c in range(max(1,2*x-9),x+1):
                for Z in subspaces(vecs,x,c):
                    mem={0}
                    for z in Z: mem|={m^z for m in mem}
                    Am=sum(1<<a for a in range(n) if img[a] in mem)
                    cst=cost(Rm0,Am); assert cst==c,(x,c,cst)
                    raw+=1
                    Rm,Am2=closure(Rm0,Am)
                    if (Rm,Am2)!=(Rm0,Am): continue      # not maximal: its closure is enumerated elsewhere
                    k=min(cert(Rm,Am2),cert(Am2,Rm))
                    if k in seen: continue
                    seen[k]=(c,Rm,Am2)
        print('x',x,'raw',raw,'maximal orbits',len(seen),round(time.time()-t0,1),flush=True)
    out=[]
    for k,(c,Rm,Am) in seen.items():
        H=hitmask(Rm,Am)
        out.append(dict(c=c,R=Rm,A=Am,H=H,fr=bin(H).count('1'),cov=bin(Rm&Am).count('1'),nR=bin(Rm).count('1'),nA=bin(Am).count('1'),
                        orb=AUT//stab(Rm,Am),selft=(cert(Rm,Am)==cert(Am,Rm))))
    pickle.dump(out,open(HERE+'/rect2.pkl','wb'))
    from collections import Counter
    print('orbits by cost',sorted(Counter(o['c'] for o in out).items()))
    for c in range(1,10):
        L=[o for o in out if o['c']==c]
        if L: m=max(L,key=lambda o:o['fr']); print('cost',c,'orbits',len(L),'max fr',m['fr'],'eff',round(m['fr']/c,1),'nR nA cov',m['nR'],m['nA'],m['cov'])
