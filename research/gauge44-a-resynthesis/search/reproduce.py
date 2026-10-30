#!/usr/bin/env python3
"""Deterministically resynthesize the 14 dimension-four A blocks of #799.

The input is #799's X4 FULL-WORD (content hash 1e1d99ba...). Each block is
replaced by an exact rationally equivalent elementary word found with a fixed
seed and 4096 pivot-order trials. The replacement keeps the block frame and
all B/cleanup gates unchanged.
"""
import argparse, copy, gzip, hashlib, json, random
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

INPUT_SHA='1e1d99ba7aab877d6b573c41f7030ee73de9a52fee51d0a822ddaae71251999f'
OUTPUT_SHA='9094660307632862c3b09027a736fe93d397e88fa74806755a2e83198c060844'
SEED=20261013; TRIALS=4096

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def csha(x): return hashlib.sha256(enc(x)).hexdigest()
def regs(e): return [e[1]]+([e[2]] if e[0]=='add' else [])
def inverse(e):
 e=list(e)
 if e[0]=='add': e[3]=-e[3]
 else: e[2],e[3]=e[3],e[2]
 return e
def unit(q): return bool(q) and (abs(q.numerator)&(abs(q.numerator)-1)==0) and (q.denominator&(q.denominator-1)==0)
def dyadic(q): return q.denominator&(q.denominator-1)==0

def symstate(gs):
 rows={}
 for e in gs:
  for q in regs(e): rows.setdefault(q,{q:Q(1)})
  if e[0]=='add':
   t,s=e[1],e[2]; c=Q(e[3],e[4]); d=rows[t]
   for k,x in list(rows[s].items()):
    z=d.get(k,Q(0))+c*x
    if z:d[k]=z
    else:d.pop(k,None)
  else:
   t=e[1];c=Q(e[2],e[3]);rows[t]={k:c*x for k,x in rows[t].items()}
 return rows

def matrix_for(gs,ids):
 st=symstate(gs);return [[st.get(r,{r:Q(1)}).get(c,Q(0)) for c in ids] for r in ids]
def add_row(M,i,j,q,ids,F,ops):
 if q:
  assert dyadic(q);ops.append(['add',ids[i],ids[j],q.numerator,q.denominator,list(F)])
  M[i]=[a+q*b for a,b in zip(M[i],M[j])]
def scale_row(M,i,q,ids,F,ops):
 if q!=1:
  assert unit(q);ops.append(['scale',ids[i],q.numerator,q.denominator,list(F)]);M[i]=[q*a for a in M[i]]
def swap_rows(M,i,j,ids,F,ops):
 if i!=j:
  add_row(M,i,j,Q(1),ids,F,ops);add_row(M,j,i,Q(-1),ids,F,ops);add_row(M,i,j,Q(1),ids,F,ops);scale_row(M,j,Q(-1),ids,F,ops)

def eliminate(mat,ids,F,order,rng):
 M=copy.deepcopy(mat);ops=[];n=len(ids);remaining=set(range(n))
 for c in order:
  cand=[i for i in remaining if unit(M[i][c])]
  if not cand:return None
  def score(i):
   q=M[i][c];return sum(bool(a) for a in M[i])+sum(bool(M[k][c]) for k in remaining if k!=i)+(i!=c)*3+(q!=1)
  k=min(cand,key=lambda i:(score(i),i!=c,rng.random())) if rng.random()<.75 else rng.choice(cand)
  swap_rows(M,c,k,ids,F,ops);scale_row(M,c,1/M[c][c],ids,F,ops)
  for i in range(n):
   if i!=c and M[i][c]:add_row(M,i,c,-M[i][c],ids,F,ops)
  remaining.remove(c)
 assert M==[[Q(i==j) for j in range(n)] for i in range(n)]
 return [inverse(e) for e in reversed(ops)]

def gate_cost(gs):
 n=0
 for e in gs:
  if e[0]=='scale': n+=abs(abs(e[2]).bit_length()-e[3].bit_length())+2
  else:
   a,b=abs(e[3]),e[4];n+=2+2*(a.bit_length()-1)+a.bit_count()+b.bit_length()-1
 return n

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 w=json.loads(gzip.decompress(a.input.read_bytes()));assert csha(w)==INPUT_SHA
 oldA=w['A'];blocks=[];i=0
 while i<len(oldA):
  F=oldA[i][-1];j=i+1
  while j<len(oldA) and oldA[j][-1]==F:j+=1
  ids=sorted({q for e in oldA[i:j] for q in regs(e)})
  if len(F)==4 and j-i>25:blocks.append((i,j,ids,F))
  i=j
 assert len(blocks)==14
 rng=random.Random(SEED);newA=[];cursor=0;receipt=[]
 for i,j,ids,F in blocks:
  old=oldA[i:j];mat=matrix_for(old,ids);best=old;bestscore=(gate_cost(old),len(old))
  for _ in range(TRIALS):
   order=list(range(len(ids)));rng.shuffle(order);candidate=eliminate(mat,ids,F,order,rng)
   if candidate is None:continue
   score=(gate_cost(candidate),len(candidate))
   if score<bestscore:
    assert symstate(candidate)==symstate(old);best,bestscore=candidate,score
  newA+=oldA[cursor:i]+best;cursor=j
  receipt.append({'start':i,'end':j,'registers':ids,'old_gates':len(old),'new_gates':len(best),'old_cost':gate_cost(old),'new_cost':gate_cost(best)})
 newA+=oldA[cursor:];out=copy.deepcopy(w);out['A']=newA
 assert symstate(out['A']+out['B'])==symstate(w['A']+w['B'])
 assert len(newA)==3528 and len(out['B'])==len(w['B']) and len(out['cleanup'])==len(w['cleanup'])
 assert csha(out)==OUTPUT_SHA
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(gzip.compress(enc(out),mtime=0))
 print(json.dumps({'status':'PASS_EXACT_A_RESYNTHESIS','input_sha256':INPUT_SHA,'output_sha256':OUTPUT_SHA,'seed':SEED,'trials_per_block':TRIALS,'old_A_gates':len(oldA),'new_A_gates':len(newA),'saved_A_gates':len(oldA)-len(newA),'blocks':receipt},indent=2))
if __name__=='__main__':main()
