#!/usr/bin/env python3
"""Exact phase-tag section and signed-word certificates. Apache-2.0.

ToikY with substantial OpenAI Codex assistance. No predecessor code imported.
"""
from __future__ import annotations
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PINS={
 'PROOF.md':'111e31099e97d4f9a376d77ca1159d6ba89e2a6b7dd36d8386888c9b91639e25',
 'README.md':'06163fba5ef8fcca2a6940313ffb506320206ce47d2cf1c4eceb8fd0d8039bfd',
 'RECIPES.json':'64b85f6aef485026eebaec7acddb41999f57e074b0dfde8077b6543700cd684b',
 'exact_phase.py':'e3d76b3373ff40a83a4b212b3fe1c0b431b3cfdc807da601d6e7f273c02c6d30',
 'SOURCE-CREDITS.md':'d4a13d8b8ed9cdb594f00efb3d1a336e09d934423330f02a1514308a720c278b',
 'NOTICE-PR3945.md':'6881464d7731757b63275f056cb9ef8406db04e76c73093d3e5b418529a879cc'}

def need(ok,message):
    if not ok:raise ValueError(message)

def unique(pairs):
    result={}
    for k,v in pairs:
        need(k not in result,'duplicate JSON key');result[k]=v
    return result

def load(path):return json.loads(path.read_bytes(),object_pairs_hook=unique)

def authenticate():
    for name,digest in PINS.items():
        p=HERE/'source'/name
        need(not p.is_symlink(),'source symlink')
        need(hashlib.sha256(p.read_bytes()).hexdigest()==digest,'source bytes: '+name)

def _apply(g,x):
    out=0
    while x:
        bit=x&-x;out^=g[bit.bit_length()-1];x^=bit
    return out

@lru_cache(maxsize=None)
def _inverse(g):
    n=len(g)
    rows=[sum(((g[j]>>i)&1)<<j for j in range(n))|(1<<(n+i)) for i in range(n)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if (rows[i]>>j)&1),None)
        need(pivot is not None,'singular binary map')
        rows[j],rows[pivot]=rows[pivot],rows[j]
        for i in range(n):
            if i!=j and (rows[i]>>j)&1:rows[i]^=rows[j]
    return tuple(sum(((rows[i]>>(n+j))&1)<<i for i in range(n)) for j in range(n))

def normal(g):
    need(isinstance(g,(tuple,list)) and len(g)>0,'nonempty binary columns')
    g=tuple(g);n=len(g)
    need(all(type(x) is int and 0<=x<1<<n for x in g),'typed column domain')
    _inverse(g)
    return g

def inverse(g):return _inverse(normal(g))

def apply(g,x):
    g=normal(g);need(type(x) is int and 0<=x<1<<len(g),'typed input domain')
    return _apply(g,x)

def compose(h,g):
    h,g=normal(h),normal(g);need(len(h)==len(g),'map width')
    return tuple(_apply(h,x) for x in g)

def pullback(g,t):
    g=normal(g);need(type(t) is int and 0<=t<1<<len(g),'typed tag domain')
    return sum(((x&t).bit_count()%2)<<j for j,x in enumerate(g))

@lru_cache(maxsize=None)
def quadratic(g):
    inv=_inverse(g);n=len(g)
    return tuple(sum((int(i==j)^((inv[i]&inv[j]).bit_count()%2))<<j
                     for j in range(n)) for i in range(n))

def _q(rows,y):
    ans=0
    for i,row in enumerate(rows):
        if (y>>i)&1:
            ans+=((row>>i)&1)+2*((row&y&~((1<<(i+1))-1)).bit_count())
    return ans%4

def canonical_phase(g,x):
    g=normal(g);y=apply(g,x)
    return _q(quadratic(g),y)

def section_phase(g,x):return (apply(g,x).bit_count()-x.bit_count())%4

