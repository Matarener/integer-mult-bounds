import math, time, sys
P={1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}
m=121; ts=0.9973135109511491
def leaf_depth(N):
    # F[d]: rho -> cnt, with m*rho*r <= N at each step; G = floor(log5(N/m)) steps
    G=0
    while 5**(G+1) <= N//m: G+=1
    F={1:1.0}; scale=0.0
    for d in range(G):
        nxt={}
        for rho,c in F.items():
            for r,pr in P.items():
                if m*rho*r<=N: nxt[rho*r]=nxt.get(rho*r,0.0)+c*pr
        s=sum(nxt.values()); scale+=math.log(s)
        F={k:v/s for k,v in nxt.items()}
    num=den=0.0
    for rho,c in F.items():
        for r,pr in P.items():
            w=c*pr*(r*rho)**ts
            num+=w*math.log(N/(r*rho)); den+=w
    return G, num/den, len(F)
t0=time.time()
for G in range(2,int(sys.argv[1])+1):
    lo=121*5**G; hi=121*5**G*49//10
    a=leaf_depth(lo); b=leaf_depth(hi)
    print(G, f"start {a[1]:.4f} end {b[1]:.4f} states {a[2]}", f"{time.time()-t0:.0f}s", flush=True)
