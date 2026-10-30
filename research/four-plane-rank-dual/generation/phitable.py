import numpy as np, itertools, time
K=4; U=list(range(1,16)); SINGLES=[1,2,4,8]
OFF=[(P,Q) for P in SINGLES for Q in SINGLES if P!=Q]
t=time.time()
tab=np.zeros((4096,15,15,15),dtype=np.uint8)   # [Z, S-1, T-1, X-1]
for S in U:
  for T in U:
    for X in U:
      rows=[P for P in SINGLES if P&S&X]; cols=[Q for Q in SINGLES if Q&T&X]
      if not rows or not cols: continue
      # pairs relevant: (P,Q) with P in rows, Q in cols, P!=Q
      rel=[i for i,(P,Q) in enumerate(OFF) if P in rows and Q in cols]
      for m in range(4096):
        Z={OFF[i] for i in rel if m>>i&1}
        br={frozenset(Q for Q in cols if (P,Q) not in Z) for P in rows}-{frozenset()}
        bc={frozenset(P for P in rows if (P,Q) not in Z) for Q in cols}-{frozenset()}
        tab[m,S-1,T-1,X-1]=min(len(br),len(bc))
np.save('phitab4.npy',tab); print('built',round(time.time()-t))
