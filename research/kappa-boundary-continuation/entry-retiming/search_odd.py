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
results=[];counts=Counter()
for hs,s in w['start_extra'].items():
 h=int(hs)
 if h%2==0 or h in a_contact:continue
 s=tuple(s); prod=next((i for i,e in enumerate(w['B']) if e[1]==h),len(w['B']))
 reads=[i for i,e in enumerate(w['B'][:prod]) if e[0]=='add' and e[2]==h]
 if not reads:continue
 counts['helpers_with_reads']+=1
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
 assert vec.pop(h)=={():Q(1)}
 if any(ww for rr in vec.values() for ww in rr):counts['nontrivial_warp_release']+=1;continue
 vec={r:row[()] for r,row in vec.items()}
 if not vec:counts['zero_effect']+=1
 need=basis(s+tuple(x for r in vec for x in bcur[prod][r]))
 nexts={r:tuple(next((e[-1] for e in w['B'][prod:] if r in regs(e)),w['helper_final'].get(str(r),[1<<i for i in range(9)]))) for r in vec}
 source_next=tuple(w['B'][prod][-1]) if prod<len(w['B']) else tuple(1<<i for i in range(9))
 bound=basis(source_next)
 # Enumerate every one-axis extension of old entry, preserving target compatibility.
 options=set()
 for x in range(1,512):
  t=basis(s+(x,))
  if len(t)!=len(s)+1 or not sub(t,source_next):continue
  if all(sub(bcur[prod][r],t) and sub(t,nexts[r]) for r in vec):options.add(t)
 info={'helper':h,'old_frame':list(s),'first_producer':prod,'reads':reads,'release_support':{str(r):str(v) for r,v in vec.items()},'minimum_release_frame':list(need),'producer_frame':list(source_next),'options':[list(t) for t in sorted(options)]}
 results.append(info)
 if options:print('CANDIDATE',json.dumps(info),flush=True)
print('CENSUS',dict(counts),'candidates',sum(bool(x['options']) for x in results),'screened',len(results))
Path(__file__).with_name('ODD-RELEASE-SEARCH.json').write_text(json.dumps({'status':'SCOPED_EXACT_RELEASE_SEARCH','counts':dict(counts),'results':results},indent=2)+'\n')
