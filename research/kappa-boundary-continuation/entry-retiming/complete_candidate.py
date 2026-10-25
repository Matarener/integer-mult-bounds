#!/usr/bin/env python3
"""Complete a single entering-helper release candidate with literal FULL repair.

Apache-2.0. Retained PR3734 words and native verifier retain their own credit.
New construction/checker written with substantial OpenAI assistance.
This builder is not an independent all-column native verifier.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip,json,copy

def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):
 raw=Path(p).read_bytes();return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)
def write(p,x):
 raw=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
 Path(p).write_bytes(gzip.compress(raw,mtime=0) if str(p).endswith('.gz') else raw)
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
def span(vs):
 a={0}
 for x in vs:a|={q^x for q in a}
 return a
def contained(a,b):return basis(a+b)==basis(b)
def add(d,s,q):
 for ww,v in list(s.items()):
  z=d.get(ww,Q(0))+q*v
  if z:d[ww]=z
  else:d.pop(ww,None)
def warp(s,op):
 return {(ww[1:] if ww and ww[0]==-op else (op,)+ww):v for ww,v in s.items()}
def regs(e):return [e[1],e[2]] if e[0]=='add' else [e[1]]
def events(w):
 for e in w['initial_corrections']:
  q=Q(e['coefficient']);s=e['source'];ww=e['operator_word']
  for op in reversed(ww):yield ['warp',s,op,[],[]]
  yield ['add',e['target'],s,q.numerator,q.denominator,[]]
  for op in ww:yield ['warp',s,-op,[],[]]
 yield from w['precondition'];yield from w['compensation'];yield from w['A'];yield from w['cut']
 by={}
 for j,(pos,h,G,f,t) in enumerate(w['warps']):by.setdefault(pos,[]).append(['warp',h,j+1,f,t])
 for i in range(len(w['B'])+1):
  yield from by.get(i,[])
  if i<len(w['B']):yield w['B'][i]
 yield from w['restore'];yield from w['cleanup']
def column(w,h):
 st={h:{():Q(1)}}
 for e in events(w):
  if e[0]=='warp':st[e[1]]=warp(st.get(e[1],{}),e[2])
  elif e[0]=='scale':
   q=Q(e[2],e[3]);st[e[1]]={ww:v*q for ww,v in st.get(e[1],{}).items()}
  else:
   need(e[0]=='add','scalar grammar');add(st.setdefault(e[1],{}),st.get(e[2],{}),Q(e[3],e[4]))
 return {r:v for r,v in st.items() if v}
def profile(w):
 v,n,h=112,704,9;full=basis(1<<i for i in range(h));kept=[r for r in range(n) if r not in set(w['removed'])]
 cur={r:basis([w['ports'][r]]) if r<v else basis(w['start_extra'].get(str(r),[])) for r in kept}
 start=cur.copy();final={r:full if r<v or r>=2*v else basis(x for x in range(1,512) if (x&w['ports'][r-v]).bit_count()%2==0) for r in kept}
 for rs,ff in w['helper_final'].items():final[int(rs)]=basis(ff)
 paid=Counter()
 def climb(r,ff):
  f=basis(ff);old=cur[r];need(contained(old,f),f'nonmonotone role{r}: {old}->{f}')
  if f!=old:paid[len(f)-len(old)]+=1;cur[r]=f
 def event(e):
  if e[0]=='warp':
   _,r,op,old,new=e;need(cur[r]==basis(old),f'warp old role{r}');cur[r]=basis(new)
  else:
   for r in regs(e):climb(r,e[-1])
 for e in w['A']:event(e)
 levels=w['target_levels']
 for ci,r in enumerate(w['centers']):
  cf=basis(w['center_frames'][ci]);need(cur[r]==cf,'center entry')
  served={basis(levels.get(str(e[1]-v),[])) for e in w['cut'] if e[2]==r}
  prev=cf
  for f in sorted(served,key=lambda x:-len(x)):
   need(contained(f,prev),'center nested path')
   if f!=prev:paid[len(prev)-len(f)]+=1;prev=f
 by={}
 for j,(pos,r,G,f,t) in enumerate(w['warps']):by.setdefault(pos,[]).append(['warp',r,j+1,f,t])
 for i in range(len(w['B'])+1):
  for e in by.get(i,[]):event(e)
  if i<len(w['B']):event(w['B'][i])
 for e in w['restore']:event(e)
 for r,f in final.items():climb(r,f)
 for e in w['cleanup']:
  need(all(r>=n or final[r]==full for r in regs(e)),'cleanup touches nonFULL role')
 widths=Counter(len(final[r])-len(start[r]) for r in kept if r>=2*v)
 return dict(sorted(paid.items())),dict(sorted(widths.items()))
def complete(w,h):
 full=list(1<<i for i in range(8,-1,-1));st=column(w,h)
 need(st.get(h)=={():Q(1)},'candidate changed its source value')
 error={r:row for r,row in st.items() if r!=h}
 bad=set(range(112,224))|{int(r) for r in w['helper_final']}|set(range(704,1408))
 need(not set(error)&bad,'candidate error touches a native nonFULL/owned endpoint: '+str(sorted(set(error)&bad)))
 repair=[]
 for r,row in sorted(error.items()):
  for ww,q in sorted(row.items()):
   need(q.denominator&(q.denominator-1)==0,'non-dyadic repair')
   for op in reversed(ww):repair.append(['warp',h,op,full,full])
   repair.append(['add',r,h,-q.numerator,q.denominator,full])
   for op in ww:repair.append(['warp',h,-op,full,full])
 w['cleanup']+=repair
 need(column(w,h)=={h:{():Q(1)}},'single-column native FULL repair')
 pp,wi=profile(w);w['report']['local_profile']={str(r):n for r,n in pp.items()};w['report']['width_inventory']={str(r):n for r,n in wi.items()}
 return {'status':'BUILT_SINGLE_HELPER_FULL_REPAIR_REQUIRES_INDEPENDENT_REPLAY','helper_original':h,'repair_events':len(repair),'repair_targets':len(error),'repair_free_terms':sum(len(r) for r in error.values()),'local_profile':pp,'width_inventory':wi,'single_column_after_repair':{str(r):{str(ww):str(q) for ww,q in row.items()} for r,row in column(w,h).items()}}
def main():
 ap=ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--helper',type=int,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 w=read(a.word);receipt=complete(w,a.helper);a.out.mkdir(parents=True,exist_ok=False);write(a.out/'WORD.json.gz',w);write(a.out/'BUILDER.json',receipt);print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
