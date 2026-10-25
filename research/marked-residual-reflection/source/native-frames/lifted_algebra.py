"""Exact all-f tensor algebra with one distinguished Pauli-controlled coordinate.
Apache-2.0; substantial OpenAI Codex assistance. No finite-f extrapolation.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from native_model import *
@dataclass(frozen=True)
class G:
 a:F=F(0);b:F=F(0)
 def __add__(s,t):
  if not isinstance(t,G):t=G(F(t))
  return G(s.a+t.a,s.b+t.b)
 def __neg__(s):return G(-s.a,-s.b)
 def __sub__(s,t):return s+-t
 def __mul__(s,t):
  if not isinstance(t,G):t=G(F(t))
  return G(s.a*t.a-s.b*t.b,s.a*t.b+s.b*t.a)
 def conj(s):return G(s.a,-s.b)
 def __truediv__(s,t):
  if not isinstance(t,G):t=G(F(t))
  d=t.a*t.a+t.b*t.b;need(bool(d),'nonzero Gaussian divisor');return s*t.conj()*G(1/d)
 def __bool__(s):return bool(s.a or s.b)
 def encode(s):return[str(s.a),str(s.b)]
ZERO=G();ONE=G(F(1));I=G(F(0),F(1));UNITS=(ONE,I,-ONE,-I)
def phasevec(q):return tuple(UNITS[(q if isinstance(q,int)else q(r))%4]for r in range(4))
def cadd(a,c):return tuple(x+y for x,y in zip(a,c))
def cmul(a,c):return tuple(x*y for x,y in zip(a,c))
def cconj(a):return tuple(x.conj()for x in a)
def czero(a):return not any(a)
class Algebra:
 def __init__(self,stages=4):
  self.stages=stages;self.m=2+2*stages;self.rep={};self.products={};self.inverses={};self.phase_cache={};self.model=Model(1,stages);self.idkey=self.canonical(ce.ident(self.m))[0]
  self.one={(self.idkey,self.idkey):(ONE,)*4};self.N=self.lift(self.model.N,exponent=1);self.U=self.lift(self.model.U);self.V=self.product(self.N,self.adjoint(self.U));self.P=[self.lift(x)for x in self.model.P];self.T=[self.lift(x,exponent=1)for x in self.model.T];self.Q=[]
  for s in range(stages+1):self.Q.append(self.lift(ce.xgate(self.m,1<<(2*s)),ce.ident(self.m)))
 def canonical(self,op):
  key=op.tab
  # Same signed tableau means the representative differs by exactly a Gaussian unit.
  state,depth=b.sparse_column(op);first=state[min(state)];q=None
  for j in range(4):
   a,c=b.gaussian_unit(first,-j)
   if a>0 and c>=0:q=j;break
  need(q is not None,'canonical Gaussian amplitude phase')
  if key not in self.rep:self.rep[key]=op.then(phase(op.n,-q))
  return key,q
 def multiply_keys(self,a,c):
  if(a,c)not in self.products:self.products[(a,c)]=self.canonical(mul(self.rep[a],self.rep[c]))
  return self.products[(a,c)]
 def adjoint_key(self,a):
  if a not in self.inverses:self.inverses[a]=self.canonical(self.rep[a].adjoint())
  return self.inverses[a]
 def lift(self,dist,bulk=None,exponent=0):
  if bulk is None:bulk=dist
  kd,qd=self.canonical(dist);kb,qb=self.canonical(bulk)
  need(b.binary_tableau(dist)==b.binary_tableau(bulk),'distinguished difference must be Pauli only')
  return{(kd,kb):phasevec(lambda r:exponent*(1-r)+qd+qb*(r-1))}
 def add(self,a,c):
  out=dict(a)
  for k,v in c.items():
   w=cadd(out.get(k,(ZERO,)*4),v)
   if czero(w):out.pop(k,None)
   else:out[k]=w
  return out
 def scale(self,a,c):
  if not isinstance(c,G):c=G(F(c))
  return{k:tuple(c*x for x in v)for k,v in a.items()if c}
 def product(self,a,c):
  out={}
  for(ad,ab),av in a.items():
   for(cd,cb),cv in c.items():
    kd,qd=self.multiply_keys(ad,cd);kb,qb=self.multiply_keys(ab,cb);phase=phasevec(lambda r:qd+qb*(r-1));value=cmul(cmul(av,cv),phase);key=(kd,kb);value=cadd(out.get(key,(ZERO,)*4),value)
    if czero(value):out.pop(key,None)
    else:out[key]=value
  return out
 def adjoint(self,a):
  out={}
  for(ad,ab),av in a.items():
   kd,qd=self.adjoint_key(ad);kb,qb=self.adjoint_key(ab);value=cmul(cconj(av),phasevec(lambda r:qd+qb*(r-1)));out=self.add(out,{(kd,kb):value})
  return out
 def mat_identity(self,n):return[[dict(self.one)if i==j else{}for j in range(n)]for i in range(n)]
 def mat_product(self,a,c):
  n=len(a);out=[[{}for j in range(n)]for i in range(n)]
  for i in range(n):
   for k in range(n):
    if not a[i][k]:continue
    for j in range(n):
     if c[k][j]:out[i][j]=self.add(out[i][j],self.product(a[i][k],c[k][j]))
  return out
 def router(self,n,a,c,selector=0,sign=1):
  out=self.mat_identity(n);Q=self.scale(self.Q[selector],sign);ep=self.scale(self.add(self.one,Q),F(1,2));em=self.scale(self.add(self.one,self.scale(Q,-1)),F(1,2));out[a][a]=out[c][c]=ep;out[a][c]=out[c][a]=em;return out
 def diagonal(self,n,bank,op):out=self.mat_identity(n);out[bank][bank]=op;return out
 def continuation(self,choice):
  if choice=='U':return self.U
  if choice=='V':return self.V
  # alpha_f=(-i)^(f+1), selected completed fresh1 p-bit. Conditional
  # continuation is directly admitted by the R diag(U,I) R word.
  need(choice in('C+','C-'),'known role')
  Q=self.Q[1];ep=self.scale(self.add(self.one,Q),F(1,2));em=self.scale(self.add(self.one,self.scale(Q,-1)),F(1,2));alpha=phasevec(lambda r:-r-1);av={k:cmul(v,alpha)for k,v in self.V.items()}
  return self.add(self.product(ep if choice=='C+'else em,self.U),self.product(em if choice=='C+'else ep,av))
 def box(self,n,stage,kind,target,source,role='U',c=1,target_P=False):
  out=self.mat_identity(n);W=self.continuation(role);P=self.P[stage]
  if kind=='F':out[source][source]=self.product(W,P);out[target][source]=self.scale(self.N,c)
  elif kind=='G':
   Wi=self.adjoint(W);out[source][source]=Wi;out[target][target]=P;out[target][source]=self.scale(self.product(self.product(P,self.N),Wi),c)
  else:raise ValueError(kind)
  if target_P:
   need(kind=='F','only forward postdelivery/pre-T target P admitted')
   out=self.mat_product(self.diagonal(n,target,P),out)
  return out
 def allf_target_residual(self,a):
  # Right-normalize the desired full native common N. A positive result
  # has entries in the fixed distinguished Pauli algebra, bulk identity.
  Ni=self.adjoint(self.N);res=[]
  for row in a:
   rr=[]
   for entry in row:
    v=self.product(entry,Ni)
    if any(kb!=self.idkey for kd,kb in v):return None
    if any(b.binary_tableau(self.rep[kd])!=b.binary_tableau(ce.ident(self.m))for kd,kb in v):return None
    rr.append(v)
   res.append(rr)
  return res
 def fingerprint(self,a):
  return tuple(tuple(tuple(sorted((str(k),tuple((v.a,v.b)for v in vec))for k,vec in entry.items()))for entry in row)for row in a)
