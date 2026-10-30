"""Independent finite subspace enumeration, with no constructor imports.
SHIN09-git, substantial OpenAI Codex assistance. Apache-2.0.
Exhausts the #6031 sector choices using literal finite vector sets.
"""
from itertools import product
from functools import lru_cache


def rank_vectors(vectors,p):
    basis={}
    for source in vectors:
        v=[x%p for x in source]
        for j in sorted(basis):
            z=v[j]
            if z:
                v=[(x-z*y)%p for x,y in zip(v,basis[j])]
        pivot=next((j for j,x in enumerate(v) if x),None)
        if pivot is not None:
            z=pow(v[pivot],-1,p)
            basis[pivot]=tuple(x*z%p for x in v)
    return len(basis)


def independent_basis(space,p):
    out=[]
    for v in sorted(space):
        if rank_vectors(out+[v],p)>len(out):
            out.append(v)
    return tuple(out)


def mv(a,v,p):
    return tuple(sum(x*y for x,y in zip(row,v))%p for row in a)


def mm(a,b,p):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b)))%p
                       for j in range(len(b[0]))) for i in range(len(a)))


def inverse(a,p):
    n=len(a)
    out=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(a)]
    for c in range(n):
        j=next((j for j in range(c,n) if out[j][c]%p),None)
        if j is None:
            raise ValueError("singular oracle pivot")
        out[c],out[j]=out[j],out[c]
        scale=pow(out[c][c]%p,-1,p)
        out[c]=[x*scale%p for x in out[c]]
        for j in range(n):
            if j!=c:
                z=out[j][c]
                out[j]=[(x-z*y)%p for x,y in zip(out[j],out[c])]
    return tuple(tuple(row[n:]) for row in out)


@lru_cache(None)
def spaces(d,p):
    vectors=tuple(product(range(p),repeat=d))
    initial=frozenset({(0,)*d})
    seen={initial}
    todo=[initial]
    while todo:
        s=todo.pop()
        for v in vectors:
            if v in s:
                continue
            bigger=frozenset(tuple((x+t*y)%p for x,y in zip(w,v))
                             for w in s for t in range(p))
            if bigger not in seen:
                seen.add(bigger)
                todo.append(bigger)
    return tuple(sorted(seen,key=lambda s:(len(s),sorted(s))))


@lru_cache(None)
def geometry(t,p):
    d=len(t)
    vectors=tuple(product(range(p),repeat=d))
    image=frozenset(mv(t,v,p) for v in vectors)
    kernel=frozenset(v for v in vectors if mv(t,v,p)==(0,)*d)
    all_s=spaces(d,p)
    ims=[independent_basis(s,p) for s in all_s if image<=s]
    kers=[independent_basis(s,p) for s in all_s if s<=kernel]
    return ims,kers,rank_vectors(t,p)


def profile(A,B,H,p):
    d=len(A)
    ai,bi=inverse(A,p),inverse(B,p)
    ts=[tuple(tuple((int(i==j)-A[i][j]-B[i][j]+H[i][j])%p for j in range(d)) for i in range(d)),
        tuple(tuple((A[i][j]-H[i][j])%p for j in range(d)) for i in range(d)),
        tuple(tuple((B[i][j]-H[i][j])%p for j in range(d)) for i in range(d)),H]
    bih,hbi=mm(bi,H,p),mm(H,bi,p)
    # Build the maps entrywise rather than importing the primary block code.
    G=[]; Gp=[[0]*(3*d) for _ in range(2*d)]
    for s in range(3):
        for i in range(d):
            if s==0:
                G.append([0]*d+list(ai[i]))
            elif s==1:
                G.append([(-bih[i][j])%p for j in range(d)]+[(-bi[i][j])%p for j in range(d)])
            else:
                G.append([(int(i==j)-bih[i][j])%p for j in range(d)]+[(ai[i][j]-bi[i][j])%p for j in range(d)])
    for i in range(d):
        for j in range(d):
            Gp[i][j]=ai[i][j]
            Gp[i][d+j]=-bi[i][j]%p
            Gp[i][2*d+j]=(ai[i][j]-bi[i][j])%p
            Gp[d+i][d+j]=hbi[i][j]
            Gp[d+i][2*d+j]=(hbi[i][j]-int(i==j))%p
    M=mm(G,Gp,p)
    choices=[geometry(t,p) for t in ts[1:]]
    base=rank_vectors(ts[0],p)+sum(d-c[2] for c in choices)
    best={}
    examined=0
    def embedded(j,v):
        return (0,)*(j*d)+tuple(v)+(0,)*((2-j)*d)
    n_options=[]
    for ns in product(*(c[1] for c in choices)):
        nb=tuple(embedded(j,v) for j,basis in enumerate(ns) for v in basis)
        n_options.append(nb)
    for ims in product(*(c[0] for c in choices)):
        ib=tuple(embedded(j,v) for j,basis in enumerate(ims) for v in basis)
        mi=tuple(mv(M,v,p) for v in ib)
        for nb in n_options:
            rho=rank_vectors(mi+nb,p)-len(nb)
            cost=base+len(ib)-len(nb)
            best[rho]=min(best.get(rho,10**9),cost)
            examined+=1
    return best,examined
