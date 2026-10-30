#!/usr/bin/env python3
"""Check the address theorem, return map and source-bound volume formula."""
from collections import Counter,defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import importlib.util
import json
from pathlib import Path
import sys

P=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            need(sha256((P.parent.parent/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash')


def rejection(name,fn):
    try: fn()
    except ValueError: return name
    raise ValueError('accepted mutation: '+name)


def coordinates(row,L,H,D):
    pairs=[]
    for _ in range(D):
        row,d=divmod(row,L*H);pairs.append(divmod(d,H))
    return row,pairs


def reference(row,L,H,D,j):
    tail,pairs=coordinates(row,L,H,D)
    # Build from the mathematical product, with every consumed high field
    # before the unused suffix. This does not call split or join.
    unused=tail
    for low,high in reversed(pairs[j:]): unused=unused*(L*H)+low*H+high
    value=unused
    for _,high in reversed(pairs[:j]): value=value*H+high
    return tuple(x[0] for x in pairs[:j]),value


def complete_case(Layout,L,H,D,T):
    layout=Layout(L,H,D,T);digest=sha256();groups=[defaultdict(list) for _ in range(D+1)]
    for root in range(layout.rows):
        for j in range(D+1):
            prefix,index=layout.descend(root,j)
            need((prefix,index)==reference(root,L,H,D,j),'independent coordinate product')
            need(layout.return_address(prefix,index)==root,'exact arbitrary-data return address')
            groups[j][prefix].append(index)
            digest.update(f'{root}:{j}:{prefix}:{index};'.encode())
    for j,packets in enumerate(groups):
        need(len(packets)==L**j,'all low prefixes')
        expected=list(range(layout.rows//L**j))
        for indices in packets.values(): need(sorted(indices)==expected,'complete child address interval')
    # Run a complete descent and return with a value which depends on all
    # exposed ancestors. Every root label is independent payload data.
    payload={():list(range(layout.rows))}
    for j in range(D):
        children={}
        for prefix,values in payload.items():
            banks=[[None]*(len(values)//L) for _ in range(L)]
            for i,value in enumerate(values):
                low,target=layout.split(i,j);need(banks[low][target] is None,'one destination');banks[low][target]=value
            for low,bank in enumerate(banks): children[prefix+(low,)]=bank
        payload=children
    for prefix,values in payload.items():
        for i,value in enumerate(values):
            values[i]=3*value+sum((k+1)*(1+h) for k,h in enumerate(layout.ancestors(i,D)))
    for j in reversed(range(D)):
        parents={}
        for prefix,values in payload.items():
            bank=parents.setdefault(prefix[:-1],[None]*(len(values)*L))
            for i,value in enumerate(values):bank[layout.join(prefix[-1],i,j)]=value
        payload=parents
    for root,value in enumerate(payload[()]):
        _,pairs=coordinates(root,L,H,D)
        need(value==3*root+sum((k+1)*(1+h) for k,(_,h) in enumerate(pairs)),'literal child return values')
    return dict(low=L,high=H,depth=D,slabs=T,rows=layout.rows,all_depth_addresses=layout.rows*(D+1),sha256=digest.hexdigest())


def matrix_product(a,b,m):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2))%m for i in range(2) for j in range(2))


def cover_route(Layout):
    q,w,B=3,2,2;mod=q**w
    lows=[a for a in product(range(q),repeat=4) if (a[0]*a[3]-a[1]*a[2])%q]
    highs=list(product(range(q**(w-1)),repeat=4));li={a:i for i,a in enumerate(lows)};hi={a:i for i,a in enumerate(highs)}
    H=len(highs);L=B*len(lows);perm=[]
    S=(1,1,0,1);inverse=(1,-1,0,1)
    for role in range(B):
        for low in lows:
            for high in highs:
                g=tuple(a+q*b for a,b in zip(low,high));out=matrix_product(g,S,mod)
                need(matrix_product(out,inverse,mod)==g,'whole local-ring inverse')
                lo=tuple(v%q for v in out);hh=tuple(v//q for v in out)
                perm.append((role*len(lows)+li[lo])*H+hi[hh])
    need(set(perm)==set(range(L*H)),'whole GL cover route')
    # At level one, an ancestor high field remains a spectator. Test every
    # actual current cover row and four different spectator/stock choices.
    layout=Layout(L,H,3);checks=0;inv=[0]*len(perm)
    for i,v in enumerate(perm):inv[v]=i
    # Validate once, then apply the literal permutation formula. Revalidating
    # the whole table at every address is not part of the finite proof.
    for oldhigh,tail in [(0,0),(H-1,0),(1,1),(H-1,L*H-1)]:
        for d,out in enumerate(perm):
            parent=(tail*L*H+d)*H+oldhigh
            routed=(tail*L*H+out)*H+oldhigh
            need(routed%H==oldhigh and routed//(H*L*H)==tail,'ancestor and unused stock fixed')
            restored=(tail*L*H+inv[out])*H+oldhigh
            need(restored==parent,'full route inverse, not only low residue')
            checks+=1
    for i in [0,H-1,L*H-1,123456]:
        need(layout.route(i,1,perm)==(i//(H*L*H)*L*H+perm[(i//H)%(L*H)])*H+i%H,'API route')
    return dict(q=q,w=w,dimension=2,productive_roles=B,low_types=L,high_matrices=H,cover_rows=len(perm),spectator_route_checks=checks)


def calculate():
    authenticate();spec=importlib.util.spec_from_file_location('batch_layout',P/'layout.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);Layout=m.Layout
    cases=[(2,1,5,2),(4,3,3,1),(6,2,4,1),(2,9,3,1),(3,4,3,2),(4,3,3,2),(2,27,2,1),(96,81,1,1)]
    results=[complete_case(Layout,*x) for x in cases];route=cover_route(Layout)
    # A child weight can read every exposed parent high field. Varying its
    # new fresh low/high pair leaves that weight unchanged.
    layout=Layout(4,3,3);weights=0
    for ancestor in range(3):
        vals=set()
        for low,high,tail in product(range(4),range(3),range(12)):
            i=((tail*4+low)*3+high)*3+ancestor
            vals.add(1+3*sum(layout.ancestors(i,1)));weights+=1
        need(vals=={1+3*ancestor},'fresh child weight independence')
    controls=[]
    wrong=layout.rows//(layout.low*layout.high)
    actual=layout.rows//layout.low
    controls.append(rejection('full-cover child volume drops high matrices',lambda:need(wrong==actual,'child volume')))
    # Two different parent high matrices collide if that ancestor is dropped.
    a,b=layout.split(0,0)[1],layout.split(1,0)[1]
    controls.append(rejection('drop ancestor high on child return',lambda:need(a//3!=b//3,'lost independent input')))
    fresh=[layout.split(i,1)[0] for i in range(layout.rows//4) if i%3==1]
    controls.append(rejection('reuse ancestor as fresh low field',lambda:need(Counter([1]*len(fresh))==Counter(fresh),'fresh cylinder')))
    # Pruning padded rows before execution loses a complete batch.
    Q=layout.rows-1;counts=Counter(layout.split(i,0)[0] for i in range(Q))
    controls.append(rejection('prune dummy rows during recursion',lambda:need(len(set(counts.values()))==1,'unequal fibers')))
    controls.append(rejection('omit inverse return route',lambda:need(matrix_product((1,0,0,1),(1,1,0,1),9)==(1,0,0,1),'changed address')))
    controls.append(rejection('allow weight to read fresh high field',lambda:need(len({1+3*h for h in range(3)})==1,'fresh-dependent weight')))
    controls.append(rejection('charge private banks as productive width',lambda:need(F(4,6)==1,'productive denominator')))
    sums=[]
    for L in [2,4,96]:
        for D in [0,1,2,8,40]:
            value=sum((F(1,L**j) for j in range(D+1)),F(0))
            need(value==F(L,L-1)*(1-F(1,L**(D+1))),'exact geometric sum')
            need(value<F(L,L-1),'active-chain bound')
            sums.append([L,D,str(value)])
    return dict(cases=results,cover_route=route,weight_checks=weights,geometric_checks=sums,
        rejected_controls=controls,source_pr=5814,source_head='68614094a31bd483083cfaf1f8735ceb6aec5224',
        conclusion='Whole-high batches contract volume by fixed W0; fresh stock contracts by W0*H.',
        limitations=['Reference addresses, not a physical tape dispatcher.','Old atom-interchange and local macro space remain premises.','Complete native/compiler/precision/analytic and owned-erasure admission remain open.'])


if __name__=='__main__':
    result=calculate()
    if sys.argv[1:]==['--write']:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(not sys.argv[1:],'unknown argument');need(result==json.loads((P/'RESULT.json').read_text()),'recorded result')
    print('PASS_DELAYED_COVER_BATCH_ALLOCATION')
    print(json.dumps({'all_depth_addresses':sum(r['all_depth_addresses'] for r in result['cases']),'controls':len(result['rejected_controls']),'route':result['cover_route']}))
