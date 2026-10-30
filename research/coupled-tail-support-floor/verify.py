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
import gzip
import zlib
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
PHYSICAL_READ_BYTES=Path.read_bytes
PHYSICAL_READ_TEXT=Path.read_text
VIRTUAL=META.get('compressed_inputs',{})
def unpack(transport,transport_sha,logical_sha,logical_bytes):
    need(hashlib.sha256(transport).hexdigest()==transport_sha,'compressed input transport hash')
    try:raw=gzip.decompress(transport)
    except(OSError,EOFError,zlib.error)as error:raise ValueError('compressed payload decoding')from error
    need(len(raw)==logical_bytes and hashlib.sha256(raw).hexdigest()==logical_sha,'compressed input logical bytes')
    return raw
def checked(relative,raw=None):
    if relative in VIRTUAL:
        need(raw is None,'logical aliases use authenticated transport bytes')
        row=VIRTUAL[relative]
        return unpack(checked(row['storage_path']),row['transport_sha256'],row['logical_sha256'],row['logical_bytes'])
    row=PINS[relative];path=ROOT/relative
    need(path.resolve()==path,'retained source must not be a symlink')
    if raw is None:raw=PHYSICAL_READ_BYTES(path)
    need(hashlib.sha256(raw).hexdigest()==row['sha256'],'retained source hash: '+relative)
    return raw
for relative in PINS:checked(relative)
for alias,row in VIRTUAL.items():
    need(alias.startswith(('source/','original/'))and alias.endswith('.json')and alias not in PINS and '..'not in Path(alias).parts,'declared read-only JSON alias')
    need(row['storage_path']in PINS and row['transport_sha256']==PINS[row['storage_path']]['sha256'],'declared transport inventory')
    checked(alias)
def logical_name(path):
    path=Path(path).resolve()
    return str(path.relative_to(ROOT))if path.is_relative_to(ROOT)else None
def alias_read_bytes(path):
    original=META.get('original_read_aliases',{}).get(str(Path(path)))
    if original is not None:return checked(original)
    relative=logical_name(path)
    need(relative is not None or not str(Path(path)).startswith('/Users/ross/git/math/'),'undeclared external workspace source read')
    return checked(relative)if relative in VIRTUAL else PHYSICAL_READ_BYTES(path)
def alias_read_text(path,encoding=None,errors=None):
    original=META.get('original_read_aliases',{}).get(str(Path(path)))
    if original is not None:return checked(original).decode(encoding or 'utf-8',errors or 'strict')
    relative=logical_name(path)
    need(relative is not None or not str(Path(path)).startswith('/Users/ross/git/math/'),'undeclared external workspace source read')
    if relative in VIRTUAL:return checked(relative).decode(encoding or 'utf-8',errors or 'strict')
    return PHYSICAL_READ_TEXT(path,encoding=encoding,errors=errors)
Path.read_bytes=alias_read_bytes
Path.read_text=alias_read_text

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
MODULES=META['executed_modules']
need(len(MODULES)==len(set(MODULES)), 'unique explicit executed module inventory')
for name,relative in MODULES.items():need(relative in PINS and relative.endswith('.py'),'declared executable source')
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
    need(not str(path).startswith('/Users/ross/git/math/'),'undeclared external dynamic source')
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
 'native_model_sha256','base_producer_sha256','reflection_source_sha256','source_path','source_sha256',
 'path','witness','witness_sha256','elapsed_seconds','executed_source_bytes','exact_source_execution','bootstrap_sha256','solver_sha256'}
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
    RESULTS.append({'entry':name+'.'+function,'status':actual.get('status','PASS_COMPLETE_RECEIPT_EQUALITY'),'mathematical_receipt':receipt})
    print('PASS_REPLAY',name,function,flush=True)
    return actual

# Immutable transport and full logical-payload authentication controls.
alias=next(iter(VIRTUAL));row=VIRTUAL[alias];transport=checked(row['storage_path'])
need(checked(alias)==unpack(transport,row['transport_sha256'],row['logical_sha256'],row['logical_bytes']),'identical lossless payload positive control')
rejection(lambda:unpack(transport+b'x',row['transport_sha256'],row['logical_sha256'],row['logical_bytes']),'compressed input transport hash')
rejection(lambda:unpack(transport,row['transport_sha256'],'0'*64,row['logical_bytes']),'compressed input logical bytes')
bad=transport[:-1]
rejection(lambda:unpack(bad,hashlib.sha256(bad).hexdigest(),row['logical_sha256'],row['logical_bytes']),'compressed payload decoding')
for alias in VIRTUAL:need(not(ROOT/alias).exists(),'logical data aliases stay in memory without writing package files')
print('PASS_LOSSLESS_READONLY_JSON_ALIAS_CONTROLS',flush=True)


