"""Free successor hand-off screen on a P104 word (local.py replay semantics)."""
import gzip,json,sys
from fractions import Fraction as Q
from collections import defaultdict
w=json.load(gzip.open(sys.argv[1]))
NP=w['public']; NR=NP+8
dim=[len(f) for f in w['frames']]
live=set(w['live']); main=live|{r+112 for r in live}
rows=[{r:Q(1)} for r in range(NR)]
holders=defaultdict(set)
for r in range(NR): holders[r].add(r)
cur=list(w['initial'])+[None]*8
def setrow(r,new):
    old=rows[r]
    for k in old:
        if k not in new: holders[k].discard(r)
    for k in new: holders[k].add(r)
    rows[r]=new
def free(h):
    return rows[h]=={h:Q(1)} and holders[h]=={h}
pts=defaultdict(list)  # helper -> list of (event index after which, frame)
helpers=[r for r in range(NP) if r not in main]
for i,e in enumerate(w['program']):
    op,r=e[:2]
    if op=='MOVE':
        cur[r]=e[3]
        if r in main: continue
        # after a climb: check freeness
        if free(r): pts[r].append((i,e[3]))
        continue
    if op in('INIT','CLEAR'):
        setrow(r,{}); cur[r]=e[2] if op=='INIT' else None; continue
    q=Q(e[-2])
    if op=='SCALE': setrow(r,{k:q*x for k,x in rows[r].items()}); continue
    s=e[2]
    if op=='COPY': setrow(r,{k:q*x for k,x in rows[s].items()})
    else:
        new=dict(rows[r])
        for k,x in rows[s].items():
            v=new.get(k,0)+q*x
            if v: new[k]=v
            else: new.pop(k,None)
        setrow(r,new)
    # after ADD, both r and other symbols: re-check helpers whose freeness may change at current frame
    for h in (r,)+tuple(k for k in rows[s] if k<NP):
        if h<NP and h not in main and free(h): pts[h].append((i,cur[h]))
# Also freeness can arise right after a MOVE or any event; collect candidate frames per helper:
res={}
tot=0
for h in helpers:
    d0,d1=dim[w['initial'][h]],dim[w['final'][h]]
    ds=sorted({dim[f] for i,f in pts[h] if d0<dim[f]<d1})
    if ds:
        res[h]={'d0':d0,'d1':d1,'mid':ds,'points':[(i,f) for i,f in pts[h] if d0<dim[f]<d1]}
        tot+=1
print('helpers',len(helpers),'with free mid points',tot)
from collections import Counter
print(Counter((v['d0'],v['d1'],tuple(v['mid'])) for v in res.values()).most_common(40))
json.dump({str(k):v for k,v in res.items()},open(sys.argv[2],'w'))
