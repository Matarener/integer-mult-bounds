import pickle, itertools, time, sys
import numpy as np
from scipy.optimize import linprog
tab=np.load('phitab4.npy')            # [Z, S-1, T-1, X-1]
U=list(range(1,16)); KEYS=[(S,T) for S in U for T in U]; SINGLES=[1,2,4,8]
OFF=[(P,Q) for P in SINGLES for Q in SINGLES if P!=Q]
obj=np.array([2*bin(X).count('1') for X in U],float)
def solve(tt, masks):
    b=np.array(tt,float)
    A=tab[masks][:, :, :, :].transpose(1,2,0,3).reshape(225, len(masks)*15).astype(float)
    c=-np.tile(obj,len(masks))
    r=linprog(c,A_ub=A,b_ub=b,bounds=(0,None),method='highs')
    return -r.fun, r.x
weak=pickle.load(open('quad_weak.pkl','rb'))
CH=int(sys.argv[1]); NCH=int(sys.argv[2]); weak=weak[CH::NCH]
res={}; t=time.time(); fails=[]; full=0
for n,tt in enumerate(weak):
    T=dict(zip(KEYS,tt))
    cheap=[i for i,(P,Q) in enumerate(OFF) if T[P,Q]<=1]
    masks=sorted({sum(1<<i for i in sub) for r in range(len(cheap)+1) for sub in itertools.combinations(cheap,r)} | {4095})
    val,x=solve(tt,masks)
    if val<16-1e-6:
        masks=list(range(4096)); full+=1
        val,x=solve(tt,masks)
    nz=[(masks[i//15], U[i%15], float(w)) for i,w in enumerate(x) if w>1e-9]
    res[tt]=(val,nz)
    if val<16-1e-6: fails.append(tt)
    if n%200==0: print(n,len(weak),round(time.time()-t),'full',full,'fails',len(fails),flush=True)
pickle.dump(res,open(f'quad_cert_{CH}.pkl','wb'))
print('done',len(weak),'full',full,'fails',len(fails),round(time.time()-t),flush=True)
