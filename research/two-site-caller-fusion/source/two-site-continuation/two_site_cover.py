#!/usr/bin/env python3
"""Finite Clifford-ray cover for two-site off-bank equations with sums.
Apache-2.0; substantial OpenAI Codex assistance. Unresolved strata explicit.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,itertools,time
from two_site import *

def divc(a,b):
 den=b[0]*b[0]+b[1]*b[1];need(den!=0,'invert nonzero Gaussian scalar')
 return((a[0]*b[0]+a[1]*b[1])/den,(a[1]*b[0]-a[0]*b[1])/den)

def coefficient_candidates(C,A,B,bank,I,g):
 X0=mono(g);XmI=add(X0,scale(I[0][0],-1));phase=[None]*4
 for r in range(len(C)):
  if r==bank:continue
  for c in range(len(C)):
   L=product(A[r],product(X0,B[c]));H=add(add(C[r][c],scale(I[r][c],-1)),product(A[r],B[c]))
   for h in set(L)|set(H):
    lv,hv=L.get(h,ZERO),H.get(h,ZERO)
    for f in range(4):
     a,b=tuple(hv[2*f:2*f+2]),tuple(lv[2*f:2*f+2])
     if b==(0,0):
      if a!=(0,0):return[]
     else:
      v=divc(a,b)
      if v not in((1,0),(-1,0),(0,1),(0,-1)):return[]
      if phase[f]is None:phase[f]=v
      elif phase[f]!=v:return[]
 choices=[(v,)if v is not None else((F(1),F(0)),(F(-1),F(0)),(F(0),F(1)),(F(0),F(-1)))for v in phase]
 out=[]
 for vv in itertools.product(*choices):
  coeff=tuple(x for pair in vv for x in pair)
  X={h:cproduct(v,coeff)for h,v in X0.items()}
  # g was normalized to one canonical ray; check every off-bank entry again.
  XmI=add(X,scale(I[0][0],-1))
  if any(add(I[r][c],product(A[r],product(XmI,B[c])))!=C[r][c]for r in range(len(C))if r!=bank for c in range(len(C))):continue
  CA=[summ(product(C[r][c],A[c])for c in range(len(C)))for r in range(len(C))];XimI=add(adjoint(X),scale(I[0][0],-1))
  D=[[add(C[r][c],product(CA[r],product(XimI,B[c])))for c in range(len(C))]for r in range(len(C))]
  if any(D[r][c]!=I[r][c]for r in range(len(C))for c in range(len(C))if(r,c)!=(bank,bank)):continue
  if unitary_clifford(D[bank][bank]):out.append((X,D[bank][bank]))
 return out

def cover(C,A,B,bank,I):
 equations=[]
 for r in range(len(C)):
  if r==bank:continue
  for c in range(len(C)):
   H=add(add(C[r][c],scale(I[r][c],-1)),product(A[r],B[c]))
   if H:
    if not A[r]or not B[c]:return[],'zero-side-nonzero-rhs',0,None
    equations.append((len(A[r])*len(B[c]),r,c,H))
 if not equations:return[],'unresolved-homogeneous-off-bank-equations',0,None
 _,r,c,H=min(equations,key=lambda t:t[0]);h=next(iter(H));candidates=set()
 for a in A[r]:
  for b in B[c]:
   v=mono(a.inv()@h@b.inv());candidates.add(next(iter(v)))
 results=[]
 for g in candidates:results.extend(coefficient_candidates(C,A,B,bank,I,g))
 return results,'finite-ray-cover',len(candidates),[r,c]

def run(q):
 source=HERE/'INPUT-EVENTS.json';f=next(x for x in json.loads(source.read_text())['fixtures']if x['q']==q)
 n,m=f['banks'],f['ambient_arity'];P,T=f['prefix_events'],f['tail_events'];I=eye(n,m);oldT=qc.replay(T,n,m);target=qc.replay(P+T,n,m)
 sites=[i for i,e in enumerate(P)if e['kind']not in('ADD','SCALE','BANK_SWAP')];ts=[i for i,e in enumerate(T)if e['kind']=='NATIVE']
 pairs={(i,j):pair_columns(P,i,j,n,m)for at,j in enumerate(sites)for i in sites[:at]};counts=Counter();cases=[];accepted=[];best=f['source_complete_mass'];start=time.monotonic()
 for mask in range(1,1<<len(ts)):
  removed={ts[r]for r in range(len(ts))if mask>>r&1};newT=[e for at,e in enumerate(T)if at not in removed];C=mm(qc.replay(inverse(newT,m),n,m),oldT);cuts={}
  for at in range(len(P)-1,-1,-1):
   if at in sites:cuts[at]=C
   C=pullback(C,P[at],m)
  for(i,j),(A,B)in pairs.items():
   _,status,_=solve(cuts[j],A,B,P[j]['bank'],I)
   if not status.startswith('unresolved'):continue
   solutions,kind,total,equation=cover(cuts[j],A,B,P[j]['bank'],I);counts[kind]+=1
   entry={'mask':mask,'sites':[i,j],'banks':[P[i]['bank'],P[j]['bank']],'labels':[P[i]['label'],P[j]['label']],'initial_status':status,'cover_status':kind,'canonical_candidates':total,'solutions':len(solutions),'equation':equation}
   cases.append(entry)
   for X,Y in solutions:
    Ri=product(X,mono(qc.decode(P[i],m)));Rj=product(Y,mono(qc.decode(P[j],m)));ri,rj=qc.rank(next(iter(Ri)).polar()),qc.rank(next(iter(Rj)).polar())
    mass=f['source_complete_mass']-sum(T[r]['rank_per_f']for r in removed)-P[i].get('rank_per_f',0)-P[j].get('rank_per_f',0)+ri+rj
    need(replay_replaced(P,newT,i,j,Ri,Rj,n,m)==target,'finite-cover exact candidate every original coefficient')
    witness=dict(entry,complete_mass=mass,stock=f['stock'],replacement_ranks=[ri,rj],replacement_operators=[serial(Ri),serial(Rj)],rank_only=True,selected_native_lowering=False)
    accepted.append(witness)
    if mass<best:best=mass;print('NEW COVER BEST',mass,'mask',mask,'sites',i,j,flush=True)
  print('cover q',q,'mask',mask,'cases',len(cases),'best',best,flush=True)
 return{'status':'PASS_EXACT_TWO_SITE_FINITE_RAY_COVER','q':q,'base_mass':f['source_complete_mass'],'stock':f['stock'],'cases':cases,'counts':dict(counts),'accepted':accepted,'best_rank_only_complete_mass':best,
        'elapsed_seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'parent_producer_sha256':hashlib.sha256((HERE/'two_site.py').read_bytes()).hexdigest(),'no_new_kappa':True,
        'scope':'Every previously unresolved pair with at least one nonzero off-bank RHS has a finite exhaustive canonical Clifford-ray cover. A surviving h in A X B forces X=a^-1 h b^-1 up to phase for some rays a,b. Every Gaussian-unit fmod4 phase is solved and verified in every coefficient. Homogeneous off-bank strata remain explicit and are not excluded.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--q',type=int,default=2);a=p.parse_args();out=run(a.q);path=HERE/('TWO-SITE-COVER-Q'+str(a.q)+'.json');path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],out['counts'],'best',out['best_rank_only_complete_mass'],flush=True)
if __name__=='__main__':main()
