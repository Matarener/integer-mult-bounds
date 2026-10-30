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
# Complete retained freezes and every original-source pin are authenticated.
for frozen in META['freezes']:
    raw=checked(frozen['manifest'])
    need(hashlib.sha256(raw).hexdigest()==frozen['sha256'],'frozen manifest pin')
    inventory=json.loads(raw)['files']
    if frozen['complete']:need(len(inventory)==len(frozen['file_map']),'complete frozen file inventory')
    for name,relative in frozen['file_map'].items():
        row=next(x for x in inventory if x['path']==name)
        need(hashlib.sha256(checked(relative)).hexdigest()==row['sha256'],'original frozen bytes '+name)
for original,relative in META['original_read_aliases'].items():
    need(Path(original).read_bytes()==checked(relative),'exact original raw source alias')
for adaptation in META['path_adaptations']:
    if 'function_source_sha256'not in adaptation:continue
    def parts(raw):
        source=raw.decode();tree=ast.parse(source)
        return {x.name:ast.get_source_segment(source,x).encode()for x in tree.body if isinstance(x,ast.FunctionDef)}
    old=parts(checked(adaptation['original']));new=parts(checked(adaptation['path']))
    need(set(new)==set(adaptation['function_source_sha256']),'exact consumed pure function inventory')
    for name,digest in adaptation['function_source_sha256'].items():
        need(old[name]==new[name]and hashlib.sha256(new[name]).hexdigest()==digest,'verbatim mathematical checker function '+name)
rejection(lambda:Path('/Users/ross/git/math/undeclared-publication-control.py').read_bytes(),'undeclared external workspace source read')
rejection(lambda:bound_spec('unbound_control','/Users/ross/git/math/undeclared-publication-control.py'),'undeclared external dynamic source')
print('PASS_FROZEN_ORIGINAL_BYTES_AND_EXACT_COMPILED_FUNCTION_MAP',flush=True)
# The raw two-plane proof has one explicitly corrected even-index ellipsis.
original=checked('source/general-clifford-retiming/kernel-search/PROOF.md').decode()
need((ROOT/'TWO-PLANE-SPECIAL-CASE.md').read_text()==original.replace('B_(2q)...B_4','B_(2q) B_(2q-2) ... B_4 (even indices only)'),'only readable even-index clarification')

# The root producer writes a receipt in main and is intentionally not run.
# This independently implemented complete audit reconstructs all36 fixed
# responses from the raw receipt, checks every original column and both
# literal inverse orders, all chronological ranks, isolation/current defect,
# Gaussian phase, complete invoice and every saved mathematical claim field.
rankaudit=replay('audit_arbitrary_skew','run','arbitrary-skew-rank-review/AUDIT.json')
need(len(rankaudit['finite_bindings'])==36 and len(rankaudit['rank_extremes'])==14,'complete finite bindings and extremes')
need(all(x['actual_binding']for x in rankaudit['finite_bindings']),'every retained fixture physically bound')
need(all(x['complete_mass']>=x['stock']for x in rankaudit['finite_bindings']),'no positive fixed-interface rank deficit')

# The explicit all-q column/dual-row induction is written in PROOF; these
# exact14 generated fixtures and56cuts additionally bind the source suffix.
transport=replay('review_transport','produce','trajectory-pairing-search/arbitrary-skew-review/TRANSPORT-REVIEW.json')
need(len(transport['fixtures'])==14 and sum(len(x['all_even_cut_transport_checks'])for x in transport['fixtures'])==56,'complete finite suffix/cut domain')
need({x['q']for x in transport['fixtures']}==set(range(2,9)),'q2 throughq8 finite corroboration')

