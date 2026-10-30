#!/usr/bin/env python3
"""Exact full-cubic scalar word and pure-layer obstruction certificates.

Apache-2.0; substantial OpenAI Codex assistance. No native caller is claimed.
"""
import argparse
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

PINS={
 'frozen/README.md':'aa52e6b495e6d65d963ba4334759f4a53883e0a9b2016c0aef4e678e04bf1f3c',
 'frozen/INDEPENDENT-REVIEW.md':'5eba8852555ebd888f82686b24aa130f36dad45c79edf551079117ceb6c2d100',
 'frozen/cubic_gate.py':'0747f9ca9a81b7c839b62ad867a0a93c0a2944b52b40436e3acc4ce91b6245fd',
 'frozen/wide_gate.py':'beaecc74e3ceb660a8f80f740c126588af0a07496c40b475bc12204c0c92d496',
 'frozen/CUBIC-FOUR-CALL-GATE.json':'2050478b6fc2082775bc2eead709ee2f771c1fd2eca26a8cca4ad25eff142029',
 'frozen/WIDE-MIXED-CUBIC-GATES.json':'9e034e5e7653c579a7cc9972884db5592bf34ab1de50a0225ff0efe40081aefa',
}
DISABLED=set()
class AuditError(ValueError):
 def __init__(self,guard,witness=None):self.guard,self.witness=guard,witness;super().__init__(guard)
def need(test,guard,witness=None):
 if not test and guard not in DISABLED:raise AuditError(guard,witness)
