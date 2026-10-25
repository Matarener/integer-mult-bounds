#!/usr/bin/env python3
"""A changed dense scalar continuation and complete physical q3 caller.
Apache-2.0; substantial OpenAI Codex assistance. No saving claimed.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse,hashlib,json
from joint_algebra import *
from joint_prefix import build as ordinary_prefix,metadata,native_pool,check_literal_family
from delivery_core_probe import inverse_events
HERE=Path(__file__).resolve().parent

def ae(d,s,c,label):return {'kind':'ADD','dst':d,'src':s,'coefficient':str(c),'label':label}
def se(b,c,label):return {'kind':'SCALE','bank':b,'coefficient':str(c),'label':label}
def bridge(name,banks=(1,4)):
 u,v=banks;label='changed scalar pair-exit '+name
 if name=='upper':return[ae(u,v,1,label)]
 if name=='lower':return[ae(v,u,1,label)]
 if name=='balanced':return[ae(u,v,1,label),se(v,-2,label),ae(v,u,1,label)]
 raise ValueError(name)

def build(name):
 P=ordinary_prefix(3);pos=next(i for i,e in enumerate(P.events)if e['label']=='diagonal continuation retain V in b accumulator')
 metadata(P.events,3);events=P.events[:pos]+bridge(name)+P.events[pos:]
 M=qc.replay(events,8,16);Mi=qc.replay(inverse_events(events,16),8,16)
 need(mm(M,Mi)==mm(Mi,M)==eye(8,16),'dense continuation all-column literal inverse')
 need(all(M[i]==P.M[i]for i in(0,2,4,5,6,7)),'every independent public column survives changed scalar carrier continuation')
 return events,M,Mi

@lru_cache(None)
def complete_native_queries(lower):
 q,k,m=3,7,16;z=Model(1,k);_,Jc=kernels(z);Fc=z.prefix(k)
 F=prefix(m,k);J=j_operator(m);A=n_pair(m,0).inv()@J;Ac=mul(z.N.adjoint(),Jc)
 B={s:plane_swap(m,0,s)@A for s in range(1,k+1)};Bc={s:mul(z.P[s-1],Ac)for s in range(1,k+1)}
 Du=B[4]@B[3]@J;Duc=mul(Bc[4],Bc[3],Jc);Q1=J.inv()@B[1]@J;Q1c=mul(Jc.adjoint(),Bc[1],Jc)
 entries={};pool=native_pool()
 for name,g,op,exp in(('B6inverse',B[6].inv(),Bc[6].adjoint(),0),('base-Duinverse',Du.inv(),Duc.adjoint(),-1),('B2inverse',B[2].inv(),Bc[2].adjoint(),0),('Q1inverse',Q1.inv(),Q1c.adjoint(),0),('Jexit',J,Jc,1)):
  physical=F@g@F.inv();actual=mul(Fc,op,Fc.adjoint());rank=qc.rank(physical.polar())
  need(ce.rank(x for x,y,p in actual.tab[m:])==rank,'independent native B rank')
  entry={'kind':'NATIVE','x_monomial':physical.data(),'rank_per_f':rank,'native_family':{'kind':'mixed-tail','inverse':False},'native_recipe_id':name,
         'recipe_embedding':list(range(m)),'phase_exponent':exp,'one_coordinate_literal_circuit':actual.circuit,'one_coordinate_tableau':[list(t)for t in actual.tab]}
  check_literal_family(entry,m);entries[name]=entry
  for inv in(False,True):
   key=name+('inv'if inv else'');literal=actual.adjoint()if inv else actual
   p={'native_rank':rank,'one_coordinate_definition_circuit':literal.circuit,'one_coordinate_tableau':[list(t)for t in literal.tab],'phase_exponent':-exp if inv else exp}
   if lower:
    rec,compiled=ce.lower_child(literal);same(compiled,literal,'mixed continuation selected-native actual phase');need(rec['rank']==rank,'native selected child rank');p['selected_native_recipe']=rec
   pool[key]=p
 return entries,pool

def tail_events(name,lower):
 entries,pool=complete_native_queries(lower);out=[];m=16
 def A(d,s,c,label):out.append(ae(d,s,c,label))
 def swap(a,b,label):out.append({'kind':'BANK_SWAP','banks':[a,b],'label':label})
 def U(bank,key,label):out.append(dict(entries[key],bank=bank,label=label))
 def neg(b,label):out.append(se(b,-1,label))
 def address(b,plane,label):
  e={'kind':'ADDRESS_OR_UNIT','bank':b,'x_monomial':plane_swap(m,0,plane).data(),'rank_per_f':0,'native_family':None,'label':label};metadata([e],3);out.append(e)
 def native(b,plane,label):
  e={'kind':'NATIVE','bank':b,'x_monomial':n_pair(m,plane).data(),'rank_per_f':2,'native_family':{'kind':'N','plane':plane,'inverse':False},'label':label};metadata([e],3);out.append(e)
 # Undo final response pair to the *changed* middle coordinates u2,v0.
 U(1,'B6inverse','undo final even factory')
 address(3,7,'final current-reader ADDRESS');native(3,7,'final current-reader native2');neg(3,'final D7 inverse sign')
 A(3,6,1,'final completed Jb3 reader');neg(3,'recover changed middle v0=-w3')
 out.extend(inverse_events(bridge(name,(1,3)),m))
 # This is precisely the ordinary q2 endpoint in the larger F7 chart.
 address(3,5,'middle current-reader ADDRESS');native(3,5,'middle current-reader native2');neg(3,'middle D5 inverse sign');A(3,4,1,'middle completed Jb2 reader')
 U(1,'base-Duinverse','base U coordinate recovery')
 A(3,2,1,'p original b1 reader');A(1,2,1,'q original b1 reader')
 publics=(0,2,4,6)
 for b in publics:A(3,b,-2,'p scalar T reader');A(1,b,-1,'q scalar T reader')
 neg(3,'K inverse sign');swap(3,1,'K inverse swap');A(1,3,1,'K inverse scalar sum');U(1,'B2inverse','K inverse B2 query');A(3,1,-1,'K inverse difference');U(3,'Q1inverse','K inverse Q1 query');A(1,3,1,'K inverse sum')
 for b in publics:A(3,b,1,'restore original t0 reader')
 U(3,'Jexit','original t0 full F7J');U(1,'Jexit','original k0 full F7J');swap(1,3,'original output slots')
 return out,pool

def fixture(name,lower):
 events,M,Mi=build(name);tail,pool=tail_events(name,lower);full=events+tail;n,m=8,16
 actual=qc.replay(full,n,m);inverse=qc.replay(inverse_events(full,m),n,m);I=eye(n,m);G=mono(prefix(m,7)@j_operator(m));expected=[[G if i==j else{}for j in range(n)]for i in range(n)]
 need(actual==expected,'changed scalar continuation complete all original inputs actual F7J')
 need(mm(actual,inverse)==mm(inverse,actual)==I,'complete both literal inverse orders')
 C=product(G,Mi[1][3]);hist=Counter(e['rank_per_f']for e in full if e['kind']=='NATIVE')
 return {'name':name,'q':3,'banks':n,'width':n,'ambient_arity':m,'prefix_events':events,'tail_events':tail,'events':full,'full_events':full,'inverse_events':inverse_events(full,m),
         'physical_prefix_matrix':sm(M),'physical_prefix_inverse':sm(Mi),'original_t_current_V_correction':serial(C),'original_t_current_V_ray_arities_per_f':[qc.rank(g.polar())for g in C],
         'native_recipe_pool':pool,'histogram':dict(hist),'native_mass':sum(r*c for r,c in hist.items()),'stock':128,
         'all_original_columns':8,'literal_inverse_orders':2,'extra_free_bridge':bridge(name),'selected_native_lowerings':lower,
         'scope':'Finite q3 exact all-f changed scalar GL2 continuation; complete conservative word, not a saving.'}

def produce(lower):
 fixtures=[fixture(name,lower)for name in('upper','lower','balanced')]
 mutant=list(fixtures[2]['events']);at=next(i for i,e in enumerate(mutant)if e['kind']=='SCALE'and e['coefficient']=='-1/2');del mutant[at]
 need(qc.replay(mutant,8,16)!=qc.replay(fixtures[2]['events'],8,16),'balanced bridge inverse scaling is necessary')
 return{'status':'PASS_DENSE_SCALAR_CONTINUATION_COMPLETE_Q3_ALL_F','fixtures':fixtures,'negative_controls':['Omitting inverse-balanced scaling changes original columns.'],
        'all_parameter_interface':'Before the retained diagonal handoff, set (Unew,Vnew)=L(U,V) by a literal rational scalar GL2 bridge. Then nextu=Unew,nextv=-Vnew-JA, with all public columns unchanged.',
        'complete_tail_equation':'Undo final B6 and D7; apply inverse L to (u2,-w3); then ordinary q2 H/L inverse in F7 chart. Only unitary operator inverses and reversible scalar operations are used.',
        'limits':['No general GL2 obstruction or improved native bill.','Constituent Clifford arity is not by itself the native cost of a sum.','Whole-word retiming may cross these stated cuts.'],
        'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}for p in('joint_algebra.py','joint_prefix.py','delivery_core_probe.py')],
        'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'no_new_kappa':True}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--no-lowering',action='store_true');a=p.parse_args();out=json.loads(json.dumps(produce(not a.no_lowering)));path=HERE/('MIXED-CONTINUATION-RANK-ONLY.json'if a.no_lowering else'MIXED-CONTINUATION.json')
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(path.read_text())==out,'saved mixed continuation differs')
 print(out['status'])
if __name__=='__main__':main()
