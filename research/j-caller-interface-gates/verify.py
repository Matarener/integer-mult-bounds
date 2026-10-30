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
    relative=logical_name(path)
    return checked(relative)if relative in VIRTUAL else PHYSICAL_READ_BYTES(path)
def alias_read_text(path,encoding=None,errors=None):
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

# Immutable transport and full logical-payload authentication controls.
alias=next(iter(VIRTUAL));row=VIRTUAL[alias];transport=checked(row['storage_path'])
need(checked(alias)==unpack(transport,row['transport_sha256'],row['logical_sha256'],row['logical_bytes']),'identical lossless payload positive control')
rejection(lambda:unpack(transport+b'x',row['transport_sha256'],row['logical_sha256'],row['logical_bytes']),'compressed input transport hash')
rejection(lambda:unpack(transport,row['transport_sha256'],'0'*64,row['logical_bytes']),'compressed input logical bytes')
bad=transport[:-1]
rejection(lambda:unpack(bad,hashlib.sha256(bad).hexdigest(),row['logical_sha256'],row['logical_bytes']),'compressed payload decoding')
for alias in VIRTUAL:need(not(ROOT/alias).exists(),'logical data aliases stay in memory without writing package files')
print('PASS_LOSSLESS_READONLY_JSON_ALIAS_CONTROLS',flush=True)

manifest=data('joint-native/FOLLOWUP-SOURCES.json')
need(hashlib.sha256(checked('source/joint-native/FOLLOWUP-SOURCES.json')).hexdigest()==META['frozen_followup_manifest_sha256']=='6fbce979d23e1fc056973a546910dc53d6d5ffdced2aa090b0107c98f66a9fcf','frozen followup manifest pin')
need(len(manifest['source_pins'])==len(META['original_source_manifest_map'])==25,'complete frozen source inventory')
for original in manifest['source_pins']:
    relative=META['original_source_manifest_map'][original['path']]
    need(hashlib.sha256(checked(relative)).hexdigest()==original['sha256'],'original frozen source bytes '+relative)
print('PASS_ALL_25_FROZEN_ORIGINAL_SOURCE_PINS',flush=True)

