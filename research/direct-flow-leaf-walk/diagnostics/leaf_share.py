# Diagnostic (not registered): leaf share and depths at level starts/ends. Run from this directory:
#   python3.12 -B leaf_share.py 2 9   (about 2 minutes)
import math, time
exec(open('overlap_flow.py').read())
W={5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224}
P={1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}
ts=0.9973135109511491; t0=time.time()
import sys
for G in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
    for N in (121*5**G+1, 121*5**G*49//10):
        R=flow(N,W,P); X=R['X']; BX=R['BX']; S=R['S']
        xt=sum(v*e**ts for e,v in X.items()); bt=sum(v*e**ts for e,v in BX.items())
        srcd=sum(v*s**ts*math.log(N/s) for s,v in S.items())/sum(v*s**ts for s,v in S.items())
        bdd=sum(v*e**ts*math.log(N/e) for e,v in BX.items() if v)/bt
        print(G,N,f"leaf share {1-bt/xt:.4f} bd depth {bdd:.4f} src depth {srcd:.4f}",f"{time.time()-t0:.0f}s",flush=True)
