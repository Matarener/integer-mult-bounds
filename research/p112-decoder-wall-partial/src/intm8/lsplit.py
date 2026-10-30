# numeric check of the level-split lemma: D(x) S D(y) == sum_j (x o 1[mu>=j]) (y o 1[lam==j])^T, S = [lam(s) <= mu(t)]
import numpy as np
rng=np.random.default_rng(1)
for tr in range(2000):
    n=10; L=rng.integers(1,5)
    mu=rng.integers(0,L+1,n); lam=rng.integers(0,L+1,n)   # 0 = unused
    x=rng.standard_normal(n)*(mu>0); y=rng.standard_normal(n)*(lam>0)
    S=((lam[None,:]<=mu[:,None])&(lam[None,:]>0)&(mu[:,None]>0)).astype(float)
    A=np.diag(x)@S@np.diag(y)
    B=sum(np.outer(x*(mu>=j),y*(lam==j)) for j in range(1,L+1))
    assert np.abs(A-B).max()<1e-12
print('LSPLIT PASS 2000')
