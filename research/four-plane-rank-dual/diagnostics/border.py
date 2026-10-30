import numpy as np
exec(open('lowreal.py').read().split("cap=int(sys.argv[1])")[0])
mult=(1, 0, 1, 2, 0, 0, 1, 1, 0, 0)
pats=[p for p,k in zip(paid,mult) for _ in range(k)]+[f for f in free for _ in range(2)]
n=len(pats); I=np.eye(8); rng=np.random.default_rng(11)
bestrun=None
for rs in range(60):
    Uv=[np.zeros(8) for _ in pats]; Vv=[np.zeros(8) for _ in pats]
    for j,(S,Tt) in enumerate(pats):
        Uv[j][coords(S)]=rng.standard_normal(len(coords(S))); Vv[j][coords(Tt)]=rng.standard_normal(len(coords(Tt)))
    hist=[]
    for it in range(20000):
        for side in (0,1):
            src=Vv if side==0 else Uv; dst=Uv if side==0 else Vv
            for r in range(8):
                js=[j for j,(S,Tt) in enumerate(pats) if r in coords(S if side==0 else Tt)]
                M=np.array([src[j] for j in js]).T
                x,*_=np.linalg.lstsq(M, I[r,:] if side==0 else I[:,r], rcond=None)
                for j,xx in zip(js,x): dst[j][r]=xx
        if it in (100,1000,3000,10000,19999):
            res=np.linalg.norm(sum(np.outer(Uv[j],Vv[j]) for j in range(n))-I)
            mx=max(np.linalg.norm(Uv[j])*np.linalg.norm(Vv[j]) for j in range(n))
            hist.append((it,res,mx))
    if bestrun is None or hist[-1][1]<bestrun[-1][1]: bestrun=hist
    if hist[-1][1]<1e-9: break
for h in bestrun: print('iter %6d residual %.3e max|u||v| %.3e'%h)
