# f(k) for k <= 4: max number of the 104 distinct port labels in a k-dim subspace of F2^9 (exhaustive over spans). PROOF.md 4, Step 2. Apache-2.0.
import sys, itertools
import _paths
from labels import *
w=[sum(((cls[1<<i]>>t)&1)<<i for i in range(9)) for t in range(v)]
from collections import Counter
cnt=Counter(w); print('distinct labels',len(cnt),'mult',sorted(set(cnt.values())), 'zero label?',cnt.get(0,0))
labs=sorted(cnt)
def span(gs):
    S={0}
    for g in gs: S|={x^g for x in S}
    return frozenset(S)
f={}
seen=set()
for k in range(1,5):
    best=0; arg=None
    for comb in itertools.combinations(labs,k):
        S=span(comb)
        if len(S)!=1<<k: continue
        n=sum(cnt[x] for x in S if x in cnt)
        if n>best: best=n; arg=comb
    f[k]=best; print('f(%d)='%k,best,flush=True)
