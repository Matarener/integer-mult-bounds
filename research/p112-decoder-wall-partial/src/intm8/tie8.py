# M=8 piece decoder: a genuine 2-level atom gives two DISJOINT nonempty supports X1=R1\R2, X2=R2 of P-functionals.
# Each must (a) meet every frame (P_F invertible), (b) be co-closed: t in X, F not containing t => X meets w_F(t)  (R1).
# CNF: a_t (t in X1), b_t (t in X2).  UNSAT => no multi-level atom in any 8-piece decoder.
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
RULES=[set() for t in range(n)]
for F in FRM:
    for t in range(n):
        if F>>t&1: continue
        w=F&~ROW[t]; assert bin(w).count('1')==4; RULES[t].add(w)
bits=lambda m:[i for i in range(n) if m>>i&1]
a=lambda t:t+1; b=lambda t:n+t+1
cl=[]
for t in range(n): cl.append([-a(t),-b(t)])
for F in FRM:
    cl.append([a(f) for f in bits(F)]); cl.append([b(f) for f in bits(F)])
for t in range(n):
    for w in RULES[t]:
        cl.append([-a(t)]+[a(g) for g in bits(w)]); cl.append([-b(t)]+[b(g) for g in bits(w)])
import os
if os.environ.get('NEARMISS')=='1':
    # no extra zeros (R1-RIG / Theorem RK-type step 1): p_t has full support w_F(t) in F-coords, so t in Z => |w \ Z| != 1
    for t in range(n):
        for w in RULES[t]:
            ws=bits(w)
            for g in ws:
                o=[h for h in ws if h!=g]
                cl.append([a(t),-a(g)]+[a(h) for h in o]); cl.append([b(t),-b(g)]+[b(h) for h in o])
# symmetry breaking (sound): swap X1<->X2 ; line 0 not in X2  (if 0 in X2 swap; if 0 in neither keep)
cl.append([-b(0)])
out=sys.argv[1]
with open(out,'w') as f:
    f.write('p cnf %d %d\n'%(2*n,len(cl)))
    for c in cl: f.write(' '.join(map(str,c))+' 0\n')
print('vars',2*n,'clauses',len(cl),'rules/line',sorted(set(len(r) for r in RULES)))
