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
    need(alias.startswith('source/')and alias.endswith('.json')and alias not in PINS and '..'not in Path(alias).parts,'declared read-only JSON alias')
    need(row['storage_path']in PINS and row['transport_sha256']==PINS[row['storage_path']]['sha256'],'declared transport inventory')
    checked(alias)
def logical_name(path):
    path=Path(path).resolve()
    return str(path.relative_to(ROOT))if path.is_relative_to(ROOT)else None
def alias_read_bytes(path):
    original=META.get('original_read_aliases',{}).get(str(Path(path)))
    if original is not None:return checked(original)
    relative=logical_name(path)
    return checked(relative)if relative in VIRTUAL else PHYSICAL_READ_BYTES(path)
def alias_read_text(path,encoding=None,errors=None):
    original=META.get('original_read_aliases',{}).get(str(Path(path)))
    if original is not None:return checked(original).decode(encoding or 'utf-8',errors or 'strict')
    relative=logical_name(path)
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
MODULES={}
for relative in PINS:
    if relative.startswith('source/') and relative.endswith('.py') and '/frozen-two-site-v1/' not in relative:
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
    RESULTS.append({'entry':name+'.'+function,'status':actual['status'],'mathematical_receipt':receipt})
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
author=data('two-site-continuation/MANIFEST.json')
need(hashlib.sha256(checked('source/two-site-continuation/MANIFEST.json')).hexdigest()==META['author_freeze']['manifest_sha256']=='44f1e264b3087ab8fdb08b4cd6e27befefbba380852b0119321724b7bc41b5da','frozen author manifest')
need(len(author['files'])==len(META['author_freeze']['original_file_map'])==24,'complete original author freeze')
for row in author['files']:
    need(hashlib.sha256(checked(META['author_freeze']['original_file_map'][row['path']])).hexdigest()==row['sha256'],'original author input '+row['path'])
audit_manifest=data('two-site-independent-audit/MANIFEST.json')
need(hashlib.sha256(checked('source/two-site-independent-audit/MANIFEST.json')).hexdigest()==META['independent_freeze']['manifest_sha256']=='4e52d2469b648d73c2af67615116c994b434fdcca2cd0aa573debe98db87324e','frozen independent manifest')
for row in audit_manifest['files']:
    need(hashlib.sha256(checked(META['independent_freeze']['original_file_map'][row['path']])).hexdigest()==row['sha256'],'independent original input '+row['path'])
for row in audit_manifest['external_dependencies']:
    relative=META['independent_freeze']['external_input_map'][row['path']]
    need(hashlib.sha256(checked(relative)).hexdigest()==row['sha256'],'independent original source pin '+relative)

# The only new engine guard is pinned to the actual executed adapter bytes.
engine=hashlib.sha256(checked('source/caller-joint/joint_algebra.py')).hexdigest()
old=checked('original/two-site-continuation/two_site.py')
need(checked('source/two-site-continuation/two_site.py')==old.replace(b'5782033e347c9b10ad47c01ed12a0a52ea07e901fa9e8f7aa9d3a2a928327232',engine.encode()),'only executed engine guard adaptation')
utility=next(x for x in META['path_adaptations']if x['path']=='source/caller-joint/validate_recipe_links.py')
def functions(raw):
    source=raw.decode();tree=ast.parse(source)
    return {node.name:ast.get_source_segment(source,node).encode()for node in tree.body if isinstance(node,ast.FunctionDef)}
original=functions(checked(utility['original']));compiled=functions(checked(utility['path']))
need(set(compiled)==set(utility['function_source_sha256']),'exact consumed recipe utility function inventory')
for name,digest in utility['function_source_sha256'].items():
    need(original[name]==compiled[name]and hashlib.sha256(compiled[name]).hexdigest()==digest,'verbatim compiled source function '+name)
print('PASS_COMPLETE_AUTHOR_INDEPENDENT_PINS_AND_SOURCE_FUNCTION_BINDING',flush=True)

