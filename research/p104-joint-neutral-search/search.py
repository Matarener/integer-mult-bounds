"""Exact dyadic contact generation and bounded joint route/scalar exploration."""
from fractions import Fraction as Q
from collections import defaultdict, Counter
from pathlib import Path
import argparse, gzip, hashlib, json, time
HERE=Path(__file__).resolve().parent
PINS={'word5713.json.gz':'9fd67dd89ed24a644257cd9aef06934ed4c6fbe0441804684a968868f2ef66a8','word5718.json.gz':'cff7196f8b168c4ebf8227185eed98387b66ec5db0179108adfea4045775cc31'}
def need(x,msg):
 if not x: raise ValueError(msg)
def add(a,b,q=Q(1)):
 for k,v in tuple(b.items()):
  z=a.get(k,0)+q*v
  if z:a[k]=z
  else:a.pop(k,None)
def scale(a,q):return {k:v*q for k,v in a.items() if v*q}
def apply(rows,e):
 op,r=e[:2]
 if op=='MOVE':return
 if op in ('INIT','CLEAR'):rows[r]={}
 elif op=='SCALE':rows[r]=scale(rows[r],Q(e[-2]))
 else:
  s=e[2];a=dict(rows[s])
  if op=='COPY':rows[r]={}
  add(rows[r],a,Q(e[-2]))
def charts_step(ch,e):
 if e[0]=='MOVE':ch[e[1]]=e[3]
 elif e[0] in ('INIT','CLEAR'):ch[e[1]]=e[2] if e[0]=='INIT' else None
def span(xs):
 s={0}
 for x in xs:s|={v^x for v in tuple(s)}
 return s
def load(name):
 p=HERE/'inputs'/name;b=p.read_bytes();need(hashlib.sha256(b).hexdigest()==PINS[name],'source hash')
 return json.loads(gzip.decompress(b))
def fmt(x):
 if isinstance(x,dict):return {str(k):fmt(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [fmt(v) for v in x]
 if isinstance(x,Q):return str(x)
 return x
def unrow(x):return {int(k):Q(v) for k,v in x.items()}
def generate(w):
 n=w['public'];N=n+w['owned_fields'];main=set(w['live'])|{r+112 for r in w['live']}
 fs=[span(b) for b in w['frames']];rows=[{r:Q(1)} for r in range(N)];ch=w['initial']+[None]*(N-n);at=defaultdict(set)
 for r,f in enumerate(ch):at[f].add(r)
 stats=Counter();by=defaultdict(list)
 # Every MOVE changes contact at both departure and arrival. No input-column-zero assumption.
 for i,e in enumerate(w['program']):
  if e[0]=='MOVE':
   _,m,old,f,_=e;at[old].remove(m);at[f].add(m);ch[m]=f
   for frame in sorted({old,f}):
    for p in sorted(at[frame]):
     if p>=n or p in main:continue
     u,v=w['initial'][p],w['final'][p]
     if not fs[u]<fs[frame]<fs[v]:continue
     stats['helper_contact_contexts']+=1
     outside={k:x for k,x in rows[p].items() if k>=n or w['initial'][k]!=u}
     options=[(None,Q(0))] if not outside else []
     for s in sorted(at[frame]-{p}):
      out={k:x for k,x in rows[s].items() if k>=n or w['initial'][k]!=u}
      if not out:
       if not outside:
        options.extend((s,q) for q in (Q(-2),Q(-1),Q(-1,2),Q(1,2),Q(1),Q(2)))
       continue
      k=min(out);q=-outside.get(k,0)/out[k]
      if q and all(outside.get(j,0)+q*out.get(j,0)==0 for j in outside.keys()|out.keys()):options.append((s,q))
     for s,q in options:
      if q.denominator&(q.denominator-1):continue
      c=dict(rows[p]);a={p:Q(1)}
      if s is not None:add(c,rows[s],q);a[s]=q
      if c.get(p)!=1:continue
      stats['prefix_candidates']+=1
      by[i].append(dict(cut=i,pivot=p,frame=frame,a=a,c=c,h0=dict(rows[p]),ranks=[len(w['frames'][frame])-len(w['frames'][u]),len(w['frames'][v])-len(w['frames'][frame])],trigger=m))
  else:
   if e[0] in ('INIT','CLEAR'):
    r=e[1];at[ch[r]].remove(r);charts_step(ch,e);at[ch[r]].add(r)
   apply(rows,e)
 cols=[{r:Q(1)} for r in range(N)];keep=[]
 for i in range(len(w['program'])-1,-1,-1):
  for s in by.pop(i,[]):
   p=s['pivot'];u=w['initial'][p];d=cols[p];beta=dict(d)
   for r in w['live']:
    if r in d:beta[r+112]=beta.get(r+112,0)-d[r]
   beta={k:v for k,v in beta.items() if v}
   if beta.get(p)!=1 or any(k>=n or w['initial'][k]!=u for k in beta):continue
   if sum(x*beta.get(k,0) for k,x in s['c'].items())!=1:continue
   s.update(d=dict(d),beta=beta);keep.append(s)
  e=w['program'][i];op,r=e[:2]
  if op in ('INIT','CLEAR'):cols[r]={}
  elif op=='SCALE':cols[r]=scale(cols[r],Q(e[-2]))
  elif op!='MOVE':
   add(cols[e[2]],cols[r],Q(e[-2]))
   if op=='COPY':cols[r]={}
 stats['compatible_bases']=len(keep);stats['other_role_candidates']=sum(s['trigger']!=s['pivot'] for s in keep)
 # Exact identical cut state dedup across consecutive MOVE triggers is left visible in raw counts.
 return sorted(keep,key=lambda s:(s['cut'],s['pivot'],tuple(s['a'].items()))),dict(stats)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--word',default='word5718.json.gz');ap.add_argument('--out',default='contacts5718.json');a=ap.parse_args()
 t=time.monotonic();w=load(a.word);cuts,stats=generate(w);out=dict(source_sha256=PINS[a.word],domain='after every MOVE, departure and arrival groups; a=e_p+q e_s, q chosen for purity or +/-1/2,+/-1,+/-2',stats=stats,cuts=cuts)
 (HERE/'results'/a.out).write_text(json.dumps(fmt(out),indent=2)+'\n');print(json.dumps(dict(stats=stats,seconds=time.monotonic()-t)),flush=True)
 if a.word=='word5713.json.gz':need(any(c['cut']==14330 and c['pivot']==708 and c['a']=={708:Q(1),154:Q(1,2)} for c in cuts),'generator must DISCOVER PR5718 control')
if __name__=='__main__':main()
