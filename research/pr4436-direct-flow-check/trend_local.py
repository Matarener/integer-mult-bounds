import math, time, sys
exec(open('overlap_flow.py').read())
W={5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224}
P={1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}
m=121; NMAX=int(sys.argv[1]); L=[0.0,1.0]; t=time.time()
marks={1000,3000,10000,30000,100000,200000}
for N in range(2,NMAX+1):
    if N<m: L.append(float(N)); continue
    r=flow(N,W,P); tot=sum(r['S'].values())
    L.append((sum(v*L[N-s] for s,v in r['S'].items())+sum(v*L[e] for e,v in r['X'].items()))/tot)
    if N in marks: print(N, '%.6f'%L[N], 'effective saving %.6f'%(1-math.log(L[N])/math.log(N)), round(time.time()-t), flush=True)
