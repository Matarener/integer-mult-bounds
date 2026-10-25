# CORE-RES xa2.py: INDEPENDENT check of kcsp.py h = 1 (A7 simplices in f^perp), same independent machinery as xa.py.
# CORE-RES xa.py: INDEPENDENT cross-check of case (a) (s = 9, min y = 7).  No base.py / CORE3 / lossy.pkl / G.npy.
# Own E8 + P112 + Bd; label subspaces via the F2 COLUMN space of Bd (functionals), not the LAB table; no Aut reduction (all 43,435 Y).
# Checks: (X1) per Y: # lossy frame-root flats Z(f);  (X2) per (f_k, Y): # i with a lossy flat among Z(f_i, f_k), Z(f_i + f_k), Z(f_i - f_k);
#         (X3) K-part star filter for every h = 0..7 and used frame set N (A_{8-h} star of lossy root/frame lines orthogonal to N);
#         (X4) A8 case: per vertex candidate Y and pairwise arc consistency for every A8 subsystem.
import itertools, numpy as np, time
from collections import Counter
t0=time.time()
roots=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; roots.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: roots.append(s)
def canon(v):
    v=tuple(v); f=next(x for x in v if x); return v if f>0 else tuple(-x for x in v)
lines=sorted({canon(r) for r in roots})
FRS=[canon(tuple(2 if k==i else s*2 if k==i+1 else 0 for k in range(8))) for i in range(0,8,2) for s in (1,-1)]
L=[v for v in lines if v not in FRS]; n=len(L); assert n==112
dot=lambda a,b: sum(x*y for x,y in zip(a,b))
FULL=(1<<n)-1
rowm=[sum(1<<s for s in range(n) if s==t or dot(L[t],L[s])==0) for t in range(n)]
# column space of Bd over F2 (Bd symmetric: columns = rows); all nonzero vectors of it = functionals on the row space
basis=[]
for t in range(n):
    v=rowm[t]
    for b in basis: v=min(v,v^b)
    if v: basis.append(v)
assert len(basis)==9
FUN=[]
for bits in range(1,512):
    v=0
    for i in range(9):
        if bits>>i&1: v^=basis[i]
    FUN.append(v)
FUN=sorted(set(FUN)); assert len(FUN)==511
# 7-dim Y <-> 2-dim subspaces {v1, v2, v1^v2} of the functional space; L(Y) = lines t with v1_t = v2_t = 0
pairs=set()
for a in range(511):
    for b in range(a+1,511):
        pairs.add(tuple(sorted((FUN[a],FUN[b],FUN[a]^FUN[b]))))
pairs=sorted(pairs); NY=len(pairs); print('7-dim Y:',NY,flush=True); assert NY==43435
LYm=[FULL&~(p[0]|p[1]) for p in pairs]
def sp(m): return np.uint64(m&((1<<64)-1)),np.uint64(m>>64)
LY=np.array([sp(m) for m in LYm],dtype=np.uint64); FU=np.array([sp(v) for v in FUN],dtype=np.uint64)
def dimspan(S):   # dim span of Bd rows in S = 9 - log2(1 + #{functionals vanishing on S})
    c=sum(1 for v in FUN if v&S==0)+1; d=c.bit_length()-1; assert 1<<d==c; return 9-d
def dimspan_minusLY(S):
    lo,hi=sp(S); S0=lo&~LY[:,0]; S1=hi&~LY[:,1]; cnt=np.ones(NY,np.int64)
    for v in FU: cnt+=(((S0&v[0])|(S1&v[1]))==0)
    return 9-np.round(np.log2(cnt)).astype(int)
def lossy_for_flat(Z):
    T=FULL&~Z; return (dimspan(T)-dimspan_minusLY(T))>=1
def Zof(vs): return sum(1<<t for t in range(n) if all(dot(L[t],v)==0 for v in vs))
# codim-2 max lines (used for |Z| >= 40)
print('max |L(Y)| over 7-dim Y:',max(bin(m).count('1') for m in LYm),flush=True)
RL={v:lossy_for_flat(Zof([v])) for v in lines}
R=[r for r in roots]
def arc(pts):
    m=len(pts); cand=[]
    for k in range(m):
        ok=np.ones(NY,bool)
        for j in range(m):
            if j!=k: ok&=RL[canon([a-b for a,b in zip(pts[j],pts[k])])]
        cand.append(set(np.where(ok)[0].tolist()))
    nz=[[sum(1<<t for t in range(n) if dot(L[t],[a-b for a,b in zip(pts[k],pts[k2])])!=0) for k2 in range(m)] for k in range(m)]
    changed=True
    while changed and all(cand):
        changed=False
        for k in range(m):
            for k2 in range(m):
                if k==k2: continue
                keep={y for y in cand[k] if any((FULL&~LYm[y]&~LYm[y2]&nz[k][k2])==0 for y2 in cand[k2])}
                if keep!=cand[k]: cand[k]=keep; changed=True
    return all(cand)
# (X4) h = 0: A8 simplices (stars of 8 roots, pairwise dot +4); (X5) h = 1: A7 simplices spanning f^perp (stars of 7 roots in f^perp)
alive=0; tot=0
for f in [None]+FRS:
    A=[i for i in range(240) if f is None or dot(R[i],f)==0]; SZ=8 if f is None else 7
    adj={i:set(j for j in A if dot(R[i],R[j])==4) for i in A}
    seen=set(); simp=[]
    def rec(cl,cand):
        if len(cl)==SZ:
            pts=[(0,)*8]+[tuple(R[x]) for x in cl]
            key=frozenset(canon([a-b for a,b in zip(pts[i],pts[j])]) for i in range(SZ+1) for j in range(i))
            if key not in seen: seen.add(key); simp.append(pts)
            return
        for j in sorted(cand):
            if j>cl[-1]: rec(cl+[j],cand&adj[j])
    for i in A: rec([i],adj[i])
    al=0
    for pts in simp:
        tot+=1; a_=arc(pts); alive+=a_; al+=a_
    print('frame root',f,'(None = A8 case) simplices',len(simp),'surviving',al,'%.0fs'%(time.time()-t0),flush=True)
print('(X4+X5) h=0,1: simplices',tot,'surviving arc consistency:',alive)
