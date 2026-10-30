"""Exact Gaussian and recipe decoder adapted from Clear1nsight PR3989.
Apache-2.0; substantial OpenAI Codex assistance. No predecessor imports.
"""
from fractions import Fraction as F
from functools import lru_cache
ONE=(F(1),F(0)); ZERO=(F(0),F(0))
def require(ok,msg):
 if not ok: raise RuntimeError(msg)
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def div(a,b):
 d=b[0]*b[0]+b[1]*b[1]
 return mul(a,(b[0]/d,-b[1]/d))
def phase(a,p):return (a,(-a[1],a[0]),neg(a),(a[1],-a[0]))[p%4]
def clean(v):return {k:a for k,a in v.items() if a!=ZERO}
def plus(v,w):
 o=dict(v)
 for k,a in w.items():o[k]=add(o.get(k,ZERO),a)
 return clean(o)
def scaled(v,a):return clean({k:mul(a,b) for k,b in v.items()})
def mv(rows,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(rows))
@lru_cache(None)
def monomial_table(rows,quadratic,linear,offset,global_phase):
 n=len(rows);table=[]
 for x in range(1<<n):
  y=mv(rows,x)^offset
  p=global_phase+sum(linear[i] for i in range(n) if x>>i&1)
  p+=2*sum((quadratic[i] & x & ~((1<<(i+1))-1)).bit_count()%2 for i in range(n) if x>>i&1)
  table.append((y,p%4))
 require(len({y for y,p in table})==1<<n,'monomial is a permutation')
 return tuple(table)
def monomial(v,r,inverse=False):
 table=monomial_table(tuple(r['matrix_rows']),tuple(r['quadratic_rows']),tuple(r['linear_Z4']),r['offset'],r['phase'])
 if inverse:
  inv={y:(x,-p) for x,(y,p) in enumerate(table)}
  return {inv[y][0]:phase(a,inv[y][1]) for y,a in v.items()}
 return {table[x][0]:phase(a,table[x][1]) for x,a in v.items()}
def fourier(v,r,inverse=False):
 s=-1 if inverse else 1
 for j in range(r):
  o={}
  for x,a in v.items():
   for y,b in [(x,(F(1,2),F(s,2))),(x^(1<<j),(F(1,2),F(-s,2)))]:
    o[y]=add(o.get(y,ZERO),mul(a,b))
  v=clean(o)
 return v

def apply(v,r,inverse=False):
 if inverse:return monomial(fourier(monomial(v,r['left'],True),r['rank'],True),r['right'],True)
 return monomial(fourier(monomial(v,r['right']),r['rank']),r['left'])
