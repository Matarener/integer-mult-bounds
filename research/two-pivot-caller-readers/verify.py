#!/usr/bin/env python3
"""Exact caller replay. Ross Richardson; substantial OpenAI Codex assistance.

Apache-2.0. Immutable predecessor implementations are compiled from the same
bytes authenticated below, with optimize=0 to preserve historical assertions.
This direct verifier needs Python's standard library, no Git and no network.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import copy
import hashlib
import importlib
import importlib.abc
import importlib.util
import json
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
META=json.loads((ROOT/'BINDINGS.json').read_bytes())
PINS={row['path']:row for row in META['files']}
def need(condition,message):
    if not condition:raise ValueError(message)
need(len(PINS)==len(META['files']),'duplicate retained-source path')
def checked(relative,raw=None):
    row=PINS[relative];path=ROOT/relative
    need(path.resolve()==path,'retained source must not be a symlink')
    if raw is None:raw=path.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==row['sha256'],'retained source hash: '+relative)
    return raw
for relative in PINS:checked(relative)

def rejection(action,needle):
    try:action()
    except ValueError as error:
        need(needle in str(error),'wrong rejecting predicate: '+str(error))
    else:raise ValueError('negative control unexpectedly accepted: '+needle)

# Positive and negative source-binding controls use real source bytes. The
# loader below has no bytecode-cache path, including for dynamic source loads.
first=next(p for p in PINS if p.endswith('.py'))
need(checked(first,checked(first))==checked(first),'identical source positive control')
rejection(lambda:checked(first,checked(first)+b'\n# altered source\n'),'retained source hash')
MODULES={}
for relative in PINS:
    if relative.startswith('source/') and relative.endswith('.py'):
        stem=Path(relative).stem
        need(stem not in MODULES,'ambiguous retained module '+stem)
        MODULES[stem]=relative
class ByteLoader(importlib.abc.Loader):
    def __init__(self,relative):self.relative=relative
    def create_module(self,spec):return None
    def exec_module(self,module):
        raw=checked(self.relative)
        exec(compile(raw,str(ROOT/self.relative),'exec',dont_inherit=True,optimize=0),module.__dict__)
class ByteFinder(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname in MODULES:
            relative=MODULES[fullname]
            return ORIGINAL_SPEC(fullname,str(ROOT/relative),loader=ByteLoader(relative))
ORIGINAL_SPEC=importlib.util.spec_from_file_location
def bound_spec(name,location,*args,**kwargs):
    path=Path(location).resolve()
    if path.is_relative_to(ROOT):
        relative=str(path.relative_to(ROOT))
        need(relative in PINS,'undeclared dynamic source '+relative)
        return ORIGINAL_SPEC(name,str(path),loader=ByteLoader(relative))
    return ORIGINAL_SPEC(name,location,*args,**kwargs)
importlib.util.spec_from_file_location=bound_spec
sys.meta_path.insert(0,ByteFinder())
def module(name):return importlib.import_module(name)
def data(relative):return json.loads(checked('source/'+relative))
def source_path(original):
    candidates=[p for p,row in PINS.items() if p.startswith('source/') and (row['origin']==original or row['origin'].endswith('/'+original))]
    need(len(candidates)==1,'one retained original source for '+original)
    return ROOT/candidates[0]

# Receipts contain original absolute provenance paths. All retained bytes are
# separately checked above. These explicitly enumerated metadata fields are
# omitted ONLY when comparing replay's mathematical body to its frozen receipt.
PROVENANCE={'sources','source_pins','producer_sha256','helper_sha256',
 'native_model_sha256','reflection_source_sha256','source_path','source_sha256',
 'path','witness','witness_sha256'}
def body(value):
    if isinstance(value,dict):return {str(k):body(v) for k,v in value.items() if k not in PROVENANCE}
    if isinstance(value,(list,tuple)):return [body(v) for v in value]
    return value
def difference(a,b,path='root'):
    if type(a)!=type(b):return path+': type mismatch'
    if isinstance(a,dict):
        if a.keys()!=b.keys():return path+': keys '+str(set(a)^set(b))
        for k in a:
            if a[k]!=b[k]:return difference(a[k],b[k],path+'.'+k)
    elif isinstance(a,list):
        if len(a)!=len(b):return path+': lengths '+str((len(a),len(b)))
        for i,(x,y) in enumerate(zip(a,b)):
            if x!=y:return difference(x,y,path+'['+str(i)+']')
    elif a!=b:return path+': '+repr(a)[:150]+' != '+repr(b)[:150]
    return path
RESULTS=[]
def replay(name,function,receipt):
    actual=json.loads(json.dumps(getattr(module(name),function)()))
    expected=data(receipt)
    aa,bb=body(actual),body(expected)
    need(aa==bb,'mathematical receipt mismatch '+receipt+' '+difference(aa,bb))
    RESULTS.append({'entry':name+'.'+function,'status':actual['status'],'mathematical_receipt':receipt})
    print('PASS_REPLAY',name,function,flush=True)
    return actual

def charts():
    c=module('chronology');b=module('batch_paid_progress');nc=module('native_chart_search');sg=module('signed_chart_optimization')
    cases=[]
    for name in ['SIGNED-CHART-HANDOFF-SIX.json','SIGNED-CHART-HANDOFF-Q3.json']:
        d=data('root-chronology/'+name);sp=source_path(d['source_path']);raw=sp.read_bytes();original=json.loads(raw)
        need(hashlib.sha256(raw).hexdigest()==d['source_sha256'],'fixed-chart original bytes')
        n,m=d['width'],d['ambient_arity'];events=nc.compile_word(original['events'],n,m//2,m,d['choices'])
        need(events==d['events'],'fixed-chart serialized choices')
        need(b.replay(events,n,m//2)==b.replay(original['events'],n,m//2),'fixed-chart every original column and both inverse orders')
        h=Counter(e['operator']['native_arity'] for e in events if e['kind']=='NATIVE')
        need(sum(r*v for r,v in h.items())==d['native_mass']==n*m,'fixed-chart break-even bill')
        need(all(2*r*r<m*m for r in h),'fixed-chart child contraction')
        cases.append(dict(banks=n,ambient_arity=m,histogram=dict(sorted(h.items())),mass=n*m))
    certificate=data('root-chronology/CHART-CYCLE-PACK-HANDOFF-SIX.json')
    raw=source_path(certificate['source_path']).read_bytes();need(hashlib.sha256(raw).hexdigest()==certificate['source_sha256'],'cycle graph source bytes')
    _,edges,_=sg.graph(json.loads(raw)['events'],6,6)
    def verify_cycles(cycles):
        used=set()
        for cycle in cycles:
            need(len(set(cycle))==len(cycle) and not used.intersection(cycle),'cycle edge disjointness')
            used.update(cycle);parity=0;degree={}
            for index in cycle:
                need(type(index)is int and 0<=index<len(edges),'cycle edge range')
                u,v,sign=edges[index];parity^=sign;degree[u]=degree.get(u,0)+1;degree[v]=degree.get(v,0)+1
            need(parity==1 and all(x%2==0 for x in degree.values()),'odd Eulerian cycle witness')
        need(len(cycles)==36,'36 cycle certificate')
    verify_cycles(certificate['cycles'])
    mutant=copy.deepcopy(certificate['cycles']);mutant.append(mutant[0]);rejection(lambda:verify_cycles(mutant),'cycle edge disjointness')
    RESULTS.append(dict(entry='fixed_chart_exact_certificate',cases=cases,edge_disjoint_odd_subgraphs=36,n6_mass_lower_bound=72,duplicate_cycle_rejected=True))
    print('PASS_FIXED_CHART',cases,'n6 lower bound72',flush=True)

def saved_quadratic():
    q=module('quadratic_charts');audit=module('audit_encoded_complete')
    cases=[]
    for name in ['INDEPENDENT-ENCODED-COMPLETE','BALANCED-PHYSICAL-REPLAY-Q3']:
        saved=data('root-chronology/CLUSTER-'+name+'-ALLPAIRS.json')
        original=json.loads(source_path(saved['source_path']).read_bytes());n,banks=saved['ambient_arity'],saved['width']
        events=q.compile_word(original['events'],banks,n,[tuple(a) for a in saved['choices']])
        need(json.loads(json.dumps(events))==saved['events'],'saved quadratic complete word')
        hist=Counter(e.get('rank_per_f',0) for e in events);hist.pop(0,None)
        mass=sum(r*v for r,v in hist.items());need(mass==saved['native_rank_mass']==130,'saved quadratic rank invoice')
        I=q.identity(n);E=q.Mono(I.rows,(1<<n)-1,(3,1)*(n//2),(0,)*n,0,(n//2)%4)
        target=q.replay([dict(kind='NATIVE',bank=i,x_monomial=E.data())for i in range(banks)],banks,n)
        need(q.replay(original['events'],banks,n)==target==q.replay(events,banks,n),'saved quadratic all original columns')
        inv=audit.inverse_events(events,n);ident=q.replay([],banks,n)
        need(q.replay(events+inv,banks,n)==ident==q.replay(inv+events,banks,n),'saved quadratic both inverse orders')
        at=next(i for i,e in enumerate(events)if e.get('rank_per_f',0))
        need(q.replay(events[:at]+events[at+1:],banks,n)!=target,'saved quadratic omitted query defect')
        cases.append(dict(name=name,mass=mass,stock=n*banks,histogram=dict(sorted(hist.items())),omitted_query_rejected=True))
    RESULTS.append(dict(entry='saved_quadratic_choices',cases=cases))
    print('PASS_SAVED_QUADRATIC',cases,flush=True)

replay('handoff_family','prove','caller/HANDOFF-FAMILY.json')
replay('review_handoff_family','run','root-chronology/INDEPENDENT-HANDOFF-FAMILY.json')
charts()
replay('audit_encoded_complete','run','root-chronology/INDEPENDENT-ENCODED-COMPLETE.json')
replay('balanced_physical_replay','produce','caller/BALANCED-PHYSICAL-REPLAY-Q3.json')
saved_quadratic()

report=dict(status='PASS_PORTABLE_CALLER_PACKAGE',claims=META['claims'],no_new_kappa=True,
 retained_files=len(PINS),mathematical_checks=RESULTS,source_bytes_compiled=True,
 historical_assertions_enabled=True,source_mutation_rejected=True,
 limits=['Written all-parameter proofs, finite exact replays and source integrity are distinct.',
 'No formal-kernel multiplication proof, physical supplier admission or selected frontier change.'])
if len(sys.argv)>1:
    need(len(sys.argv)==2 and sys.argv[1]=='--json','only --json is supported')
    print(json.dumps(report,indent=2,sort_keys=True))
else:print(report['status'],','.join(report['claims']),'no_new_kappa=true',flush=True)
