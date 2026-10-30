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

replay('even_parity_source','run','native-frames/EVEN-PARITY-SOURCE.json')
replay('even_parity_source_independent','run','q4-pauli-fusion/INDEPENDENT-EVEN-PARITY-SOURCE.json')
replay('even_parity_handoff_gate','run','native-frames/EVEN-PARITY-HANDOFF-GATE.json')
replay('even_parity_caller','run','caller/EVEN-PARITY-CALLER.json')
replay('diagonal_j_factory_gate','run','native-frames/DIAGONAL-J-FACTORY-GATE.json')
replay('star_factory_audit','run','q4-pauli-fusion/STAR-FACTORY-AUDIT.json')

replay('joint_prefix','produce','caller-joint/JOINT-PREFIX.json')
# Consume the published selected-native witnesses. Do not repeat their
# expensive synthesis. The source producer still reconstructs the complete
# physical word, all-f phases, H/L map, inverses and reader defect controls.
def without_recipes(value):
    if isinstance(value,dict):return {k:without_recipes(v)for k,v in value.items()if k not in('selected_native_recipe','selected_native_lowering_included')}
    if isinstance(value,list):return [without_recipes(v)for v in value]
    return value
actual_joint=json.loads(json.dumps(module('joint_tail').produce(lower=False)))
fixed_joint=data('caller-joint/JOINT-COMPLETE.json')
aa,bb=without_recipes(body(actual_joint)),without_recipes(body(fixed_joint))
need(aa==bb,'complete joint source/word mismatch '+difference(aa,bb))
auditor=module('fixed_native_recipes');native_ce=module('native_model').ce
fixed_checks=[auditor.audit_fixture(native_ce,x)for x in fixed_joint['fixtures']]
# Reconstruct the entire rejected original receipt from the corrected
# fixed evidence plus compact metadata-only byte splices. Exact SHA pins
# authenticate both complete byte strings before the same pointer control.
old_patch=data('caller-joint/BEFORE-ID-FIX-PATCH.json')
old_raw=checked('source/caller-joint/JOINT-COMPLETE.json')
need(hashlib.sha256(old_raw).hexdigest()==old_patch['corrected_sha256'],'corrected full receipt reconstruction pin')
previous=len(old_raw)
for splice in old_patch['replacements']:
    start,end=splice['start'],splice['end']
    need(type(start)is int and type(end)is int and 0<=start<=end<=previous,'descending disjoint original receipt splice')
    need(old_raw[start:end]==splice['corrected'].encode(),'exact corrected receipt splice context')
    old_raw=old_raw[:start]+splice['original'].encode()+old_raw[end:]
    previous=start
need(hashlib.sha256(old_raw).hexdigest()==old_patch['original_sha256']=='a12efdd2cd056e63d57e1da9de346ebafc6cd88cbebc0af2f7993cd31a628a96','complete original receipt exact reconstruction pin')
old_joint=json.loads(old_raw)
rejection(lambda:auditor.audit_fixture(native_ce,old_joint['fixtures'][0]),'every paid native event has retained recipe')
print('PASS_REJECTED_PRE_FIX_INVERSE_RECIPE_POINTERS',flush=True)
RESULTS.append(dict(entry='joint_tail completed source word plus independent fixed native recipes',status=actual_joint['status'],witness_generated=False,fixed_witness_checked=True,fixtures=fixed_checks))
print('PASS_COMPLETE_JOINT_WORD_AND_FIXED_NATIVE_RECIPES',flush=True)
replay('literal_inverse_binding','run','joint-native/LITERAL-INVERSE-BINDING.json')
core=module('joint_coefficient_gate').formal_core()
need(body(core)==body(data('joint-native/JOINT-COEFFICIENT-GATE.json')['formal_original_column_core']),'full noncommutative core/public-reader inverse')
replay('general_source_gate','run','joint-native/GENERAL-SOURCE-GATE.json')


transfer=data('root-joint/SCAN-TRANSFER-SOURCES.json')
need(transfer['base']==META['scientific_base'],'canonical transfer base pin')
for row in transfer['sources']:
    need(hashlib.sha256(checked('source/transfer/'+row['path'])).hexdigest()==row['sha256'],'retained transfer source bytes')
need(PINS['original/joint-native/GENERAL-SOURCE-PROOF.md']['sha256']=='464bfd5ff9c9d8ef1270b1379361d13d42da452b8236ba73e97dd318e83b9778','original universal support proof pin')
for qvalue in range(2,65):
    nvalue,mvalue=2*qvalue+2,4*qvalue+4
    need(nvalue*mvalue-2*qvalue+(2*qvalue+4)==nvalue*mvalue+4,'equal-volume complete mass floor')
    for evalue in range(2*mvalue,4*mvalue):
        need(Fraction(evalue//mvalue)>=Fraction(evalue,2*mvalue),'integer chunk root-scan lower bound')
RESULTS.append(dict(entry='full_scan_transfer_sources_and_exact_integer_controls',equal_volume_native_normalization_required=True,partial_or_unequal_volume_bridge_excluded=True,no_new_kappa=True))
print('PASS_TRANSFER_SOURCE_BINDING equal-volume moment scope retained',flush=True)

report=dict(status='PASS_PORTABLE_CALLER_PACKAGE',claims=META['claims'],no_new_kappa=True,
 retained_files=len(PINS),mathematical_checks=RESULTS,source_bytes_compiled=True,
 historical_assertions_enabled=True,source_mutation_rejected=True,
 limits=['Written all-parameter proofs, finite exact replays and source integrity are distinct.',
 'No formal-kernel multiplication proof, physical supplier admission or selected frontier change.'])
if len(sys.argv)>1:
    need(len(sys.argv)==2 and sys.argv[1]=='--json','only --json is supported')
    print(json.dumps(report,indent=2,sort_keys=True))
else:print(report['status'],','.join(report['claims']),'no_new_kappa=true',flush=True)
