#!/usr/bin/env python3
"""Replay the connector theorem package and its paid profiles.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]

def require(value,message):
    if not value:raise ValueError(message)

def load_check():
    spec=importlib.util.spec_from_file_location('connector_check',PACKAGE/'check.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def power_bound(rank,numerator,denominator,bits=40):
    scale=1<<bits;goal=pow(rank,numerator)<<(denominator*bits);lo=0;hi=rank*scale+1
    while hi-lo>1:
        mid=(lo+hi)//2
        if pow(mid,denominator)<=goal:lo=mid
        else:hi=mid
    return lo,lo if pow(lo,denominator)==goal else lo+1

def profile(source,g,thin):
    counts={int(r):-2*g*v for r,v in source['paid'].items()}
    for r,v in source['helpers'].items():counts[int(r)]=counts.get(int(r),0)+2*g*v
    counts[8*g+1]=counts.get(8*g+1,0)+208;counts[9]=counts.get(9,0)+208*g;counts[1]-=104*thin
    return {r:c for r,c in counts.items() if c}

def pricing():
    source=json.loads((ROOT/'research/p104-helper-subspace-splits/RESULT.json').read_text())['local'];bad=profile(source,3,8)
    linear=sum(r*c for r,c in bad.items());require(linear==-336,'Escape price mass')
    require(min(r for r,c in bad.items() if c>0)==8,'Positive escape rank floor')
    require(max(r for r,c in bad.items() if c<0)==7,'Negative escape rank ceiling')
    candidates=[]
    for g,thin,ports in ((127,10,1),(31,5,2)):
        candidate=profile(source,g,thin);lo=hi=0
        for r,c in candidate.items():
            a,b=power_bound(r,1993,2000)
            lo+=c*(a if c>=0 else b);hi+=c*(b if c>=0 else a)
        require(lo>0,'The long relaxation must retain a positive exact price margin')
        candidates.append({'q':104,'g':g,'ports_per_binary_block':ports,'full_calls':2*g,'thin_queries_per_native_port':thin,'saving':'7/2000','moment_lower_numerator':str(lo),'moment_upper_numerator':str(hi),'moment_denominator':str(1<<40),'status':'POSITIVE_OPTIMISTIC_PRICE_ONLY; NO CALLER OR KAPPA CLAIM'})
    return {'pinned_supplier':'PR5599 09dd0965711ca7eeb169057a420abab1c9052137','escape':{'q':104,'g':3,'thin_queries_per_copy':8,'signed_profile':{str(r):v for r,v in sorted(bad.items())},'linear_margin':linear,'all_concave_moments_rejected':True},'unconstructed_candidates':candidates}

def run():
    sources=json.loads((PACKAGE/'SOURCES.json').read_text());count=0
    for row in sources['files']:
        if row['usage']=='input':
            require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Source digest: '+row['path']);count+=1
    checker=load_check();controls=checker.run()
    result={'status':'PASS_ONE_SIDED_CONNECTOR_OBSTRUCTION','scope':'Finite matrices over every characteristic-two field; any finite star stage splits and call order; one-sided equal leaf signatures','authenticated_inputs':count,'controls':controls,'pricing':pricing(),'limits':['No kappa increase','The full escape word is binary algebra, not a physical native caller','The 127-leaf price profile has no operator','No proof-assistant or independent human acceptance']}
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if '--write-result' in sys.argv:(PACKAGE/'RESULT.json').write_text(encoded)
    else:require((PACKAGE/'RESULT.json').read_text()==encoded,'Committed result differs')
    print(encoded,end='')
if __name__=='__main__':run()
