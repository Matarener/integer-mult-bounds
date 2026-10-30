#!/usr/bin/env python3
"""Exact finite controls for the accompanying universal algebraic proof."""
import json
P=65537
IROOT=256

def need(ok,msg):
    if not ok: raise ValueError(msg)
def eye(n): return [[int(i==j) for j in range(n)] for i in range(n)]
def scale(A,c): return [[x*c%P for x in row]for row in A]
def mul(A,B):
    n=len(A);C=[[0]*n for _ in range(n)]
    for i,row in enumerate(A):
        for k,a in enumerate(row):
            if a:
                for j,b in enumerate(B[k]):
                    C[i][j]=(C[i][j]+a*b)%P
    return C
def block(A,B,C,D):return [a+b for a,b in zip(A,B)]+[c+d for c,d in zip(C,D)]
def diag(A,B):
    z=[[0]*len(A)for _ in A];return block(A,z,z,B)
def shear(A,lower=False):
    I=eye(len(A));z=scale(I,0)
    return block(I,z,A,I)if lower else block(I,A,z,I)
def gaussian(bits,axis):
    n=1<<bits;a=(1+IROOT)*pow(2,-1,P)%P;b=(1-IROOT)*pow(2,-1,P)%P
    return [[(a if i==j else 0)+(b if i==(j^(1<<axis))else 0)for j in range(n)]for i in range(n)]
def swapaxes(bits,j):
    n=1<<bits
    def f(x):
        return x if (x&1)==((x>>j)&1)else x^1^(1<<j)
    return [[int(i==f(k))for k in range(n)]for i in range(n)]
def product(xs,I):
    r=I
    for x in xs:r=mul(x,r)
    return r

def main():
    tests=0
    for stages in range(1,4):
        bits=stages+1;n=1<<bits;I=eye(n);Z=scale(I,0)
        Q=gaussian(bits,0);Qi=product([Q]*3,I)
        Ds=[gaussian(bits,j)for j in range(1,bits)]
        Cs=[swapaxes(bits,j)for j in range(1,bits)]
        As=[];Bs=[]
        for C,D in zip(Cs,Ds):
            R=mul(D,Q);A=mul(C,D);B=mul(D,C);L=diag(A,B)
            need(mul(C,C)==I and mul(C,R)==mul(R,C),'native premises')
            need(mul(A,Q)==mul(Q,B),'intertwiner')
            need(mul(C,Q)!=mul(Q,C),'control genuinely noncommutes Q')
            for lam in [0,1,P-1,2,pow(2,-1,P)]:
                F=mul(diag(D,D),shear(scale(mul(C,Qi),lam),True))
                N=mul(diag(D,D),shear(scale(mul(Q,C),-lam)))
                S=diag(C,I);T=diag(I,C)
                lf=shear(scale(Qi,lam),True);ub=shear(scale(Q,-lam))
                need(mul(mul(S,F),T)==mul(L,lf),'normalized forward')
                need(mul(mul(S,N),T)==mul(L,ub),'normalized backward')
                need(mul(L,lf)==mul(lf,L)and mul(L,ub)==mul(ub,L),'both shears commute')
                tests+=3
            J=block(Z,I,scale(I,-1),Z)
            low=shear(Qi,True);up=shear(scale(Q,-1))
            word=mul(J,mul(low,mul(L,mul(up,low))))
            need(word==diag(mul(B,Qi),mul(A,Q)),'actual ordinary swap boundary')
            need(word!=diag(mul(Qi,B),mul(A,Q)),'wrong side Q mutation detected')
            As.append(A);Bs.append(B)
        CP=product(Cs,I);DP=product(Ds,I)
        need(product(As,I)==mul(CP,DP),'ordered A product')
        need(product(Bs,I)==mul(DP,CP),'ordered B product')
        need(mul(CP,mul(DP,Q))==mul(mul(DP,Q),CP),'global Gaussian commutation')
        if stages>1:need(mul(Cs[0],Cs[1])!=mul(Cs[1],Cs[0]),'noncommuting code control')
        tests+=4
    print(json.dumps({'status':'PASS','exact_controls':tests,'modulus':P,'universal_evidence':'INTERTWINER-PROOF.txt','new_kappa':False},sort_keys=True))
if __name__=='__main__':main()
