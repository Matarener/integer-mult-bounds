"""For every ordinary width-8 or width-9 helper and every raise P = E + <u>: which contacts block,
and are they all reads before the first producer?"""
import sys
from collections import Counter,defaultdict
from timeline import *
tag=sys.argv[1] if len(sys.argv)>1 else 'base'
w=load(tag); ev=events(w); con=contacts(ev)
bill,widths,chain,start,end=C.frame_bill(w)
rest=set(map(int,w['helper_final'])); removed=set(w['removed'])
corrsrc={c['source'] for c in w['initial_corrections']}
res=[]
for h in range(224,704):
    if h in removed or h in rest: continue
    E=start[h]; wd=C.dim(end[h])-C.dim(E)
    if wd not in (8,9): continue
    cs=[ev[p] for p in con[h]]
    prod=next((i for i,e in enumerate(cs) if writes(e,h)),len(cs))
    seen=set(); ok_us=[]
    for u in range(1,512):
        if E>>u & 1: continue
        P=C.span(tuple(C.points(E))+(u,)) if False else None
        # P = E + <u>: points of E and of E^u
        pts=C.points(E); P=0
        for x in pts: P|=1<<x; P|=1<<(x^u)
        if P in seen: continue
        seen.add(P)
        block=[i for i,e in enumerate(cs) if e['frame'] is None or (e['frame'] & P)!=P]
        # frameless cut/corr: a correction on h always blocks; cut gates never touch h
        lb=max(block) if block else -1
        if lb>=prod: continue
        if any(not(cs[i]['kind']=='add' and cs[i]['g'][2]==h) for i in block): continue
        ok_us.append((P,len(block),lb,prod))
    if ok_us:
        best=min(ok_us,key=lambda t:t[1])
        kinds=Counter()
        for i in range(best[2]+1):
            e=cs[i]; other=e['g'][1]
            kinds[(e['sec'],'tgt' if 112<=other<224 else 'hlp' if other>=224 else 'src')]+=1
        res.append((h,wd,len(ok_us),best[1],dict(kinds),best[3]-best[2],h in corrsrc))
print(tag,'candidates (h, width, admissible P, min blockers, kinds, contacts to producer, correction source)')
by=Counter()
for r in res:
    by[r[1]]+=1
    print(r)
print('by width',dict(by))
