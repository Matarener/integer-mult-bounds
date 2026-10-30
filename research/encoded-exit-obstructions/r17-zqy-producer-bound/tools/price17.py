"""Exact-Decimal price of b purchases on the R16 model (16 backward FULLs; base T0+{9:128}, P0+{1:128})."""
import sys; sys.path.insert(0, str(__import__('pathlib').Path.home()/'imb-harness/r16/tools'))
from price16 import *
U = D('0.00302728825')
Tb, Pb = add(T0, {9: 128}), add(P0, {1: 128})
tau = M(Tb, Pb, U) / 16
print('break-even per backward FULL at C=U: purchase cost sum r^(1-U) <', tau)
for name, dp in [('b free', {}), ('63 H1', {1: 63}), ('64 H1', {1: 64}), ('112 H1 (lower bound, post-return)', {1: 112}),
                 ('8 H8 (pre-return y/h copy: D Z y, exit Q merged)', {8: 8}), ('8 H9 (R Z y)', {9: 8})]:
    cost = sum(c * pw(r, 1 - U) for r, c in dp.items())
    r = root(Tb, add(Pb, {k: 16 * v for k, v in dp.items()}))
    print(f'{name:52s} cost/FULL {float(cost):9.4f}  root {float(r):.13f}  beats U: {r > U}')
