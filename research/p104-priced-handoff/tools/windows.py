"""Frame-independent screen: times where helper h is pure ({h:1}) and no other register holds h,
strictly after h's first scalar event and strictly before its last scalar event (mid-life windows)."""
import gzip,json,sys
from fractions import Fraction as Q
from collections import defaultdict,Counter
w=json.load(gzip.open(sys.argv[1]))
NP=w['public']; NR=NP+8
live=set(w['live']); main=live|{r+112 for r in live}
P=w['program']
first={};last={}
for i,e in enumerate(P):
    if e[0]=='MOVE': continue
    for r in ((e[1],) if e[0] in('INIT','CLEAR','SCALE') else (e[1],e[2])):
        first.setdefault(r,i); last[r]=i
rows=[{r:Q(1)} for r in range(NR)]
holders=defaultdict(set)
for r in range(NR): holders[r].add(r)
def setrow(r,new):
    for k in rows[r]:
        if k not in new: holders[k].discard(r)
    for k in new: holders[k].add(r)
    rows[r]=new
win=defaultdict(list); nholders=defaultdict(list)
for i,e in enumerate(P):
    op,r=e[:2]
    if op=='MOVE': continue
    touched=set(rows[r])
    if op in('INIT','CLEAR'): setrow(r,{})
    elif op=='SCALE': q=Q(e[-2]); setrow(r,{k:q*x for k,x in rows[r].items()})
    else:
        q=Q(e[-2]); s=e[2]
        if op=='COPY': setrow(r,{k:q*x for k,x in rows[s].items()})
        else:
            new=dict(rows[r])
            for k,x in rows[s].items():
                v=new.get(k,0)+q*x
                if v: new[k]=v
                else: new.pop(k,None)
            setrow(r,new)
    touched|=set(rows[r])|{r}
    for h in touched:
        if h<NP and h not in main and first.get(h,1e9)<=i<last.get(h,-1):
            if rows[h]=={h:Q(1)} and holders[h]=={h}: win[h].append(i)
            # record holders count for diagnostics
print('helpers with mid-life pure isolated windows',len(win),sum(map(len,win.values())))
for h in list(win)[:20]: print(h,win[h][:10],'first',first[h],'last',last[h])
