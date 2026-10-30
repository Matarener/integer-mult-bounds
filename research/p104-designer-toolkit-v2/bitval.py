import os
"""bitval: exact BIT value of a (paid, targets) invoice.  [BITADAPT]
raw crossing kappa*:  sum_r T_r r^(1-k) = sum_r P_r r^(1-k)   (mpmath, 50 digits)
admitted(tested): the PR #5512 ordinary.py finite-level chain (uniform=tested-1e-8, C1=uniform-cover_gap, 3 levels rho=1/100, floor 1e-12).
global invoice of a local word:  P = OUTER + CALLS*localpaid,  T = T0 - ... (see bitstack)."""
import sys
from fractions import Fraction as F
from mpmath import mp,mpf,findroot,log
mp.dps=50
CALLS=18
def f(k,T,P):
    t=1-k; return sum(c*mpf(r)**t for r,c in T.items())-sum(c*mpf(r)**t for r,c in P.items())
def crossing(T,P,lo=mpf('0.0001'),hi=mpf('0.02')):
    a,b=lo,hi; fa=f(a,T,P)
    for _ in range(170):
        m=(a+b)/2; fm=f(m,T,P)
        if (fm>0)==(fa>0): a,fa=m,fm
        else: b=m
    return (a+b)/2
def admitted(tested,backend0=F(1737729,500000000),rho=F(1,100)):
    """tested: Fraction (the PR uses floor to 1e-8); returns the 3-level admitted value as Fraction"""
    uniform=tested-F(1,10**8); cover_gap=F(1,2**36)+F(1,10**20); C1=uniform-cover_gap; backend=backend0
    for j in range(3):
        a=(1-rho)*C1+rho*backend; b=F((a*10**12).__floor__(),10**12); backend=b
    return backend
def tested_of(kappa,q=8):
    return F(int(mpf(kappa)*10**q),10**q)
def adm(kappa,q=8): return admitted(tested_of(kappa,q))
def from_pr_invoice(inv):
    return {int(k):v for k,v in inv['targets'].items()},{int(k):v for k,v in inv['paid'].items()}
if __name__=='__main__':
    import json
    inv=json.load(open(sys.argv[1] if len(sys.argv)>1 else os.path.dirname(os.path.abspath(__file__)) + '/ext/BITADAPT/pkg/research/bit-g20-nine-owned-relations/INVOICE.json'))
    T,P=from_pr_invoice(inv); k=crossing(T,P); print('raw crossing',mp.nstr(k,20)); a=adm(k); print('admitted',a,float(a),a==F(435496247,125*10**9))
