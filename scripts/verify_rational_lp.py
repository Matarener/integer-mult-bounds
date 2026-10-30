#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay exact certificates for max c*x subject to A*x<=b and x>=0.

This checks supplied rational witnesses; it does not run an optimization solver.
Credits: weak LP duality and Farkas' lemma. Ali Romman with OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import require,_pairs,_integer,_not_integer
finally:
    sys.path.pop(0)


def rational(value):
    require((type(value) is int and abs(value)<=10**60) or
            (type(value) is str and len(value)<=128 and
             re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?',value) is not None),
            'use bounded integers or integer-fraction strings')
    return Q(value)


def vector(value,size,label):
    require(type(value) is list and len(value)==size,label+' dimension differs')
    return [rational(x) for x in value]


def model(problem):
    require(type(problem) is dict and problem.keys()=={'schema','contract','variables','constraints','objective'} and
            problem['schema']=='integer-mult-rational-lp/v1','invalid LP schema')
    require(type(problem['contract']) is str and 0<len(problem['contract'])<=4096,'invalid model contract')
    names=problem['variables'];rows=problem['constraints']
    require(type(names) is list and 1<=len(names)<=128 and
            all(type(s) is str and 0<len(s)<=128 for s in names) and len(set(names))==len(names),
            'provide 1..128 distinct variable names')
    require(type(rows) is list and 1<=len(rows)<=128,'provide 1..128 constraints')
    ids=[];A=[];b=[]
    for row in rows:
        require(type(row) is dict and row.keys()=={'id','coefficients','upper'},'invalid constraint fields')
        name=row['id']
        require(type(name) is str and 0<len(name)<=128 and name not in ids,'constraint IDs must be unique')
        ids.append(name);A.append(vector(row['coefficients'],len(names),'constraint'));b.append(rational(row['upper']))
    c=vector(problem['objective'],len(names),'objective')
    return A,b,c,names,ids


def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))


def verify(problem,certificate):
    A,b,c,names,ids=model(problem);n=len(c);m=len(b)
    require(type(certificate) is dict and certificate.get('schema')=='integer-mult-lp-certificate/v1',
            'invalid certificate schema')
    kind=certificate.get('kind')
    fields={'bounds':{'primal','dual'},'infeasible':{'dual'},'unbounded':{'primal','ray'}}
    require(type(kind) is str and kind in fields and certificate.keys()==fields[kind]|{'schema','kind'},
            'invalid certificate kind or fields')
    result={'schema':'integer-mult-lp-replay/v1','kind':kind,'valid':True,
            'scope':'Exact certificate for this declared continuous linear program only. '
                    'It does not prove that the constraints cover a source construction, '
                    'a larger search family, or complete kappa admission.'}
    if 'primal' in certificate:
        x=vector(certificate['primal'],n,'primal')
        slack=[bound-dot(row,x) for row,bound in zip(A,b)]
        require(all(v>=0 for v in x),'negative primal variable')
        require(all(v>=0 for v in slack),'primal violates a constraint')
        result['primal_slack']={name:str(v) for name,v in zip(ids,slack)}
        result['primal_value']=str(dot(c,x))
        result['primal_integral']=all(v.denominator==1 for v in x)
    if 'dual' in certificate:
        y=vector(certificate['dual'],m,'dual')
        require(all(v>=0 for v in y),'negative dual multiplier')
        weighted=[sum((A[i][j]*y[i] for i in range(m)),Q(0)) for j in range(n)]
        bound=dot(b,y)
        result['dual_value']=str(bound)
        if kind=='bounds':
            reduced=[a-cost for a,cost in zip(weighted,c)]
            require(all(v>=0 for v in reduced),'dual does not bound the objective')
            gap=bound-dot(c,x)
            require(gap>=0,'negative primal-dual gap')
            result['dual_slack']={name:str(v) for name,v in zip(names,reduced)}
            result['gap']=str(gap);result['optimal']=gap==0
        else:
            require(all(v>=0 for v in weighted),'Farkas coefficients must be nonnegative')
            require(bound<0,'Farkas right side must be strictly negative')
            result['weighted_coefficients']={name:str(v) for name,v in zip(names,weighted)}
    if kind=='unbounded':
        ray=vector(certificate['ray'],n,'ray');changes=[dot(row,ray) for row in A]
        require(all(v>=0 for v in ray),'ray leaves the nonnegative orthant')
        require(all(v<=0 for v in changes),'ray increases a constrained left side')
        gain=dot(c,ray);require(gain>0,'ray must strictly improve the objective')
        result['ray_gain']=str(gain);result['constraint_changes']={name:str(v) for name,v in zip(ids,changes)}
    return result


def load(path):
    with Path(path).open('rb') as stream:raw=stream.read(4*1024*1024+1)
    require(len(raw)<=4*1024*1024,'input exceeds 4 MiB')
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,parse_int=_integer,
                     parse_float=_not_integer,parse_constant=_not_integer)
    return value,{'path':str(path),'bytes':len(raw),'sha256':sha256(raw).hexdigest()}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem');parser.add_argument('certificate');args=parser.parse_args(argv)
    try:
        problem,pin=load(args.problem);certificate,receipt=load(args.certificate)
        result=verify(problem,certificate);result['inputs']={'problem':pin,'certificate':receipt}
        result['contract']=problem['contract']
    except (OSError,ValueError,TypeError,RecursionError,ZeroDivisionError) as exc:
        print(json.dumps({'status':'INVALID_LP_CERTIFICATE','error':str(exc)}),file=sys.stderr);return 2
    print(json.dumps(result,indent=2,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
