#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate finite reviewer for five-replica R437 owner pooling.

Imports neither the builder nor the predecessor pooling implementation.
Reconstructs each owner, schedule window and actual paid child independently;
prices with the retained, separately authored base-two moment engine.
Substantial OpenAI assistance; no independent human or native admission claim.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO/'research/kappa-next-regime/sources/PR3959/research/rank7-pooled-r437-bit/R437-GLOBAL-TEMPLATE.json.gz'
PRIOR = REPO/'research/kappa-next-regime/sources/PR3959/research/rank7-pooled-r437-bit/CLAIM.json'
ENGINE = REPO/'research/native-complex-moment552/engines/base_two_moment.py'
PINS = {
    SOURCE:'6e03c76f5a4227394ea57e901eb7e93f4d1ee411ccfecd483fd44ea043550494',
    PRIOR:'496de468b69975ad5da003f32ffaa4e11289eb9df39cb81c4275c27679a2a390',
    ENGINE:'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
}


def require(ok,reason):
    if not ok: raise ValueError(reason)


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def read(path):
    b=path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix=='.gz' else b)


def boundaries(schedule):
    previous={}
    sweeps=[]
    out={}
    scalar=[[int(i==j) for j in range(8)] for i in range(8)]
    for time,event in enumerate(schedule):
        kind=event['kind']
        if kind=='local_cover_sweep':
            pair=event['pair'];stage=event['stage']
            sweeps.append((time,stage,pair))
            previous[pair]=time
            dst,src,c=(pair,pair+4,-1) if event['reverse'] else (pair+4,pair,1)
            scalar[dst]=[x+c*y for x,y in zip(scalar[dst],scalar[src])]
        elif kind=='bridge':
            dst,src,c=event['dst'],event['src'],event['coefficient']
            previous[dst]=previous[src]=time
            scalar[dst]=[x+c*y for x,y in zip(scalar[dst],scalar[src])]
            scalar[src+4]=[x-c*y for x,y in zip(scalar[src+4],scalar[dst+4])]
        elif kind=='idle':
            stages=[s for t,s,pair in sweeps if previous.get(event['pair'],-1)<t<time and pair!=event['pair']]
            if stages and event['rank']:
                out[str(event['idx'])]=[event['pair'],event['rank'],stages]
        elif kind=='exchange':
            scalar=scalar[4:]+[[-x for x in row] for row in scalar[:4]]
    require(scalar==[[int(i==j) for j in range(8)] for i in range(8)],'literal scalar controller identity')
    return out


