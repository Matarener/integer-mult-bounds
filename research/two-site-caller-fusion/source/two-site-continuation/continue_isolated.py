#!/usr/bin/env python3
"""One bounded continuation: isolated two-site pairs after the saved fusion.
Apache-2.0; substantial OpenAI Codex assistance. Rank intake only.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,time
from isolated_fusion import *
HERE=Path(__file__).resolve().parent

def unary(A,e):
 op=ce.Op(A.m,tuple(tuple(t)for t in e['one_coordinate_tableau']),e['one_coordinate_literal_circuit']);value=A.lift(op)
 units=(G(F(1)),G(F(0),F(1)),G(F(-1)),G(F(0),F(-1)))
 v=tuple(units[j]for j in e['extra_global_phase_exponent_by_f_mod4'])
 return{k:tuple(x*y for x,y in zip(w,v))for k,w in value.items()}
def isunit(E):
 if len(E)!=1:return False
 (kd,kb),v=next(iter(E.items()))
 return kd==kb and all(x.a*x.a+x.b*x.b==1 for x in v)
def rank_family(A,E):need(isunit(E),'actual single uniform unitary Clifford');return ce.rank(x for x,y,p in A.rep[next(iter(E))[0]].tab[A.m:])

def apply_events(E,n,A):
 M=A.mat_identity(n);Mi=A.mat_identity(n)
 for e in E:
  k=e['kind']
  if k=='ADD':
   d,s,c=e['dst'],e['src'],F(e['coefficient']);M[d]=[A.add(x,A.scale(y,c))for x,y in zip(M[d],M[s])]
   for row in Mi:row[s]=A.add(row[s],A.scale(row[d],-c))
  elif k=='SCALE':
   b,c=e['bank'],F(e['coefficient']);M[b]=[A.scale(x,c)for x in M[b]]
   for row in Mi:row[b]=A.scale(row[b],1/c)
  elif k=='BANK_SWAP':
   i,j=e['banks'];M[i],M[j]=M[j],M[i]
   for row in Mi:row[i],row[j]=row[j],row[i]
  else:
   b=e['bank'];U=unary(A,e);Ui=A.adjoint(U);M[b]=[A.product(U,x)for x in M[b]]
   for row in Mi:row[b]=A.product(row[b],Ui)
 return M,Mi

def pullback_general(C,e,A):
 C=[[dict(x)for x in row]for row in C];k=e['kind']
 if k=='ADD':
  d,s,c=e['dst'],e['src'],F(e['coefficient']);C[d]=[A.add(x,A.scale(y,-c))for x,y in zip(C[d],C[s])]
  for row in C:row[s]=A.add(row[s],A.scale(row[d],c))
 elif k=='SCALE':
  b,c=e['bank'],F(e['coefficient']);C[b]=[A.scale(x,1/c)for x in C[b]]
  for row in C:row[b]=A.scale(row[b],c)
 elif k=='BANK_SWAP':
  i,j=e['banks'];C[i],C[j]=C[j],C[i]
  for row in C:row[i],row[j]=row[j],row[i]
 else:
  b=e['bank'];U=unary(A,e);Ui=A.adjoint(U);C[b]=[A.product(Ui,x)for x in C[b]]
  for row in C:row[b]=A.product(row[b],U)
 return C

def pair_cols(P,i,j,n,A):
 b=P[i]['bank'];col=[dict(A.one)if r==b else{}for r in range(n)];row=[dict(x)for x in col]
 for e in P[i+1:j+1]:
  k=e['kind']
  if k=='ADD':
   d,s,c=e['dst'],e['src'],F(e['coefficient']);col[d]=A.add(col[d],A.scale(col[s],c));row[s]=A.add(row[s],A.scale(row[d],-c))
  elif k=='SCALE':
   b,c=e['bank'],F(e['coefficient']);col[b]=A.scale(col[b],c);row[b]=A.scale(row[b],1/c)
  elif k=='BANK_SWAP':
   i0,j0=e['banks'];col[i0],col[j0]=col[j0],col[i0];row[i0],row[j0]=row[j0],row[i0]
  else:
   b=e['bank'];U=unary(A,e);col[b]=A.product(U,col[b]);row[b]=A.product(row[b],A.adjoint(U))
 return col,row

def run(seconds):
 source=HERE/'ISOLATED-FUSION-Q2.json';f=json.loads(source.read_text());n=f['banks'];A=Algebra(5);P,T=f['prefix_events'],f['tail_events'];I=A.mat_identity(n)
 M,Mi=apply_events(P+T,n,A);need(A.mat_product(M,Mi)==A.mat_product(Mi,M)==I,'continuation source every original field and both inverse orders')
 oldT,_=apply_events(T,n,A);sites=[i for i,e in enumerate(P)if e['kind']not in('ADD','SCALE','BANK_SWAP')];ts=[i for i,e in enumerate(T)if e['kind']=='NATIVE'];pairs={};cases=[];counts=Counter();done=[];start=time.monotonic();timeout=False
 for mask in range(1,1<<len(ts)):
  removed={ts[r]for r in range(len(ts))if mask>>r&1};newT=[e for at,e in enumerate(T)if at not in removed];_,Tinv=apply_events(newT,n,A);C=A.mat_product(Tinv,oldT);cuts={}
  for at in range(len(P)-1,-1,-1):
   if at in sites:cuts[at]=C
   C=pullback_general(C,P[at],A)
  for jj,j in enumerate(sites):
   C=cuts[j];bank=P[j]['bank']
   if any(C[r][c]!=I[r][c]for r in range(n)for c in range(n)if(r,c)!=(bank,bank)):counts['correction-not-one-bank']+=jj;continue
   if not isunit(C[bank][bank]):counts['correction-not-one-Clifford']+=jj;continue
   for i in sites[:jj]:
    if(i,j)not in pairs:pairs[i,j]=pair_cols(P,i,j,n,A)
    col,row=pairs[i,j]
    if any(col[r]for r in range(n)if r!=bank)or any(row[c]for c in range(n)if c!=bank):counts['not-isolated-both-sides']+=1;continue
    if not isunit(col[bank]):counts['transport-not-one-Clifford']+=1;continue
    L=A.product(C[bank][bank],A.product(col[bank],unary(A,P[i])));R=A.product(A.adjoint(col[bank]),unary(A,P[j]));a,b=rank_family(A,L),rank_family(A,R)
    mass=f['complete_native_mass']-sum(T[r]['rank_per_f']for r in removed)-P[i].get('rank_per_f',0)-P[j].get('rank_per_f',0)+abs(a-b)
    cases.append({'mask':mask,'removed_tail_labels':[T[r]['label']for r in removed],'sites':[i,j],'labels':[P[i]['label'],P[j]['label']],'L_R_ranks':[a,b],
                  'minimum_new_native_mass':abs(a-b),'complete_mass':mass,'stock':f['stock'],'rank_only':True,'selected_new_lowering':False})
    counts['isolated-pairs-priced']+=1
    if time.monotonic()-start>seconds:timeout=True;break
   if timeout:break
  if timeout:break
  done.append(mask);print('continued mask',mask,'cases',len(cases),'best',min([f['complete_native_mass']]+[x['complete_mass']for x in cases]),flush=True)
 return{'status':'PASS_BOUNDED_GENERAL_CLIFFORD_ISOLATED_PAIR_CONTINUATION','source_path':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'q':2,'base_mass':f['complete_native_mass'],'stock':f['stock'],'tail_native_sites':ts,'completed_masks':done,'timed_out':timeout,'counts':dict(counts),'cases':cases,
     'best_rank_only_complete_mass':min([f['complete_native_mass']]+[x['complete_mass']for x in cases]),'elapsed_seconds':time.monotonic()-start,
     'scope':'After the independently complete mass76 word, delete a nonempty subset of its remaining tail native queries. Price every two-existing-prefix-unary pair whose transported whole-bank row AND column are isolated and whose required cut correction is a single unitary Clifford bank. Other pairs are not excluded. The exact minimum for that stratum is |rank(L)-rank(R)|, with unrestricted physical monomial adapters.',
     'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'no_new_kappa':True}
def main():
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=int,default=180);a=p.parse_args();out=run(a.seconds);path=HERE/'CONTINUED-ISOLATION-Q2.json';path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],'best',out['best_rank_only_complete_mass'],out['counts'],flush=True)
if __name__=='__main__':main()
