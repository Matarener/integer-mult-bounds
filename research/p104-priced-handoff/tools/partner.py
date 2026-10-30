"""Single-partner co-framed hand-off screen (exhaustive over time).
Helper h mid-life with holders(h)=={h}, row(h)=h+D (D!=0). Partner j with row(j)=c*D at time t.
Hand-off at frame F: h -= (1/c) j ; s += (1/c) j ; s replaces h afterwards.
Price: gain g(k-d0,d1-k); cost: for h and j, 0 if F in their window chain else g(split) (if nestable)."""
import gzip,json,sys,bisect
from fractions import Fraction as Q
from collections import defaultdict,Counter
C=float(sys.argv[3]) if len(sys.argv)>3 else 0.0030814
f=lambda x: x**(1-C) if x>0 else 0.0
g=lambda a,b: f(a)+f(b)-f(a+b) if a>0 and b>0 else 0.0
w=json.load(gzip.open(sys.argv[1])); NP=w['public']; NR=NP+8; FR=w['frames']; dim=[len(x) for x in FR]
def elems(b):
    out={0}
    for v in b: out|={x^v for x in out}
    return out
EL=[sum(1<<x for x in elems(b)) for b in FR]
def sub(a,b): return (EL[a]|EL[b])==EL[b]   # frame a subset of frame b
P=w['program']; live=set(w['live']); main=live|{r+112 for r in live}
def regs(e): return (e[1],) if e[0] in('MOVE','INIT','CLEAR','SCALE') else (e[1],e[2])
cur=list(w['initial'])+[None]*8
sidx={r:[] for r in range(NR)}; win={r:[] for r in range(NR)}
chain={r:[cur[r]] for r in range(NR)}
for i,e in enumerate(P):
    if e[0]=='MOVE': chain[e[1]].append(e[3]); continue
    for x in regs(e):
        sidx[x].append(i); win[x].append(chain[x])
        fr=e[-1] if e[0] not in('INIT','CLEAR') else e[2]
        chain[x]=[fr] if e[0]!='CLEAR' else [None]
for r in range(NR): win[r].append(chain[r])
def window(j,t):
    k=bisect.bisect_right(sidx[j],t); return win[j][k]
first={r:sidx[r][0] for r in range(NP) if sidx[r]}; last={r:sidx[r][-1] for r in range(NP) if sidx[r]}
d0=[dim[w['initial'][r]] for r in range(NP)]; d1=[dim[w['final'][r]] for r in range(NP)]
rows=[{r:Q(1)} for r in range(NR)]
holders=defaultdict(set)
for r in range(NR): holders[r].add(r)
def norm(row):
    if not row: return None
    k0=min(row); c=row[k0]
    return tuple(sorted((k,x/c) for k,x in row.items())),c
index=defaultdict(set)  # normalized D -> helpers carrying it
carry={}  # h -> key
def dkey(h):
    if not(h<NP and h not in main and h in first): return None
    if holders[h]!={h} or rows[h].get(h)!=1: return None
    D={k:x for k,x in rows[h].items() if k!=h}
    n=norm(D); return n[0] if n else None
def refresh(h):
    k=carry.pop(h,None)
    if k is not None: index[k].discard(h)
    k=dkey(h)
    if k is not None: carry[h]=k; index[k].add(h)
stats=Counter(); out=[]
def rr(basis):
    rows=[]
    for v in basis:
        for r in rows:
            if v^r<v: v^=r
        if v:
            rows=[(r^v if r^v<r else r) for r in rows]; rows.append(v)
    return rows
def rank(b): return len(rr(b))
def price(h,j,i):
    chh=window(h,i); chj=window(j,i)
    if None in chj: return
    best=None
    Fs=set(chh)|set(chj)
    for F in Fs:
        k=dim[F]
        if not(d0[h]<k<d1[h]): continue
        cs=[]
        for ch in (chh,chj):
            if F in ch: cs.append(0.0)
            elif sub(ch[0],F) and sub(F,ch[-1]): cs.append(g(k-dim[ch[0]],dim[ch[-1]]-k))
            else: cs.append(None)
        if None in cs: continue
        gain=g(k-d0[h],d1[h]-k); net=gain-sum(cs)
        r=(net,gain,sum(cs),h,j,i,F,k,[dim[x] for x in chh],[dim[x] for x in chj])
        if best is None or r[0]>best[0]: best=r
    # generic F of dim k between lo=A_h+A_j and hi=B_h & B_j
    lo=rank(FR[chh[0]]+FR[chj[0]]); him=EL[chh[-1]]&EL[chj[-1]]
    if all(him>>v&1 for v in rr(FR[chh[0]]+FR[chj[0]])):
        dhi=him.bit_count().bit_length()-1
        for k in range(max(lo,d0[h]+1),min(dhi,d1[h]-1)+1):
            cs=sum(g(k-dim[ch[0]],dim[ch[-1]]-k) for ch in (chh,chj))
            gain=g(k-d0[h],d1[h]-k)
            rr_=(gain-cs,gain,cs,h,j,i,'gen',k,[dim[x] for x in chh],[dim[x] for x in chj])
            stats['generic']+=1
            if best is None or rr_[0]>best[0]: best=rr_
    if best: out.append(best)
for i,e in enumerate(P):
    op,r=e[:2]
    if op=='MOVE': continue
    before=set(rows[r])
    if op in('INIT','CLEAR'): newrow={}
    elif op=='SCALE': q=Q(e[-2]); newrow={k:q*x for k,x in rows[r].items()}
    else:
        q=Q(e[-2]); s=e[2]
        if op=='COPY': newrow={k:q*x for k,x in rows[s].items()}
        else:
            newrow=dict(rows[r])
            for k,x in rows[s].items():
                v=newrow.get(k,0)+q*x
                if v: newrow[k]=v
                else: newrow.pop(k,None)
    for k in rows[r]:
        if k not in newrow: holders[k].discard(r)
    for k in newrow: holders[k].add(r)
    rows[r]=newrow
    aff={k for k in before|set(newrow) if k<NP}|{r}
    for h in aff: refresh(h)
    if op in ('ADD','COPY'): refresh(e[2])
    # matches involving changed register r as partner, or helpers whose D changed (h in aff) vs all partners
    n=norm(rows[r])
    if n:
        for h in index.get(n[0],()):
            if h!=r and first[h]<=i<last[h]: stats['match']+=1; price(h,r,i)
    for h in aff:
        if h in carry and first[h]<=i<last[h]:
            key=carry[h]
            # find partners holding exactly c*D: candidates are holders of min symbol of D
            k0=key[0][0]
            for j in holders[k0]:
                if j!=h:
                    nj=norm(rows[j])
                    if nj and nj[0]==key: stats['match2']+=1; price(h,j,i)
out.sort(key=lambda o:-o[0])
print(dict(stats),'priced',len(out),'net>0',sum(o[0]>0 for o in out))
seen=set()
for o in out:
    if o[0]>0 and (o[3],o[4]) not in seen: seen.add((o[3],o[4])); print(o)
json.dump(out,open(sys.argv[2],'w'))
