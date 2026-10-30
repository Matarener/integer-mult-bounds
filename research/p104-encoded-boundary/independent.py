#!/usr/bin/env python3
"""Separately assembled dense operator checks, no imports from primary verifier."""
from fractions import Fraction as Q


def need(ok,msg):
    if not ok: raise ValueError(msg)


def zero(n): return [[Q(0) for _ in range(n)] for _ in range(n)]
def identity(n):
    a=zero(n)
    for i in range(n): a[i][i]=Q(1)
    return a

def mm(a,b):
    bt=list(zip(*b))
    return [[sum(x*y for x,y in zip(row,col)) for col in bt] for row in a]

def inverse(a):
    n=len(a); out=[row[:]+unit for row,unit in zip(a,identity(n))]
    for j in range(n):
        k=next(i for i in range(j,n) if out[i][j])
        out[j],out[k]=out[k],out[j]
        t=out[j][j];out[j]=[v/t for v in out[j]]
        for i in range(n):
            if i!=j:
                t=out[i][j]
                out[i]=[v-t*w for v,w in zip(out[i],out[j])]
    return [row[n:] for row in out]


def matrices(b,axis,chart=True):
    p=len(b);n=p+len(b[0]);size=2*n*n*2
    d=zero(n)
    for i in range(p):
        d[i][i]=1
        for j in range(n-p):d[i][j+p]=d[j+p][i]=Q(b[i][j],2)
    for i in range(n-p):
        for j in range(n-p):d[i+p][j+p]=sum(Q(b[k][i]*b[k][j],4) for k in range(p))-(i==j)
    def ix(bank,i,j,z):return ((bank*n+i)*n+j)*2+z
    L=identity(size);Pi=identity(size);S=zero(size)
    for bank in range(2):
        for i in range(n):
            for j in range(n):
                for z in range(2):S[ix(bank,i,j,z)][ix(1-bank,i,j,z)]=1
    for fixed in range(n):
        for k in range(n):
            i,j=(k,fixed) if axis==0 else (fixed,k)
            # Each T block invertible; different fibers/ports need not commute with D.
            t=[[Q(1),Q(i+j+1)],[Q(0),Q(1)]] if chart else identity(2)
            for z in range(2):
                r=ix(0,i,j,z);L[r]=[Q(0)]*size
                for ell in range(n):
                    ii,jj=(ell,fixed) if axis==0 else (fixed,ell)
                    L[r][ix(0,ii,jj,z)]=d[k][ell]
                if k>=p:
                    for w in range(2):L[r][ix(1,i,j,w)]=t[z][w]
                    for bank in range(2):
                        rr=ix(bank,i,j,z);Pi[rr]=[Q(0)]*size;Pi[rr][ix(1-bank,i,j,z)]=1
    return L,Pi,S


def main():
    checks=0
    for b in ([[1]],[[1,-1]]):
        for chart in (False,True):
            lr,pr,s=matrices(b,0,chart);lc,pc,_=matrices(b,1,chart)
            ar=mm(pr,lr);acbar=mm(mm(s,mm(pc,lc)),s)
            # Exact physical ordered product, reversed after the bank-orientation map.
            k=mm(mm(mm(mm(mm(s,pc),lc),s),inverse(lr)),pr)
            need(mm(k,ar)==acbar,'K A_r = Abar_c')
            need(mm(inverse(ar),ar)==identity(len(ar)),'independent inverse')
            need(ar!=acbar,'identity-boundary control')
            wrong=mm(mm(pc,lc),inverse(ar))
            need(mm(wrong,ar)!=acbar,'omitted source-target reversal control')
            wrong=mm(mm(mm(s,lc),s),inverse(ar))
            need(mm(wrong,ar)!=acbar,'omitted literal occupancy control')
            # Common address transform commutes only in homogeneous-chart test.
            if not chart:
                common=zero(len(ar))
                for j in range(0,len(ar),2):common[j][j+1]=1;common[j+1][j]=-1
                need(mm(common,ar)==mm(ar,common),'uniform completion control')
                need(mm(common,acbar)==mm(acbar,common),'reversed completion control')
            checks+=len(ar)
    print('PASS_P104_BOUNDARY_DENSE columns='+str(checks)+' chart_cases=4 negative_controls=12')

if __name__=='__main__':main()
