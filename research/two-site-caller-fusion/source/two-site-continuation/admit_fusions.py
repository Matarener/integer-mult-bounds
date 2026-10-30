#!/usr/bin/env python3
"""Current used-only native recipes and serialized literal inverse admission.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,copy
from isolated_fusion import *
from continue_isolated import apply_events
from validate_recipe_links import compile_literal,compile_recipe,embedding_circuit
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'inputs/REPAIRED-SIMPLIFIED-FUSIONS.json'
SOURCE_SHA='4491cfe2a1f3e48510b33403b9b50c704865c3b1dc6d659ef5157840654e8fc3'
MANIFEST=HERE/'inputs/REPAIRED-MANIFEST.json'
MANIFEST_SHA='dde942457256b0f037a65eebeb5df822fe4d8911c0441657816c77a4c20c6f1c'

def toggle(key):return key[:-3]if key.endswith('inv')else key+'inv'
def native_record(p,extra):
 return{'selected_native_recipe':p['selected_native_recipe'],
        'one_coordinate_definition_circuit':p.get('one_coordinate_definition_circuit',p.get('one_coordinate_literal_circuit')),
        'one_coordinate_tableau':p['one_coordinate_tableau'],'extra_global_phase_exponent_by_f_mod4':extra}
def inverse_current(events,m):
 out=[]
 for original in reversed(events):
  e=copy.deepcopy(original);kind=e['kind']
  if kind=='ADD':e['coefficient']=str(-F(e['coefficient']))
  elif kind=='SCALE':e['coefficient']=str(1/F(e['coefficient']))
  elif kind!='BANK_SWAP':
   op=compile_literal(e['one_coordinate_literal_circuit'],m).adjoint();e['one_coordinate_literal_circuit']=op.circuit;e['one_coordinate_tableau']=[list(t)for t in op.tab]
   e['extra_global_phase_exponent_by_f_mod4']=[(-p)%4 for p in e['extra_global_phase_exponent_by_f_mod4']]
   if kind=='NATIVE':e['native_recipe_id']=toggle(e['native_recipe_id'])
   e['source_operator_is_adjoint']=not e.get('source_operator_is_adjoint',False)
  out.append(e)
 return out

def check_native_event(e,pool,m,cache):
 need('x_monomial'not in e and'native_family'not in e and'phase_exponent'not in e,'current literal event has no stale operator/family/phase shadows')
 actual=compile_literal(e['one_coordinate_literal_circuit'],m)
 need(actual.tab==tuple(tuple(t)for t in e['one_coordinate_tableau']),'literal event independently reconstructed signed tableau')
 rank=ce.rank(x for x,y,p in actual.tab[m:]);need(rank==e['rank_per_f'],'actual current event native arity')
 if e['kind']=='NATIVE':
  key=e['native_recipe_id'];need(key in pool,'current native pointer exists '+key);p=pool[key]
  need(e['extra_global_phase_exponent_by_f_mod4']==p['extra_global_phase_exponent_by_f_mod4'],'current native pointer has exact all-f phase vector '+key)
  if key not in cache:
   dim=len(p['one_coordinate_tableau'])//2;op=compile_literal(p['one_coordinate_definition_circuit'],dim)
   need(op.tab==tuple(tuple(t)for t in p['one_coordinate_tableau']),'used pool definition independently reconstructed tableau '+key)
   rec=compile_recipe(p['selected_native_recipe'],dim);same(rec,op,'used selected recipe actual Gaussian phase '+key);cache[key]=rec
  selected=compile_literal(embedding_circuit(cache[key].circuit,e['recipe_embedding'],m),m)
  same(selected,actual,'actual native event equals complete embedded selected recipe '+key)
  need(p['selected_native_recipe']['rank']==rank,'selected child arity agrees '+key)
  cap=int(((m*m-1)//2)**0.5)
  need(rank<=cap and rank<m,'every actual child strictly contracts at the pinned ambient arity')
 else:need(rank==0,'declared free literal event is actually monomial')

def bind(q,sources):
 science_path=HERE/('ISOLATED-FUSION-Q'+str(q)+'.json');f=json.loads(science_path.read_text());s=next(x for x in sources['fixtures']if x['q']==q)
 event_input=next(x for x in json.loads((HERE/'INPUT-EVENTS.json').read_text())['fixtures']if x['q']==q);keys=('kind','bank','banks','dst','src','coefficient','x_monomial','rank_per_f','label')
 strip=lambda E:[{k:e[k]for k in keys if k in e}for e in E]
 need(strip(s['prefix_events'])==event_input['prefix_events']and strip(s['tail_events'])==event_input['tail_events'],'repaired selected source has exactly the frozen mathematical event input')
 m,n=f['ambient_arity'],f['banks'];oldP,oldT=s['prefix_events'],s['tail_events'];kept=[j for j in range(len(oldT))if j not in f['removed_tail_sites']]
 source_index=list(range(len(oldP)))+[len(oldP)+j for j in kept];oldE=oldP+oldT;events=[];pool={}
 for at,e in enumerate(f['events']):
  kind=e['kind']
  if kind in('ADD','SCALE','BANK_SWAP'):
   events.append({k:e[k]for k in('kind','dst','src','coefficient','bank','banks','label')if k in e});continue
  op=compile_literal(e['one_coordinate_literal_circuit'],m);need(op.tab==tuple(tuple(t)for t in e['one_coordinate_tableau']),'scientific replacement literal tableau')
  d={'kind':kind,'bank':e['bank'],'label':e['label'],'rank_per_f':e['rank_per_f'],'one_coordinate_literal_circuit':op.circuit,
     'one_coordinate_tableau':[list(t)for t in op.tab],'extra_global_phase_exponent_by_f_mod4':e['extra_global_phase_exponent_by_f_mod4'],
     'source_fixture_q':q,'source_event_ordinal':source_index[at],'source_operator_is_adjoint':False}
  if kind=='NATIVE':
   if at in f['sites']:
    need(e.get('native_recipe_id')=='two-site-later','new native site has current selected recipe')
    key='changed-later'
    for inv in(False,True):
     p=f['new_native_recipe_pool']['two-site-later'+('inv'if inv else'')];pool[key+('inv'if inv else'')]=native_record(p,p['extra_global_phase_exponent_by_f_mod4'])
    d['native_recipe_id']=key;d['recipe_embedding']=list(range(m))
   else:
    inherited=oldE[source_index[at]];need(inherited['kind']=='NATIVE','unchanged native event corresponds to its current selected source')
    actual=compile_literal(inherited['one_coordinate_literal_circuit'],m);same(op,actual,'unchanged actual source selected native physical phase')
    need(d['extra_global_phase_exponent_by_f_mod4']==[(inherited['phase_exponent']*(1-r))%4 for r in range(4)],'unchanged actual source all-f phase')
    oldkey=inherited['native_recipe_id'];base=oldkey[:-3]if oldkey.endswith('inv')else oldkey
    for name in(base,base+'inv'):
     p=s['native_recipe_pool'][name];pool['inherited-'+name]=native_record(p,[(p['phase_exponent']*(1-r))%4 for r in range(4)])
    d['native_recipe_id']='inherited-'+oldkey;d['recipe_embedding']=inherited['recipe_embedding']
  events.append(d)
 inv=inverse_current(events,m);used={e['native_recipe_id']for e in events+inv if e['kind']=='NATIVE'};pool={k:pool[k]for k in sorted(used)}
 cache={};checked=0
 for e in events+inv:
  if e['kind']not in('ADD','SCALE','BANK_SWAP'):check_native_event(e,pool,m,cache);checked+=1
 need(set(cache)==set(pool),'pool contains exactly used forward and inverse native definitions')
 A=Algebra(2*q+1);M,Mi=apply_events(events,n,A);Iactual,Ii=apply_events(inv,n,A)
 need(Iactual==Mi and Ii==M,'serialized inverse itself independently replays to the exact inverse matrix')
 need(A.mat_product(M,Iactual)==A.mat_product(Iactual,M)==A.mat_identity(n),'serialized full forward and inverse in both orders, every original field')
 target=A.mat_identity(n);g=prefix(m,2*q+1)@j_operator(m);Gout=A.lift(xop(g),exponent=g.global_phase)
 for b in range(n):target[b][b]=Gout
 need(M==target,'current serialized physical word equals diag(F_k J) on every original independent owner, all f')
 hist=Counter(e['rank_per_f']for e in events if e['kind']=='NATIVE');need(sum(r*c for r,c in hist.items())==f['complete_native_mass'],'current complete histogram from actual events')
 # A valid pointer with the wrong direction is rejected even though the
 # literal reversed circuit has not changed.
 bad=next(copy.deepcopy(e)for e in inv if e['kind']=='NATIVE');bad['native_recipe_id']=toggle(bad['native_recipe_id'])
 try:check_native_event(bad,pool,m,{})
 except ValueError:pass
 else:raise ValueError('wrong-direction inverse pointer mutant not rejected')
 # Preserve f1 and alter f2 only: this catches a tensor-lift phase omission.
 bad=copy.deepcopy(inv);at=next(i for i,e in enumerate(bad)if e['kind']=='NATIVE');bad[at]['extra_global_phase_exponent_by_f_mod4'][2]^=2
 try:check_native_event(bad[at],pool,m,{})
 except ValueError:pass
 else:raise ValueError('f2-only scalar phase mutant not rejected')
 omitted=[e for i,e in enumerate(events)if i!=f['sites'][0]];wrong,_=apply_events(omitted,n,A);need(wrong!=target,'omitting changed free monomial alters original-input columns')
 return{'q':q,'name':'two-site-physical-monomial-continuation','banks':n,'width':n,'ambient_arity':m,'events':events,'full_events':events,
        'prefix_events':events[:len(oldP)],'tail_events':events[len(oldP):],'inverse_events':inv,'native_recipe_pool':pool,'histogram':dict(hist),
        'native_mass':f['complete_native_mass'],'stock':f['stock'],'D':f['D'],'changed_sites':f['sites'],'changed_native_ranks':f['new_site_ranks_per_f'],
        'all_original_columns':n,'literal_inverse_orders':2,'every_serialized_unary_checked':checked,'used_only_native_definitions':len(pool),
        'source_scientific_receipt':{'path':str(science_path),'sha256':hashlib.sha256(science_path.read_bytes()).hexdigest()},
        'proof':'Complete actual literal forward and serialized inverse, every selected recipe embedding, all-f phase vectors, original owner labels and diag(F_k J) target are checked. General-Clifford tensor algebra covers every positive f, not a finite-f extrapolation.',
        'limits':['Finite q as listed. No all-q family is inferred.','Native mass remains four units above stock, so no kappa improvement is claimed.','Complete-field ADD/monomial/scalar scans remain paid outer costs; exact events are retained.']}

def produce():
 need(hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA,'frozen repaired source artifact pin');need(hashlib.sha256(MANIFEST.read_bytes()).hexdigest()==MANIFEST_SHA,'frozen repaired source manifest pin')
 sources=json.loads(SOURCE.read_text());fixtures=[bind(q,sources)for q in(2,3)]
 return{'status':'PASS_COMPLETE_TWO_SITE_FUSIONS_SELECTED_NATIVE_SERIALIZED_INVERSES_ALL_F','schema':'current-literal-tensor-family-events-v1','fixtures':fixtures,
     'source_repaired_artifact_sha256':SOURCE_SHA,'source_repaired_manifest_sha256':MANIFEST_SHA,
     'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}for p in('INPUT-EVENTS.json','isolated_fusion.py','continue_isolated.py')],
     'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     'negative_controls':['Opposite-direction native pointer rejects while keeping the literal inverse circuit unchanged.','f2-only Gaussian-unit change rejects while f1 is unchanged.','Omitting the first changed free monomial changes original-input columns.'],
     'no_new_kappa':True}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(produce()));path=HERE/'ADMITTED-TWO-SITE-FUSIONS.json'
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(path.read_text())==out,'saved current admitted words differ')
 print(out['status'],[(f['q'],f['native_mass'],f['stock'])for f in out['fixtures']],flush=True)
if __name__=='__main__':main()
