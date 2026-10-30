#!/usr/bin/env python3
"""Verify the coupled-star exclusion and its exact controls.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]


def require(test,message):
    if not test:raise ValueError(message)


def local(name):
    spec=importlib.util.spec_from_file_location(name,PACKAGE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def bound_power(rank,bits=48):
    # Enclose rank^(319/320) by integer powers only.
    scale=1<<bits;goal=pow(rank,319)<<(320*bits);lo=0;hi=rank*scale+1
    while hi-lo>1:
        mid=(lo+hi)//2
        if pow(mid,320)<=goal:lo=mid
        else:hi=mid
    return lo,lo if pow(lo,320)==goal else lo+1


def pricing():
    source=json.loads((ROOT/'research/p104-helper-subspace-splits/RESULT.json').read_text())['local']
    net={int(r):v for r,v in source['paid'].items()}
    for r,v in source['helpers'].items():net[int(r)]=net.get(int(r),0)-v
    require(sum(r*v for r,v in net.items())==1720,'Pinned full rank mass')
    g=1023;q=104;coeff={r:-2*(g+2)*v for r,v in net.items()}
    coeff[8*g+1]=coeff.get(8*g+1,0)+2*q;coeff[9]=coeff.get(9,0)+2*q*g
    lower=upper=0
    for r,count in coeff.items():
        lo,hi=bound_power(r)
        lower+=count*(lo if count>=0 else hi)
        upper+=count*(hi if count>=0 else lo)
    require(lower>0,'The excluded relaxed profile must pass its price screen')
    require(20000000>320*62009,'Screen saving exceeds the refreshed selected saving')
    h=104*8-720
    require(8*(h-104)<h,'Eight-call query frame rejection')
    return {'supplier':'PR5599 09dd0965711ca7eeb169057a420abab1c9052137','net_rank_mass':1720,'excluded_relaxation':{'q':q,'g':g,'full_calls':2*g+4,'main_fields':2*q*(g+1),'main_targets':{str(8*g+1):2*q,'9':2*q*g},'saving':'1/320','moment_interval_numerators':[str(lower),str(upper)],'denominator':str(1<<48),'status':'POSITIVE_PRICE_SCREEN_BUT_NO_CALLER_IN_THE_DECLARED_FRAME'},'rejected_eight_call_frame':{'q':104,'L':8,'N':720,'h':h,'left':8*(h-104),'right':h}}


def run():
    sources=json.loads((PACKAGE/'SOURCES.json').read_text())
    inputs=[row for row in sources['files'] if row['usage']=='input']
    for row in inputs:
        require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Source digest: '+row['path'])
    checker=local('check_certificates')
    result={'status':'PASS_ALL_ORDER_COUPLED_STAR_EXCLUSION','scope':'All odd g>=3, all positive channel dimensions, all characteristic-two fields, all call orders; fixed star queries and four complementary connectors','authenticated_inputs':len(inputs),'certificate_check':checker.verify(),'matrix_controls':local('model_checks').run(checker),'pricing':pricing(),'limits':['No native or characteristic-zero reduction','No new kappa','Other query frames and connector contracts are not excluded','No proof-assistant or independent human acceptance']}
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if '--write-result' in sys.argv:(PACKAGE/'RESULT.json').write_text(encoded)
    else:require((PACKAGE/'RESULT.json').read_text()==encoded,'Committed result differs from replay')
    print(encoded,end='')

if __name__=='__main__':run()
