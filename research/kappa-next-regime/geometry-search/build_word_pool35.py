#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind the improved complete R437 word to the exact T35 owner allocation.

Native word and record grammar descend from ai-nanachi/PR3647; ownership
pooling descends from Rohan Arun/PR3939/3959. New A/C scalar word refinement
and finite five-replica packing were prepared with substantial OpenAI
assistance under the user's direction. See ../word-search and README.md.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import struct
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SCOPE=HERE.parent
PARENT=HERE/'pool35'
ADAPTER=SCOPE/'native-catalogue/adapter.py'
WORD=SCOPE/'word-search/candidate/WORD.json.gz'
RECORDS=SCOPE/'word-search/native/records/249-records.bin'
SOURCE=SCOPE/'sources/PR3647/research/bit-p111-r437-gl464-470-20261018'
ENGINE=REPO/'research/native-complex-moment552/engines/moment.py'
WORD_SHA='3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0'
WORD_GZIP_SHA='ee42c58fb0cd23bad942ec472c7fb4f87db8261ce6ee4b2bc7e812212d8b836e'
PARENT_CONTENT_SHA='eaf20fb0dfeb1f8e0d5cdf1e353326f73c42faa2b815d0334338b387b6b8e2c1'
RECORD_SHA='46de969ce23c7cc5fd0f93ab5b24dd1fd3dfed85ddb462c881082ca23702d2f4'


def need(ok,reason):
    if not ok:raise ValueError(reason)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value
    spec.loader.exec_module(value)
    return value


def dimension(lines,frame):
    basis={}
    for index in frame:
        row=list(map(Q,lines[index]))
        for pivot,vector in sorted(basis.items()):
            coefficient=row[pivot]
            if coefficient:row=[a-coefficient*b for a,b in zip(row,vector)]
        pivot=next((i for i,x in enumerate(row) if x),None)
        if pivot is not None:
            coefficient=row[pivot]
            basis[pivot]=[x/coefficient for x in row]
    return len(basis)


