#!/usr/bin/env python3
"""Constructive frame optimization for changed literal scalar circuits.

Credit: rank7-joint-frame-optimum's chronological graph and min-sum
elimination method, and the source word's cited native construction lineage.
This implementation adds assignment traceback and admits changed gate graphs.
Optimization is a floating screening step; literal traces and final exact
invoice checks must independently validate any resulting gain. Apache-2.0.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
from itertools import product
from math import prod
from pathlib import Path
import argparse,gzip,json
from fanout_search import basis,span,contains,meet,phi,read,expand,regs,derive_cleanup

FULL=basis(tuple(1<<i for i in range(9)))

@lru_cache(None)
def join(a,b):return basis(a+b)

@lru_cache(None)
def domain(lo,hi):
    assert contains(lo,hi)
    if len(hi)-len(lo)>4:raise ValueError('quotient capacity')
    choices={lo}
    for _ in range(len(hi)-len(lo)):
        choices|={join(f,(v,)) for f in choices for v in hi if not contains((v,),f)}
        # Basis vectors alone do not enumerate quotient lines: include all
        # upper-space vectors on each level.
        choices|={join(f,(v,)) for f in choices for v in span(hi)-span(f)}
    return tuple(sorted(choices,key=lambda f:(len(f),f)))

def graph(w):
    live=set(range(704))-set(w['removed']);sec=expand(w)
    starts={r:basis((w['ports'][r],)) if r<112 else basis(tuple(w['start_extra'].get(str(r),[]))) for r in live}
    ends={r:FULL if not 112<=r<224 else basis(tuple(v for v in range(512) if not ((v&w['ports'][r-112]).bit_count()%2))) for r in live}
    ends.update({int(r):basis(tuple(f)) for r,f in w['helper_final'].items()})
    cur={r:(-1,starts[r]) for r in live};edges=[];nodes=[];frames=[]
    def anchor(r,f,new=None):
        f=basis(tuple(f));a,af=cur[r];edges.append((r,a,af,-1,f));cur[r]=(-1,f if new is None else basis(tuple(new)))
    for name in ('A','B','restore'):
        for i,e in enumerate(sec[name]):
            if e[0]=='warp':anchor(e[1],e[3],e[4]);continue
            j=len(nodes);f=basis(tuple(e[-1]));nodes.append((name,i));frames.append(f)
            for r in regs(e):
                a,af=cur[r];edges.append((r,a,af,j,f));cur[r]=(j,f)
        if name=='A':
            for r,f in zip(w['centers'],w['center_frames']):anchor(r,f)
            for t in range(112):anchor(112+t,w['target_levels'].get(str(t),[]))
    for r in live:anchor(r,ends[r])
    incoming=defaultdict(list);outgoing=defaultdict(list)
    for r,a,af,b,bf in edges:
        incoming[b].append((a,af));outgoing[a].append((b,bf))
    lo=[];hi=[FULL]*len(nodes)
    for i in range(len(nodes)):
        f=()
        for a,af in incoming[i]:f=join(f,lo[a] if a>=0 else af)
        lo.append(f)
    for i in reversed(range(len(nodes))):
        for b,bf in outgoing[i]:hi[i]=meet(hi[i],hi[b] if b>=0 else bf)
        if not contains(lo[i],hi[i]):raise ValueError(('infeasible',nodes[i],lo[i],hi[i]))
    variable={i for i in range(len(nodes)) if lo[i]!=hi[i]};adj={i:set() for i in variable}
    for _,a,_,b,_ in edges:
        if a in variable and b in variable:adj[a].add(b);adj[b].add(a)
    comps=[];seen=set()
    for root in sorted(variable):
        if root in seen:continue
        todo=[root];seen.add(root);comp=[]
        while todo:
            i=todo.pop();comp.append(i)
            for j in adj[i]-seen:todo.append(j);seen.add(j)
        comps.append(tuple(sorted(comp)))
    return sec,nodes,frames,edges,lo,hi,comps

def solve_component(comp,edges,lo,hi,max_bucket):
    members=set(comp);owned=[e for e in edges if e[1] in members or e[3] in members]
    choices={i:domain(lo[i],hi[i]) for i in comp};factors=[]
    for _,a,af,b,bf in owned:
        scope=tuple(i for i in (a,b) if i in choices);table={}
        for vals in product(*(range(len(choices[i])) for i in scope)):
            ass={i:choices[i][v] for i,v in zip(scope,vals)}
            before=ass.get(a,lo[a] if a>=0 else af);after=ass.get(b,lo[b] if b>=0 else bf)
            if contains(before,after):table[vals]=phi(len(after)-len(before))
        factors.append((scope,table))
    adj={i:set() for i in comp}
    for scope,_ in factors:
        for i in scope:adj[i].update(set(scope)-{i})
    trace=[];attempts=0
    while adj:
        var=min(adj,key=lambda i:(prod(len(choices[j]) for j in adj[i]|{i}),len(adj[i]),i))
        neighbors=tuple(sorted(adj[var]));variables=(var,)+neighbors
        cap=prod(len(choices[i]) for i in variables)
        if cap>max_bucket:raise ValueError(('bucket capacity',cap,len(comp)))
        used=[f for f in factors if var in f[0]];factors=[f for f in factors if var not in f[0]]
        indexes=[tuple(variables.index(i) for i in scope) for scope,_ in used]
        table={};back={};attempts+=cap
        for vals in product(*(range(len(choices[i])) for i in variables)):
            costs=[f[1].get(tuple(vals[j] for j in pos)) for f,pos in zip(used,indexes)]
            if any(c is None for c in costs):continue
            total=sum(costs);key=vals[1:]
            if key not in table or total<table[key]-1e-11:table[key]=total;back[key]=vals[0]
        if not table:raise ValueError('empty factor')
        factors.append((neighbors,table));trace.append((var,neighbors,back))
        for j in neighbors:adj[j].update(set(neighbors)-{j});adj[j].remove(var)
        del adj[var]
    assignment={}
    for var,neighbors,back in reversed(trace):assignment[var]=back[tuple(assignment[j] for j in neighbors)]
    return {i:choices[i][v] for i,v in assignment.items()},attempts

def optimize(w,max_bucket=100000):
    sec,nodes,frames,edges,lo,hi,comps=graph(w);ass=dict(enumerate(lo));attempts=0
    for comp in comps:
        solved,count=solve_component(comp,edges,lo,hi,max_bucket);ass.update(solved);attempts+=count
    out=deepcopy(w)
    expanded=deepcopy(sec)
    for i,(name,p) in enumerate(nodes):expanded[name][p][-1]=list(ass[i])
    out['A']=expanded['A'];out['restore']=expanded['restore'];out['B']=[]
    for e in expanded['B']:
        if e[0]=='warp':out['warps'][e[2]-1][0]=len(out['B'])
        else:out['B'].append(e)
    paid=Counter()
    for _,a,af,b,bf in edges:
        before=ass[a] if a>=0 else af;after=ass[b] if b>=0 else bf
        assert contains(before,after)
        if len(after)>len(before):paid[len(after)-len(before)]+=1
    for r,f in zip(w['centers'],w['center_frames']):
        f=basis(tuple(f))
        levels={basis(tuple(w['target_levels'].get(str(e[1]-112),[]))) for e in w['cut'] if e[2]==r}
        for level in sorted(levels,key=lambda f:-len(f)):
            assert contains(level,f)
            if f!=level:paid[len(f)-len(level)]+=1
            f=level
    derive_cleanup(out);out['report']['local_profile']={str(r):n for r,n in sorted(paid.items())}
    old=Counter({int(r):n for r,n in w['report']['local_profile'].items()});delta=paid.copy();delta.subtract(old)
    return out,dict(delta={r:n for r,n in delta.items() if n},attempts=attempts,components=len(comps),variables=sum(map(len,comps)),changed_frames=sum(f!=ass[i] for i,f in enumerate(frames)),saving=-sum(n*phi(r) for r,n in delta.items()))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    w,receipt=optimize(read(a.word));a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    a.out.with_suffix('.result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
