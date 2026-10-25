"""Apply PR5548's credited independent dense interpreter to four new P104 maps.

New inventory, bindings, rank-support checks and scoped controls: thu-nmrc
with substantial OpenAI Codex assistance. Apache-2.0. The reused arithmetic
engine is preserved byte-for-byte and retains Chris R/Clear1nsight's credit.
"""
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
from copy import deepcopy
import argparse,gzip,importlib.util,json,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;IN=ROOT/'inputs'
def need(ok,why):
 if not ok:raise ValueError(why)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def enc(x):return json.loads(json.dumps(x,sort_keys=True))
def read(n):
 raw=(IN/n).read_bytes();return json.loads(gzip.decompress(raw)if n.endswith('.gz')else raw)
def authenticate():
 p=read('INPUT-PINS.json')
 for n,h in p['files'].items():need(sha256((IN/n).read_bytes()).hexdigest()==h,'source authentication before import '+n)
 need(p['files']['pr5548_dense_check.py']==p['PR5548_dense_module_sha256']=='43fd40847a0853c0ac511d58ce77ef822a5c6dd1b25f662f01cefaa3196a2f7d','exact credited dense module')
 need(p['files']['PR5545-EXPORT.json']==p['PR5545_export_manifest_sha256'],'official source export manifest')
 m=read('PR5545-EXPORT.json');need(m['commit']==p['reviewed_source_commit']and len(m['files'])==33,'official source head and full inventory')
 rows={x['path']:x for x in m['files']}
 for n,path in [('SOURCE-WORD.json.gz','research/p104-full-frame-contact/WORD.json.gz'),('clifford_exact.py','research/p104-native-channel/vendor/clifford_exact.py'),('native_verify.py','research/p104-native-channel/vendor/native_verify.py')]:need(rows[path]['sha256']==p['files'][n]and rows[path]['size']==(IN/n).stat().st_size,'retained source '+path)
 inv=read('PR5548-CAPSULE-INVENTORY.json')['files'];need(inv['capsule/outputs/p104-native-contact-audit-20261025/check.py']==p['files']['pr5548_dense_check.py'],'published dense source inventory')
 for n in ('clifford_exact.py','native_verify.py'):need(inv['capsule/outputs/p104-native-contact-audit-20261025/sources/'+n]==p['files'][n],'compiler/literal definitions shared with audited source')
 return p

def inventory(old,new):
 need({k:v for k,v in old.items()if k!='program'}=={k:v for k,v in new.items()if k!='program'},'unchanged public/chart/target metadata')
 need([e[:-1]for e in old['program']if e[0]!='MOVE']==[e[:-1]for e in new['program']if e[0]!='MOVE'],'exact scalar and owned schedule')
 frames=old['frames'];data=[]
 for w in (old,new):
  d=defaultdict(list)
  for i,e in enumerate(w['program']):
   if e[0]=='MOVE':d[e[2],e[3]].append(dict(event=i,role=e[1],private=e[4]))
  data.append(d)
 before,after=data;added=set(after)-set(before);removed=set(before)-set(after);common=set(before)&set(after)
 need(added=={(17,720),(17,782),(615,207),(775,207)},'exact four added maps')
 def record(pair):
  a,b=pair
  return dict(source_frame=a,target_frame=b,source_basis=frames[a],target_basis=frames[b],rank=abs(len(frames[a])-len(frames[b])),before=before.get(pair,[]),after=after.get(pair,[]),multiplicity_delta=len(after.get(pair,[]))-len(before.get(pair,[])))
 changed=sorted(k for k in set(before)|set(after)if len(before.get(k,[]))!=len(after.get(k,[])))
 delta=Counter()
 for k in changed:delta[record(k)['rank']]+=record(k)['multiplicity_delta']
 delta={r:n for r,n in sorted(delta.items())if n};need(delta=={1:2,2:-3,3:1,4:-1,5:1},'complete literal local paid delta')
 return dict(before_distinct=len(before),after_distinct=len(after),common_distinct=len(common),added=[record(x)for x in sorted(added)],removed=[record(x)for x in sorted(removed)],all_changed_multiplicities=[record(x)for x in changed],local_paid_delta=delta,total_MOVE_count_before=sum(map(len,before.values())),total_MOVE_count_after=sum(map(len,after.values())),PR5548_paid_pairs=[[739,240],[240,127],[739,127]],PR5548_pair_overlap=[list(x)for x in sorted(added&{(739,240),(240,127),(739,127)})])

def compare(D,actual,expected,rank,label):
 a,b=D.compile_circuit(actual),D.compile_circuit(expected);digest=sha256();supports=Counter();anchor=None
 for column in range(512):
  left=D.dense_column(a,column);right=D.dense_column(b,column)
  need(left==right,label+' complete exact complex column '+str(column))
  re,im,d=left;need(sum(v*v for v in re)+sum(v*v for v in im)==1<<(2*d),label+' exact norm')
  support=sum(bool(x or y)for x,y in zip(re,im));need(support==1<<rank,label+' measured child rank')
  supports[support]+=1
  if column==0:
   row=next(i for i,(x,y)in enumerate(zip(re,im))if x or y);anchor=dict(column=0,row=row,real=re[row],imag=im[row],denominator_exponent=d)
  digest.update(json.dumps([column,d,re,im],separators=(',',':')).encode());digest.update(b'\n')
 return dict(columns=512,complex_entry_comparisons=512*512,matrix_sha256=digest.hexdigest(),column_support_histogram=dict(supports),absolute_anchor=anchor)

