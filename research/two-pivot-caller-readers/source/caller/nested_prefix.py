"""Exact ideal prefixes for nested three-response replacements.

This is a construction helper, not a native admission or a receipt.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
from itertools import combinations
from pivot_plane_probe import Z, I, N, add, neg, mul, inv, eye, mm, es, null, summ


def skeleton(q, betas=None):
    n = 2*q+2
    out = []
    def a(d,s,c=I): out.append(('a',d,s,c))
    def query(d,s,depth):
        if depth == 0:
            out.append(('q',d,s,N))
            return
        b,c = 2*depth, 2*depth+1
        a(c,d,neg(I));a(s,b)
        query(d,s,depth-1)
        a(s,b,neg(I));a(d,c)
        out.append(('q',b,d,N))
        a(d,c,neg(I))
        out.append(('q',c,b,N))
        a(b,s);a(c,d);a(d,c,neg(I))
        out.append(('s',b,c,I))
    # All independent incoming b fields use the same paid input exposure.
    betas=[F(1)]*q if betas is None else list(map(F,betas))
    for j in range(1,q+1):a(2*j,1,(F(0),betas[j-1]))
    query(1,0,q)
    out.append(('q',0,1,N));out.append(('q',1,0,N))
    out.append(('s',0,1,I))
    for j in range(1,q+1):a(2*j,1,(F(0),-betas[j-1]))
    return n,out


def prefixes(q,betas=None):
    n,ops=skeleton(q,betas)
    M=eye(n);out=[]
    for typ,d,s,c in ops:
        if typ=='s':
            M=[list(row) for row in M]
            M[d],M[s]=M[s],M[d]
        else:
            M=mm(es(n,d,s,c),M)
        if typ=='q':out.append((M,s,d))
    target=[[N if i==j else Z for j in range(n)]for i in range(n)]
    if M!=target:raise ValueError('nested ideal skeleton not full N')
    return ops,out


def rref_null(A):
    return null(A)


def source_choice(B,src,prefer_real=True):
    """Choose E-column coefficients with source1, minimizing N-row support.

    B has two E-columns. The search is only the finitely many possible
    active constraints of its at-most-two-dimensional affine solution.
    """
    n=len(B)
    # c_j=a_j+N*b_j.  Source normalization is exact (real1,N0).
    realrows=[];imagrows=[]
    for row in B:
        realrows.append([z for x in row for z in (x[0],-x[1])])
        imagrows.append([z for x in row for z in (x[1],x[0])])
    def solve(A,b):
        m=len(A);k=4;A=[list(row)+[rhs]for row,rhs in zip(A,b)];r=0;p=[]
        for j in range(k):
            h=next((h for h in range(r,m)if A[h][j]),None)
            if h is None:continue
            A[r],A[h]=A[h],A[r];v=A[r][j];A[r]=[x/v for x in A[r]]
            for h in range(m):
                if h!=r and A[h][j]:
                    v=A[h][j];A[h]=[x-v*y for x,y in zip(A[h],A[r])]
            p.append(j);r+=1
        if any(not any(row[:k]) and row[k]for row in A):return None
        x=[F(0)]*k
        for h,j in enumerate(p):x[j]=A[h][k]
        return x
    candidates=[]
    # Two normalization constraints leave at most two independent choices.
    for count in range(3):
        for chosen in combinations(range(n),count):
            A=[realrows[src],imagrows[src]]+[imagrows[i]for i in chosen]
            x=solve(A,[F(1),F(0)]+[F(0)]*count)
            if x is None:continue
            u=[summ(mul(z,(x[2*j],x[2*j+1]))for j,z in enumerate(row))for row in B]
            if u[src]!=I:raise ValueError('source normalization')
            key=(sum(z[1]!=0 for z in u),sum(z!=Z for z in u),sum(abs(z[0])+abs(z[1])for z in u))
            candidates.append((key,u,x))
    if not candidates:return None
    return min(candidates,key=lambda t:t[0])


def probe(q,c_weights=None,betas=None):
    n=2*q+2;ops,pre=prefixes(q,betas)
    weights=[1]*q if c_weights is None else c_weights
    V=[[I if i==1 else Z, (F(weights[(i-3)//2]),F(0))if i>=3 and i%2 else Z]for i in range(n)]
    rows=[]
    for M,src,dst in pre:
        answer=source_choice(mm(M,V),src)
        rows.append((src,dst,answer))
    return rows


if __name__=='__main__':
    for q in(1,2,3):
        print('q',q)
        for src,dst,res in probe(q):
            print(src,'->',dst, None if res is None else (res[0],res[1]))
