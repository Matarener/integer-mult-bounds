"""Independent structural certificate. No candidate builder or invoice imports."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import gzip,json,hashlib,sys
P=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(gzip.decompress(p.read_bytes()))
def span(b):
 s={0}
 for x in b:s|={x^y for y in tuple(s)}
 return s
def events(w):
 out=[]
 for i in range(len(w['B'])+1):
  out.extend(('warp',j,r) for j,r in enumerate(w['warps']) if r[0]==i)
  if i<len(w['B']):out.append(('gate',i,w['B'][i]))
 return out
def matrix(g,rs):
 n=len(rs);a=[[F(i==j) for j in range(n)] for i in range(n)]
 if g[0]=='add':a[rs.index(g[1])][rs.index(g[2])]+=F(g[3],g[4])
 else:assert g[0]=='scale';a[rs.index(g[1])][rs.index(g[1])]=F(g[2],g[3])
 return a
def mul(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def charges(w):
 cur={r:span([w['ports'][r]]) if r<112 else span(w['start_extra'].get(str(r),[])) for r in range(704)};bills={r:Counter() for r in cur}
 def climb(r,bs):
  s=span(bs);assert cur[r]<=s
  d=len(s).bit_length()-len(cur[r]).bit_length();cur[r]=s
  if d:bills[r][d]+=1
 def gate(g):
  if g[0]=='warp':assert cur[g[1]]==span(g[3]);cur[g[1]]=span(g[4])
  else:
   for r in (g[1:3] if g[0]=='add' else g[1:2]):climb(r,g[-1])
 for g in w['A']:gate(g)
 for r,e in zip(w['centers'],w['center_frames']):climb(r,e)
 for t in range(112):climb(112+t,w.get('target_levels',{}).get(str(t),[]))
 for typ,j,g in events(w):
  if typ=='warp':assert cur[g[1]]==span(g[3]);cur[g[1]]=span(g[4])
  else:gate(g)
 for g in w['restore']:gate(g)
 for r in cur:
  if r in w['removed']:continue
  e=w['helper_final'].get(str(r),list(range(512)))
  if 112<=r<224:e=[x for x in range(512) if (x&w['ports'][r-112]).bit_count()%2==0]
  climb(r,e)
 return bills
rows=[]
for pin in json.loads((P/'SOURCE-PINS.json').read_text()):assert sha((P/pin['retained']).read_bytes())==pin['sha256']
for provider in ('base','extra'):
 old=read(P/'sources'/f'STAGED644-660-{provider}.json.gz');new=read(P/'lead1-words'/f'DELAYED-{provider}.json.gz')
 oe=events(old);expected=list(oe);checks=[]
 for start,stop,d,h,q in [(591,1045,640,644,2),(641,1085,656,660,-1)]:
  release=('gate',start,old['B'][start]);assert release[2][:5]==['add',d,h,q,1]
  left=oe.index(release);right=next(i for i,e in enumerate(oe) if e[:2]==('gate',stop))
  count=warps=0
  for typ,j,g in oe[left+1:right]:
   if typ=='warp':assert g[1] not in (d,h);warps+=1
   else:
    rs=sorted(set([d,h]+(g[1:3] if g[0]=='add' else g[1:2])))
    a,b=matrix(release[2],rs),matrix(g,rs);assert mul(a,b)==mul(b,a);count+=1
  expected.remove(release);where=next(i for i,e in enumerate(expected) if e[:2]==('gate',stop));changed=list(release[2]);changed[-1]=old['B'][stop][-1];expected.insert(where,('gate',start,changed))
  checks.append(dict(start=start,stop=stop,exact_commutators=count,crossed_warps_including_stop_cut=warps))
 # IDs must remain stable, and every full scalar gate/frame must equal independent relocation.
 actual=events(new);assert len(actual)==len(expected)
 for a,e in zip(actual,expected):
  assert a[0]==e[0]
  if a[0]=='warp':assert a[1]==e[1] and a[2][1:]==e[2][1:]
  else:assert a[2]==e[2]
 for k in old:
  if k not in ('B','warps','cleanup','report'):assert old[k]==new[k],k
 # Independent cleanup inversion including native operator identity/sign and dirty buffer relabeling.
 n=2*new['report']['v']+new['report']['R'];buf=lambda r:r+n if str(r) in new['helper_final'] else r
 fw=list(new['A'][new['prelude_events']:])+[(['warp',e[2][1],e[1]+1] if e[0]=='warp' else e[2]) for e in actual]+new['restore'];clean=[];full=[256,128,64,32,16,8,4,2,1]
 for g in fw[::-1]:
  if g[0]=='warp':clean.append(['warp',buf(g[1]),-g[2],full])
  elif 112<=g[1]<224:continue
  elif g[0]=='add':clean.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],full])
  else:clean.append(['scale',buf(g[1]),g[3],g[2],full])
 assert clean==new['cleanup']
 cb,ca=charges(new),charges(old);delta=Counter();changed=[]
 for r in cb:
  ds={k:cb[r][k]-ca[r][k] for k in set(cb[r])|set(ca[r]) if cb[r][k]!=ca[r][k]}
  if ds:changed.append(r);delta.update(ds);assert ds=={1:-1,2:-1,3:1}
 assert changed==[640,656] and dict(delta)=={1:-2,2:-2,3:2}
 native=json.loads((P/'evidence'/f'native-{provider}'/'RESULT.json').read_text());assert native['word_sha256']==sha((P/'lead1-words'/f'DELAYED-{provider}.json.gz').read_bytes())
 rows.append(dict(provider=provider,checks=checks,changed_wire_bills=changed,delta=dict(delta),native_word_hash_matches=True))
print(json.dumps(dict(status='PASS_INDEPENDENT_STRUCTURAL_CERTIFICATE',python=sys.version,scope='Exact commuting proof on arbitrary full dirty states; inverse transpose follows from equality of invertible operators. Independently reconstructed cleanup and donor invoices. Does not replay native or outer admission.',checks=rows),indent=2))
