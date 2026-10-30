# Independent re-check (for L = P112 = E8 \ frame FR) of R1-RIG step 1: an 8-term decoder M = P Q^T (rank 8, M_tt = 1,
# M_ts = 0 for t orth s) has NO extra zero: M_ts != 0 for every non-orthogonal pair.  Own zero-pattern CNF.
# For any frame F in L: M[F,F] = I and rank 8 => M_us = sum_{g in w_F(u) & w_F(s)} M_ug M_gs (Schur complement 0).
# vars z(u,s) = [M_us = 0] (u != s non-orth); t(u,g,s) <-> ~z(u,g) & ~z(g,s).  Each clause is a necessary condition.
# usage: rigz.py out.cnf K seed [extra frame idx file]   (frames subset: sound, more frames = stronger)
import sys,os,random; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
out=sys.argv[1]; K=int(sys.argv[2]); seed=int(sys.argv[3])
rng=random.Random(seed); fidx=rng.sample(range(len(FRM)),K)
if len(sys.argv)>4: fidx+= [int(x) for x in open(sys.argv[4]).read().split()]
fidx=sorted(set(fidx))
orth=lambda u,s: u!=s and Bd[u,s]==1
nv=0; Z={}
def newv():
    global nv; nv+=1; return nv
for u in range(n):
    for s in range(n):
        if u!=s and Bd[u,s]==0: Z[(u,s)]=newv()
T={}; cl=[]
def tv(u,g,s):
    # literal "term (u,g,s) nonzero"; g in frame, u,s off frame; u==g or g==s impossible here
    if (u,g,s) in T: return T[(u,g,s)]
    v=newv(); T[(u,g,s)]=v; a=Z[(u,g)]; b=Z[(g,s)]
    cl.append([-v,-a]); cl.append([-v,-b]); cl.append([v,a,b]); return v
def exactly_one_forbidden(lits):
    if len(lits)==1: cl.append([-lits[0]])
    else:
        for i in range(len(lits)): cl.append([-lits[i]]+[lits[j] for j in range(len(lits)) if j!=i])
for fi in fidx:
    F=FRM[fi]; FL=[g for g in range(n) if F>>g&1]
    off=[u for u in range(n) if not F>>u&1]
    W={u:[g for g in FL if Bd[u,g]==0] for u in off}
    for u in off:
        for s in off:
            com=[g for g in W[u] if g in W[s]]
            lits=[tv(u,g,s) for g in com]
            if u==s: cl.append(lits)                       # M_uu = 1 needs a nonzero term
            elif Bd[u,s]==1:                                 # forced zero: not exactly one nonzero term
                if lits: exactly_one_forbidden(lits)
            else:
                z=Z[(u,s)]
                if lits:
                    cl.append([z]+lits)                      # nonzero needs a nonzero term
                    for i in range(len(lits)):               # zero => not exactly one
                        cl.append([-z,-lits[i]]+[lits[j] for j in range(len(lits)) if j!=i])
                else: cl.append([z])
cl.append(list(Z.values()))                                  # GOAL: some extra zero
with open(out,'w') as f:
    f.write('p cnf %d %d\n'%(nv,len(cl)))
    for c in cl: f.write(' '.join(map(str,c))+' 0\n')
open(out+'.frames','w').write(' '.join(map(str,fidx)))
print('frames',len(fidx),'zvars',len(Z),'vars',nv,'clauses',len(cl))
