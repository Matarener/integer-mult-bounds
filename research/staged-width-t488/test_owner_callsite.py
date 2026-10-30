# SPDX-License-Identifier: Apache-2.0
"""Production-callsite mutation controls using minimal fixtures; no full replay."""
import sys
if sys.flags.optimize: raise SystemExit("optimized Python is unsupported for verification")
"""Independent actual production-callsite and shared-validator mutation audit."""
from pathlib import Path
from collections import Counter
import ast,copy,gzip,hashlib,json,tempfile
import numpy as np
D=Path(__file__).parent;SRC=D/'owners/independent_literal.py';PINS=SRC.parent/'SOURCE-PINS.json';source=SRC.read_bytes();tree=ast.parse(source);sha=lambda b:hashlib.sha256(b).hexdigest()
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in('need','validate_owner_constraints','owner_control_tests')]
production=[n for n in tree.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and getattr(n.value.func,'id',None)=='validate_owner_constraints'];assert len(production)==1
rules=[n.args[1].value for fn in functions if fn.name=='validate_owner_constraints' for n in ast.walk(fn)if isinstance(n,ast.Call)and getattr(n.func,'id',None)=='need'];assert len(rules)==5

def prepare(disabled=(),skip_call=False):
 fs=copy.deepcopy(functions)
 for fn in fs:
  if fn.name=='validate_owner_constraints':
   for n in ast.walk(fn):
    if isinstance(n,ast.Call)and getattr(n.func,'id',None)=='need'and n.args[1].value in disabled:n.args[0]=ast.Constant(True)
 env={'np':np};mod=ast.Module(body=fs,type_ignores=[]);ast.fix_missing_locations(mod);exec(compile(mod,str(SRC),'exec'),env)
 statement=ast.Pass()if skip_call else copy.deepcopy(production[0]);mod=ast.Module(body=[statement],type_ignores=[]);ast.fix_missing_locations(mod);return env,compile(mod,str(SRC),'exec')
def fixture():
 n=408;return dict(t=np.zeros(n,dtype=int),h=np.arange(n),N=1,lo=np.array([[-1]]),hi=np.array([[0]]),o=np.zeros(n,dtype=int),c=np.zeros(n,dtype=int),key=np.arange(n),z=np.zeros(n,dtype=int),idx=np.arange(n),expected=np.zeros(n,dtype=int),H=Counter({1:65088}),profile={1:65088},T=1)
def corrupted(which):
 e=fixture()
 if which==0:e['h'][1]=0
 elif which==1:e['lo'][0,0]=0
 elif which==2:e['key'][1]=0
 elif which==3:e['z'][0]=1
 elif which==4:e['profile'][1]+=1
 return e
def run(env,code,fixture):
 e=dict(env);e.update(fixture);exec(code,e)
base,code=prepare();run(base,code,fixture());assert len(base['owner_control_tests']())==5
for j,rule in enumerate(rules):
 try:run(base,code,corrupted(j));raise RuntimeError('baseline acceptsbad')
 except ValueError as e:assert str(e)==rule
variants=[]
for disabled in [[r]for r in rules]+[rules]:
 env,code=prepare(disabled);run(env,code,fixture());accepted=[]
 for j,rule in enumerate(rules):
  try:run(env,code,corrupted(j))
  except ValueError:continue
  accepted.append(rule)
 assert set(accepted)==set(disabled),'external fixture harness failed to detect exact disabled set'
 try:env['owner_control_tests']();raise RuntimeError('embeddedcontrols missed disabledgate')
 except ValueError as e:assert 'control accepted'in str(e)
 variants.append({'disabled':disabled,'bad_inputs_accepted_by_mutant':accepted,'external_mutation_test_failed_as_required':True,'embedded_controls_detected':True})
env,code=prepare(skip_call=True)
for j in range(5):run(env,code,corrupted(j))
variants.append({'disabled':['production validation callsite'],'bad_inputs_accepted_by_mutant':rules,'external_mutation_test_failed_as_required':True,'embedded_function_tests_alone_would_not_cover_callsite':True})
assert SRC.read_bytes()==source,'source drift'
r={'status':'PASS_PRODUCTION_CALLSITE_MUTATIONS','source_sha256':sha(source),'baseline_valid_and_five_invalid_fixtures':True,'variants':variants,'scope':'Actual production callsite and shared validator executed with minimal fixture variables; no full owner replay. External corruption tests detect skipped production validation independently of embedded controls.','attribution':'Adapted from independent overlap test_fix_callsite.py; gate-disable methodology from PR3694 at cfee00c832d799b2fde891047734eb15cfbd1102.'}
print(json.dumps(r,sort_keys=True))
