exec(open('overlap_flow_depth.py').read())  # run from this directory
W={5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224}
P={1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}
m=121
sav=(0.001,0.0012,0.0015)
worst={(d,s):0 for d in (0,1,2) for s in sav}
for N in [int(1000*1.05**i) for i in range(0,200) if 1000*1.05**i<2.5e6]:
    G0=0
    while 5**(G0+1)<=N//m: G0+=1
    ks={}
    for d in (0,1):
        if G0-d<1: continue
        R=flow(N,W,P,G0-d); S,X=R['S'],R['X']
        for s in sav:
            z=1-s
            ks[(d,s)]=sum(v*e**z for e,v in X.items())/sum(v*x**z for x,v in S.items() if m*x>N)
    if N>=3e5:
        for s in sav:
            worst[(0,s)]=max(worst[(0,s)],ks[(0,s)]); worst[(1,s)]=max(worst[(1,s)],ks[(1,s)])
            worst[(2,s)]=max(worst[(2,s)],min(ks[(0,s)],ks[(1,s)]))
for s in sav:
    eta=(1-s)*121**(-s)
    print(f"saving {s}: eta {eta:.6f} | depth G0: sup kappa(N>=3e5) {worst[(0,s)]:.6f} | depth G0-1, low sources dropped: {worst[(1,s)]:.6f} | per-N best of the two: {worst[(2,s)]:.6f}")
