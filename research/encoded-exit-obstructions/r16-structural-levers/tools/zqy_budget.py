"""Break-even H1 budget for buying the #5415 observation b=ZQY per backward FULL (16 applicable).
Supplied exit (#5415): +8 rank-9 targets and +8 H1 per FULL; purchase adds X more H1 per FULL."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from price16 import *
base = root(); U = D('0.00302728825')
for X in [0, 8, 16, 32, 48, 56, 60, 64, 72, 112]:
    T = add(T0, {9: 16*8}); P = add(P0, {1: 16*(8+X)})
    r = root(T, P); print(f'X={X:4d} H1/FULL  root {float(r):.10f} dC {float(r-base):+.3e}  beats U {r>U}')
lo, hi = 0, 200
while hi-lo > 1:
    m = (lo+hi)//2
    if root(add(T0,{9:128}), add(P0,{1:16*(8+m)})) > U: lo = m
    else: hi = m
print('largest integer X with root > U:', lo, 'H1 per backward FULL (vs 120 to buy full QY)')
