#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Find and certify minimum common dyadic precision in a bounded linear region.

Classical interval branch-and-bound and nested-grid binary search. Prepared
for Ali Romman with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
import re
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


class BudgetEnd(Exception):
    pass


def rational(x):
    require(type(x) is int or type(x) is str and len(x)<=128
            and re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?',x,re.ASCII),'Use exact rational entries')
    q=Q(x);require(abs(q.numerator)<=10**9 and q.denominator<=10**9,'Rational limit is 10^9');return q


def read(path):
    with Path(path).open('rb') as f:raw=f.read(8*1024**2+1)
    require(len(raw)<=8*1024**2,'Input exceeds 8 MiB')
    return json.loads(raw,object_pairs_hook=_pairs,parse_int=_integer,
                      parse_float=_not_integer,parse_constant=_not_integer),sha256(raw).hexdigest()


def validate(value):
    require(type(value) is dict and value.keys()=={'schema','lower','upper','constraints','max_bits','node_budget'}
            and value['schema']=='dyadic-feasibility/v1','Invalid dyadic problem')
    raw=value['lower'];require(type(raw) is list and 1<=len(raw)<=8,'Use 1..8 parameters')
    n=len(raw)
    def vector(raw):
        require(type(raw) is list and len(raw)==n,'Wrong vector size');return [rational(x) for x in raw]
    lower,upper=vector(value['lower']),vector(value['upper'])
    require(all(lo<=hi for lo,hi in zip(lower,upper)),'Invalid box')
    require(type(value['max_bits']) is int and 0<=value['max_bits']<=30,'Use max_bits in 0..30')
    require(type(value['node_budget']) is int and 1<=value['node_budget']<=50000,'Use node_budget in 1..50000')
    rows=value['constraints'];require(type(rows) is list and len(rows)<=64,'At most 64 constraints')
    constraints=[]
    for row in rows:
        require(type(row) is dict and row.keys()=={'coefficients','bound','strict'}
                and type(row['strict']) is bool,'Invalid constraint')
        constraints.append((vector(row['coefficients']),rational(row['bound']),row['strict']))
    return lower,upper,constraints


def grid_box(lower,upper,precision):
    scale=1<<precision
    return [ceil(q*scale) for q in lower], [floor(q*scale) for q in upper]


def excludes(row,lo,hi,scale):
    a,b,strict=row
    minimum=sum((c*(l if c>=0 else h) for c,l,h in zip(a,lo,hi)),Q(0))
    return minimum>=b*scale if strict else minimum>b*scale


def satisfies(rows,point,scale):
    for a,b,strict in rows:
        total=sum((c*z for c,z in zip(a,point)),Q(0))
        if not (total<b*scale if strict else total<=b*scale):return False
    return True


def search(value):
    lower,upper,rows=validate(value);used=0;best=None;excluded=None
    def at_precision(precision):
        scale=1<<precision
        def visit(lo,hi):
            nonlocal used
            if used>=value['node_budget']:raise BudgetEnd
            used+=1
            if any(l>h for l,h in zip(lo,hi)):return None,{'empty':True}
            for i,row in enumerate(rows):
                if excludes(row,lo,hi,scale):return None,{'row':i}
            midpoint=[(l+h)//2 for l,h in zip(lo,hi)]
            if satisfies(rows,midpoint,scale):return midpoint,None
            axis=max(range(len(lo)),key=lambda i:hi[i]-lo[i]);split=midpoint[axis]
            require(lo[axis]<hi[axis],'A rejected singleton must have a violated row')
            left_hi=hi[:];left_hi[axis]=split
            point,left=visit(lo,left_hi)
            if point is not None:return point,None
            right_lo=lo[:];right_lo[axis]=split+1
            point,right=visit(right_lo,hi)
            if point is not None:return point,None
            return None,{'axis':axis,'split':split,'left':left,'right':right}
        return visit(*grid_box(lower,upper,precision))
    try:
        high=value['max_bits'];point,tree=at_precision(high)
        if point is None:
            excluded={'bits':high,'tree':tree};status='infeasible_through_limit'
        else:
            best={'bits':high,'numerators':point};low=-1
            while high>low+1:
                mid=(low+high)//2;point,tree=at_precision(mid)
                if point is None:low=mid;excluded={'bits':mid,'tree':tree}
                else:high=mid;best={'bits':mid,'numerators':point}
            status='minimal'
    except BudgetEnd:
        status='unresolved'
    result={'schema':'dyadic-parameter-certificate/v1','status':status,'feasible':best,'infeasible':excluded,
            'minimum_bits_lower':excluded['bits']+1 if excluded else 0,
            'minimum_bits_upper':best['bits'] if best else None,'nodes':used}
    verify(value,result);return result


def verify(value,result):
    """Check an attaining point and complete exclusion tree; do not search."""
    lower,upper,rows=validate(value);n=len(lower)
    require(type(result) is dict and result.get('schema')=='dyadic-parameter-certificate/v1','Invalid certificate')
    used=result.get('nodes');require(type(used) is int and 1<=used<=value['node_budget'],'Invalid node count')
    feasible,infeasible=result.get('feasible'),result.get('infeasible');checked=0
    def precision(item):
        require(type(item) is dict and type(item.get('bits')) is int and 0<=item['bits']<=value['max_bits'],
                'Invalid precision');return item['bits']
    if feasible is not None:
        p=precision(feasible);point=feasible.get('numerators')
        require(type(point) is list and len(point)==n and all(type(z) is int for z in point),'Invalid dyadic point')
        lo,hi=grid_box(lower,upper,p)
        require(all(l<=z<=h for l,z,h in zip(lo,point,hi)) and satisfies(rows,point,1<<p),'False feasible point')
    if infeasible is not None:
        p=precision(infeasible);scale=1<<p
        def check(tree,lo,hi):
            nonlocal checked
            checked+=1;require(checked<=used,'Exclusion tree exceeds reported work')
            require(type(tree) is dict,'Invalid exclusion node')
            if tree.keys()=={'empty'}:
                require(tree['empty'] is True and any(l>h for l,h in zip(lo,hi)),'Box is not empty');return
            if tree.keys()=={'row'}:
                i=tree['row'];require(type(i) is int and 0<=i<len(rows) and excludes(rows[i],lo,hi,scale),
                                      'Row does not exclude the whole box');return
            require(tree.keys()=={'axis','split','left','right'},'Invalid partition node')
            axis,split=tree['axis'],tree['split']
            require(type(axis) is int and 0<=axis<n and type(split) is int and lo[axis]<=split<hi[axis],
                    'Invalid partition boundary')
            left_hi=hi[:];left_hi[axis]=split;right_lo=lo[:];right_lo[axis]=split+1
            check(tree['left'],lo,left_hi);check(tree['right'],right_lo,hi)
        check(infeasible.get('tree'),*grid_box(lower,upper,p))
    lo=infeasible['bits']+1 if infeasible else 0;hi=feasible['bits'] if feasible else None
    require(type(result.get('minimum_bits_lower')) is int
            and (result.get('minimum_bits_upper') is None or type(result['minimum_bits_upper']) is int)
            and result.get('minimum_bits_lower')==lo and result.get('minimum_bits_upper')==hi
            and (hi is None or lo<=hi),'False minimum-precision bracket')
    status=result.get('status')
    if status=='minimal':require(hi is not None and lo==hi,'Minimum not established')
    elif status=='infeasible_through_limit':require(hi is None and lo==value['max_bits']+1,'Limit not excluded')
    else:require(status=='unresolved' and used==value['node_budget'],'Invalid unresolved status')
    return True


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('problem');parser.add_argument('--check')
    args=parser.parse_args(argv)
    try:
        value,digest=read(args.problem)
        if args.check:
            result,_=read(args.check)
            require(type(result) is dict and result.get('input_sha256')==digest,'Problem bytes changed')
            verify(value,result);print('PASS_DYADIC_PARAMETER_CERTIFICATE')
        else:
            result=search(value);result['input_sha256']=digest;print(json.dumps(result,sort_keys=True,separators=(',',':')))
    except (OSError,ValueError,TypeError,KeyError,RecursionError,ZeroDivisionError) as exc:
        print(str(exc),file=sys.stderr);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
