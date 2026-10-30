#!/usr/bin/env python3
"""Exact rational low-rank root flats and one literal C5 incidence application.
Chris R / Clear1nsight with OpenAI Codex assistance. Apache-2.0.
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
CAP={2:2,3:4,4:8,5:12,6:20,7:36}

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

def old_filter(weights,b):
    if sum(w-2 for w in weights)>=6*b:return False
    d=[0,53,78,92,100,106,109,111,112]
    for level in range(1,b+1):
        small=weights[:len(weights)-b+level]
        total=sum(CAP[w] for w in small)
        tight=sum(32 if w==7 else CAP[w] for w in small)
        if level==1 and tight<53 and total<73:return False
        if level==2 and tight<78 and total<82:return False
        if level>=3 and total<d[level]:return False
    small=weights[:len(weights)-b]
    if sum(CAP[w] for w in small)>=53:return True
    if sum(small)<=7:return False
    for mask in range(1<<len(small)):
        if sum(w for i,w in enumerate(small) if mask>>i&1)<=6 and sum(w for i,w in enumerate(small) if not(mask>>i&1))<=6:return False
    return True

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

def rank4_gram():
    cases=[]
    for off in product((-1,0,1),repeat=6):
        g=[[2 if i==j else 0 for j in range(4)] for i in range(4)]
        for (i,j),x in zip(combinations(range(4),2),off):g[i][j]=g[j][i]=x
        if any(determinant([r[:k] for r in g[:k]])<=0 for k in range(1,5)):continue
        det=determinant(g)
        adj=[[(-1)**(i+j)*determinant([[g[a][b] for b in range(4) if b!=i] for a in range(4) if a!=j]) for j in range(4)] for i in range(4)]
        count=sum(sum(k[i]*adj[i][j]*k[j] for i in range(4) for j in range(4))==2*det for k in product(range(-2,3),repeat=4))
        cases.append([list(off),det,count])
    histogram=Counter(c[2] for c in cases)
    require(len(cases)==393 and max(histogram)==24,'rank4 Gram target cap')
    return {'patterns':len(cases),'candidate_vectors':len(cases)*625,'signed_target_histogram':{str(k):histogram[k] for k in sorted(histogram)},'maximum_lines':max(histogram)//2,'case_digest':sha256(json.dumps(cases,separators=(',',':')).encode()).hexdigest()}

def caller(weights):
    require(old_filter(weights,6),'not an original historical survivor')
    total=sum(CAP[w] for w in weights);n=len(weights)
    require(total<164,'no strict incidence contradiction')
    return {'weights':weights,'b':6,'t':5,'n':n,'strict_excess':sum(w-2 for w in weights),
            'quotient_dimension':5,'code_intersection_dimension':6,
            'total_support_capacity':total,'singleton_support_floor':224-6*n,'new_support_floor':164,
            'contradiction_margin':164-total,
            'six_rank5_capacity':72,'inherited_second_weight':78,
            'preferred_five_piece_capacity':60}

def compute():
    authenticate();roots=load_roots()
    pair=flats(roots,2);triple=flats(roots,3)
    require(pair['maximum']==3 and triple['maximum']==6,'low rank root capacities')
    return {'schema_version':1,'model':'full120 E8 root lines; fixed112 puncture',
            'rational_flats':[pair,triple],'rank4_gram':rank4_gram(),
            'theorem':'M >= ceil(((2*n-3)*(112-z)-choose(n,2)*(12-z))/(n-2)); at n=11, M>=164+4*z',
            'callers':[caller([5]*10+[7]),caller([5]*9+[6,6])],
            'no_new_kappa':True}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-expected',action='store_true');args=ap.parse_args()
    result=compute()
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write_expected:(HERE/'RESULT.json').write_text(encoded)
    else:require(result==json.loads((HERE/'RESULT.json').read_text()),'receipt mismatch')
    print('PASS_P112_SIX_DIMENSIONAL_INCIDENCE root_rank3_cap=6 root_rank4_cap=12 support_floor164 caller_margins8,16 no_new_kappa')
if __name__=='__main__':main()
