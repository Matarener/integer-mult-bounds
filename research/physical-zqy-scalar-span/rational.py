"""Exact rational echelon rank; assertions are not used as checks."""
from fractions import Fraction as F
class ExactSpan:
 def __init__(self):self.piv={};self.max_num=0;self.max_den=0
 def add(self,v):
  v=dict(v)
  while v:
   k=min(v)
   if k not in self.piv:
    q=v[k];v={j:x/q for j,x in v.items()};self.piv[k]=v
    self.max_num=max(self.max_num,max(abs(x.numerator).bit_length() for x in v.values()));self.max_den=max(self.max_den,max(x.denominator.bit_length() for x in v.values()));return True
   q=v[k]
   for j,x in self.piv[k].items():
    z=v.get(j,F(0))-q*x
    if z:v[j]=z
    else:v.pop(j,None)
  return False
