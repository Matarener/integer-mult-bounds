# SPDX-License-Identifier: Apache-2.0
"""Exact stationary common-frame pairs; Chris R with substantial OpenAI assistance.

Uses credited PR3886 chronological tracing and sign certificates unchanged.
No scalar opcode, coefficient, order, native operator or interface is edited.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import hashlib,json,types
P=Path(__file__).resolve().parent

def require(ok,why):
    if not ok:raise ValueError(why)

def module(name,path):
    m=types.ModuleType(name);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
R=module('credited_retiming',P/'vendor/retiming.py')

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@lru_cache(None)
def frames(lo,hi):
    require(R.contained(lo,hi),'empty frame interval')
    require(R.rank(hi)-R.rank(lo)<=4,'declared exhaustive resource limit')
    current={lo};out={lo}
    for _ in range(R.rank(hi)-R.rank(lo)):
        nxt=set()
        for f in current:
            for v in range(1,512):
                if hi>>v&1 and not f>>v&1:nxt.add(R.join(f,R.span((v,))))
        out.update(nxt);current=nxt
    return tuple(sorted(out))

def topology(word):
    nodes,where,bill=R.tracing(word)
    def add(a):return a[0] in ('A','B','restore') and word[a[0]][a[1]][0]=='add'
    addresses=sorted({a for a,r in where if add(a)})
    pairs=sorted({(x[0],y[0]) for seq in nodes.values() for x,y in zip(seq,seq[1:]) if add(x[0]) and add(y[0])})
    return nodes,where,bill,addresses,pairs

def model(word,nodes,where,selected):
    """Delete selected frames; retain exact per-register external boundaries."""
    gates=lambda a:word[a[0]][a[1]]
    bounds={a:[1,(1<<512)-1] for a in selected};tracks=[];old=Counter()
    registers=set(r for a in selected for r in R.touched(gates(a)))
    for r in sorted(registers):
        seq=nodes[r];positions=sorted(where[(a,r)] for a in selected if r in R.touched(gates(a)))
        groups=[]
        for pos in positions:
            if groups and pos==groups[-1][-1]+1:groups[-1].append(pos)
            else:groups.append([pos])
        for group in groups:
            successor=seq[group[-1]+1]
            require(successor[1]!='map','map must have an explicit entry check')
            before,after=seq[group[0]][2],successor[3]
            aa=tuple(seq[i][0] for i in group)
            for i in group:old[R.rank(seq[i][3])-R.rank(seq[i][2])]+=1
            old[R.rank(after)-R.rank(seq[group[-1]][3])]+=1
            first,last=aa[0],aa[-1]
            bounds[first][0]=R.join(bounds[first][0],before);bounds[last][1]&=after
            if successor[1]=='check':bounds[last][0]=R.join(bounds[last][0],after)
            tracks.append((r,before,aa,after,successor[1]))
    return bounds,tracks,old

def bill_delta(tracks,old,assignment):
    new=Counter()
    for _,p,aa,q,kind in tracks:
        chain=[p]+[assignment[a] for a in aa]+[q]
        require(all(R.contained(x,y) for x,y in zip(chain,chain[1:])),'final pair containment')
        if kind=='check':require(chain[-2]==q,'fixed native/cut boundary')
        for x,y in zip(chain,chain[1:]):new[R.rank(y)-R.rank(x)]+=1
    delta=tuple(new[k]-old[k] if k else 0 for k in range(10))
    require(sum(k*n for k,n in enumerate(delta))==0,'rank mass drift')
    return delta

def direct_orders(tracks,old,a,b,fa,fb,olda,oldb):
    # The only nonconstant relation in a coupled pair is Fa <= Fb.
    first_a=R.contained(fa,oldb);first_b=R.contained(olda,fb)
    for yes,assignment in ((first_a,{a:fa,b:oldb}),(first_b,{a:olda,b:fb})):
        if yes:bill_delta(tracks,old,assignment)
    return first_a,first_b

def profiles(hist):
    return [{'delta':list(d),'count':n,'caps':R.caps(d),'prefixes':[sum(R.caps(d)[:j]) for j in range(1,9)],
             'nonimproving':R.all_power_nonnegative(d)} for d,n in sorted(hist.items())]

def census(word):
    nodes,where,baseline,addresses,pairs=topology(word)
    singles=Counter();joint=Counter();cells=Counter();counts=Counter();quotients=Counter();records=[];samples={};false=[]
    for a in addresses:
        bounds,tracks,old=model(word,nodes,where,(a,))
        for f in frames(*bounds[a]):
            d=bill_delta(tracks,old,{a:f});singles[d]+=1
    intervals=set()
    for a,b in pairs:
        bounds,tracks,old=model(word,nodes,where,(a,b))
        require(any(aa==(a,b) for _,_,aa,_,_ in tracks),'uncoupled pair leaked')
        la,ha=bounds[a];lb,hb=bounds[b]
        ha &= hb;lb=R.join(lb,la)
        require(R.contained(la,ha) and R.contained(lb,hb),'invalid propagated interval')
        intervals.update(((la,ha),(lb,hb)))
        quotients[(R.rank(ha)-R.rank(la),R.rank(hb)-R.rank(lb))]+=1
        olda=R.span(tuple(word[a[0]][a[1]][-1]));oldb=R.span(tuple(word[b[0]][b[1]][-1]))
        dims=set();rows=[]
        for fa in frames(la,ha):
            for fb in frames(lb,hb):
                if not R.contained(fa,fb):continue
                assignment={a:fa,b:fb};delta=bill_delta(tracks,old,assignment)
                joint[delta]+=1;dims.add((R.rank(fa),R.rank(fb)))
                first_a,first_b=direct_orders(tracks,old,a,b,fa,fb,olda,oldb)
                require(first_a or first_b,'legal final pair without direct legal intermediate')
                # Recheck the entire affected boundary system for the stated intermediate.
                interim={a:fa,b:oldb} if first_a else {a:olda,b:fb}
                bill_delta(tracks,old,interim)
                counts['first_a_legal']+=first_a;counts['first_b_legal']+=first_b
                rows.append([list(R.basis(fa)),list(R.basis(fb)),list(delta),first_a,first_b])
                if fa!=olda and fb!=oldb:samples.setdefault(a[0]+'-'+b[0],[a,b,list(R.basis(fa)),list(R.basis(fb)),list(delta)])
        predicted=set()
        for da in range(R.rank(la),R.rank(ha)+1):
            for db in range(max(da,R.rank(lb)),R.rank(hb)+1):
                cap=R.rank(R.join(la,ha&lb))
                minimum=R.rank(lb)+max(0,da-cap)
                if minimum<=db:predicted.add((da,db))
                else:false.append([a,b,da,db,minimum,list(R.basis(la)),list(R.basis(ha)),list(R.basis(lb)),list(R.basis(hb))])
        require(dims==predicted,'dimension-feasibility lemma differs from exhaustive subspaces')
        for da,db in dims:
            row=next(x for x in rows if len(x[0])==da and len(x[1])==db)
            cells[tuple(row[2])]+=1
        records.append([a,b,rows])
    require(all(R.all_power_nonnegative(d) for d in singles|joint),'non-improvement sign not certified')
    total=len(addresses)*(len(addresses)-1)//2
    return {'add_addresses':len(addresses),'all_unordered_distinct_pairs':total,
       'coupled_pairs':len(pairs),'uncoupled_pairs_by_independence':total-len(pairs),
       'single_frame_assignments':sum(singles.values()),'pair_frame_assignments':sum(joint.values()),
       'pair_dimension_cells':sum(cells.values()),'sequential':dict(counts),'no_legal_intermediate':0,
       'quotient_dimensions':{str(k):v for k,v in sorted(quotients.items())},
       'single_profiles':profiles(singles),'joint_profiles':profiles(joint),'dimension_profiles':profiles(cells),
       'false_dimension_cells':len(false),'false_dimension_examples':false[:4],
       'intervals':[[list(R.basis(lo)),list(R.basis(hi))] for lo,hi in sorted(intervals)],
       'all_assignment_stream_sha256':digest(records),'whole_word_samples':list(samples.values()),
       'baseline_profile':baseline}
