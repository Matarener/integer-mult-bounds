# CORE-RES r8bin.py: R8 via the BINOMIAL (toric) part of the rank-8 completion equations.  EXACT (integer arithmetic only).
# Rank-8 completion M (M_tt = 1, M_ts = 0 for t orth s, rank 8).  Frame F: M_FF = I, so M = M[:,F] M[F,:].
# Unknowns u_t(g) = M_tg, v_t(g) = M_gt for t not in F, g in w(t) := {g in F : c_g.c_t != 0} (|w(t)| = 4); zero off w(t) (mask),
# NONZERO on w(t) by INT-M8 Step A (no extra zeros, CHECKED: kissat UNSAT + drat-trim VERIFIED).
# Equations used: for every ordered pair t, t' (not in F) with c_t orth c_t' and |w(t) & w(t')| = 2 = {g1, g2}:
#      u_t(g1) v_t'(g1) + u_t(g2) v_t'(g2) = 0   <=>   u_t(g1) v_t'(g1) / (u_t(g2) v_t'(g2)) = -1     (binomial).
# Lattice Lambda = Z-span of the exponent vectors.  Each binomial is homogeneous in u_t and in v_t separately, so the torus T of
# independent scalings (alpha_t, beta_t, tau_g; rank 215) solves it.  If rank Lambda = N - 215 and Z^N/Lambda is torsion-free, the solutions
# of the binomial system over any char-0 field = (G8 point) x T; then the diagonal equations M_tt = 1 force beta_t = 1/alpha_t: M = D G8 D^-1.  Torsion-freeness is certified by
# Gauss-Jordan elimination over Z using ONLY unit pivots (+-1): the final pivot rows are a basis of Lambda of the form [+-I | X].
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import time
t0=time.time()
fi=int(sys.argv[1]) if len(sys.argv)>1 else 0
Fm=FRM[fi]; F=[g for g in range(n) if Fm>>g&1]; assert len(F)==8
Ci=[[int(v) for v in C[t]] for t in range(n)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
OUT=[t for t in range(n) if t not in F]
w={t:[g for g in F if dot(Ci[t],Ci[g])!=0] for t in OUT}
assert all(len(w[t])==4 for t in OUT)
var={}
for t in OUT:
    for g in w[t]:
        var[('u',t,g)]=len(var); var[('v',t,g)]=len(var)
N=len(var)
rows=[]
for t in OUT:
    for t2 in OUT:
        if t2==t or dot(Ci[t],Ci[t2])!=0: continue
        I=[g for g in w[t] if g in w[t2]]
        if len(I)!=2: continue
        g1,g2=I
        r={var[('u',t,g1)]:1, var[('v',t2,g1)]:1}
        r[var[('u',t,g2)]]=r.get(var[('u',t,g2)],0)-1; r[var[('v',t2,g2)]]=r.get(var[('v',t2,g2)],0)-1
        rows.append({k:x for k,x in r.items() if x})
print('frame',fi,'N unknowns',N,'binomial equations',len(rows),flush=True)
# intersection sizes over orthogonal pairs outside F must lie in {0,2,4} (1 or 3 would contradict G8 being a completion)
from collections import Counter
isz=Counter(len([g for g in w[t] if g in w[t2]]) for t in OUT for t2 in OUT if t2!=t and dot(Ci[t],Ci[t2])==0)
print('orthogonal-pair |w cap w\'| distribution',dict(isz),flush=True); assert set(isz)<= {0,2,4}
# the scaling torus: exponent vectors of d_t (t in OUT) and tau_g (g in F); its Q-rank must be exactly 111
def qrank_int(vecs,p=2147483647):
    M=[[x%p for x in v] for v in vecs]; r=0; ncol=len(M[0])
    for c in range(ncol):
        pv=next((i for i in range(r,len(M)) if M[i][c]),None)
        if pv is None: continue
        M[r],M[pv]=M[pv],M[r]; inv=pow(M[r][c],p-2,p); M[r]=[x*inv%p for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]: f=M[i][c]; M[i]=[(x-f*y)%p for x,y in zip(M[i],M[r])]
        r+=1
    return r
# T' = independent scalings: u_t -> alpha_t u_t, v_t -> beta_t v_t (t in OUT), and tau_g (u(.,g)*tau, v(.,g)/tau).  216 vectors, one relation.
tor=[]
for t in OUT:
    v=[0]*N
    for g in w[t]: v[var[('u',t,g)]]=1
    tor.append(v)
    v=[0]*N
    for g in w[t]: v[var[('v',t,g)]]=1
    tor.append(v)
for g in F:
    v=[0]*N
    for t in OUT:
        if g in w[t]: v[var[('u',t,g)]]=1; v[var[('v',t,g)]]=-1
    tor.append(v)
tr=qrank_int(tor); print("rank of T' (mod p):",tr,flush=True)
rel=[sum(tor[2*i][j]-tor[2*i+1][j] for i in range(len(OUT)))-sum(tor[2*len(OUT)+i][j] for i in range(8)) for j in range(N)]
assert all(x==0 for x in rel) and tr==215     # one relation => Q-rank <= 215; mod-p rank 215 => Q-rank = 215
for r in rows:
    for v in tor: assert sum(x*v[k] for k,x in r.items())==0
print("T' lies in the kernel of every binomial exponent vector: OK",flush=True)
# sanity: G8 point u = v = c_t.c_g/8 = +-1/2 satisfies every binomial equation (sign check: product of signs = -1)
def sg(t,g): return 1 if dot(Ci[t],Ci[g])>0 else -1
bad=0
for t in OUT:
    for t2 in OUT:
        if t2==t or dot(Ci[t],Ci[t2])!=0: continue
        I=[g for g in w[t] if g in w[t2]]
        if len(I)!=2: continue
        g1,g2=I
        if sg(t,g1)*sg(t2,g1)*sg(t,g2)*sg(t2,g2)!=-1: bad+=1
print('G8 point violates',bad,'binomial equations',flush=True); assert bad==0

# ---- unit-pivot Gauss-Jordan over Z (sparse dict rows)
R=[dict(r) for r in rows]
colrows={}
for i,r in enumerate(R):
    for c in r: colrows.setdefault(c,set()).add(i)
alive=set(range(len(R))); piv=[]; maxabs=1
while True:
    found=None
    for i in alive:
        for c,x in R[i].items():
            if x in (1,-1): found=(i,c); break
        if found: break
    if not found: break
    i,c=found; alive.discard(i); piv.append((i,c))
    pr=R[i]; sgn=pr[c]
    for j in list(colrows.get(c,())):
        if j==i: continue
        f=R[j][c]*sgn          # R_j -= f * pr  (pr[c] = sgn, sgn^2 = 1)
        for cc,x in pr.items():
            y=R[j].get(cc,0)-f*x
            if y:
                if cc not in R[j]: colrows.setdefault(cc,set()).add(j)
                R[j][cc]=y; maxabs=max(maxabs,abs(y))
            else:
                if cc in R[j]: del R[j][cc]; colrows[cc].discard(j)
    # drop zero rows
    for j in list(alive):
        if not R[j]: alive.discard(j)
rem=[j for j in alive if R[j]]
rank=len(piv)
print('unit pivots (rank of Lambda):',rank,' N - rank =',N-rank,' leftover nonzero rows without unit entries:',len(rem),' max |entry|',maxabs,'%.0fs'%(time.time()-t0),flush=True)
if rem:
    import sympy
    sub=sorted({c for j in rem for c in R[j]})
    Mx=sympy.Matrix([[R[j].get(c,0) for c in sub] for j in rem])
    from sympy.matrices.normalforms import smith_normal_form
    snf=smith_normal_form(Mx,domain=sympy.ZZ); d=[snf[i,i] for i in range(min(snf.shape)) if snf[i,i]!=0]
    print('residual block',Mx.shape,'Smith diagonal (nonzero):',d,flush=True)
    rank+=len(d); tors=[x for x in d if abs(x)!=1]
    print('total rank',rank,'N-rank',N-rank,'torsion invariants',tors)
    if not tors: rem=[]
if not rem and N-rank==215:
    # diagonal equations: at the G8 point sum_g u_t(g) v_t(g) = 4 * (1/2)(1/2) = 1; on the coset it is alpha_t beta_t (tau cancels) => beta_t = 1/alpha_t
    print("THEOREM CHECK PASS (frame %d): Lambda has rank N-215, Z^N/Lambda torsion-free, T' (rank 215) inside its kernel => binomial solutions = G8 point x T'; diagonal eqs force beta_t = 1/alpha_t => M = D G8 D^-1"%fi)
else:
    print('NOT CLOSED by the binomial part alone')
