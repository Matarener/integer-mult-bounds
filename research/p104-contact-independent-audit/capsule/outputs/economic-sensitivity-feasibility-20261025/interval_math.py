"""Reused F4 rational interval engine; algorithm is not independently reimplemented."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import hashlib,json,sys
B=Path(__file__).resolve().parent
P=B/'capsule-f4/invoice.json'
def require(c,m):
 if not c: raise ValueError(m)
def ln_unit(u):
 z=(u-1)/(u+1); require(0<=z<=F(1,3),'log domain')
 n=24; s=2*sum((z**(2*j+1)/F(2*j+1) for j in range(n)),F(0))
 tail=2*z**(2*n+1)/(F(2*n+1)*(1-z*z))
 return s,s+tail
L2=ln_unit(F(2))
def ln_rank(r):
 k=r.bit_length()-1; a,b=ln_unit(F(r,2**k))
 return a+k*L2[0],b+k*L2[1]
def exp_minus(x):
 require(0<=x<1,'alternating exponential domain')
 s=F(1); term=F(1); low=high=None
 for k in range(1,13):
  term*= -x/k; s+=term
  if k==11: low=s
  if k==12: high=s
 return low,high
def power(r,c):
 if c==0 or r==1: return F(r),F(r)
 a,b=ln_rank(r)
 return r*exp_minus(c*b)[0],r*exp_minus(c*a)[1]
def moment(h,c):
 values={int(r):power(int(r),c) for side in h.values() for r in side}
 low=high=F(0)
 for side,sign in [('productive',1),('paid',-1)]:
  for r,n in h[side].items():
   a,b=values[int(r)]
   low+=n*(a if sign==1 else -b);high+=n*(b if sign==1 else -a)
 return low,high
def dec(x,rounding):
 with localcontext() as ctx:
  ctx.prec=24;ctx.rounding=rounding
  return str(Decimal(x.numerator)/Decimal(x.denominator))
def interval(a,b):
 return {'lower_decimal_outward':dec(a,'ROUND_FLOOR'),'upper_decimal_outward':dec(b,'ROUND_CEILING')}
def ceil(x): return -(-x.numerator//x.denominator)
