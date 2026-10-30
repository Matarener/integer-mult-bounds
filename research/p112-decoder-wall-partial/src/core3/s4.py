# CORE3 s4.py: finite facts for |supp beta| >= 4 (NOTES sec. 4-5).  EXACT.
# Part A (hurt configurations, any s): J = set of h distinct frame roots f_m, and P112 root lines r_m with f_m.r_m != 0,
#   f_i.r_m = 0 (i != m in J).  Test: rank_F2 Bd[H^c(a) u D, D] = h for EVERY a with a.r_m != 0 (all m), D = {r_m}.
#   Per nonzero w in F2^D: S_w = {t : sum_{m in w} Bd[t, r_m] = 1}; OK iff S_w meets D, or some r_m lies in span_Q(S_w)
#   (then a ⊥ S_w forces a.r_m = 0).
# Part B (loss with dim Y = 7): for the flat orbits whose H^c has a cocircuit spanning <= 7 label dims (or a coloop),
#   max over ALL 7-dim subspaces Y of F2^9 of loss(T,Y) = dim span lab(T) - dim span lab(T \ L(Y)).
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import pickle, itertools, numpy as np, time
from fractions import Fraction as Fr
from collections import Counter
HERE3=os.path.dirname(os.path.abspath(__file__)); t0=time.time()
Ci=[[int(v) for v in C[t]] for t in range(n)]
def dot(u,v): return sum(a*b for a,b in zip(u,v))
def qrank(rows):
    M=[[Fr(v) for v in r] for r in rows]; R=0
    for c in range(8):
        p=next((i for i in range(R,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[R],M[p]=M[p],M[R]
        for i in range(len(M)):
            if i!=R and M[i][c]!=0: f=M[i][c]/M[R][c]; M[i]=[x-f*y for x,y in zip(M[i],M[R])]
        R+=1
    return R
frames8=[];seen=set()
for i in FR:
    v=list(R120[i]); key=tuple(v) if next(x for x in v if x)>0 else tuple(-x for x in v)
    if key not in seen: seen.add(key); frames8.append(list(key))
NF=[frozenset(i for i,f in enumerate(frames8) if dot(f,Ci[t])!=0) for t in range(n)]
assert all(len(x)==4 for x in NF)
# ---------------- Part A
fails=Counter(); tot=Counter(); spancache={}
def ok_config(D):
    for wbits in range(1,1<<len(D)):
        w=[D[i] for i in range(len(D)) if wbits>>i&1]
        S=[t for t in range(n) if sum(int(Bd[t,r]) for r in w)%2==1]
        if any(t in D for t in S): continue
        key=frozenset(S)
        if key not in spancache:
            rS=qrank([Ci[t] for t in S]) if S else 0
            spancache[key]=(rS,[r for r in range(n) if (qrank([Ci[t] for t in S]+[Ci[r]]) if S else 1)==rS])
        rS,inspan=spancache[key]
        if rS==8: continue
        if any(r in inspan for r in D): continue
        return False,w
    return True,None
for h in range(2,6):
    for J in itertools.combinations(range(8),h):
        cand=[[t for t in range(n) if NF[t]&set(J)=={m}] for m in J]
        for D in itertools.product(*cand):
            if len(set(D))<h: continue
            ok,w=ok_config(list(D)); tot[h]+=1
            if not ok: fails[h]+=1
    print('Part A h=%d: configs %d, failures %d  (%.0fs)'%(h,tot[h],fails[h],time.time()-t0),flush=True)
print('Part A: h<=5 is the max possible (each root line meets exactly 4 frame roots, so N(r_m) needs 3 frame roots outside J)')
# ---------------- Part B
FL=pickle.load(open(HERE3+'/flats.pkl','rb')); ST=pickle.load(open(HERE3+'/stats.pkl','rb'))
FULL=(1<<n)-1
ODD=[sum(1<<t for t in range(n) if bin(h&LAB[t]).count('1')&1) for h in range(512)]
ZER=[FULL&~ODD[h] for h in range(512)]
def split(m): return np.uint64(m&((1<<64)-1)),np.uint64(m>>64)
OD=np.array([split(m) for m in ODD],dtype=np.uint64)
# all 7-dim subspaces Y = ker h1 & ker h2 (2-dim annihilator {h1,h2,h1^h2}); L(Y) = ZER[h1] & ZER[h2]
ann=set()
for h1 in range(1,512):
    for h2 in range(h1+1,512):
        ann.add(tuple(sorted((h1,h2,h1^h2))))
ann=sorted(ann); print('7-dim subspaces:',len(ann))
LY=np.array([split(ZER[a]&ZER[b]) for a,b,_ in ann],dtype=np.uint64)
def spandim_many(Tm):
    """for each Y: dim span lab(T \\ L(Y)) = 9 - log2 #{h : ODD[h] & (T\\L(Y)) = 0}"""
    lo,hi=split(Tm)
    S0=lo&~LY[:,0]; S1=hi&~LY[:,1]
    cnt=np.zeros(len(LY),np.int64)
    for h in range(512):
        cnt+=(((S0&OD[h,0])|(S1&OD[h,1]))==0)
    return 9-np.round(np.log2(cnt)).astype(int)
def rank_lines(m):
    b=[]
    for t in range(n):
        if m>>t&1:
            v=LAB[t]
            for y in b: v=min(v,v^y)
            if v: b.append(v)
    return len(b)
for o in ST:
    T=FULL&~o['mask']
    if o['kappa']<=7 or o['cocirc']<=2:
        D=rank_lines(T); sd=spandim_many(T); loss=D-sd
        c=Counter(loss.tolist())
        print('flat rank %d |Z| %d D %d kappa %d: loss distribution over 7-dim Y:'%(o['rank'],o['nZ'],D,o['kappa']),sorted(c.items()),flush=True)
print('done %.0fs'%(time.time()-t0))