import ast
for frozen in META['freezes']:
    raw=checked(frozen['manifest']);need(hashlib.sha256(raw).hexdigest()==frozen['sha256'],'frozen exact manifest')
    inv=json.loads(raw)['files']
    if frozen['complete']:need(len(inv)==len(frozen['file_map']),'complete frozen inventory')
    for name,relative in frozen['file_map'].items():
        need(hashlib.sha256(checked(relative)).hexdigest()==next(x['sha256']for x in inv if x['path']==name),'raw frozen file '+name)
for a in META['path_adaptations']:
    if 'function_source_sha256'not in a:continue
    def parts(raw):
        s=raw.decode();return {n.name:ast.get_source_segment(s,n).encode()for n in ast.parse(s).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    old,new=parts(checked(a['original'])),parts(checked(a['path']))
    need(set(new)==set(a['function_source_sha256']),'exact pure function inventory')
    for name,digest in a['function_source_sha256'].items():need(old[name]==new[name]and hashlib.sha256(new[name]).hexdigest()==digest,'unchanged recipe function '+name)
base=checked('original/coupled-tail-escape/local_block.py')
expected=base.replace(b'5782033e347c9b10ad47c01ed12a0a52ea07e901fa9e8f7aa9d3a2a928327232',PINS['source/caller-joint/joint_algebra.py']['sha256'].encode()).replace(b'7457b3672d5a73c584d2073b5d3312e6429fd3f433151f15f8f07da33aa4c59a',PINS['source/caller-joint/validate_recipe_links.py']['sha256'].encode())
need(checked('source/portable/local_block.py')==expected,'only two executed hash guard changes')
rejection(lambda:Path('/Users/ross/git/math/undeclared-tail-control.py').read_bytes(),'undeclared external workspace source read')
print('PASS_COMPLETE_FROZEN_TAIL_SOURCE_BINDINGS',flush=True)
q2=replay('local_block','produce','coupled-tail-escape/LOCAL-BLOCK.json')
q3=replay('q3_tail','produce','coupled-tail-escape/Q3-LOCAL-BLOCK.json')
need((q2['unchanged_prefix_native_mass'],q2['local_native_mass'],q2['endpoint_stock'],q2['unavoidable_entry']['native_arity_per_f'])==(66,10,72,6),'q2 whole prefix/local/stock/entry invoice')
need((q3['unchanged_prefix_native_mass'],q3['local_native_mass'],q3['stock'],q3['unavoidable_entry']['native_arity_per_f'])==(120,12,128,8),'q3 whole prefix/local/stock/entry invoice')
print('PASS_SOURCE_LOCAL_BLOCKS_AND_ALL_F_SUPPORT_WITNESSES',flush=True)

for dependency in META.get('independent_external_sources',[]):
    need(hashlib.sha256(checked(dependency['relative'])).hexdigest()==dependency['sha256'],'raw independent source input')
independent=replay('audit_tail','run','coupled-tail-independent-review/AUDIT.json')
need([(x['q'],x['prefix_native_mass'],x['local_native_mass'],x['single_entry_arity'])for x in independent['cases']]==[(2,66,10,6),(3,120,12,8)],'complete independent exact local cases')
need([x['q']for x in independent['conditional_tail_rank_grid']]==list(range(2,11)),'conditional rank grid q2throughq10')
ce=module('native_model').ce
try:ce.diag(2,(2,0),(0,0))
except AssertionError:pass
else:raise ValueError('historical source assertions disabled under optimized parent')
rejection(lambda:bound_spec('unbound_tail_control','/Users/ross/git/math/undeclared-tail-control.py'),'undeclared external dynamic source')
print('PASS_COMPLETE_INDEPENDENT_LOCAL_TAIL_SUPPORT_NO_NEW_KAPPA',flush=True)

admitted=data('two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json')
for f in admitted['fixtures']:
    q=f['q'];cut={2:69,3:119}[q]
    prefix=Counter(e['rank_per_f']for e in f['events'][:cut]if e['kind']=='NATIVE')
    need(prefix=={2:{2:33},3:{2:60}}[q],'actual fixed prefix histogram for conditional moment')
print('PASS_CONDITIONAL_FULLSCAN_MOMENT_PREFIX_BINDING',flush=True)

# Exact next-interface appendix, strictly planning-only and rank-neutral.
for x in META['cut58_raw_sources']:
    need(hashlib.sha256(checked(x['relative'])).hexdigest()==x['sha256'],'raw cut58 planning source pin')
planning=replay('cut58','produce','early-cut58-planning/CUT58.json')
review=replay('audit_cut58','run','early-cut58-independent-review/AUDIT.json')
need(planning['target_is_not_achieved']is True and planning['hypothetical_target_suffix_mass']==16,'open hypothetical target never claimed achieved')
need((planning['prefix_native_mass'],planning['suffix_native_mass'],planning['complete_mass'],planning['stock'])==(54,22,76,72),'unchanged planning native bill')
need(review['all_current_input_columns']==6 and review['literal_inverse_orders']==2 and review['neutral_factorization_mass']==22,'complete independent planning-only scope')
print('PASS_CUT58_NEXT_INTERFACE_NEUTRAL_ONLY_TARGET16_OPEN',flush=True)
