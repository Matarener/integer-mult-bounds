# CORE3 xcheck.py: INDEPENDENT re-derivation of the finite facts V0-V3 (no flats.py / G.npy / LAB labels used).
#  - flats: BFS over the Q-matroid of the 112 lines with EXACT integer normals (Fractions kernel), orbits via pynauty canonical
#    certificates of the Bd graph with the flat as a vertex colour class (Aut(Bd) = the linear group, checked in flats.py).
#  - F2 facts computed from Bd columns directly: rank_F2 Bd[:, X] = dim span lab(X).
#  - V3 replaced by the STRONGER statement G2: for every orthogonal pair of P112 root lines r ⊥ r', the lines t with
#    Bd[t,r] != Bd[t,r'] span Q^8 (so rank Bd[H^c(a) u {r,r'}, {r,r'}] = 2 for EVERY a != 0).
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import n, C, Bd, R120, FR
import pynauty, itertools, time
from fractions import Fraction as Fr
from collections import Counter
t0=time.time()
Ci=[[int(v) for v in C[t]] for t in range(n)]
ADJ={i:[j for j in range(n) if j!=i and Bd[i,j]] for i in range(n)}
def cert(mask):
    F={t for t in range(n) if mask>>t&1}
    if not F or len(F)==n: col=[set(range(n))]
    else: col=[F,set(range(n))-F]
    return (len(F),pynauty.certificate(pynauty.Graph(n,adjacency_dict=ADJ,vertex_coloring=col)))
def kernel(rows):
    M=[[Fr(v) for v in r] for r in rows]; piv=[]; R=0
    for c in range(8):
        p=next((i for i in range(R,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[R],M[p]=M[p],M[R]; M[R]=[x/M[R][c] for x in M[R]]
        for i in range(len(M)):
            if i!=R and M[i][c]!=0: f=M[i][c]; M[i]=[x-f*y for x,y in zip(M[i],M[R])]
        piv.append(c); R+=1
    out=[]
    for f in [c for c in range(8) if c not in piv]:
        x=[Fr(0)]*8; x[f]=Fr(1)
        for i,c in enumerate(piv): x[c]=-M[i][f]
        out.append(x)
    return out,R
def flat_of(lines):
    ker,r=kernel([Ci[t] for t in lines])
    m=0
    for t in range(n):
        if all(sum(a*b for a,b in zip(k,Ci[t]))==0 for k in ker): m|=1<<t
    return r,m
def lines_of(m): return [t for t in range(n) if m>>t&1]
reps={0:{cert(0):0}}
for r in range(0,7):
    nxt={}
    for F in reps[r].values():
        Fl=lines_of(F); seen=set()
        # use a basis of F to keep the kernel small
        basis=[]
        for t in Fl:
            if kernel([Ci[s] for s in basis+[t]])[1]>len(basis): basis.append(t)
        for t in range(n):
            if F>>t&1: continue
            rr,cl=flat_of(basis+[t])
            if cl in seen: continue
            seen.add(cl); assert rr==r+1
            c=cert(cl)
            if c not in nxt: nxt[c]=cl
    reps[r+1]=nxt
    print('rank',r+1,'orbits',len(nxt),'%.0fs'%(time.time()-t0),flush=True)
# ---- F2 matroid of Bd columns
COL=[sum(int(Bd[t,s])<<t for t in range(n)) for s in range(n)]   # column s as a 112-bit row-vector
def f2rank(vs):
    b=[]
    for v in vs:
        for y in b: v=min(v,v^y)
        if v: b.append(v)
    return len(b)
def rk(m): return f2rank([COL[s] for s in lines_of(m)])
def rowspace_supports(m):
    """all nonzero vectors of the row space of Bd[:, m] (as subsets of m): rows of Bd restricted to columns m, F2 span."""
    cols=lines_of(m)
    rows=[sum(int(Bd[t,s])<<i for i,s in enumerate(cols)) for t in range(n)]
    b=[]
    for v in rows:
        for y in b: v=min(v,v^y)
        if v: b.append(v)
    sup=[]
    for bits in range(1,1<<len(b)):
        v=0
        for i in range(len(b)):
            if bits>>i&1: v^=b[i]
        sup.append(sum(1<<cols[i] for i in range(len(cols)) if v>>i&1))
    return sup
FULL=(1<<n)-1
tab=Counter(); bad=0; maxZ=0; Dlt9=[]
for r in range(0,8):
    for F in reps[r].values():
        T=FULL&~F; D=rk(T); maxZ=max(maxZ,bin(F).count('1')) if r==7 else maxZ
        colo=[t for t in lines_of(T) if rk(T&~(1<<t))<D]
        N=T
        for t in colo: N&=~(1<<t)
        kap=min(rk(S) for S in rowspace_supports(N))     # min span-dim over all cocircuit-containing supports (<= kappa)
        tab[(r,bin(F).count('1'),D,len(colo),kap)]+=1
        if D<9: Dlt9.append((r,bin(F).count('1')))
        if len(colo)>1 or kap<7: bad+=1
print('orbits per rank',[len(reps[r]) for r in range(8)])
print('table (rank,|Z|,D,#coloops,kappa):',sorted(tab.items()))
print('V0 max |Z| on rank-7 flats:',maxZ,' V2 flats with D<9:',Dlt9,' V1 failures:',bad,'%.0fs'%(time.time()-t0),flush=True)
# ---- G2
roots=list(range(n))
def dot(u,v): return sum(a*b for a,b in zip(u,v))
g2bad=0; pairs=0
for r1 in range(n):
    for r2 in range(r1+1,n):
        if dot(Ci[r1],Ci[r2])!=0: continue
        pairs+=1
        Dl=[t for t in range(n) if Bd[t,r1]!=Bd[t,r2]]
        if kernel([Ci[t] for t in Dl])[1]<8: g2bad+=1
print('G2: orthogonal root-line pairs',pairs,' pairs whose separating lines do NOT span Q^8:',g2bad,'%.0fs'%(time.time()-t0))
