#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct and replay integer rank transfers for concave invoice improvement.

Classical majorization supplies the transfer argument. Retain the signed-invoice
tool credits. Prepared for Ali Romman with OpenAI Codex assistance.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import (compare_invoices,load_invoice,require,
                                           _pairs,_integer,_not_integer)
finally:
    sys.path.pop(0)

MAX_SLOTS=2048

def vectors(a,b):
    require(sum(a.values())<=MAX_SLOTS and sum(b.values())<=MAX_SLOTS,
            'transfer plans support at most 2048 jobs per histogram')
    def expand(hist):return sorted((int(r) for r,n in hist.items() for _ in range(n)),reverse=True)
    left,right=expand(a),expand(b)
    size=max(len(left),len(right))
    return left+[0]*(size-len(left)),right+[0]*(size-len(right))


def transfer_plan(source,target):
    if sum(source)!=sum(target):
        return None,{'reason':'unequal_rank_mass','source_mass':sum(source),'target_mass':sum(target)}
    margin=0
    for i,(a,b) in enumerate(zip(source,target)):
        margin+=a-b
        if margin<0:return None,{'reason':'majorization_prefix','prefix_length':i+1,'margin':margin}
    current=list(source);steps=[];donors=[]
    for j,wanted in enumerate(target):
        if current[j]>wanted:donors.append(j)
        while current[j]<wanted:
            require(bool(donors),'majorization construction has no donor')
            i=donors[-1]
            amount=min(current[i]-target[i],wanted-current[j])
            steps.append({'from':i,'to':j,'amount':amount})
            current[i]-=amount;current[j]+=amount
            if current[i]==target[i]:donors.pop()
    require(current==target,'transfer endpoint mismatch')
    return steps,None


def replay(source,target,steps):
    require(type(steps) is list and len(steps)<=2*MAX_SLOTS,'invalid transfer list')
    current=list(source)
    for step in steps:
        require(type(step) is dict and step.keys()=={'from','to','amount'},'invalid transfer fields')
        i,j,amount=step['from'],step['to'],step['amount']
        require(type(i) is int and type(j) is int and 0<=i<len(current) and
                0<=j<len(current) and i!=j,'invalid transfer indices')
        require(type(amount) is int and amount>0 and
                2*amount<=current[i]-current[j],'transfer is not a balancing step')
        current[i]-=amount;current[j]+=amount
    require(current==target,'transfer endpoint mismatch')
    return True


def verify(old,new,certificate):
    comparison=compare_invoices(old,new)
    require(type(certificate) is dict and certificate.keys()=={'schema','paid','targets'} and
            certificate['schema']=='integer-mult-recursive-transfers/v1','invalid transfer certificate')
    for side,a,b in (('paid',new['paid'],old['paid']),('targets',old['targets'],new['targets'])):
        source,target=vectors(a,b)
        replay(source,target,certificate[side])
    return comparison


def plan(old,new):
    comparison=compare_invoices(old,new)
    certificate={'schema':'integer-mult-recursive-transfers/v1'};obstructions={}
    for side,a,b in (('paid',new['paid'],old['paid']),('targets',old['targets'],new['targets'])):
        source,target=vectors(a,b)
        steps,obstruction=transfer_plan(source,target)
        if obstruction:obstructions[side]=obstruction
        else:certificate[side]=steps
    result={'schema':'integer-mult-recursive-transfer-report/v1','contract':comparison['contract'],
            'supported':not obstructions,'obstructions':obstructions,
            'scope':'Equal-mass majorization certificate on declared ranks only. Paid steps run '
                    'from new to old; reverse them for paid concentration. Target steps run '
                    'from old to new. No physical map, target independence or kappa is certified.'}
    if not obstructions:
        verify(old,new,certificate)
        result['certificate']=certificate
        result['strict_for_strictly_concave_tariffs']=bool(certificate['paid'] or certificate['targets'])
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old');parser.add_argument('new')
    parser.add_argument('--verify',metavar='CERTIFICATE.json',help='replay a certificate object from a prior report')
    args=parser.parse_args(argv)
    try:
        old,a=load_invoice(args.old);new,b=load_invoice(args.new)
        inputs={'old':a,'new':b}
        if args.verify:
            with Path(args.verify).open('rb') as stream:raw=stream.read(1024*1024+1)
            require(len(raw)<=1024*1024,'certificate exceeds 1 MiB')
            certificate=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,
                                   parse_int=_integer,parse_float=_not_integer,parse_constant=_not_integer)
            verify(old,new,certificate)
            result={'schema':'integer-mult-recursive-transfer-replay/v1','valid':True,
                    'scope':'Declared integer ranks only; physical legality is not verified.'}
            inputs['certificate']={'path':args.verify,'bytes':len(raw),'sha256':sha256(raw).hexdigest()}
        else:result=plan(old,new)
        result['inputs']=inputs
    except (OSError,ValueError,TypeError,RecursionError) as exc:
        print(json.dumps({'status':'INVALID_TRANSFER_PLAN','error':str(exc)}),file=sys.stderr);return 2
    print(json.dumps(result,indent=2,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
