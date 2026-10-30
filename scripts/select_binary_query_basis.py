#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct and certify a minimum-cost basis of a binary query span.

Classical weighted matroid greedy algorithm and fundamental-circuit criterion.
Prepared for Ali Romman with substantial OpenAI Codex assistance.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


def bits(text, width):
    require(type(text) is str and len(text) <= 64 and re.fullmatch(r'0|[1-9a-f][0-9a-f]*',text,re.ASCII),
            'Use canonical lowercase hexadecimal without 0x')
    value=int(text,16);require(value.bit_length()<=width,'Vector exceeds width');return value


def read(path):
    with Path(path).open('rb') as f:raw=f.read(2*1024**2+1)
    require(len(raw)<=2*1024**2,'Input exceeds 2 MiB')
    return json.loads(raw,object_pairs_hook=_pairs,parse_int=_integer,
                      parse_float=_not_integer,parse_constant=_not_integer),sha256(raw).hexdigest()


def validate(value):
    require(type(value) is dict and value.keys()=={'schema','width','vectors'}
            and value['schema']=='binary-query-basis/v1','Invalid basis problem')
    width=value['width'];rows=value['vectors']
    require(type(width) is int and 1<=width<=256,'Use width 1..256')
    require(type(rows) is list and 1<=len(rows)<=4096,'Use 1..4096 vectors')
    vectors,costs=[],[]
    for row in rows:
        require(type(row) is dict and row.keys()=={'bits','cost'},'Invalid query')
        require(type(row['cost']) is int and 0<=row['cost']<=10**12,'Invalid acquisition cost')
        vectors.append(bits(row['bits'],width));costs.append(row['cost'])
    return width,vectors,costs


def reduce(vector, pivots):
    coefficients=0
    for pivot,(row,mask) in sorted(pivots.items(),reverse=True):
        if vector>>pivot&1:vector^=row;coefficients^=mask
    return vector,coefficients


def dual_forms(basis,width):
    rows=basis[:];transform=[1<<i for i in range(len(rows))];pivots=[]
    for column in range(width):
        k=len(pivots);at=next((i for i in range(k,len(rows)) if rows[i]>>column&1),None)
        if at is None:continue
        rows[k],rows[at]=rows[at],rows[k];transform[k],transform[at]=transform[at],transform[k]
        for i in range(len(rows)):
            if i!=k and rows[i]>>column&1:rows[i]^=rows[k];transform[i]^=transform[k]
        pivots.append(column)
    return [sum(((transform[j]>>i)&1)<<p for j,p in enumerate(pivots)) for i in range(len(rows))]


def select(value):
    width,vectors,costs=validate(value);chosen=[];pivots={}
    for i in sorted(range(len(vectors)),key=lambda i:(costs[i],i)):
        remaining,mask=reduce(vectors[i],pivots)
        if remaining:
            pivots[remaining.bit_length()-1]=(remaining,mask^(1<<len(chosen)));chosen.append(i)
    representations=[reduce(v,pivots)[1] for v in vectors]
    result={'schema':'binary-query-basis-certificate/v1','selected':chosen,
            'cost':sum(costs[i] for i in chosen),'representations':[format(x,'x') for x in representations],
            'dual':[format(x,'x') for x in dual_forms([vectors[i] for i in chosen],width)]}
    verify(value,result);return result


def verify(value,result):
    """Check independence, full-span expressions and every improving exchange."""
    width,vectors,costs=validate(value)
    require(type(result) is dict and result.get('schema')=='binary-query-basis-certificate/v1','Invalid certificate')
    chosen=result.get('selected')
    require(type(chosen) is list and len(chosen)<=width
            and all(type(i) is int and 0<=i<len(vectors) for i in chosen)
            and len(chosen)==len(set(chosen)),'Invalid selected basis')
    r=len(chosen);raw=result.get('dual');expressions=result.get('representations')
    require(type(raw) is list and len(raw)==r,'Invalid dual forms')
    dual=[bits(x,width) for x in raw]
    for i,form in enumerate(dual):
        for j,index in enumerate(chosen):
            require((form&vectors[index]).bit_count()%2==int(i==j),'Basis independence witness is false')
    require(type(expressions) is list and len(expressions)==len(vectors),'Incomplete query coverage')
    for i,text in enumerate(expressions):
        mask=bits(text,r);reconstructed=0
        while mask:
            low=mask&-mask;j=low.bit_length()-1;mask^=low
            reconstructed^=vectors[chosen[j]]
            require(costs[i]>=costs[chosen[j]],'A cheaper basis exchange exists')
        require(reconstructed==vectors[i],'False query representation')
    require(type(result.get('cost')) is int and result['cost']==sum(costs[i] for i in chosen),'Wrong total cost')
    return True


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('problem');parser.add_argument('--check')
    args=parser.parse_args(argv)
    try:
        value,digest=read(args.problem)
        if args.check:
            result,_=read(args.check)
            require(type(result) is dict and result.get('input_sha256')==digest,'Problem bytes changed')
            verify(value,result);print('PASS_MINIMUM_BINARY_QUERY_BASIS')
        else:
            result=select(value);result['input_sha256']=digest;print(json.dumps(result,indent=2,sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError,RecursionError) as exc:
        print(str(exc),file=sys.stderr);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
