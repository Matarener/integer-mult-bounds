"""tk sens WORD [--calls N] [--json]
kappa marginals of a word's exact invoice (P104CLEAN/sens.py generalised): how much kappa moves if every call (default 18) gets one more/fewer paid rank,
a merge of paid ranks, a credit hand-off split, ...  Pure arithmetic on the exact (T,P) tables (Decimal-free Newton, 1e-16): a model of the invoice, not a word."""
import json
from collections import Counter
from tkcommon import *
def kap(T,P):
    f=lambda k:sum(n*r**(1-k) for r,n in T.items())-sum(n*r**(1-k) for r,n in P.items())
    lo,hi=1e-5,0.02
    for _ in range(200):
        m=(lo+hi)/2
        if f(m)>0: lo=m
        else: hi=m
    return lo
def table(T,P,calls=18):
    b=kap(T,P)
    def mod(dT={},dP={}):
        T2=Counter(T);P2=Counter(P)
        for r,n in dT.items(): T2[r]+=n*calls
        for r,n in dP.items(): P2[r]+=n*calls
        return kap(T2,P2)-b
    rows=[('per call: remove one rank-1 paid',mod(dP={1:-1})),('remove rank-2 paid',mod(dP={2:-1})),
          ('merge 2 rank1 into 1 rank2 (paid)',mod(dP={1:-2,2:1})),('merge 3 r1 ->r3',mod(dP={1:-3,3:1})),
          ('merge r1xk -> rk, k=9',mod(dP={1:-9,9:1}))]
    for a in range(1,5): rows.append(('handoff %d+%d (T credit only)'%(a,9-a),mod(dT={a:1,9-a:1,9:-1})))
    rows+=[('split into 9 ones',mod(dT={1:9,9:-1})),('split 3x3',mod(dT={3:3,9:-1})),('extra rank-9 helper credit w/o pay',mod(dT={9:1}))]
    return b,rows
def main(a):
    path,w=load(a.word); rep=legal.check(w); T,P=X.invoice(rep)
    b,rows=table(T,P,a.calls)
    if a.json: print(json.dumps(dict(base=b,rows=rows),indent=1)); return 0
    print('base',b)
    for n,v in rows: print(n,v)
    return 0
