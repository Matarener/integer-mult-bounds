# INDEPENDENT cross-check of the m=8 lemma (no rectangle canonicalisation, no maximality filter, separate closure/rank/frame code).
# For every X orbit rep (xorb.pkl; completeness checked by cntsub.c orbit-size sums) and EVERY c-dim subspace Z of X* (RREF enumeration,
# label-generated or not), c <= 7, c >= 2x-9: R = labels in X, A = labels whose functional on X lies in Z.  Test rules R1/R2 (numpy).
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pickle, itertools, time
from base import LAB, Bd as Bd0, C   # labels only used to define R,A; Bd recomputed below
n=112
G=C@C.T; Bd=((G==0)|np.eye(n,dtype=bool)).astype(np.uint8)
assert (Bd==Bd0).all()
# frames: independent recursion on numpy adjacency
adj=[set(np.nonzero(Bd[i])[0])-{i} for i in range(n)]
frames=[]
def grow(cl,cand):
    if len(cl)==8: frames.append(tuple(cl)); return
    for v in sorted(cand):
        if v>cl[-1]: grow(cl+[v],cand&adj[v])
for v in range(n): grow([v],adj[v])
assert len(frames)==1260
Fm=np.zeros((1260,n),dtype=bool)
for i,F in enumerate(frames): Fm[i,list(F)]=True
# rules: for t, for frame F not containing t: W = F minus lines orthogonal to t (4 lines)
rules=[[] for _ in range(n)]
for i,F in enumerate(frames):
    for t in range(n):
        if t in F: continue
        W=[f for f in F if Bd[t,f]==0]; assert len(W)==4
        rules[t].append(W)
for t in range(n): rules[t]=np.array(sorted(set(map(tuple,rules[t]))))
def closure(Z):   # Z: bool array
    Z=Z.copy()
    while True:
        new=False
        for t in np.nonzero(~Z)[0]:
            if Z[rules[t]].all(axis=1).any(): Z[t]=True; new=True
        if not new: return Z
def f2rank(M):
    M=M.copy()%2; r=0
    for c in range(M.shape[1]):
        p=np.nonzero(M[r:,c])[0]
        if len(p)==0: continue
        p=r+p[0]; M[[r,p]]=M[[p,r]]
        idx=np.nonzero(M[:,c])[0]; idx=idx[idx!=r]; M[idx]^=M[r]; r+=1
        if r==M.shape[0]: break
    return r
def form(x,y):   # Bd[t,s] = form(lab_t, lab_s): recover from Bd via labels (bilinear over F2^9); compute through PHI solve
    raise NotImplementedError
# PHI: solve Bd[t,s] = lab_t^T PHI lab_s over F2 (81 unknowns) by elimination, independently of base.PHI
bits=lambda v:[(v>>i)&1 for i in range(9)]
rowsA=[];rhs=[]
for t in range(0,n,3):
    for s in range(n):
        x,y=bits(LAB[t]),bits(LAB[s]); rowsA.append([x[i]&y[j] for i in range(9) for j in range(9)]); rhs.append(int(Bd[t,s]))
A=np.array(rowsA,dtype=np.uint8); b=np.array(rhs,dtype=np.uint8)
Mx=np.concatenate([A,b[:,None]],1); r=0; piv=[]
for c in range(81):
    p=np.nonzero(Mx[r:,c])[0]
    if len(p)==0: continue
    p=r+p[0]; Mx[[r,p]]=Mx[[p,r]]; idx=np.nonzero(Mx[:,c])[0]; idx=idx[idx!=r]; Mx[idx]^=Mx[r]; piv.append(c); r+=1
PHI=np.zeros(81,dtype=np.uint8)
for i,c in enumerate(piv): PHI[c]=Mx[i,81]
PHI=PHI.reshape(9,9)
LB=np.array([bits(v) for v in LAB],dtype=np.uint8)
assert ((LB@PHI@LB.T)%2==Bd).all()
def subspaces(x,c):
    for piv in itertools.combinations(range(x),c):
        free=[[j for j in range(piv[i]) if j not in piv] for i in range(c)]
        tot=sum(len(f) for f in free)
        for s in range(1<<tot):
            rows=[];k=0
            for i in range(c):
                v=1<<piv[i]
                for j in free[i]:
                    if s>>k&1: v|=1<<j
                    k+=1
                rows.append(v)
            mem={0}
            for v in rows: mem|={m^v for m in mem}
            yield mem
reps=pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'xorb.pkl'),'rb'))
t0=time.time(); tested=0; surv=0
for x in range(1,10):
    for Bas,_ in reps[x]:
        Xb=np.array([bits(v) for v in Bas],dtype=np.uint8)            # x x 9
        # members of X and R = labels in X
        memX={0}
        for v in Bas: memX|={m^v for m in memX}
        Rm=np.array([LAB[t] in memX for t in range(n)])
        img=(LB@PHI.T@Xb.T)%2      # img[a,i] = form(b_i, lab_a) = b_i^T PHI lab_a
        imgv=[int(sum(int(img[a,i])<<i for i in range(x))) for a in range(n)]
        for c in range(max(1,2*x-9),min(x,7)+1):
            for mem in subspaces(x,c):
                Am=np.array([imgv[a] in mem for a in range(n)])
                if not Am.any(): continue
                cst=f2rank(Bd[np.ix_(np.nonzero(Rm)[0],np.nonzero(Am)[0])])
                if cst>7: continue
                tested+=1
                Z=closure(~Rm); Zp=closure(~Am)
                D=~(Z|Zp)
                if (Fm&D).any(axis=1).all(): surv+=1; print('SURVIVOR',x,c,cst,flush=True)
    print('x',x,'tested',tested,'survivors',surv,round(time.time()-t0,1),flush=True)
print('XCHECK_M8', 'PASS' if surv==0 else 'FAIL', tested)
