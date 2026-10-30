# FULLWALL base: P112 (geom.py / #5088 order), Bd, frames, F2^9 labels + form, Aut gens.  python = W/venv/bin/python -I
import itertools, numpy as np, os, pickle
HERE=os.path.dirname(os.path.abspath(__file__))
def roots_e8():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for s in (-1,1):
            r=[0]*8; r[i]=2; r[j]=2*s; R.append(tuple(r))
    for tail in itertools.product((-1,1),repeat=7):
        if tail.count(-1)%2==0: R.append((1,)+tail)
    R.sort(); return R
R120=roots_e8(); DOT=np.array(R120)@np.array(R120).T
FR=[R120.index(tuple(2 if k==i else s*2 if k==i+1 else 0 for k in range(8))) for i in range(0,8,2) for s in (-1,1)]
LIVE=[i for i in range(120) if i not in FR]
n=112
C=np.array([R120[i] for i in LIVE])           # 2x-scaled coordinates
G=C@C.T
Bd=((G==0)|np.eye(n,dtype=bool)).astype(np.int64)
ROW=[sum(int(Bd[t,s])<<s for s in range(n)) for t in range(n)]   # row bitmasks
def f2rank_masks(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
def cost(Rm,Am):
    """rank_F2 Bd[R,A] for bitmasks R,A"""
    return f2rank_masks([ROW[t]&Am for t in range(n) if Rm>>t&1])
# frames: orthogonal 8-cliques
def frames():
    nb=[ROW[t]&~(1<<t) for t in range(n)]
    out=[]
    def rec(cl,cand,last):
        if len(cl)==8: out.append(sum(1<<x for x in cl)); return
        c=cand
        while c:
            x=(c&-c).bit_length()-1; c&=c-1
            if x>last: rec(cl+[x],cand&nb[x],x)
    rec([],(1<<n)-1,-1); return out
FRM=frames()
# F2^9 labels: coordinates of each row in a basis of the row space
def labels():
    basis=[];idx=[]
    for t in range(n):
        v=ROW[t]
        for x in basis: v=min(v,v^x)
        if v: basis.append(v); idx.append(t)
    assert len(idx)==9
    # solve: row_t = sum c_i row_{idx_i}; brute force via linear algebra over F2 on 9 vars
    M=np.array([[ROW[i]>>s&1 for s in range(n)] for i in idx],dtype=np.uint8)  # 9 x n
    # find 9 columns making M invertible
    cols=[];
    for s in range(n):
        if f2rank_masks([sum(int(M[i,c])<<j for j,c in enumerate(cols+[s])) for i in range(9)])>len(cols): cols.append(s)
        if len(cols)==9: break
    Ms=M[:,cols]
    # inverse of Ms over F2
    A=np.concatenate([Ms.T.copy(),np.eye(9,dtype=np.uint8)],1)%2  # solve c^T Ms = row_t[cols]
    r=0
    for c in range(9):
        p=next(i for i in range(r,9) if A[i,c]); A[[r,p]]=A[[p,r]]
        for i in range(9):
            if i!=r and A[i,c]: A[i]^=A[r]
        r+=1
    inv=A[:,9:]  # inv @ Ms.T = I
    lab=[]
    for t in range(n):
        y=np.array([ROW[t]>>s&1 for s in cols],dtype=np.uint8)
        c=(inv@y)%2
        lab.append(int(sum(int(c[i])<<i for i in range(9))))
    PHI=np.array([[Bd[idx[i],idx[j]] for j in range(9)] for i in range(9)])  # Bd[t,s]=c_t^T PHI c_s
    return lab,PHI,idx
LAB,PHI,BIDX=labels()
PHIROW=[sum(int(PHI[i,j])<<j for j in range(9)) for i in range(9)]
def phi_vec(x):  # Phi x as 9-bit int
    return sum(((bin(PHIROW[i]&x).count('1'))&1)<<i for i in range(9))
PL=[phi_vec(x) for x in LAB]
def form(x,y): return bin(phi_vec(x)&y).count('1')&1
if __name__=='__main__':
    assert len(FRM)==1260, len(FRM)
    assert all(form(LAB[t],LAB[s])==Bd[t,s] for t in range(n) for s in range(n))
    print('frames',len(FRM),'labels distinct',len(set(LAB)))
