#!/usr/bin/env python3
"""Exact early cut58 block and a scan-simplifying, rank-neutral identity.
Apache-2.0; substantial OpenAI Codex assistance. Planning only; no new kappa.
"""
from pathlib import Path
from collections import Counter
import argparse,copy,hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent
PIN='30d3f569d91304856118796f0c586176d0ad961eff70b09c78fce7532392101f'
needpath=R/'two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json'
if hashlib.sha256(needpath.read_bytes()).hexdigest()!=PIN:raise ValueError('admitted frozen source pin')
sys.path.insert(0,str(R/'coupled-tail-escape'))
import local_block as late
from joint_algebra import *
from validate_recipe_links import compile_literal,compile_recipe,embedding_circuit

def produce():
 f=next(f for f in json.loads(needpath.read_text())['fixtures']if f['q']==2)
 old=next(f for f in json.loads((R/'folded-fusion/SIMPLIFIED-FUSIONS.json').read_text())['fixtures']if f['q']==2)
 n,m,cut=6,12,58;E=copy.deepcopy(f['events'][cut:]);Ei=copy.deepcopy(f['inverse_events'][:len(E)]);pool={}
 need(E[0]['label']=='query5 source J','actual entrance is source query5, no virtual read')
 for events in(E,Ei):
  for e in events:
   if e['kind']in('ADD','SCALE','BANK_SWAP'):continue
   src=old['events'][e['source_event_ordinal']];g=qc.decode(src,m);op=compile_literal(src['one_coordinate_literal_circuit'],m)
   ep=tuple(src['phase_exponent']*(1-r)%4 for r in range(4))
   if e['source_operator_is_adjoint']:g=g.inv();op=op.adjoint();ep=tuple(-x%4 for x in ep)
   e['x_monomial']=g.data();actual=compile_literal(e['one_coordinate_literal_circuit'],m)
   same(actual,op,'cut58 source literal signed operator and Gaussian phase')
   need(late.extra(e)==ep,'cut58 all-f global phase correction')
   if e['kind']=='NATIVE':
    rec=f['native_recipe_pool'][e['native_recipe_id']];d=len(rec['one_coordinate_tableau'])//2
    selected=compile_recipe(rec['selected_native_recipe'],d)
    full=compile_literal(embedding_circuit(selected.circuit,e['recipe_embedding'],m),m)
    same(full,actual,'every cut58 forward/inverse selected recipe and embedding')
    need(tuple(rec['extra_global_phase_exponent_by_f_mod4'])==ep,'cut58 selected recipe scalar family')
    pool[e['native_recipe_id']]=rec
 M=qc.replay(E,n,m);Mi=qc.replay(Ei,n,m)
 need(mm(M,Mi)==mm(Mi,M)==eye(n,m),'all6 arbitrary current inputs, both literal inverse orders')
 get=lambda label:qc.decode(next(e for e in E if e['label']==label),m)
 K=get('query5 source J');A=get('final independent a J query');W=get('dual Q1 recovery');T=n_pair(m,5);P=get('query5 source swap')
 RR=qc.identity(m)
 for e in E:
  if e['label']in('w reverse2 ADDRESS','w reverse2 selected native2','final extraction D_final inverse sign'):RR=qc.decode(e,m)@RR
 I=mono(qc.identity(m));minus=qc.Mono(qc.identity(m).rows,0,(0,)*m,(0,)*m,0,2)
 need(mono(K)==mono(A),'early source response equals later independent-a response')
 need(mono(RR@P)==mono(minus@T),'reverse-current reader times source ADDRESS = -freshT')
 for g in(K,W):need(mono(g@T)==mono(T@g),'old-support operator commutes actual freshT')
 IW=add(I,scale(mono(W),-1));X=[[{}for _ in range(n)]for _ in range(n)]
 X[0][0]=mono(K@T)
 X[1][0]=scale(mono(W@K@T),-1);X[1][2]=product(IW,mono(T));X[1][3]=scale(mono(T),-1);X[1][4]=scale(mono(W@T@K),-1)
 X[2][0]=scale(mono(K@T),-1);X[2][2]=mono(T);X[2][3]=scale(mono(T),-1);X[2][4]=scale(mono(T@K),-1)
 X[3][0]=scale(mono(K@W@K@T),-1);X[3][1]=mono(K@T);X[3][2]=product(mono(K),product(IW,mono(T)));X[3][4]=scale(mono(K@W@T@K),-1)
 X[4][4]=mono(T@K);X[5][5]=mono(T)
 need(M==X,'complete displayed six-by-six early-block target')
 # A constructive identity with the same native bill: eliminate P and R
 # together, transport one common T across the old-support K/W operators.
 w=Word(n,m);w.unary(4,K,'sourceK',True);w.add(3,4,1,'delivery');w.add(2,3,-1,'b accumulator')
 for bank in range(n):w.unary(bank,T,'freshT',True)
 w.unary(0,K,'aK',True);w.add(2,0,-1,'isolate b');
 # SCALE is an actual full-field scan, never a free query or a discarded dirt.
 w.M[3]=[scale(x,-1)for x in w.M[3]]
 for row in w.Mi:row[3]=scale(row[3],-1)
 w.events.append(dict(kind='SCALE',bank=3,coefficient='-1',label='RP=-T sign'))
 w.add(3,4,1,'completed source reader')
 # Copy only the final scalar/core segment, identified by its unique label.
 start=next(i for i,e in enumerate(E)if e['label']=='dual p shared T reader')
 for e in E[start:]:
  if e['kind']=='ADD':w.add(e['dst'],e['src'],F(e['coefficient']),e['label'])
  elif e['kind']=='BANK_SWAP':w.swap(*e['banks'],label=e['label'])
  else:w.unary(e['bank'],qc.decode(e,m),e['label'],e['kind']=='NATIVE')
 need(w.M==M and mm(w.M,w.Mi)==mm(w.Mi,w.M)==eye(n,m),'rank-neutral simplified network complete equality and inverse')
 native=lambda ev:Counter(e['rank_per_f']for e in ev if e['kind']=='NATIVE')
 prefixmass=sum(e['rank_per_f']for e in f['events'][:cut]if e['kind']=='NATIVE');hist=native(E)
 need(prefixmass==54 and sum(r*c for r,c in hist.items())==22 and f['native_mass']==76,'exact original prefix54 suffix22 bill')
 need(sum(r*c for r,c in native(w.events).items())==22,'simplified network fully charged at22')
 no_reader=[e for e in E if e['label']!='odd b accumulator']
 need(qc.replay(no_reader,n,m)!=M,'omitting actual arbitrary-source accumulator is rejected')
 no_sign=copy.deepcopy(X);no_sign[1][3]=mono(T)
 need(no_sign!=M,'losing RP minus sign changes arbitrary input3')
 return dict(status='PASS_EXACT_EARLY_CUT58_BLOCK_PLANNING_ONLY',no_new_kappa=True,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  source_sha256=PIN,source_path=str(needpath),q=2,banks=n,ambient_arity=m,cut_event_ordinal=cut,cut_label=E[0]['label'],prefix_native_mass=54,suffix_native_mass=22,complete_mass=76,stock=72,
  hypothetical_target_suffix_mass=16,hypothetical_complete_mass=70,target_is_not_achieved=True,
  events=E,inverse_events=Ei,native_recipe_pool=pool,complete_local_matrix=sm(M),complete_local_inverse=sm(Mi),
  operators=dict(T=T.data(),K=K.data(),W=W.data(),P=P.data(),reverse_current=RR.data()),
  simplified_rank_neutral_events=w.events,simplified_native_histogram=dict(native(w.events)),original_native_histogram=dict(hist),
  proof_scope='Exact finite q2 physical suffix on all6 independent arbitrary current banks, both inverse orders, exact all-f phase residues. The reduced scalar network is proved equal but is not separately selected-native-admitted.',
  useful_identity='R*P=-T with actual minus phase; K=A and [K,T]=[W,T]=0. Source warp and reverse reader can be removed jointly, replacing them by one charged T and scalar sign. Native bill remains22.',
  remaining_gap='A coupled replacement must lower22 to<=16 with the full displayed matrix unchanged. No such factorization or lower bound ruling it out is established. Entries alone only reach rank6 and do not exclude16.',
  negative_controls=['Omitting odd source b-accumulator changes arbitrary-input matrix.','Replacing RP=-T by +T changes input3 column.'],
  limits=['No broad enumeration or frame optimization.','No clean/correlated input promise or free copy/zero helper.','Same-volume full-bank arities only; partial/striped query costs need weighted accounting.','The neutral rewrite still pays three K rank2, six T rank2 and one W rank4 queries, plus every ADD/SCALE/SWAP scan.','No positive moment, BIT compatibility, owner/controller/precision/storage or kappa claim.'])

def main():
 a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');args=a.parse_args();x=json.loads(json.dumps(produce()));p=HERE/'CUT58.json'
 if args.write:p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(p.read_text())==x,'saved early-cut58 receipt')
 print(x['status'],'prefix54 suffix22; neutral rewrite22; target<=16 OPEN')
if __name__=='__main__':main()
