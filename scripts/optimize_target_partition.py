#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optimize a bounded target-partition menu with explicit per-piece paid fees.

Exact dynamic programming uses the existing rigorous power bounds. Physical
target independence remains a premise. Ali Romman with OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import (load_invoice,validate_invoice,require,MAX_COUNT,
                                           _pairs,_integer,_not_integer)
    from evaluate_recursive_power import parse_exponent,power_bounds
finally:
    sys.path.pop(0)


def prepare(base,plan):
    base=validate_invoice(base,'baseline')
    require(type(plan) is dict and plan.keys()=={'schema','target_rank','max_pieces','options'} and
            plan['schema']=='integer-mult-target-partition/v1','invalid partition schema')
    target,limit=plan['target_rank'],plan['max_pieces']
    require(type(target) is int and 2<=target<=256 and base['targets'].get(str(target),0)>0,
            'need an existing target rank in 2..256')
    require(type(limit) is int and 2<=limit<=32,'max_pieces must be in 2..32')
    require(type(plan['options']) is list and 1<=len(plan['options'])<=16,'provide 1..16 options')
    options=[];names=set();ranks={target};growth={}
    for row in plan['options']:
        require(type(row) is dict and row.keys()=={'id','rank','fee'},'invalid option fields')
        name,rank=row['id'],row['rank']
        require(type(name) is str and 0<len(name)<=128 and name not in names,'option IDs must be unique')
        names.add(name)
        require(type(rank) is int and 1<=rank<target,'each piece must be smaller than the target')
        fee=validate_invoice(row['fee'],'piece fee')
        require(fee['contract']==base['contract'] and not fee['targets'],'fee must be paid-only with the baseline contract')
        net=dict(fee['paid']);net[str(rank)]=net.get(str(rank),0)-1
        net={r:n for r,n in net.items() if n};ranks.update(map(int,net))
        for r,n in fee['paid'].items():growth[r]=max(growth.get(r,0),n)
        require(base['targets'].get(str(rank),0)+limit<=MAX_COUNT,'possible target count exceeds schema limit')
        options.append({'id':name,'rank':rank,'fee':fee,'net':net})
    require(len(ranks)<=128,'at most 128 power ranks across the menu')
    require(all(base['paid'].get(r,0)+limit*n<=MAX_COUNT for r,n in growth.items()),
            'possible paid count exceeds schema limit')
    require(len(base['paid'].keys()|growth.keys())<=4096 and
            len(base['targets'].keys()|{str(o['rank']) for o in options})<=4096,'possible support exceeds schema limit')
    return base,target,limit,options,ranks


def dynamic(options,target,limit,bound,exclude=None):
    """Minimize one additive bound, optionally excluding one full count vector."""
    states={(0,0,False):(0,())}
    for index,option in enumerate(options):
        following={}
        for (mass,pieces,different),(cost,counts) in states.items():
            maximum=min((target-mass)//option['rank'],limit-pieces)
            for count in range(maximum+1):
                changed=different or (exclude is not None and count!=exclude[index])
                key=(mass+count*option['rank'],pieces+count,changed)
                value=(cost+count*option[bound],counts+(count,))
                if key not in following or value<following[key]:following[key]=value
        states=following
    feasible=[v for (mass,pieces,different),v in states.items()
              if mass==target and 2<=pieces<=limit and (exclude is None or different)]
    return min(feasible) if feasible else None


def optimize(base,plan,exponent,bits=128):
    base,target,limit,options,ranks=prepare(base,plan)
    require(isinstance(exponent,Q) and 0<exponent<1,'need a rational exponent in (0,1)')
    require(type(bits) is int and 16<=bits<=256,'bits must be in 16..256')
    scale=1<<bits
    powers={r:tuple(int(v*scale) for v in power_bounds(r,exponent,bits)) for r in ranks}
    for option in options:
        lo=hi=0
        for r,n in option['net'].items():
            a,b=powers[int(r)];lo+=n*(a if n>0 else b);hi+=n*(b if n>0 else a)
        option['lower'],option['upper']=lo,hi
    upper=dynamic(options,target,limit,'upper')
    report={'schema':'integer-mult-target-partition-result/v1','exponent':str(exponent),'bits':bits,
            'target_rank':target,'max_pieces':limit,'feasible':upper is not None,
            'scope':'Optimum over this declared menu at this exponent only. Per-piece fees '
                    'are additive premises. Source legality, independent target ownership, '
                    'route completeness and complete kappa admission are not verified.'}
    if upper is None:return report
    lower=dynamic(options,target,limit,'lower');best_cost,counts=upper
    alternative=dynamic(options,target,limit,'lower',exclude=counts)
    result={**base,'paid':dict(base['paid']),'targets':dict(base['targets'])}
    result['targets'][str(target)]-=1
    for option,count in zip(options,counts):
        result['targets'][str(option['rank'])]=result['targets'].get(str(option['rank']),0)+count
        for rank,n in option['fee']['paid'].items():result['paid'][rank]=result['paid'].get(rank,0)+count*n
    result=validate_invoice(result,'partition invoice')
    fixed_lo,fixed_hi=powers[target]
    pair=lambda a,b:{'lower':str(Q(a,scale)),'upper':str(Q(b,scale))}
    partition=lambda cs:{o['id']:n for o,n in zip(options,cs) if n}
    report.update(certified_optimal=alternative is None or alternative[0]>=best_cost,
                  global_optimum=pair(fixed_lo+lower[0],fixed_hi+best_cost),
                  best={'partition':partition(counts),'pieces':sum(counts),'invoice':result,
                        'new_minus_baseline':pair(fixed_lo+sum(n*o['lower'] for o,n in zip(options,counts)),
                                                  fixed_hi+best_cost)},
                  optimistic_partition=partition(lower[1]),
                  alternative=None if alternative is None else {
                      'lower_without_replaced_target':str(Q(alternative[0],scale)),
                      'partition':partition(alternative[1])},
                  recommendation=('certified_improvement' if fixed_hi+best_cost<0 else
                                  'no_strict_improvement_in_this_menu' if fixed_lo+lower[0]>=0 else
                                  'unresolved_improvement'))
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline');parser.add_argument('plan');parser.add_argument('--exponent',required=True)
    parser.add_argument('--bits',type=int,default=128);args=parser.parse_args(argv)
    try:
        base,pin=load_invoice(args.baseline)
        with Path(args.plan).open('rb') as stream:raw=stream.read(8*1024*1024+1)
        require(len(raw)<=8*1024*1024,'plan exceeds 8 MiB')
        plan=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,parse_int=_integer,
                        parse_float=_not_integer,parse_constant=_not_integer)
        report=optimize(base,plan,parse_exponent(args.exponent),args.bits)
        report['inputs']={'baseline':pin,'plan':{'path':args.plan,'bytes':len(raw),'sha256':sha256(raw).hexdigest()}}
    except (OSError,ValueError,TypeError,RecursionError,ZeroDivisionError) as exc:
        print(json.dumps({'status':'INVALID_TARGET_PARTITION','error':str(exc)}),file=sys.stderr);return 2
    print(json.dumps(report,indent=2,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