def from_records(raw,dimensions):
    """Second route to the two IR streams, starting from actual exported bytes."""
    records=list(struct.iter_unpack('<6i',raw));programs={}
    for reverse in (False,True):
        out=[]
        for op,x,y,c,f,z in (reversed(records) if reverse else records):
            if op==0:
                old,new=(c,y) if reverse else (y,c)
                event=[0,x,old,new,f,int(reverse)]
            elif op==1:event=[1,x,y,-c if reverse else c,f,int(reverse)]
            elif op==(3 if reverse else 2):
                event=[2,x,y,c,f,abs(dimensions[c]-dimensions[f]),int(reverse)]
            else:
                need(op==(2 if reverse else 3),'closed exported record grammar')
                event=[3,x,y,c,f,z,int(reverse)]
            out.append(event)
        programs['reverse' if reverse else 'forward']=out
    return programs


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE/'pool35-word')
    args=parser.parse_args()
    need(__debug__,'assertions enabled for retained interval engine')
    need(not args.out.exists(),'fresh output directory required')
    need(sha256(WORD.read_bytes()).hexdigest()==WORD_GZIP_SHA,'exact changed word container')
    need(sha256(gzip.decompress(WORD.read_bytes())).hexdigest()==WORD_SHA,'exact changed word content')
    need(sha256(RECORDS.read_bytes()).hexdigest()==RECORD_SHA,'pinned actual native export bytes')
    parent=read(PARENT/'GLOBAL-TEMPLATE.json.gz')
    need(sha256(canonical(parent)).hexdigest()==PARENT_CONTENT_SHA,'exact already-reviewed T35 owners')
    predecessor=read(PARENT/'RESULT.json')
    need(predecessor['template_content_sha256']==PARENT_CONTENT_SHA,'parent receipt source binding')
    word=read(WORD);old_word=read(SOURCE/'data/r0042/R437-COMPOSED-WORD.json.gz')
    for key in ('h','v','R','form','frames','lines','start','final','D','B','ret','scatter'):
        need(word[key]==old_word[key],'unchanged native boundary or source section '+key)
    dimensions=[dimension(word['lines'],frame) for frame in word['frames']]
    adapter=module('pool35_word_native_lowering',ADAPTER)
    old_programs,_,_=adapter.lower_word(old_word,dimensions)
    need(old_programs==parent['local_programs'],'old native IR positive control')
    programs,local,info=adapter.lower_word(word,dimensions)
    need(programs==from_records(RECORDS.read_bytes(),dimensions),'word lowering equals freshly exported native record IR')
    need(info['forward']['source_record_sha256']==RECORD_SHA,'same exact record source pin')
    need(sum(r*n for r,n in local.items())==5113,'unchanged complete local rank mass')
    t=deepcopy(parent);t['local_programs']=programs;t['source_record_sha256']=RECORD_SHA
    t['version']='r437-pool5-blocks-T35-complete-AC-word'
    t['local_word_override']={'word_content_sha256':WORD_SHA,
        'parent_template_content_sha256':PARENT_CONTENT_SHA,
        'local_programs':info,
        'scope':'Complete A/C word substitution; all endpoints, helpers, source/scatter lists, controller and absolute owners retained.'}
    paid=Counter();roles=[]
    for before,after in zip(parent['calls'],t['calls']):
        after['local_hash']=info[after['orientation']]['sha256']
        need(after['owners']==before['owners'],'every absolute owner unchanged')
        paid.update(local)
        for helper,(family,route) in enumerate(after['owners'][222:]):
            _,child,offset,width=route
            roles.append([after['stage'],after['replica'],helper,family,child,offset,width])
    need(roles==read(PARENT/'OWNER-INVENTORY.json.gz'),'complete137655-role inventory retained')
    idles=read(PARENT/'IDLE-INVENTORY.json.gz');idle=Counter(row[-1] for row in idles)
    need(dict(idle)=={int(k):v for k,v in predecessor['idle_profile'].items()},'all69930 absolute idles retained')
    paid.update(idle)
    need(sum(r*n for r,n in paid.items())==1977885,'complete T35 rank mass')
    need(sha256(ENGINE.read_bytes()).hexdigest()=='81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482','retained exact engine pin')
    engine=module('pool35_word_exact_moment',ENGINE)
    price=engine.certify(dict(paid),64,31080,True)
    lower,upper=Q(price['lower']),Q(price['upper'])
    old_lower=Q(predecessor['bit_endpoint_lower'])
    prior_lower=old_lower-Q(predecessor['gain_over_PR3959_lower'])
    need(lower>old_lower,'strict next complete-word gain over packing-only result')
    result=deepcopy(predecessor)
    result.update(status='PASS_POOL35_COMPLETE_AC_WORD_TEMPLATE_AND_EXACT_PRICE',
        local_profile=dict(sorted(local.items())),profile=dict(sorted(paid.items())),
        paid_requests=sum(paid.values()),bit_endpoint_lower=str(lower),bit_endpoint_upper=str(upper),
        bit_endpoint_lower_decimal=engine.decimal(lower),bit_endpoint_upper_decimal=engine.decimal(upper),
        gain_over_PR3959_lower=str(lower-prior_lower),gain_over_PR3959_lower_decimal=engine.decimal(lower-prior_lower),
        gain_over_pool35_lower=str(lower-old_lower),gain_over_pool35_lower_decimal=engine.decimal(lower-old_lower),
        interval_price={k:v for k,v in price.items() if k in ('lower','upper','lower_endpoint_residual_upper','upper_endpoint_residual_lower','strict_rational_signs')},
        template_content_sha256=sha256(canonical(t)).hexdigest(),
        parent_template_content_sha256=PARENT_CONTENT_SHA,word_content_sha256=WORD_SHA,
        source_record_sha256=RECORD_SHA,local_programs=info,
        scope='Complete finite A/C-refined R437 word on the exact T35 absolute-owner template, with outward-rational full-fallback invoice. Independent native, physical, coefficient and outer-supplier checks remain the parent continuation obligations; this receipt alone asserts no unconditional kappa theorem.')
    pins=[Path(__file__),ADAPTER,WORD,RECORDS,PARENT/'GLOBAL-TEMPLATE.json.gz',PARENT/'RESULT.json',
          PARENT/'OWNER-INVENTORY.json.gz',PARENT/'IDLE-INVENTORY.json.gz',PARENT/'POOL-MOVES.json',ENGINE]
    result['source_sha256'].update({str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in pins})
    args.out.mkdir(parents=True)
    (args.out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(canonical(t),mtime=0))
    for name in ('OWNER-INVENTORY.json.gz','IDLE-INVENTORY.json.gz','POOL-MOVES.json'):
        (args.out/name).write_bytes((PARENT/name).read_bytes())
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])
    print(json.dumps({k:result[k] for k in ('bit_endpoint_lower_decimal','bit_endpoint_upper_decimal',
        'gain_over_PR3959_lower_decimal','gain_over_pool35_lower_decimal','profile','template_content_sha256')},sort_keys=True))


if __name__=='__main__':main()
