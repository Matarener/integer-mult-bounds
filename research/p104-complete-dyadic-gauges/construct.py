"""Bind every actual scalar coefficient to an anchored representation graph.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source P104 word retains inputs/NOTICE.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import json


def need(ok,reason):
    if not ok:raise ValueError(reason)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def exponent(q):
    n=abs(q.numerator);e=1-q.denominator.bit_length()
    while n%2==0:n//=2;e+=1
    return e


def graph(word):
    public=word['public'];active={r:r+1 for r in range(public)};initial=dict(active)
    signs={i:1 for i in range(public+1)};count=public;edges=Counter();nodes=[]
    for a in initial.values():edges[a,0,0]+=1
    for event in word['program']:
        op,r=event[:2];a=active.get(r,0);b=0
        if op=='INIT':
            count+=1;a=count;active[r]=a;signs[a]=1
        elif op=='CLEAR':del active[r]
        elif op in ('ADD','COPY','SCALE'):
            q=Q(event[-2])
            if op=='SCALE':
                b=a;count+=1;a=count;active[r]=a;signs[a]=signs[b]*(-1 if q<0 else 1)
            else:b=active[event[2]]
            edges[a,b,exponent(q)]+=1
        nodes.append([a,b])
    need(set(active)==set(range(public)),'all owned epochs closed')
    for a in active.values():edges[0,a,0]+=1
    return {'nodes':nodes,'signs':signs,'initial':initial,'final':active,'count':count,
            'edges':[[a,b,e,w] for (a,b,e),w in sorted(edges.items())]}


def verify_dual(data,certificate):
    need(certificate.get('schema')=='p104-gauge-dual/1','dual schema')
    x=certificate['potentials'];y=certificate['dual']
    need(len(x)==data['count']+1 and x[0]==0 and all(type(v) is int and abs(v)<=128 for v in x),'exact potential vector')
    need(len(y)==len(data['edges']) and all(type(v) is int for v in y),'exact dual vector')
    balance=[0]*len(x);primal=dual=0
    for (a,b,e,w),v in zip(data['edges'],y):
        need(abs(v)<=w,'dual capacity')
        balance[a]+=v;balance[b]-=v
        primal+=w*abs(e+x[a]-x[b]);dual+=e*v
    need(not any(balance),'dual conservation')
    need(primal==dual==certificate['objective'],'matching unbounded primal and dual')
    return x,primal


def build(source,data,powers,local):
    gauge={n:Q(s)*Q(2)**powers[n] for n,s in data['signs'].items()}
    word=deepcopy(source);word['program']=[];edits=[];boundaries=[];native=[]
    n=source['public']+source['owned_fields']
    original=[{i:Q(1)} for i in range(n)];changed=deepcopy(original)
    for r,a in data['initial'].items():
        q=gauge[a]
        if q!=1:
            event=['SCALE',r,str(q),source['initial'][r]]
            word['program'].append(event);boundaries.append(['entry',event])
        changed[r]={r:q}
    for i,(old,(a,b)) in enumerate(zip(source['program'],data['nodes'])):
        op,r=old[:2];new=list(old)
        if op in ('INIT','CLEAR'):original[r]={};changed[r]={}
        elif op=='MOVE':
            need(changed[r]=={j:gauge[a]*v for j,v in original[r].items()},'every native input gauge')
            native.append([old,str(gauge[a])])
        else:
            q=Q(old[-2]);adjusted=q*gauge[a]/gauge[b];new[-2]=str(adjusted)
            if op=='SCALE':
                original[r]={j:q*v for j,v in original[r].items()}
                changed[r]={j:adjusted*v for j,v in changed[r].items()}
            elif op=='COPY':
                original[r]={j:q*v for j,v in original[old[2]].items()}
                changed[r]={j:adjusted*v for j,v in changed[old[2]].items()}
            else:
                local.add(original[r],original[old[2]],q)
                local.add(changed[r],changed[old[2]],adjusted)
            need(changed[r]=={j:gauge[a]*v for j,v in original[r].items()},'every scalar representation invariant')
        if op=='SCALE' and Q(new[-2])==1:edits.append([i,old,None])
        else:
            word['program'].append(new)
            if new!=old:edits.append([i,old,new])
    for r,a in data['final'].items():
        q=1/gauge[a]
        if q!=1:
            event=['SCALE',r,str(q),source['final'][r]]
            word['program'].append(event);boundaries.append(['exit',event])
        changed[r]={j:q*v for j,v in changed[r].items()}
    need(changed==original,'all public and dirty-owned boundary values')
    return word,edits,boundaries,native
