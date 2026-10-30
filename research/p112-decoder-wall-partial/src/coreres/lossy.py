# CORE-RES lossy.py: for every 7-dim label subspace Y (up to Aut), the LOSSY flats Z (loss(L \ Z, Y) >= 1) and the rank of the
# union of their direction spaces Z^perp.  Case (a) (s = 9, min y = 7) needs a vertex k with y_k = 7 such that >= 7 of the 8
# directions p_i - p_k (linearly independent) are lossy for Y_k = span lab(A_k).  EXACT (F2 + integer arithmetic).
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import numpy as np, pickle, time
from fractions import Fraction as Fr
from collections import Counter, defaultdict
t0=time.time(); HERE=os.path.dirname(os.path.abspath(__file__)); C3=os.path.join(HERE,'..','core3')
ST=pickle.load(open(C3+'/stats.pkl','rb'))
G=np.load(os.path.join(HERE,'..','core3','G.npy')).astype(np.int64); NG=len(G)
for g in G[::5000]: assert (Bd[np.ix_(g,g)]==Bd).all()
FULL=(1<<n)-1
ODD=[sum(1<<t for t in range(n) if bin(h&LAB[t]).count('1')&1) for h in range(512)]
ZER=[FULL&~ODD[h] for h in range(512)]
def split(m): return np.uint64(m&((1<<64)-1)),np.uint64(m>>64)
OD=np.array([split(m) for m in ODD],dtype=np.uint64)
ann=set()
for h1 in range(1,512):
    for h2 in range(h1+1,512): ann.add(tuple(sorted((h1,h2,h1^h2))))
ann=sorted(ann); NY=len(ann); print('7-dim Y:',NY,flush=True)
akey=np.array([a*262144+b*512+c for a,b,c in ann],dtype=np.int64); assert (np.diff(akey)>0).all()
LY=np.array([split(ZER[a]&ZER[b]) for a,b,_ in ann],dtype=np.uint64)
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
# label action of Aut: lab(g t) = M_g lab(t); columns M_g e_i = lab(g(BIDX[i]))  (lab(BIDX[i]) = e_i)
assert all(LAB[BIDX[i]]==1<<i for i in range(9))
LABa=np.array(LAB,dtype=np.int64)
cols=LABa[G[:,BIDX]]                       # NG x 9
def apply_M(cols,x):                       # M x for 9-bit x (vector over g)
    out=np.zeros(len(cols),np.int64)
    for i in range(9):
        if x>>i&1: out^=cols[:,i]
    return out
# check linearity on all lines for a sample of g
for gi in range(0,NG,7919):
    for t in range(n): assert apply_M(cols[gi:gi+1],LAB[t])[0]==LAB[G[gi][t]]
# M_g^T h: (M^T h)_i = parity(col_i & h)
def MT(h):
    out=np.zeros(NG,np.int64)
    for i in range(9):
        c=cols[:,i]&h; p=np.zeros(NG,np.int64)
        x=c.copy()
        while x.any(): p^=x&1; x>>=1
        out|=p<<i
    return out
MTtab={}
def mt(h):
    if h not in MTtab: MTtab[h]=MT(h).astype(np.int16)
    return MTtab[h]
# Y orbits: Y index -> orbit via union-find under the generators (use all of G's action on a rep instead: orbit of rep = {g^-1 Y})
def yimg_all(yi):
    """indices of g^-1 Y for all g (ann(g^-1 Y) = M_g^T ann(Y))"""
    a,b,c=ann[yi]; A=mt(a); B=mt(b); Cc=mt(c)
    s=np.sort(np.stack([A,B,Cc],1).astype(np.int64),1); key=s[:,0]*262144+s[:,1]*512+s[:,2]
    idx=np.searchsorted(akey,key); assert (akey[idx]==key).all(); return idx
orbit_of=-np.ones(NY,np.int64); reps=[]
for yi in range(NY):
    if orbit_of[yi]>=0: continue
    imgs=yimg_all(yi); orbit_of[np.unique(imgs)]=len(reps); reps.append(yi)
print('Y orbits under Aut:',len(reps),'%.0fs'%(time.time()-t0),flush=True)
# special flat orbits: lossy Y-sets
special=[o for o in ST if o['kappa']<=7 or o['cocirc']<=2]
GINV=np.argsort(G,axis=1)
def img_mask(mask,gi):
    return sum(1<<int(G[gi][t]) for t in range(n) if mask>>t&1)
lossyflats=defaultdict(set)   # Y rep -> set of flat masks lossy for it
for o in special:
    T=FULL&~o['mask']; D=rank_lines(T); loss=D-spandim_many(T); S0=np.where(loss>=1)[0]
    assert loss.max()<=1
    inS0=np.zeros(NY,bool); inS0[S0]=True
    for r in reps:
        imgs=yimg_all(r)               # g^-1 Y_r for each g
        sel=np.where(inS0[imgs])[0]   # g with Z0 lossy for g^-1 Y  <=>  g Z0 lossy for Y
        if len(sel)==0: continue
        v=np.array([(o['mask']>>t)&1 for t in range(n)],dtype=bool)
        imgv=v[GINV[sel]]                                  # rows: g(Z0) as boolean vectors
        for row in np.unique(np.packbits(imgv,axis=1,bitorder='little'),axis=0):
            Zm=int.from_bytes(row.tobytes(),'little'); lossyflats[r].add((Zm,o['rank'],o['nZ']))
    print('special flat orbit rank %d |Z| %d: %d lossy Y; done %.0fs'%(o['rank'],o['nZ'],len(S0),time.time()-t0),flush=True)
# direction spaces Z^perp (exact integer nullspace) and rank of their union
Ci=[[Fr(int(v)) for v in C[t]] for t in range(n)]
def rref(rows):
    M=[r[:] for r in rows]; piv=[]; R=0
    for c in range(8):
        p=next((i for i in range(R,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[R],M[p]=M[p],M[R]; f=M[R][c]; M[R]=[x/f for x in M[R]]
        for i in range(len(M)):
            if i!=R and M[i][c]!=0: g=M[i][c]; M[i]=[x-g*y for x,y in zip(M[i],M[R])]
        piv.append(c); R+=1
    return M[:R],piv
def perp(lines):
    M,piv=rref([Ci[t] for t in lines]); free=[c for c in range(8) if c not in piv]; out=[]
    for f in free:
        v=[Fr(0)]*8; v[f]=Fr(1)
        for i,c in enumerate(piv): v[c]=-M[i][f]
        out.append(v)
    return out
pcache={}
res=[]
for r in reps:
    dirs=[]; typ=Counter()
    for Zm,rk,nz in lossyflats[r]:
        if Zm not in pcache: pcache[Zm]=perp([t for t in range(n) if Zm>>t&1])
        dirs+=pcache[Zm]; typ[(rk,nz)]+=1
    rk=len(rref(dirs)[0]) if dirs else 0
    res.append((r,rk,dict(typ),int((orbit_of==orbit_of[r]).sum())))
pickle.dump(dict(reps=reps,res=res,lossy={r:sorted(lossyflats[r]) for r in reps}),open(HERE+'/lossy.pkl','wb'))
print('direction-rank distribution over Y orbits:',sorted(Counter(x[1] for x in res).items()))
for r,rk,typ,osz in res:
    if rk>=7: print('  Y rep',r,'orbit size',osz,'dir rank',rk,'lossy flat types (rank,|Z|):#',typ)
print('done %.0fs'%(time.time()-t0))