replay('gl2_continuation_gate','run','joint-native/GL2-CONTINUATION-GATE.json')
replay('routing_inventory','run','joint-native/ROUTING-INVENTORY.json')
replay('routing_moment_gate','run','joint-native/ROUTING-MOMENT-GATE.json')
replay('dual_core_gate','run','joint-native/DUAL-CORE-GATE.json')
dual=replay('dual_core_binding','run','joint-native/DUAL-CORE-BINDING.json')
rejection(lambda:module('gl2_continuation_gate').beta_delta([[Fraction(1),Fraction(2)],[Fraction(2),Fraction(4)]]),'genuine scalar GL2')
rejection(lambda:module('routing_inventory').build(3,(0,0)),'complete routing schedule')
# A favorable optimistic envelope at b=0 is accepted. The 1/600 ceiling
# is not promoted into an impossibility for every positive or zero b.
q0=8;n0=2*q0+2;h0=n0*n0-q0;r0=2*((q0+1)//2)+6
need(Fraction(h0,n0)+Fraction(r0,2*n0)<n0,'q8 b=0 support-only envelope is a real scope escape')
for fixture in dual['fixtures']:
    q=fixture['q'];n=2*q+2;folded=fixture['name']=='folded-dual'
    need(fixture['prefix_native_histogram']=={'2':n*n-q+int(not folded)},'paid/folded exact prefix source bill')
    need(fixture['prefix_margin']==2*q-2*int(not folded),'paid extra query not conflated with folded prefix')
    if q==3 and folded:need(fixture['prefix_native_histogram']=={'2':61},'q3 source-note61 correction bound to unchanged producer')
transfer=data('root-joint/SCAN-TRANSFER-SOURCES.json')
for row in transfer['sources']:need(hashlib.sha256(checked('source/transfer/'+row['path'])).hexdigest()==row['sha256'],'full scan source pin')
RESULTS.append(dict(entry='scoped_domain_and_transfer_controls',singular_GL2_rejected=True,incomplete_route_rejected=True,q8_b0_optimistic_envelope_accepted=True,paid_folded_prefixes_distinguished=True,q3_prose_erratum_matches_original_61=True))

fusion_manifest=data('folded-fusion/MANIFEST.json')
need(hashlib.sha256(checked('source/folded-fusion/MANIFEST.json')).hexdigest()==META['fusion_freeze']['manifest_sha256']=='dde942457256b0f037a65eebeb5df822fe4d8911c0441657816c77a4c20c6f1c','repaired fusion manifest pin')
for original in fusion_manifest['files']:
    need(hashlib.sha256(checked('source/folded-fusion/'+original['path'])).hexdigest()==original['sha256'],'complete repaired fusion byte inventory')
for original in data('folded-fusion/INPUT-PINS.json')['files']:
    relative=META['fusion_freeze']['inputs_original_map'][original['frozen_copy']]
    need(hashlib.sha256(checked(relative)).hexdigest()==original['sha256'],'complete original fusion input bytes')
fusion=replay('verify_fusions','run','folded-fusion/VERIFICATION.json')
optimized_original=data('folded-fusion/VERIFICATION-OPTIMIZED.json')
need({k:body(v)for k,v in optimized_original.items()if k!='validation_mode'}=={k:body(v)for k,v in fusion.items()if k!='validation_mode'},'original optimized receipt has identical mathematics')
schema=module('fixture_schema');fixed=module('fixed_native_recipes');ce=module('native_model').ce
independent=module('audit_fusions');independent_receipt=data('fusion-audit/AUDIT.json')
need(independent_receipt['status']=='PASS_LITERAL_FUSION_WORDS_AND_CURRENT_METADATA','independent repaired-word admission')
independent_cases=[];fixed_cases=[]
for artifact in('SIMPLIFIED-FUSIONS.json','THREE-FUSIONS.json'):
    for fixture in data('folded-fusion/'+artifact)['fixtures']:
        # Recompute every derived schema field, including prefix inverse in
        # both orders. Stale shadow metadata cannot pass beside a valid word.
        stats=json.loads(json.dumps(schema.current_statistics(fixture['q'],fixture['prefix_events'],fixture['tail_events'])))
        for key,value in stats.items():need(value==fixture[key],'every current derived field '+key)
        fixed_cases.append(fixed.audit_fixture(ce,fixture))
        independent_cases.append(independent.check_fixture(artifact,fixture))
        rejection(lambda:module('verify_fusions').validate_scientific_metadata(dict(fixture,P2tilde=[])),'current fixture field allowlist')
        n,q=fixture['banks'],fixture['q'];third=artifact=='THREE-FUSIONS.json'
        need(fixture['histogram']==({'2':n*n-2,'4':1,'8':1}if third else{'2':n*n-1,'4':1,'6':1}),'actual full fused profile')
        need(fixture['prefix_D']==(2*q-4 if third else 2*q+2),'distinct default/third prefix margins')
        need(fixture['original_t_current_V_arity_per_f']==2*q+2,'changed original-t coefficient; old2q not reused')
need(body(independent_cases)==body(independent_receipt['cases']),'independent literal event/serialized-inverse/recipe audit cases')
need(body(independent.formal_rewrites())==body(independent_receipt['formal_all_parameter_rewrites']),'independent free-operator preload/core/public-column identities')
for row in independent_receipt['all_q_coefficient_checks']:
    q=row['q'];z,J,F,C=independent.required(q);gamma=independent.left_gamma(C);expected=[0]*z.n
    for h in(0,1):
        expected[h]=(1<<h)|(1<<(2+h));expected[2+h]=1<<h
        for s in range(5,2*q+2,2):expected[2*s+h]=1<<(2*s+h)
    need(gamma==tuple(expected)and independent.b.native_rank(C)==row['arity_per_f']==2*q+2,'independent finite polar-block binding of written all-q coefficient')
RESULTS.append(dict(entry='repaired_fusion_current_metadata_and_independent_actual_recipes',status=fusion['status'],cases=independent_cases,all_current_fields_recomputed=True,unknown_predecessor_field_rejected=True,fixed_recipe_controls=fixed_cases,scope='All-q written local rewrites remain conditional on the source interface; complete literal/selected-native serializations are q2/q3.'))
print('PASS_REPAIRED_FUSION_FULL_FIELDS_AND_INDEPENDENT_RECIPES',flush=True)

def screen_body(value):
    if isinstance(value,dict):return{k:screen_body(v)for k,v in value.items()if k!='elapsed_seconds'}
    if isinstance(value,(list,tuple)):return[screen_body(v)for v in value]
    return value
screens=module('one_site_absorption')
screen_inputs=[('SINGLE-SITE-ABSORPTION.json',[f for f in data('caller-joint/DUAL-CORE-RANK-ONLY.json')['fixtures']if f['name']=='folded-dual'],False),
 ('AFTER-TWO-SCREEN.json',data('folded-fusion/COMBINED-FUSIONS.json')['fixtures'],False),
 ('ALL-UNARY-AFTER-TWO-SCREEN.json',data('folded-fusion/SIMPLIFIED-FUSIONS.json')['fixtures'],True)]
for receipt,fixtures,include_zero in screen_inputs:
    actual=json.loads(json.dumps([screens.screen(f,include_zero=include_zero)for f in fixtures]));expected=data('folded-fusion/'+receipt)['results']
    need(screen_body(actual)==screen_body(expected),'complete finite single-site census '+receipt)
    for row in actual:
        # Every rejected case fails bank locality. No general Clifford-sum
        # classification is needed for this particular finite census.
        need(row['other_rejections']=={}and row['candidate_cut_checks']==row['not_single_bank']+len(row['accepted_single_site_fusions']),'all bank-local cases retained without a scalar or multi-ray filter')
    RESULTS.append(dict(entry='one_site_absorption.screen',receipt=receipt,include_zero_rank_existing_unaries=include_zero,cases=[{k:v for k,v in row.items()if k in('q','candidate_cut_checks','best_complete_mass','stock','other_rejections')}for row in actual],scope='Declared q2/q3 fixed scalar/address word templates as exact all-positive-f families. No multi-site, extra unary, changed scalar or global optimum claim.'))
    print('PASS_EXACT_SINGLE_SITE_CENSUS',receipt,flush=True)

report=dict(status='PASS_PORTABLE_J_INTERFACE_GATES',claims=META['claims'],no_new_kappa=True,
 mathematical_checks=RESULTS,retained_physical_files=len(PINS),lossless_logical_aliases=len(VIRTUAL),
 compressed_transport_bytes=sum(row['transport_bytes']for row in VIRTUAL.values()),
 complete_logical_alias_bytes=sum(row['logical_bytes']for row in VIRTUAL.values()),
 source_bytes_compiled=True,historical_assertions_enabled=True,
 limits=['The three gate domains and bounded constructive fusion are separate; arbitrary simultaneous changes and later retiming are not covered.',
 'Finite q2/q3 source bindings, all-q conditional interfaces, written proofs, exact replay and formal-kernel acceptance are distinct.',
 'Equal-volume full-bank/fixed-site/full-scan premises and the retained outer transfer remain explicit.'])
if len(sys.argv)>1:
    need(len(sys.argv)==2 and sys.argv[1]=='--json','only --json is supported')
    print(json.dumps(report,indent=2,sort_keys=True))
else:print(report['status'],'no_new_kappa=true',flush=True)
