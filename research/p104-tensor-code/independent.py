#!/usr/bin/env python3
"""Independent Fraction matrix/evaluator oracle; primary builders supply words only."""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path


def need(ok,msg):
    if not ok:raise ValueError(msg)


def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(row) for row in zip(*a)]
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def plus(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(a,c):return [[c*x for x in row] for row in a]
def kron(a,b):return [[x*y for x in row for y in line] for row in a for line in b]
def block(a,b,c,d):return [r+s for r,s in zip(a,b)]+[r+s for r,s in zip(c,d)]
def zero(n):return [[Q(0) for _ in range(n)] for _ in range(n)]
def inverse(a):
    n=len(a);x=[r[:]+s for r,s in zip(a,eye(n))]
    for j in range(n):
        k=next(i for i in range(j,n) if x[i][j]);x[j],x[k]=x[k],x[j]
        t=x[j][j];x[j]=[v/t for v in x[j]]
        for i in range(n):
            if i!=j:
                t=x[i][j];x[i]=[v-t*w for v,w in zip(x[i],x[j])]
    return [r[n:] for r in x]


def symbolic_word(word,size):
    a=eye(size)
    for op in word:
        if op[0]=='add':a[op[1]]=[x+op[3]*y for x,y in zip(a[op[1]],a[op[2]])]
        elif op[0]=='half':a[op[1]]=[x/2 for x in a[op[1]]]
        elif op[0]=='double':a[op[1]]=[x*2 for x in a[op[1]]]
        else:raise ValueError('unknown operation')
    return a


def main():
    spec=importlib.util.spec_from_file_location('word_builders',Path(__file__).with_name('verify.py'));w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
    columns=0;controls=0
    for b in ([[1,-1]],[[1,0],[-1,1]]):
        p=len(b);n=p+len(b[0]);I=eye(n);P=zero(n)
        for i in range(p):P[i][i]=1
        U=eye(n)
        for i,row in enumerate(b):
            for j,c in enumerate(row,p):U[i][j]=Q(c,2)
        Ui=inverse(U);Ut=transpose(U);Uit=transpose(Ui);A=mm(mm(Ut,P),U);M=mm(U,Ut);N=mm(Uit,Ui)
        L=kron(U,Uit);Li=inverse(L);Lit=transpose(Li);C=block(L,zero(n*n),zero(n*n),Lit);Ci=inverse(C)
        ar=kron(A,I);ac=kron(I,A);II=eye(n*n);Z=zero(n*n)
        lower=block(II,Z,ar,II);upper=block(II,scale(ac,-1),Z,II)
        encoded_lower=block(II,Z,kron(P,M),II);encoded_upper=block(II,scale(kron(M,P),-1),Z,II)
        need(mm(mm(C,lower),Ci)==encoded_lower,'lower tensor identity')
        need(mm(mm(C,upper),Ci)==encoded_upper,'upper tensor identity')
        need(symbolic_word(w.code_word(b),2*n*n)==C,'literal encoder all basis')
        need(symbolic_word(w.code_word(b,True),2*n*n)==Ci,'literal decoder all basis')
        need(symbolic_word(w.coded_pair(b),2*n*n)==mm(encoded_upper,encoded_lower),'literal coded pair all basis')
        need(symbolic_word(w.reference_pair(b),2*n*n)==mm(upper,lower),'literal reference pair all basis')
        # Full identity corrections: the missing terms are not the zero operator.
        full_lower=block(II,Z,II,II);full_upper=block(II,scale(II,-1),Z,II)
        need(mm(mm(C,full_lower),Ci)==block(II,Z,kron(N,M),II),'full lower correction')
        need(mm(mm(C,full_upper),Ci)==block(II,scale(kron(M,N),-1),Z,II),'full upper correction')
        need(encoded_lower!=mm(mm(C,full_lower),Ci),'omitted identity correction rejected');controls+=1
        need(kron(P,M)!=kron(P,I),'discarded cross-axis M rejected');controls+=1
        wrong=list(w.code_word(b));ix=next(i for i,o in enumerate(wrong) if o[0]=='double');wrong.pop(ix)
        need(symbolic_word(wrong,2*n*n)!=C,'missing donor restoration rejected');controls+=1
        # Noncommuting physical charts: exact cut order, no donated basis move.
        size=2*n*n
        # Two address coordinates per physical role: G never mixes owners.
        if n==3:
            cc=kron(C,eye(2));cci=kron(Ci,eye(2));lo=kron(lower,eye(2));up=kron(upper,eye(2));G=[]
            for cut in range(3):
                g=eye(2*size)
                for owner in range(size):g[2*owner][2*owner+1]=cut+owner+1
                G.append(g)
            first=mm(mm(mm(mm(G[1],cc),lo),cci),inverse(G[0]))
            second=mm(mm(mm(mm(G[2],cc),up),cci),inverse(G[1]))
            total=mm(mm(mm(mm(G[2],cc),mm(up,lo)),cci),inverse(G[0]))
            need(mm(second,first)==total,'ordered physical cut cancellation')
            need(mm(cc,G[1])!=mm(G[1],cc),'free physical chart commute rejected');controls+=1
        columns+=size
    print('PASS_P104_TENSOR_CODE_INDEPENDENT all_basis_columns='+str(columns)+' controls='+str(controls))

if __name__=='__main__':main()
