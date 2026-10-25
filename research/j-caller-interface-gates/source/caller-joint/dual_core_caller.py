#!/usr/bin/env python3
"""Changed dual source core, source-bound H/L and full literal joint callers.
Apache-2.0; substantial OpenAI Codex assistance. No saving claimed.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse,hashlib,json
from joint_algebra import *
from joint_prefix import metadata,check_literal_family,original_formula
from base_core_retraction import dual_prefix
from literal_events import inverse_events
HERE=Path(__file__).resolve().parent


def formula(q,fold):
 old=original_formula(q);n=2*q+2;m=4*q+4;J=mono(j_operator(m));Q=old['Q1'];P=old['B'][2]if fold else product(J,old['B'][2]);Du,Dv=old['Du'],old['Dv']
 K=[[Q,{}],[add(Q,scale(P,-1)),P]]
 H=[[product(Du,x)for x in K[1]],[product(Dv,x)for x in K[0]]]
 L=[[{}for j in range(n)]for i in range(2)]
 U_S=product(Du,add(J,scale(product(K[1][0],J),-1)))
 V_S=product(Dv,add(scale(J,2),scale(product(Q,J),-1)))
 for b in[0]+[2*r for r in range(1,q+1)]:L[0][b]=dict(U_S);L[1][b]=dict(V_S)
 L[0][2]=add(L[0][2],scale(product(Du,J),-1));L[1][2]=add(L[1][2],scale(product(Dv,J),-1))
 for r in range(2,q+1):L[1][2*r]=add(L[1][2*r],product(old['R'][r],J))
 M=eye(n,m)
 for i in range(n):M[i]=[J if i==j else{}for j in range(n)]
 for row,b in enumerate((1,3)):M[b]=list(L[row]);M[b][1],M[b][3]=H[row]
 return dict(matrix=M,H=H,L=L,K=K,P=P,Du=Du,Dv=Dv,Q=Q)

@lru_cache(None)
def paid_P_recipe(q,lower):
 m=4*q+4;k=2*q+1;z=Model(1,k);_,J=kernels(z);A=mul(z.N.adjoint(),J);B2=mul(z.P[1],A);P=mul(J,B2);F=z.prefix(k)
 actual=mul(F,P.adjoint(),F.adjoint());g=prefix(m,k)@(j_operator(m)@(plane_swap(m,0,2)@(n_pair(m,0).inv()@j_operator(m)))).inv()@prefix(m,k).inv()
 rank=qc.rank(g.polar());pool={}
 for inv in(False,True):
  name='dual-P-recovery'+('inv'if inv else'');op=actual.adjoint()if inv else actual
  p={'native_rank':rank,'one_coordinate_definition_circuit':op.circuit,'one_coordinate_tableau':[list(t)for t in op.tab],'phase_exponent':1 if inv else-1}
  if lower:
   rec,compiled=ce.lower_child(op);same(compiled,op,'dual core selected P recovery phase');need(rec['rank']==rank,'dual native P recovery rank');p['selected_native_recipe']=rec
  pool[name]=p
 e={'kind':'NATIVE','x_monomial':g.data(),'rank_per_f':rank,'native_family':{'kind':'dual-tail','inverse':False},'native_recipe_id':'dual-P-recovery','recipe_embedding':list(range(m)),
    'phase_exponent':-1,'one_coordinate_literal_circuit':actual.circuit,'one_coordinate_tableau':[list(t)for t in actual.tab]}
 check_literal_family(e,m);return e,pool


def fixture(q,fold,lower):
 W,E=dual_prefix(q,fold);n,m=W.n,W.m;k=2*q+1;M=qc.replay(E,n,m);Mi=qc.replay(inverse_events(E,m),n,m);F=prefix(m,k);J=j_operator(m);fo=formula(q,fold)
 ret=[[product(mono(F.inv()),x)for x in row]for row in M]
 need(ret==fo['matrix'],'source-bound dual core H/L on every original field')
 need(mm(M,Mi)==mm(Mi,M)==eye(n,m),'dual prefix literal inverse both orders')
 need(all(M[i]==W.M[i]for i in range(n)if i not in(1,3)),'dual prefix complete public original inputs')
 source=json.loads((HERE/'JOINT-COMPLETE.json').read_text());old=next(f for f in source['fixtures']if f['q']==q);pool=dict(old['native_recipe_pool'])
 if not lower:
  pool={key:{k:v for k,v in p.items()if k!='selected_native_recipe'}for key,p in pool.items()}
 tail=[]
 def a(d,s,c,label):
  if c:tail.append({'kind':'ADD','dst':d,'src':s,'coefficient':str(c),'label':label})
 def u(bank,label,key):
  src=next(e for e in old['events']if e.get('native_recipe_id')==key);tail.append(dict(src,bank=bank,label=label))
 def neg(bank,label):tail.append({'kind':'SCALE','bank':bank,'coefficient':'-1','label':label})
 def swap(i,j,label):tail.append({'kind':'BANK_SWAP','banks':[i,j],'label':label})
 # These source-pinned original-tail events implement the unchanged suffix
 # current readers and U factory, with actual source circuits and adapters.
 at=next(i for i,e in enumerate(old['events'])if e['label']=='joint U coordinate recovery')
 tail.extend(old['events'][:at+1])
 for b in(0,2,*[2*r for r in range(2,q+1)]):
  a(3,b,-2,'dual p shared T reader');a(1,b,-1,'dual q shared T reader')
 a(3,2,1,'dual p b1 reader');a(1,2,1,'dual q b1 reader')
 # p=Krow1(t-T,k), q=Krow2(t-T,k); K is scalar-triangular.
 a(1,3,-1,'dual remove shared Q tbar')
 if fold:u(1,'dual B2 recovery','tail-B2-recovery')
 else:
  event,extra=paid_P_recipe(q,lower);tail.append(dict(event,bank=1,label='dual continued P recovery'));pool.update(extra)
 u(3,'dual Q1 recovery','tail-Q1-recovery');a(1,3,1,'dual restore k from k-tbar')
 for b in(0,2,*[2*r for r in range(2,q+1)]):a(3,b,1,'dual restore t from tbar')
 u(3,'dual original t full FJ','tail-J');u(1,'dual original k full FJ','tail-J');swap(1,3,'dual restore original output slots')
 full=E+tail;G=mono(F@J);expected=[[G if i==j else{}for j in range(n)]for i in range(n)]
 actual=qc.replay(full,n,m);inverse=inverse_events(full,m);actuali=qc.replay(inverse,n,m)
 need(actual==expected,'complete dual caller all original independent inputs')
 need(mm(actual,actuali)==mm(actuali,actual)==eye(n,m),'complete dual caller literal inverse both orders')
 hist=Counter(e['rank_per_f']for e in full if e['kind']=='NATIVE');phist=Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE')
 C=product(G,Mi[1][3]);need(len(C)==1 and qc.rank(next(iter(C)).polar())==2*q,'changed original-t/current-V inverse arity2qf')
 return{'q':q,'name':'folded-dual'if fold else'paid-dual','banks':n,'width':n,'ambient_arity':m,'prefix_events':E,'tail_events':tail,'events':full,'full_events':full,'inverse_events':inverse,
        'physical_prefix_matrix':sm(M),'physical_prefix_inverse':sm(Mi),'retarded_H':sm(fo['H']),'retarded_L':sm(fo['L']),'core_Knew':sm(fo['K']),'P2tilde':serial(fo['P']),
        'original_t_current_V_correction':serial(C),'original_t_current_V_arity_per_f':2*q,'original_t_current_U_correction':serial(product(G,Mi[1][1])),
        'prefix_histogram':dict(phist),'prefix_D':n*m-sum(r*c for r,c in phist.items()),'histogram':dict(hist),'native_mass':sum(r*c for r,c in hist.items()),'stock':n*m,
        'native_recipe_pool':pool,'all_original_columns':n,'literal_inverse_orders':2,'selected_native_lowerings':lower,
        'source_choice':'stage2 w=(0,1), r=(-1,1); source normalized exactly. First/third choices and all suffix stages unchanged.',
        'reader_identity':'p=w2+Jb1-2T, q=Du^-1U+Jb1-T equal Knew(t0-T,k0), T=sum completed J(a,b).',
        'limits':['No positive native deficit claimed.','Paid-dual has one extra early J; folded-dual retimes only its single J-valued postfanout through the next source query.','Retirement of original owners is not inferred from this coupled core.']}

def produce(lower):
 cases=[fixture(q,fold,lower)for q in(2,3)for fold in(False,True)]
 return{'status':'PASS_CHANGED_DUAL_CORE_COMPLETE_CALLERS_ALL_ORIGINAL_COLUMNS_ALL_F','fixtures':cases,
        'all_parameter_HL':'H=diag(Du,Dv) Swap Knew; Knew=[[Q1,0],[Q1-P2tilde,P2tilde]], P2tilde=JB2 (paid) orB2(folded). Common suffix readers obey unchanged current-reader recurrence.',
        'source_pins':[{'path':str(HERE/p),'sha256':hashlib.sha256((HERE/p).read_bytes()).hexdigest()}for p in('joint_algebra.py','joint_prefix.py','base_core_retraction.py','literal_events.py','JOINT-COMPLETE.json')],
        'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'no_new_kappa':True}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--no-lowering',action='store_true');a=p.parse_args();out=json.loads(json.dumps(produce(not a.no_lowering)));path=HERE/('DUAL-CORE-RANK-ONLY.json'if a.no_lowering else'DUAL-CORE.json')
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(path.read_text())==out,'saved dual-core caller differs')
 print(out['status'])
if __name__=='__main__':main()