# Rebuild the current used-only physical words from their scientific fixed
# witnesses, then compare every mathematical field to the admitted artifact.
admitted=replay('admit_fusions','produce','two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json')
replay('controls','produce','two-site-continuation/CONTROLS.json')
independent=module('audit_two_sites');frozen_independent=data('two-site-independent-audit/AUDIT.json')
sources=data('two-site-continuation/inputs/REPAIRED-SIMPLIFIED-FUSIONS.json')
cases=[]
for fixture in admitted['fixtures']:
    q=fixture['q'];source=next(x for x in sources['fixtures']if x['q']==q)
    science=data('two-site-continuation/ISOLATED-FUSION-Q'+str(q)+'.json')
    cases.append(independent.check(q,fixture,source,science))
need(json.loads(json.dumps(cases))==frozen_independent['cases'],'every independent physical transport/native/phase proof field')
RESULTS.append(dict(entry='audit_two_sites.check',cases=cases,not_called='Original run/load-control wrapper writes scratch; registered replay calls all complete mathematical check cases and independently authenticates the full source inventory.'))
print('PASS_INDEPENDENT_ALL_COLUMNS_TRANSPORT_PHASE_NATIVE_AND_LITERAL_INVERSES',flush=True)

# The complete seven-mask census is the same authenticated general-Clifford
# engine, with independent row-only/column-only scope controls. It is not
# advertised as a second independent general-Clifford census implementation.
continuation=json.loads(json.dumps(module('continue_isolated').run(180)))
saved_continuation=data('two-site-continuation/CONTINUED-ISOLATION-Q2.json')
need(body(continuation)==body(saved_continuation),'complete bounded census mathematical payload '+difference(body(continuation),body(saved_continuation)))
need(continuation['completed_masks']==list(range(1,8))and not continuation['timed_out']and not continuation['cases'],'all seven masks completed, no eligible isolated pair')
need(continuation['counts']=={'correction-not-one-bank':4887,'not-isolated-both-sides':34},'all4921 existing cut pairs accounted')
algorithm_controls=module('replay_continuation').controls()
saved_census_audit=data('two-site-independent-audit/CONTINUATION-REPLAY.json')
need(continuation['counts']==saved_census_audit['counts']and algorithm_controls==saved_census_audit['algorithm_controls'],'independent reviewed two-sided scope controls and complete census counts')
need(saved_census_audit['nonempty_tail_subsets']==7 and saved_census_audit['pairs_per_subset']==703,'independent frozen census domain')
RESULTS.append(dict(entry='continue_isolated.run + replay_continuation.controls',counts=continuation['counts'],completed_masks=continuation['completed_masks'],algorithm_controls=algorithm_controls,scope='Complete unchanged general-Clifford census; source path relocation excluded only after separate original-byte authentication. The original writing/run wrapper is not called.'))
print('PASS_COMPLETE_ISOLATED_CENSUS_AND_INDEPENDENT_TWO_SIDED_CONTROLS',flush=True)
ce=module('native_model').ce
try:ce.diag(2,(2,0),(0,0))
except AssertionError:pass
else:raise ValueError('retained source assertions disabled under optimized parent')
for fixture in admitted['fixtures']:
    n=2*fixture['q']+2
    need(fixture['histogram']=={'2':n*n,'4':1},'complete actual stock-plus-four profile')
    need(fixture['native_mass']==fixture['stock']+4 and fixture['D']==-4,'no favorable native deficit')
    need(fixture['all_original_columns']==n and fixture['used_only_native_definitions']==14,'complete original-input and used-only native domain')
RESULTS.append(dict(entry='assertion_and_scope_controls',legacy_assertions_active=True,complete_mass_still_stock_plus4=True))

# Four exact fixed-word certificates; no bounded proposer search is run.
pair_manifest=data('trajectory-pairing-search/MANIFEST.json')
need(hashlib.sha256(checked('source/trajectory-pairing-search/MANIFEST.json')).hexdigest()==META['pairing_freeze']['manifest_sha256']=='623ac76418785a29d3a45868f07cbcae0df6e3176585a701fd6776c98c97d3c8','frozen four-word pairing manifest')
for row in pair_manifest['files']:
    need(hashlib.sha256(checked(META['pairing_freeze']['file_map'][row['path']])).hexdigest()==row['sha256'],'exact original pairing input '+row['path'])
