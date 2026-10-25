"""Exact decoupled ceiling (valid upper bound on root) for any chart/warp lever with FIXED
per-register scalar order and fixed endpoint dims: each register independently picks a
nondecreasing level sequence through its ADD intervals; cost = sum f(climb sizes)."""
import sys,gzip,json; sys.path.insert(0,str(__import__('pathlib').Path.home()/'imb-harness/r12/tools'))
from moment import *
from collections import Counter,defaultdict
side=sys.argv[1] if len(sys.argv)>1 else 'forward'; Cc=0.00302
w=json.loads(gzip.decompress(open(ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','rb').read()))
c=w['canonical'];fr=c['frames'];dim=lambda i:len(fr[i])
s={i:dim(c['start'][i]) for i in range(632)}; fn={i:dim(c['final'][i]) for i in range(632)}
seq=defaultdict(list); actual=defaultdict(list)
for op in w['programs'][side]:
    if op[0]=='scalar' and op[1][0]=='add':
        a,b=tuple(op[1][1]),tuple(op[1][2])
        if a[0]=='L' and b[0]=='L':
            A,B=a[1],b[1]; I=(max(s[A],s[B]),min(fn[A],fn[B]))
            seq[A].append(I); seq[B].append(I)
f=lambda x:x**(1-Cc); INF=float('inf')
def dp(r):
    S,F=s[r],fn[r]
    best={S:(0.0,())}
    for lo,hi in seq[r]:
        new={}
        for l,(cst,pr) in best.items():
            for m in range(max(l,lo),hi+1):
                v=(cst+(f(m-l) if m>l else 0), pr+((m-l,) if m>l else ()))
                if m not in new or v[0]<new[m][0]: new[m]=v
        best=new
    cst,pr=min(((cst+(f(F-l) if F>l else 0),pr+((F-l,) if F>l else ())) for l,(cst,pr) in best.items()),key=lambda t:t[0])
    return pr
P=Counter()
for r in range(632): P.update(dp(r))
P[8]+=8
print('decoupled ceiling paid',dict(sorted(P.items())),'mass',sum(k*v for k,v in P.items()))
_,_,T,PP,_=invoice({'helpers':{4:28,7:7,8:47,9:326},'paid':dict(P)}); print('root ceiling',root(T,PP))
