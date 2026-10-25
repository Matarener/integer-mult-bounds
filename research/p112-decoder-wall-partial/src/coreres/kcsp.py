# CORE-RES kcsp.py: case (a2) for h = |N7| in {0, 1}: the K7 vertices form an A_{8-h} root simplex spanning U = (used frame roots)^perp.
# CSP over the K7 vertices only: domain(k) = 7-dim Y lossy for every K7-direction p_k' - p_k; pairwise constraint
#   lines outside L(Y_k) u L(Y_k') must be orthogonal to p_k - p_k'  (they lie in E_k & E_k').  Arc consistency + backtracking.  EXACT.
# (For h = 1 this ignores the N7 vertex entirely: a necessary condition only.)
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import numpy as np, itertools, time
from collections import Counter
t0=time.time()
FULL=(1<<n)-1
ODD=[sum(1<<t for t in range(n) if bin(h&LAB[t]).count('1')&1) for h in range(512)]
ZER=[FULL&~ODD[h] for h in range(512)]
def split(m): return np.uint64(m&((1<<64)-1)),np.uint64(m>>64)
OD=np.array([split(m) for m in ODD],dtype=np.uint64)
ann=sorted({tuple(sorted((h1,h2,h1^h2))) for h1 in range(1,512) for h2 in range(h1+1,512)}); NY=len(ann)
LYm=[ZER[a]&ZER[b] for a,b,_ in ann]; LY=np.array([split(m) for m in LYm],dtype=np.uint64)
def spandim_many(Tm):
    lo,hi=split(Tm); S0=lo&~LY[:,0]; S1=hi&~LY[:,1]; cnt=np.zeros(NY,np.int64)
    for h in range(512): cnt+=(((S0&OD[h,0])|(S1&OD[h,1]))==0)
    return 9-np.round(np.log2(cnt)).astype(int)
def rank_lines(m):
    b=[]
    for t in range(n):
        if m>>t&1:
            v=LAB[t]
            for y in b: v=min(v,v^y)
            if v: b.append(v)
    return len(b)
Ci=[[int(v) for v in C[t]] for t in range(n)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def key(v):
    f=next(x for x in v if x); return tuple(v) if f>0 else tuple(-x for x in v)
lossyY={}
for i in range(120):
    k=key(list(R120[i]))
    if k in lossyY: continue
    Z=sum(1<<t for t in range(n) if dot(Ci[t],k)==0); T=FULL&~Z
    lossyY[k]=(rank_lines(T)-spandim_many(T))>=1
FRV=[list(R120[i]) for i in FR]
R240=[list(r) for r in R120]+[[-x for x in r] for r in R120]
D240=np.array(R240)@np.array(R240).T
def simplices(allowed):
    """A_L root simplices {0} u {v_1..v_L}: cliques of L roots with pairwise dot +4 (2x coords; real +1), all in 'allowed'."""
    adj={i:set(j for j in allowed if D240[i,j]==4) for i in allowed}
    out={}
    def rec(cl,cand,L):
        if len(cl)==L:
            pts=[[0]*8]+[R240[r] for r in cl]
            ks=frozenset(key([a-b for a,b in zip(pts[i],pts[j])]) for i in range(len(pts)) for j in range(i))
            if ks not in out: out[ks]=pts
            return
        for j in sorted(cand):
            if j>cl[-1]: rec(cl+[j],cand&adj[j],L)
    return rec,out,adj
def csp(pts):
    m=len(pts)
    dom=[]
    for k in range(m):
        ok=np.ones(NY,bool)
        for j in range(m):
            if j!=k: ok&=lossyY[key([a-b for a,b in zip(pts[j],pts[k])])]
        dom.append(set(np.where(ok)[0].tolist()))
    d0=[len(d) for d in dom]
    nz=[[sum(1<<t for t in range(n) if dot(Ci[t],[a-b for a,b in zip(pts[k],pts[k2])])!=0) if k!=k2 else 0 for k2 in range(m)] for k in range(m)]
    def comp(k,y,k2,y2): return (FULL&~LYm[y]&~LYm[y2]&nz[k][k2])==0
    changed=True
    while changed and all(dom):
        changed=False
        for k in range(m):
            for k2 in range(m):
                if k==k2: continue
                keep={y for y in dom[k] if any(comp(k,y,k2,y2) for y2 in dom[k2])}
                if keep!=dom[k]: dom[k]=keep; changed=True
    if not all(dom): return d0,[len(d) for d in dom],False
    order=sorted(range(m),key=lambda k:len(dom[k])); sol=[None]
    def bt(i,asg):
        if sol[0]: return
        if i==m: sol[0]=dict(asg); return
        k=order[i]
        for y in dom[k]:
            if all(comp(k,y,k2,asg[k2]) for k2 in asg): asg[k]=y; bt(i+1,asg); del asg[k]
    bt(0,{})
    return d0,[len(d) for d in dom],sol[0] is not None
for h in (0,1):
    tot=0; alive=0
    Ns=[()] if h==0 else [(i,) for i in range(8)]
    for N in Ns:
        allowed=[i for i in range(240) if all(dot(R240[i],FRV[j])==0 for j in N)]
        rec,out,adj=simplices(allowed)
        for i in allowed: rec([i],adj[i],8-h)
        for ks,pts in out.items():
            d0,d1,ok=csp(pts); tot+=1; alive+=ok
            if ok: print('  SURVIVOR h',h,'N',N,'domains',d0,'->',d1,flush=True)
        print('h',h,'N',N,'A_%d simplices'%(8-h),len(out),'%.0fs'%(time.time()-t0),flush=True)
    print('h',h,': simplices',tot,'with a consistent K7 assignment:',alive,flush=True)
