#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct an exact optimum and dual witness for a bounded feasible LP.

Classical vertex enumeration and linear-programming duality. Prepared for
Ali Romman with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import re
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


def rational(x):
    require(type(x) is int or type(x) is str and len(x)<=1024
            and re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?',x,re.ASCII),'Use exact rational entries')
    return Q(x)


def vector(raw,n):
    require(type(raw) is list and len(raw)==n,'Wrong vector size')
    return [rational(x) for x in raw]


def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))


def read(path):
    with Path(path).open('rb') as f:raw=f.read(1024**2+1)
    require(len(raw)<=1024**2,'Input exceeds 1 MiB')
    return json.loads(raw,object_pairs_hook=_pairs,parse_int=_integer,
                      parse_float=_not_integer,parse_constant=_not_integer),sha256(raw).hexdigest()


def validate(value):
    require(type(value) is dict and value.keys()=={'schema','objective','lower','upper','constraints','feasible'}
            and value['schema']=='rational-box-lp/v1','Invalid bounded LP')
    require(type(value['objective']) is list and 1<=len(value['objective'])<=6,'Use 1..6 parameters')
    n=len(value['objective']);c=vector(value['objective'],n)
    lower,upper,seed=(vector(value[name],n) for name in ('lower','upper','feasible'))
    require(all(lo<=hi for lo,hi in zip(lower,upper)),'Empty declared box')
    constraints=value['constraints'];require(type(constraints) is list and len(constraints)+2*n<=24,'At most 24 total rows')
    rows=[];bounds=[]
    for item in constraints:
        require(type(item) is dict and item.keys()=={'coefficients','bound'},'Invalid constraint')
        rows.append(vector(item['coefficients'],n));bounds.append(rational(item['bound']))
    for i in range(n):
        unit=[Q(j==i) for j in range(n)];rows.append(unit);bounds.append(upper[i])
        rows.append([-x for x in unit]);bounds.append(-lower[i])
    require(comb(len(rows),n)<=50000,'Active-basis bound exceeds 50000')
    require(all(abs(x.numerator)<=10**9 and x.denominator<=10**9
                for row in rows+[bounds,c,seed] for x in row),'Input rational limit is 10^9')
    require(all(dot(row,seed)<=bound for row,bound in zip(rows,bounds)),'The supplied incumbent is infeasible')
    return rows,bounds,c,seed


def solve(a,b):
    n=len(a);rows=[row[:]+[rhs] for row,rhs in zip(a,b)]
    for k in range(n):
        pivot=next((i for i in range(k,n) if rows[i][k]),None)
        if pivot is None:return None
        rows[k],rows[pivot]=rows[pivot],rows[k];d=rows[k][k];rows[k]=[x/d for x in rows[k]]
        for i in range(n):
            if i!=k and rows[i][k]:
                factor=rows[i][k];rows[i]=[x-factor*y for x,y in zip(rows[i],rows[k])]
    return [row[-1] for row in rows]


def optimize(value):
    rows,bounds,c,seed=validate(value);n=len(c);count=0
    if not any(c):
        point,dual=seed,[Q(0)]*len(rows)
    else:
        point=dual=None
        for indices in combinations(range(len(rows)),n):
            count+=1;active=[rows[i] for i in indices]
            candidate=solve(active,[bounds[i] for i in indices])
            if candidate is None or any(dot(row,candidate)>b for row,b in zip(rows,bounds)):continue
            multipliers=solve([list(column) for column in zip(*active)],c)
            if any(x<0 for x in multipliers):continue
            point=candidate;dual=[Q(0)]*len(rows)
            for i,x in zip(indices,multipliers):dual[i]=x
            break
        require(point is not None,'No primal-dual vertex found in the complete bounded search')
    result={'schema':'rational-box-optimum/v1','point':list(map(str,point)),
            'dual':list(map(str,dual)),'objective':str(dot(c,point)),'bases_examined':count}
    verify(value,result);return result


def verify(value,result):
    """Check feasibility and a matching dual upper bound without vertex search."""
    rows,bounds,c,_=validate(value);n=len(c)
    require(type(result) is dict and result.get('schema')=='rational-box-optimum/v1','Invalid optimum certificate')
    point=vector(result.get('point'),n);dual=vector(result.get('dual'),len(rows))
    require(all(dot(row,point)<=b for row,b in zip(rows,bounds)),'Point violates a constraint')
    require(all(y>=0 for y in dual),'Negative dual multiplier')
    require(all(sum((dual[i]*rows[i][j] for i in range(len(rows))),Q(0))==c[j] for j in range(n)),
            'Dual does not reconstruct objective')
    objective=rational(result.get('objective'))
    require(objective==dot(c,point)==dot(bounds,dual),'Primal and dual objectives differ')
    return True


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('problem');parser.add_argument('--check')
    args=parser.parse_args(argv)
    try:
        value,digest=read(args.problem)
        if args.check:
            result,_=read(args.check)
            require(type(result) is dict and result.get('input_sha256')==digest,'Problem bytes changed')
            verify(value,result);print('PASS_RATIONAL_BOX_OPTIMUM')
        else:
            result=optimize(value);result['input_sha256']=digest;print(json.dumps(result,indent=2,sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError,RecursionError,ZeroDivisionError) as exc:
        print(str(exc),file=sys.stderr);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
