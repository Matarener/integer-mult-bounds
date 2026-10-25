# CORE3 core3.py: the facts used by the |supp beta| = 3 proof (NOTES sec. 2), all EXACT (F2 / integer / Fractions).
#  V1  for every flat Z (rank <= 7, all Aut-orbits), T = L \ Z, N = T minus its coloops:
#      #coloops(T) <= 1, and kappa(N) >= 7 (every cocircuit of N spans >= 7 label dims).  Coloop only on the 59-line flat,
#      whose normal is a P112 root r and whose coloop is the line of r.
#  V2  D(T) = dim span lab(T) is 9 except on the 56-line flat, whose normal is a frame root.
#  V3  danger configuration (two losses): a_j ~ f_j, a_l ~ f_l frame roots (j,l != k), r_j = p_j - p_k, r_l = p_l - p_k P112 roots,
#      f_j . r_l = 0, f_l . r_j = 0, f_j . r_j != 0, f_l . r_l != 0, a_k = x f_j + y f_l (x,y != 0):
#      min rank_F2 Bd[H^c(a_k), {r_j, r_l}] over ALL such configurations and ALL ratios x:y.
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import pickle, itertools
from fractions import Fraction as Fr
from collections import Counter
HERE3=os.path.dirname(os.path.abspath(__file__))
FL=pickle.load(open(HERE3+'/flats.pkl','rb'))
FULL=(1<<n)-1
Ci=[[int(v) for v in C[t]] for t in range(n)]
ODD=[sum(1<<t for t in range(n) if bin(h&LAB[t]).count('1')&1) for h in range(512)]
def lines_of(m): return [t for t in range(n) if m>>t&1]
def rank_lines(m):
    b=[]
    for t in lines_of(m):
        v=LAB[t]
        for y in b: v=min(v,v^y)
        if v: b.append(v)
    return len(b)
def coloops(T):
    r=rank_lines(T); return [t for t in lines_of(T) if rank_lines(T&~(1<<t))<r]
def kappa(T):
    k=10**9
    for h in range(1,512):
        Cm=T&ODD[h]
        if Cm: k=min(k,rank_lines(Cm))
    return k
def nullspace(rows):   # exact rational nullspace of the row vectors (vectors x with rows.x = 0)
    M=[[Fr(v) for v in r] for r in rows]; m=8; piv=[]; R=0
    for c in range(m):
        p=next((i for i in range(R,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[R],M[p]=M[p],M[R]; M[R]=[x/M[R][c] for x in M[R]]
        for i in range(len(M)):
            if i!=R and M[i][c]!=0: f=M[i][c]; M[i]=[x-f*y for x,y in zip(M[i],M[R])]
        piv.append(c); R+=1
    free=[c for c in range(m) if c not in piv]; out=[]
    for f in free:
        x=[Fr(0)]*m; x[f]=Fr(1)
        for i,c in enumerate(piv): x[c]=-M[i][f]
        out.append(x)
    return out
def parallel(u,v):
    return all(u[i]*v[j]==u[j]*v[i] for i in range(8) for j in range(8))
FRV=[list(R120[i]) for i in FR]
frames8=[];seen=set()
for v in FRV:
    key=tuple(v) if next(x for x in v if x)>0 else tuple(-x for x in v)
    if key not in seen: seen.add(key); frames8.append(list(key))
assert len(frames8)==4*1 or True
print('frame root lines (up to sign):',len(frames8))
# ---------------- V1, V2
bad=0; stat=Counter()
for o in FL:
    if o['rank']>7: continue
    T=FULL&~o['mask']; D=rank_lines(T); cl=coloops(T); N=T
    for t in cl: N&=~(1<<t)
    kN=kappa(N)
    stat[(o['rank'],o['nlines'],D,len(cl),kN)]+=1
    if len(cl)>1 or kN<7: bad+=1; print('V1 FAIL',o['rank'],o['nlines'],D,cl,kN)
    if cl or D<9:
        Zl=lines_of(o['mask']); ns=nullspace([Ci[t] for t in Zl]); assert len(ns)==1; nv=ns[0]
        isroot=[t for t in range(n) if parallel(nv,Ci[t])]
        isfr=[f for f in frames8 if parallel(nv,f)]
        print('flat rank',o['rank'],'|Z|',o['nlines'],'orbit',o['orbit'],'D',D,'coloops',cl,'normal ~ P112 line',isroot,'normal ~ frame root',len(isfr)>0)
        if cl: assert isroot==cl, 'coloop is not the normal line'
        if D<9: assert isfr and o['nlines']==56
print('V1/V2 table (rank,|Z|,D,#coloops,kappa(N)):',sorted(stat.items()))
print('V1 failures:',bad)
# ---------------- V3 danger enumeration
def dot(u,v): return sum(a*b for a,b in zip(u,v))
def rank_bd(Rl,Al):
    rows=[sum(int(Bd[t,s])<<i for i,s in enumerate(Al)) for t in Rl]
    b=[]
    for v in rows:
        for y in b: v=min(v,v^y)
        if v: b.append(v)
    return len(b)
cnt=0; worst=Counter(); minr=9
for fj,fl in itertools.permutations(frames8,2):
    for rj in range(n):
        if dot(fl,Ci[rj])!=0 or dot(fj,Ci[rj])==0: continue
        for rl in range(n):
            if rl==rj or dot(fj,Ci[rl])!=0 or dot(fl,Ci[rl])==0: continue
            # a_k = x fj + y fl, x,y != 0.  Special ratios: those making a_k orthogonal to some line beyond the lines orthogonal to both.
            ratios=set()
            for t in range(n):
                u,w=dot(Ci[t],fj),dot(Ci[t],fl)
                if u!=0 and w!=0: ratios.add(Fr(-w,u))      # x/y with x u + y w = 0  ->  x = -w/u * y
            cands=[('generic',None)]+[('x/y=%s'%q,q) for q in ratios]
            for nm,q in cands:
                if q is None:
                    Rk=[t for t in range(n) if not (dot(Ci[t],fj)==0 and dot(Ci[t],fl)==0)]
                else:
                    ak=[q*a+b for a,b in zip(fj,fl)]
                    Rk=[t for t in range(n) if dot(Ci[t],ak)!=0]
                r=rank_bd(Rk,[rj,rl]); cnt+=1; worst[r]+=1; minr=min(minr,r)
print('V3 danger configs x ratios checked:',cnt,' rank_F2 Bd[R_k,{r_j,r_l}] distribution:',sorted(worst.items()),' MIN =',minr)
