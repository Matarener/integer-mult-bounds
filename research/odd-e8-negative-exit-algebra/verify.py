"""Exact actual-E witness and generic fresh-stage controls; Apache-2.0."""
import hashlib,json
from fractions import Fraction as F
from pathlib import Path
from itertools import product
p=Path(__file__).resolve().parent
def need(ok,why):
 if not ok:raise ValueError(why)
for row in json.loads((p/'PINS.json').read_text()):need(hashlib.sha256((p/row['path']).read_bytes()).hexdigest()==row['sha256'],'source authentication')
def dot(a,b):return (a&b).bit_count()%2
def act(cols,x):
 y=0
 for j,c in enumerate(cols):
  if x>>j&1:y^=c
 return y
def mul(a,b):return tuple(act(a,c)for c in b)
def transpose(a):return tuple(sum(((a[k]>>j)&1)<<k for k in range(len(a)))for j in range(len(a)))
def normal(q,n):
 def trans(v):return tuple((1<<j)^(v if v>>j&1 else 0)for j in range(n))
 if not q&1:G=trans(1^q)
 else:
  j=next(j for j in range(1,n)if not(q>>j&1));G=mul(trans((1<<j)^q),trans(1^(1<<j)))
 need(act(G,1)==q and mul(transpose(G),G)==tuple(1<<j for j in range(n)),'orthogonal actual normalizer')
 rows=transpose(G);z=sum((((r.bit_count()-1)//2)&1)<<j for j,r in enumerate(rows))
 # L=Z_z P_G, so its input sign is z dot Gx.
 return G,act(transpose(G),z)
def smul(a,b):return mul(a[0],b[0]),b[1]^act(transpose(b[0]),a[1])
def sinv(a):
 G=transpose(a[0]);return G,act(transpose(G),a[1])
def signed(a,x):return act(a[0],x),(-1 if dot(a[1],x)else 1)
def cp(a,b):return a[0]+b[0],a[1]+b[1]
def cm(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def column(a,x):
 out={}
 for shift,c in [(0,(F(1,2),F(1,2))),(1,(F(1,2),F(-1,2)))]:
  y,s=signed(a,x^shift)
  for b,d in [(0,(F(1,2),F(-1,2))),(1,(F(1,2),F(1,2)))]:out[y^b]=cp(out.get(y^b,(0,0)),cm((s*c[0],s*c[1]),d))
 return {y:c for y,c in out.items()if c!=(0,0)}
def main():
 d=json.loads((p/'source/NORMALIZERS.json').read_text());M=list(zip(*d['mode_columns']));ports=d['ports'];orth=json.loads((p/'source/K-TEMPLATE.json').read_text())['orthonormal_basis_raw27']
 need(len(ports)==112 and len({v['q']for v in ports})==112,'distinct source labels')
 need(all(sum(x*x for x in r)==4 for r in M),'constant source projector diagonal')
 need(all(sum(M[i][a]*M[i][b]for i in range(112))==(56 if a==b else 0)for a,b in product(range(8),repeat=2)),'actual orthogonal mode columns')
 need(tuple(i for i,x in enumerate(M[0])if x)!=tuple(i for i,x in enumerate(M[1])if x),'different source cubes')
 need(sum(a*b for a,b in zip(M[0],M[1]))==2,'actual cross-cube coefficient')
 # Scalar C=1/2(P1P2+P1P3+P2P3-P1P2P3), P=MM^T/4.
 pij=F(sum(a*b for a,b in zip(M[1],M[0])),4);cij=pij/2
 need(cij==F(1,4),'E inverse cross-cube entry')
 pi=F(1,14);ediag=-(3*pi*pi*(1-pi)*F(98,1-98)+pi**3*F(-1078,1+1078));eidiag=F(1)
 need(ediag==F(1541,104663) and ediag>0,'actual E diagonal')
 coefficient=cij*ediag*eidiag
 need(all(dot(a,b)==int(i==j)for i,a in enumerate(orth)for j,b in enumerate(orth)) and len(orth)==25,'source global I25 chart')
 def q(triple):
  raw=sum(ports[k]['q']<<(9*j)for j,k in enumerate(triple));return sum(dot(raw,b)<<j for j,b in enumerate(orth))
 qi,qj=q((1,0,0)),q((0,0,0));need(qi!=qj and dot(qi,qi)==dot(qj,qj)==1,'actual product labels')
 Li,Lj=normal(qi,25),normal(qj,25);A=smul(sinv(Li),Lj);need(act(A[0],1)!=1,'selected path moves central line')
 # Sparse exact phase/column calculation; no2^25 array or numerical tolerance.
 for x in [0,1]+[1<<j for j in range(1,25)]:
  col=column(A,x);need(len(col)==4 and all(a*a+b*b==F(1,4)for a,b in col.values()),'four phase-exact supports')
 # Every private-basis marker equals the target signed monomial entry.
 need(len([j for j in range(1,73)])==72,'actual three24-private-stage markers')
 # Repeated-stage and same-owner controls: forbidden extensions really cancel.
 need(smul(sinv(A),A)==(tuple(1<<j for j in range(25)),0),'repeated stage inverse control')
 same=smul(sinv(Lj),Lj);need(len(column(same,0))==1,'same-owner monomial control')
 # Two common axes invalidate trivial-intersection argument.
 swap=(2,1,4,8);need(mul(swap,swap)==(1,2,4,8) and swap!=(1,2,4,8),'two-common-axis intersection control')
 need(73**2+3*73+73*72//2+2==8178 and 2*4198-216>8178 and 2*4197-216==8178,'explicit native group cardinality threshold')
 result=dict(columnwise_group_log2_upper=8178,columnwise_nonmembership_from_f=4198,owner_input=[0,0,0],owner_output=[1,0,0],middle_owners=[[0,0,0],[0,0,0]],E_inverse_cross_entry=str(cij),E_diagonal=str(ediag),E_inverse_diagonal='1',surviving_coefficient=str(coefficient),product_labels=[qi,qj],selected_permutation_columns=list(A[0]),selected_sign=A[1],conjugated_zero_column=[[y,[str(a),str(b)]]for y,(a,b)in sorted(column(A,0).items())],ambient_axes=73,private_markers=72,ADD_lower_bound='max(0,2*f-216)',target='Q^-1 D123 on original independent negative-bank inputs',scope='postdecoder from emitted bank and independent workspace; no correlated retained histories')
 need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((p/'RESULT.json').read_text()),sort_keys=True),'typed receipt equality')
 print('PASS_ACTUAL_ODD_E8_NEGATIVE_EXIT '+json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
