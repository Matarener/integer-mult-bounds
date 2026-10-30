# CORE-RES a8star.py: case (a2) with h = 0 (all nine terms have y = 7): the simplex is an A8 root simplex (star.py: only h = 0 survives).
# For each of the 960 A8 subsystems: per vertex k, the candidate Y_k = 7-dim Y for which all 8 directions p_j - p_k are lossy; then the
# CSP: choose Y_k (k = 0..8) such that for every line s, c_s . p_k is constant on {k : s not in L(Y_k)} (those lines must be in E_k,
# i.e. b_s = c_s . p_k, and b_s is one number).  Pairwise form: s outside L(Y_k) u L(Y_k') => c_s orth p_k - p_k'.  EXACT.
# Also: summary of lossy counts per Y orbit (for case (a1)).
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import numpy as np, pickle, itertools, time
from collections import Counter
t0=time.time(); HERE=os.path.dirname(os.path.abspath(__file__))
LO=pickle.load(open(HERE+'/lossy.pkl','rb'))
# ---- (a1) summary: per Y orbit, # lossy 56-flats and # lossy non-root (kappa-7) flats
mx56=0; mxo=0
for r in LO['reps']:
    c=Counter(nz for _,_,nz in LO['lossy'][r])
    mx56=max(mx56,c[56]); mxo=max(mxo,sum(v for k,v in c.items() if k not in (56,59)))
print('(a1) max over Y of #lossy 56-flats:',mx56,'  max #lossy non-root flats:',mxo,flush=True)
FULL=(1<<n)-1
ODD=[sum(1<<t for t in range(n) if bin(h&LAB[t]).count('1')&1) for h in range(512)]
ZER=[FULL&~ODD[h] for h in range(512)]
def split(m): return np.uint64(m&((1<<64)-1)),np.uint64(m>>64)
OD=np.array([split(m) for m in ODD],dtype=np.uint64)
ann=set()
for h1 in range(1,512):
    for h2 in range(h1+1,512): ann.add(tuple(sorted((h1,h2,h1^h2))))
ann=sorted(ann); NY=len(ann)
LYm=[ZER[a]&ZER[b] for a,b,_ in ann]
LY=np.array([split(m) for m in LYm],dtype=np.uint64)
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
def line_key(v):
    f=next(x for x in v if x); return tuple(v) if f>0 else tuple(-x for x in v)
# lossy arrays for the 120 root-line flats Z(r)
lossyY={}
for i in range(120):
    v=list(R120[i]); key=line_key(v)
    if key in lossyY: continue
    Z=sum(1<<t for t in range(n) if dot(Ci[t],v)==0); T=FULL&~Z
    lossyY[key]=(rank_lines(T)-spandim_many(T))>=1
print('lossy arrays for',len(lossyY),'root lines %.0fs'%(time.time()-t0),flush=True)
# A8 subsystems (as a8.py)
nbr={i:[j for j in range(120) if DOT[i,j]==-4] for i in range(120)}
chains=[]
def rec(ch):
    if len(ch)==8: chains.append(list(ch)); return
    for j in nbr[ch[-1]]:
        if j not in ch and all(DOT[j,x]==0 for x in ch[:-1]): rec(ch+[j])
for i in range(120): rec([i])
subs={}
for c in chains:
    pts=[[0]*8]
    for r in c: pts.append([a+b for a,b in zip(pts[-1],R120[r])])
    L36=frozenset(line_key([a-b for a,b in zip(pts[i],pts[j])]) for i in range(9) for j in range(i))
    if L36 not in subs: subs[L36]=pts
print('A8 subsystems',len(subs),flush=True)
surv=0; stats=Counter()
for si,(L36,pts) in enumerate(subs.items()):
    cand=[]
    for k in range(9):
        ok=np.ones(NY,bool)
        for j in range(9):
            if j!=k: ok&=lossyY[line_key([a-b for a,b in zip(pts[j],pts[k])])]
        cand.append(list(np.where(ok)[0]))
    stats[tuple(sorted(len(c) for c in cand))[:1]]+=1
    if any(len(c)==0 for c in cand): continue
    # pairwise CSP with arc consistency then backtracking
    bad=[[0]*9 for _ in range(9)]   # bad[k][k'] = mask of lines NOT orthogonal to p_k - p_k'
    for k in range(9):
        for k2 in range(9):
            if k!=k2: bad[k][k2]=sum(1<<t for t in range(n) if dot(Ci[t],[a-b for a,b in zip(pts[k],pts[k2])])!=0)
    def compat(k,y,k2,y2): return (FULL&~LYm[y]&~LYm[y2]&bad[k][k2])==0
    dom=[set(c) for c in cand]; changed=True
    while changed:
        changed=False
        for k in range(9):
            for k2 in range(9):
                if k==k2: continue
                keep={y for y in dom[k] if any(compat(k,y,k2,y2) for y2 in dom[k2])}
                if keep!=dom[k]: dom[k]=keep; changed=True
    sol=None
    if all(dom):
        order=sorted(range(9),key=lambda k:len(dom[k]))
        def bt(i,asg):
            global sol
            if sol: return
            if i==9: sol=dict(asg); return
            k=order[i]
            for y in dom[k]:
                if all(compat(k,y,k2,asg[k2]) for k2 in asg): asg[k]=y; bt(i+1,asg); del asg[k]
        bt(0,{})
    print('A8 sub',si,'candidate |Y_k|',[len(c) for c in cand],'after arc consistency',[len(d) for d in dom],'CSP solution:',sol is not None,flush=True)
    if sol: surv+=1
print('min-candidate distribution over subsystems:',sorted(stats.items()))
print('A8 subsystems with a consistent (Y_k) assignment:',surv,'%.0fs'%(time.time()-t0))
