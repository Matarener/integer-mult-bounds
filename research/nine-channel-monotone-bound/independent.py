"""All-event adjoint census with an orthogonal mode projector, exact Q."""
from fractions import Fraction as Q
from collections import Counter, defaultdict
import time
from pathlib import Path

def add(a,b,c):
    for i,v in b.items():
        x=a.get(i,Q(0))+c*v
        if x:a[i]=x
        else:a.pop(i,None)

def insert(basis,row):
    row=dict(row)
    while row:
        p=min(row)
        if p not in basis:
            a=row[p]; basis[p]={i:v/a for i,v in row.items()}
            return p
        add(row,basis[p],-row[p])
    return None

def idx(ref):return ref[1]+(632 if ref[0]=='C' else 0)

def census(w,R):
    events=w['programs']['backward'];n=633+w['owned_extra_slots_by_direction']['backward']
    cur=w['canonical']['start'][:]+[None]*(n-632)
    before={}
    for k,e in enumerate(events):
        if e[0]=='scalar' and e[1][0]=='clear':
            d=idx(e[1][1]);before[k]=cur[d];cur[d]=e[2]
        elif e[0] in ('climb','warp'):
            d=e[2] if e[0]=='climb' else idx(e[1])
            if cur[d]!=e[3]:raise ValueError('forward coframe')
            before[k]=cur[d];cur[d]=e[4]
    if cur[:632]!=w['canonical']['final']:raise ValueError('final frames')
    cols=[{i:Q(1)} for i in range(632)]+[{} for _ in range(n-632)]
    bases={}; seen=defaultdict(set); projected={}; contacts=0
    def observe(d):
        nonlocal contacts
        f=cur[d]
        if f is None or len(w['canonical']['frames'][f])>=8 or not cols[d]:return
        contacts+=1
        key=tuple(sorted(cols[d].items()))
        if key in seen[f]:return
        seen[f].add(key)
        if key not in projected:
            row={i:v for i,v in cols[d].items() if i<224 or w['canonical']['start'][i]!=0}
            mode=[sum((r[i]*v for i,v in cols[d].items() if i<112),Q(0))/56 for r in R]
            for j,a in enumerate(mode):
                if a:
                    add(row,{i:x for i,x in enumerate(R[j]) if x},-a)
                    row[632+j]=a
            projected[key]=row
        p=insert(bases.setdefault(f,{}),projected[key])
        if p is not None and p>=632:raise ValueError(('single-frame clean response',f))
    for d in range(n):observe(d)
    for k in range(len(events)-1,-1,-1):
        e=events[k];typ=e[0];changed=[]
        if typ=='scalar':
            a=e[1];d=idx(a[1]);kind=a[0]
            if kind=='add':
                src=idx(a[2])
                if d==src or cur[d]!=e[2] or cur[src]!=e[2]:raise ValueError('ADD coframe')
                add(cols[src],cols[d],Q(a[3],a[4]));changed=[src]
            elif kind=='scale':
                if not a[2] or cur[d]!=e[2]:raise ValueError('SCALE coframe')
                cols[d]={i:v*Q(a[2],a[3]) for i,v in cols[d].items()};changed=[d]
            elif kind=='clear':cols[d]={};changed=[d]
            else:raise ValueError(('unhandled scalar',kind))
        elif typ in ('climb','warp'):
            d=e[2] if typ=='climb' else idx(e[1]);changed=[d]
            if cur[d]!=e[4]:raise ValueError('reverse coframe')
        elif typ not in ('physical_add','adapter','phase'):raise ValueError(('unhandled event',typ))
        if k in before:cur[d]=before[k]
        for d in changed:observe(d)
    return bases,{'all_event_contacts':contacts,'distinct_frame_columns':sum(map(len,seen.values())),'projected_columns':len(projected)}

def paircheck(bases):
    groups=defaultdict(list)
    for f,b in bases.items():
        for p in b:groups[p].append(f)
    pairs=set()
    for g in groups.values():
        for i,f in enumerate(g):
            for h in g[:i]:pairs.add(tuple(sorted((f,h))))
    intersections=0;t=time.time()
    print('independent candidate pairs',len(pairs),flush=True)
    for k,(f,g) in enumerate(sorted(pairs)):
        b=dict(bases[f])
        for row in bases[g].values():
            p=insert(b,row)
            if p is not None and p>=632:raise ValueError(('two-frame clean',f,g))
        if len(b)<len(bases[f])+len(bases[g]):intersections+=1
        if k%50000==0:print('pair',k,'seconds',round(time.time()-t,2),flush=True)
    return {'frames':len(bases),'total_distinct_pairs':len(bases)*(len(bases)-1)//2,'eliminated_pairs':len(pairs),'nontrivial_nuisance_intersections':intersections,'clean_pairs':0}