def sha(x):return hashlib.sha256(x).hexdigest()
def serial(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [serial(v) for v in x]
 return x
def typed(a,b):
 if type(a) is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(typed(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(typed(x,y) for x,y in zip(a,b))
 return a==b
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def capture_module(name,raw):
 m=types.ModuleType(name);m.__file__='<captured '+name+'>';sys.modules[name]=m
 exec(compile(raw,m.__file__,'exec',dont_inherit=True,optimize=0),m.__dict__)
 return m

def rejection(name,thunk,guard):
 global DISABLED
 try:thunk()
 except AuditError as error:
  need(error.guard==guard,'intended control guard: '+name,{'actual':error.guard,'expected':guard});witness=error.witness
 else:raise AuditError('mutation unexpectedly accepted: '+name)
 before=DISABLED
 try:
  DISABLED=before|{guard};thunk()
 finally:DISABLED=before
 return {'name':name,'guard':guard,'witness':witness,'named_guard_deleted':'ACCEPTED'}
def mismatch(A,B):
 if len(A)!=len(B):return {'row_counts':[len(A),len(B)]}
 for i,(a,b) in enumerate(zip(A,B)):
  if len(a)!=len(b):return {'row':i,'column_counts':[len(a),len(b)]}
  for j,(x,y) in enumerate(zip(a,b)):
   if x!=y:return {'output_row':i,'input_column':j,'actual':serial(x),'expected':serial(y)}
 return None
def equal(A,B,guard):
 w=mismatch(A,B);need(w is None,guard,w)

# Independent rational regular-action engine. Polynomial multiplication is
# realized as ordinary matrix multiplication, not the source convolution code.
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def zeros(n,m):return [[F(0) for _ in range(m)] for _ in range(n)]
def mm(A,B):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]
def plus(A,B):return [[x+y for x,y in zip(a,b)] for a,b in zip(A,B)]
def minus(A,B):return [[x-y for x,y in zip(a,b)] for a,b in zip(A,B)]
def inverse(A):
 n=len(A);W=[list(map(F,row))+extra for row,extra in zip(A,eye(n))]
 for j in range(n):
  p=next((i for i in range(j,n) if W[i][j]),None);need(p is not None,'independent invertible scalar bridge')
  W[j],W[p]=W[p],W[j];scale=W[j][j];W[j]=[x/scale for x in W[j]]
  for i in range(n):
   if i!=j:
    scale=W[i][j];W[i]=[x-scale*y for x,y in zip(W[i],W[j])]
 result=[row[n:] for row in W];equal(mm(A,result),eye(n),'independent exact scalar inverse');return result
def lift(poly):
 n=len(poly);out=zeros(3*n,3*n)
 for i,row in enumerate(poly):
  for j,c in enumerate(row):
   for a in range(3):
    for b in range(3):out[3*i+a][3*j+b]=F(c[(a-b)%3])
 return out
def scalar_lift(A):return lift([[(F(x),F(0),F(0)) for x in row] for row in A])
def raw_word(word):
 W=eye(9);B=eye(3)
 for event in word:
  if event['op']=='FREE':C=[[F(x) for x in row] for row in event['matrix']];W=mm(scalar_lift(C),W);B=mm(C,B)
  else:
   i,j,s,e=event['dst'],event['src'],event['sign'],event.get('power',1)
   need(i!=j and s in (-1,1) and e in (1,2),'declared actual paid cubic alphabet')
   T=eye(9)
   for b in range(3):T[3*i+(b+e)%3][3*j+b]+=s
   W=mm(T,W);C=eye(3);C[i][j]+=s;B=mm(C,B)
 return W,B,mm(scalar_lift(inverse(B)),W)
def accept_direction(g,D):
 rank=g.coeff_span(D)
 need(rank==1,'constant rational bank direction',{'coefficient_span_rank':rank})
def accept_nilpotent(g,A):
 rank=g.rankq(A);square=g.qmm(A,A)
 need(rank==1 and square==zeros(3,3),'rank-one square-zero bank direction',{'rank':rank,'square':serial(square)})
def regular_audit(g,report):
 controls=[];fixtures=[]
 for index,record in enumerate(report['normalization_fixtures']):
  W,B,P=raw_word(record['word']);expected=lift(record['normalized_full_ring_matrix'])
  equal(P,expected,'complete augmentation-normalized regular operator')
  for A in record['constant_rank1_directions']:
   A=[[F(x) for x in row] for row in A]
   accept_nilpotent(g,A)
   accept_direction(g,g.matsub(g.transvection(A),g.eye()))
  controls.append(rejection('fixture'+str(index)+':omit_final_augmentation',lambda W=W,expected=expected:equal(W,expected,'complete augmentation-normalized regular operator'),'complete augmentation-normalized regular operator'))
  wrong=json.loads(json.dumps(record['word']))
  first=next(e for e in wrong if e['op']=='PAID');first['power']=3-first.get('power',1)
  wrongP=raw_word(wrong)[2]
  controls.append(rejection('fixture'+str(index)+':change_query_power',lambda wrongP=wrongP,expected=expected:equal(wrongP,expected,'complete augmentation-normalized regular operator'),'complete augmentation-normalized regular operator'))
  fixtures.append({'ordinary_rational_columns':9,'augmentation':B,'raw_regular_operator':W,'normalized_regular_operator':P})
 target=lift([[g.N if i==j else g.Z for j in range(3)] for i in range(3)])
 polyword=report['controls']['excluded_N_dependent_four_factor_word'];word=[lift(T) for T in polyword]
 def product(factors):
  P=eye(9)
  for T in factors:P=mm(T,P)
  return P
 P=product(word);equal(P,target,'complete full-cubic target on all columns')
 literal_inverse=[minus(eye(9),minus(T,eye(9))) for T in reversed(word)]
 equal(mm(product(literal_inverse),P),eye(9),'literal inverse on all regular columns')
 for j in range(4):
  omitted=product(word[:j]+word[j+1:])
  controls.append(rejection('excluded_word_omit_factor'+str(j),lambda omitted=omitted:equal(omitted,target,'complete full-cubic target on all columns'),'complete full-cubic target on all columns'))
  D=g.matsub([[tuple(map(F,c)) for c in row] for row in polyword[j]],g.eye())
  controls.append(rejection('operator_dependent_direction'+str(j),lambda D=D:accept_direction(g,D),'constant rational bank direction'))
 bad=(F(1),F(2),F(1));badmatrix=lift([[bad if i==j else g.Z for j in range(3)] for i in range(3)])
 controls.append(rejection('omit_eigenvalue_one_component',lambda:equal(badmatrix,target,'complete full-cubic target on all columns'),'complete full-cubic target on all columns'))
 controls.append(rejection('replace_paid_direction_by_identity',lambda:accept_nilpotent(g,eye(3)),'rank-one square-zero bank direction'))
 return {'basis_order':'bank0*(1,N,N2), bank1*(1,N,N2), bank2*(1,N,N2)','normalization_fixtures':fixtures,'excluded_operator_dependent_word':word,'excluded_word_full_operator':P,'excluded_word_literal_inverse':product(literal_inverse),'primitive_only_false_target_regular_operator':badmatrix,'primitive_only_false_target_augmentation':4,'controls':controls}

# This fresh finite stage exposes all coefficient matrices rather than
# inferring a central solution from intentionally noncentral fixtures.
def field_audit(w):
 controls=[];n,k=3,5
 uc=[[F(0) for _ in range(k)] for _ in range(n)];vr=[[F(0) for _ in range(n)] for _ in range(k)]
 for h in range(k):
  j=h%n;uc[j][h]=1;uc[(j+1)%n][h]=h+1;vr[h][(j+2)%n]=F((-1)**h)
 U,V=w.const(uc),w.const(vr);B=w.mm(V,U);L=[[B[i][j] if i>j else w.Z for j in range(k)] for i in range(k)];up=[[B[i][j] if i<j else w.Z for j in range(k)] for i in range(k)]
 al=[w.sub(w.N if h%2==0 else w.N2,w.O) for h in range(k)];t=w.sub(w.N,w.O)
 gi=w.negmat(L)
 for h in range(k):gi[h][h]=w.kinv(al[h])
 G=w.inv(gi);W=w.eye(n)
 for h in range(k):W=w.mm(w.ma(w.eye(n),[[w.scale(al[h],uc[i][h]*vr[h][j]) for j in range(n)] for i in range(n)]),W)
 equal(W,w.ma(w.eye(n),w.mm(w.mm(U,G),V)),'interaction resolvent full coefficients')
 C=w.ms(B,w.scalar(gi,t));A=[list(r) for r in up];H=[list(r) for r in L]
 for h in range(k):
  if h%2==0:A[h][h]=w.neg(w.O)
  else:H[h][h]=w.O
 equal(C,w.ma(A,w.scalar(H,w.N)),'complementary triangular coefficient split')
 defect=w.ms(W,w.scalar(w.eye(n),w.N))
 def accept_defect(d):equal(w.mm(w.mm(U,G),C),w.mm(d,U),'target-sensitive interaction identity')
 accept_defect(defect)
 controls.append(rejection('drop_noncentral_target_defect',lambda:accept_defect(w.zero(n,n)),'target-sensitive interaction identity'))
 wrongH=[list(r) for r in H];wrongH[1][1]=w.neg(w.O)
 controls.append(rejection('wrong_second_power_diagonal_sign',lambda:equal(C,w.ma(A,w.scalar(wrongH,w.N)),'complementary triangular coefficient split'),'complementary triangular coefficient split'))
 interaction={'n':n,'k':k,'U':U,'V':V,'B':B,'G_inverse':gi,'G':G,'W':W,'C':C,'A':A,'H':H,'target_defect':defect,'rank_C':w.rank(C),'r_if_central':k-n}
 # Nontrivial Jordan blocks at the nonzero eigenvalue require more than
 # a first power in the projector formula. Zero remains semisimple.
 PA=w.const([[-1,1,2,0],[0,-1,0,3],[0,0,0,0],[0,0,0,0]])
 PH=w.const([[0,0,0,0],[0,0,0,0],[1,0,1,0],[0,2,1,1]])
 projections=[]
 def accept_projection(M,P):
  good=w.mm(P,P)==P and w.mm(P,M)==M and w.mm(M,P)==M and w.rank(P)==w.rank(M)
  need(good,'image-kernel spectral projector',{'idempotence_defect':serial(w.ms(w.mm(P,P),P)),'projection_rank':w.rank(P),'matrix_rank':w.rank(M)})
 for tag,M,base in [('upper',PA,w.ma(w.eye(4),PA)),('lower',PH,w.ms(w.eye(4),PH))]:
  P=w.ms(w.eye(4),w.power(base,4));accept_projection(M,P)
  wrong=w.ms(w.eye(4),base)
  controls.append(rejection(tag+':truncate_Jordan_projector',lambda M=M,wrong=wrong:accept_projection(M,wrong),'image-kernel spectral projector'))
  projections.append({'kind':tag,'matrix':M,'projector':P,'diagonal':[P[i][i] for i in range(4)],'nonzero_eigenvalue_multiplicity':2,'rank':w.rank(M)})
 # Pure four-layer identities include explicit noncentral remainders.
 A=w.const([[0,1,0],[0,0,0],[0,0,0]]);B=w.const([[0,0,0],[-1,0,0],[0,0,0]])
 C=w.const([[0,0,0],[0,0,1],[0,0,0]]);D=w.const([[0,0,0],[0,0,0],[0,1,0]])
 def squarezero(M):need(w.mm(M,M)==w.zero(len(M),len(M)),'whole layer square-zero premise',{'square':serial(w.mm(M,M))})
 for M in (A,B,C,D):squarezero(M)
 t2=w.sub(w.N2,w.O);I=w.eye(3)
 Qm=w.mm(w.ma(I,w.scalar(D,t2)),w.ma(I,w.scalar(C,t)))
 target=w.scalar(w.mm(w.ms(I,w.scalar(A,t)),w.ms(I,w.scalar(B,t2))),w.N)
 Fm=w.ma(w.ma(w.ma(I,w.scalar(A,(F(2),F(0)))),B),w.scalar(w.mm(A,B),(F(3),F(0))))
 q0=w.ma(w.ms(w.ms(I,C),w.scalar(D,(F(2),F(0)))),w.scalar(w.mm(D,C),(F(3),F(0))));q1=w.ms(C,D)
 equal(Qm,w.ma(q0,w.scalar(q1,w.N)),'pure left-pair exact coefficient identity')
 equal(target,w.ma(w.ms(A,B),w.scalar(Fm,w.N)),'pure right-inverse exact coefficient identity')
 e=w.ms(q0,w.ms(A,B));f=w.ms(q1,Fm)
 lhs=w.ms(w.mm(D,w.ms(Fm,I)),w.ma(A,w.mm(A,B)))
 rhs=w.scalar(w.ms(w.ma(e,f),w.scalar(w.mm(D,f),(F(3),F(0)))),(F(1,3),F(0)))
 equal(lhs,rhs,'pure-layer target-defect identity')
 controls.append(rejection('pure_layers_drop_target_defect',lambda:equal(lhs,w.zero(3,3),'pure-layer target-defect identity'),'pure-layer target-defect identity'))
 controls.append(rejection('pure_layers_change_cross_coefficient_sign',lambda:equal(Qm,w.ma(q0,w.scalar(w.ma(C,D),w.N)),'pure left-pair exact coefficient identity'),'pure left-pair exact coefficient identity'))
 P=w.mm(w.ma(I,B),w.ma(I,A));Pinv=w.mm(w.ms(I,A),w.ms(I,B))
 equal(w.mm(P,Pinv),I,'two-square-zero-layer literal inverse')
 need(w.trace(P)==w.trace(Pinv),'two-layer reciprocal trace')
 wrong=w.mm(w.ms(I,B),w.ms(I,A))
 controls.append(rejection('reverse_two_layer_inverse_order',lambda:equal(w.mm(P,wrong),I,'two-square-zero-layer literal inverse'),'two-square-zero-layer literal inverse'))
 controls.append(rejection('mixing_inside_layer_breaks_squarezero',lambda:squarezero(w.ma(A,B)),'whole layer square-zero premise'))
 return {'interaction_fixture':interaction,'nonzero_Jordan_projection_fixtures':projections,'pure_layer_fixture':{'A':A,'B':B,'C':C,'D':D,'left_pair':Qm,'right_inverse_target':target,'rational_defect':e,'primitive_defect':f,'forced_relation_lhs':lhs,'actual_defect_rhs':rhs},'two_layer_fixture':{'P':P,'literal_inverse':Pinv,'trace':w.trace(P)},'controls':controls}

def invoice(n,k,s):
 need(n>0 and k>0 and s>0 and k<=s*(n//2),'matching-layer invoice domain')
 H={1:8*k,2:40*k,3:16*k,5:12*(n*s-2*k)};m=2+5*s;stock=12*n
 mass=sum(r*c for r,c in H.items());need(m*stock-mass==24*n-16*k,'complete optimistic invoice identity')
 return {'n':n,'k':k,'layers':s,'m':m,'W':stock,'H':H,'mass':mass,'D':m*stock-mass}
def accept_invoice(actual,expected):need(actual==expected,'all inactive-bank idle charges',{'actual':actual,'expected':expected})
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 need(a.output.is_absolute(),'absolute output required')
 for parent in (Path(__file__).resolve().parent,a.inputs.resolve()):need(not a.output.resolve().is_relative_to(parent),'external output required')
 need(not a.output.exists() and not a.output.is_symlink(),'new output required')
 raw={p:(a.inputs/p).read_bytes() for p in PINS};need({p:sha(v) for p,v in raw.items()}==PINS,'authenticated captured source bytes')
 g=capture_module('c09_frozen_cubic',raw['frozen/cubic_gate.py']);w=capture_module('c09_frozen_wide',raw['frozen/wide_gate.py'])
 oldc=json.loads(json.dumps(g.receipt()));oldw=json.loads(json.dumps(w.receipt()))
 need(typed(oldc,json.loads(raw['frozen/CUBIC-FOUR-CALL-GATE.json'])),'complete typed historical cubic receipt')
 need(typed(oldw,json.loads(raw['frozen/WIDE-MIXED-CUBIC-GATES.json'])),'complete typed historical wide receipt')
 regular=regular_audit(g,oldc);field=field_audit(w)
 invoices=[invoice(*x) for x in [(3,5,5),(6,9,4),(9,13,4)]]
 H=invoices[0]['H'];accept_invoice(H,invoice(3,5,5)['H']);wrong=dict(H);wrong[5]=0
 controls=regular['controls']+field['controls']+[rejection('omit_all_idle_banks',lambda:accept_invoice(wrong,H),'all inactive-bank idle charges')]
 balances=[]
 for n in (3,6,9,12,24,48):
  k=n+(n+3)//3;r=k-n
  balances.append({'n':n,'minimum_mixed_k':k,'r':r,'each_power_count_minimum':max(0,k-2*r),'each_power_count_maximum':min(k,2*r),'homogeneous_k_minimum':2*n,'determinant_requires_multiple_of_three':True})
 result={'schema':'c09_cubic_scalar_gates.v1','status':'PASS_FULL_CUBIC_SCALAR_WORD_AND_PURE_LAYER_OBSTRUCTIONS','scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','checker_sha256':sha(Path(__file__).read_bytes()),'input_sha256':PINS,'complete_historical_receipts':{'cubic':oldc,'wide':oldw},'independent_full_regular_action':regular,'fresh_cyclotomic_coefficient_certificates':field,'conditional_complete_optimistic_invoices':invoices,'alphabet_balance_corollary':balances,'production_controls':controls,'actual_semantic_rejections':len(controls),'executed_named_guard_deletions':len(controls),'source_execution':{'unchanged_captured_modules':['cubic_gate.py','wide_gate.py'],'optimize':0,'receipt_functions_replayed_completely':True},'limits':['The theorem concerns identity in full Q[N]/(N^3-1), not any fixed nonfaithful operator representation.','n3 arbitrary-polynomial coefficient bound and wide mixed N/N2 bounds have different alphabets.','Four pure layers are excluded; four internally mixed layers are not excluded here.','Finite exact fixtures validate identities and controls, not the all-word quantifiers.','No positive scalar synthesis, native frame admission, source-code transport, owner stock, precision, physical runtime or new kappa claim.','Quadratic continuation is preserved only as historical context and is outside this contribution.']}
 encoded=(json.dumps(serial(result),sort_keys=True,indent=2)+'\n').encode()
 if a.output.suffix=='.gz':encoded=gzip.compress(encoded,mtime=0)
 with a.output.open('xb') as f:f.write(encoded)
 print(json.dumps({'status':result['status'],'controls':len(controls),'sha256':sha(encoded)},sort_keys=True))
if __name__=='__main__':main()
