# f(6), f(5): over all 788035 three-dim subspaces Z of the class space, ports with labels in Z^perp (and one more class). PROOF.md 4, Step 2. Apache-2.0.
import sys, itertools, numpy as np, time
import _paths
from labels import *
cl=np.zeros((512,v),dtype=bool)
for c in range(1,512): cl[c]=[cls[c]>>t&1 for t in range(v)]
liv=~cl  # live sets of single classes
from collections import Counter
hist3=Counter(); f6=0; f5=0; T=time.time(); n=0
for a in range(1,512):
  for b in range(a+1,512):
    if (a^b)<b: continue
    P=liv[a]&liv[b]&liv[a^b]
    for c in range(b+1,512):
      if c in (a^b,): continue
      # canonical: c minimal of its coset beyond b... require c < all of a^c,b^c,a^b^c
      if min(a^c,b^c,a^b^c)<c: continue
      Q=P&liv[c]&liv[a^c]&liv[b^c]&liv[a^b^c]
      s=int(Q.sum()); n+=1; hist3[s]+=1
      if s>f6: f6=s
      if s>f5:
        m=int((Q[None,:]&liv).sum(1)[1:].max())
        # exclude classes inside Z (they give Q itself)
        if m> f5:
          # recompute excluding Z members
          Zs={a,b,a^b,c,a^c,b^c,a^b^c}
          vals=(Q[None,:]&liv).sum(1)
          m=max(int(vals[x]) for x in range(1,512) if x not in Zs)
          f5=max(f5,m)
print('3-dim Z count',n,'f(6)',f6,'f(5)',f5,'hist',sorted(hist3.items()),round(time.time()-T),'s')
