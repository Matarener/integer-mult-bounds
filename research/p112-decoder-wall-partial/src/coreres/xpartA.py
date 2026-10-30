# CORE-RES xpartA.py: INDEPENDENT re-check of CORE3 s4.py Part A (hurt configurations), own E8/P112/Bd, own ranks (mod p > Hadamard).
# Config: h distinct frame roots f_m (m in J) and P112 root lines r_m with r_m non-orth f_m and r_m orth f_i (i in J, i != m), r_m distinct.
# Claim: rank_F2 Bd[H^c(a) u D, D] = h for EVERY a with a.r_m != 0 for all m (D = {r_m}).
# Exact test: rank < h iff some nonzero w subset of D has S_w = {t : sum_{m in w} Bd[t, r_m] odd} disjoint from D and no r_m in span_Q(S_w).
import itertools, time
from collections import Counter
t0=time.time()
roots=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; roots.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: roots.append(s)
def canon(v):
    f=next(x for x in v if x); return tuple(v) if f>0 else tuple(-x for x in v)
lines=sorted({canon(r) for r in roots})
FRS=[canon(tuple(2 if k==i else s*2 if k==i+1 else 0 for k in range(8))) for i in range(0,8,2) for s in (1,-1)]
L=[v for v in lines if v not in FRS]; n=len(L)
dot=lambda a,b: sum(x*y for x,y in zip(a,b))
Bd=[[1 if (t==s or dot(L[t],L[s])==0) else 0 for s in range(n)] for t in range(n)]
P=2147483647
def rank_p(vecs):
    b={}
    for v in vecs:
        v=[x%P for x in v]
        for c,bv in b.items():
            if v[c]: f=v[c]; v=[(x-f*y)%P for x,y in zip(v,bv)]
        c=next((i for i in range(8) if v[i]),None)
        if c is None: continue
        inv=pow(v[c],P-2,P); b[c]=[x*inv%P for x in v]
    return len(b)
NF=[frozenset(i for i in range(8) if dot(L[t],FRS[i])!=0) for t in range(n)]
assert all(len(x)==4 for x in NF)
cache={}
def ok(D):
    for wb in range(1,1<<len(D)):
        w=[D[i] for i in range(len(D)) if wb>>i&1]
        S=tuple(t for t in range(n) if sum(Bd[t][r] for r in w)%2)
        if any(t in D for t in S): continue
        if S not in cache:
            base=[L[t] for t in S]; r0=rank_p(base)
            cache[S]=(r0,frozenset(r for r in range(n) if rank_p(base+[L[r]])==r0))
        r0,ins=cache[S]
        if any(r in ins for r in D): continue
        return False
    return True
for h in range(2,6):
    tot=fail=0
    for J in itertools.combinations(range(8),h):
        cand=[[t for t in range(n) if NF[t]&set(J)=={m}] for m in J]
        for D in itertools.product(*cand):
            if len(set(D))<h: continue
            tot+=1; fail+= not ok(list(D))
    print('h=%d configs %d failures %d (%.0fs)'%(h,tot,fail,time.time()-t0),flush=True)
