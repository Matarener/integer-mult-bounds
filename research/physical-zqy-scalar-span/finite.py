"""Finite Gaussian-integer column certificates; no modular nonmembership shortcut.

A nonzero modular minor is used only as a rank LOWER bound. Rational span
UPPER bounds and an exact operator relation are supplied separately.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
import monomial as M

PRIME=998244353
IMAG=911660635

def need(ok,why):
 if not ok:raise ValueError(why)

class Span:
 def __init__(self):self.piv={}
 def add(self,v):
  v=dict(v)
  while v:
   k=min(v)
   if k not in self.piv:
    q=pow(v[k],PRIME-2,PRIME);self.piv[k]={j:x*q%PRIME for j,x in v.items()};return True
   q=v[k]
   for j,x in self.piv[k].items():
    z=(v.get(j,0)-q*x)%PRIME
    if z:v[j]=z
    else:v.pop(j,None)
  return False

RELATION={157:1,51:1,156:-1,49:-1}
SUBSTITUTION={157:{156:1,49:1,51:-1}}

def relation_zero(operators,relation):
 out={}
 for j,q in relation.items():
  for x,v in enumerate(M.decode(operators[j])):
   a,b=((q,0),(0,q),(-q,0),(0,-q))[v%4];k=x,v//4
   c,d=out.get(k,(0,0));c+=a;d+=b
   if c or d:out[k]=c,d
   else:out.pop(k,None)
 return not out

def operator_rank(operators):
 need(IMAG*IMAG%PRIME==PRIME-1,'Gaussian prime embedding')
 need(len(operators)==len(set(operators))==215,'literal operator inventory')
 need(relation_zero(operators,RELATION),'exact four-term physical relation')
 bad=list(operators);values=M.decode(bad[157]);values[0]^=1;bad[157]=values.tobytes()
 need(not relation_zero(bad,RELATION),'wrong absolute phase must break relation')
 s=Span()
 for op in operators:s.add({x*512+a//4:pow(IMAG,a%4,PRIME) for x,a in enumerate(M.decode(op))})
 need(len(s.piv)==214,'width-one independent 214-minor')
 return {'operators':215,'width_one_exact_rank':214,'rank_lower_prime':PRIME,'sqrt_minus_one':IMAG,'exact_relation':{str(k):v for k,v in RELATION.items()},'wrong_phase_control':True}

def physical_projection_rank(versions):
 index={};classes={};vspan=Span();projection=Span()
 for row in versions:
  v={}
  for (role,op),q in row.items():
   q=q.numerator*pow(q.denominator,PRIME-2,PRIME)%PRIME
   for j,a in SUBSTITUTION.get(op,{op:1}).items():
    key=role,j;k=index.setdefault(key,len(index));classes[k]=(role[0]=='L' and 112<=role[1]<224);z=(v.get(k,0)+q*a)%PRIME
    if z:v[k]=z
    else:v.pop(k,None)
  vspan.add(v)
  projection.add({k:q for k,q in v.items() if not classes[k]})
 # Coordinate injection is an actual pure-y operator, with the identity map.
 k=index.setdefault((('L',112),0),len(index));before=len(vspan.piv)
 need(vspan.add({k:1}),'physical pure-y positive control')
 return {'rank_lower_V':before,'rank_lower_non_Y_projection':len(projection.piv),'positive_control_rank':len(vspan.piv)}

def matrix_rank_det(rows,prime):
 a=[r[:] for r in rows];n=len(a);r=0;det=1
 for c in range(n):
  pivot=next((k for k in range(r,n) if a[k][c]),None)
  if pivot is None:continue
  if pivot!=r:a[pivot],a[r]=a[r],a[pivot];det=-det
  z=a[r][c];det=det*z%prime;q=pow(z,prime-2,prime);a[r]=[x*q%prime for x in a[r]]
  for k in range(r+1,n):
   z=a[k][c]
   if z:a[k]=[(x-z*y)%prime for x,y in zip(a[k],a[r])]
  r+=1
 return r,det%prime if r==n else 0

def tensor_square(operators):
 prime=1000000009;imag=569522298
 need(imag*imag%prime==prime-1,'second Gaussian prime embedding')
 ops=[M.decode(x) for x in operators];need(all(x[0]==0 for x in ops),'zero-vector phase anchor for every map')
 gram=[]
 for a in ops:
  row=[]
  for b in ops:
   re=im=0
   for x,y in zip(a,b):
    if x//4!=y//4:continue
    ph=(y-x)%4
    if ph==0:re+=1
    elif ph==1:im+=1
    elif ph==2:re-=1
    else:im-=1
   row.append(pow((re+imag*im)%prime,2,prime))
  gram.append(row)
 rank,det=matrix_rank_det(gram,prime)
 need(rank==215 and det==298401053,'tensor-square nonzero Gaussian-integer Gram determinant')
 return {'width':2,'rank':rank,'prime':prime,'sqrt_minus_one':imag,'determinant_mod_prime':det,'all_zero_anchors_one':True}
