#!/usr/bin/env python3
"""Exact finite controls for the written sparse-volume theorem; Apache-2.0."""
from fractions import Fraction as F
from pathlib import Path
import json
Z=(F(0),F(0));O=(F(1),F(0));I=(F(0),F(1));a=(F(1,2),F(1,2));b=(F(1,2),F(-1,2))
def require(p,m):
 if not p: raise RuntimeError(m)
def add(x,y):return (x[0]+y[0],x[1]+y[1])
def neg(x):return (-x[0],-x[1])
def sub(x,y):return add(x,neg(y))
def cj(x):return (x[0],-x[1])
def mul(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def scale(x,t):return (x[0]*t,x[1]*t)
def eye(n):return [[O if i==j else Z for j in range(n)] for i in range(n)]
def zero(m,n=None):return [[Z for _ in range(n or m)] for _ in range(m)]
def adj(X):return [[cj(v) for v in r] for r in zip(*X)]
def mm(X,Y):
 out=zero(len(X),len(Y[0]))
 for i,row in enumerate(X):
  for k,u in enumerate(row):
   if u==Z:continue
   for j,v in enumerate(Y[k]):
    if v!=Z:out[i][j]=add(out[i][j],mul(u,v))
 return out
def kron(X,Y):return [[mul(x,y) for x in xr for y in yr] for xr in X for yr in Y]
def plus(X,Y):return [[add(x,y) for x,y in zip(rx,ry)] for rx,ry in zip(X,Y)]
def sc(X,q):return [[scale(v,q) for v in r] for r in X]
def block(A,B,C,D):return [x+y for x,y in zip(A,B)]+[x+y for x,y in zip(C,D)]
def prod(M,N):return [[mul(x,cj(y)) for x,y in zip(rx,ry)] for rx,ry in zip(M,N)]
def pow2log(q):
 require(q>0,'positive norm squared')
 n,d=q.numerator,q.denominator
 require(n&(n-1)==0 and d&(d-1)==0,'fixture norm must be exact power of two')
 return n.bit_length()-d.bit_length()
def phi(M,N):
 out=Z
 for row in prod(M,N):
  for z in row:
   if z!=Z:out=add(out,scale(z,-F(pow2log(z[0]*z[0]+z[1]*z[1]),2)))
 return out
def matrices(f):
 K=[[a,b],[b,a]]; A=B=[[O]]
 for _ in range(f):A=kron(A,kron(K,eye(2)));B=kron(B,kron(eye(2),K))
 return A,B,mm(B,A)
def fixture(f,wrong=False):
 A,B,C=matrices(f);v=len(A);z=zero(v);J=block(z,A if wrong else adj(A),z,z)
 M=block(C,sc(B,F(1,2)),z,eye(v))
 Minv=block(adj(C),sc(mm(adj(C),B),F(-1,2)),z,eye(v))
 N=mm(adj(Minv),J)
 return v,A,B,C,J,M,N

def evaluate():
 ends=[]
 for f in (1,2):
  v,A,B,C,J,M,N=fixture(f)
  require(mm(adj(M),N)==J,'exact inverse-dual endpoint')
  require(phi(eye(2*v),J)==Z,'initial zero potential')
  require(phi(M,N)==(F(f*v,2),F(0)),'coupling entropy endpoint')
  require(all(sum(x!=Z for x in row)==2**f for row in B),'row support')
  require(all(x==Z or x[0]*x[0]+x[1]*x[1]==F(1,2**f) for row in B for x in row),'row flatness')
  # Ordinary potential ignores the off-diagonal coupling.
  ordinary=block(C,zero(v),sc(mm(adj(B),C),F(-1,2)),eye(v))
  diag=block(C,zero(v),zero(v),eye(v))
  require(phi(M,ordinary)==phi(diag,diag),'ordinary potential blindness')
  ends.append({'f':f,'V':v,'phi':str(F(f*v,2))})
 v,A,B,C,J,Final,Nfinal=fixture(1);n=2*v
 # Genuine complex shears: independently update M and its inverse dual N.
 M=eye(n);N=[r[:] for r in J];pair_checks=0
 for t,s,c in [(0,4,(F(1,2),F(0))),(1,0,(F(0),F(1,2))),(5,1,(F(2),F(0))),(7,2,(F(-3,2),F(1,2)))]:
  old=prod(M,N);M[t]=[add(x,mul(c,y)) for x,y in zip(M[t],M[s])]
  N[s]=[sub(x,mul(cj(c),y)) for x,y in zip(N[s],N[t])];new=prod(M,N)
  require(all(add(old[t][j],old[s][j])==add(new[t][j],new[s][j]) for j in range(n)),'column-pair invariant')
  require(mm(adj(M),N)==J,'full inverse-dual invariant');pair_checks+=n
 # Nonunit complex row scale and row permutation preserve every product.
 before=prod(M,N);c=(F(2),F(2));ci=(F(1,4),F(1,4)) # 1/conj(c)
 M[0]=[mul(c,x) for x in M[0]];N[0]=[mul(ci,x) for x in N[0]]
 require(prod(M,N)==before,'nonunit monomial invariant')
 M[0],M[6]=M[6],M[0];N[0],N[6]=N[6],N[0];after=prod(M,N);before[0],before[6]=before[6],before[0]
 require(after==before,'row permutation invariant')
 # The general native jump really can be nonzero after cheap coupling.
 pre=block(eye(v),sc(eye(v),F(1,2)),zero(v),eye(v))
 preinv=block(eye(v),sc(eye(v),F(-1,2)),zero(v),eye(v));preN=mm(adj(preinv),J)
 Q=block(C,zero(v),zero(v),eye(v));post=mm(Q,pre);postN=mm(Q,preN)
 delta=sub(phi(post,postN),phi(pre,preN));require(delta==(F(1),F(1)),'interleaved native jump retained')
 require(phi(Q,mm(Q,J))==Z,'target-first native jump zero')
 # Unspecified off-domain clean behavior: M=[[Final,R],[0,D]], D nonunit.
 d=2;R=[[(F(i%3-1,2),F((i+j)%2,2)) for j in range(d)] for i in range(n)]
 D=[[ (F(2),F(0)),O],[Z,(F(1,2),F(0))]];Di=[[(F(1,2),F(0)),neg(O)],[Z,(F(2),F(0))]]
 full=block(Final,R,zero(d,n),D);JJ=block(J,zero(n,d),zero(d,n),zero(d))
 NN=block(Nfinal,zero(n,d),sc(mm(mm(adj(Di),adj(R)),Nfinal),F(-1)),zero(d))
 require(mm(adj(full),NN)==JJ,'clean off-domain inverse-dual identity')
 require(phi(full,NN)==(F(v,2),F(0)),'clean-returned endpoint potential')
 # Controls reject the exact failure modes at issue, not the theorem by sampling.
 controls={}
 _,_,_,_,_,badM,badN=fixture(1,wrong=True)
 controls['wrong_preconditioner_orientation']=phi(badM,badN)!=(F(v,2),F(0))
 controls['interleaved_jump_omitted']=delta!=Z
 badfull=[r[:] for r in full];badfull[-1][4]=O
 clean_restored=lambda X:all(x==Z for row in X[n:] for x in row[:n])
 require(clean_restored(full),'clean restoration on every legal input')
 controls['clean_output_leak']=not clean_restored(badfull)
 # Omitting conjugation in inverse-dual update is invalid for imaginary shear.
 MM=eye(n);NN0=[r[:] for r in J];cc=(F(0),F(1,2));t,s=0,4
 MM[t]=[add(x,mul(cc,y)) for x,y in zip(MM[t],MM[s])]
 NN0[s]=[sub(x,mul(cc,y)) for x,y in zip(NN0[s],NN0[t])]
 controls['missing_inverse_dual_conjugation']=mm(adj(MM),NN0)!=J
 # A noncommuting fixture catches BA/AB order substitutions hidden by tensors.
 An=[[O,Z],[Z,I]];Bn=[[a,b],[b,a]];Cn=mm(Bn,An);zn=zero(2)
 Jn=block(zn,adj(An),zn,zn);Fn=block(Cn,sc(Bn,F(1,2)),zn,eye(2))
 expectedN=block(zn,Bn,zn,sc(eye(2),F(-1,2)))
 require(mm(adj(Fn),expectedN)==Jn,'noncommuting BA endpoint')
 require(phi(Fn,expectedN)==(F(1),F(0)),'noncommuting entropy endpoint')
 badF=block(mm(An,Bn),sc(Bn,F(1,2)),zn,eye(2))
 controls['wrong_noncommuting_order']=mm(adj(badF),expectedN)!=Jn
 require(all(controls.values()),'all defect controls reject '+str(controls))
 return {'endpoint_fixtures':ends,'complex_pair_column_checks':pair_checks,'noncommuting_endpoint':True,'interleaved_native_jump':['1','1'],'clean_auxiliary_coordinates':d,'monomial_controls':2,'negative_controls':controls,'theorem_evidence':'Written all-dimension proof; finite controls are not an exhaustive proof.','uniform_K_bound':'S>=fV/(16K) only for zero native jump','general_bound':'8K*S+Re(Delta_Q)>=fV/2','new_kappa':False}
if __name__=='__main__':
 r=evaluate();require(r==json.loads((Path(__file__).parent/'RESULT.json').read_text()),'frozen result equality')
 print('PASS_SPARSE_FEEDBACK_VOLUME endpoint_f=1,2 complex_pair_columns=32 controls=5 child_jump_explicit no_new_kappa')
