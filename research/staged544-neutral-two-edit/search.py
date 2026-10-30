#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded neutral-first search on exact PR3734 words.

Chris R / Clear1nsight with substantial OpenAI assistance. Geometry and the
single-gate retiming machinery are reused from credited PR3886, not independent.
"""
import argparse
from bisect import bisect_left
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import time
import types

P = Path(__file__).resolve().parent

def authenticate_sources():
    for row in json.loads((P/'SOURCES.json').read_text())['snapshots']:
        raw=(P/row['local']).read_bytes()
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:
            raise ValueError('source length/SHA256 drift: '+row['local'])
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if blob!=row['git_blob']:raise ValueError('source Git blob drift: '+row['local'])

authenticate_sources()

def module(name, path):
    m = types.ModuleType(name)
    m.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), m.__dict__)
    return m

R = module('retiming_source', P/'vendor/pr3886_retiming.py')
C = module('retained_core', P/'vendor/audit_core.py')
A = module('retained_adapter', P/'vendor/audit_verify.py')
need = R.need

def load(tag):
    return json.loads(gzip.decompress((P/'inputs'/('BORROW-WORD-43'+tag+'.json.gz')).read_bytes()))

def canonical(w):
    return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()

def digest(w):
    return hashlib.sha256(canonical(w)).hexdigest()

def placements(w, max_distance=None, gate_filter=None, sections=('A','B','restore'), trace=None,
               target_cut=None, trusted_reach=False):
    """All cut/dimension prices in the declared class, plus exact frame bounds.

    Like PR3886 this first prices a relaxation. Returned witnesses must separately
    pass frame_bill; a relaxed zero is not admission. One representative subspace
    per dimension is generated here (not exhaustive over subspaces).
    """
    nodes, where, bill = R.tracing(w) if trace is None else trace
    for section in sections:
        gates = w[section]
        for lo, hi in R.segments(w, section):
            occ = {}
            for i in range(lo, hi):
                for r in R.touched(gates[i]):
                    occ.setdefault(r, []).append(i)
            for i in range(lo, hi):
                g = gates[i]
                if g[0] != 'add' or (gate_filter is not None and not gate_filter(section, i, g)):
                    continue
                lower, upper = i, i+1
                if not trusted_reach:
                    while lower > lo and R.crosses(g, gates[lower-1]): lower -= 1
                    while upper < hi and R.crosses(g, gates[upper]): upper += 1
                else:
                    need(target_cut is not None,'trusted reach needs an exact cut')
                    lower,upper=target_cut,target_cut
                if max_distance is not None:
                    lower, upper = max(lower,i-max_distance), min(upper,i+1+max_distance)
                removal = [0]*10
                reduced, entries, exits = {}, {}, {}
                for r in R.touched(g):
                    seq = nodes[r]
                    pos = where[((section,i),r)]
                    _, _, p, u = seq[pos]
                    q = seq[pos+1][3]
                    removal[R.rank(u)-R.rank(p)] -= 1
                    removal[R.rank(q)-R.rank(u)] -= 1
                    removal[R.rank(q)-R.rank(p)] += 1
                    indices = occ[r]
                    reduced[r] = [x for x in indices if x != i]
                    entries[r] = seq[where[((section,indices[0]),r)]][2]
                    last = where[((section,indices[-1]),r)]
                    exits[r] = seq[last+1][3]
                cuts=range(lower,upper+1) if target_cut is None else ([target_cut] if lower<=target_cut<=upper else [])
                for cut in cuts:
                    if cut == i+1: continue
                    boundary = []
                    for r in R.touched(g):
                        indices = reduced[r]
                        j = bisect_left(indices,cut)
                        p = R.span(tuple(gates[indices[j-1]][-1])) if j else entries[r]
                        q = R.span(tuple(gates[indices[j]][-1])) if j<len(indices) else exits[r]
                        boundary.append((p,q))
                    L = R.join(boundary[0][0],boundary[1][0])
                    H = boundary[0][1]&boundary[1][1]
                    if not R.contained(L,H): continue
                    dims = [(R.rank(p),R.rank(q)) for p,q in boundary]
                    # Deterministically extend L to H; relative subspace choices
                    # other than this extension are outside this search alphabet.
                    extension = list(R.basis(L))
                    frames = {len(extension): tuple(extension)}
                    mask = L
                    for v in R.basis(H):
                        if not ((mask>>v)&1):
                            extension.append(v); mask = R.span(tuple(extension))
                            frames[len(extension)] = tuple(extension)
                    for d in range(R.rank(L),R.rank(H)+1):
                        delta = removal.copy()
                        for p,q in dims:
                            delta[q-p] -= 1; delta[d-p] += 1; delta[q-d] += 1
                        delta[0] = 0
                        yield {'section':section,'index':i,'cut':cut,'frame':list(frames[d]),
                               'delta':tuple(delta),'lower_dim':R.rank(L),'upper_dim':R.rank(H),
                               'registers':list(R.touched(g))}

def apply(w, rec):
    return R.apply_move(w,rec['section'],rec['index'],rec['cut'],rec['frame'])

def inspect_first(tag, distance):
    w=load(tag); counts=Counter(); examples=[]; unique=set()
    t=time.monotonic()
    for rec in placements(w,max_distance=distance):
        counts['prices'] += 1
        if any(rec['delta']): continue
        counts['neutral_prices'] += 1
        g=w[rec['section']][rec['index']]
        newindex=rec['cut']-(rec['cut']>rec['index'])
        if newindex==rec['index'] and R.span(tuple(g[-1]))==R.span(tuple(rec['frame'])):
            counts['identity'] += 1; continue
        key=(rec['section'],rec['index'],rec['cut'],R.span(tuple(rec['frame'])))
        if key in unique:continue
        unique.add(key)
        examples.append(rec)
        counts['changed_frame' if R.span(tuple(g[-1]))!=R.span(tuple(rec['frame'])) else 'same_frame'] += 1
        counts['by_'+rec['section']] += 1
        counts['slack_'+str(rec['upper_dim']-rec['lower_dim'])] += 1
    print(json.dumps({'provider':tag,'distance':distance,'counts':counts,'seconds':time.monotonic()-t}),flush=True)
    (P/('FIRST-'+tag+'.json')).write_text(json.dumps(examples,sort_keys=True)+'\n')

def explore(tag, distance=2, changed_only=True, limit=None, write=True, progress=True):
    w=load(tag); original=C.frame_bill(w); counts=Counter(); states=[]; gains=[]
    records=[r for r in placements(w,max_distance=distance) if not any(r['delta'])]
    if changed_only:
        records=[r for r in records if R.span(tuple(w[r['section']][r['index']][-1]))!=R.span(tuple(r['frame']))]
    if limit is not None:records=records[:limit]
    t=time.monotonic()
    for serial,first in enumerate(records):
        new=apply(w,first)
        try:bill,widths,*_=C.frame_bill(new)
        except C.AuditFailure:
            counts['first_boundary_rejected']+=1;continue
        need(bill==original[0] and widths==original[1],'neutral literal bill differs')
        counts['legal_first']+=1
        touched=set(first['registers'])
        scope=lambda sec,i,g:bool(touched.intersection(R.touched(g)))
        delta_counts=Counter(); second_count=0;uncertified=[]
        for second in placements(new,gate_filter=scope):
            delta=second['delta'];delta_counts[delta]+=1;second_count+=1
            if not R.all_power_nonnegative(delta):
                counts['uncertified_prices']+=1
                candidate=apply(new,second)
                try:after,newwidths,*_=C.frame_bill(candidate)
                except C.AuditFailure:
                    counts['second_boundary_rejected']+=1;continue
                need(newwidths==widths,'helper inventory drift')
                actual=tuple([0]+[after.get(k,0)-bill.get(k,0) for k in range(1,10)])
                need(actual==delta,'relaxed vs actual legal bill differs')
                cap=R.caps(delta)
                profitable=all(x<=0 for x in cap) and any(x<0 for x in cap)
                item={'first':first,'second':second,'profile':after,'caps':cap,'all_concave_improvement':profitable}
                uncertified.append(item)
                if profitable:
                    gains.append(item)
                    if progress:print('GAIN',tag,serial,json.dumps(item),flush=True)
                    if write:(P/('GAINS-'+tag+'.json')).write_text(json.dumps(gains,sort_keys=True,indent=2)+'\n')
        counts['second_prices']+=second_count
        states.append({'first':first,'second_prices':second_count,
                       'deltas':[{'delta':d,'count':n,'certificate':R.all_power_nonnegative(d)} for d,n in sorted(delta_counts.items())],
                       'uncertified':uncertified})
        if progress and serial%10==0:print('PROGRESS',tag,serial+1,len(records),dict(counts),'seconds',time.monotonic()-t,flush=True)
    report={'provider':tag,'distance':distance,'changed_frame_only':changed_only,'counts':counts,'states':states,'gains':gains}
    if write:(P/('SEARCH-'+tag+'.json')).write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    if progress:print('DONE',tag,dict(counts),'seconds',time.monotonic()-t,flush=True)
    return report

def adjacent_pairs(tag, write=True, progress=True):
    """Every original adjacent commuting ADD pair; retain both original frames.

    First move is the left ADD rightwards past the right ADD. The second move
    may retime either of those ADDs anywhere in its corridor, with any frame
    dimension. Other gates/frames and all external interfaces remain fixed.
    """
    w=load(tag);baseline=R.tracing(w);original=baseline[2];counts=Counter();states=[];gains=[]
    t=time.monotonic()
    for section in ('A','B','restore'):
        for lo,hi in R.segments(w,section):
            for i in range(lo,hi-1):
                g,h=w[section][i:i+2]
                if g[0]!='add' or h[0]!='add' or not R.crosses(g,h):continue
                counts['commuting_adjacent_pairs']+=1
                if g==h:counts['identical_gates']+=1;continue
                new=w.copy();new[section]=w[section].copy()
                new[section][i:i+2]=[h,g]
                trace=adjacent_trace(w,baseline,section,i)
                if trace is None:
                    counts['frame_rejected']+=1;continue
                need(trace[2]==original,'frame-preserving commuting swap not neutral')
                counts['legal_first']+=1
                filt=lambda sec,j,k:j in (i,i+1)
                dc=Counter();unc=[]
                for second in placements(new,gate_filter=filt,sections=(section,),trace=trace):
                    d=second['delta'];dc[d]+=1;counts['second_prices']+=1
                    if not R.all_power_nonnegative(d):
                        counts['uncertified_prices']+=1
                        cand=apply(new,second)
                        try:after,*_=C.frame_bill(cand)
                        except C.AuditFailure:
                            counts['second_boundary_rejected']+=1;continue
                        need(tuple([0]+[after.get(k,0)-original.get(k,0) for k in range(1,10)])==d,'invoice mismatch')
                        item={'first':{'section':section,'index':i,'cut':i+2,'frame':g[-1]},'second':second,'profile':after,'caps':R.caps(d)}
                        unc.append(item)
                        if all(x<=0 for x in R.caps(d)) and any(x<0 for x in R.caps(d)):
                            gains.append(item)
                            if progress:print('GAIN_PAIR',tag,json.dumps(item),flush=True)
                states.append({'section':section,'left_index':i,'second_prices':sum(dc.values()),
                    'deltas':[{'delta':d,'count':n,'certificate':R.all_power_nonnegative(d)} for d,n in sorted(dc.items())],
                    'uncertified':unc})
                if progress and counts['legal_first']%250==0:print('PAIR_PROGRESS',tag,dict(counts),'seconds',time.monotonic()-t,flush=True)
    result={'provider':tag,'counts':counts,'states':states,'gains':gains}
    if write:(P/('PAIRS-'+tag+'.json')).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    if progress:print('PAIRS_DONE',tag,dict(counts),'seconds',time.monotonic()-t,flush=True)
    return result

def corridor_bounds(w):
    out={}
    for section in ('A','B','restore'):
        gates=w[section]
        for lo,hi in R.segments(w,section):
            for i in range(lo,hi):
                g=gates[i]
                if g[0]!='add':continue
                low,up=i,i+1
                while low>lo and R.crosses(g,gates[low-1]):low-=1
                while up<hi and R.crosses(g,gates[up]):up+=1
                out[section,i]=(low,up)
    return out

def adjacent_trace(w, baseline, section, i):
    """Exact incremental trace of an adjacent frame-preserving ADD swap.

    Shared registers require equal frames in both orders. Exclusive registers
    retain their entire frame sequence; only the one event address is renamed.
    This returns exactly the same nodes, where and bill as a fresh full trace.
    """
    g,h=w[section][i:i+2]
    G,H=set(R.touched(g)),set(R.touched(h))
    if G&H and R.span(tuple(g[-1]))!=R.span(tuple(h[-1])):return None
    old_nodes,old_where,bill=baseline
    nodes=old_nodes.copy();where=old_where.copy()
    for regs,old,new in ((G-H,i,i+1),(H-G,i+1,i)):
        for r in regs:
            pos=where.pop(((section,old),r))
            seq=old_nodes[r].copy()
            addr,kind,p,f=seq[pos]
            seq[pos]=((section,new),kind,p,f)
            nodes[r]=seq;where[((section,new),r)]=pos
    return nodes,where,bill

def adjacent_novel_cuts(tag, write=True, progress=True):
    """Third-gate retimings into the newly exposed middle cut.

    See PROOF.md: every second move of a third gate outside this cut has an
    identical-price baseline counterpart. Moving either swapped gate is covered
    by adjacent_pairs. The caller must replay the baseline obstruction too.
    """
    w=load(tag);baseline=R.tracing(w);original=baseline[2];bounds=corridor_bounds(w)
    counts=Counter();states=[];gains=[];t=time.monotonic()
    for section in ('A','B','restore'):
        for lo,hi in R.segments(w,section):
            for i in range(lo,hi-1):
                g,h=w[section][i:i+2]
                if g[0]!='add' or h[0]!='add' or not R.crosses(g,h):continue
                if g==h:continue
                new=w.copy();new[section]=w[section].copy();new[section][i:i+2]=[h,g]
                trace=adjacent_trace(w,baseline,section,i)
                if trace is None:continue
                need(trace[2]==original,'non-neutral adjacent swap')
                counts['legal_first']+=1
                def allowed(sec,j,k):
                    if not lo<=j<hi or j in (i,i+1) or k[0]!='add':return False
                    low,up=bounds[sec,j]
                    return (up>=i and R.crosses(k,h)) if j<i else (low<=i+2 and R.crosses(k,g))
                dc=Counter();unc=[]
                for second in placements(new,gate_filter=allowed,sections=(section,),trace=trace,
                                         target_cut=i+1,trusted_reach=True):
                    d=second['delta'];dc[d]+=1;counts['second_prices']+=1
                    if not R.all_power_nonnegative(d):
                        counts['uncertified_prices']+=1
                        cand=apply(new,second)
                        try:after,*_=C.frame_bill(cand)
                        except C.AuditFailure:
                            counts['second_boundary_rejected']+=1;continue
                        need(tuple([0]+[after.get(k,0)-original.get(k,0) for k in range(1,10)])==d,'invoice mismatch')
                        item={'first':{'section':section,'index':i,'cut':i+2,'frame':g[-1]},'second':second,'profile':after,'caps':R.caps(d)}
                        unc.append(item)
                        gains.append(item)
                        if progress:print('NOVEL_UNCERTIFIED',tag,json.dumps(item),flush=True)
                states.append({'section':section,'left_index':i,'second_prices':sum(dc.values()),
                    'deltas':[{'delta':d,'count':n,'certificate':R.all_power_nonnegative(d)} for d,n in sorted(dc.items())],
                    'uncertified':unc})
                if progress and counts['legal_first']%500==0:print('NOVEL_PROGRESS',tag,dict(counts),'seconds',time.monotonic()-t,flush=True)
    result={'provider':tag,'counts':counts,'states':states,'gains':gains}
    if write:(P/('NOVEL-'+tag+'.json')).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    if progress:print('NOVEL_DONE',tag,dict(counts),'seconds',time.monotonic()-t,flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--inspect-first',action='store_true');ap.add_argument('--explore',action='store_true');ap.add_argument('--pairs',action='store_true');ap.add_argument('--novel',action='store_true');ap.add_argument('--distance',type=int,default=2)
    ap.add_argument('--all-first',action='store_true');ap.add_argument('--limit',type=int)
    args=ap.parse_args()
    if args.inspect_first:
        for tag in ('base','extra'):inspect_first(tag,args.distance)
    if args.explore:
        for tag in ('base','extra'):explore(tag,args.distance,not args.all_first,args.limit)
    if args.pairs:
        for tag in ('base','extra'):adjacent_pairs(tag)
    if args.novel:
        for tag in ('base','extra'):adjacent_novel_cuts(tag)
