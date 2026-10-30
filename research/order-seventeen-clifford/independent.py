#!/usr/bin/env python3
"""Separately written exact integer audit; no imports from verify.py.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Retains Nick Petalas's PR6192 cap/Bell method and Ross Richardson's lineage.
"""
import json


def need(ok, why):
    if not ok: raise ValueError(why)


def add(x,y): return (x[0]+y[0],x[1]+y[1])
def mul(x,y): return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def conjugate(x): return x[0],-x[1]

def mm(a,b):
    columns=list(zip(*b))
    return [[(sum(x[0]*y[0]-x[1]*y[1] for x,y in zip(row,col)),
              sum(x[0]*y[1]+x[1]*y[0] for x,y in zip(row,col)))
             for col in columns] for row in a]

def adjoint(a):return [[conjugate(x) for x in col] for col in zip(*a)]
def scaled(a,n):return [[(n*x,n*y) for x,y in row] for row in a]
def identity(n):return [[(int(i==j),0) for j in range(n)] for i in range(n)]
def bits(n):return [(n>>j)&1 for j in range(4)]

def pauli(a,b):
    out=[[(0,0) for _ in range(16)] for _ in range(16)]
    for y in range(16):out[y^a][y]=((-1)**((y&b).bit_count()),0)
    return out

def f2mm(a,b):return [[sum(x*y for x,y in zip(row,col))%2 for col in zip(*b)] for row in a]
def f2rank(a):
    a=[row[:] for row in a];rank=0
    for c in range(len(a[0])):
        k=next((i for i in range(rank,len(a)) if a[i][c]),None)
        if k is None:continue
        a[k],a[rank]=a[rank],a[k]
        for i in range(rank+1,len(a)):
            if a[i][c]:a[i]=[x^y for x,y in zip(a[i],a[rank])]
        rank+=1
    return rank

A=[[0,0,0,1],[0,0,1,0],[0,1,0,1],[1,0,1,1]]
G=[]
for x in range(16):
    q=bits(x);parity=q[0]*q[3]+q[1]*q[2]+q[2]*q[3]
    row=[]
    for y in range(16):
        sign=(-1)**(parity+(x&y).bit_count())
        row.append((sign,0) if q[3] else (0,-sign))
    G.append(row)
I=identity(16);need(mm(G,adjoint(G))==scaled(I,16),'unitarity')
power=I;phi=[[(0,0) for _ in range(16)] for _ in range(16)]
for j in range(17):
    for x in range(16):
        for y in range(16):phi[x][y]=add(phi[x][y],mul((4**(16-j),0),power[x][y]))
    power=mm(power,G)
need(all(v==(0,0) for row in phi for v in row),'Phi17 exact zero')
need(power==scaled(I,4**17),'order17 exact identity')
trace=(sum(G[i][i][0] for i in range(16)),sum(G[i][i][1] for i in range(16)))
need(trace==(-4,0),'trace minus one')
for i in range(4):
    actual=mm(mm(G,pauli(1<<i,0)),adjoint(G))
    need(actual==scaled(pauli(0,1<<i),16),'X image')
    zmask=sum(A[j][i]<<j for j in range(4))
    expected=pauli(1<<i,zmask)
    phase=(0,1) if i==3 else (1,0)
    expected=[[mul(phase,v) for v in row] for row in expected]
    actual=mm(mm(G,pauli(0,1<<i)),adjoint(G))
    need(actual==scaled(expected,16),'Z image with exact phase')
# Eight qubits: x_D,x_S,z_D,z_S; Bell V=CNOT(D->S) H_D.
N=16;H=[[int(i==j) for j in range(N)] for i in range(N)]
for i in range(4):H[i],H[8+i]=H[8+i],H[i]
C=[[int(i==j) for j in range(N)] for i in range(N)]
for i in range(4):C[4+i][i]=1;C[8+i][12+i]=1
T=f2mm(C,H);Ti=f2mm(H,C)
need(f2mm(T,Ti)==[[int(i==j) for j in range(N)]for i in range(N)],'Bell inverse')
S=[[int(i==j) for j in range(N)]for i in range(N)]
for i in range(4):
    S[i]=[int(j==8+i) for j in range(N)]
    S[8+i]=[int(j==i)^(A[i][j-8] if 8<=j<12 else 0)for j in range(N)]
W=f2mm(f2mm(Ti,S),T)
B=[row[8:] for row in W[:8]]
expected=[[int(i==j) for j in range(4)]+[A[i][j]^int(i==j)for j in range(4)] for i in range(4)]
expected += [[int(i==j)for j in range(4)]*2 for i in range(4)]
need(B==expected and f2rank(B)==8,'full native B rank')
need(f2rank([[S[i][j]^int(i==j) for j in range(16)]for i in range(16)])==8,'active defect rank eight')
print(json.dumps({'status':'PASS_INDEPENDENT_ORDER17','unitarity_entries':256,'phi17_entries':256,'order17_entries':256,'pauli_images':8,'trace':'-1','active_symplectic_defect_rank':f2rank([[S[i][j]^int(i==j) for j in range(16)]for i in range(16)]),'Bell_B_rank':f2rank(B),'Bell_B':B},sort_keys=True))
