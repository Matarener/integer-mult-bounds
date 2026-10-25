#!/usr/bin/env python3
"""Source-bound integrated native implementation contract; read-only replay.
Chris R / Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse,hashlib,json,subprocess,sys,types
from collections import Counter
from copy import deepcopy
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def local(name):
 path=HERE/name;obj=types.ModuleType(name.replace('.','_'));obj.__file__=str(path)
 exec(compile(path.read_bytes(),str(path),'exec'),obj.__dict__);return obj
A=local('auth.py');need=A.need;parse=A.parse
STATUS='PASS_QQ16_ACTUAL_RECURSIVE_BRIDGE_CONTRACT'

def physical(mode):
 result=subprocess.run([sys.executable,'-I','-O','-Werror','-B',str(HERE/'physical_fixture.py'),str(mode)],cwd=ROOT,capture_output=True,text=True,timeout=180)
 need(result.returncode==0,'actual physical fixture failure:'+result.stdout+result.stderr)
 need(not result.stderr,'physical fixture emitted stderr:'+result.stderr)
 return parse(result.stdout)

def compute():
 pins=A.authenticate() # Includes every canonical module before any inherited execution.
 word=parse((HERE/'vendor/PR4106-WORD.json').read_text());old=parse((HERE/'vendor/PR4015-WORD.json').read_text())
 numerical=parse((HERE/'vendor/PR4109-RESULT.json').read_text())
 need(numerical['exact_format']['signed_component_bits']=='P+28+6t' and numerical['exact_format']['new_minus_baseline_bits']==0,'inherited common caller format')
 need(Counter((e[2],e[3]) for e in word if e[0]=='line')==Counter((e[2],e[3]) for e in old if e[0]=='line'),'same actual signed child multiset')
 C=local('construction.py');F=local('feasibility.py');B=local('batch.py');R=local('realization.py')
 prefix=ROOT/'research/physical-complex-controller'
 source={n:(prefix/p).read_text() for n,p in {'machine':'machine.py','root_plan':'root_plan.py','selected_binding':'selected_binding.py','bank_packets':'bank_packets.py','physical_proof':'PROOF.md'}.items()}
 contract=C.audit(word,source);cost=F.audit(word);batch=B.audit(word)
 native=parse((ROOT/'research/qq16-line-normalized-decoder/RESULT.json').read_text())
 coverage=R.coverage(word,native)
 # Bind newly emitted actual MonomialPackets literals, including the 64
 # identity spectators, to every authenticated source recipe.
 dictionary={(r['port'],r['sign']):r for r in native['native']['signed_rank_one_recipes']}
 generated=[]
 for e in coverage['events']:
  r=dictionary[e['port'],e['sign']];recipe=C.signed_recipe(r['q'],r['sign'],73)
  for side in ('right','left'):
   rows=recipe[side]['matrix_rows']
   columns=[sum(((rows[j]>>i)&1)<<j for j in range(73)) for i in range(73)]
   need(columns[:9]==r[side+'_columns'] and columns[9:]==[1<<i for i in range(9,73)],'actual73D monomial source binding')
  need(recipe['left']['offset']==r['left_offset'],'actual signed affine offset')
  generated.append([e['event'],A.sha(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode())])
 # New source-aware semantic controls for the rejected alternative. No new
 # word is proposed by that route, and no savings are credited from it.
 negatives=[]
 for label,change in [('missing corrected-W source',lambda w:w.__setitem__(1703,['add','Z10','W1','1'])),('premature Z12 reuse',lambda w:w.__setitem__(800,['add','W0','Z12','1']))]:
  changed=deepcopy(word);change(changed)
  try:B.audit(changed)
  except (ValueError,KeyError):negatives.append(label)
  else:raise ValueError('accepted semantic control:'+label)
 axis=local('vendor/PR3884-tapes.py');fallback=R.audit(axis)
 execution={mode:physical(mode) for mode in ('2','signs','conversion')}
 need(execution['2']['recursive_boundaries']=={'enter':10,'return':10},'nontrivial actual recursive fixture')
 need(execution['2']['active_backend_reentry_rejected'],'no reentry on active backend')
 need(len(execution['signs']['fixtures'])==2,'both actual physical signs')
 need(len(execution['conversion']['rejections'])==7,'all physical boundary failures')
 result={'status':STATUS,'outcome_class':'B: implemented reusable prepared-packet native precision/return contract; complete QQ16 supplier/caller affordability unestablished',
 'source_inputs':pins,'scientific_base':'bb4bccbf42844d2801487450727c2f63e10d1d0f',
 'external_boundary':{'caller':'Unchanged4106word and4109 entry domain, with actual admitted e=73lambda physical parent capsule, complete passives/guards/stock, original component_bits H, disjoint closed native/wrapper inventories and borrowed source/output ports.',
 'backend':'Actual physical-complex-controller Machine C endpoint; inherited source-relative refinement, selected native/common-label, chronological hosting, ordinary B1/C0, Compact and long-record assumptions.',
 'return':'Every exact signed native callback projects to q_c,W_c, preserving borrowed payload/encoded descriptors and clearing owned bridge/backend work. No invocation on an active Machine.'},
 'precision':{'coarse_quantum':'h*2^(-9-3t), t=lambda-1>=0','coarse_component_bits':'W_c=P+28+6t',
 'reserve':'a=8lambda at admitted directleaf, otherwise2Blambda; B=1041408Gamma+2^100000',
 'working_quantum':'q_c*2^(-a)','minimum_signed_bits':'W_req=W_c+2a+1; extra1 covers Gaussian modulus vs component supremum',
 'actual_signed_bits':'H=p+2C0d+3, C0=2^210000, unchanged admitted parent component_bits',
 'admission':'H>=W_req; promote lowa zeros and H-W_c-a high sign bits; check exact fractional divisibility and signed return before projection',
 'sufficient_subdomain':'P<=p+4Bd+1, lambda<=d => W_req<H; an actualQQ16producer binding is not inferred',
 'completed_error':'zero conditional on retained exact Machine refinement and admission; reserve reusable after every exact return, no224a debt'},
 'complete_compatible_invoice':{'native':'sum actual224 T_C(lambda,v_j,H,p,d,K,guards,rows) with unchanged source recursion and internal parking included',
 'wrappers_maps':'448 T_M(H)+352 T_cover(W_c), each on actual domains; numerical head counts are not tape prices',
 'coarse_arithmetic':'1820 T_unit(W_c)+896 T_quarter(W_c)+416 T_clear(W_c)',
 'conversions':'Paid Count-to-unary setup; pattern construction, source-preserving promotion, checked projection, protected copies, erasure and marker returns. See bridge.py and PROOF.md for linear finite-state bound.',
 'additional':'Actual decoder acquisition/placement, descriptor arithmetic, current endpoint reconnection and retirement remain explicit nonzero unknown terms for a complete caller.',
 'callback_inventory_upper':'2I+2^20 owned physical tapes, I=2q_*^2+100696823; separate native Machine and ordinary/monomial inventory plus bounded bridge metadata. Existing caller inventory separate.',
 'space':'Complete coarse caller and retained returns + O_q(max_j v_j)+F_q, including working/protected copies; one callback active.',
 'relative':'4015/4106 use identical signed child multisets and common actualH; prescribed native/conversion bills agree.4106removes100whole-field unitADDs;800logicalallowance is separate. No fullphysical runtime dominance or globalcredit established.'},
 'literal_native_variants':contract['literal_coverage']['inventory'],
 'actual73D_recipe_count':len(generated),'actual73D_recipes_sha256':A.sha(json.dumps(generated,separators=(',',':')).encode()),
 'execution':execution,'alternative_controls':negatives,
 'significance':'Supplies an implemented paid source-tape bridge and zero completed native error/interior reserve for a named real recursive backend on its prepared ABI. Moves the missing decision to actual caller packet/output lease and full usage/reconnection bill. Descriptor or logical-coordinate reference alone is insufficient.',
 'remaining_obligations':['Install224owned recovery outputs and16private arrays without borrowing480dirty producer helpers or clobbering live query state.','Bind actual F0/B1 Q-to-G/currentbridge owner/phase and caller packet acquisition; no original-input/current-endpoint substitution.','Pay covers, physical layout/control/usage/retirement and prove a favorable complete supplier moment; no selected idle credit here.','Retained production backend all-size/refinement assumptions are inherited; reduced physical fixtures are not full O73/GL64 execution or human/formal approval.'],
 'rejected_alternatives':{'batch':'Seven lanes repairs one divisor only; fixed whole-field pooling <=224 fails at depth>=2 without padding/changed row split. No universal batch impossibility.',
 'tagged_axis':'Constructive7-tape signed ABI with exact invoice; directseek route has quadratic movement in its stated layout, no cheap recursive tariff. Other radix/layout routes remain open.'},
 'selected_kappa':'836330098538459/500000000000000000 unchanged; no new supplier, merge or frontier admission',
 'new_code_sha256':{n:A.sha((HERE/n).read_bytes()) for n in ('construction.py','feasibility.py','batch.py','realization.py','bridge.py','physical_fixture.py')}}
 return {'RESULT.json':result,'CONTRACT.json':contract,'BILL.json':cost,'BATCH.json':batch,'PHYSICAL.json':fallback,'COVERAGE.json':coverage}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 names=('RESULT.json','CONTRACT.json','BILL.json','BATCH.json','PHYSICAL.json','COVERAGE.json')
 if a.write:need(not any((HERE/n).exists() for n in names),'refuse overwrite')
 objects=compute()
 for n,obj in objects.items():
  if a.write:
   with(HERE/n).open('x') as f:f.write(json.dumps(obj,indent=2,sort_keys=True)+'\n')
  else:need(A.typed(parse((HERE/n).read_text()))==A.typed(obj),'whole typed receipt mismatch:'+n)
 print(STATUS);print('actual_recursive_C_bridge exact_return common_admitted_H all224_bound conditional_no_new_kappa')
if __name__=='__main__':main()
