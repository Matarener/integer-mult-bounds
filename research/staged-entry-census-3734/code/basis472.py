"""Optimal basis of the fixed-inventory LP for the parent and helper-472 inventories (input to the exact dual)."""
import numpy as np
from scipy.optimize import linprog
from ideal import patterns, root, CAPS, NCALL, T
W=[4,5,6,7,8,9]
for name,local,items in (('parent',{1:2440,2:725,3:224,4:102,5:20,8:8},{4:26,5:2,6:18,7:53,8:96,9:213}),
                         ('472',{1:2455,2:716,3:222,4:104,5:20,8:8},{4:26,5:2,6:18,7:54,8:95,9:213})):
    cols=[];left=[]
    for cap in CAPS:
        for p in patterns(cap,W): cols.append((cap,p)); left.append(cap-sum(k*x for k,x in zip(p,W)))
    A=np.zeros((10,len(cols)))
    for j,(cap,p) in enumerate(cols):
        for i,k in enumerate(p): A[i,j]=k
        A[6+list(CAPS).index(cap),j]=1
    b=[items[x]*NCALL for x in W]+[CAPS[c]*112*T for c in CAPS]
    a=0.00173
    for _ in range(6):
        cost=[0.0 if l==0 else l**(1-a) for l in left]
        res=linprog(cost,A_eq=A,b_eq=b,bounds=(0,None),method='highs')
        prof={r:n*NCALL for r,n in local.items()}
        for y,l in zip(res.x,left):
            if l and y>1e-9: prof[l]=prof.get(l,0)+y
        a=root(prof)
    basis=[cols[j] for j in range(len(cols)) if res.x[j]>1e-7]
    print(name,'ideal root',f'{a:.18f}','basis patterns',len(basis))
    for cap,p in basis: print('   ',(cap,p),'remainder',cap-sum(k*x for k,x in zip(p,W)))
