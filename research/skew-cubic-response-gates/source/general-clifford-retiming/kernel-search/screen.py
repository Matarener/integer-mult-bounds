#!/usr/bin/env python3
"""Exact finite-support skew-kernel invoice proposals; no kappa admission."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys,itertools,random,time,argparse
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent.parent
sys.path.insert(0,str(R/'caller-joint'))
from joint_algebra import *

def embed(g,m):
 d=len(g.rows);return qc.Mono(g.rows+tuple(1<<i for i in range(d,m)),g.offset,g.alpha+(0,)*(m-d),g.quad+(0,)*(m-d),g.constant,g.global_phase)
def invoice(j,q=2):
 k=2*q+1;n=2*q+2;m=2*(k+1);J=embed(j,m);N=lambda s:n_pair(m,s);P=lambda s:plane_swap(m,0,s)
 F=prefix(m,k);bar=N(1)@J@N(1).inv();B1=P(1)@N(0).inv()@J;Q=J.inv()@B1@J
 rparent=qc.rank((F@J).polar());rJ=qc.rank(J.polar());rbar=qc.rank(bar.polar());rQ=qc.rank((F@Q.inv()@F.inv()).polar())
 T=P(4)@bar
 for t in range(3,q+1):T=P(2*t)@bar@N(2*t-1)@T
 rR=qc.rank(T.polar());rL=4*q-4;rV=abs(rL-rR)
 base=2*(k*(n-1)+1)+2*(q-1);mass=base+2*rJ+3*q*rbar+rQ+rV;stock=n*rparent
 return dict(q=q,ambient_arity=m,parent_arity=rparent,J_rank=rJ,Jbar_rank=rbar,Q_rank=rQ,L_rank=rL,R_rank=rR,new_site_ranks=[0,rV],mass=mass,optimistic_stock=stock,D_optimistic=stock-mass)

def candidates(limit=10000):
 # All 4-axis invertible linear involutions, with a deterministic random bank
 # of diagonal Z4 quadratic conjugations. Exact square is rechecked before use.
 d=4;I=qc.identity(d);rng=random.Random(202610191355);linears=[]
 for rows in itertools.product(range(1,16),repeat=4):
  if qc.rank(rows)!=4:continue
  if any(qc.linear(rows,qc.linear(rows,1<<i))!=1<<i for i in range(d)):continue
  linears.append(rows)
 yield I,{'family':'identity'}
 # Every Hermitian Pauli involution in X characters, including tensor Y phases.
 for off in range(16):
  for x in range(16):
   alpha=tuple(2*((x>>i)&1)for i in range(4));c=qc.parity(off&x)
   S=qc.Mono(I.rows,off,alpha,(0,)*4,c,0)
   yield S,{'family':'Pauli','offset':off,'phase_mask':x}
 for rows in linears:
  for off in range(16):
   if qc.linear(rows,off)!=off:continue
   S=qc.Mono(rows,off,(0,)*4,(0,)*4)
   yield S,{'family':'affine_involution','rows':rows,'offset':off}
 for i in range(limit):
  rows=rng.choice(linears);offs=[x for x in range(16)if qc.linear(rows,x)==x];off=rng.choice(offs)
  P=qc.Mono(rows,off,(0,)*4,(0,)*4)
  alpha=tuple(rng.randrange(4)for _ in range(4));quad=tuple(sum(rng.randrange(2)<<j for j in range(i+1,4))for i in range(4));W=qc.Mono(I.rows,0,alpha,quad)
  yield W@P@W.inv(),{'family':'quadratic_conjugate','trial':i,'rows':rows,'offset':off,'W':W.data()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=10000);args=ap.parse_args();seen=set();hist=Counter();best=None;bestdesc=None;records=[];started=time.time()
 for S,desc in candidates(args.trials):
  if S in seen:continue
  seen.add(S);need(S@S==qc.identity(4),'actual involution square')
  j=qc.Mono(S.rows,S.offset,S.alpha,S.quad,S.constant,1);x=invoice(j);hist[x['D_optimistic']]+=1
  if best is None or x['D_optimistic']>best['D_optimistic']:
   best=x;bestdesc=desc;records.append({'invoice':x,'J':j.data(),'source':desc});print('BEST',len(seen),x,flush=True)
   (HERE/'BEST.json').write_text(json.dumps({'best':records[-1],'improvements':records,'tested_distinct':len(seen),'no_new_kappa':True},indent=2,sort_keys=True)+'\n')
  if x['D_optimistic']>0:break
  if len(seen)%500==0:print('PROGRESS',len(seen),time.time()-started,flush=True)
 out={'tested_distinct':len(seen),'D_histogram':dict(hist),'best':best,'best_source':bestdesc,'elapsed_seconds':time.time()-started,'no_new_kappa':True,'scope':'enumerated affine and Pauli involutions plus deterministic finite Z4-quadratic conjugates; rank invoice only'}
 (HERE/'SCREEN.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('DONE',out,flush=True)
if __name__=='__main__':main()
