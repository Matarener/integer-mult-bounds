"""Unchanged pure source helpers; unrelated synthesis omitted. Apache-2.0; Codex assistance."""
from joint_algebra import *

def inverse(E,m):
 out=[]
 for event in reversed(E):
  e=dict(event)
  if e['kind']=='ADD':e['coefficient']=str(-F(e['coefficient']))
  elif e['kind']=='SCALE':e['coefficient']=str(1/F(e['coefficient']))
  elif e['kind']!='BANK_SWAP':e['x_monomial']=qc.decode(e,m).inv().data()
  out.append(e)
 return out

def pullback(C,e,m):
 C=[[dict(x)for x in row]for row in C];kind=e['kind']
 if kind=='ADD':
  d,s,c=e['dst'],e['src'],F(e['coefficient']);C[d]=[add(x,scale(y,-c))for x,y in zip(C[d],C[s])]
  for row in C:row[s]=add(row[s],scale(row[d],c))
 elif kind=='BANK_SWAP':
  i,j=e['banks'];C[i],C[j]=C[j],C[i]
  for row in C:row[i],row[j]=row[j],row[i]
 elif kind=='SCALE':
  b,c=e['bank'],F(e['coefficient']);C[b]=[scale(x,1/c)for x in C[b]]
  for row in C:row[b]=scale(row[b],c)
 else:
  b=e['bank'];G,Gi=mono(qc.decode(e,m)),mono(qc.decode(e,m).inv());C[b]=[product(Gi,x)for x in C[b]]
  for row in C:row[b]=product(row[b],G)
 return C

def pair_columns(P,i,j,n,m):
 """A=V e_b, B=e_b^T V^-1, V=E_j...E_(i+1)."""
 I=mono(qc.identity(m));b=P[i]['bank'];A=[dict(I)if r==b else{}for r in range(n)];B=[dict(x)for x in A]
 for e in P[i+1:j+1]:
  kind=e['kind']
  if kind=='ADD':
   d,s,c=e['dst'],e['src'],F(e['coefficient']);A[d]=add(A[d],scale(A[s],c));B[s]=add(B[s],scale(B[d],-c))
  elif kind=='BANK_SWAP':
   d,s=e['banks'];A[d],A[s]=A[s],A[d];B[d],B[s]=B[s],B[d]
  elif kind=='SCALE':
   d,c=e['bank'],F(e['coefficient']);A[d]=scale(A[d],c);B[d]=scale(B[d],1/c)
  else:
   d=e['bank'];g=qc.decode(e,m);A[d]=product(mono(g),A[d]);B[d]=product(B[d],mono(g.inv()))
 need(summ(product(B[r],A[r])for r in range(n))==I,'paired transported row/column BA=I')
 return A,B