review_manifest=data('completed-gates-review/MANIFEST.json')
need(hashlib.sha256(checked('source/completed-gates-review/MANIFEST.json')).hexdigest()==META['pairing_freeze']['review_manifest_sha256']=='ef3697eece91ee6d52ae3f5e88b95028091829d6961118052dff1e25df212ba3','frozen completed review manifest')
for name,relative in META['pairing_freeze']['review_file_map'].items():
    row=next(x for x in review_manifest['files']if x['path']==name)
    need(hashlib.sha256(checked(relative)).hexdigest()==row['sha256'],'retained independent pairing input '+name)
need(len(META['original_read_aliases'])==3,'three exact original proposal read aliases')
for original,relative in META['original_read_aliases'].items():
    need(Path(original).read_bytes()==checked(relative),'original-path alias returns exact retained bytes')
certificate=data('trajectory-pairing-search/FULL-STOCK-CERTIFICATES.json')
admission=module('admit_pairings');pairing_independent=module('pairing_audit')
independent_certificate=data('completed-gates-review/PAIRING-AUDIT.json')
fresh=[];fresh_independent=[]
for name in('REPAIRED','TWO-SITE'):
    for q in(2,3):
        current=json.loads(json.dumps(admission.fixture(name,q)))
        saved=next(x for x in certificate['fixtures']if x['family']==name and x['q']==q)
        need(body(current)==body(saved),'complete fixed-word pairing witness '+name+' q'+str(q)+' '+difference(body(current),body(saved)))
        independent_case=json.loads(json.dumps(pairing_independent.check(name,q)))
        saved_independent=next(x for x in independent_certificate['fixtures']if x['family']==name and x['q']==q)
        need(independent_case==saved_independent,'every independent fixed-word certificate field '+name+' q'+str(q))
        need(current['admitted_floor_per_f']==current['stock']==(72 if q==2 else 128),'four exact stock floors')
        fresh.append(dict(family=name,q=q,floor=current['admitted_floor_per_f'],source_mass=current['original_native_mass'],paths=current['trajectory_ranks_per_f']))
        fresh_independent.append(dict(family=name,q=q,every_edge_once=independent_case['every_edge_once'],wrong_routing_control=independent_case['wrong_routing_control']))
RESULTS.append(dict(entry='admit_pairings.fixture + pairing_audit.check',fixed_word_certificates=fresh,independent_literal_admission=fresh_independent,scope='Common-frame ADD graph and fixed literal physical boundaries of the four named words only. Arbitrary Clifford gauges may mix tensor coordinates. No all-q caller or source-invoice optimality.'))
print('PASS_FOUR_COMPLETE_FIXED_WORD_STOCK_FLOORS_AND_INDEPENDENT_PAIRING_ADMISSION',flush=True)

report=dict(status='PASS_PORTABLE_TWO_SITE_CALLER_FUSIONS',claims=META['claims'],no_new_kappa=True,
 mathematical_checks=RESULTS,retained_physical_files=len(PINS),lossless_logical_aliases=len(VIRTUAL),
 compressed_transport_bytes=sum(row['transport_bytes']for row in VIRTUAL.values()),
 complete_logical_alias_bytes=sum(row['logical_bytes']for row in VIRTUAL.values()),
 source_bytes_compiled=True,historical_assertions_enabled=True,
 limits=['Finite q2/q3 complete caller families, for every positive f. No all-q caller induction.',
 'General isolated rank-distance lemma and finite isolated continuation census have separate premises.',
 'No favorable supplier, global optimum, physical owner/controller/precision/tape admission, compatible BIT or new kappa.'])
if len(sys.argv)>1:
    need(len(sys.argv)==2 and sys.argv[1]=='--json','only --json is supported')
    print(json.dumps(report,indent=2,sort_keys=True))
else:print(report['status'],'no_new_kappa=true',flush=True)
