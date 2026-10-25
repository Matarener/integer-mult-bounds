import math, sys, time
from verify import flow, multis  # same flow as the registered verifier
W={5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224}
P={1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}
m=121
f=lambda t: sum(W[k]*k**t for k in W)-sum(P[r]*r**t for r in P)
lo,hi=0.99,1.0
for _ in range(80):
    mid=(lo+hi)/2
    if f(mid)>0: hi=mid
    else: lo=mid
ts=(lo+hi)/2; print("root t* =",repr(ts),"s* =",1-ts, "f(1-0.0026865)=",f(1-0.0026865))
Ns=[int(1000*1.05**i) for i in range(0,400) if 1000*1.05**i<float(sys.argv[1])]
t0=time.time()
for N in Ns:
    R=flow(N,W,P)
    S=R['S'];X=R['X']
    st=sum(v*s**ts for s,v in S.items()); xt=sum(v*e**ts for e,v in X.items())
    ms=sum(v*s**ts*math.log(s) for s,v in S.items())/st; mx=sum(v*e**ts*math.log(e) for e,v in X.items())/xt
    g=ms-mx
    cap=(1-ts)*g/(g+1+math.log(m))
    k10=sum(v*e**(1-0.001) for e,v in X.items())/sum(v*s**(1-0.001) for s,v in S.items())
    print(N,R['G'],f"xt/st={xt/st:.9f} g={g:.4f} cap={cap:.6f} kappa(0.001)={k10:.6f} eta={0.999*m**-0.001:.6f}",f"{time.time()-t0:.0f}s",flush=True)
