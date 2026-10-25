# orbit reps (under Aut(Bd), via pynauty certificates of the coloured orthogonality graph) of label-closed subspaces X of F2^9
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from base import *
import pynauty, time
from subsp import rref, labmask
ADJ={i:[j for j in range(n) if j!=i and Bd[i,j]] for i in range(n)}
def cert(mask):
    s=set(t for t in range(n) if mask>>t&1)
    g=pynauty.Graph(n,adjacency_dict=ADJ,vertex_coloring=[s,set(range(n))-s] if s and len(s)<n else [set(range(n))])
    return pynauty.certificate(g)
def autsize(mask):
    s=set(t for t in range(n) if mask>>t&1)
    g=pynauty.Graph(n,adjacency_dict=ADJ,vertex_coloring=[s,set(range(n))-s] if s and len(s)<n else [set(range(n))])
    _,a,b,_,_=pynauty.autgrp(g); return round(a*10**b)
if __name__=='__main__':
    t0=time.time(); AUT=autsize(0); print('Aut',AUT)
    reps={0:[((),0)]}
    level=[((),0)]
    for d in range(1,10):
        seen={}
        for B,m in level:
            for t in range(n):
                if m>>t&1: continue
                B2=rref(list(B)+[LAB[t]]); m2=labmask(B2)
                c=cert(m2)
                if c not in seen: seen[c]=(B2,m2)
        level=list(seen.values()); reps[d]=level
        tot=sum(AUT//autsize(m) for _,m in level)
        print('dim',d,'orbits',len(level),'subspaces',tot,round(time.time()-t0,1),flush=True)
    pickle.dump(reps,open(HERE+'/xorb.pkl','wb'))
