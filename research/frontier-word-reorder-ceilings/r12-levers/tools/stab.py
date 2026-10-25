"""Exact per-register ceiling for any lever keeping the scalar ADD graph and all
endpoints but freeing scalar order and frames (free warps, any dims).
Each add (A,B) needs A,B at a common frame of some dim d in [max(sA,sB),min(fA,fB)].
Register cost >= min over stabbing chains of sum f(gaps). Sum + centres -> root ceiling."""
import sys,gzip,json,itertools; sys.path.insert(0,str(__import__('pathlib').Path.home()/'imb-harness/r12/tools'))
from moment import *
from collections import Counter,defaultdict
w=json.loads(gzip.decompress(open(ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','rb').read()))
c=w['canonical'];fr=c['frames'];dim=lambda i:len(fr[i])
s={i:dim(c['start'][i]) for i in range(632)}; fn={i:dim(c['final'][i]) for i in range(632)}
iv=defaultdict(set)
for op in w['programs']['forward']:
    if op[0]=='scalar' and op[1][0]=='add':
        a,b=tuple(op[1][1]),tuple(op[1][2])
        if a[0]=='L' and b[0]=='L':
            A,B=a[1],b[1]; I=(max(s[A],s[B]),min(fn[A],fn[B]))
            assert I[0]<=I[1]; iv[A].add(I); iv[B].add(I)
def best(A):
    lo,hi=s[A],fn[A]; need=[I for I in iv[A] if not (I[0]<=lo<=I[1] or I[0]<=hi<=I[1])]
    pts=list(range(lo+1,hi)); bestc=None
    for k in range(len(pts)+1):
        for X in itertools.combinations(pts,k):
            if all(any(I[0]<=x<=I[1] for x in X) for I in need):
                ch=[lo,*X,hi]; prof=[ch[i+1]-ch[i] for i in range(len(ch)-1)]
                cost=sum(p**(1-0.003) for p in prof)
                if bestc is None or cost<bestc[0]: bestc=(cost,prof)
    return bestc[1]
P=Counter(); nst=Counter()
for A in range(632):
    pr=best(A); nst[len(pr)]+=1; P.update(pr)
P[8]+=8
print('min chain lengths',dict(nst),'paid',dict(P))
H,_,T,PP,_=invoice({'helpers':{4:28,7:7,8:47,9:326},'paid':dict(P)}); print('ceiling root',root(T,PP))