# The older two-plane theorem is a special case with useful equality examples.
# Execute the complete independent algebra/actual-source cases and the full
# retained literal-circuit checker rather than regenerating any proposer.
gates=module('audit_gates');special=json.loads(json.dumps(gates.kernel_checks()))
saved=data('completed-gates-review/AUDIT.json')['kernel']
need(special==saved,'complete two-plane grid and actual-source independent payload')
need(len(special['finite_rank_identity_grid'])==28 and len(special['actual_q2_q3_transport_bindings'])==8,'complete special-case domain')
literal=replay('validate_kernels','run','general-clifford-retiming/kernel-search/VALIDATION.json')
need(literal['distinct_literal_circuit_inverse_pairs']==140,'all140 exact circuit/inverse pairs')
neutral={(x['kernel'],x['q']):(x['mass'],x['stock'])for x in special['actual_q2_q3_transport_bindings']}
need({key:neutral[key]for key in [('rankzero_Pauli',2),('rankzero_Pauli',3),('odd_rankone_involution',2),('odd_rankone_involution',3)]}=={('rankzero_Pauli',2):(60,60),('rankzero_Pauli',3):(112,112),('odd_rankone_involution',2):(66,66),('odd_rankone_involution',3):(120,120)},'exact named Pauli and odd-rank neutral examples')
print('PASS_ALL_TWO_PLANE_SPECIAL_CASES_AND_LITERAL_RECIPES',flush=True)

# All cubic producer functions are called through run(), which does not
# write. Its normal/-O main-only writes are outside this registered path.
cubic=replay('cubic_gate','run','general-clifford-retiming/order-three-response/CUBIC.json')
independent_cubic=json.loads(json.dumps(gates.cubic_checks()))
need(independent_cubic==data('completed-gates-review/AUDIT.json')['cubic'],'complete independent cubic full-entry/power/trace payload')
need([x['native_B_rank']for x in cubic['fixtures']]==[1,2,3,4]and [x['span_rank_I_J_J2']for x in cubic['fixtures']]==[2,3,3,3],'actual tensor scaling and quadratic failure')
replay('lambda_controls','run','arbitrary-skew-rank-review/LAMBDA-CONTROLS.json')

# Defect-sensitive controls supplement the independent controls inside each
# audit. They do not silently modify authenticated evidence.
row=data('root-joint/ARBITRARY-SKEW-GATE.json')['fixtures'][0]
bad=copy.deepcopy(row);bad['Q_rank']+=1
try:module('audit_arbitrary_skew').inspect(bad['J'],bad['q'],claimed=bad,name='damaged-invoice-control')
except ValueError as error:need('saved finite fixture field Q_rank'in str(error),'specific changed-Q rejection')
else:raise ValueError('damaged Q tariff accepted')
ce=module('native_model').ce
try:ce.diag(2,(2,0),(0,0))
except AssertionError:pass
else:raise ValueError('legacy assertions disabled under optimized parent')
need(cubic['fixtures'][1]['quadratic_relation']is False and cubic['fixtures'][1]['span_rank_I_J_J2']==3,'f2 missing-reader control')
print('PASS_EXACT_RESPONSE_GATES_NO_NEW_KAPPA',json.dumps(dict(wider_bindings=36,extremes=14,suffix_fixtures=14,suffix_cuts=56,two_plane_actual=8,literal_inverse_pairs=140,cubic_f=[1,2,3,4],formal_kernel=False,no_new_kappa=True)),flush=True)

# Bounded successful-contribution continuation: two new fixed-word certificates
# for the already retained actual odd-rank neutral fixtures. No discovery runs.
for x in META['odd_raw_sources']:
    need(hashlib.sha256(checked(x['relative'])).hexdigest()==x['sha256'],'raw odd-certificate source pin')
odd=replay('audit_odd','run','odd-kernel-independent-review/AUDIT.json')
need([(x['q'],x['ambient'],x['parent'],x['floor'],x['source_mass'],x['stock'])for x in odd['fixtures']]==[(2,12,11,66,66,66),(3,16,15,120,120,120)],'actual odd native parent versus ambient and sharp fixed-word stock floors')
need(odd['fixtures'][0]['path_ranks']==[12,11,10,11,11,11]and odd['fixtures'][1]['path_ranks']==[15]*8,'complete exact odd holonomy ranks')
print('PASS_ODD_FIXED_WORD_FRAME_COROLLARY_NO_NEW_KAPPA',flush=True)
