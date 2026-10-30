# CORE3 stats.py: for every flat Z (rank <= 7, up to Aut; flats.pkl) the label structure of T = H^c = L \ Z
# (H^c(q) = L \ Z(q) with Z(q) = lines orthogonal to q, a flat of rank <= 7; every such flat occurs for q generic in Z^perp).
#  D(T)      = dim span lab(T)                      [I3: need >= 8]
#  cocirc    = min |T \ L(H)| over F2-hyperplanes H of span lab(T)   (min cocircuit of the label matroid of T)
#  kappa(T)  = min over cocircuits C of dim span lab(C)  (no subspace Y with dim Y < kappa contains a cocircuit, so removing
#              the lines of such a Y from T never lowers span lab(T))   [I4']
# EXACT (F2 / integer arithmetic only).
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import pickle
from collections import Counter, defaultdict
HERE3=os.path.dirname(os.path.abspath(__file__))
FL=pickle.load(open(HERE3+'/flats.pkl','rb'))
FULL=(1<<n)-1
ODD=[sum(1<<t for t in range(n) if bin(h&LAB[t]).count('1')&1) for h in range(512)]
def rank_lines(m):
    b=[]
    x=m
    while x:
        t=(x&-x).bit_length()-1; x&=x-1; v=LAB[t]
        for y in b: v=min(v,v^y)
        if v: b.append(v)
    return len(b)
res=[]; byrank=defaultdict(Counter)
for o in FL:
    if o['rank']>7: continue
    T=FULL&~o['mask']
    D=rank_lines(T)
    cc=10**9; kap=10**9; cmin_sp=None
    seenC=set()
    for h in range(1,512):
        Cm=T&ODD[h]
        if not Cm or Cm in seenC: continue
        seenC.add(Cm)
        sz=bin(Cm).count('1'); cc=min(cc,sz)
        k=rank_lines(Cm); kap=min(kap,k)
    r=dict(rank=o['rank'],nZ=o['nlines'],nT=bin(T).count('1'),D=D,cocirc=cc,kappa=kap,orbit=o['orbit'],mask=o['mask'])
    res.append(r); byrank[o['rank']][(r['nZ'],D,cc,kap)]+=1
for rk in sorted(byrank):
    print('rank',rk,'orbits',sum(byrank[rk].values()),' (|Z|, D, min cocircuit, kappa): #orbits')
    for k,v in sorted(byrank[rk].items()): print('   ',k,v)
r7=[r for r in res if r['rank']==7]
print('I1 max |Z| over rank-7 flats (= max lines on a hyperplane):',max(r['nZ'] for r in r7), ' => min |H^c(q)| =',112-max(r['nZ'] for r in r7))
print('I3 min D over rank-7 flats:',min(r['D'] for r in r7),' over all flats:',min(r['D'] for r in res))
print('min cocircuit over all flats:',min(r['cocirc'] for r in res),'  kappa_min over all flats:',min(r['kappa'] for r in res))
pickle.dump(res,open(HERE3+'/stats.pkl','wb'))
