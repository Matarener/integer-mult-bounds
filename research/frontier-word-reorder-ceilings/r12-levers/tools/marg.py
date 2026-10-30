import sys; sys.path.insert(0,str(__import__('pathlib').Path.home()/'imb-harness/r12/tools'))
from moment import *
import math
H,N,T,P,word=invoice()
C=root(T,P)
f=lambda x:x**(1-C)
print('surplus',sum(k*n for k,n in T.items())-sum(r*n for r,n in P.items()))
dM=sum(-n*k**(1-C)*math.log(k) for k,n in T.items())+sum(n*r**(1-C)*math.log(r) for r,n in P.items())
print('C*',C,'dM/dC',dM)
def dC(dm): return -dm/dM
# per-local (x18) moves
for name,dm in [('helper 4->9 alone',18*(f(9)-f(4))),('one paid rank1 removed',18*f(1)),
  ('helper+1 rank 9',18*f(9)),('paid 4+4->3+5',18*(2*f(4)-f(3)-f(5))),('paid 2->1+1',18*(f(2)-2*f(1))),('helper 8->9',18*(f(9)-f(8))),('helper 9 -> 4+5', 18*(f(4)+f(5)-f(9)))]:
    print(f'{name:30s} dM={dm:.6g} dC={dC(dm):.4e}')
print('frontier gap to beat (0.0030217758):', 0.0030217758-C)
