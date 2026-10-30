"""Co-framed hand-off screen: helper h at frame F (d0<dim F<d1) such that
(2) every register holding symbol h sits at F, and (1) h in span(rows at F).
Then an invertible ADD transform at F realises the successor rename (no paid change)."""
import gzip,json,sys
from fractions import Fraction as Q
from collections import defaultdict,Counter
w=json.load(gzip.open(sys.argv[1]))
NP=w['public']; NR=NP+8
dim=[len(f) for f in w['frames']]
live=set(w['live']); main=live|{r+112 for r in live}
rows=[{r:Q(1)} for r in range(NR)]
holders=defaultdict(set)
for r in range(NR): holders[r].add(r)
cur=list(w['initial'])+[None]*8
atF=defaultdict(set)
for r in range(NP): atF[cur[r]].add(r)
d0=[dim[w['initial'][r]] for r in range(NP)]; d1=[dim[w['final'][r]] for r in range(NP)]
ishelper=[r not in main for r in range(NP)]
def setrow(r,new):
    old=rows[r]
    for k in old:
        if k not in new: holders[k].discard(r)
    for k in new: holders[k].add(r)
    rows[r]=new
def setcur(r,f):
    if cur[r] is not None: atF[cur[r]].discard(r)
    cur[r]=f
    if f is not None: atF[f].add(r)
def inspan(h,F):
    # is unit vector e_h in span of rows at F ?  sparse elimination
    piv={}  # pivot symbol -> row
    for j in atF[F]:
        v=dict(rows[j])
        for p,rv in piv.items():
            c=v.get(p)
            if c:
                for k,x in rv.items():
                    y=v.get(k,0)-c*x
                    if y: v[k]=y
                    else: v.pop(k,None)
        if not v: continue
        p=min(v); c=v[p]; v={k:x/c for k,x in v.items()}
        for q,rv in piv.items():
            cc=rv.get(p)
            if cc:
                for k,x in v.items():
                    y=rv.get(k,0)-cc*x
                    if y: rv[k]=y
                    else: rv.pop(k,None)
        piv[p]=v
    t={h:Q(1)}
    for p,rv in piv.items():
        c=t.get(p)
        if c:
            for k,x in rv.items():
                y=t.get(k,0)-c*x
                if y: t[k]=y
                else: t.pop(k,None)
    return not t
found=defaultdict(dict)  # h -> {F: first event}
nc2=0;ntest=0
def test(h,i):
    global nc2,ntest
    F=cur[h]
    if F is None or not (d0[h]<dim[F]<d1[h]): return
    if F in found[h]: return
    if any(cur[j]!=F for j in holders[h]): return
    nc2+=1
    if inspan(h,F): found[h][F]=i
for i,e in enumerate(w['program']):
    op,r=e[:2]
    touched=set()
    if op=='MOVE':
        setcur(r,e[3]); touched=set(rows[r])|{r}
    elif op in('INIT','CLEAR'):
        touched=set(rows[r]); setrow(r,{}); setcur(r,e[2] if op=='INIT' else None)
    else:
        q=Q(e[-2])
        if op=='SCALE': setrow(r,{k:q*x for k,x in rows[r].items()}); touched=set(rows[r])
        else:
            s=e[2]; touched=set(rows[r])
            if op=='COPY': setrow(r,{k:q*x for k,x in rows[s].items()})
            else:
                new=dict(rows[r])
                for k,x in rows[s].items():
                    v=new.get(k,0)+q*x
                    if v: new[k]=v
                    else: new.pop(k,None)
                setrow(r,new)
            touched|=set(rows[r])
    # span at frame cur[r] changed: any helper at that frame might newly pass (1)
    F=cur[r]
    cand={k for k in touched if k<NP and ishelper[k]}
    if F is not None: cand|={k for k in atF[F] if k<NP and ishelper[k]}
    for h in cand: test(h,i)
res={}
for h,d in found.items():
    if d: res[h]={'d0':d0[h],'d1':d1[h],'mid':sorted({dim[F] for F in d}),'pts':sorted((i,F) for F,i in d.items())}
print('tests (2) passed',nc2,'helpers with co-framed handoff',len(res))
print(Counter((v['d0'],v['d1'],tuple(v['mid'])) for v in res.values()).most_common(50))
json.dump({str(k):v for k,v in res.items()},open(sys.argv[2],'w'))
