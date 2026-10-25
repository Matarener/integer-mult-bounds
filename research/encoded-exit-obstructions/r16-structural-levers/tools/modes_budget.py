"""Coupled-type size needed for a bought exit (each of the 112 supported ports needs its own H1, by
zqy_commute.py) to pay: m modes regain 16m rank-9 targets, cost 16(m + 112) H1 over 16 backward FULLs."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from price16 import *
U = D('0.00302728825')
for m in range(8, 20):
    r = root(add(T0, {9: 16*m}), add(P0, {1: 16*(m+112)}))
    print(m, f'{float(r):.10f}', r > U)
