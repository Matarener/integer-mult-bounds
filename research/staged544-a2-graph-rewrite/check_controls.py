#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite-subspace and polynomial-identity checks; all failures explicit."""
import json,itertools,time
from collections import Counter
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import types
P=Path(__file__).resolve().parent
V=types.ModuleType('entry');V.__file__=str(P/'verify.py');exec(compile((P/'verify.py').read_bytes(),str(P/'verify.py'),'exec'),V.__dict__)
need=V.need

def pointset(vectors):
    out={0}
    for v in vectors:out|={x^v for x in tuple(out)}
    return frozenset(out)

def points(mask):return frozenset(x for x in range(512) if mask>>x&1)

def dim(space):return len(space).bit_length()-1

@lru_cache(None)
def independent_frames(low,high):
    if not low<=high:return ()
    # Form quotient representatives without calling retained span/join/basis.
    reps={min(v^u for u in low) for v in high};nonzero=sorted(reps-{0})
    need(len(nonzero)<=15,'independent quotient cap')
    out=set()
    for bits in range(1<<len(nonzero)):
        generators=[nonzero[i] for i in range(len(nonzero)) if bits>>i&1]
        quotient=pointset(generators)
        out.add(frozenset(x^y for x in quotient for y in low))
    return tuple(sorted(out,key=lambda x:tuple(sorted(x))))

def plus(a,b):
    out=a.copy()
    for k,v in b.items():out[k]=out.get(k,0)+v
    return {k:v for k,v in out.items() if v}

def times(a,b):
    out={}
    for (i,j),v in a.items():
        for (k,l),w in b.items():out[i+k,j+l]=out.get((i+k,j+l),0)+v*w
    return {k:v for k,v in out.items() if v}

def poly_matrix(gates):
    rows=[[{(0,0):int(i==j)} if i==j else {} for j in range(3)] for i in range(3)]
    for t,s,c in gates:rows[t]=[plus(x,times(c,y)) for x,y in zip(rows[t],rows[s])]
    return rows

def group_controls():
    a={(1,0):1};b={(0,1):1};ab={(1,1):1};n_ab={(1,1):-1};checks=0
    for i,j,k in itertools.permutations(range(3)):
        for orientation in (0,1):
            g=(i,j,a) if not orientation else(j,k,a)
            h=(j,k,b) if not orientation else(i,j,b)
            central=(i,k,n_ab if not orientation else ab)
            before=poly_matrix([g,h])
            for pos in (0,1,2):
                after=[h,g];after.insert(pos,central)
                need(before==poly_matrix(after),'symbolic A2 identity')
                bad=deepcopy(after);bad[pos]=(i,k,{power:-v for power,v in central[2].items()})
                need(before!=poly_matrix(bad),'wrong sign not rejected')
                need(before!=poly_matrix([h,g]),'missing central gate not rejected')
                bad[pos]=(i,k,plus(a,b));need(before!=poly_matrix(bad),'wrong product not rejected');checks+=1
    return checks

def expect(fn):
    try:fn()
    except (ValueError,ZeroDivisionError):return
    raise ValueError('expected rejection absent')

