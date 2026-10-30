"""Exact common-chart multi-channel cut screen on an explicitly supplied word.
Prepared for zxv with OpenAI Codex assistance; Apache-2.0.
Ali Romman supplies the cut interface and predecessor P104 construction.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict,Counter
from hashlib import sha256
import gzip,json,pickle,time,math,sys
HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
OUT=HERE
WORD=Path(sys.argv[1]) if len(sys.argv)>1 else P/'WORD.json.gz'
w=json.loads(gzip.decompress(WORD.read_bytes()))
n=w['public'];N=n+w['owned_fields'];main=set(w['live'])|{r+112 for r in w['live']}
group={r for r in range(n) if r not in main and (w['initial'][r],w['final'][r])==(3,127)}
frames=w['frames'];program=w['program']
def add(a,b,q):
 for k,v in b.items():
  z=a.get(k,0)+q*v
  if z:a[k]=z
  else:a.pop(k,None)
def enc(v):return {str(k):str(x) for k,x in v.items()}
def span(b):
 s={0}
 for x in b:s|={a^x for a in tuple(s)}
 return s
# Record each event on every chart it touches. All other chart rows and suffix
# columns are unchanged, so their previous recorded cut has identical spaces.
current=w['initial']+[None]*w['owned_fields'];at=defaultdict(set)
for r,f in enumerate(current):
 if f is not None:at[f].add(r)
snapshots={};active=set()
for i,e in enumerate(program):
 op,r=e[:2];touched=set()
 if op in ('MOVE','INIT','CLEAR'):
  if current[r] is not None:touched.add(current[r]);at[current[r]].remove(r)
  if op=='MOVE':f=e[3]
  elif op=='INIT':f=e[2];active.add(r)
  else:f=None;active.remove(r)
  current[r]=f
  if f is not None:touched.add(f);at[f].add(r)
 else:touched.add(e[-1])
 for chart in touched:
  E=tuple(sorted(at[chart]))
  if chart not in (3,127) and len(E)>=1:snapshots.setdefault(i,[]).append((chart,E,tuple(active)))
print('candidate',n,N,'group',len(group),'snapshots',sum(map(len,snapshots.values())),'maxcohort',max(len(s[1]) for ss in snapshots.values() for s in ss),flush=True)
allcount=sum(map(len,snapshots.values()))
state_hash=sha256(json.dumps([(i,f,E) for i,ss in snapshots.items() for f,E,_ in ss],separators=(',',':')).encode()).hexdigest()
print('all event states',allcount,flush=True)
# Suffix columns: reverse scalar execution updates the source column.
columns=[{r:Q(1)} for r in range(N)];suffix={}
for i in range(len(program)-1,-1,-1):
 if i in snapshots:
  suffix[i]={r:columns[r].copy() for r in set(r for _,E,_ in snapshots[i] for r in E)}
 e=program[i];op,r=e[:2]
 if op in ('INIT','CLEAR'):columns[r]={}
 elif op=='SCALE':columns[r]={k:Q(e[-2])*v for k,v in columns[r].items()}
 elif op in ('ADD','COPY'):
  add(columns[e[2]],columns[r],Q(e[-2]))
  if op=='COPY':columns[r]={}
print('suffix snapshots complete',len(suffix),flush=True)
def kernel_vectors(vectors,E):
 """Return exact coframe vectors whose image is supported inside helper group."""
 pivots={};out=[]
 for r in E:
  v={k:x for k,x in vectors[r].items() if k not in group};a={r:Q(1)}
  while v:
   k=min(v)
   if k not in pivots:
    q=v[k];pivots[k]=({j:x/q for j,x in v.items()},{j:x/q for j,x in a.items()});break
   b,c=pivots[k];q=v[k];add(v,b,-q);add(a,c,-q)
  if not v:
   image={}
   for s,q in a.items():add(image,vectors[s],q)
   if not set(image)<=group:raise ValueError('Kernel image leaves the declared boundary group')
   if image:out.append((a,image))
 # Remove dependent image generators while retaining their coframe witnesses.
 # Zero-image kernel directions cannot produce a unit boundary pairing.
 image_basis={}
 for a,image in out:
  a=a.copy();image=image.copy()
  while image:
   k=min(image)
   if k not in image_basis:
    q=image[k]
    image_basis[k]=({j:x/q for j,x in a.items()},{j:x/q for j,x in image.items()})
    break
   ba,bi=image_basis[k];q=image[k];add(a,ba,-q);add(image,bi,-q)
 return list(image_basis.values())
def dyadic(q):return q.denominator&(q.denominator-1)==0
def oddpart(k):
 k=abs(k)
 while k and k%2==0:k//=2
 return k
rows=[{r:Q(1)} if r<n else {} for r in range(N)];reports=[];hits=[];coverage=Counter();started=time.time()
for i,e in enumerate(program):
 op,r=e[:2]
 if op in ('INIT','CLEAR'):rows[r]={}
 elif op=='SCALE':rows[r]={k:Q(e[-2])*v for k,v in rows[r].items()}
 elif op=='COPY':rows[r]={k:Q(e[-2])*v for k,v in rows[e[2]].items()}
 elif op=='ADD':add(rows[r],rows[e[2]],Q(e[-2]))
 if i not in snapshots:continue
 for f,E,active in snapshots[i]:
  A=kernel_vectors(rows,E);B=kernel_vectors(suffix[i],E)
  coverage[str((len(A),len(B)))]+=1
  if not A or not B:continue
  pairs=[];g=0
  for ai,(a,c) in enumerate(A):
   for bi,(b,d) in enumerate(B):
    v=sum(x*b.get(r,0) for r,x in a.items());v2=sum(x*d.get(r,0) for r,x in c.items())
    if v or v2:
     pairs.append((ai,bi,v,v2));g=math.gcd(g,oddpart(v2.numerator))
  rep=dict(cut_after=i,frame=f,dimension=len(frames[f]),cohort=list(E),prefix_dimension=len(A),suffix_dimension=len(B),gcd_odd_numerators=g,nonzero_internal_pairs=sum(v!=0 for _,_,v,v2 in pairs),nonzero_boundary_pairs=sum(v2!=0 for _,_,v,v2 in pairs),active_owned=list(active))
  rep['A']=[(enc(a),enc(c)) for a,c in A]
  rep['B']=[(enc(b),enc(d)) for b,d in B]
  rep['pairing']=[(ai,bi,str(v),str(v2)) for ai,bi,v,v2 in pairs]
  reports.append(rep)
  if g==1:
   hit={**rep,'A':[(enc(a),enc(c)) for a,c in A],'B':[(enc(b),enc(d)) for b,d in B],'pairing':[(ai,bi,str(v),str(v2)) for ai,bi,v,v2 in pairs]};hits.append(hit)
   print('HIT',i,'frame',f,'dims',len(A),len(B),'pairs',len(pairs),'unitentries',sum(oddpart(v.numerator)==1 for _,_,v,_ in pairs),'dyadic',all(all(dyadic(x) for x in a.values()) for a,c in A+B),flush=True)
 if i%500==0:print('at',i,'reports',len(reports),'hits',len(hits),'seconds',round(time.time()-started,1),flush=True)
result={'status':'EXACT_FIXED_WORD_COMMON_CHART_BOUNDARY_PAIRING_EXCLUSION','source_word_sha256':sha256(WORD.read_bytes()).hexdigest(),'group':sorted(group),'all_snapshots':allcount,'bounded_snapshots':sum(map(len,snapshots.values())),'event_cuts':len(snapshots),'state_sha256':state_hash,'max_cohort':max(len(E) for ss in snapshots.values() for f,E,_ in ss),'dimension_counts':dict(coverage),'reports':reports,'hits':hits}
(OUT/'ALL-EVENT-CUT-SCREEN.json').write_text(json.dumps(result,indent=2)+'\n')
print('DONE',len(reports),'reports',len(hits),'hits',round(time.time()-started,1),flush=True)
