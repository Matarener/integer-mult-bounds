#!/usr/bin/env python3
"""Exact odd-helper release search against the attached PR3734 word."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,json
P=Path(__file__).resolve().parents[2]/'kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43base.json.gz'
w=json.loads(gzip.decompress(P.read_bytes()))
def basis(vs):
 p={}
 for x in vs:
  for k in sorted(p,reverse=True):
   if x>>k&1:x^=p[k]
  if x:
   k=x.bit_length()-1
   for j in p:
    if p[j]>>k&1:p[j]^=x
   p[k]=x
 return tuple(p[k] for k in sorted(p,reverse=True))
def sub(a,b):return basis(a+b)==basis(b)
def regs(e):return [e[1],e[2]] if e[0]=='add' else [e[1]]
cur=[(q,) for q in w['ports']]+[() for _ in range(592)]
for h,s in w['start_extra'].items():cur[int(h)]=tuple(s)
a_contact=set()
for e in w['A']:
 a_contact.update(regs(e))
 if e[0]=='warp':cur[e[1]]=tuple(e[-1]);continue
 for r in regs(e):cur[r]=tuple(e[-1])
bcur=[cur.copy()];warpby={}
for wi,(pos,h,G,frm,to) in enumerate(w['warps']):warpby.setdefault(pos,[]).append((h,tuple(to),wi+1))
for i,e in enumerate(w['B']):
 for h,to,op in warpby.get(i,[]):cur[h]=to
 for r in regs(e):cur[r]=tuple(e[-1])
 bcur.append(cur.copy())

from functools import lru_cache
@lru_cache(None)
def sm(f):
 vals={0}
 for x in f:vals|={x^v for v in vals}
 return sum(1<<x for x in vals)
def masksub(a,b):return a&~b==0
nxt=[tuple(w['helper_final'].get(str(r),[1<<i for i in range(9)])) for r in range(704)]
bnext=[None]*(len(w['B'])+1); bnext[-1]=nxt.copy()
for i in range(len(w['B'])-1,-1,-1):
 for r in regs(w['B'][i]):nxt[r]=tuple(w['B'][i][-1])
 for r,to,op in warpby.get(i,[]):nxt[r]=tuple(w['warps'][op-1][3])
 bnext[i]=nxt.copy()
results=[];counts=Counter()
for hs,s in w['start_extra'].items():
 h=int(hs)
 if h%2==0 or h in a_contact:continue
 s=tuple(s); prod=next((i for i,e in enumerate(w['B']) if e[1]==h),len(w['B']))
 reads=[i for i,e in enumerate(w['B'][:prod]) if e[0]=='add' and e[2]==h]
 if not reads:continue
 counts['helpers_with_reads']+=1
 source_next=tuple(w['B'][prod][-1]) if prod<len(w['B']) else tuple(1<<i for i in range(9))
 potential={basis(s+(x,)) for x in range(1,512)}
 potential={t for t in potential if len(t)==len(s)+1 and sub(t,source_next)}
 vec={h:{():Q(1)}}
 for i,e in enumerate(w['B'][:prod]):
  for r,to,op in warpby.get(i,[]):
   if r in vec:vec[r]={(op,)+ww:val for ww,val in vec[r].items()}
  if e[0]=='add':
   d,r,a,b=e[1:5]
   for ww,val in list(vec.get(r,{}).items()):
    nr=vec.setdefault(d,{});nv=nr.get(ww,Q(0))+Q(a,b)*val
    if nv:nr[ww]=nv
    else:nr.pop(ww,None)
   if not vec.get(d):vec.pop(d,None)
  else:
   d,a,b=e[1:4]
   if d in vec:vec[d]={ww:val*Q(a,b) for ww,val in vec[d].items()}
  cut=i+1
  if cut<=reads[-1]:continue
  assert vec[h]=={():Q(1)}
  if any(ww for r,rr in vec.items() if r!=h for ww in rr):counts['warped_cuts']+=1;continue
  vv={r:row[()] for r,row in vec.items() if r!=h}
  counts['cuts_screened']+=1
  options=[]
  for t in potential:
   ts=sm(t)
   if all(masksub(sm(bcur[cut][r]),ts) and masksub(ts,sm(bnext[cut][r])) for r in vv):options.append(t)
  if options:
   info={'helper':h,'old_frame':list(s),'first_producer':prod,'cut':cut,'reads':reads,'release_support':{str(r):str(v) for r,v in vv.items()},'options':[list(t) for t in sorted(options)]}
   results.append(info); print('CANDIDATE',json.dumps(info),flush=True)
print('CENSUS',dict(counts),'candidates',len(results))
Path(__file__).with_name('ODD-CUT-SEARCH.json').write_text(json.dumps({'status':'SCOPED_EXACT_ALL_CUT_RELEASE_SEARCH','counts':dict(counts),'candidates':results},indent=2)+'\n')
