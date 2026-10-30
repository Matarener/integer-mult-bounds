#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct a minimum-cost complete binary linear word on at most four roles.

Classical finite-group shortest paths and feasible potentials. Project context:
zero-frame target-feedback censuses. Prepared for Ali Romman with OpenAI Codex.
"""
import argparse
from hashlib import sha256
import heapq
import json
from pathlib import Path
import re
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


def read(path):
    with Path(path).open('rb') as f:raw=f.read(4*1024**2+1)
    require(len(raw)<=4*1024**2,'Input exceeds 4 MiB')
    return json.loads(raw,object_pairs_hook=_pairs,parse_int=_integer,
                      parse_float=_not_integer,parse_constant=_not_integer),sha256(raw).hexdigest()


def validate(value):
    require(type(value) is dict and value.keys()=={'schema','width','target','gates'}
            and value['schema']=='binary-linear-synthesis/v1','Invalid synthesis problem')
    n=value['width'];require(type(n) is int and 1<=n<=4,'Use 1..4 arbitrary roles')
    target=value['target'];gates=value['gates']
    require(type(target) is list and len(target)==n and all(type(r) is int and 0<=r<1<<n for r in target),
            'Target must contain one binary row mask per output')
    require(type(gates) is list and len(gates)<=18,'At most 18 gates')
    seen=set()
    for gate in gates:
        require(type(gate) is dict and gate.keys()=={'op','src','dst','cost'} and gate['op'] in ('xor','swap'),
                'Invalid gate')
        a,b=gate['src'],gate['dst']
        require(type(a) is int and type(b) is int and 0<=a<n and 0<=b<n and a!=b,'Invalid gate roles')
        require(type(gate['cost']) is int and 1<=gate['cost']<=10**9,'Gate costs must be in 1..10^9')
        key=(gate['op'],a,b) if gate['op']=='xor' else ('swap',min(a,b),max(a,b))
        require(key not in seen,'Duplicate generator');seen.add(key)
    start=sum((1<<i)<<(n*i) for i in range(n))
    goal=sum(row<<(n*i) for i,row in enumerate(target))
    return n,gates,start,goal


def step(state,gate,n):
    mask=(1<<n)-1;a,b=gate['src'],gate['dst']
    src=(state>>(a*n))&mask;dst=(state>>(b*n))&mask
    if gate['op']=='xor':return state^(src<<(b*n))
    change=src^dst;return state^(change<<(a*n))^(change<<(b*n))


def synthesize(value):
    n,gates,start,goal=validate(value);distance={start:0};previous={};queue=[(0,start)]
    while queue:
        cost,state=heapq.heappop(queue)
        if distance[state]!=cost:continue
        for i,gate in enumerate(gates):
            after=step(state,gate,n);candidate=cost+gate['cost']
            if after not in distance or candidate<distance[after]:
                distance[after]=candidate;previous[after]=(state,i);heapq.heappush(queue,(candidate,after))
    word=[]
    if goal in distance:
        state=goal
        while state!=start:
            state,i=previous[state];word.append(i)
        word.reverse()
    result={'schema':'binary-linear-word-certificate/v1','status':'optimal' if goal in distance else 'unreachable',
            'word':word,'cost':distance.get(goal),'potential':{format(s,'x'):distance[s] for s in sorted(distance)}}
    verify(value,result);return result


def verify(value,result):
    """Check graph closure/potentials and replay literal bits on every input."""
    n,gates,start,goal=validate(value)
    require(type(result) is dict and result.get('schema')=='binary-linear-word-certificate/v1','Invalid certificate')
    raw=result.get('potential');require(type(raw) is dict and 1<=len(raw)<=1<<(n*n),'Invalid potential table')
    distance={}
    for key,cost in raw.items():
        require(type(key) is str and len(key)<=4 and re.fullmatch(r'0|[1-9a-f][0-9a-f]*',key,re.ASCII),
                'Invalid state key')
        state=int(key,16)
        require(state<1<<(n*n) and type(cost) is int and 0<=cost<=10**15,'Invalid state potential')
        distance[state]=cost
    require(distance.get(start)==0,'Initial potential must be zero')
    for state,cost in distance.items():
        for gate in gates:
            after=step(state,gate,n)
            require(after in distance and distance[after]<=cost+gate['cost'],'Missing state or false potential')
    if result.get('status')=='unreachable':
        require(goal not in distance and result.get('word')==[] and result.get('cost') is None,'False unreachability')
        return True
    require(result.get('status')=='optimal' and goal in distance,'Invalid status')
    word=result.get('word')
    require(type(word) is list and len(word)<1<<(n*n)
            and all(type(i) is int and 0<=i<len(gates) for i in word),'Invalid word')
    cost=sum(gates[i]['cost'] for i in word)
    require(type(result.get('cost')) is int and result['cost']==cost==distance[goal],'Cost does not attain lower bound')
    for input_value in range(1<<n):
        registers=[(input_value>>i)&1 for i in range(n)]
        for i in word:
            gate=gates[i];a,b=gate['src'],gate['dst']
            if gate['op']=='xor':registers[b]^=registers[a]
            else:registers[a],registers[b]=registers[b],registers[a]
        expected=[(row&input_value).bit_count()%2 for row in value['target']]
        require(registers==expected,'Word fails a complete arbitrary-input endpoint')
    return True


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('problem');parser.add_argument('--check')
    args=parser.parse_args(argv)
    try:
        value,digest=read(args.problem)
        if args.check:
            result,_=read(args.check)
            require(type(result) is dict and result.get('input_sha256')==digest,'Problem bytes changed')
            verify(value,result);print('PASS_OPTIMAL_BINARY_LINEAR_WORD')
        else:
            result=synthesize(value);result['input_sha256']=digest;print(json.dumps(result,indent=2,sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError,RecursionError) as exc:
        print(str(exc),file=sys.stderr);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
