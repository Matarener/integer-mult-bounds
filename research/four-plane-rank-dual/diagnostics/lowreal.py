import itertools, numpy as np, pickle, sys, time
A,B,C,D=1,2,4,8
paid=[((A|C),(A|C)),((B|C),(B|C)),((A|D),(A|D)),((B|D),(B|D)),((C|D),(A|B)),((A|B|D),(A|B|C)),((B|C|D),(A|C|D)),((A|B),(C|D)),((A|B|C),(A|B|D)),((A|C|D),(B|C|D))]
cost=[2,2,2,2,2,4,4,2,4,4]
free=[(A,B),(B,A),(C,D),(D,C)]
coords=lambda S:[2*k+i for k in range(4) if S>>k&1 for i in range(2)]
rng=np.random.default_rng(3)
def als(pats,restarts=30,iters=600):
    n=len(pats); I=np.eye(8); best=9
    for _ in range(restarts):
        Uv=[np.zeros(8) for _ in pats]; Vv=[np.zeros(8) for _ in pats]
        for j,(S,Tt) in enumerate(pats):
            Uv[j][coords(S)]=rng.standard_normal(len(coords(S))); Vv[j][coords(Tt)]=rng.standard_normal(len(coords(Tt)))
        for it in range(iters):
            for side in (0,1):
                src=Vv if side==0 else Uv; dst=Uv if side==0 else Vv
                for r in range(8):
                    js=[j for j,(S,Tt) in enumerate(pats) if r in coords(S if side==0 else Tt)]
                    if not js: continue
                    M=np.array([src[j] for j in js]).T
                    x,*_=np.linalg.lstsq(M, I[r,:] if side==0 else I[:,r], rcond=None)
                    for j,xx in zip(js,x): dst[j][r]=xx
            if it%50==49:
                res=np.linalg.norm(sum(np.outer(Uv[j],Vv[j]) for j in range(n))-I)
                if res<1e-10: return res,(Uv,Vv)
        res=np.linalg.norm(sum(np.outer(Uv[j],Vv[j]) for j in range(n))-I); best=min(best,res)
    return best,None
cap=int(sys.argv[1]); t=time.time(); tried=0; best=9
for mult in itertools.product(range(3),repeat=len(paid)):
    m=sum(c*k for c,k in zip(cost,mult))
    if m>cap or sum(mult)<4: continue
    pats=[p for p,k in zip(paid,mult) for _ in range(k)]+[f for f in free for _ in range(2)]
    # necessary: every diagonal plane block reachable by >=2 paid terms (free atoms never touch diagonal blocks)
    if any(sum(1 for S,Tt in pats[:sum(mult)] if S&P and Tt&P)<2 for P in (A,B,C,D)): continue
    tried+=1
    r,sol=als(pats,restarts=6,iters=300)
    if r<best: best=r; bestmult=mult
    if r<1e-8:
        print('FOUND mass',m,'mult',mult,flush=True); pickle.dump((pats,sol),open('lowreal_found.pkl','wb')); break
    if tried%20==0: print('tried',tried,'best',round(best,5),round(time.time()-t),flush=True)
print('end tried',tried,'best',best,flush=True)
print('bestmult',bestmult,flush=True)
pats=[p for p,k in zip(paid,bestmult) for _ in range(k)]+[f for f in free for _ in range(2)]
r,sol=als(pats,restarts=200,iters=3000)
print('hard re-solve residual',r,flush=True)
if sol: pickle.dump((pats,sol),open('lowreal_found.pkl','wb'))
