import io, json, tarfile, itertools, pickle, sys, time
import numpy as np
from scipy.optimize import linprog
ROOT='imb/'
arch=open(ROOT+'research/community-frontier1094-audit/selected-replay.tar.gz','rb').read()
with tarfile.open(fileobj=io.BytesIO(arch),mode='r:gz') as tf:
    data=json.loads(tf.extractfile('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json').read())
rec=sorted(data['recipes'],key=lambda r:r['port']); labels=[r['q'] for r in rec]
planes=json.load(open(ROOT+'research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json'))['matching']
dot=lambda a,b: bin(a&b).count('1')&1
def rank2(rows):
    rank=0; rows=list(rows)
    while rows:
        p=rows.pop()
        if not p: continue
        rank+=1; low=p&-p; rows=[r^p if r&low else r for r in rows]
    return rank
K=4; U=list(range(1,1<<K)); KEYS=[(S,T) for S in U for T in U]
# precompute pairwise plane Gram blocks as bit rows: G[p][q] = list of 2 ints (rows of 2x2 over F2)
G={}
for p in range(56):
    for q in range(56):
        G[p,q]=[sum(dot(labels[a],labels[b])<<j for j,b in enumerate(planes[q])) for a in planes[p]]
def tariffs(quad):
    out=[]
    for S in U:
        rowsP=[quad[k] for k in range(K) if S>>k&1]
        for T in U:
            colsQ=[quad[k] for k in range(K) if T>>k&1]
            rows=[]
            for p in rowsP:
                for r in range(2):
                    v=0
                    for jj,q in enumerate(colsQ): v|=G[p,q][r]<<(2*jj)
                    rows.append(v)
            out.append(rank2(rows))
    return tuple(out)
t=time.time(); classes={}
for n,quad in enumerate(itertools.combinations(range(56),4)):
    classes.setdefault(tariffs(quad),[]).append(quad)
    if n%50000==0: print('done',n,len(classes),round(time.time()-t),flush=True)
pickle.dump(classes,open('quad_classes.pkl','wb'))
print('quadruples',sum(len(v) for v in classes.values()),'classes',len(classes),round(time.time()-t),flush=True)
pop=lambda x: bin(x).count('1')
weak=0; weakcls=[]
for tt,v in classes.items():
    T=dict(zip(KEYS,tt))
    c=[-2*pop(X) for X in U]
    A=[[1.0 if (S&X and Tt&X) else 0.0 for X in U] for S,Tt in KEYS]
    val=-linprog(c,A_ub=A,b_ub=[T[k] for k in KEYS],bounds=[(0,None)]*len(U),method='highs').fun
    if val<16-1e-6: weak+=len(v); weakcls.append(tt)
pickle.dump(weakcls,open('quad_weak.pkl','wb'))
print('block-rank weak quadruples',weak,'classes',len(weakcls),round(time.time()-t),flush=True)
