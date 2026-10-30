#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compute an exact two-fee region that preserves increasing concave cost order.

Retain the classical hinge-order and signed-invoice tool credits.
Prepared for Ali Romman with OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import compare_invoices,load_invoice,validate_invoice,require,MAX_COUNT
finally:
    sys.path.pop(0)


def clip(polygon,a,b,c):
    """Intersect a convex polygon with a*x+b*y<=c, using rational arithmetic."""
    if not polygon:return []
    output=[]
    previous=polygon[-1];pv=a*previous[0]+b*previous[1]-c
    for current in polygon:
        cv=a*current[0]+b*current[1]-c
        if (pv<=0)!=(cv<=0):
            ratio=pv/(pv-cv)
            output.append(tuple(previous[i]+ratio*(current[i]-previous[i]) for i in (0,1)))
        if cv<=0:output.append(current)
        previous,pv=current,cv
    clean=[]
    for point in output:
        if not clean or point!=clean[-1]:clean.append(point)
    if len(clean)>1 and clean[0]==clean[-1]:clean.pop()
    return clean


def region(old,new,fee_a,fee_b,fixed_a=None):
    comparison=compare_invoices(old,new)
    fees=[validate_invoice(f,'fee') for f in (fee_a,fee_b)]
    for fee in fees:
        require(fee['contract']==comparison['contract'],'fee contract differs')
        require(not fee['targets'] and bool(fee['paid']),'fee must be nonzero and paid-only')
    if fixed_a is not None:
        require(type(fixed_a) is int and 0<=fixed_a<=MAX_COUNT,'fixed A must be an integer in 0..10^60')
    delta=comparison['signed_net_delta']
    ranks=sorted({int(r) for h in (delta,fees[0]['paid'],fees[1]['paid']) for r in h})
    require(len(ranks)<=512,'fee regions support at most 512 distinct ranks')
    hinge=lambda hist,k:sum(n*min(int(r),k) for r,n in hist.items())
    constraints=[{'rank':k,'a':hinge(fees[0]['paid'],k),'b':hinge(fees[1]['paid'],k),
                  'budget':-hinge(delta,k)} for k in ranks]
    bad=next((row for row in constraints if row['budget']<0),None)
    result={'schema':'integer-mult-recursive-fee-region/v1','contract':comparison['contract'],
            'constraints':constraints,'feasible':bad is None,
            'scope':'Exact weak order for all increasing concave tariffs with f(0)=0. '
                    'Fractional multiplicities describe a relaxation; actual fees need integers. '
                    'Source legality and complete kappa admission are not verified.'}
    if bad:
        result['obstruction']=bad;result['vertices']=[];return result
    xmax=min(Q(r['budget'],r['a']) for r in constraints)
    ymax=min(Q(r['budget'],r['b']) for r in constraints)
    polygon=[(Q(0),Q(0))] if xmax==0 else [(Q(0),Q(0)),(xmax,Q(0)),(xmax,ymax),(Q(0),ymax)]
    for row in constraints:polygon=clip(polygon,row['a'],row['b'],Q(row['budget']))
    result['vertices']=[{'a':str(x),'b':str(y),
                         'binding_ranks':[r['rank'] for r in constraints if r['a']*x+r['b']*y==r['budget']]}
                        for x,y in polygon]
    result['axis_bounds']={'a':str(xmax),'b':str(ymax)}
    if fixed_a is not None:
        limits=[(Q(r['budget']-r['a']*fixed_a,r['b']),r['rank']) for r in constraints]
        bound=min(value for value,k in limits)
        result['fixed_a']={'a':fixed_a,'feasible':bound>=0,'b_upper':str(bound),
                           'limiting_ranks':[k for value,k in limits if value==bound]}
        if bound>=0:
            whole=bound.numerator//bound.denominator
            result['fixed_a']['max_whole_b']=whole
            result['fixed_a']['next_b_rejected_at']=[r['rank'] for r in constraints
                if r['a']*fixed_a+r['b']*(whole+1)>r['budget']]
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('old','new','fee_a','fee_b'):parser.add_argument(name)
    parser.add_argument('--fixed-a',type=int)
    args=parser.parse_args(argv)
    try:
        inputs={};invoices=[]
        for name in ('old','new','fee_a','fee_b'):
            invoice,pin=load_invoice(getattr(args,name));invoices.append(invoice);inputs[name]=pin
        result=region(*invoices,fixed_a=args.fixed_a);result['inputs']=inputs
    except (OSError,ValueError,TypeError,RecursionError) as exc:
        print(json.dumps({'status':'INVALID_FEE_REGION','error':str(exc)}),file=sys.stderr);return 2
    print(json.dumps(result,indent=2,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
