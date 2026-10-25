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

def query_count_scope():
    """Replay arbitrary-support queries on every independent marked column."""
    gate=module('marked_residual_gate')
    cases=[]
    for L,masks,words in [
        (2,(3,3),[[(0,3),(1,3)],[(0,1),(0,2),(1,3)],
                  [(0,1),(0,2),(1,1),(1,2)]]),
        (3,(1,6),[[(0,1),(1,6)]])]:
        target=[(bank,x^mask,owner,mask.bit_count()%4)
                for bank,mask in enumerate(masks)
                for x in range(1<<L) for owner in range(L)]
        for word in words:
            actual=[]
            for bank in range(2):
                for x in range(1<<L):
                    for owner in range(L):
                        y,phase=x,0
                        for operand,support in word:
                            if operand==bank:
                                y^=support;phase=(phase+support.bit_count())%4
                        actual.append((bank,y,owner,phase))
            need(actual==target,'multi-plane query word: every column and Gaussian phase')
            ranks=[len(gate.commutator_entries(L,support)) for _,support in word]
            target_rank=sum(len(gate.commutator_entries(L,mask)) for mask in masks)
            planes=sum(support.bit_count() for _,support in word)
            need(sum(ranks)==target_rank==planes*(1<<L),'query words pay the complete plane debt')
            cases.append(dict(planes=L,bank_masks=list(masks),queries=len(word),
                              native_plane_count=planes,query_commutator_ranks=ranks))
    need(cases[0]['query_commutator_ranks']==[8,8] and
         cases[2]['query_commutator_ranks']==[4,4,4,4],
         'two multi-plane calls and four single-plane calls have the same rank bill')
    rejection(lambda:need(all(rank<=4 for rank in cases[0]['query_commutator_ranks']),
                          'single-plane commutator cap'), 'single-plane commutator cap')
    RESULTS.append(dict(entry='query_count_scope',cases=cases,
                        arbitrary_support_single_plane_cap_rejected=True))
    print('PASS_QUERY_COUNT_SCOPE two/three/four calls, same full-pair plane bill',flush=True)

replay('marked_residual_gate','prove','q4-pauli-fusion/MARKED-RESIDUAL-GLOBAL-FLOOR.json')
query_count_scope()
replay('audit_marked_plane_bound','run','root-chronology/INDEPENDENT-MARKED-PLANE-BOUND.json')
replay('audit_partial_reflection','run','root-chronology/INDEPENDENT-PARTIAL-REFLECTION.json')
replay('conjugated_reflection','run','native-frames/CONJUGATED-REFLECTION.json')
replay('source_progress_tradeoff','run','native-frames/SOURCE-PROGRESS-TRADEOFF.json')
replay('one_chunk_phase','run','native-frames/ONE-CHUNK-PHASE.json')

report=dict(status='PASS_PORTABLE_CALLER_PACKAGE',claims=META['claims'],no_new_kappa=True,
 retained_files=len(PINS),mathematical_checks=RESULTS,source_bytes_compiled=True,
 historical_assertions_enabled=True,source_mutation_rejected=True,
 limits=['Written all-parameter proofs, finite exact replays and source integrity are distinct.',
 'No formal-kernel multiplication proof, physical supplier admission or selected frontier change.'])
if len(sys.argv)>1:
    need(len(sys.argv)==2 and sys.argv[1]=='--json','only --json is supported')
    print(json.dumps(report,indent=2,sort_keys=True))
else:print(report['status'],','.join(report['claims']),'no_new_kappa=true',flush=True)
