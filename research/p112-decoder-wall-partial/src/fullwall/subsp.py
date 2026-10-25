# enumerate label-closed subspaces of F2^9: Y = span L(Y)  (L = labels inside). canonical key = frozenset? use RREF tuple
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from base import *
import sys, time
def rref(vs):
    b=[]
    for v in vs:
        for x in b:
            if v ^ x < v: v^=x
        if v:
            # reduce existing by v on its top bit
            hb=v.bit_length()-1
            b=[x^v if x>>hb&1 else x for x in b]; b.append(v)
    return tuple(sorted(b))
def members(basis):
    S=[0]
    for v in basis: S=S+[x^v for x in S]
    return S
labset={x:t for t,x in enumerate(LAB)}
def labmask(basis):
    m=0
    for x in members(basis):
        t=labset.get(x)
        if t is not None: m|=1<<t
    return m
if __name__=='__main__':
    t0=time.time()
    level={():0}; allsp={():0}
    for d in range(9):
        nxt={}
        for B,m in level.items():
            for t in range(n):
                if m>>t&1: continue
                B2=rref(list(B)+[LAB[t]])
                if B2 in nxt: continue
                nxt[B2]=labmask(B2)
        level=nxt; allsp.update(nxt)
        print('dim',d+1,len(nxt),round(time.time()-t0,1),flush=True)
    pickle.dump(allsp,open(HERE+'/subsp.pkl','wb'))
