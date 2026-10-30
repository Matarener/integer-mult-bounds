# Build Aut(Bd) (172,032 permutations of the 112 lines) by BFS from the pynauty generators -> G.npy (not shipped, regenerated).
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import pynauty, time, numpy as np
OUT=os.path.dirname(os.path.abspath(__file__)); t0=time.time()
ADJ={i:[j for j in range(n) if j!=i and Bd[i,j]] for i in range(n)}
gens,a,b,_,_=pynauty.autgrp(pynauty.Graph(n,adjacency_dict=ADJ)); AUT=round(a*10**b); print('Aut',AUT,'gens',len(gens))
gens=[np.array(g,dtype=np.int16) for g in gens]
for g in gens: assert (Bd[np.ix_(g,g)]==Bd).all()
idp=np.arange(n,dtype=np.int16); seen={idp.tobytes()}; frontier=[idp]; allg=[idp]
while frontier:
    nf=[]
    for p in frontier:
        for g in gens:
            q=g[p]; k=q.tobytes()
            if k not in seen: seen.add(k); nf.append(q); allg.append(q)
    frontier=nf
G=np.array(allg,dtype=np.int16); assert len(G)==AUT==172032; print('G built',G.shape,round(time.time()-t0,1))
np.save(OUT+'/G.npy',G)