def main():
    started=time.monotonic();S,C,A=V.setup();identities=group_controls();intervals=0;flags=0
    for tag in ('base','extra'):
        w=V.load(tag);receipt=json.loads((P/f'RESULT-{tag}.json').read_text());data=receipt['census']
        # Independent quotient-subset closure is exhaustive, not a random check.
        for low,high in data['intervals']+data['contractions']['intervals']:
            l,h=int(low),int(high);actual={points(x) for x in S.frames(l,h)}
            need(actual==set(independent_frames(points(l),points(h))),'subspace enumeration mismatch');intervals+=1
        # Recompute every retained local rank invoice from independent point sets.
        _,_,chain,start,end=C.frame_bill(w)
        expected=Counter()
        for row in data['records']+data['contractions']['records']:
            sec,i=row['section'],row['index'];old_length=3 if len(row['gates'])==2 else 2;block=w[sec][i:i+old_length];regs={r for g in block for r in g[1:3]};bounds={};old=Counter()
            for r in regs:
                seq=[event for event in chain[r] if event[0][0]!='centre'];inds=[j for j,(where,d,u) in enumerate(seq) if where in tuple((sec,j) for j in range(i,i+old_length))]
                need(inds,'missing independent event');lo,hi=min(inds),max(inds)
                before=seq[lo-1][2] if lo else start[r]
                # Native entry is an exact check; the recorded warp row is its
                # output map, not a paid successor climb. Centre descent is
                # temporary service, filtered above, never persistent state.
                after=seq[hi][2] if type(seq[hi+1][1]) is not int else seq[hi+1][2]
                bounds[r]=(points(before),points(after))
                for _,d,u in seq[lo:hi+1]:need(type(d)is int,'crossed native boundary');old[d]+=1
                old[dim(points(after))-dim(points(seq[hi][2]))]+=1
            cur={r:x for r,(x,y) in bounds.items()};new=Counter()
            for gate in row['gates']:
                fr=pointset(gate[-1])
                for r in gate[1:3]:
                    need(cur[r]<=fr<=bounds[r][1],'independent frame failure');new[dim(fr)-dim(cur[r])]+=1;cur[r]=fr
            for r,(x,y) in bounds.items():new[dim(y)-dim(cur[r])]+=1
            delta=[0]+[new[r]-old[r] for r in range(1,10)];need(delta==row['delta'],'independent invoice mismatch');flags+=1
            if old_length==2:expected[tuple(delta)]+=1
        need([{'delta':list(d),'count':n} for d,n in sorted(expected.items())]==data['profiles'],'histogram mismatch')
        # Independently enumerate graph sites using the dependency matrix support.
        sites=[]
        for sec in ('A','B','restore'):
            for lo,hi in S.R.segments(w,sec):
                for i in range(lo,hi-1):
                    g,h=w[sec][i:i+2]
                    if g[0]!='add' or h[0]!='add':continue
                    t,s=g[1:3];u,v=h[1:3]
                    if len({t,s,u,v})==3 and ((s==u) != (v==t)):sites.append([sec,i])
        need(sites==data['motifs'],'motif completeness')
        # Separately assemble the complete Cartesian flag state sets with
        # frozenset geometry; production DFS/deduplication is not reused.
        nodes,where,_=S.R.tracing(w);all_flags=set()
        for sec,i in sites:
            bounds,_=S.boundary(nodes,where,w,sec,i)
            bounds={r:(points(a),points(b)) for r,(a,b) in bounds.items()}
            for pos in (0,1,2):
                gates=S.expand(*w[sec][i:i+2],pos)
                states=[({r:a for r,(a,b) in bounds.items()},())]
                for gate in gates:
                    next_states=[];a,b=gate[1:3]
                    for cur,chosen in states:
                        lower=pointset(cur[a]|cur[b]);upper=bounds[a][1]&bounds[b][1]
                        for frame in independent_frames(lower,upper):
                            new=cur.copy();new[a]=new[b]=frame
                            next_states.append((new,chosen+(tuple(sorted(frame)),)))
                    states=next_states
                all_flags.update((sec,i,pos,chosen) for cur,chosen in states)
        retained={(r['section'],r['index'],r['central_position'],tuple(tuple(sorted(pointset(g[-1]))) for g in r['gates'])) for r in data['records']}
        retained.update((sec,i,pos,tuple(tuple(sorted(pointset(f))) for f in frames)) for sec,i,pos,frames,error in data['fixed_boundary_rejections'])
        need(all_flags==retained,'complete independent flag set mismatch')
        row=data['records'][0];m=S.apply(w,row['section'],row['index'],row['gates'],C)
        bad=deepcopy(m);j=next(j for j,g in enumerate(bad['cleanup']) if g[0]=='add');bad['cleanup'].pop(j)
        need(not C.same_cleanup(C.derive_cleanup(bad),bad['cleanup']),'cleanup deletion undetected')
        expect(lambda:A.semantics(C,bad))
        bad=deepcopy(row['gates']);bad[0][-1]=[512];expect(lambda:S.invoice({r:(1,(1<<512)-1) for r in {r for g in bad for r in g[1:3]}},bad))
        expect(lambda:S.expand(['scale',1,1,1,[]],['add',2,1,1,1,[]],0))
        expect(lambda:S.expand(['add',1,2,1,1,[]],['add',2,1,1,1,[]],0))
    # The actual production sign mutation must break a source identity.
    mutated=types.ModuleType('wrong_production_sign');mutated.__file__=str(P/'search.py')
    source=(P/'search.py').read_text();need('h[2],-a*b' in source,'mutation anchor')
    exec(compile(source.replace('h[2],-a*b','h[2],a*b'),str(P/'search.py'),'exec'),mutated.__dict__)
    g=['add',0,1,2,1,[]];h=['add',1,2,3,1,[]]
    need(mutated.matrix([g,h])!=mutated.matrix(mutated.expand(g,h,1)),'production sign mutation survived')
    sources=json.loads((P/'SOURCES.json').read_text())['snapshots'];row=sources[0];raw=(P/row['local']).read_bytes();expect(lambda:V.authenticate(raw[:-1]+bytes([raw[-1]^1]),row))
    print('PASS_A2_CONTROLS',json.dumps({'symbolic_identities':identities,'wrong_sign_missing_gate_wrong_product_controls':3*identities,'independent_frame_intervals':intervals,'independent_legal_invoices':flags,'seconds':round(time.monotonic()-started,3)},sort_keys=True))
if __name__=='__main__':main()
