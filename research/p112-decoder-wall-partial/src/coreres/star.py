# CORE-RES star.py: case (a2) of s = 9 (|K7| >= 2, all nine terms cost exactly 7) -- the STAR filter.  EXACT.
# Necessary conditions at a vertex k in K7 (Y_k = span lab(A_k), dim 7), proved in NOTES sec. 2:
#  (N1) all 8 directions q_j = p_j - p_k are lossy for Y_k  (loss(L \ Z(q_j), Y_k) >= 1);
#  (N2) the terms N7 = [9] \ K7 have a_i ~ frame root f_i (distinct); dual basis: f_i . q_j = 0 for j != i, f_i . q_i != 0;
#  (N3) the K7 directions (m - 1 = 8 - h of them) are root or frame-root lines (|Z| >= 40 and lossy), orthogonal to every used f_i,
#       pairwise |dot| = 1 (real units) with a balanced sign pattern (A_{m-1} star; equal scales).
# We fix Y_k to each of the 56 Aut-orbit representatives (Aut is checked orthogonal below, so it preserves dots and frame roots).
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import numpy as np, pickle, itertools, time, pynauty
from fractions import Fraction as Fr
from math import gcd
t0=time.time(); HERE=os.path.dirname(os.path.abspath(__file__))
LO=pickle.load(open(HERE+'/lossy.pkl','rb'))
Ci=[[int(v) for v in C[t]] for t in range(n)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
# ---- Aut is orthogonal (checked on the pynauty generators; G.npy is their closure)
ADJ={i:[j for j in range(n) if j!=i and Bd[i,j]] for i in range(n)}
gens=pynauty.autgrp(pynauty.Graph(n,adjacency_dict=ADJ))[0]
basis=[]
for t in range(n):
    if np.linalg.matrix_rank(C[basis+[t]])>len(basis): basis.append(t)
    if len(basis)==8: break
Binv=np.linalg.inv(C[basis].T.astype(float))
for g in gens:
    ok=False
    for signs in itertools.product((1,-1),repeat=8):
        T=(C[[g[t] for t in basis]].T*np.array(signs))@Binv
        img=(T@C.T).T
        if all(np.allclose(img[t],C[g[t]]) or np.allclose(img[t],-C[g[t]]) for t in range(n)):
            ok=np.allclose(T.T@T,np.eye(8)); break
    assert ok
print('Aut generators orthogonal: OK',flush=True)
FRV=[list(R120[i]) for i in FR]          # 8 frame roots (2x coords), mutually orthogonal
assert all(dot(FRV[i],FRV[j])==0 for i in range(8) for j in range(i))
def prim(v):
    v=[Fr(x) for x in v]; den=1
    for x in v: den=den*x.denominator//gcd(den,x.denominator)
    w=[int(x*den) for x in v]; g=0
    for x in w: g=gcd(g,abs(x))
    w=[x//g for x in w]; f=next(x for x in w if x)
    return tuple(w if f>0 else [-x for x in w])
def rref(rows):
    M=[[Fr(x) for x in r] for r in rows]; piv=[]; R=0
    for c in range(8):
        p=next((i for i in range(R,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[R],M[p]=M[p],M[R]; f=M[R][c]; M[R]=[x/f for x in M[R]]
        for i in range(len(M)):
            if i!=R and M[i][c]!=0: g=M[i][c]; M[i]=[x-g*y for x,y in zip(M[i],M[R])]
        piv.append(c); R+=1
    return M[:R],piv
def perp(lines):
    M,piv=rref([Ci[t] for t in lines]); free=[c for c in range(8) if c not in piv]; out=[]
    for f in free:
        v=[Fr(0)]*8; v[f]=Fr(1)
        for i,c in enumerate(piv): v[c]=-M[i][f]
        out.append(prim(v))
    return out
def rk(vs): return len(rref(vs)[0]) if vs else 0
ROOTS={prim(C[t]) for t in range(n)}; FRS={prim(f) for f in FRV}
total_stars=0; report=[]
for r in LO['reps']:
    lines_=[]; planes=[]
    for Zm,rank_,nz in LO['lossy'][r]:
        P=perp([t for t in range(n) if Zm>>t&1])
        if len(P)==1: lines_.append((P[0],nz))
        else: planes.append((P,nz))
    # BUGFIX (found by xa.py): prim() halves D-type roots (2,2,0..) -> (1,1,0..); rescale root directions to norm 8 (2x coords)
    def toroot(v):
        nn=dot(v,v); assert nn in (2,8), nn
        return tuple(2*x for x in v) if nn==2 else tuple(v)
    rootdirs=[toroot(v) for v,nz in lines_ if nz in (56,59)]
    for v,nz in lines_:
        if nz==59: assert v in ROOTS
        if nz==56: assert v in FRS
    for v in rootdirs: assert dot(v,v)==8
    stars=0
    for h in range(0,8):
        m1=8-h
        for N in itertools.combinations(range(8),h):
            Nf=[FRV[i] for i in N]
            # K-part candidates: root/frame lines orthogonal to all used frame roots
            KC=[v for v in rootdirs if all(dot(v,f)==0 for f in Nf)]
            if len(KC)<m1: continue
            # N-part candidates for each f in N: lossy line q with q.f != 0, q orth other used f's; or a lossy plane containing such q
            NC=[]
            for i,f in enumerate(Nf):
                others=[g for j,g in enumerate(Nf) if j!=i]
                c=[('L',v) for v,nz in lines_ if dot(v,f)!=0 and all(dot(v,g)==0 for g in others)]
                for P,nz in planes:
                    # subspace of the plane orthogonal to the others; need a vector in it with nonzero f-component
                    sols=[x for x in [P[0],P[1]]]
                    # generic element a P0 + b P1: conditions linear in (a,b); find whether a solution space with f.q != 0 exists
                    A=[[dot(P[0],g),dot(P[1],g)] for g in others]
                    # nullspace of A in (a,b)
                    rA=rk([[Fr(x) for x in row]+[0]*6 for row in A]) if A else 0
                    if rA==0:
                        if dot(P[0],f)!=0 or dot(P[1],f)!=0: c.append(('P',tuple(P)))
                    elif rA==1:
                        row=next(row for row in A if any(row)); ab=(row[1],-row[0])
                        q=prim([ab[0]*x+ab[1]*y for x,y in zip(P[0],P[1])])
                        if dot(q,f)!=0: c.append(('L',q))
                NC.append(c)
            if any(len(c)==0 for c in NC): continue
            # A_{m1} stars inside KC: cliques of size m1 with |dot|=4 (2x coords: real 1 -> 4), balanced signs
            adj={a:[b for b in range(len(KC)) if b!=a and abs(dot(KC[a],KC[b]))==4] for a in range(len(KC))}
            found=[]
            def rec(cl,cand):
                if found: return
                if len(cl)==m1:
                    # balanced: choose sign of first, propagate; all products must be +4
                    sg={cl[0]:1}
                    for x in cl[1:]: sg[x]=1 if dot(KC[cl[0]],KC[x])*1>0 else -1
                    if all(sg[a]*sg[b]*dot(KC[a],KC[b])==4 for a,b in itertools.combinations(cl,2)):
                        found.append(list(cl))
                    return
                for b in cand:
                    if not cl or b>cl[-1]:
                        rec(cl+[b],[c for c in cand if c in adj[b]] if cl else adj[b])
            if m1==0: found.append([])
            else:
                for a in range(len(KC)):
                    rec([a],adj[a])
                    if found: break
            if not found: continue
            # independence: K-star spans U (dim m1) automatically if found star is independent; N-part adds the f directions
            Kst=[KC[x] for x in found[0]]
            if rk(Kst)!=m1: continue
            stars+=1
            report.append((r,h,N,len(KC),[len(c) for c in NC]))
    total_stars+=stars
    print('Y rep',r,'stars (h,N) feasible:',stars,'%.0fs'%(time.time()-t0),flush=True)
print('TOTAL (Y rep, h, N) with a valid star:',total_stars)
from collections import Counter
print('by h:',sorted(Counter(x[1] for x in report).items()))
pickle.dump(report,open(HERE+'/star.pkl','wb'))
