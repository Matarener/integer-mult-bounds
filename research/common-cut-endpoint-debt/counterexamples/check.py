#!/usr/bin/env python3
"""Exact dressed-cut counterexamples and finite paired vacancy decoders.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
Only the finite witnesses and declared written tensor law are asserted.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

PINS = {
 'frozen/INSERTION-SUPPLEMENT.md':'f01718e0987aef7c06198630be1a80824de45970f929073f48e1f2c09208fa50',
 'frozen/insertion_supplement.py':'7818a2e53b467aadddb61a488e6eef4d9f41320a87f4643f1aa2eeb3bb53acf1',
 'frozen/INSERTION-SUPPLEMENT.json':'c880bcd2e6a641d04a8f1a53e5cac29411487154d37e9da9db268a30011bd0c4',
 'frozen/pair_decoder.py':'87897cb26525098dc65aa7c4a5b4cac3a6f4619a1b0dd7ad68f0f9cb834aed42',
 'frozen/PAIR-DECODER.json':'01c55761fdd8eee88a15aae75d5751732b5869a4702a7cd9df94eedf0402dfdb',
 'frozen/clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
 'frozen/COMPILER-NOTICE.md':'a92f49c5ced455160fbedcc8954e3c9255e3605e88ad12ae5a84f1c4302986f1',
 'frozen/LICENSE':'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4',
}
DISABLED=set()
class AuditError(ValueError):
 def __init__(self,guard,witness=None):
  self.guard,self.witness=guard,witness
  super().__init__(guard)
def need(condition,guard,witness=None):
 if not condition and guard not in DISABLED:raise AuditError(guard,witness)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def serial(obj):
 if isinstance(obj,Q):return str(obj)
 if isinstance(obj,dict):return {str(k):serial(v) for k,v in obj.items()}
 if isinstance(obj,(tuple,list)):return [serial(v) for v in obj]
 return obj
ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0));UNITS=(ONE,(Q(0),Q(1)),(-Q(1),Q(0)),(Q(0),-Q(1)))
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def put(v,k,a):
 value=add(v.get(k,ZERO),a)
 if value!=ZERO:v[k]=value
 elif k in v:del v[k]
def mv(rows,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(rows))
def phase(Qrows,alpha,x):
 n=len(Qrows)
 return (sum(alpha[i] for i in range(n) if x>>i&1)+2*sum(((Qrows[i]>>(i+1))&(x>>(i+1))).bit_count() for i in range(n) if x>>i&1))%4
def evaluate(circuit,n,column):
 """Independent Gaussian-rational literal-gate evaluator, not compiler code."""
 v={column:ONE}
 for event in circuit:
  kind=event[0];w={}
  if kind=='P':w={mv(event[1],x):a for x,a in v.items()}
  elif kind=='X':w={x^event[1]:a for x,a in v.items()}
  elif kind=='D':w={x:mul(a,UNITS[phase(event[1],event[2],x)]) for x,a in v.items()}
  elif kind=='phase':w={x:mul(a,UNITS[event[1]%4]) for x,a in v.items()}
  elif kind=='C':
   axis,sign=event[1:];u=(Q(1,2),Q(sign,2));t=(Q(1,2),Q(-sign,2))
   for x,a in v.items():put(w,x,mul(a,u));put(w,x^axis,mul(a,t))
  else:raise AuditError('known literal Gaussian event',event)
  v={x:a for x,a in w.items() if a!=ZERO}
 return v
def matrix(op):return [evaluate(op.circuit,op.n,j) for j in range(1<<op.n)]
def mserial(cols):return [[[i,str(a),str(b)] for i,(a,b) in sorted(v.items())] for v in cols]
def discrepancy(actual,expected):
 if len(actual)!=len(expected):return {'column_count':[len(actual),len(expected)]}
 for j,(a,b) in enumerate(zip(actual,expected)):
  for i in sorted(set(a)|set(b)):
   if a.get(i,ZERO)!=b.get(i,ZERO):return {'input_column':j,'output_row':i,'actual':serial(a.get(i,ZERO)),'expected':serial(b.get(i,ZERO))}
 return None
def accept_equal(actual,expected,guard):
 witness=discrepancy(actual,expected);need(witness is None,guard,witness)
def monomial_defect(cols):
 rows=[]
 for j,col in enumerate(cols):
  if len(col)!=1:return {'input_column':j,'nonzero_output_rows':len(col),'column':mserial([col])[0]}
  i,a=next(iter(col.items()))
  if a not in UNITS:return {'input_column':j,'nonunit_phase':serial(a)}
  rows.append(i)
 if len(set(rows))!=len(rows):return {'output_rows_not_a_permutation':rows}
 return None
def accept_monomial(cols,guard):
 defect=monomial_defect(cols);need(defect is None,guard,defect)
def reject(name,thunk,guard):
 global DISABLED
 try:thunk()
 except AuditError as e:
  need(e.guard==guard,'intended rejection guard: '+name,{'expected':guard,'actual':e.guard});witness=e.witness
 else:raise AuditError('mutation unexpectedly accepted: '+name)
 prior=DISABLED
 try:
  DISABLED=prior|{guard}
  thunk()
 finally:DISABLED=prior
 return {'name':name,'guard':guard,'discrepancy':witness,'same_guard_deleted':'ACCEPTED'}
def module(name,raw):
 m=types.ModuleType(name);m.__file__=name+'.py';sys.modules[name]=m
 exec(compile(raw,m.__file__,'exec',dont_inherit=True,optimize=0),m.__dict__)
 return m

def insertion_audit(ce,historical):
 n=4;p,q,u,v=1,2,4,8
 Cp,Cq,Cu=ce.cgate(n,p),ce.cgate(n,q),ce.cgate(n,u)
 DX=Cu.then(Cp);DY=Cu.then(Cq);K=Cp.adjoint().then(Cq)
 M=ce.perm(n,[2,3,4,8]).then(ce.diag(n,[3,1,0,0]))
 address=ce.perm(n,[2,3,4,8])
 need(address.then(address).then(address).tab==ce.ident(n).tab,'common address order three')
 need(any(((a&b).bit_count()%2)!=int(i==j) for i,a in enumerate((2,3)) for j,b in enumerate((2,3))),'common address is nonorthogonal')
 H=DX.then(M).then(DX.adjoint());swap=ce.perm(n,[1,2,8,4]);Hs=DX.then(swap).then(DX.adjoint())
 def pull(D,logical):return D.adjoint().then(logical).then(D)
 X,Y=pull(DX,H),pull(DY,H);Xs,Ys=pull(DX,Hs),pull(DY,Hs)
 expectY=K.adjoint().then(M).then(K)
 operations={'DX':DX,'DY':DY,'K':K,'common_physical_M':M,'common_logical_H':H,'common_X_pullback':X,'common_Y_pullback':Y,'fresh_physical_swap':swap,'fresh_logical_H':Hs,'fresh_X_pullback':Xs,'fresh_Y_pullback':Ys}
 records={}
 for name,op in operations.items():
  cols=matrix(op)
  # Full ordinary basis columns independently check the compiler's phase.
  built=[]
  for j in range(1<<n):
   nums,den=op.zero_state(j);built.append({i:(Q(a,2**den),Q(b,2**den)) for i,(a,b) in enumerate(nums) if a or b})
  accept_equal(cols,built,'literal evaluator all columns')
  lowered,recipe=ce.lower_child(op)
  accept_equal(matrix(recipe),cols,'literal lowering all columns and phase')
  records[name]={'events':op.circuit,'signed_tableau':op.tab,'lowering':lowered,'lowered_events':recipe.circuit,'all_input_columns':mserial(cols)}
 for op,expected,guard in [(X,M,'common X exact pullback'),(Y,expectY,'common Y exact pullback'),(Xs,swap,'fresh X exact pullback'),(Ys,swap,'fresh Y exact pullback')]:accept_equal(matrix(op),matrix(expected),guard)
 for op in (X,Xs):accept_monomial(matrix(op),'simultaneous X monomial admission')
 for op in (Y,Ys):accept_monomial(matrix(op),'simultaneous Y monomial admission')
 image=ce.apply(Hs.tab,(u,u,1))
 need(image==(0,v,0),'past to future signed Pauli transport',{'actual':image})
 # Pauli phase is retained and independently checked on every address column.
 def pauli(x,z,ph):return [{j^x:UNITS[(ph+2*((z&j).bit_count()%2))%4]} for j in range(1<<n)]
 def compose(A,B):
  out=[]
  for col in B:
   v={}
   for j,b in col.items():
    for i,a in A[j].items():put(v,i,mul(a,b))
   out.append(v)
  return out
 transported=compose(matrix(Hs),compose(pauli(u,u,1),matrix(Hs.adjoint())))
 accept_equal(transported,pauli(*image),'exact signed Pauli conjugation')
 controls=[]
 missing=ce.perm(n,[2,3,4,8]);missingH=DX.then(missing).then(DX.adjoint())
 controls.append(reject('omit_common_quadratic_chirp',lambda:accept_monomial(matrix(pull(DY,missingH)),'simultaneous Y monomial admission'),'simultaneous Y monomial admission'))
 controls.append(reject('omit_past_frame_dressing',lambda:accept_monomial(matrix(pull(DX,swap)),'simultaneous X monomial admission'),'simultaneous X monomial admission'))
 # Change the actual inverse Cu event into its positive counterpart.
 wrong=ce.ident(n)
 for event in DX.adjoint().circuit:
  need(event[0]=='C','dressing inverse uses actual C gates')
  wrong=wrong.then(ce.cgate(n,event[1],1 if event[1]==u else event[2]))
 wrongH=DX.then(swap).then(wrong)
 controls.append(reject('replace_past_inverse_by_positive_gate',lambda:accept_equal(matrix(pull(DX,wrongH)),matrix(swap),'fresh X exact pullback'),'fresh X exact pullback'))
 phaseH=Hs.then(ce.Op(n,ce.identity(n),[('phase',1)]))
 need(phaseH.tab==Hs.tab,'global i preserves signed tableau')
 for D,guard in ((DX,'fresh X exact pullback'),(DY,'fresh Y exact pullback')):
  controls.append(reject('global_i_at_'+guard,lambda D=D,guard=guard:accept_equal(matrix(pull(D,phaseH)),matrix(swap),guard),guard))
 oldkeys={'common_axis_physical':'common_physical_M','common_axis_X_cut':'common_X_pullback','common_axis_Y_cut':'common_Y_pullback','fresh_swap_X_cut':'fresh_X_pullback','fresh_swap_Y_cut':'fresh_Y_pullback'}
 for old,new in oldkeys.items():need(serial(records[new]['lowering'])==historical[old],'historical insertion lowering reconciliation: '+old)
 need(serial(H.circuit)==historical['common_axis_logical_events'],'historical logical common-axis events')
 undressed_rank=ce.lower_child(pull(DX,swap))[0]['rank']
 need(undressed_rank==historical['undressed_swap_cut_rank']==2,'historical undressed rank two')
 return {'address_bits':n,'arbitrary_columns_per_field':1<<n,'operations':records,'transported_signed_Pauli':{'input':[u,u,1],'output':image,'all_input_columns':mserial(transported)},'undressed_logical_swap_native_rank':undressed_rank,'missing_chirp_Y_native_rank':ce.lower_child(pull(DY,missingH))[0]['rank'],'historical_fields_compared':list(oldkeys)+['common_axis_logical_events','undressed_swap_cut_rank'],'controls':controls}

# Complete two-field sparse matrices: each row is a map from arbitrary input
# column to an exact Gaussian rational coefficient.
def rowadd(a,b,coefficient=ONE):
 out=dict(a)
 for k,value in b.items():put(out,k,mul(coefficient,value))
 return out
def identity_rows(N):return [{j:ONE} for j in range(N)]
def translation_rows(kernel,N):return [{j^mask:value for mask,value in kernel.items()} for j in range(N)]
def apply_kernel(rows,kernel):
 return [sumrows([(rows[i^mask],value) for mask,value in kernel.items()]) for i in range(len(rows))]
def sumrows(terms):
 out={}
 for row,c in terms:out=rowadd(out,row,c)
 return out
def apply_matrix(rows,op):return [sumrows([(rows[j],value) for j,value in row.items()]) for row in op]
def transpose_columns(cols,N):return [{j:cols[j][i] for j in range(N) if i in cols[j]} for i in range(N)]
def accept_endpoint(rows,N):
 witness=discrepancy(rows,identity_rows(2*N))
 if witness is not None and 'input_column' in witness:
  witness['input_column'],witness['output_row']=witness['output_row'],witness['input_column']
 need(witness is None,'all arbitrary two-field decoder columns',witness)
def signed_swap(x,y):
 x=[rowadd(a,b,(-Q(1),Q(0))) for a,b in zip(x,y)]
 y=[rowadd(b,a) for a,b in zip(x,y)]
 x=[rowadd(a,b,(-Q(1),Q(0))) for a,b in zip(x,y)]
 return x,y

def decode(A,B,normalize,omit=None,replace_B=None):
 N=len(A);inputs=identity_rows(2*N)
 x=apply_matrix(inputs[:N],A);y=apply_matrix(inputs[N:],A)
 if omit!='normalize':y=apply_matrix(y,normalize)
 if omit!='signed_swap':x,y=signed_swap(x,y)
 BB=B if replace_B is None else replace_B
 if omit!='shear1':x=[rowadd(a,b) for a,b in zip(x,apply_matrix(y,BB))]
 if omit!='shear2':y=[rowadd(b,a,(-Q(1),Q(0))) for b,a in zip(y,apply_matrix(x,A))]
 if omit!='shear3':x=[rowadd(a,b) for a,b in zip(x,apply_matrix(y,BB))]
 return x+y

def decoder_audit(old,report,ce):
 cases=[];controls=[]
 for f in (1,2,3):
  N=1<<(2*f);a,b,square=old.vacancy(f)
  A=translation_rows(a,N);B=translation_rows(b,N);normalize=translation_rows({square:ONE},N)
  rows=decode(A,B,normalize);accept_endpoint(rows,N)
  oldcase=old.witness(f)
  need(oldcase==report['finite_cases'][f-1],'complete retained decoder finite case')
  need(len(a)==4**f and all(x!=ZERO for x in a.values()),'complete nonzero tensor translation support')
  need(set(a)==set(range(N)),'all distinct tensor translations')
  need(all(abs(r)+abs(i)==Q(1,2**f) and (r==0 or i==0) for r,i in a.values()),'tensor coefficient modulus')
  for omitted in ('normalize','signed_swap','shear1','shear2','shear3'):
   controls.append(reject('f'+str(f)+':omit_'+omitted,lambda omitted=omitted,A=A,B=B,normalize=normalize,N=N:accept_endpoint(decode(A,B,normalize,omitted),N),'all arbitrary two-field decoder columns'))
  cases.append({'f':f,'ordinary_input_columns':2*N,'vacancy_kernel':old.serial(a),'inverse_kernel':old.serial(b),'normalization_translation':square,'operator_shear_terms':4**f,'three_expanded_operator_shear_ADDs':3*4**f,'literal_signed_swap_unit_ADDs':3,'literal_translation_prepare_restore_scans':6*(4**f-1),'initial_second_field_translation_scans':1,'all_input_endpoint_rows':mserial(rows),'coefficient_l1':2**f,'historical_complete_finite_case':oldcase})
 A2,B2,square=old.vacancy(2);a1,b1,_=old.vacancy(1)
 N=16;A=translation_rows(A2,N);B=translation_rows(B2,N);normal=translation_rows({square:ONE},N);wrongB=translation_rows(b1,N)
 controls.append(reject('reuse_four_term_inverse_at_f2',lambda:accept_endpoint(decode(A,B,normal,replace_B=wrongB),N),'all arbitrary two-field decoder columns'))
 # A is the GL(2,2) order-three address permutation, so A^2 is a
 # non-involutory monomial. This makes the generic normalization issue real.
 op=ce.perm(2,[2,3]);A=transpose_columns(matrix(op),4);B=transpose_columns(matrix(op.adjoint()),4)
 A2=transpose_columns(matrix(op.then(op)),4);correct=transpose_columns(matrix(op.then(op).adjoint()),4)
 need(A2!=correct,'non-involutory monomial square fixture')
 good=decode(A,B,correct);accept_endpoint(good,4)
 bad=decode(A,B,A2)
 expected_bad=identity_rows(8)[:4]+apply_matrix(identity_rows(8)[4:],A)
 accept_equal(bad,expected_bad,'noninvolutory shortcut explicit endpoint')
 controls.append(reject('generic_A_squared_instead_of_inverse_square',lambda:accept_endpoint(bad,4),'all arbitrary two-field decoder columns'))
 generic={'address_bits':2,'ordinary_input_columns':8,'A_rows':mserial(A),'A_inverse_rows':mserial(B),'A_squared_rows':mserial(A2),'inverse_square_rows':mserial(correct),'corrected_endpoint_rows':mserial(good),'historical_shortcut_endpoint_rows':mserial(bad),'incorrect_endpoint':'(u,A v)','corrected_normalization':'(A^2)^-1 on the second field'}
 return {'finite_cases':cases,'generic_noninvolutory_square':generic,'controls':controls,'historical_generic_sentence':'Retained unchanged as provenance; corrected normalization is stated explicitly in the new proof.','cost_scope':'Expanded operator-ADD support and the literal three-unit-ADD signed exchange are counted. Address scans, coefficients, phases, precision and native child lowering are separate paid obligations.'}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 need(args.output.is_absolute(),'absolute output required')
 output=args.output.resolve()
 for protected in (Path(__file__).resolve().parent,args.inputs.resolve()):need(not output.is_relative_to(protected),'external output required')
 need(not args.output.exists() and not args.output.is_symlink(),'new output required')
 raw={name:(args.inputs/name).read_bytes() for name in PINS}
 need({name:sha(value) for name,value in raw.items()}==PINS,'authenticated captured input bytes')
 ce=module('c07_exact_compiler',raw['frozen/clifford_exact.py']);old=module('c07_original_pair_decoder',raw['frozen/pair_decoder.py'])
 insertion=insertion_audit(ce,json.loads(raw['frozen/INSERTION-SUPPLEMENT.json']))
 decoder=decoder_audit(old,json.loads(raw['frozen/PAIR-DECODER.json']),ce)
 controls=insertion['controls']+decoder['controls']
 result={'schema':'c07_counterexamples.v1','status':'PASS_EXACT_COUNTEREXAMPLES_NO_SUPPLIER_OR_KAPPA_CLAIM','scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','checker_sha256':sha(Path(__file__).read_bytes()),'authenticated_source_sha256':PINS,'insertion':insertion,'paired_decoder':decoder,'control_count':len(controls),'executed_named_guard_deletions':len(controls),'execution_scope':{'captured_compiler_optimize':0,'original_pair_functions_optimize':0,'old_insertion_main':'not executed; all named mathematical witnesses freshly reconstructed, finite lowering fields reconciled','old_pair_main':'not executed; original vacancy/witness functions and all their mathematical guards execute for f=1,2,3; complete finite-case objects compared'},'limits':['The dressed swap disproves past/future absorption from intersection invariance, not the corrected unary endpoint support theorem.','No D4 endpoint improvement is supplied.','Native rank zero does not make address, chirp or full-array scans free.','The 4^f term theorem applies to this direct translation expansion; it is not a general circuit complexity lower bound.','All-f native phase/control/precision and physical cost admission remain separate.','No radical/P112 source claim is added.']}
 payload=(json.dumps(serial(result),sort_keys=True,indent=2)+'\n').encode()
 if args.output.suffix=='.gz':payload=gzip.compress(payload,mtime=0)
 with args.output.open('xb') as stream:stream.write(payload)
 print(json.dumps({'status':result['status'],'controls':len(controls),'output_sha256':sha(payload)},sort_keys=True))
if __name__=='__main__':main()
