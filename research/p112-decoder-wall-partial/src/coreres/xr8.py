# CORE-RES xr8.py: INDEPENDENT cross-check of r8bin.py (no base.py, no FULLWALL code; own E8, own P112, own frame, own equations).
# Checks: (1) binomial exponent lattice Lambda has rank N - 215 (mod-p rank >= ..., T' kernel bound <= ...);
#         (2) Lambda is saturated: an explicit rank x rank minor with det = +-1 (det mod 24 primes + Hadamard bound, CRT);
#         (3) G8 point solves every binomial; T' (independent u/v scalings + frame torus) has rank 215 and is in the kernel.
import itertools, numpy as np, sys, time
t0=time.time()
roots=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; roots.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: roots.append(s)
assert len(roots)==240
def canon(v):
    f=next(x for x in v if x); return v if f>0 else tuple(-x for x in v)
lines=sorted({canon(r) for r in roots}); assert len(lines)==120
frame_roots={canon(tuple(2 if k==i else s*2 if k==i+1 else 0 for k in range(8))) for i in range(0,8,2) for s in (1,-1)}
L=[v for v in lines if v not in frame_roots]; n=len(L); assert n==112
dot=lambda a,b: sum(x*y for x,y in zip(a,b))
# a frame of P112: 8 mutually orthogonal lines (choose the lexicographically LAST one found, to differ from base.py's FRM[0])
fr=[]
def rec(cl,start):
    if len(cl)==8: fr.append(list(cl)); return len(fr)>=50
    for t in range(start,n):
        if all(dot(L[t],L[x])==0 for x in cl):
            if rec(cl+[t],t+1): return True
    return False
rec([],0); F=fr[-1]
OUT=[t for t in range(n) if t not in F]
w={t:[g for g in F if dot(L[t],L[g])!=0] for t in OUT}; assert all(len(x)==4 for x in w.values())
var={}
for t in OUT:
    for g in w[t]: var[('u',t,g)]=len(var)
for t in OUT:
    for g in w[t]: var[('v',t,g)]=len(var)
N=len(var)
rows=[]; signs_ok=True
for t in OUT:
    for t2 in OUT:
        if t==t2 or dot(L[t],L[t2])!=0: continue
        I=[g for g in w[t] if g in w[t2]]
        assert len(I) in (0,2,4)
        if len(I)!=2: continue
        g1,g2=I; r=np.zeros(N,np.int64)
        r[var[('u',t,g1)]]+=1; r[var[('v',t2,g1)]]+=1; r[var[('u',t,g2)]]-=1; r[var[('v',t2,g2)]]-=1
        rows.append(r)
        sg=lambda a,b: 1 if dot(L[a],L[b])>0 else -1
        if sg(t,g1)*sg(t2,g1)*sg(t,g2)*sg(t2,g2)!=-1: signs_ok=False
B=np.array(rows); print('N',N,'binomials',len(B),'G8 point solves all:',signs_ok,flush=True); assert signs_ok
tor=[]
for t in OUT:
    for typ in 'uv':
        v=np.zeros(N,np.int64)
        for g in w[t]: v[var[(typ,t,g)]]=1
        tor.append(v)
for g in F:
    v=np.zeros(N,np.int64)
    for t in OUT:
        if g in w[t]: v[var[('u',t,g)]]=1; v[var[('v',t,g)]]=-1
    tor.append(v)
T=np.array(tor); assert not (B@T.T).any(); print("T' in kernel: OK",flush=True)
def rank_modp(M,p):
    M=M.copy()%p; r=0; rows_,cols_=M.shape; piv=[]
    for c in range(cols_):
        nz=np.nonzero(M[r:,c])[0]
        if len(nz)==0: continue
        i=r+nz[0]; M[[r,i]]=M[[i,r]]; inv=pow(int(M[r,c]),p-2,p); M[r]=(M[r]*inv)%p
        col=M[:,c].copy(); col[r]=0; nzr=np.nonzero(col)[0]
        if len(nzr): M[nzr]=(M[nzr]-np.outer(col[nzr],M[r]))%p
        piv.append(c); r+=1
        if r==rows_: break
    return r,piv
p0=1000003
rT,_=rank_modp(T,p0); print("rank T' mod p:",rT,flush=True); assert rT==215   # <= 215 (one relation), so = 215 over Q
# choose independent rows: greedy mod p over rows (transpose trick: rank of B^T pivots = independent rows)
rB,pivrows=rank_modp(B.T.copy(),p0); print('rank Lambda mod p:',rB,' N - rank =',N-rB,flush=True)
assert rB==N-215     # Q-rank >= mod-p rank = N-215 and Q-rank <= N-215 (T' of rank 215 in the kernel)
Bs=B[pivrows]; rB2,pivcols=rank_modp(Bs.copy(),p0); assert rB2==rB
Msq=Bs[:,pivcols]
# det of the rank x rank minor: mod many primes + Hadamard bound
import math
logH=sum(0.5*math.log2(float((r*r).sum())) for r in Msq)   # log2 Hadamard bound
primes=[]; q=2**31-1
def isprime(x):
    if x<2: return False
    for d in range(2,int(x**0.5)+1):
        if x%d==0: return False
    return True
while sum(math.log2(x) for x in primes)<logH+2:
    if isprime(q): primes.append(q)
    q-=2
def det_modp(M,p):
    M=M.copy()%p; m=len(M); d=1
    for c in range(m):
        nz=np.nonzero(M[c:,c])[0]
        if len(nz)==0: return 0
        i=c+nz[0]
        if i!=c: M[[c,i]]=M[[i,c]]; d=-d
        piv=int(M[c,c]); d=d*piv%p; inv=pow(piv,p-2,p)
        col=M[c+1:,c].copy(); nzr=np.nonzero(col)[0]
        if len(nzr):
            f=(col[nzr]*inv)%p
            M[c+1+nzr]=(M[c+1+nzr]-((f[:,None]*M[c])%p))%p
    return d%p
res=[det_modp(Msq,p) for p in primes]
# CRT
x=0; mod=1
for r,p in zip(res,primes):
    t=((r-x)*pow(mod,-1,p))%p; x+=mod*t; mod*=p
if x>mod//2: x-=mod
print('minor size',len(Msq),'log2 Hadamard bound %.1f'%logH,'#primes',len(primes),'det =',x,flush=True)
print('XCHECK', 'PASS' if abs(x)==1 else 'FAIL', '(Lambda saturated, rank N-215: binomial solutions = G8 point x T\')','%.0fs'%(time.time()-t0))
