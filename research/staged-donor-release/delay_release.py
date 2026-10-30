"""Commute two releases to their first producer, preserving all other frames."""
import copy,gzip,json
from pathlib import Path
from collections import Counter
from invoice import profile
from sources.staged_pair import cleanup
P=Path(__file__).parent

def build(w):
 x=copy.deepcopy(w);at={}
 for j,rec in enumerate(w['warps']):at.setdefault(rec[0],[]).append((j,copy.deepcopy(rec)))
 moves={}
 for h,d,q in [(644,640,2),(660,656,-1)]:
  start=next(i for i,g in enumerate(w['B']) if g[:5]==['add',d,h,q,1])
  stop=next(i for i in range(start+1,len(w['B'])) if w['B'][i][1]==h)
  for i in range(start+1,stop):
   g=w['B'][i]
   if g[0]=='add':assert g[1]!=h and g[2]!=d
   else:assert g[1] not in (h,d)
   assert all(r[1][1] not in (h,d) for r in at.get(i,[]))
  assert all(r[1][1] not in (h,d) for r in at.get(stop,[]))
  moves[start]=(stop,['add',d,h,q,1,w['B'][stop][-1]])
 b=[];warps=[None]*len(w['warps'])
 for i in range(len(w['B'])+1):
  for j,rec in at.get(i,[]):rec[0]=len(b);warps[j]=rec
  for stop,g in moves.values():
   if i==stop:b.append(copy.deepcopy(g))
  if i<len(w['B']) and i not in moves:b.append(copy.deepcopy(w['B'][i]))
 x['B']=b;x['warps']=warps;x['cleanup']=cleanup(x)
 bill,inv,_=profile(x);x['report']['local_profile']={str(k):v for k,v in bill.items()}
 return x,dict(bill=bill,inventory=inv,moves=moves,delta=dict(Counter(bill)-Counter()))

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();assert not out.exists();out.mkdir()
 for provider in ('base','extra'):
  w=json.load(gzip.open(P/'sources'/f'STAGED644-660-{provider}.json.gz'));x,r=build(w)
  (out/f'DELAYED-{provider}.json.gz').write_bytes(gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0))
  print(provider,json.dumps(r))
