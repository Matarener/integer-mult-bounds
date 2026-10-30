"""Ceiling for any chart/retiming lever that keeps per-register climb mass:
replace each register's climb chain by one climb of the same total rank."""
import sys,gzip,json; sys.path.insert(0,str(__import__('pathlib').Path.home()/'imb-harness/r12/tools'))
from moment import *
from collections import Counter,defaultdict
w=json.loads(gzip.decompress(open(ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','rb').read()))
c=w['canonical'];fr=c['frames'];dim=lambda i:len(fr[i])
helpers={4:28,7:7,8:47,9:326}
for side in ['forward','backward']:
    steps=defaultdict(list)
    for op in w['programs'][side]:
        if op[0]=='climb': steps[op[2]].append(op[5])
    nsteps=Counter(len(v) for v in steps.values())
    one=Counter(sum(v) for v in steps.values()); one[8]+=8  # centres
    print(side,'chain lengths',dict(sorted(nsteps.items())),'consolidated paid',dict(one))
    for name,N in [('current',LOCAL['paid']),('consolidated',dict(one))]:
        H,_,T,P,_=invoice({'helpers':helpers,'paid':N}); print(f'  {name:13s} root {root(T,P):.10f}')
    # helper-only consolidation (main chains kept) : classify main as registers with total 8 and start dim>=0 not helper — ambiguous; report split
