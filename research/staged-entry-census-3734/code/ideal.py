"""Fixed-inventory ideal packing ceiling of the T360 owner model (float LP over idle-bin patterns,
then root of the paid moment). Diagnostic only; ceiling.py gives the exact certificate."""
import numpy as np
from scipy.optimize import brentq, linprog
T=360; NCALL=9*T
CAPS={8:6,16:4,32:4,48:4}
def F(profile,a): return sum(n*r**(1-a) for r,n in profile.items())-896*T*73**(1-a)
def root(profile): return brentq(lambda a:F(profile,a),1e-4,5e-3,xtol=1e-18)
def patterns(cap,W):
    out=[]
    def rec(i,rest,cur):
        if i==len(W): out.append(tuple(cur)); return
        for k in range(rest//W[i]+1): rec(i+1,rest-k*W[i],cur+[k])
    rec(0,cap,[]); return out
def ideal(local,items,iters=4):
    W=sorted(items); cols=[];left=[]
    for cap in CAPS:
        for p in patterns(cap,W):
            cols.append((cap,p)); left.append(cap-sum(k*x for k,x in zip(p,W)))
    A=np.zeros((len(W)+len(CAPS),len(cols)))
    for j,(cap,p) in enumerate(cols):
        for i,k in enumerate(p): A[i,j]=k
        A[len(W)+list(CAPS).index(cap),j]=1
    b=[items[x]*NCALL for x in W]+[CAPS[c]*112*T for c in CAPS]
    a=0.00173
    for _ in range(iters):
        cost=[0.0 if l==0 else l**(1-a) for l in left]
        res=linprog(cost,A_eq=A,b_eq=b,bounds=(0,None),method='highs')
        assert res.status==0,res.message
        prof={r:n*NCALL for r,n in local.items()}
        for y,l in zip(res.x,left):
            if l and y>1e-9: prof[l]=prof.get(l,0)+y
        a=root(prof)
    return a
if __name__=='__main__':
    L3734={1:2440,2:725,3:224,4:102,5:20,8:8}; I3734={4:26,5:2,6:18,7:53,8:96,9:213}
    LPRE={1:2437,2:724,3:226,4:102,5:20,8:8}; IPRE={4:26,5:2,6:18,7:52,8:97,9:213}
    a1=ideal(L3734,I3734); a0=ideal(LPRE,IPRE)
    print('ideal 3734',f'{a1:.15f}','ideal PRE(3682)',f'{a0:.15f}','ideal gain',f'{a1-a0:.3e}','(published realized gain 2.946e-8)')
