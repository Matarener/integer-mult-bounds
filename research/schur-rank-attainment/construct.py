"""Attainment through a rank minor; literal prescribed Schur witnesses.
New construction: SHIN09-git, substantial OpenAI Codex assistance, Apache-2.0.
Sector factorization and ordered maps: Wojt #5128, Petalas #6031 and lineage.
"""
from pathlib import Path
from types import ModuleType


def source_module(name):
    path=Path(__file__).with_name(name+".py")
    mod=ModuleType(name)
    mod.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),"exec"),mod.__dict__)
    return mod


la=source_module("linear")
Mat,need,eye,zeros,block=la.Mat,la.need,la.eye,la.zeros,la.block


def compressed(A,B,H):
    d,p=A.r,A.p
    need(d>0 and all((X.r,X.c,X.p)==(d,d,p) for X in (A,B,H)),"pivot shapes")
    A.inverse()
    B.inverse()
    return [eye(d,p)-A-B+H,A-H,B-H,H]


def ordered_maps(A,B,H):
    d,p=A.r,A.p
    ai,bi=A.inverse(),B.inverse()
    O=zeros(d,d,p)
    G=block([[O,ai],[-bi@H,-bi],[eye(d,p)-bi@H,ai-bi]])
    Gp=block([[ai,-bi,ai-bi],[O,H@bi,H@bi-eye(d,p)]])
    return G,Gp


def defect_pairing(A,B,H):
    ts=compressed(A,B,H)
    d,p=A.r,A.p
    erows,kcols,emeta,kmeta=[],[],[],[]
    for j,T in enumerate(ts[1:]):
        for w in T.T.kernel():
            wa=(Mat([w],p,d)@A).a[0]
            e=(tuple(wa)+tuple(w) if j==0 else
               (0,)*d+tuple(w) if j==1 else
               (0,)*d+tuple(-x for x in w))
            erows.append(e)
            emeta.append((j,w))
        for z in T.kernel():
            az=(A@la.from_columns([z],d,p)).T.a[0]
            k=(tuple(-x for x in z)+tuple(az) if j==0 else
               tuple(-x for x in z)+(0,)*d if j==1 else
               tuple(z)+(0,)*d)
            kcols.append(k)
            kmeta.append((j,z))
    E=Mat(erows,p,2*d)
    K=la.from_columns(kcols,2*d,p)
    nu=len(erows)
    need(E.rank()==K.rank()==nu,"independent defect lifts")
    G,Gp=ordered_maps(A,B,H)
    # Verify every lifted row/vector against its pure-sector original.
    for e,(j,w) in zip(E.a,emeta):
        pure=[0]*(3*d)
        pure[j*d:(j+1)*d]=w
        need(Mat([e],p,2*d)@Gp==Mat([pure],p,3*d),"left lift identity")
    for k,(j,z) in zip(K.T.a,kmeta):
        pure=[0]*(3*d)
        pure[j*d:(j+1)*d]=z
        need(G@la.from_columns([k],2*d,p)==la.from_columns([pure],3*d,p),"right lift identity")
    C=E@K
    return ts,C,emeta,kmeta


def minor_chain(C):
    """Pairs of retained coordinate rows/columns; never mixes sector bases."""
    need(C.r==C.c,"square defect pairing")
    nu=C.r
    rank=C.rank()
    _,col_piv=la.eliminate(C.a,C.c,C.p)
    small=C.take(list(range(nu)),col_piv)
    _,row_piv=la.eliminate(small.T.a,small.T.c,C.p)
    core_i=set(row_piv)
    core_j=set(col_piv)
    ii,jj=list(range(nu)),list(range(nu))
    chain=[(tuple(ii),tuple(jj),"start")]
    for i in list(ii):
        if i not in core_i:
            ii.remove(i)
            chain.append((tuple(ii),tuple(jj),"one row"))
    for j in list(jj):
        if j not in core_j:
            jj.remove(j)
            chain.append((tuple(ii),tuple(jj),"one column"))
    need(len(ii)==len(jj)==rank and C.take(ii,jj).rank()==rank,"maximal rank minor")
    while ii:
        size=len(ii)
        found=None
        for i in ii:
            for j in jj:
                ni=[x for x in ii if x!=i]
                nj=[x for x in jj if x!=j]
                if C.take(ni,nj).rank()==size-1:
                    found=(ni,nj)
                    break
            if found is not None:
                break
        need(found is not None,"nonzero cofactor exists")
        ii,jj=found
        chain.append((tuple(ii),tuple(jj),"paired row/column"))
    return chain


