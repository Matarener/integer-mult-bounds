#!/usr/bin/env python3
"""Two-site exact Clifford equation screen on immutable event-only input.
Apache-2.0; substantial OpenAI Codex assistance. No heuristic lower bound.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ENGINE=HERE.parent/'caller-joint/joint_algebra.py'
need_engine='6fe4de627845a36e2e08723e705daa86959846fe4ea577e94fca233829d7d5c9'
if hashlib.sha256(ENGINE.read_bytes()).hexdigest()!=need_engine:raise ValueError('frozen exact engine pin')
sys.path.insert(0,str(ENGINE.parent))
from joint_algebra import *

def inverse(E,m):
 out=[]
 for event in reversed(E):
  e=dict(event)
  if e['kind']=='ADD':e['coefficient']=str(-F(e['coefficient']))
  elif e['kind']=='SCALE':e['coefficient']=str(1/F(e['coefficient']))
  elif e['kind']!='BANK_SWAP':e['x_monomial']=qc.decode(e,m).inv().data()
  out.append(e)
 return out

def pullback(C,e,m):
 C=[[dict(x)for x in row]for row in C];kind=e['kind']
 if kind=='ADD':
  d,s,c=e['dst'],e['src'],F(e['coefficient']);C[d]=[add(x,scale(y,-c))for x,y in zip(C[d],C[s])]
  for row in C:row[s]=add(row[s],scale(row[d],c))
 elif kind=='BANK_SWAP':
  i,j=e['banks'];C[i],C[j]=C[j],C[i]
  for row in C:row[i],row[j]=row[j],row[i]
 elif kind=='SCALE':
  b,c=e['bank'],F(e['coefficient']);C[b]=[scale(x,1/c)for x in C[b]]
  for row in C:row[b]=scale(row[b],c)
 else:
  b=e['bank'];G,Gi=mono(qc.decode(e,m)),mono(qc.decode(e,m).inv());C[b]=[product(Gi,x)for x in C[b]]
  for row in C:row[b]=product(row[b],G)
 return C

def invertible_ray(E):return len(E)==1 and all(v[2*r]or v[2*r+1]for v in E.values()for r in range(4))
def ray_inverse(E):
 need(invertible_ray(E),'invert only a nonzero single Clifford ray')
 v=next(iter(E.values()));norm=[v[2*r]**2+v[2*r+1]**2 for r in range(4)]
 return{g:tuple(x/norm[i//2]for i,x in enumerate(w))for g,w in adjoint(E).items()}
def unitary_clifford(E):
 if len(E)!=1:return False
 v=next(iter(E.values()))
 return all((v[2*r],v[2*r+1])in((F(1),F(0)),(F(-1),F(0)),(F(0),F(1)),(F(0),F(-1)))for r in range(4))

def pair_columns(P,i,j,n,m):
 """A=V e_b, B=e_b^T V^-1, V=E_j...E_(i+1)."""
 I=mono(qc.identity(m));b=P[i]['bank'];A=[dict(I)if r==b else{}for r in range(n)];B=[dict(x)for x in A]
 for e in P[i+1:j+1]:
  kind=e['kind']
  if kind=='ADD':
   d,s,c=e['dst'],e['src'],F(e['coefficient']);A[d]=add(A[d],scale(A[s],c));B[s]=add(B[s],scale(B[d],-c))
  elif kind=='BANK_SWAP':
   d,s=e['banks'];A[d],A[s]=A[s],A[d];B[d],B[s]=B[s],B[d]
  elif kind=='SCALE':
   d,c=e['bank'],F(e['coefficient']);A[d]=scale(A[d],c);B[d]=scale(B[d],1/c)
  else:
   d=e['bank'];g=qc.decode(e,m);A[d]=product(mono(g),A[d]);B[d]=product(B[d],mono(g.inv()))
 need(summ(product(B[r],A[r])for r in range(n))==I,'paired transported row/column BA=I')
 return A,B

def solve(C,A,B,bank,I):
 equation=None
 for r in range(len(C)):
  if r==bank:continue
  for c in range(len(C)):
   if invertible_ray(A[r])and invertible_ray(B[c]):
    rhs=add(add(C[r][c],scale(I[r][c],-1)),product(A[r],B[c]))
    X=product(ray_inverse(A[r]),product(rhs,ray_inverse(B[c])))
    equation=(r,c)
    if not unitary_clifford(X):return None,'unique-nonunit-or-nonclifford',equation
    # Every off-later-bank coefficient is checked, not only the source equation.
    XmI=add(X,scale(I[0][0],-1))
    for rr in range(len(C)):
     if rr==bank:continue
     for cc in range(len(C)):
      if add(I[rr][cc],product(A[rr],product(XmI,B[cc])))!=C[rr][cc]:return None,'off-bank-defect',equation
    # C Z^-1 must be one literal unitary diagonal bank factor.
    CA=[summ(product(C[rr][cc],A[cc])for cc in range(len(C)))for rr in range(len(C))]
    XimI=add(adjoint(X),scale(I[0][0],-1));D=[[add(C[rr][cc],product(CA[rr],product(XimI,B[cc])))for cc in range(len(C))]for rr in range(len(C))]
    if any(D[rr][cc]!=I[rr][cc]for rr in range(len(C))for cc in range(len(C))if(rr,cc)!=(bank,bank)):return None,'second-bank-defect',equation
    if not unitary_clifford(D[bank][bank]):return None,'second-nonunit-or-nonclifford',equation
    return(X,D[bank][bank]),'accepted',equation
 if any(A[r]for r in range(len(A))if r!=bank):return None,'unresolved-no-invertible-ray-equation',None
 if any(C[r][c]!=I[r][c]for r in range(len(C))if r!=bank for c in range(len(C))):return None,'row-confined-effect-cannot-fit',None
 return None,'unresolved-row-confined-factorization',None

def event_replacement(e,R):
 g,v=next(iter(R.items()));rank=qc.rank(g.polar());d={k:x for k,x in e.items()if k in('bank','label')}
 d.update(kind='NATIVE'if rank else'ADDRESS_OR_UNIT',x_monomial=g.data(),rank_per_f=rank,
          scalar_phase_by_f_mod4=[[str(v[2*r]),str(v[2*r+1])]for r in range(4)],label='two-site replacement of '+e['label'])
 # The decoder can only carry a global/tensor affine phase. Non-affine fmod4
 # phases are retained explicitly and replayed by the matrix verifier below.
 return d

def replay_replaced(P,T,i,j,Ri,Rj,n,m):
 W=eye(n,m)
 for at,e in enumerate(P+T):
  if at in(i,j):
   R=Ri if at==i else Rj;b=e['bank'];W[b]=[product(R,x)for x in W[b]]
  else:
   k=e['kind']
   if k=='ADD':W[e['dst']]=[add(x,scale(y,F(e['coefficient'])))for x,y in zip(W[e['dst']],W[e['src']])]
   elif k=='BANK_SWAP':a,b=e['banks'];W[a],W[b]=W[b],W[a]
   elif k=='SCALE':W[e['bank']]=[scale(x,F(e['coefficient']))for x in W[e['bank']]]
   else:b=e['bank'];G=mono(qc.decode(e,m));W[b]=[product(G,x)for x in W[b]]
 return W

def screen(f,max_seconds=1200):
 start=time.monotonic();q,n,m=f['q'],f['banks'],f['ambient_arity'];P,T=f['prefix_events'],f['tail_events'];I=eye(n,m)
 target=qc.replay(P+T,n,m);oldT=qc.replay(T,n,m)
 need(sum(e.get('rank_per_f',0)for e in P+T if e['kind']=='NATIVE')==f['source_complete_mass'],'frozen actual event native bill')
 sites=[i for i,e in enumerate(P)if e['kind']not in('ADD','SCALE','BANK_SWAP')];tailsites=[i for i,e in enumerate(T)if e['kind']=='NATIVE'];pairs={}
 for jj,j in enumerate(sites):
  for i in sites[:jj]:pairs[i,j]=pair_columns(P,i,j,n,m)
 counts=Counter();accepted=[];improving=[];done=[];timed_out=False;best=f['source_complete_mass']
 for mask in range(1,1<<len(tailsites)):
  removed={tailsites[r]for r in range(len(tailsites))if mask>>r&1};newT=[e for at,e in enumerate(T)if at not in removed]
  C=mm(qc.replay(inverse(newT,m),n,m),oldT);cuts={}
  for at in range(len(P)-1,-1,-1):
   if at in sites:cuts[at]=C
   C=pullback(C,P[at],m)
  removed_mass=sum(T[r]['rank_per_f']for r in removed)
  for (i,j),(A,B)in pairs.items():
   result,status,equation=solve(cuts[j],A,B,P[j]['bank'],I);counts[status]+=1
   if result:
    X,Y=result;Ri=product(X,mono(qc.decode(P[i],m)));Rj=product(Y,mono(qc.decode(P[j],m)))
    need(unitary_clifford(Ri)and unitary_clifford(Rj),'both replacements actual unitary Clifford families')
    ri,rj=qc.rank(next(iter(Ri)).polar()),qc.rank(next(iter(Rj)).polar());mass=f['source_complete_mass']-removed_mass-P[i].get('rank_per_f',0)-P[j].get('rank_per_f',0)+ri+rj
    witness={'tail_mask':mask,'removed_tail_sites':sorted(removed),'removed_tail_labels':[T[r]['label']for r in sorted(removed)],'sites':[i,j],'banks':[P[i]['bank'],P[j]['bank']],
             'labels':[P[i]['label'],P[j]['label']],'equation':list(equation),'old_ranks':[P[i].get('rank_per_f',0),P[j].get('rank_per_f',0)],'new_ranks':[ri,rj],
             'complete_mass':mass,'stock':f['stock'],'replacement_operators':[serial(Ri),serial(Rj)],'rank_only':True,'selected_native_lowering':False}
    if mass<=best:
     need(replay_replaced(P,newT,i,j,Ri,Rj,n,m)==target,'candidate complete arbitrary-input physical word every coefficient')
     witness['all_original_columns_verified']=n
    accepted.append(witness)
    if mass<best:best=mass;improving.append(witness);print('q',q,'new best',mass,'stock',f['stock'],'mask',mask,'sites',i,j,flush=True)
   if time.monotonic()-start>max_seconds:timed_out=True;break
  if timed_out:break
  done.append(mask);print('q',q,'finished mask',mask,'/',(1<<len(tailsites))-1,'checks',sum(counts.values()),'best',best,flush=True)
 return{'q':q,'banks':n,'ambient_arity':m,'base_mass':f['source_complete_mass'],'stock':f['stock'],'prefix_unary_sites':sites,'tail_native_sites':tailsites,
        'completed_tail_masks':done,'timed_out':timed_out,'counts':dict(counts),'accepted':accepted,'strict_improvements':improving,'best_rank_only_complete_mass':best,
        'all_accepted_meeting_current_best_full_coefficients_verified':True,'elapsed_seconds':time.monotonic()-start,
        'scope':'Exact two-existing-unary replacement model. A nonempty tail native subset is removed; all other event sites are fixed. Every pair with an invertible single-ray off-bank equation is solved uniquely. Unresolved pairs are counted and are not excluded. Accepted operators are unitary Clifford tensor families with explicit Gaussian-unit phase for every fmod4. Native rank invoices are not selected child recipes or owner admission.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--q',type=int,default=2);p.add_argument('--seconds',type=int,default=1200);a=p.parse_args();source=HERE/'INPUT-EVENTS.json';data=json.loads(source.read_text());f=next(x for x in data['fixtures']if x['q']==a.q)
 out=screen(f,a.seconds);out['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();out['engine_sha256']=need_engine;out['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out['no_new_kappa']=True
 path=HERE/('TWO-SITE-Q'+str(a.q)+'.json');path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('DONE',path.name,'best',out['best_rank_only_complete_mass'],'counts',out['counts'],flush=True)
if __name__=='__main__':main()
