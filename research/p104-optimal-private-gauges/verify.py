"""Construct a globally optimal dyadic gauge in the stated private grammar.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Source P104 and exact min-cut credits remain in inputs/NOTICE and vendor.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def exponent(q):
    n=abs(q.numerator);e=1-q.denominator.bit_length()
    while n%2==0:
        n//=2;e+=1
    return e


def graph(word):
    active={};signs={0:1};rows=[];edges=Counter();count=0
    for event in word['program']:
        op,r=event[:2];a=active.get(r,0);b=0
        if op=='INIT':
            count+=1;a=count;active[r]=a;signs[a]=1
        elif op=='CLEAR':
            del active[r]
        elif op in ('ADD','COPY','SCALE'):
            q=Q(event[-2])
            if op=='SCALE':
                b=a
                if a:
                    count+=1;a=count;active[r]=a;signs[a]=signs[b]*(-1 if q<0 else 1)
            else:
                b=active.get(event[2],0)
            if a or b:
                edges[a,b,exponent(q)]+=1
        rows.append([a,b])
    components=[];todo=set(range(1,count+1))
    while todo:
        comp={min(todo)}
        while True:
            grown=comp|{b for a,b,e in edges if a in comp and b}|{a for a,b,e in edges if b in comp and a}
            if grown==comp:break
            comp=grown
        need(any((a in comp and not b) or (b in comp and not a) for a,b,e in edges),
             'each gauge component has a public anchor')
        components.append(sorted(comp));todo-=comp
    return rows,signs,edges,components


def optimize_component(component, edges, cut):
    terms=[(a,b,e,w) for (a,b,e),w in sorted(edges.items()) if a in component or b in component]
    bound=len(component)*max(abs(e) for a,b,e,w in terms)
    if not bound:
        return {n:0 for n in component},{'nodes':component,'bound':0,'energy':0}
    ids={(n,k):i for i,(n,k) in enumerate((n,k) for n in component for k in range(1-bound,bound+1))}
    unary=[[0,0] for _ in ids];pairs=Counter();constant=0
    def bit(n,k):
        if n==0:return ('fixed',int(0>=k))
        if k<=-bound:return ('fixed',1)
        if k>bound:return ('fixed',0)
        return ('variable',ids[n,k])
    for a,b,e,w in terms:
        for t in range(min(-bound+e,-bound)+1,max(bound+e,bound)+1):
            u,v=bit(a,t-e),bit(b,t)
            if u==v:continue
            if u[0]==v[0]=='variable':
                i,j=sorted([u[1],v[1]]);pairs[i,j]+=w
            elif u[0]==v[0]=='fixed':
                constant+=w*abs(u[1]-v[1])
            else:
                var,fixed=(u,v) if u[0]=='variable' else (v,u)
                unary[var[1]][1-fixed[1]]+=w
    table=[{'i':i,'j':j,'costs':[0,w,w,0]} for (i,j),w in sorted(pairs.items())]
    barrier=1+sum(w*abs(e) for a,b,e,w in terms)
    for node in component:
        for k in range(1-bound,bound):
            table.append({'i':ids[node,k],'j':ids[node,k+1],'costs':[0,barrier,0,0]})
    problem={'schema':'submodular-binary-costs/v1','unary':unary,'pairs':table,'fixed':[None]*len(ids)}
    certificate=cut.optimize(problem)
    values={n:-bound+sum(certificate['assignment'][ids[n,k]] for k in range(1-bound,bound+1)) for n in component}
    for n in component:
        need(all(certificate['assignment'][ids[n,k]]==int(values[n]>=k) for k in range(1-bound,bound+1)),
             'monotone threshold reconstruction')
    all_values={0:0,**values}
    direct=sum(w*abs(e+all_values[a]-all_values[b]) for a,b,e,w in terms)
    need(direct==constant+certificate['energy'],'exact integer gauge objective')
    return values,{'nodes':component,'bound':bound,'constant':constant,'energy':direct,
                   'problem':problem,'certificate':certificate}


def construct(source, local, cut):
    nodes,signs,edges,components=graph(source)
    powers={0:0};certificates=[]
    for component in components:
        values,certificate=optimize_component(component,edges,cut)
        powers.update(values);certificates.append(certificate)
    gauge={n:Q(signs[n])*Q(2)**x for n,x in powers.items()}
    word=deepcopy(source);word['program']=[];edits=[]
    original=[{i:Q(1)} for i in range(source['public']+source['owned_fields'])]
    changed=deepcopy(original);native=[]
    for i,(old,(a,b)) in enumerate(zip(source['program'],nodes)):
        op,r=old[:2];new=list(old)
        if op in ('INIT','CLEAR'):
            original[r]={};changed[r]={}
        elif op=='MOVE':
            need(changed[r]=={j:gauge[a]*v for j,v in original[r].items()},'native linear gauge invariant')
            native.append([old, str(gauge[a])])
        else:
            q=Q(old[-2]);adjusted=q*gauge[a]/gauge[b]
            new[-2]=str(adjusted)
            if op=='SCALE':
                original[r]={j:q*v for j,v in original[r].items()}
                changed[r]={j:adjusted*v for j,v in changed[r].items()}
            elif op=='COPY':
                original[r]={j:q*v for j,v in original[old[2]].items()}
                changed[r]={j:adjusted*v for j,v in changed[old[2]].items()}
            else:
                local.add(original[r],original[old[2]],q)
                local.add(changed[r],changed[old[2]],adjusted)
            need(changed[r]=={j:gauge[a]*v for j,v in original[r].items()},'complete stepwise gauge invariant')
        if op=='SCALE' and r>=source['public'] and Q(new[-2])==1:
            edits.append([i,old,None])
        else:
            word['program'].append(new)
            if new!=old:edits.append([i,old,new])
    need(changed==original,'all public and cleared private endpoints')
    return word,certificates,powers,edges,edits,native


def run(emit):
    for row in json.loads((HERE/'SOURCES.json').read_text())['vendored_inputs']:
        need(sha256((HERE/row['path']).read_bytes()).hexdigest()==row['sha256'],'frozen source '+row['path'])
    source=json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()))
    local=load(HERE/'inputs/local.py','gauge_local')
    sys.path.insert(0,str(HERE/'vendor'))
    try:cut=load(HERE/'vendor/optimize_binary_costs.py','gauge_cut')
    finally:sys.path.pop(0)
    word,certificates,powers,edges,edits,native=construct(source,local,cut)
    before,after=local.replay(source),local.replay(word)
    transpose=local.reverse_columns(word)
    for key in ('paid','helpers','owned_fields','peak_owned_fields','public_inputs','paid_rank_mass'):
        need(before[key]==after[key],'retained profile '+key)
    baseline=sum(w*abs(e) for (a,b,e),w in edges.items())
    optimum=sum(c['energy'] for c in certificates)
    sign_saving=2*sum(e[0]=='SCALE' and e[1]>=source['public'] and Q(e[-2])<0 for e in source['program'])
    need(before['real_scalar_allowance']-after['real_scalar_allowance']==2*(baseline-optimum)+sign_saving,
         'complete scalar allowance equals certified objective')
    need(after['real_scalar_allowance']<before['real_scalar_allowance'],'strict complete gain')
    controls=[]
    case=next(c for c in certificates if c['bound'])
    bad=deepcopy(case['certificate']);bad['energy']-=1
    try:cut.verify(case['problem'],bad)
    except ValueError as error:controls.append(['false optimum',str(error)])
    else:raise ValueError('false minimum accepted')
    bad=deepcopy(word)
    i=next(i for i,e in enumerate(bad['program']) if e[0]=='ADD' and e[1]<source['public'] and e[2]>=source['public'])
    bad['program'][i][-2]=str(2*Q(bad['program'][i][-2]))
    try:local.replay(bad)
    except ValueError as error:controls.append(['missing read compensation',str(error)])
    else:raise ValueError('bad gauge accepted')
    result={'schema':'p104-optimal-private-gauges/1','before':before,'after':after,'transpose':transpose,
            'gauge_nodes':len(powers)-1,'exponents':{str(k):v for k,v in powers.items()},
            'certificates':certificates,'baseline_exponent_cost':baseline,'optimal_exponent_cost':optimum,
            'sign_saving':sign_saving,'edits':edits,'instructions':len(word['program']),
            'native_gauge_sha256':sha256(canonical(native)).hexdigest(),
            'canonical_word_sha256':sha256(canonical(word)).hexdigest(),'controls':controls}
    if emit:
        (emit/'RESULT.json').write_bytes(json.dumps(result,indent=1,sort_keys=True).encode()+b'\n')
        (emit/'WORD.json.gz').write_bytes(gzip.compress(canonical(word),mtime=0))
    else:
        need(canonical(result)==canonical(json.loads((HERE/'RESULT.json').read_text())),'complete result receipt')
        need(canonical(word)==canonical(json.loads(gzip.decompress((HERE/'WORD.json.gz').read_bytes()))),'complete emitted word')
    print('PASS_P104_OPTIMAL_PRIVATE_GAUGES',before['real_scalar_allowance'],after['real_scalar_allowance'],len(edits))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--emit',type=Path)
    run(p.parse_args().emit)
