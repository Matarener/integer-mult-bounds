"""Exact Clifford state/absolute-phase oracle using polynomial storage.

No dense state, floating arithmetic or owner coefficients are used.
P/D/X/phase/C literals have the conventions of the pinned exact compiler.
"""
from hashlib import sha256
from fractions import Fraction as F
from functools import lru_cache
import json
def need(ok,why):
 if not ok:raise ValueError(why)
def parity(x):return x.bit_count()&1
def mv(rows,x):return sum(parity(row&x)<<j for j,row in enumerate(rows))
def transpose(rows,n):return tuple(sum(((rows[j]>>i)&1)<<j for j in range(n))for i in range(n))
@lru_cache(None)
def inverse_rows(rows):
 n=len(rows);a=[x|(1<<(n+j))for j,x in enumerate(rows)]
 for j in range(n):
  p=next((i for i in range(j,n)if a[i]>>j&1),None);need(p is not None,'invertible P');a[p],a[j]=a[j],a[p]
  for i in range(n):
   if i!=j and a[i]>>j&1:a[i]^=a[j]
 return tuple(x>>n for x in a)
def mul_i(a,b,p):return[(a,b),(-b,a),(-a,-b),(b,-a)][p%4]
def qvalue(alpha,S,x):
 value=0
 while x:
  bit=x&-x;j=bit.bit_length()-1;x^=bit;value+=alpha[j]+2*parity(S[j]&x)
 return value%4
def support_map(B,x):
 out=0
 while x:
  bit=x&-x;out^=B[bit.bit_length()-1];x^=bit
 return out
def echelon(B):
 piv={}
 for j,col in enumerate(B):
  x=col;word=1<<j
  while x:
   k=x.bit_length()-1
   if k not in piv:piv[k]=(x,word);break
   a,b=piv[k];x^=a;word^=b
  need(bool(x),'independent affine support columns')
 return piv
def coordinates(piv,x):
 word=0
 while x:
  k=x.bit_length()-1
  if k not in piv:return None
  a,b=piv[k];x^=a;word^=b
 return word
def pullback(alpha,S,base,cols):
 """q(base+cols*z)=constant+alpha_new*z+2*beta_new quadratic."""
 const=qvalue(alpha,S,base);products=[mv(S,c)for c in cols]
 newalpha=[(qvalue(alpha,S,c)+2*parity(base&v))%4 for c,v in zip(cols,products)]
 newS=[sum(parity(c&v)<<j for j,v in enumerate(products))for c in cols]
 return const,newalpha,newS
