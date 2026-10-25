"""R16 float/Decimal pricer for the selected #5413 profile and structural lever screens.
M(C) = sum_T n k^(1-C) - sum_P n r^(1-C). Numerical screens only (no outward rounding)."""
from decimal import Decimal as D, getcontext
import json, sys
getcontext().prec = 50
P0 = {1:41154,2:7416,3:9180,4:2286,5:720,8:144,16:448,24:448,32:448,40:448,48:448,56:448,64:448,72:224}
T0 = {4:504,7:126,8:990,9:5724,17:448,25:448,33:448,41:448,49:448,57:448,65:448,73:224,145:224}
def pw(x, e): return (D(x).ln()*e).exp()
def M(T, P, C):
    e = 1-D(C)
    return sum(n*pw(k,e) for k,n in T.items() if n) - sum(n*pw(r,e) for r,n in P.items() if n)
def root(T=T0, P=P0, lo='0', hi='0.05'):
    lo, hi = D(lo), D(hi)
    if M(T,P,lo) <= 0: return D(0)
    while M(T,P,hi) > 0: hi *= 2
    for _ in range(80):
        m = (lo+hi)/2
        if M(T,P,m) > 0: lo = m
        else: hi = m
    return lo
def add(h, d):
    h = dict(h)
    for k, v in d.items(): h[k] = h.get(k,0)+v
    return h
if __name__ == '__main__':
    r = root(); print('selected root', r)
    eps = D('1e-12'); print('dM/dC', (M(T0,P0,r+eps)-M(T0,P0,r-eps))/(2*eps))
    print('mass surplus', sum(k*n for k,n in T0.items())-sum(k*n for k,n in P0.items()))
