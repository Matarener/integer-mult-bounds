#!/usr/bin/env python3
"""Exact cubic Clifford/tensor counterexample; no supplier or kappa claim."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent.parent
for pin in json.loads((HERE/'SOURCE-PINS.json').read_text())['read_only_sources']:
    if hashlib.sha256(Path(pin['path']).read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('source pin '+pin['path'])
sys.path.insert(0,str(R/'caller-joint'))
from joint_algebra import ce,mul,need
Z=(F(0),F(0));O=(F(1),F(0))
def plus(a,b):return(a[0]+b[0],a[1]+b[1])
def times(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def divide(a,b):
 d=b[0]**2+b[1]**2;need(bool(d),'nonzero Gaussian denominator');return((a[0]*b[0]+a[1]*b[1])/d,(a[1]*b[0]-a[0]*b[1])/d)
def eye(d):return[[O if i==j else Z for j in range(d)]for i in range(d)]
def add(A,B):return[[plus(x,y)for x,y in zip(a,b)]for a,b in zip(A,B)]
def product(A,B):
 d=len(A);return[[sumg(times(A[i][k],B[k][j])for k in range(d))for j in range(d)]for i in range(d)]
def sumg(items):
 a=Z
 for b in items:a=plus(a,b)
 return a
def tensor(A,B):return[[times(A[i][j],B[k][l])for j in range(len(A))for l in range(len(B))]for i in range(len(A))for k in range(len(B))]
def matrix(op):
 columns=[]
 for j in range(1<<op.n):
  v,d=op.zero_state(j);columns.append([(F(a,1<<d),F(b,1<<d))for a,b in v])
 return[list(row)for row in zip(*columns)]
def serial(A):return[[[str(a),str(b)]for a,b in row]for row in A]
def spanrank(matrices):
 rows=[list(row)for row in zip(*[[x for line in A for x in line]for A in matrices])];r=0
 for c in range(len(matrices)):
  pivot=next((i for i in range(r,len(rows))if rows[i][c]!=Z),None)
  if pivot is None:continue
  rows[r],rows[pivot]=rows[pivot],rows[r];p=rows[r][c];rows[r]=[divide(x,p)for x in rows[r]]
  for i in range(len(rows)):
   if i==r:continue
   t=rows[i][c]
   if t!=Z:rows[i]=[plus(a,(-b[0],-b[1]))for a,b in zip(rows[i],[times(t,x)for x in rows[r]])]
  r+=1
 return r

def family(f):
 out=ce.ident(f)
 for j in range(f):
  C=ce.cgate(f,1<<j);Q=tuple(1<<j if i==j else 0 for i in range(f));S=ce.diag(f,Q);phase=ce.Op(f,ce.identity(f),[('phase',1)])
  out=mul(phase,C,S,C,S.adjoint(),out)
 return out

def fixed_pauli_trace(op):
 n=op.n;count=0;total=0
 for x in range(1<<n):
  for z in range(1<<n):
   p=(x&z).bit_count()%4;a,b,c=ce.apply(op.tab,(x,z,p))
   if(a,b)==(x,z):
    d=(c-p)%4;need(d in(0,2),'Hermitian fixed Pauli sign');count+=1;total+=1 if d==0 else-1
 return count,total

def run():
 J=[[(F(-1,2),F(1,2)),(F(1,2),F(1,2))],[(F(-1,2),F(1,2)),(F(-1,2),F(-1,2))]]
 need(matrix(family(1))==J,'actual i C S C S^-1 matrix including Gaussian phase')
 need(sumg(J[i][i]for i in range(2))==(F(-1),F(0)),'trace -1')
 need(plus(times(J[0][0],J[1][1]),tuple(-a for a in times(J[0][1],J[1][0])))==O,'determinant 1')
 result=[];T=[[O]]
 for f in range(1,5):
  T=tensor(T,J);op=family(f);A=matrix(op);need(A==T,'actual tensor family every matrix entry');I=eye(1<<f);A2=product(A,A);need(product(A2,A)==I,'actual order three all tested f')
  residual=add(add(A2,A),I);quad=all(v==Z for row in residual for v in row);need(quad==(f==1),'quadratic holds only f1 in retained fixtures')
  r=ce.rank(x for x,z,p in op.tab[f:]);need(r==f,'actual native B rank scales with f')
  columns=[x|(z<<f)for x,z,p in op.tab];defect=ce.rank(c^(1<<j)for j,c in enumerate(columns));need(defect==2*f,'actual symplectic defect rank')
  count,total=fixed_pauli_trace(op);tr=sumg(A[i][i]for i in range(1<<f));norm=tr[0]**2+tr[1]**2
  need(total==norm and count==1<<(2*f-defect),'signed Pauli fixed-character trace formula')
  span=spanrank([I,A,A2]);need(span==(2 if f==1 else 3),'actual whole-field powers span')
  out={'f':f,'matrix':serial(A),'native_B_rank':r,'symplectic_defect_rank':defect,'trace':[str(tr[0]),str(tr[1])],'fixed_Pauli_count':count,'signed_fixed_Pauli_sum':total,'quadratic_relation':quad,'span_rank_I_J_J2':span,'literal_circuit':op.circuit,'signed_tableau':op.tab}
  if f==2:out['quadratic_residual']=serial(residual)
  result.append(out)
 # Explicit inverse-reader failure: adding J² to span(I,J) raises rank at f=2.
 need(result[1]['span_rank_I_J_J2']==3,'two raw/response readers cannot deliver inverse at f2')
 return {'base_matrix':serial(J),'fixtures':result,'scope':'exact f=1,2,3,4 tensor family; written trace gate covers arbitrary Gaussian-rational Cliffords','no_complete_caller_constructed':True,'no_new_kappa':True}

if __name__=='__main__':
 out=run();dest='CUBIC.json'if __debug__ else'CUBIC-OPTIMIZED.json';(HERE/dest).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'pass':True,'fixtures':[{k:v for k,v in f.items()if k in('f','native_B_rank','symplectic_defect_rank','quadratic_relation','span_rank_I_J_J2','trace')}for f in out['fixtures']],'no_new_kappa':True},sort_keys=True))