class State:
 """psi(b+B*y)=(ar+i*ai)/2^den * i^q(y), independent columns B."""
 def __init__(self,n,basis=0):
  need(isinstance(n,int)and isinstance(basis,int)and n>=0 and 0<=basis<1<<n,'basis input');self.n=n;self.b=basis;self.B=[];self.alpha=[];self.S=[];self.ar=1;self.ai=0;self.den=0;self.stats={'C_raise':0,'C_same':0,'C_drop':0,'gates':0};self.peak_rank=0
 @property
 def rank(self):return len(self.B)
 def scalar(self,a,b,den=0):
  self.ar,self.ai=self.ar*a-self.ai*b,self.ar*b+self.ai*a;self.den+=den
  while self.den and not(self.ar&1)and not(self.ai&1):self.ar//=2;self.ai//=2;self.den-=1
 def phase(self,p):self.ar,self.ai=mul_i(self.ar,self.ai,p)
 def validate(self):
  r=self.rank;need(len(self.alpha)==len(self.S)==r and r<=self.n,'phase/support dimensions');need(all(0<=a<4 for a in self.alpha),'Z4 phase coefficients')
  need(0<=self.b<1<<self.n and all(0<=b<1<<self.n for b in self.B),'physical affine masks');echelon(self.B);need(all(0<=row<1<<r for row in self.S),'phase matrix masks')
  need(all(((self.S[i]>>i)&1)==self.alpha[i]%2 for i in range(r)),'quadratic diagonal equals linear parity')
  need(all(((self.S[i]>>j)&1)==((self.S[j]>>i)&1)for i in range(r)for j in range(i)),'symmetric binary quadratic form')
  need((self.ar*self.ar+self.ai*self.ai)*(1<<r)==1<<(2*self.den),'exact unit norm from support dimension')
 def apply(self,e):
  kind=e[0];self.stats['gates']+=1
  if kind=='P':
   rows=e[1];need(len(rows)==self.n and all(isinstance(x,int)and 0<=x<1<<self.n for x in rows),'P dimension and masks');need(len(echelon(rows))==self.n,'invertible P');self.b=mv(rows,self.b);self.B=[mv(rows,c)for c in self.B]
  elif kind=='X':need(isinstance(e[1],int)and 0<=e[1]<1<<self.n,'X mask');self.b^=e[1]
  elif kind=='phase':need(isinstance(e[1],int),'integer phase');self.phase(e[1])
  elif kind=='D':
   S=list(e[1]);alpha=list(e[2]);need(len(S)==len(alpha)==self.n and all(isinstance(x,int)and 0<=x<1<<self.n for x in S)and all(isinstance(a,int)for a in alpha),'D dimension and masks');need(all(((S[i]>>j)&1)==((S[j]>>i)&1)for i in range(self.n)for j in range(i))and all(alpha[i]%2==((S[i]>>i)&1)for i in range(self.n)),'Clifford diagonal polynomial')
   const,a,T=pullback(alpha,S,self.b,self.B);self.phase(const);self.alpha=[(x+y)%4 for x,y in zip(self.alpha,a)];self.S=[x^y for x,y in zip(self.S,T)]
  else:
   need(kind=='C'and isinstance(e[2],int)and e[2]in[-1,1]and isinstance(e[1],int)and 0<=e[1]<1<<self.n,'known C primitive');q,s=e[1:];r=self.rank;v=coordinates(echelon(self.B),q)
   if v is None:
    self.scalar(1,s,1);self.B.append(q);self.alpha.append((-s)%4);self.S.append(1<<r);self.stats['C_raise']+=1
   else:
    delta=qvalue(self.alpha,self.S,v);h=mv(self.S,v);need(parity(h&v)==delta%2,'quadratic derivative parity')
    if not(delta&1):
     k=delta//2;t=s*(1-2*k);self.phase(s*k);self.alpha=[(a+t*((h>>j)&1))%4 for j,a in enumerate(self.alpha)];self.S=[row^(h if h>>j&1 else 0)for j,row in enumerate(self.S)];self.stats['C_same']+=1
    else:
     need(h!=0,'odd derivative has nonzero support constraint');eta=((s-delta)//2)%2;p=(h&-h).bit_length()-1;y0=(1<<p)if eta else 0;cols=[(1<<j)^((1<<p)if h>>j&1 else 0)for j in range(r)if j!=p];const,a,T=pullback(self.alpha,self.S,y0,cols)
     self.b^=support_map(self.B,y0);self.B=[support_map(self.B,c)for c in cols];self.alpha=a;self.S=T;self.phase(const);self.scalar(1,s);self.stats['C_drop']+=1
  self.peak_rank=max(self.peak_rank,self.rank);self.validate();return self
 def amplitude(self,x):
  need(0<=x<1<<self.n,'output basis address');v=coordinates(echelon(self.B),x^self.b)
  if v is None:return(0,0),0
  return mul_i(self.ar,self.ai,qvalue(self.alpha,self.S,v)),self.den
 def anchor(self):
  piv=echelon(self.B);x=self.b;y=0
  for k in sorted(piv,reverse=True):
   if x>>k&1:a,b=piv[k];x^=a;y^=b
  a,b=mul_i(self.ar,self.ai,qvalue(self.alpha,self.S,y));r=self.rank;t=F(1,1<<((r+1)//2));alpha=(t,t if r&1 else F());actual=(F(a,1<<self.den),F(b,1<<self.den));choices=[alpha,(-alpha[1],alpha[0]),(-alpha[0],-alpha[1]),(alpha[1],-alpha[0])];need(actual in choices,'actual dyadic Clifford anchor has mu4 phase relative to alpha_r')
  return{'axis_dimension':self.n,'rank':r,'first_nonzero_basis':x,'numerator':[a,b],'denominator_exponent':self.den,'mu4_phase':choices.index(actual),'peak_rank':self.peak_rank,'branch_counts':dict(self.stats)}
 def representation(self):return{'n':self.n,'affine_base':self.b,'independent_support_columns':list(self.B),'linear_Z4':list(self.alpha),'binary_symmetric_rows':list(self.S),'Gaussian_numerator':[self.ar,self.ai],'denominator_exponent':self.den}
def state(op_or_word,n=None,basis=0):
 if hasattr(op_or_word,'circuit'):n=op_or_word.n;word=op_or_word.circuit
 else:need(n is not None,'dimension required for a literal word');word=op_or_word
 out=State(n,basis)
 for e in word:out.apply(e)
 return out
def anchor(op_or_word,n=None,basis=0):return state(op_or_word,n,basis).anchor()
def tableau_from_word(word,n):
 """Independent literal Heisenberg replay, including exact Pauli signs."""
 tab=[(1<<j,0,0)for j in range(n)]+[(0,1<<j,0)for j in range(n)]
 for e in word:
  k=e[0]
  if k=='P':G=tuple(e[1]);GiT=transpose(inverse_rows(G),n);tab=[(mv(G,x),mv(GiT,z),p)for x,z,p in tab]
  elif k=='X':tab=[(x,z,(p+2*parity(e[1]&z))%4)for x,z,p in tab]
  elif k=='phase':continue
  elif k=='D':S,a=e[1:];tab=[(x,z^mv(S,x),(p+qvalue(a,S,x))%4)for x,z,p in tab]
  else:need(k=='C','known tableau primitive');q,s=e[1:];tab=[(x^q,z,(p+3*s)%4)if parity(q&z)else(x,z,p)for x,z,p in tab]
 return tuple(tab)
def canonicalize(op,verify_tableau=True):
 if verify_tableau:need(tableau_from_word(op.circuit,op.n)==tuple(tuple(x)for x in op.tab),'provided signed tableau agrees with literal circuit')
 a=anchor(op);key=sha256((json.dumps({'n':op.n,'signed_tableau':op.tab},sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest();return key,a['mu4_phase']