def plan(A,B,H):
    ts,C,emeta,kmeta=defect_pairing(A,B,H)
    d,p=A.r,A.p
    nu=C.r
    n0=sum(T.rank() for T in ts)
    nmax=ts[0].rank()+3*d+nu
    rho0=2*d-2*nu+C.rank()
    states={}
    for ii,jj,kind in minor_chain(C):
        rho=2*d-len(ii)-len(jj)+C.take(ii,jj).rank()
        n=nmax-len(ii)-len(jj)
        need(rho not in states,"rank must rise strictly along retained chain")
        need(n==max(n0+rho-rho0,nmax-2*(2*d-rho)),"sharp dimension law")
        ibases,nbases=[],[]
        for j in range(3):
            annihilators=[emeta[i][1] for i in ii if emeta[i][0]==j]
            ibases.append(Mat(annihilators,p,d).kernel())
            nbases.append([kmeta[k][1] for k in jj if kmeta[k][0]==j])
        states[rho]={"n":n,"I":ibases,"N":nbases,"kind":kind,
                     "rows":list(ii),"columns":list(jj)}
    need(sorted(states)==list(range(rho0,2*d+1)),"complete rank interval")
    return {"n0":n0,"nmax":nmax,"rho0":rho0,"nu":nu,"pairing_rank":C.rank(),
            "pairing":C,"states":states,"sectors":ts}


def sector_factors(T,ibasis,nbasis):
    d,p=T.r,T.p
    sigma=T.image()
    standard=eye(d,p).a
    full=sigma+la.extension(sigma,standard,d,p)
    coordinates=la.from_columns(full,d,p).inverse()
    phi=(coordinates@T).take(list(range(len(sigma))),list(range(d)))
    kb=la.extension(nbasis,T.kernel(),d,p)
    basis=list(nbasis)+kb
    basis+=la.extension(basis,standard,d,p)
    coords=la.from_columns(basis,d,p).inverse()
    psi=coords.take(list(range(len(nbasis),len(nbasis)+len(kb))),list(range(d)))
    tau=la.extension(sigma,ibasis,d,p)
    X=la.from_columns(sigma+[(0,)*d]*len(kb)+tau,d,p)
    Y=la.stack([phi,psi,zeros(len(tau),d,p)])
    need(X@Y==T,"sector factor product")
    need(X.rank()==len(ibasis) and d-Y.rank()==len(nbasis),"sector factor dimensions")
    need(all(all(not x for x in (Y@la.from_columns([v],d,p)).T.a[0]) for v in nbasis),
         "sector kernel containment")
    return X,Y


def build(A,B,H,state):
    ts=compressed(A,B,H)
    d,p=A.r,A.p
    factors=[sector_factors(ts[0],ts[0].image(),ts[0].kernel())]
    factors += [sector_factors(T,I,N) for T,I,N in zip(ts[1:],state["I"],state["N"])]
    projection=la.join([X for X,Y in factors])
    inclusion=la.stack([Y for X,Y in factors])
    need(projection@inclusion==eye(d,p),"split boundary pi i")
    n=inclusion.r
    basis=inclusion.image()+projection.kernel()
    change=la.from_columns(basis,n,p)
    inv=change.inverse()
    pd,qd=[],[]
    for (X,Y),(pv,qv) in zip(factors,((0,0),(1,0),(0,1),(1,1))):
        pd += [pv]*Y.r
        qd += [qv]*Y.r
    P0=Mat([[pd[i]*int(i==j) for j in range(n)] for i in range(n)],p,n)
    Q0=Mat([[qd[i]*int(i==j) for j in range(n)] for i in range(n)],p,n)
    P,Q=inv@P0@change,inv@Q0@change
    need(n==state["n"],"realized dimension")
    return P,Q


def literal_rank(A,B,H,P,Q):
    d,n,p=A.r,P.r,A.p
    need(n>=d and (P.r,P.c,P.p)==(Q.r,Q.c,Q.p)==(n,n,p),"literal shapes")
    need(P@P==P and Q@Q==Q and P@Q==Q@P,"commuting idempotents")
    top=list(range(d)); rest=list(range(d,n))
    need(P.take(top,top)==A and Q.take(top,top)==B and (P@Q).take(top,top)==H,
         "prescribed blocks")
    S=P.take(rest,rest)-P.take(rest,top)@A.inverse()@P.take(top,rest)
    Z=Q.take(rest,rest)-Q.take(rest,top)@B.inverse()@Q.take(top,rest)
    return (S@Z-Z@S).rank()
