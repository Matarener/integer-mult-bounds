import numpy as np, math
P={1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}
ts=0.9973135109511491
rs=np.array(sorted(P)); lr=np.log(rs); base=np.array([P[r]*r**ts for r in rs],float)
def law(lam):
    w=base*np.exp(-lam*lr); return w/w.sum()
def mean(lam): return float((law(lam)*lr).sum())
ln5=math.log(5)
rng=np.random.default_rng(7)
print("G  overshoot_estimate  (B = G ln5)")
for G in (50,200,1000,4000,16000,64000,256000,1000000):
    B=G*ln5
    # choose tilt so the tilted mean equals B/G (Esscher); exact reweighting factor exp(lam*S) up to a constant
    lo,hi=0.0,1.0
    for _ in range(80):
        mid=(lo+hi)/2
        if mean(mid)>B/G: lo=mid
        else: hi=mid
    lam=(lo+hi)/2; q=law(lam)
    n=rng.multinomial(G,q,size=400000)
    S=n@lr
    keep=S<=B
    w=np.exp(lam*(S[keep]-B))   # original/tilted density ratio up to a constant
    est=float(((B-S[keep])*w).sum()/w.sum())
    print(G, round(est,3), "lambda",round(lam,5), "kept", keep.mean().round(3), flush=True)
print("1/lambda* =", 1/0.007499128505171482)
