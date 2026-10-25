# m=8 test.  In an 8-term decoder, for every frame F: P_F invertible, Q_F = P_F^{-T}.  Hence (PROVED in NOTES):
#  (R1) for t not in F: P_t in span{P_g : g in F, g not orth t} (4 lines)  =>  zero sets Z_k={t: P_t[k]=0}, Z'_k={t:Q_t[k]=0} are R1-closed
#  (R2) sum_{f in F} P_f[k] Q_f[k] = 1  =>  R_k & A_k meets every frame.
# Test every maximal rectangle (R,A) of cost <= 7: Z=cl(L\R), Z'=cl(L\A); if L\(Z|Z') misses a frame, no sub-rectangle can be a term.
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from base import *
from collections import Counter
RS=pickle.load(open(HERE+'/rect2.pkl','rb'))
FULL=(1<<n)-1
# rules: (t, mask of the 4 non-orthogonal frame lines)
RULES=[set() for t in range(n)]
for F in FRM:
    for t in range(n):
        if F>>t&1: continue
        w=F&~ROW[t]          # frame lines not orthogonal to t (ROW includes t itself, t not in F)
        assert bin(w).count('1')==4
        RULES[t].add(w)
RULES=[sorted(r) for r in RULES]
print('distinct 4-set rules per line',Counter(len(r) for r in RULES))
def cl(Z):
    ch=True
    while ch:
        ch=False
        for t in range(n):
            if Z>>t&1: continue
            for w in RULES[t]:
                if w&Z==w: Z|=1<<t; ch=True; break
    return Z
if __name__=='__main__':
    surv=[]; stat=Counter()
    for o in RS:
        if o['c']>7: continue
        Z=cl(FULL&~o['R']); Zp=cl(FULL&~o['A'])
        D_=FULL&~(Z|Zp)
        ok=all(F&D_ for F in FRM)
        stat[(o['c'],ok)]+=1
        if ok: surv.append(o)
    print(sorted(stat.items()))
    print('cost<=7 maximal rectangles surviving R1+R2:',len(surv))
    pickle.dump(surv,open(HERE+'/m8surv.pkl','wb'))
