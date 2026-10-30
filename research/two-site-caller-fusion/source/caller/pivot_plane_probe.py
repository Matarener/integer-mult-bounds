#!/usr/bin/env python3
"""Bounded n4 source-retraction screen; actual code/native closure not inferred."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json, sys
sys.dont_write_bytecode=True
Z=(F(0),F(0));I=(F(1),F(0));N=(F(0),F(1))
def add(a,b):return(a[0]+b[0],a[1]+b[1])
def neg(a):return(-a[0],-a[1])
def mul(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def inv(a):
 d=a[0]*a[0]+a[1]*a[1]
 if not d:raise ValueError('nonunit')
 return(a[0]/d,-a[1]/d)
def eye(n):return [[I if i==j else Z for j in range(n)] for i in range(n)]
def mm(A,B):return [[summ(mul(x,y) for x,y in zip(r,c)) for c in zip(*B)] for r in A]
def summ(xs):
 a=Z
 for b in xs:a=add(a,b)
 return a
def es(n,d,s,c):
 A=eye(n);A[d][s]=c;return A
def null(A):
 A=[list(r) for r in A];m=len(A);n=len(A[0]);p=[];r=0
 for c in range(n):
  k=next((k for k in range(r,m) if A[k][c]),None)
  if k is None:continue
  A[r],A[k]=A[k],A[r];v=A[r][c];A[r]=[x/v for x in A[r]]
  for j in range(m):
   if j!=r and A[j][c]:
    v=A[j][c];A[j]=[x-v*y for x,y in zip(A[j],A[r])]
  p.append(c);r+=1
  if r==m:break
 out=[]
 for c in range(n):
  if c in p:continue
  v=[F(0)]*n;v[c]=F(1)
  for j,d in enumerate(p):v[d]=-A[j][c]
  out.append(v)
 return out

def rank(A):
 A=[list(r) for r in A];m=len(A);n=len(A[0]);r=0
 for c in range(n):
  k=next((k for k in range(r,m) if A[k][c]!=Z),None)
  if k is None:continue
  A[r],A[k]=A[k],A[r];v=inv(A[r][c]);A[r]=[mul(x,v) for x in A[r]]
  for j in range(m):
   if j!=r and A[j][c]!=Z:
    v=A[j][c];A[j]=[add(x,neg(mul(v,y))) for x,y in zip(A[j],A[r])]
  r+=1
  if r==m:break
 return r

def prefixes(n=4):
 ops=[('q',0,1,N),('a',0,2,I),('q',1,0,N),('a',0,2,neg(I)),('a',1,3,I),('q',2,1,N),('a',1,3,neg(I)),('q',3,2,N),('a',1,3,I),('a',2,0,I),('q',0,3,neg(N)),('a',2,0,neg(I))]
 M=eye(n);Mi=eye(n);out=[]
 for typ,d,s,c in ops:
  M=mm(es(n,d,s,c),M);Mi=mm(Mi,es(n,d,s,neg(c)))
  if typ=='q':out.append((M,Mi,s,d))
 return out

def real_source(B,src):
 ns=null([[z for x in r for z in (x[1],x[0])] for r in B])
 for v in ns:
  u=[summ(mul(x,(v[2*j],v[2*j+1])) for j,x in enumerate(r)) for r in B]
  if any(x[1] for x in u):raise ValueError('nonreal null witness')
  if u[src][0]:return [x[0]/u[src][0] for x in u]
 return None

def serial(A):return [[[str(x),str(y)] for x,y in r] for r in A]
def run():
 pre=prefixes();found=[];count=0;dimension_fail=0
 for tail1 in product((-1,0,1),repeat=3):
  u1=list(map(F,tail1));u1.insert(pre[0][2],F(1))
  v1=mm(pre[0][1],[[(x,F(0))] for x in u1])
  for tail2 in product((-1,0,1),repeat=3):
   count+=1;u2=list(map(F,tail2));u2.insert(pre[1][2],F(1))
   v2=mm(pre[1][1],[[(x,F(0))] for x in u2])
   V=[[v1[i][0],v2[i][0]] for i in range(4)]
   if rank(V)!=2:dimension_fail+=1;continue
   choices=[]
   for M,Mi,src,dst in pre:
    u=real_source(mm(M,V),src)
    if u is None:break
    choices.append([str(x) for x in u])
   else:found.append({'first_source':list(map(str,u1)),'second_source':list(map(str,u2)),'input_plane':serial(V),'source_retractions':choices})
 return {'status':'BOUNDED_EXACT_SOURCE_RETRACTION_SCREEN','candidate_pairs':count,'source_tail_alphabet':[-1,0,1],'dimension_failures':dimension_fail,'solutions':found,'scope':'Old n4 five-shear ideal topology only; arbitrary real source-retraction columns allowed at later queries. Source-code algebra, native encoder and actual correction are not inferred.','native_invoice_if_admitted':'Same five raw carriers plus full global fresh progress; constant bank GL source changes only. Any N-dependent initial plane encoder and terminal correction remain paid/open.'}
if __name__=='__main__':
 out=run();Path(__file__).with_name('PIVOT-PLANE-PROBE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],out['candidate_pairs'],'pairs',len(out['solutions']),'solutions')
 if out['solutions']:print(json.dumps(out['solutions'][0]))