def inspect(template):
    T=template['replicas'];W=template['live']
    require(isinstance(T,int) and T>0 and T%5==0 and W==888*T,'positive five-replica dimension')
    require(template['m']==64 and template['stages']==9,'fixed native dimensions')
    require(template['private_centre_reserve']==9 and template['bank_padding'] is None,'all private fields retained')
    require(template['banks_per_stage']==template['hosting']['banks_per_stage']=={str(s):0 for s in range(9)},'no hidden banks')
    windows=boundaries(template['schedule'])
    require(windows==template['hosting']['windows'],'schedule-derived idle windows')
    local={}
    for orientation,program in template['local_programs'].items():
        counted=Counter()
        for event in program:
            if event[0]==0 and event[4]>0: counted[event[4]]+=1
            if event[0]==2: counted[event[5]]+=1
        local[orientation]=counted
    require(local['forward']==local['reverse'],'equal actual local IR bills')
    paid=Counter();used=defaultdict(int);domain=set();inventory=[]
    for call in template['calls']:
        s,rep=call['stage'],call['replica']
        require((s,rep) not in domain and 0<=s<9 and 0<=rep<T,'unique call key')
        domain.add((s,rep))
        require(len(call['owners'])==659,'659 exact local roles')
        require(len({(fam,tuple(route)) for fam,route in call['owners']})==659,'same-call owner-map injection')
        reverse=int(call['orientation']=='reverse')
        expected_data=[[888*rep+222*call['pair']+111*((i//111)^reverse)+i%111,['data',s,i%111]] for i in range(222)]
        require(call['owners'][:222]==expected_data,'literal productive data ownership')
        paid.update(local[call['orientation']])
        for helper,(family,route) in enumerate(call['owners'][222:]):
            require(len(route)==4 and route[0]=='hosted','all helpers hosted')
            child,off,width=route[1:]
            require(str(child) in windows,'named idle child')
            pair,cap,stages=windows[str(child)]
            require(s in stages and pair!=call['pair'],'helper inside inactive chronological window')
            require(0<=family<W and (family%888)//222==pair,'absolute family within child pair')
            require(width==8 and 0<=off and off+8<=cap,'eight-axis residual within owner')
            mask=255<<off
            require(not (used[child,family]&mask),'no overlapping helper coordinates')
            used[child,family]|=mask
            inventory.append([s,rep,helper,family,child,off,width])
    require(domain=={(s,r) for s in range(9) for r in range(T)},'full stage/replica domain')
    idle=Counter();idle_records=[]
    for child,win in sorted(windows.items(),key=lambda x:int(x[0])):
        child=int(child);pair,cap,stages=win
        for rep in range(T):
            for cp in range(222):
                family=888*rep+222*pair+cp
                mask=used[child,family];taken=mask.bit_count()
                require(mask==(1<<taken)-1,'compact occupied native-axis prefix')
                rank=cap-taken
                require(rank>0,'positive remainder for width-eight model')
                idle[rank]+=1
                idle_records.append([child,rep,cp,family,taken,rank])
    paid.update(idle)
    require(sum(paid.values())==28233*T,'every paid request included')
    require(sum(r*n for r,n in paid.items())==56511*T,'complete raw rank mass')
    require(64*W-sum(r*n for r,n in paid.items())==321*T,'complete raw deficit')
    require(2*max(paid)**2<64**2,'strict recursive child guard')
    return dict(sorted(paid.items())),dict(sorted(idle.items())),inventory,idle_records


def source_match(candidate,source,moves):
    require(candidate['schedule']==source['schedule'] and candidate['local_programs']==source['local_programs'],
            'scalar and native local words unchanged')
    for key in ('cover','data_route','geometry_sha256','residual_isometries','h','m','source_record_sha256'):
        require(candidate[key]==source[key],'source-bound geometry property '+key)
    seeds={c['stage']:c for c in source['calls'] if c['replica']==0}
    expected={}
    for s in range(9):
        for r in range(candidate['replicas']):
            row=deepcopy(seeds[s]);row['replica']=r
            for owner in row['owners']:owner[0]+=888*r
            expected[s,r]=row
    changed=set()
    for move in moves:
        s,r,h=move['stage'],move['call_replica'],move['helper']
        require((s,r,h) not in changed,'distinct moved logical roles');changed.add((s,r,h))
        old,new=move['old'],move['new']
        require(old['child']==new['child']==6,'only identical window-six transfers')
        require(r//5==(new['family']//888)//5 and new['family']//888==5*(r//5), 'five-replica block locality')
        require(expected[s,r]['owners'][222+h]==[old['family'],['hosted',6,old['offset'],8]],'exact old owner')
        expected[s,r]['owners'][222+h]=[new['family'],['hosted',6,new['offset'],8]]
    require(len(changed)==8*candidate['replicas']//5,'eight exact moves per block')
    require(candidate['calls']==[expected[s,r] for s in range(9) for r in range(candidate['replicas'])],
            'complete unchanged and changed actual calls')


def price_check(profile,live,lower):
    spec=importlib.util.spec_from_file_location('pool5_base_two',ENGINE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    signs=[]
    for a,is_lower in ((lower,True),(lower+Q(1,10**24),False)):
        lo,hi=module.moment(64,live,list(profile.items()),a)
        badlo,badhi=module.moment(64,live,[(1,32*64*64*sum(profile.values()))],a)
        lo+=badlo/10**16;hi+=badhi/10**16
        require(hi<1 if is_lower else lo>1,'independent exact endpoint and full fallback')
        signs.append(dict(endpoint=str(a),moment_lower=str(lo),moment_upper=str(hi),strict_sign='below' if is_lower else 'above'))
    return signs


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=HERE/'pool35')
    parser.add_argument('--out',type=Path,default=HERE/'POOL35-INDEPENDENT-REVIEW.json')
    args=parser.parse_args()
    require(not args.out.exists(),'fresh receipt path required')
    for path,pin in PINS.items():require(sha256(path.read_bytes()).hexdigest()==pin,'source hash '+str(path))
    source=read(SOURCE);candidate=read(args.candidate/'GLOBAL-TEMPLATE.json.gz')
    receipt=read(args.candidate/'RESULT.json');moves=read(args.candidate/'POOL-MOVES.json')['moves']
    source_match(candidate,source,moves)
    profile,idle,roles,records=inspect(candidate)
    require(profile=={int(r):n for r,n in receipt['profile'].items()},'actual profile matches receipt')
    require(idle=={int(r):n for r,n in receipt['idle_profile'].items()},'actual idle profile matches receipt')
    for name,value,key in [('GLOBAL-TEMPLATE.json.gz',candidate,'template_content_sha256'),
                           ('OWNER-INVENTORY.json.gz',roles,'owner_inventory_content_sha256'),
                           ('IDLE-INVENTORY.json.gz',records,'idle_inventory_content_sha256')]:
        require(read(args.candidate/name)==value,'complete emitted inventory '+name)
        require(sha256(canonical(value)).hexdigest()==receipt[key],'payload digest '+name)
    lower=Q(receipt['bit_endpoint_lower'])
    signs=price_check(profile,candidate['live'],lower)
    require(lower>Q(read(PRIOR)['bit_pooled']),'strict increase over PR3959')
    controls={}
    def reject(name,mutate):
        t=deepcopy(candidate);mutate(t)
        try:inspect(t)
        except ValueError as exc:controls[name]=str(exc)
        else:raise ValueError('semantic control accepted: '+name)
    first=moves[0];second=moves[1]
    def owner(t,move):return t['calls'][move['stage']*t['replicas']+move['call_replica']]['owners'][222+move['helper']]
    reject('family_out_of_domain',lambda t:owner(t,first).__setitem__(0,t['live']))
    reject('invalid_destination_window',lambda t:owner(t,first)[1].__setitem__(1,2))
    reject('coordinate_collision',lambda t:owner(t,second).__setitem__(1,deepcopy(owner(t,first)[1])))
    reject('wrong_helper_width',lambda t:owner(t,first)[1].__setitem__(3,7))
    reject('truncated_call_roles',lambda t:t['calls'][0]['owners'].pop())
    reject('duplicate_call_key',lambda t:t['calls'][1].__setitem__('replica',0))
    reject('wrong_private_reserve',lambda t:t.__setitem__('private_centre_reserve',8))
    reject('omitted_scalar_bridge',lambda t:t['schedule'].pop(next(i for i,x in enumerate(t['schedule']) if x['kind']=='bridge')))
    try:price_check(profile,candidate['live'],lower+Q(1,10**24))
    except ValueError as exc:controls['next_grid_rejected']=str(exc)
    else:raise ValueError('next-grid control accepted')
    result=dict(status='PASS_POOL35_INDEPENDENT_FINITE_OWNER_AND_PRICE_REVIEW',replicas=candidate['replicas'],
        calls=len(candidate['calls']),roles=len(roles),idle_children=len(records),moves=len(moves),
        paid_requests=sum(profile.values()),profile=profile,rank_mass=sum(r*n for r,n in profile.items()),
        live=candidate['live'],physical=candidate['live']+9,stock_index_bits=(candidate['live']+8).bit_length(),
        source_sha256={str(p.relative_to(REPO)):pin for p,pin in PINS.items()},
        candidate_template_content_sha256=sha256(canonical(candidate)).hexdigest(),
        independent_interval_signs=signs,controls=controls,
        scope='Independent standard-library finite owner, inherited scalar/geometry binding, IR child recount and second-engine price review only. Physical CALL/RETURN, native execution, complete supplier/outer admission remain external obligations. Independent implementation in the same AI-assisted session, not human review.')
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],len(controls),'controls',len(roles),'roles')


if __name__=='__main__':main()
