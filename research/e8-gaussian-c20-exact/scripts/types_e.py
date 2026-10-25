"""Rank-maximal flat-pair types (1<=R<=3) with e = 128R+128-h <= EMAX; dedupe by (miss set, R).  Output types_e{EMAX}.pkl"""
import pickle, sys, numpy as np
from collections import Counter
EMAX=int(sys.argv[1])
d=pickle.load(open('hits_table.pkl','rb')); fl=d['fl']; R=d['R']; H=d['hits']; C=d['C']
n=len(fl); L=[set(f) for f,dd in fl]
E=128*R+128-H
sup=[[j for j in range(n) if L[i] < L[j]] for i in range(n)]
enlX=np.zeros((n,n),bool); enlY=np.zeros((n,n),bool)
for i in range(n):
    if sup[i]:
        enlX[i]=(R[sup[i],:]==R[i][None,:]).any(0)
        enlY[:,i]=(R[:,sup[i]]==R[:,i][:,None]).any(1)
ok=(R>=1)&(R<=3)&(E<=EMAX)&~enlX&~enlY
ts=np.argwhere(ok)
Lo=np.zeros((n,60),np.int64)
for i,(f,dd) in enumerate(fl): Lo[i,sorted(f)]=1
inc=np.zeros((60,640),np.int64)
for k,c in enumerate(C): inc[c,k]=1
meet=(Lo@inc>0)
miss={}
for a,b in ts:
    m=~(meet[a]&meet[b]); key=(int(R[a,b]),np.packbits(m).tobytes())
    if key not in miss: miss[key]=(int(a),int(b))
print('EMAX',EMAX,'rank-max pairs',len(ts),'distinct (R,miss)',len(miss))
print(Counter((len(fl[a][0]),len(fl[b][0]),int(R[a,b]),int(E[a,b])) for (r,k),(a,b) in miss.items()).most_common())
pickle.dump([(a,b,r,int(E[a,b]),np.unpackbits(np.frombuffer(k,np.uint8))[:640].astype(bool)) for (r,k),(a,b) in miss.items()],open('types_e%d.pkl'%EMAX,'wb'))
