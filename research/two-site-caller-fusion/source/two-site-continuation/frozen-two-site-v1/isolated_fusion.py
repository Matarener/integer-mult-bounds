#!/usr/bin/env python3
"""Exact two-site physical monomial/Bruhat fusion, all-f full columns.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import argparse,hashlib,json,sys
from two_site import *
from lifted_algebra import Algebra,G,ONE as GONE,ZERO as GZERO
from validate_recipe_links import compile_monomial,compile_recipe
HERE=Path(__file__).resolve().parent

def bphase(m,p):return ce.Op(m,ce.identity(m),[('phase',p%4)])

@lru_cache(None)
def xop(g):
 """Compile an arbitrary X-character Gaussian monomial to a physical circuit."""
 m=len(g.rows);out=ce.ident(m)
 for i,a in enumerate(g.alpha):
  if a%4==1:out=out.then(ce.cgate(m,1<<i,1))
  elif a%4==3:out=out.then(ce.cgate(m,1<<i,-1))
  elif a%4==2:out=out.then(ce.xgate(m,1<<i))
 for i,row in enumerate(g.quad):
  for j in range(i+1,m):
   if row>>j&1:
    out=out.then(ce.cgate(m,1<<i)).then(ce.cgate(m,1<<j)).then(ce.cgate(m,(1<<i)|(1<<j),-1))
 ri=qc.inverse(g.rows);rows=tuple(sum(((ri[j]>>i)&1)<<j for j in range(m))for i in range(m))
 out=out.then(ce.perm(m,rows))
 if g.offset:out=out.then(ce.diag(m,[0]*m,[2*((g.offset>>i)&1)for i in range(m)]))
 if(g.constant+g.global_phase)%4:out=out.then(bphase(m,g.constant+g.global_phase))
 return out

def family(A,E):
 need(unitary_clifford(E),'convert one actual unitary Clifford family')
 g,v=next(iter(E.items()));base=A.lift(xop(g));weights=tuple(G(v[2*r],v[2*r+1])for r in range(4))
 return{k:tuple(a*b for a,b in zip(value,weights))for k,value in base.items()}

def one_coordinate(E):
 g,v=next(iter(E.items()));c=(v[2],v[3]);units=((1,0),(0,1),(-1,0),(0,-1));need(c in units,'one-coordinate Gaussian unit')
 return xop(g).then(bphase(len(g.rows),units.index(c)))

def ring_replay(events,n,m,A,replace=None):
 M=A.mat_identity(n);Mi=A.mat_identity(n)
 for at,e in enumerate(events):
  kind=e['kind']
  if kind=='ADD':
   d,s,c=e['dst'],e['src'],F(e['coefficient']);M[d]=[A.add(x,A.scale(y,c))for x,y in zip(M[d],M[s])]
   for row in Mi:row[s]=A.add(row[s],A.scale(row[d],-c))
  elif kind=='SCALE':
   b,c=e['bank'],F(e['coefficient']);M[b]=[A.scale(x,c)for x in M[b]]
   for row in Mi:row[b]=A.scale(row[b],1/c)
  elif kind=='BANK_SWAP':
   i,j=e['banks'];M[i],M[j]=M[j],M[i]
   for row in Mi:row[i],row[j]=row[j],row[i]
  else:
   b=e['bank'];U=replace[at]if replace and at in replace else A.lift(xop(qc.decode(e,m)),exponent=qc.decode(e,m).global_phase);Ui=A.adjoint(U)
   M[b]=[A.product(U,x)for x in M[b]]
   for row in Mi:row[b]=A.product(row[b],Ui)
 return M,Mi

def family_phase(A,value,op):
 base=A.lift(op);need(len(value)==len(base)==1 and set(value)==set(base),'new unary is one fixed Clifford ray for every f')
 v,b=next(iter(value.values())),next(iter(base.values()));units=((1,0),(0,1),(-1,0),(0,-1));out=[]
 for a,c in zip(v,b):
  ratio=a/c;pair=(ratio.a,ratio.b);need(pair in units,'all-f correction is a Gaussian unit');out.append(units.index(pair))
 return out

def serial_general(A,E):
 return[{'distinguished_tableau':[list(t)for t in kd],'bulk_tableau':[list(t)for t in kb],
          'coefficients_by_f_mod4':[x.encode()for x in v]}for(kd,kb),v in E.items()]

def run(q=2,i=31,j=51):
 source=HERE/'INPUT-EVENTS.json';f=next(x for x in json.loads(source.read_text())['fixtures']if x['q']==q);n,m=f['banks'],f['ambient_arity'];P,T=f['prefix_events'],f['tail_events']
 # The removable native is the whole original U-coordinate recovery.
 removed={at for at,e in enumerate(T)if e['label']=='joint U coordinate recovery'};need(len(removed)==1,'one selected whole tail native')
 newT=[e for at,e in enumerate(T)if at not in removed];C=mm(qc.replay(inverse(newT,m),n,m),qc.replay(T,n,m))
 for at in range(len(P)-1,j,-1):C=pullback(C,P[at],m)
 Acol,Brow=pair_columns(P,i,j,n,m);b=P[j]['bank'];I=eye(n,m)
 need(not any(Acol[r]for r in range(n)if r!=b)and not any(Brow[c]for c in range(n)if c!=b),'transported bank direction is isolated in BOTH row and column')
 need(all(C[r][c]==I[r][c]for r in range(n)for c in range(n)if(r,c)!=(b,b)),'required correction is only the isolated current bank')
 need(unitary_clifford(Acol[b])and unitary_clifford(C[b][b]),'isolated transport and correction are actual unitary Clifford families')
 L=product(C[b][b],product(Acol[b],mono(qc.decode(P[i],m))));R=product(adjoint(Acol[b]),mono(qc.decode(P[j],m)))
 Lop,Rop=one_coordinate(L),one_coordinate(R);lrec,lout=ce.lower_child(Lop);rrec,rout=ce.lower_child(Rop);same(lout,Lop,'L Bruhat exact Gaussian phase');same(rout,Rop,'R Bruhat exact Gaussian phase')
 # L=LL F_a LR, R=RL F_b RR. Choose NEW FIRST unary U=RL LR.
 Uop=mul(compile_monomial(rrec['left'],m),compile_monomial(lrec['right'],m));need(ce.rank(x for x,y,p in Uop.tab[m:])==0,'first replacement is a physical monomial, not a hidden native query')
 Vop=mul(Lop,Uop.adjoint(),Rop);rank=ce.rank(x for x,y,p in Vop.tab[m:]);need(rank==abs(lrec['rank']-rrec['rank']),'two-site exact native-distance invoice')
 A=Algebra(2*q+1);Lf,Rf=family(A,L),family(A,R);Uf=A.lift(Uop);Vf=A.product(Lf,A.product(A.adjoint(Uf),Rf));vphase=family_phase(A,Vf,Vop)
 oldE=P+T;newE=P+newT;M,Mi=ring_replay(newE,n,m,A,{i:Uf,j:Vf});target,targeti=ring_replay(oldE,n,m,A)
 need(M==target,'every original independent bank coefficient, exact all-f Gaussian tensor algebra')
 need(Mi==targeti,'complete literal inverse every original field')
 need(A.mat_product(M,Mi)==A.mat_product(Mi,M)==A.mat_identity(n),'both complete arbitrary-input inverse orders')
 expected=A.mat_identity(n);Gout=A.lift(xop(prefix(m,2*q+1)@j_operator(m)),exponent=(prefix(m,2*q+1)@j_operator(m)).global_phase)
 for r in range(n):expected[r][r]=Gout
 need(M==expected,'actual final F_k J on every original owner, without dropped right gauges')
 # Complete selected recipe for the only new native unary and its inverse.
 recipes={}
 for inv in(False,True):
  op=Vop.adjoint()if inv else Vop;rec,out=ce.lower_child(op);same(out,op,'new unary selected-native actual Gaussian phase');need(rec['rank']==rank,'new unary selected child rank')
  recipes['two-site-later'+('inv'if inv else'')]={'selected_native_recipe':rec,'one_coordinate_literal_circuit':op.circuit,'one_coordinate_tableau':[list(t)for t in op.tab],
       'extra_global_phase_exponent_by_f_mod4':[(-x)%4 if inv else x for x in vphase]}
 modified=[]
 for at,e in enumerate(newE):
  if at in(i,j):
   op=Uop if at==i else Vop;fr=Uf if at==i else Vf;r=0 if at==i else rank
   modified.append({'kind':'NATIVE'if r else'ADDRESS_OR_UNIT','bank':e['bank'],'label':'two-site physical replacement of '+e['label'],'rank_per_f':r,
      'one_coordinate_literal_circuit':op.circuit,'one_coordinate_tableau':[list(t)for t in op.tab],
      'extra_global_phase_exponent_by_f_mod4':family_phase(A,fr,op),'native_recipe_id':'two-site-later'if r else None})
  else:modified.append(dict(e,unchanged_event_input=True))
 hist=Counter(e['rank_per_f']for e in modified if e['kind']=='NATIVE');mass=sum(r*c for r,c in hist.items());need(mass==f['source_complete_mass']-sum(T[r]['rank_per_f']for r in removed)-P[i].get('rank_per_f',0)-P[j].get('rank_per_f',0)+rank,'all changed native costs included')
 wrong,_=ring_replay(newE,n,m,A,{j:Vf});need(wrong!=target,'omitting changed first physical monomial rejects original columns')
 return{'status':'PASS_COMPLETE_TWO_SITE_PHYSICAL_BRUHAT_FUSION_ALL_COLUMNS_ALL_F','q':q,'banks':n,'ambient_arity':m,'sites':[i,j],'old_site_labels':[P[i]['label'],P[j]['label']],
     'removed_tail_sites':sorted(removed),'removed_tail_labels':[T[r]['label']for r in removed],'L':serial(L),'R':serial(R),'L_rank_per_f':lrec['rank'],'R_rank_per_f':rrec['rank'],
     'new_site_ranks_per_f':[0,rank],'histogram':dict(hist),'complete_native_mass':mass,'stock':f['stock'],'D':f['stock']-mass,'old_complete_mass':f['source_complete_mass'],
     'events':modified,'new_native_recipe_pool':recipes,'first_monomial_recipe':{'literal_circuit':Uop.circuit,'tableau':[list(t)for t in Uop.tab]},
     'all_original_columns_verified':n,'literal_inverse_orders':2,'selected_new_native_lowering':True,'unchanged_native_lowering':'inherits only the actual event operators; final source recipe manifest must be pinned independently after repair',
     'target':'diag(F_k J) on every original input, exact all-f phases and original owner labels retained',
     'negative_controls':['Omitting the first changed physical monomial rejects original columns.'],
     'phase_scope':'Every new operation is one fixed one-coordinate Clifford tensor power, multiplied by its explicit fmod4 Gaussian-unit vector; these scalar controls are paid scans, not native-rank mass.',
     'limits':['Complete fixed q as listed, not an all-q construction.','No outer exponent improvement claimed; positive stock deficit is not established unless D>0.','Unchanged source selected-native recipes are not re-certified from stale inherited metadata.'],
     'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'engine_sha256':need_engine,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'no_new_kappa':True}

def main():
 p=argparse.ArgumentParser();p.add_argument('--q',type=int,default=2);p.add_argument('--i',type=int,default=31);p.add_argument('--j',type=int,default=51);p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(run(a.q,a.i,a.j)));path=HERE/('ISOLATED-FUSION-Q'+str(a.q)+'.json')
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(path.read_text())==out,'saved complete isolated fusion differs')
 print(out['status'],'mass',out['complete_native_mass'],'stock',out['stock'],'ranks',out['new_site_ranks_per_f'],flush=True)
if __name__=='__main__':main()
