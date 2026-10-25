#!/usr/bin/env python3
"""Check determinant characters in exact finite local algebras.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product
from math import gcd,prod
import json


def require(c,m):
    if not c: raise ValueError(m)


class Field:
    def __init__(self,q):
        require(q in (2,3,4,5,7),'unsupported fixture field')
        self.q=q; self.p=2 if q==4 else q
        self.plus=[[a^b if q==4 else (a+b)%q for b in range(q)] for a in range(q)]
        def multiply(a,b):
            if q!=4: return a*b%q
            c=0
            for _ in range(2):
                if b&1: c^=a
                b>>=1; a<<=1
                if a&4: a^=7
            return c
        self.times=[[multiply(a,b) for b in range(q)] for a in range(q)]
    def add(self,a,b): return self.plus[a][b]
    def neg(self,a): return a if self.q==4 else -a%self.q
    def mul(self,a,b): return self.times[a][b]
    def power(self,a,n):
        out=1
        while n:
            if n&1: out=self.mul(out,a)
            a=self.mul(a,a); n//=2
        return out
    def inv(self,a):
        require(a!=0,'zero inverse'); return self.power(a,self.q-2)
    def det(self,A):
        A=[list(r) for r in A]; out=1
        for k in range(len(A)):
            pivot=next((i for i in range(k,len(A)) if A[i][k]),None)
            if pivot is None: return 0
            if pivot!=k: A[k],A[pivot]=A[pivot],A[k]; out=self.neg(out)
            out=self.mul(out,A[k][k]); iv=self.inv(A[k][k])
            for i in range(k+1,len(A)):
                if A[i][k]:
                    factor=self.mul(A[i][k],iv)
                    for j in range(k+1,len(A)):
                        A[i][j]=self.add(A[i][j],self.neg(self.mul(factor,A[k][j])))
        return out


class Algebra:
    def __init__(self,q,heights):
        self.F=Field(q); self.heights=heights; self.r=len(heights)
        self.cutoffs=[self.F.p**e for e in heights]
        self.monomials=list(product(*(range(n) for n in self.cutoffs)))
        self.N=len(self.monomials); self.index={m:i for i,m in enumerate(self.monomials)}
        self.zero=(0,)*self.N; self.one=(1,)+(0,)*(self.N-1)
        self.variables=[]
        for i in range(self.r):
            ex=[0]*self.r; ex[i]=1; v=[0]*self.N; v[self.index[tuple(ex)]]=1; self.variables.append(tuple(v))
        self.table=[]
        for a in self.monomials:
            row=[]
            for b in self.monomials:
                c=tuple(x+y for x,y in zip(a,b)); row.append(self.index.get(c,-1))
            self.table.append(row)
    def add(self,a,b): return tuple(self.F.add(x,y) for x,y in zip(a,b))
    def scaled(self,c,a): return tuple(self.F.mul(c,x) for x in a)
    def mul(self,a,b):
        out=[0]*self.N
        for i,x in enumerate(a):
            if x:
                for j,y in enumerate(b):
                    k=self.table[i][j]
                    if y and k>=0: out[k]=self.F.add(out[k],self.F.mul(x,y))
        return tuple(out)
    def power(self,a,n):
        out=self.one
        while n:
            if n&1: out=self.mul(out,a)
            a=self.mul(a,a); n//=2
        return out
    def tangent(self,images):
        indices=[v.index(1) for v in self.variables]
        return [[images[j][i] for j in range(self.r)] for i in indices]
    def substitution(self,images):
        powers=[]
        for a,n in zip(images,self.cutoffs):
            row=[self.one]
            for _ in range(1,n): row.append(self.mul(row[-1],a))
            powers.append(row)
        columns=[]
        for monomial in self.monomials:
            v=self.one
            for i,e in enumerate(monomial): v=self.mul(v,powers[i][e])
            columns.append(v)
        return columns


def image_index(p,q,heights):
    m=q-1; modulus=2*m; N=pow(p,sum(heights),modulus); h=m
    for e in heights:
        residue=N*(pow(p,e,modulus)-1)%modulus
        require(residue%2==0,'even exponent numerator')
        h=gcd(h,residue//2)
    return h


def verify_map(A,images,full):
    F=A.F
    require(all(a[0]==0 and A.power(a,n)==A.zero for a,n in zip(images,A.cutoffs)), 'invalid substitution relation')
    L=A.tangent(images); require(F.det(L)!=0,'singular tangent')
    for i,ei in enumerate(A.heights):
        for j,ej in enumerate(A.heights):
            require(ej<=ei or L[j][i]==0,'height flag violation')
    predicted=1
    for e in set(A.heights):
        ids=[i for i,h in enumerate(A.heights) if h==e]
        block=[[L[i][j] for j in ids] for i in ids]
        predicted=F.mul(predicted,F.power(F.det(block),A.N*(F.p**e-1)//2))
    columns=A.substitution(images); actual=F.det(list(zip(*columns)))
    require(actual==predicted,'automorphism determinant character')
    pairs=0
    indices=range(A.N) if full else [x.index(1) for x in A.variables]
    for i in indices:
        for j in range(A.N):
            k=A.table[i][j]; expected=A.zero if k<0 else columns[k]
            require(A.mul(columns[i],columns[j])==expected,'literal multiplication identity'); pairs+=1
    return actual,pairs


def main():
    maps=products=units=controls=0; contexts=[]; complete={}
    for q,heights in [(4,(2,)),(4,(1,1)),(2,(1,2))]:
        A=Algebra(q,heights); count=0; images_seen=set()
        radical=[(0,)+v for v in product(range(q),repeat=A.N-1)]
        for images in product(radical,repeat=A.r):
            if not A.F.det(A.tangent(images)): continue
            if any(A.power(a,n)!=A.zero for a,n in zip(images,A.cutoffs)): continue
            value,checks=verify_map(A,images,True); images_seen.add(value); count+=1; maps+=1; products+=checks
        predicted={A.F.power(c,image_index(A.F.p,q,heights)) for c in range(1,q)}
        require(images_seen==predicted,'complete automorphism image')
        expected={(4,(2,)):48,(4,(1,1)):2880,(2,(1,2)):2048}[(q,heights)]
        require(count==expected,'complete substitution census')
        complete[str((q,heights))]=count; contexts.append((q,heights))
    for q,heights in [(2,(1,1,1)),(3,(1,)),(3,(1,1)),(3,(1,1,1)),(5,(1,)),(5,(1,1)),(7,(1,)),(7,(1,1)),(4,(1,2))]:
        A=Algebra(q,heights); images_seen=set(); candidates=[]
        for i in range(A.r):
            for c in range(1,q):
                images=list(A.variables); images[i]=A.scaled(c,images[i]); candidates.append(images)
            for j in range(A.r):
                if i!=j and heights[j]<=heights[i]:
                    for c in range(1,q):
                        images=list(A.variables); images[i]=A.add(images[i],A.scaled(c,images[j])); candidates.append(images)
            nonlinear=[]
            for k,m in enumerate(A.monomials):
                if sum(m)<2: continue
                v=tuple(int(j==k) for j in range(A.N))
                if A.power(v,A.cutoffs[i])==A.zero: nonlinear.append(v)
            for v in nonlinear[:3]:
                images=list(A.variables); images[i]=A.add(images[i],v); candidates.append(images)
        for images in candidates:
            value,checks=verify_map(A,images,A.N<=9); images_seen.add(value); maps+=1; products+=checks
        h=image_index(A.F.p,q,heights)
        predicted={A.F.power(c,h) for c in range(1,q)}
        # Independent diagonal scales attain the entire product subgroup.
        attained={1}
        for i in range(A.r):
            values={A.F.power(c,A.N*(A.cutoffs[i]-1)//2) for c in range(1,q)}
            attained={A.F.mul(x,y) for x in attained for y in values}
        require(attained==predicted and images_seen<=predicted,'predicted determinant subgroup')
        contexts.append((q,heights))
    triples=0
    for q,heights in contexts:
        A=Algebra(q,heights); F=A.F; h=image_index(F.p,q,heights)
        selected=[]
        if A.N<=4:
            selected=[v for v in product(range(q),repeat=A.N) if v[0]]
        else:
            for c in range(1,q):
                for j in range(A.N):
                    v=[0]*A.N; v[0]=c
                    if j: v[j]=1
                    selected.append(tuple(v))
        for u in selected:
            columns=[A.mul(u,tuple(int(i==j) for i in range(A.N))) for j in range(A.N)]
            require(F.det(list(zip(*columns)))==F.power(u[0],A.N),'unit determinant'); units+=1
        zs={F.power(c,h) for c in range(1,q)}
        actual={(F.inv(F.mul(x,z)),F.inv(F.mul(y,z)),F.mul(F.mul(x,y),z))
                for x,y,z in product(range(1,q),range(1,q),zs)}
        predicted={(u,v,w) for u,v,w in product(range(1,q),repeat=3)
                   if F.power(F.mul(F.mul(u,v),w),(q-1)//h)==1}
        require(actual==predicted and len(actual)==(q-1)**3//h,'covariant determinant image'); triples+=len(actual)
    A=Algebra(4,(1,2)); bad=list(A.variables); bad[0]=A.add(bad[0],bad[1])
    require(A.power(bad[0],2)!=A.zero,'forbidden height mixing'); controls+=1
    require(image_index(2,4,(2,))==3 and image_index(2,4,(1,1))==1,'height-sensitive image'); controls+=1
    F=Field(7); require(F.power(4,2)!=1 and F.power(F.mul(F.mul(4,1),2),2)==1,'inverse input convention'); controls+=1
    for p in (2,3,5,7):
        for q in (p,p*p,p**3):
            for heights in ((1,),(2,),(1,2),(2,3),(3,3)):
                N=p**sum(heights); expected=q-1
                for e in heights: expected=gcd(expected,N*(p**e-1)//2)
                require(image_index(p,q,heights)==expected,'modular exponent extraction'); controls+=1
    require(image_index(2,4,(10**100+1,10**90+2))==1,'large binary-encoded heights'); controls+=1
    print('PASS_FROBENIUS_TENSOR_CHARACTERS '+json.dumps(dict(contexts=len(contexts),
        substitution_maps=maps,basis_product_checks=products,unit_maps=units,
        determinant_triples=triples,controls=controls,complete_automorphism_domains=complete),sort_keys=True))


if __name__=='__main__': main()
