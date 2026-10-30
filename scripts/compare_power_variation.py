#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify power order for general-rank invoices with a finite root budget.

Use the classical generalized Descartes bound, exact endpoint roots and
directed-power brackets. An unspent root budget is inconclusive. The proof
and limits are in docs/research/recursive-power-variation.md.
Ali Romman with substantial OpenAI Codex assistance. Retain the invoice,
power-engine and T16 crossing predecessors' credit.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import compare_invoices,load_invoice,require
    from evaluate_recursive_power import power_bounds
finally:
    sys.path.pop(0)


bounded_power=lru_cache(maxsize=32768)(power_bounds)


@lru_cache(maxsize=512)
def prime_factors(rank):
    """Return prime valuations without constructing large integer powers."""
    factors=[];divisor=2
    while divisor*divisor<=rank:
        exponent=0
        while rank%divisor==0:
            rank//=divisor;exponent+=1
        if exponent:factors.append((divisor,exponent))
        divisor=3 if divisor==2 else divisor+2
    if rank>1:factors.append((rank,1))
    return tuple(factors)


def endpoint_multiplicity(delta,endpoint):
    if sum(count*rank**endpoint for rank,count in delta.items()):
        return 0
    exponents={}
    for rank,count in delta.items():
        for prime,exponent in prime_factors(rank):
            exponents[prime]=exponents.get(prime,0)+count*rank**endpoint*exponent
    # F'(endpoint)=log(product prime**exponents[prime]). Unique prime
    # factorization proves exact equality; no floating logarithm is used.
    return 2 if all(value==0 for value in exponents.values()) else 1


def enclosure(delta,t,bits):
    lower=upper=Q(0)
    for rank,count in delta.items():
        lo,hi=((Q(rank**int(t)),)*2 if t in (0,1) else bounded_power(rank,t,bits))
        lower+=count*(lo if count>0 else hi)
        upper+=count*(hi if count>0 else lo)
    return lower,upper


def sign(interval):
    low,high=interval
    return 1 if low>0 else -1 if high<0 else 0 if low==high==0 else None


def witness(t,interval):
    return {'t':str(t),'lower':str(interval[0]),'upper':str(interval[1])}


def classify(delta,bits=128,grid=64):
    require(type(bits) is int and 16<=bits<=256,'bits must be an integer in16..256')
    require(type(grid) is int and 2<=grid<=256,'grid must be an integer in2..256')
    delta=dict(sorted((int(r),n) for r,n in delta.items() if n))
    require(len(delta)<=512,'power comparison supports at most512 nonzero ranks')
    if not delta:
        return {'classification':'equal','root_budget':0,'interior_roots':0,'root_witnesses':[]}
    signs=[1 if n>0 else -1 for n in delta.values()]
    budget=sum(a!=b for a,b in zip(signs,signs[1:]))
    endpoints={str(t):endpoint_multiplicity(delta,t) for t in (0,1)}
    remaining=budget-sum(endpoints.values())
    require(remaining>=0,'endpoint roots exceed the sign-variation budget')
    points=([Q(1,2)] if not remaining else [Q(i,grid) for i in range(grid+1)])
    values=[enclosure(delta,t,bits) for t in points]
    point_signs=[sign(v) for v in values]
    roots=[]
    for i,t in enumerate(points):
        if 0<t<1 and point_signs[i]==0:
            roots.append({'exact':witness(t,values[i])})
        if i and point_signs[i] in (-1,1) and point_signs[i-1] in (-1,1):
            if point_signs[i]!=point_signs[i-1]:
                roots.append({'left':witness(points[i-1],values[i-1]),'right':witness(t,values[i])})
    require(len(roots)<=remaining,'root witnesses exceed the sign-variation budget')
    sample=next((witness(t,v) for t,v,s in zip(points,values,point_signs) if 0<t<1 and s in (-1,1)),None)
    complete=len(roots)==remaining and sample is not None
    classification=('inconclusive' if not complete else 'crossing' if roots else
                    'uniformly_higher' if Q(sample['lower'])>0 else 'uniformly_lower')
    return {'classification':classification,'root_budget':budget,
            'endpoint_multiplicity_lower_bounds':endpoints,'root_witnesses':roots,
            'interior_roots':len(roots) if complete else None,
            'interior_root_lower_bound':len(roots),'interior_root_upper_bound':remaining,
            'all_interior_roots_simple':True if complete else None,
            'unspent_root_budget':remaining-len(roots),'sample':sample,
            'grid':grid,'bits':bits,'evaluated_points':len(points),
            'reason':'All possible roots are accounted for.' if complete else
                     'The root budget or a strict interior sign remains unresolved.'}


def compare(old,new,bits=128,grid=64):
    source=compare_invoices(old,new)
    return {'schema':'integer-mult-power-variation/v1','contract':source['contract'],
            'quantity':source['quantity'],'signed_net_delta':source['signed_net_delta'],
            'exponent_domain':'0 < t < 1',**classify(source['signed_net_delta'],bits,grid),
            'scope':'Declared invoice arithmetic only. No source, native, compiler or kappa admission.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old');parser.add_argument('new')
    parser.add_argument('--bits',type=int,default=128)
    parser.add_argument('--grid',type=int,default=64)
    args=parser.parse_args()
    try:
        old,old_pin=load_invoice(args.old);new,new_pin=load_invoice(args.new)
        report=compare(old,new,args.bits,args.grid)
        report['inputs']={'old':old_pin,'new':new_pin}
    except (OSError,ValueError,TypeError,RecursionError) as error:
        print('Power variation comparison failed: '+str(error),file=sys.stderr)
        return 2
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