def calculate():
 pins=authenticate();old=read('SOURCE-WORD.json.gz');new=read('PUBLIC-WORD.json.gz');inv=inventory(old,new)
 C=load('added_maps_source_compiler',IN/'clifford_exact.py');V=load('added_maps_literal_definitions',IN/'native_verify.py');D=load('credited_pr5548_dense',IN/'pr5548_dense_check.py')
 records=[];program=[];controls={}
 for r in inv['added']:
  a,b,rank=r['source_frame'],r['target_frame'],r['rank'];label=f'{a}_to_{b}'
  need(len(old['frames'][b])-len(old['frames'][a])==rank and all(not x['private']for x in r['after']),'new positive public child')
  op=C.canonical_frame(9,tuple(old['frames'][a])).adjoint().then(C.canonical_frame(9,tuple(old['frames'][b])))
  recipe,_=C.lower_child(op);need(recipe['rank']==rank and recipe['right']is not None,'literal positive child rank')
  actual=V.recipe(recipe);expected=V.adjoint(V.frame(old['frames'][a],9))+V.frame(old['frames'][b],9)
  checked=compare(D,actual,expected,rank,label)
  phase_fault=actual+(('phase',1),)
  need(V.tableau(phase_fault)==V.tableau(actual),'phase-only mutant invisible to signed Pauli tableau')
  controls[label+'_wrong_global_phase']=dict(first_rejected_column=D.first_difference(phase_fault,expected),signed_tableau_unchanged=True)
  inverse=list(actual);i=next(i for i,g in enumerate(inverse)if g[0]=='C');inverse[i]=('C',inverse[i][1],-inverse[i][2]);controls[label+'_wrong_child_sign']=dict(first_rejected_column=D.first_difference(tuple(inverse),expected))
  wrong=deepcopy(recipe);wrong['left']['offset']^=1;controls[label+'_wrong_boundary']=dict(first_rejected_column=D.first_difference(V.recipe(wrong),expected))
  try:need((1<<(rank+1))==next(iter(checked['column_support_histogram'])),'wrong declared rank versus exact dense support')
  except ValueError:controls[label+'_wrong_declared_rank']='REJECTED'
  else:raise ValueError('rank mutant accepted')
  records.append(dict(**r,**checked,actual_gate_count=len(actual),expected_gate_count=len(expected)))
  program.append(dict(pair=[a,b],rank=rank,recipe=recipe,actual_literal=actual,expected_literal=expected))
  print('PASS added map',a,b,'rank',rank,'all512columns absolutephase',flush=True)
 # Authentication controls are pure byte checks before any source import.
 for name in ('clifford_exact.py','pr5548_dense_check.py'):
  need(sha256((IN/name).read_bytes()+b'\n').hexdigest()!=pins['files'][name],'source corruption rejected before import')
 return enc(dict(schema='p104-added-maps-dense-audit/1',status='PASS_FOUR_NEW_MAPS_ONLY',reviewed_source_commit=pins['reviewed_source_commit'],reviewed_public_commit=pins['reviewed_public_commit'],source_pins=pins['files'],inventory=inv,maps=records,controls=controls,source_authentication_controls=2,complex_entry_comparisons=4*512*512,base_dimension=512,engine='Unmodified PR5548 compile_circuit/dense_column/first_difference; new streamed comparison also checks every column norm/support. No vendor state/tableau is used for matrix equality.',positive_width_implication='Each exact base chart equality tensors factorwise; absolute phase i^theta lifts as i^(f theta), scalars remain exterior. This covers four added map interfaces only.',coverage=dict(previous_common_MOVE_pairs=inv['common_distinct'],all_old_paid_foundation_checked=False,whole_caller_replayed=False,full_framework_admitted=False,new_kappa=None),limits=['Uses credited source compiler and literal circuit descriptions; dense arithmetic interpreter is credited reuse from PR5548, not a new independent arithmetic implementation.','Does not independently close the old paid-map foundation, all-width native implementation premise, full caller dual, erasure, precision/tape/storage, uniform compiler or analytic recovery.','Normal/optimized equality is reproducibility, not a second implementation or human/proof-kernel acceptance.'])),enc(program)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r,p=calculate()
 for n,d in [('RESULT.json',r),('MAPS-PROGRAM.json',p)]:
  f=ROOT/n
  if a.write:f.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
  else:need(json.loads(f.read_bytes())==d,'frozen scientific receipt '+n)
 print(json.dumps(dict(status=r['status'],complex_entry_comparisons=r['complex_entry_comparisons'],science_sha256=sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest()),sort_keys=True))
if __name__=='__main__':main()