@lru_cache(maxsize=None)
def _tag(g):
    result=0
    for j,col in enumerate(g):
        diff=(_q(quadratic(g),col)-(col.bit_count()-1))%4
        need(diff%2==0,'even phase-section difference')
        result|=(diff//2)<<j
    return result

def tag(g):return _tag(normal(g))

def cocycle(h,g):
    return tag(g)^pullback(g,tag(h))^tag(compose(h,g))

def word_certificate(maps,signs=None):
    need(isinstance(maps,(tuple,list)) and maps,'nonempty word')
    maps=[normal(g) for g in maps];n=len(maps[0])
    need(all(len(g)==n for g in maps),'word width')
    signs=[1]*len(maps) if signs is None else signs
    need(isinstance(signs,(tuple,list)) and len(signs)==len(maps)
         and all(type(s) is int and s in (-1,1) for s in signs),'typed word signs')
    product=tuple(1<<j for j in range(n));section_tag=0
    for g,sign in zip(maps,signs):
        h=g if sign==1 else inverse(g)
        local_tag=tag(g) if sign==1 else pullback(h,tag(g))
        section_tag^=pullback(product,local_tag)
        product=compose(h,product)
    return {'product':list(product),'tag':section_tag^tag(product),'section_tag':section_tag}

def check_word(maps,certificate,signs=None):
    expected=word_certificate(maps,signs)
    need(json.dumps(certificate,sort_keys=True)==json.dumps(expected,sort_keys=True),
         'complete typed word certificate')
    return expected

def gate_phase(g,x,sign):
    need(type(sign) is int and sign in (-1,1),'typed gate sign')
    return canonical_phase(g,x) if sign==1 else -canonical_phase(g,apply(inverse(g),x))%4

def actual_maps():
    authenticate();items=load(HERE/'source/RECIPES.json')['items']
    need(len(items)==40,'frozen descriptor domain')
    warps=[x for x in items if x['kind']=='warp']
    gs=sorted({normal(x['G_columns']) for x in warps})
    need(len(warps)==16 and len(gs)==4 and all(len(g)==9 for g in gs),'four changed-interface maps only')
    return gs

def audit(certificate=None):
    gs=actual_maps();rows=[];phase_checks=0
    for g in gs:
        t=tag(g);gi=inverse(g);ti=tag(gi);ell=cocycle(gi,g)
        need(compose(gi,g)==tuple(1<<j for j in range(9)),'actual inverse')
        for x in range(512):
            need(canonical_phase(g,x)==(section_phase(g,x)+2*((t&x).bit_count()%2))%4,'actual section identity')
            need((canonical_phase(g,x)+canonical_phase(gi,apply(g,x)))%4
                 ==2*((ell&x).bit_count()%2),'actual inverse character')
            need((2*((ell&apply(gi,x)).bit_count()%2)+canonical_phase(gi,x))%4
                 ==gate_phase(g,x,-1),'corrected inverse with left tag')
            phase_checks+=1
        rows.append({'columns':list(g),'tag':t,'inverse_tag':ti,'inverse_defect':ell})
    for h in gs:
        for g in gs:
            product=compose(h,g);ell=cocycle(h,g)
            for x in range(512):
                need((canonical_phase(g,x)+canonical_phase(h,apply(g,x)))%4
                     ==(canonical_phase(product,x)+2*((ell&x).bit_count()%2))%4,'actual coboundary composition')
    maps=[gs[0],gs[1],gs[2],gs[3],gs[0],gs[1]];signs=[1,-1,1,1,-1,-1]
    word=word_certificate(maps,signs)
    for x in range(512):
        y=x;phase=0
        for g,sign in zip(maps,signs):
            phase+=gate_phase(g,y,sign);y=apply(g if sign==1 else inverse(g),y)
        need(y==apply(word['product'],x),'signed word permutation')
        need(phase%4==(canonical_phase(word['product'],x)+2*((word['tag']&x).bit_count()%2))%4,
             'signed word exact global phase')
    witness=(1,2,8,32,44,128,59,66,489);wi=inverse(witness)
    need(witness in gs and tag(witness)==144 and tag(wi)==68 and cocycle(wi,witness)==256,'credited source witness')
    # Alpha=1+i, beta=1-i are numerators over2. Anticommuting Z sends
    # beta to -beta; this equals i*C†, including its mandatory global phase.
    alpha,beta=(1,1),(1,-1)
    times_i=lambda z:(-z[1],z[0])
    need(times_i(beta)==alpha and times_i(alpha)==tuple(-x for x in beta),'central C global i')
    need((144&16).bit_count()%2==1 and beta!=tuple(-x for x in beta),'naive untagged frame differs')
    expected={'schema_version':1,'width':9,'maps':rows,'signed_word':{'indices':[0,1,2,3,0,1],
                'signs':signs,'certificate':word},'credited_inverse_witness':{'tag':144,'inverse_tag':68,'defect':256},
                'frame_rebinding':{'tag':144,'direction':16,'required_global_i':True}}
    cert=load(HERE/'CERTIFICATE.json') if certificate is None else certificate
    need(json.dumps(cert,sort_keys=True)==json.dumps(expected,sort_keys=True),'complete typed phase certificate')
    return {'actual_maps':len(gs),'actual_states_per_map':512,'phase_checks':phase_checks,
            'actual_pair_checks':16*512,'signed_word_states':512,'source_witness':expected['credited_inverse_witness'],
            'signed_word':word,'central_C_requires_global_i':True,'predecessor_executable_imported':False,
            'physical_recipe_replaced':False,'native_tariff_proved':False,'new_kappa':False}

if __name__=='__main__':print('PASS_NATIVE_LIFT_PHASE_TAGS '+json.dumps(audit(),sort_keys=True))
