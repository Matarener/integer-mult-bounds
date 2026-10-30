"""Find and emit independent helper splits on the changed G20 word.

Adapted from Ali Romman PR5609 and PR5599. Substantial OpenAI Codex
assistance. Apache-2.0. Preserve all notices in prior/ and source/.
"""
import sys,collections,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import integration as B
spec=importlib.util.spec_from_file_location('cuts',ROOT/'source/cut_search.py');K=importlib.util.module_from_spec(spec);spec.loader.exec_module(K)
base,frames,_=B.source();geom=B.SOURCE.Geometry(frames)
canonical={int(k):K.rational_basis(v['B'])for k,v in frames.items()};shapes=sorted(set(canonical.values()));label={k:shapes.index(v)for k,v in canonical.items()};label[None]=None;dim={i:len(v)for i,v in enumerate(shapes)}
from functools import lru_cache
@lru_cache(None)
def nested(u,f,v):return dim[v]<dim[f]<dim[u] and K.rational_basis(shapes[u]+shapes[f])==shapes[u] and K.rational_basis(shapes[f]+shapes[v])==shapes[f]
def bits(x):return [i for i in range(x.bit_length())if x>>i&1]
def need(c,m):
 if not c:raise ValueError(m)
def replay(w):
 n=len(w['start']);rows=[1<<i for i in range(n)];st=w['start'][:];paid=collections.Counter()
 for ix,e in enumerate(w['records']):
  op,d=e[:2]
  if op=='ADD':need(st[d]==st[e[2]]==e[3],f'coframe {ix}');rows[d]^=rows[e[2]]
  elif op=='ERASE':need(d in w['owned'],'Owned only');rows[d]=0;st[d]=e[2]
  elif op=='INIT':need(d in w['owned']and not rows[d],'Zero INIT');st[d]=e[2]
  else:
   need(op in ['Q','ZERO_Q']and st[d]==e[2],'Query frame');geom.nested(*e[2:]);st[d]=e[3]
   if op=='Q':paid[e[4]]+=1
   else:need(not rows[d],'Whole zero')
 expected=[0 if i in w['owned']else(1<<i)^((1<<(i-111))if 111<=i<222 else 0)for i in range(n)]
 need(rows==expected and st==w['final'],'Exact all-input endpoint')
 return dict(paid)

def find(w):
 n=len(w['start']);es=w['records'];owned=set(w['owned']);groups=collections.defaultdict(set)
 for h in range(222,n):
  if h not in owned:groups[label[w['start'][h]],label[w['final'][h]]].add(h)
 comp=collections.defaultdict(list);masks={}
 for g,hs in groups.items():
  masks[g]=((1<<n)-1)^sum(1<<h for h in hs)
  for f in range(len(shapes)):
   if nested(g[0],f,g[1]):comp[f].append(g)
 a=[1<<i for i in range(n)];b=a[:];after={}
 for k in reversed(range(len(es))):
  e=es[k];op,d=e[:2]
  if op=='ADD':b[e[2]]^=b[d]
  elif op=='ERASE':after[k]=b[d];b[d]=0
 st=w['start'][:];banks=collections.defaultdict(set)
 for i,f in enumerate(st):banks[label[f]].add(i)
 seen=set();candidates={};contexts=0
 def check(f,k):
  nonlocal contexts
  if f not in comp or not banks[f]:return
  fs=tuple(sorted(banks[f]));aa=tuple(a[i]for i in fs);bb=tuple(b[i]for i in fs)
  for g in comp[f]:
   key=g,f,fs,aa,bb
   if key in seen:continue
   seen.add(key);contexts+=1;mask=masks[g];left=K.kernel([x&mask for x in aa]);right=K.kernel([x&mask for x in bb]);pivots=set(fs)&groups[g]
   if not pivots or not left or not right:continue
   left=left+[u^v for j,u in enumerate(left)for v in left[j+1:]]
   for u in left:
    c=K.combine(aa,u)
    if not c:continue
    opts={}
    for v in right:
     d=K.combine(bb,v);pair=((u&v).bit_count()%2,(c&d).bit_count()%2)
     if pair!=(0,0):opts.setdefault(pair,(v,d))
    if (1,1) in opts:v,d=opts[1,1]
    elif (1,0)in opts and(0,1)in opts:v,d=(opts[1,0][i]^opts[0,1][i]for i in range(2))
    else:continue
    p=min(pivots,key=lambda p:(not(c>>p&d>>p&1),p));actual=st[p];av=sum(1<<fs[i]for i in bits(u));bv=sum(1<<fs[i]for i in bits(v));ranks=[dim[g[0]]-dim[f],dim[f]-dim[g[1]]];score=sum(r**(1-.00351)for r in ranks)-(sum(ranks))**(1-.00351)
    h=dict(cut=k,frame=actual,pivot=p,a=bits(av),b=bits(bv),c=bits(c),d=bits(d),ranks=ranks,score=score)
    signature=(g,tuple(bits(c)),tuple(bits(d)),f)
    if signature not in candidates:candidates[signature]=h
 def move(d,f):
  old=label[st[d]];banks[old].remove(d);banks[label[f]].add(d);st[d]=f;return{old,label[f]}
 for f in list(banks):check(f,-1)
 for k,e in enumerate(es):
  op,d=e[:2];affected={label[st[d]]}
  if op=='ADD':a[d]^=a[e[2]];b[e[2]]^=b[d]
  elif op=='ERASE':a[d]=0;b[d]=after[k]
  if op in ['Q','ZERO_Q','INIT','ERASE']:affected|=move(d,e[3]if op in ['Q','ZERO_Q']else e[2])
  for f in affected:check(f,k)
 print('CENSUS',contexts,len(candidates),flush=True)
 return sorted(candidates.values(),key=lambda h:(-h['score'],h['cut'],len(h['a'])+len(h['b'])))
def basis(a,b,p,f):
 a=sum(1<<i for i in a);b=sum(1<<i for i in b);need((a&b).bit_count()%2,'Unit pairing');rows={i:1<<i for i in set(bits(a|b))|{p}};out=[]
 def add(d,s):
  nonlocal b
  out.append(['ADD',d,s,f]);rows[d]^=rows[s]
  if b>>s&1:b^=1<<d
 if not(a>>p&1):
  j=bits(a)[0]
  add(p,j);add(j,p);add(p,j)
 for i in bits(a^rows[p]):
  # After the swap, original coordinate i may occupy the swapped role.
  q=next(q for q,row in rows.items()if row==1<<i)
  add(p,q)
 need(rows[p]==a and b>>p&1,'Basis row formed')
 for i in bits(b^(1<<p)):add(i,p)
 need(b==1<<p and rows[p]==a,'Both basis conditions')
 return out

def split(w,h):
 from copy import deepcopy
 out=deepcopy(w);p=h['pivot'];f=h['frame'];z=len(w['start']);cut=h['cut'];u=w['start'][p];v=w['final'][p];G=basis(h['c'],h['d'],p,u);J=basis(h['a'],h['b'],p,f)
 def sub(e):
  e=e[:]
  if e[1]==p:e[1]=z
  if e[0]=='ADD'and e[2]==p:e[2]=z
  return e
 out['start'].append(f);out['final'].append(v);out['final'][p]=f
 out['records']=G[::-1]+w['records'][:cut+1]+J+[sub(e)for e in J[::-1]+w['records'][cut+1:]]+[sub([*e[:-1],v])for e in G]
 replay(out);return out
