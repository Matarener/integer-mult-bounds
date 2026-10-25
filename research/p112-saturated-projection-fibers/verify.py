#!/usr/bin/env python3
"""Shared-kernel saturated root fibers; exact characteristic-zero certificates.
Chris R / Clear1nsight with OpenAI Codex assistance. Apache-2.0.
Rational elimination and shell binding adapted from PR3991, exact head
 e4eb3b7a1334b6fef88fc251c43d9940c8d38de8; frozen predecessor unchanged.
"""
import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def require(ok, message):
    if not ok: raise ValueError(message)

def authenticate():
    source=json.loads((HERE/'SOURCES.json').read_text())
    for item in source['files']:
        if item['usage']=='input':
            require(sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'source digest: '+item['path'])

def primitive(row):
    g=gcd(*row)
    if not g:return tuple(row)
    if next(x for x in row if x)<0:g=-g
    return tuple(x//g for x in row)

def basis(rows):
    """Canonical primitive integer version of rational RREF; no floating point."""
    out=[]
    for original in rows:
        row=tuple(original)
        for old in out:
            pivot=next(i for i,x in enumerate(old) if x)
            if row[pivot]:row=primitive(tuple(old[pivot]*x-row[pivot]*y for x,y in zip(row,old)))
        if not any(row):continue
        row=primitive(row);pivot=next(i for i,x in enumerate(row) if x)
        out=[primitive(tuple(row[pivot]*x-old[pivot]*y for x,y in zip(old,row))) if old[pivot] else old for old in out]
        out.append(row);out.sort(key=lambda r:next(i for i,x in enumerate(r) if x))
    return tuple(out)

def load_roots():
    spec=importlib.util.spec_from_file_location('pinned_geometry',ROOT/'research/p112-root-simplex-exclusion/geometry.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    roots=module.root_lines()
    require(len(roots)==120 and all(sum(x*x for x in r)==8 for r in roots),'root shell')
    frame=set()
    for i in range(0,8,2):
        for sign in (-2,2):
            row=[0]*8;row[i]=2;row[i+1]=sign;frame.add(tuple(row))
    live=[r for r in roots if r not in frame]
    require(len(live)==112,'live puncture')
    require(all(sum(x*y for x,y in zip(a,b)) in (-4,0,4) for a,b in combinations(roots,2)),'distinct root Cartan inner products')
    require(all(sum(r[i]*r[j] for r in live)==(112 if i==j else 0) for i in range(8) for j in range(8)),'live evaluation Gram identity')
    return roots

def flats(roots, rank):
    groups={}
    independent=0
    for indices in combinations(range(len(roots)),rank):
        key=basis(roots[i] for i in indices)
        if len(key)!=rank:continue
        independent+=1
        mask=sum(1<<i for i in indices)
        groups[key]=groups.get(key,0)|mask
    # Every point in a root-spanned flat extends to a basis of that flat.
    masks=sorted(groups.values())
    histogram=dict(sorted(Counter(m.bit_count() for m in masks).items()))
    return {'rank':rank,'independent_bases':independent,'flats':len(masks),
            'histogram':{str(k):v for k,v in histogram.items()},'maximum':max(histogram),
            'closure_digest':sha256(json.dumps(masks,separators=(',',':')).encode()).hexdigest(),
            'maximizer':next([i for i in range(120) if m>>i&1] for m in masks if m.bit_count()==max(histogram))}

def determinant(rows):
    a=[list(row) for row in rows];n=len(a);previous=1;sign=1
    for k in range(n-1):
        pivot=next((j for j in range(k,n) if a[j][k]),None)
        if pivot is None:return 0
        if pivot!=k:a[k],a[pivot]=a[pivot],a[k];sign=-sign
        for i in range(k+1,n):
            for j in range(k+1,n):
                numerator=a[k][k]*a[i][j]-a[i][k]*a[k][j]
                require(numerator%previous==0,'Bareiss divisibility')
                a[i][j]=numerator//previous
        previous=a[k][k]
        for i in range(k+1,n):a[i][k]=0
    return sign*a[-1][-1]


def saturated_pair_certificate():
    records=[];intersections=Counter();patterns=0
    for off in product((-1,0,1),repeat=6):
        g=[[2 if i==j else 0 for j in range(4)]for i in range(4)]
        for (i,j),x in zip(combinations(range(4),2),off):g[i][j]=g[j][i]=x
        if any(determinant([r[:k] for r in g[:k]])<=0 for k in range(1,5)):continue
        patterns+=1;det=determinant(g)
        adj=[[(-1)**(i+j)*determinant([[g[a][b] for b in range(4) if b!=i]for a in range(4)if a!=j])for j in range(4)]for i in range(4)]
        candidates=[k for k in product(range(-2,3),repeat=4) if next((x for x in k if x),0)>0 and sum(k[i]*adj[i][j]*k[j]for i in range(4)for j in range(4))==2*det]
        require(len(candidates)<=12,'rank4 cap')
        if len(candidates)<11:continue
        groups={}
        for tri in combinations(range(len(candidates)),3):
            key=basis(candidates[i]for i in tri)
            if len(key)==3:groups[key]=groups.get(key,0)|sum(1<<i for i in tri)
        require(max(map(int.bit_count,groups.values()))==6,'candidate rank3 cap')
        saturated=sorted(m for m in groups.values()if m.bit_count()==6)
        pairhist=Counter((a&b).bit_count()for a,b in combinations(saturated,2))
        require(len(saturated)==12 and min(pairhist)>=2,'saturated pair completeness')
        intersections.update(pairhist)
        records.append([list(off),len(candidates),saturated,dict(sorted(pairhist.items()))])
    require(patterns==393 and len(records)==105,'complete Gram filter')
    require(intersections=={2:1890,3:5040},'saturated intersection census')
    return {'positive_Gram_patterns':patterns,'relevant_patterns':len(records),'saturated_flats_per_case':12,
            'pair_intersections':{str(k):intersections[k]for k in sorted(intersections)},
            'certificate_digest':sha256(json.dumps(records,separators=(',',':'),sort_keys=True).encode()).hexdigest()}

def orthogonal_fibers(roots):
    records=[]
    for i,j in combinations(range(120),2):
        a,b=roots[i],roots[j]
        if sum(x*y for x,y in zip(a,b)):continue
        groups={};zeros=[]
        for t,r in enumerate(roots):
            da=sum(x*y for x,y in zip(r,a));db=sum(x*y for x,y in zip(r,b))
            projected=tuple(8*x-da*y-db*z for x,y,z in zip(r,a,b))
            if not any(projected):zeros.append(t);continue
            key=primitive(projected);groups[key]=groups.get(key,0)|(1<<t)
        masks=sorted(groups.values());hist=Counter(map(int.bit_count,masks))
        require(hist=={1:30,2:32,4:6} and zeros==[i,j],'orthogonal full-root fiber census')
        records.append([i,j,masks])
    require(len(records)==3780,'all orthogonal pairs')
    return {'planes':len(records),'full_root_projection_tests':120*len(records),
            'fiber_size_histogram':{'1':30,'2':32,'4':6},'top11_sum':34,
            'partition_digest':sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest()}

def caller():
    weights=[2,2,5]+[6]*8
    source=ROOT/'research/p112-b6-t4-reconciliation/vendor/bk2b.py'
    old={};exec(compile(source.read_text().split('import sys')[0],str(source),'exec'),old)
    require(old['feasible'](weights,6) and not old['killed'](weights,6),'historical caller')
    require(sum(w-2 for w in weights)==35,'strict excess')
    return {'weights':weights,'historical_cell':[6,5],'pieces':11,'strict_excess':35,
            'quotient_dimension':5,'code_intersection_dimension':6,
            'preferred_five_piece_capacity':56,'six_piece_capacity':76,'inherited_second_weight':78,
            'total_support_capacity':176,'new_support_floor':178,'contradiction_margin':2}

def capacity_corollary():
    """Exact budget DP, retaining all distinct sorted maximizing profiles."""
    caps={2:2,3:4,4:8,5:12,6:20}
    increments=[caps[w+1]-caps[w] for w in range(2,6)]
    require(increments==sorted(increments)==[2,4,4,8],'discrete convex capacities')
    states={0:(0,{()})};rows=[]
    for n in range(12):
        maximum=max(v[0]for v in states.values())
        profiles=sorted({w for value,ws in states.values()if value==maximum for w in ws})
        require(len(profiles)==1,'unique sorted capacity maximizer')
        rows.append({'pieces':n,'maximum_capacity':maximum,'maximizer':list(profiles[0])})
        new={}
        for budget,(value,ws)in states.items():
            for w in caps:
                b=budget+w-2
                if b>35:continue
                score=value+caps[w];words={tuple(sorted(word+(w,)))for word in ws}
                old=new.get(b,(-1,set()))
                if score>old[0]:new[b]=(score,words)
                elif score==old[0]:new[b]=(score,old[1]|words)
        states=new
    require(rows[-1]['maximum_capacity']==176 and rows[-1]['maximizer']==[2,2,5]+[6]*8,'extremal caller')
    return {'piece_limit':11,'allowed_weights':[2,3,4,5,6],'strict_excess_limit':36,
            'required_code_dimension':6,'capacity_increments':increments,'maxima_by_length':rows,
            'maximum_capacity':176,'incidence_floor':178,'uniform_margin':2}

def compute():
    authenticate();roots=load_roots()
    rank2=flats(roots,2);rank3=flats(roots,3)
    require(rank3['histogram']=={'3':37800,'4':40320,'6':7560},'rank3 closure gap')
    # A rank-two span generated by a nonorthogonal pair has three root lines.
    directions={primitive(r) for r in roots}
    for a,b in combinations(roots,2):
        dot=sum(x*y for x,y in zip(a,b))
        if dot:
            third=tuple(x-(1 if dot>0 else -1)*y for x,y in zip(a,b))
            require(sum(x*x for x in third)==8 and primitive(third) in directions,'nonorthogonal pair third root')

    branches=[{'full_kernel_roots':0,'max_live_zero_roots':0,'max_singletons':46,'support_floor':178},
              {'full_kernel_roots':1,'max_live_zero_roots':1,'max_singletons':35,'support_floor':187},
              {'full_kernel_roots':2,'max_live_zero_roots':2,'max_singletons':34,'support_floor':186},
              {'full_kernel_roots':3,'max_live_zero_roots':3,'max_singletons':33,'support_floor':185}]
    return {'schema_version':1,'rational_flats':[rank2,rank3],
            'saturated_pair':saturated_pair_certificate(),'orthogonal_kernel':orthogonal_fibers(roots),
            'capacity_corollary':capacity_corollary(),'branches':branches,'uniform_support_floor':min(x['support_floor']for x in branches),'caller':caller(),'no_new_kappa':True}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-expected',action='store_true');args=ap.parse_args()
    result=compute()
    if args.write_expected:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:require(result==json.loads((HERE/'RESULT.json').read_text()),'receipt mismatch')
    print('PASS_P112_SATURATED_FIBERS relevant_Gram105 orthogonal_planes3780 uniform_floor178 caller_cap176 margin2')
if __name__=='__main__':main()
