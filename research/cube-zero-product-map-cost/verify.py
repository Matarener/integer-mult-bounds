#!/usr/bin/env python3
"""Check every quadratic relation space over four prime fields.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product
import json


def require(c,m):
    if not c: raise ValueError(m)


def rref(rows,p):
    rows=[list(r) for r in rows if any(r)]; k=0
    for j in range(3):
        pivot=next((i for i in range(k,len(rows)) if rows[i][j]%p),None)
        if pivot is None: continue
        rows[k],rows[pivot]=rows[pivot],rows[k]; t=pow(rows[k][j],-1,p)
        rows[k]=[x*t%p for x in rows[k]]
        for i in range(len(rows)):
            if i!=k:
                t=rows[i][j]; rows[i]=[(x-t*y)%p for x,y in zip(rows[i],rows[k])]
        k+=1
    return tuple(tuple(r) for r in rows[:k])


def projective(n,p):
    return [v for v in product(range(p),repeat=n) if any(v) and next(x for x in v if x)==1]


def subspaces(p):
    lines=projective(3,p); out={()}
    for v in lines: out.add(rref([v],p))
    for v in lines:
        j=next(i for i,x in enumerate(v) if x)
        basis=[]
        for k in range(3):
            if k!=j:
                a=[0]*3; a[k]=1; a[j]=-v[k]*pow(v[j],-1,p)%p; basis.append(a)
        out.add(rref(basis,p))
    out.add(((1,0,0),(0,1,0),(0,0,1)))
    return sorted(out,key=lambda x:(len(x),x))


def reduce3(v,K,p):
    v=list(v)
    for row in K:
        j=next(i for i,x in enumerate(row) if x); t=v[j]
        v=[(x-t*y)%p for x,y in zip(v,row)]
    return tuple(v)


MONOMIALS=[(0,0),(1,0),(0,1),(2,0),(1,1),(0,2)]


class Ring:
    def __init__(self,p,K):
        self.p,self.K=p,K; self.zero=(0,)*6; self.one=(1,0,0,0,0,0)
        self.x=(0,1,0,0,0,0); self.y=(0,0,1,0,0,0)
    def add(self,a,b): return tuple((x+y)%self.p for x,y in zip(a,b))
    def neg(self,a): return tuple(-x%self.p for x in a)
    def scalar(self,a): return (a%self.p,0,0,0,0,0)
    def mul(self,a,b):
        out=[0]*6
        for i,u in enumerate(MONOMIALS):
            for j,v in enumerate(MONOMIALS):
                m=(u[0]+v[0],u[1]+v[1])
                if sum(m)<=2: out[MONOMIALS.index(m)]+=a[i]*b[j]
        return tuple(x%self.p for x in out[:3])+reduce3(out[3:],self.K,self.p)
    def mm(self,A,B):
        return [[self.add(self.mul(A[i][0],B[0][j]),self.mul(A[i][1],B[1][j]))
                 for j in range(2)] for i in range(2)]
    def sm(self,A): return [[self.scalar(x) for x in r] for r in A]
    def act(self,A,v): return [self.add(self.mul(A[i][0],v[0]),self.mul(A[i][1],v[1])) for i in range(2)]


def inverse(A,p):
    a,b=A[0]; c,d=A[1]; t=pow((a*d-b*c)%p,-1,p)
    return [[d*t%p,-b*t%p],[-c*t%p,a*t%p]]


def main():
    contexts=cost_three=cost_two=basis_actions=zero_tests=controls=0
    by_field={}
    for p in (2,3,5,7):
        spaces=subspaces(p); require(len(spaces)==2*p*p+2*p+4,'complete subspace count')
        directions=projective(2,p); high=0
        for K in spaces:
            ring=Ring(p,K); z,o,x,y=ring.zero,ring.one,ring.x,ring.y
            M=[[ring.mul(x,x),ring.mul(x,y)],[ring.mul(x,y),ring.mul(y,y)]]
            C1=[[x,z],[y,o]]; C2=[[o,y],[z,z]]; C3=[[x,z],[z,o]]
            require(ring.mm(ring.mm(C1,C2),C3)==M,'three-factor word')
            zeros=[]
            for a,b in directions:
                for c,d in directions:
                    polynomial=((a*c)%p,(a*d+b*c)%p,(b*d)%p)
                    if not any(reduce3(polynomial,K,p)): zeros.append(((a,b),(c,d)))
                    zero_tests+=1
            if len(K)==0: predicted=True
            elif len(K)==1:
                a,b,c=K[0]
                predicted=(a!=0 and all((a*t*t+b*t+c)%p!=0 for t in range(p)))
            else: predicted=False
            require(predicted==(not zeros),'independent root and product classifications')
            if predicted:
                cost_three+=1; high+=1; word=[C1,C2,C3]
            else:
                cost_two+=1; phi,v=zeros[0]
                psi=next(w for w in directions if (phi[0]*w[1]-phi[1]*w[0])%p)
                t=next(w for w in directions if (w[0]*v[1]-w[1]*v[0])%p)
                G=[list(phi),list(psi)]; H=[[t[0],v[0]],[t[1],v[1]]]
                N=ring.mm(ring.mm(ring.sm(G),M),ring.sm(H))
                require(N[0][1]==z,'zero chart')
                F1=[[N[0][0],z],[N[1][0],o]]; F2=[[o,z],[z,N[1][1]]]
                word=[ring.sm(inverse(G,p)),F1,F2,ring.sm(inverse(H,p))]
                result=ring.sm([[1,0],[0,1]])
                for A in word: result=ring.mm(result,A)
                require(result==M,'two-factor free-chart construction')
            free=[i for i in range(3) if all(not row[i] or next(j for j,a in enumerate(row) if a)!=i for row in K)]
            for j in [0,1,2]+[i+3 for i in free]:
                basis=[0]*6; basis[j]=1
                for coordinate in range(2):
                    vector=[z,z]; vector[coordinate]=tuple(basis)
                    expected=ring.act(M,vector); actual=vector
                    for A in reversed(word): actual=ring.act(A,actual)
                    require(actual==expected,'complete input basis action')
                    basis_actions+=1
            if not K:
                require(ring.mm(ring.mm(C3,C2),C1)!=M,'order control')
                for factors in ([C2,C3],[C1,C3],[C1,C2]):
                    require(ring.mm(*factors)!=M,'dropped factor control'); controls+=1
                controls+=1
            contexts+=1
        require(high==1+p*(p-1)//2,'finite-field irreducible count')
        by_field[str(p)]={'relation_spaces':len(spaces),'cost_three':high}
    # A split quadratic line must not be called irreducible.
    for p in (2,3,5,7):
        K=rref([(0,1,0)],p)
        require(reduce3((0,1,0),K,p)==(0,0,0),'split-relation control'); controls+=1
    print('PASS_CUBE_ZERO_PRODUCT_MAP_COST '+json.dumps(dict(contexts=contexts,cost_two=cost_two,
        cost_three=cost_three,basis_actions=basis_actions,projective_products=zero_tests,
        controls=controls,fields=by_field),sort_keys=True))


if __name__=='__main__': main()
