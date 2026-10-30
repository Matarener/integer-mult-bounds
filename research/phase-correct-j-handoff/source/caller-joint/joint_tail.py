#!/usr/bin/env python3
"""A complete, fully paid joint J cleanup with scalar-only public readers.

Every inverse is a literal inverse of a unitary Clifford or a reversible
scalar event. No inverse of a nonunit operator is an implementation primitive.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json
from joint_algebra import *
from joint_prefix import build as build_prefix, original_formula, native_pool, metadata, check_literal_family
HERE=Path(__file__).resolve().parent

def tail(q,lower=True):
 P=build_prefix(q);n,m,k=P.n,P.m,2*q+1
 metadata(P.events,q)
 W=Word(n,m);F=prefix(m,k);J=j_operator(m);N=n_pair(m,0);A=N.inv()@J
 z=Model(1,k);_,Jce=kernels(z);Fce=z.prefix(k);Ace=mul(z.N.adjoint(),Jce)
 B={s:plane_swap(m,0,s)@A for s in range(1,k+1)}
 Bce={s:mul(z.P[s-1],Ace)for s in range(1,k+1)}
 E=qc.identity(m);Ece=z.I
 for r in range(2,q+1):E=B[2*r]@E;Ece=mul(Bce[2*r],Ece)
 Du=E@B[3]@J;Duce=mul(Ece,Bce[3],Jce)
 Q1=J.inv()@B[1]@J;Q1ce=mul(Jce.adjoint(),Bce[1],Jce)
 pool=native_pool()

 def custom(bank,g,literal,exponent,label,recipe_id):
  physical=F@g@F.inv();actual=mul(Fce,literal,Fce.adjoint())
  r=qc.rank(physical.polar())
  need(ce.rank(x for x,y,p in actual.tab[m:])==r,'independent physical Clifford B rank')
  for inverse in(False,True):
   key=recipe_id+('inv'if inverse else'')
   if key in pool:continue
   op=actual.adjoint()if inverse else actual
   entry={'one_coordinate_tableau':[list(t)for t in op.tab],'one_coordinate_definition_circuit':op.circuit,
          'phase_exponent':-exponent if inverse else exponent,'native_rank':r}
   if lower:
    rec,compiled=ce.lower_child(op);same(compiled,op,'complete joint query selected-native actual Gaussian phase')
    need(rec['rank']==r,'selected native child rank')
    entry['selected_native_recipe']=rec
   pool[key]=entry
  W.unary(bank,physical,label,r!=0,{'kind':'tail','inverse':False})
  e=W.events[-1];e['native_recipe_id']=recipe_id;e['recipe_embedding']=list(range(m));e['phase_exponent']=exponent
  e['one_coordinate_literal_circuit']=actual.circuit;e['one_coordinate_tableau']=[list(t)for t in actual.tab]
  check_literal_family(e,m)

 def native(bank,plane,label):
  W.unary(bank,n_pair(m,plane),label,True,{'kind':'N','plane':plane,'inverse':False});metadata([W.events[-1]],q)
 def address(bank,plane,label):
  W.unary(bank,plane_swap(m,0,plane),label);metadata([W.events[-1]],q)
 def negate(bank,label):
  g=qc.Mono(qc.identity(m).rows,0,(0,)*m,(0,)*m,0,2)
  W.unary(bank,g,label);e=W.events[-1];op=ce.Op(m,ce.identity(m),[('phase',2)])
  e['phase_exponent']=2;e['one_coordinate_literal_circuit']=op.circuit;e['one_coordinate_tableau']=[list(t)for t in op.tab]
  check_literal_family(e,m)

 # Recover the current-reader coordinate w2. The final extraction counts.
 for r in range(q,1,-1):
  o=2*r+1
  address(3,o,f'w reverse{r} ADDRESS')
  native(3,o,f'w reverse{r} selected native2')
  if r==q:negate(3,'final extraction D_final inverse sign')
  W.add(3,2*r,1,f'w reverse{r} completed Jb reader')
 # One unitary query recovers z, with the full base B3 J=P3 N included.
 custom(1,Du.inv(),Duce.adjoint(),-1,'joint U coordinate recovery','tail-Du-recovery')

 # In F coordinates p=w2 and q=z. T=sum already completed J*(a,b).
 # p+Jb1-2T = Krow1(t0-T,k0), q+Jb1-T = Krow2(t0-T,k0).
 W.add(3,2,1,'p shared original b1 reader');W.add(1,2,1,'q shared original b1 reader')
 publics=[0]+[2*r for r in range(1,q+1)]
 for bank in publics:
  W.add(3,bank,-2,'p scalar-only T reader');W.add(1,bank,-1,'q scalar-only T reader')

 # Exact two-query inverse of the full coupled K, not a diagonal-core promise.
 # p bank3 / q bank1 end as original(t0-T,k0).
 negate(3,'K inverse first sign');W.swap(3,1,'K inverse bank bridge')
 W.add(1,3,1,'K inverse first scalar sum')
 custom(1,B[2].inv(),Bce[2].adjoint(),0,'K inverse B2 unitary query','tail-B2-recovery')
 W.add(3,1,-1,'K inverse scalar difference')
 custom(3,Q1.inv(),Q1ce.adjoint(),0,'K inverse Q1 unitary query','tail-Q1-recovery')
 W.add(1,3,1,'K inverse final scalar sum')
 for bank in publics:W.add(3,bank,1,'restore t0 from t0-T')
 custom(3,J,Jce,1,'literal F J original t output','tail-J')
 custom(1,J,Jce,1,'literal F J original k output','tail-J')
 W.swap(1,3,'restore original t0/k0 output slots')

 target=mono(F@J);Id=eye(n,m)
 expected=[[target if i==j else{}for j in range(n)]for i in range(n)]
 complete=mm(W.M,P.M);inverse=mm(P.Mi,W.Mi)
 need(complete==expected,'every original independent input has full F_k J output')
 need(mm(complete,inverse)==mm(inverse,complete)==Id,'complete physical literal inverse both orders')
 need(mm(W.M,W.Mi)==mm(W.Mi,W.M)==Id,'tail is reversible on every arbitrary entering field')
 need(qc.replay(P.events+W.events,n,m)==expected,'separate full physical event replay')
 inv_events=W.inverse_events()
 for e in inv_events:
  if e['kind']not in('ADD','BANK_SWAP'):check_literal_family(e,m)
 need(qc.replay(inv_events,n,m)==W.Mi,'literal tail inverse metadata matches all original columns')
 hist=Counter(e['rank_per_f']for e in W.events if e['kind']=='NATIVE')
 need(hist=={2:q+1,4:2,6:1},'complete conservative joint-tail histogram')
 total=Counter(e['rank_per_f']for e in P.events+W.events if e['kind']=='NATIVE')
 need(sum(r*c for r,c in total.items())==n*m+16,'complete joint bill has deficit minus16')
 return {'q':q,'width':n,'banks':n,'ambient_arity':m,'events':W.events,'inverse_events':inv_events,
         'tail_matrix':sm(W.M),'tail_inverse':sm(W.Mi),'native_recipe_pool':pool,
         'tail_histogram':dict(hist),'tail_native_mass':2*q+16,'complete_histogram':dict(total),
         'complete_native_mass':n*m+16,'stock':n*m,'D':-16,
         'full_events':P.events+W.events,'all_original_columns':n,'literal_inverse_orders':2,
         'correctness_identity':'tail * physical_prefix = diag(F_k J) on every original input for every positive f',
         'reader_identity':'p=w2+Jb1-2T, q=Du^-1 U+Jb1-T equal K(t0-T,k0); T=sum completed J(a,b)',
         'limits':['Conservative fully paid complete caller, not a saving.','No nonunit operator inverse is an implementation primitive.',
                   'The q-1 reverse-reader exposures include the final extraction.','Every helper/public value is arbitrary and retained; no extra helper or private field.']}

def produce(lower=True):
 fixtures=[tail(q,lower)for q in(2,3)]
 trial=fixtures[1];events=list(trial['full_events'])
 at=next(i for i,e in enumerate(events)if e.get('label')=='restore t0 from t0-T')
 wrong=events[:at]+events[at+1:]
 need(qc.replay(wrong,8,16)!=qc.replay(events,8,16),'omitted original-input t reader rejected')
 wrong=[dict(e)for e in events]
 at=next(i for i,e in enumerate(wrong)if e.get('label')=='w reverse3 completed Jb reader')
 del wrong[at]
 need(qc.replay(wrong,8,16)!=qc.replay(events,8,16),'omitted final extraction public reader rejected')
 return {'status':'PASS_COMPLETE_J_JOINT_CALLER_ALL_COLUMNS_ALL_F','scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
         'fixtures':fixtures,'selected_native_lowering_included':lower,
         'negative_controls':['Omitted t0-T restoration reader rejected.','Omitted final extraction Jb_q reader rejected.'],
         'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}for p in('joint_algebra.py','joint_prefix.py','JOINT-PREFIX.json')],
         'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'no_new_kappa':True}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--no-lowering',action='store_true');a=p.parse_args()
 out=json.loads(json.dumps(produce(not a.no_lowering)));path=HERE/('JOINT-COMPLETE-RANK-ONLY.json'if a.no_lowering else'JOINT-COMPLETE.json')
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(path.read_text())==out,'saved complete joint caller differs')
 print(out['status'],'selected_native',out['selected_native_lowering_included'])
if __name__=='__main__':main()
