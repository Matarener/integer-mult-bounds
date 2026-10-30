"""Exact monomial column algebra; source K_G convention from native phase audit."""
from functools import lru_cache
from array import array
N=512
IDENTITY=array('H',(4*x for x in range(N))).tobytes()

def decode(value):
 a=array('H');a.frombytes(value);return a

def linear(columns,x):
 answer=0
 for j,c in enumerate(columns):
  if x>>j&1:answer^=c
 return answer

def inverse_columns(columns):
 pivots={}
 for j,value in enumerate(columns):
  coefficient=1<<j
  for pivot in sorted(pivots,reverse=True):
   if value>>pivot&1:value^=pivots[pivot][0];coefficient^=pivots[pivot][1]
  if not value:raise ValueError('singular native map')
  pivots[value.bit_length()-1]=value,coefficient
 result=[]
 for j in range(9):
  value,coefficient=1<<j,0
  for pivot in sorted(pivots,reverse=True):
   if value>>pivot&1:value^=pivots[pivot][0];coefficient^=pivots[pivot][1]
  if value:raise ValueError('inverse construction')
  result.append(coefficient)
 return result

def native(columns):
 # K_G|x>=i^q(Gx)|Gx>, Q=I+G^-T G^-1. Same retained PR2226 phase convention.
 inv=inverse_columns(columns)
 tr=[sum(((inv[j]>>i)&1)<<j for j in range(9)) for i in range(9)]
 quadratic=[(1<<j)^linear(tr,inv[j]) for j in range(9)]
 result=[]
 for x in range(N):
  y=linear(columns,x)
  phase=sum((quadratic[j]>>j&1)*(y>>j&1) for j in range(9))
  phase+=2*sum((quadratic[j]>>i&1)*(y>>i&1)*(y>>j&1) for i in range(9) for j in range(i+1,9))
  result.append(4*y+phase%4)
 return array('H',result).tobytes()

@lru_cache(None)
def multiply(left,right):
 l,r=decode(left),decode(right)
 return array('H',(4*(l[v//4]//4)+(l[v//4]%4+v%4)%4 for v in r)).tobytes()

@lru_cache(None)
def conjugate(op):
 return array('H',(4*(v//4)+(-v%4) for v in decode(op))).tobytes()

@lru_cache(None)
def inverse(op):
 a=decode(op);result=[0]*N
 for x,v in enumerate(a):result[v//4]=4*x+(-v%4)
 return array('H',result).tobytes()
