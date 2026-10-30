"""Find a bounded noncommuting polynomial certificate by word reduction.

This discovery code is not used by the independent certificate checker.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import heapq
import json
from pathlib import Path
import time
import multisplit_search as M

def lead(poly):return max(poly,key=lambda w:(len(w),w))
def shift(poly,left,right):return {left+w+right for w in poly}
def proof_shift(proof,left,right):return {(i,left+a,b+right) for i,a,b in proof}

def complete(equations,max_degree=4,max_rules=500,max_pairs=30000):
 rules=[];queue=[];counter=0;done=0;start=time.monotonic()
 def reduce(poly,proof):
  poly=set(poly);proof=set(proof)
  while poly:
   found=None
   for word in sorted(poly,key=lambda w:(len(w),w),reverse=True):
    for leading,p,r in rules:
     for pos in range(len(word)-len(leading)+1):
      if word[pos:pos+len(leading)]==leading:
       found=(word,pos,leading,p,r);break
     if found:break
    if found:break
   if not found:break
   word,pos,leading,p,r=found;left=word[:pos];right=word[pos+len(leading):]
   poly^=shift(p,left,right);proof^=proof_shift(r,left,right)
  return poly,proof
 def insert(poly,proof):
  nonlocal counter
  if not poly:return
  leading=lead(poly);idx=len(rules);rules.append((leading,poly,proof))
  for other in range(idx+1):
   for i,j in ((idx,other),(other,idx)):
    u=rules[i][0];v=rules[j][0]
    for k in range(1,min(len(u),len(v))+1):
     if u[-k:]==v[:k] and len(u)+len(v)-k<=max_degree:
      item=(i,(),v[k:],j,u[:-k],());counter+=1;heapq.heappush(queue,(len(u)+len(v)-k,counter,item))
    for pos in range(len(u)-len(v)+1):
     if u[pos:pos+len(v)]==v:
      item=(i,(),(),j,u[:pos],u[pos+len(v):]);counter+=1;heapq.heappush(queue,(len(u),counter,item))
 for ei,(_,p) in enumerate(equations):
  p,r=reduce(p,{(ei,(),())});insert(p,r)
  if p=={()}:return {'proof':sorted(r),'rules':len(rules),'pairs':done}
 while queue and done<max_pairs and len(rules)<max_rules:
  _,_,(i,a,b,j,c,d)=heapq.heappop(queue);done+=1
  p=shift(rules[i][1],a,b)^shift(rules[j][1],c,d)
  r=proof_shift(rules[i][2],a,b)^proof_shift(rules[j][2],c,d)
  p,r=reduce(p,r)
  if p=={()}:return {'proof':sorted(r),'rules':len(rules),'pairs':done}
  insert(p,r)
  if done%1000==0:print('completion',done,len(rules),len(queue),round(time.monotonic()-start,2),flush=True)
 return {'proof':None,'rules':len(rules),'pairs':done,'queued':len(queue)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--degree',type=int,default=4);ap.add_argument('--splits',type=int,default=3);args=ap.parse_args()
 M.SPLITS=args.splits;o=[(j,k) for k in range(args.splits) for j in range(3)];names,eq=M.equations(3,o)
 start=time.monotonic();result=complete(eq,args.degree)
 if result['proof']:
  check=set()
  for i,l,r in result['proof']:check^=shift(eq[i][1],tuple(l),tuple(r))
  if check!={()}:raise ValueError('Bad completion certificate')
 print('FINAL',{k:v if k!='proof' else len(v or []) for k,v in result.items()},time.monotonic()-start,flush=True)
 Path(__file__).with_name(f'COMPLETION-M{args.splits}-D{args.degree}.json').write_text(json.dumps({'order':o,'names':names,'degree_limit':args.degree,**result},indent=2)+'\n')
if __name__=='__main__':main()
