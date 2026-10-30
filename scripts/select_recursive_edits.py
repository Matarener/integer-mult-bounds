#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Select compatible invoice edits by exhaustive, interval-certified accounting.

Each edit is a complete single-edit invoice relative to the same baseline.
Integer capacities and original inventory limit simultaneous edits.
Ali Romman with OpenAI Codex assistance; retain the invoice/power tool credits.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import (load_invoice,validate_invoice,require,compare_invoices,
                                           MAX_COUNT,_pairs,_integer,_not_integer)
    from evaluate_recursive_power import parse_exponent,power_bounds
finally:
    sys.path.pop(0)


def prepare(base,plan):
    base=validate_invoice(base,'baseline')
    require(type(plan) is dict and plan.keys()=={'schema','capacities','edits'} and
            plan['schema']=='integer-mult-recursive-edit-plan/v1','invalid edit-plan schema')
    capacities=plan['capacities']
    require(type(capacities) is dict and len(capacities)<=32,'at most 32 resources')
    for key,value in capacities.items():
        require(type(key) is str and 0<len(key)<=128 and type(value) is int and
                0<=value<=MAX_COUNT,'invalid resource capacity')
    require(type(plan['edits']) is list and 1<=len(plan['edits'])<=16,'provide 1..16 edits')
    edits=[];ids=set();keys=set();growth={}
    for raw in plan['edits']:
        require(type(raw) is dict and raw.keys()=={'id','invoice','uses'},'invalid edit fields')
        name=raw['id'];uses=raw['uses']
        require(type(name) is str and 0<len(name)<=128 and name not in ids,'edit IDs must be unique')
        ids.add(name)
        require(type(uses) is dict and uses.keys()<=capacities.keys(),'unknown resource')
        require(all(type(n) is int and 0<=n<=MAX_COUNT for n in uses.values()),'invalid resource use')
        candidate=validate_invoice(raw['invoice'],name)
        comparison=compare_invoices(base,candidate)
        change={}
        for side in ('paid','targets'):
            for rank in base[side].keys()|candidate[side].keys():
                amount=candidate[side].get(rank,0)-base[side].get(rank,0)
                if amount:
                    change[side,rank]=amount;keys.add((side,rank))
                    growth[side,rank]=growth.get((side,rank),0)+max(0,amount)
        edits.append({'id':name,'uses':dict(uses),'change':change,'net':comparison['signed_net_delta']})
    ranks={r for e in edits for r in e['net']}
    require(len(ranks)<=64,'at most 64 uncancelled ranks across all edits')
    for (side,rank),amount in growth.items():
        require(base[side].get(rank,0)+amount<=MAX_COUNT,'possible combined count exceeds schema limit')
    for side in ('paid','targets'):
        require(len(base[side].keys()|{r for s,r in keys if s==side})<=4096,'possible combined support exceeds schema limit')
    return base,capacities,edits


def select(base,plan,exponent,bits=128,report_limit=16):
    base,capacities,edits=prepare(base,plan)
    require(isinstance(exponent,Q) and 0<exponent<1,'need a rational exponent in (0,1)')
    require(type(bits) is int and 16<=bits<=256,'bits must be in 16..256')
    require(type(report_limit) is int and 1<=report_limit<=256,'report_limit must be in 1..256')
    ranks={r for e in edits for r in e['net']}
    powers={r:power_bounds(int(r),exponent,bits) for r in ranks}
    for edit in edits:
        lo=hi=Q(0)
        for rank,count in edit['net'].items():
            a,b=powers[rank];lo+=count*(a if count>0 else b);hi+=count*(b if count>0 else a)
        edit['bounds']=(lo,hi)
    feasible=[];pruned=0
    def visit(index,mask,uses,removed,lo,hi):
        nonlocal pruned
        if index==len(edits):
            feasible.append((mask,lo,hi));return
        visit(index+1,mask,uses,removed,lo,hi)
        edit=edits[index]
        new_uses=dict(uses);new_removed=dict(removed)
        for key,n in edit['uses'].items():new_uses[key]=new_uses.get(key,0)+n
        for key,n in edit['change'].items():
            if n<0:new_removed[key]=new_removed.get(key,0)-n
        if (any(n>capacities[k] for k,n in new_uses.items()) or
            any(n>base[side].get(rank,0) for (side,rank),n in new_removed.items())):
            pruned+=2**(len(edits)-index-1);return
        a,b=edit['bounds']
        visit(index+1,mask|(1<<index),new_uses,new_removed,lo+a,hi+b)
    visit(0,0,{}, {},Q(0),Q(0))
    best=min(feasible,key=lambda row:(row[2],row[0].bit_count(),row[0]))
    def chosen(mask):return [e for i,e in enumerate(edits) if mask&(1<<i)]
    def signature(mask):
        value={}
        for e in chosen(mask):
            for r,n in e['net'].items():value[r]=value.get(r,0)+n
        return {r:n for r,n in value.items() if n}
    best_signature=signature(best[0])
    certified=all(mask==best[0] or lo>=best[2] or signature(mask)==best_signature
                  for mask,lo,hi in feasible)
    selected=chosen(best[0]);result={**base,'paid':dict(base['paid']),'targets':dict(base['targets'])}
    used={}
    for edit in selected:
        for (side,rank),n in edit['change'].items():result[side][rank]=result[side].get(rank,0)+n
        for key,n in edit['uses'].items():used[key]=used.get(key,0)+n
    result=validate_invoice(result,'selected combination')
    contenders=[row for row in feasible if row[1]<=best[2]]
    pair=lambda lo,hi:{'lower':str(lo),'upper':str(hi)}
    return {'schema':'integer-mult-recursive-edit-selection/v1','exponent':str(exponent),'bits':bits,
            'subsets':2**len(edits),'feasible_subsets':len(feasible),'infeasible_subsets':pruned,
            'certified_optimal':certified,'global_optimum':pair(min(r[1] for r in feasible),best[2]),
            'best':{'ids':[e['id'] for e in selected],'uses':used,'invoice':result,
                    'new_minus_baseline':pair(best[1],best[2])},
            'possible_optima_count':len(contenders),
            'possible_optima':[{'ids':[e['id'] for e in chosen(mask)],'bounds':pair(lo,hi)}
                               for mask,lo,hi in contenders[:report_limit]],
            'scope':'Exhaustive optimum enclosure over these declared independent edits only. '
                    'Gross removals cannot reuse added output. Capacities and physical independence '
                    'are declarations. Interval overlap is not equality or a certified winner.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline');parser.add_argument('plan');parser.add_argument('--exponent',required=True)
    parser.add_argument('--bits',type=int,default=128);parser.add_argument('--report-limit',type=int,default=16)
    args=parser.parse_args(argv)
    try:
        base,pin=load_invoice(args.baseline)
        with Path(args.plan).open('rb') as source:raw=source.read(8*1024*1024+1)
        require(len(raw)<=8*1024*1024,'plan exceeds 8 MiB')
        plan=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,parse_int=_integer,
                        parse_float=_not_integer,parse_constant=_not_integer)
        result=select(base,plan,parse_exponent(args.exponent),args.bits,args.report_limit)
        result['inputs']={'baseline':pin,'plan':{'path':args.plan,'bytes':len(raw),'sha256':sha256(raw).hexdigest()}}
    except (OSError,ValueError,TypeError,RecursionError,ZeroDivisionError) as exc:
        print(json.dumps({'status':'INVALID_EDIT_SELECTION','error':str(exc)}),file=sys.stderr);return 2
    print(json.dumps(result,indent=2,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
