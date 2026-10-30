"""RLEVER: is the #5756 signal sign matrix S low-degree algebraic in the port bits (gauge-free test on row pairs)?"""
import os
import sys,itertools
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/RESIDUAL')
from geo import *
g=load(); S=np.sign(g['S']).astype(int); ports=g['ports']; m=g['m']
K=S.shape[0]
def bits(p): return [(p>>t)&1 for t in range(9)]
def monos(deg):
    return [c for d in range(deg+1) for c in itertools.combinations(range(9),d)]
def fit(idx,y,deg):
    """solve over F2: sum coef*mono(p_i)=y_i for i in idx; return True if consistent"""
    M=monos(deg); A=np.array([[int(all(bits(ports[i])[t] for t in c)) for c in M] for i in idx],dtype=np.uint8)
    b=np.array(y,dtype=np.uint8); A=np.concatenate([A,b[:,None]],1)
    r=0; rows,cols=A.shape
    for c in range(cols-1):
        piv=None
        for i in range(r,rows):
            if A[i,c]: piv=i;break
        if piv is None: continue
        A[[r,piv]]=A[[piv,r]]
        for i in range(rows):
            if i!=r and A[i,c]: A[i]^=A[r]
        r+=1
    return not any(A[i,-1] and not A[i,:-1].any() for i in range(rows))
res={d:0 for d in (1,2,3,4)}; tot=0
for k in range(K):
    for l in range(k+1,K):
        idx=[i for i in range(m) if S[k,i]!=0 and S[l,i]!=0]
        if len(idx)<3: continue
        y=[int(S[k,i]*S[l,i]<0) for i in idx]; tot+=1
        for d in res:
            if fit(idx,y,d): res[d]+=1
print('row pairs',tot,'consistent by degree',res)
for k in range(K):
    idx=[i for i in range(m) if S[k,i]!=0]; y=[int(S[k,i]<0) for i in idx]
    print(k,len(idx),[fit(idx,y,d) for d in (1,2,3)])
