"""Independent literal G20 relation-word audit; no candidate module imports.

Internal OpenAI Codex review for ai-nanachi, Apache-2.0.  The method of owning
nine capture relations is Ali Romman's PR5421; this tests its distinct G20
application.  This is not external or formal theorem verification.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import gzip,json,hashlib,datetime
HERE=Path(__file__).resolve().parent;RUN=HERE.parent
SRC=RUN/'vendor/g20'
CAND=RUN
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def need(c,m):
 if not c:raise ValueError(m)
def rank(rows):
 a=[[F(v)for v in r]for r in rows];j=0
 for k in range(8):
  p=next((i for i in range(j,len(a))if a[i][k]),None)
  if p is None:continue
  a[j],a[p]=a[p],a[j];v=a[j][k];a[j]=[x/v for x in a[j]]
  for i in range(j+1,len(a)):
   v=a[i][k]
   if v:a[i]=[x-v*y for x,y in zip(a[i],a[j])]
  j+=1
 return j
def orth(a,b):return all(sum(F(x)*F(y)for x,y in zip(r,s))==0 for r in a for s in b)
def replay(word,base,fd):
 n=660;owned=set(word['owned']);rows=[1<<i for i in range(n)];hdr=base['final']+[None,None]
 paid=Counter();ops=Counter();edges=set();touched=set();active=set();peak=0
 for ix,e in enumerate(word['records']):
  op,d=e[:2];ops[op]+=1
  if op=='ERASE':
   need(d in owned,'Unowned original erased');rows[d]=0;hdr[d]=e[2];active.discard(d)
  elif op=='INIT':need(d in owned and rows[d]==0,'INIT nonzero/unowned');hdr[d]=e[2]
  elif op=='ADD':
   _,_,s,f=e;need(d!=s and hdr[d]==hdr[s]==f,'Misaligned ADD')
   rows[d]^=rows[s]
   if d in owned:active.add(d)
  elif op in('Q','ZERO_Q'):
   _,_,a,b,k=e;need(hdr[d]==a,'Wrong query birth')
   lo,hi=(a,b)if fd[str(a)]['dim']<fd[str(b)]['dim']else(b,a)
   need(0<k<8 and fd[str(hi)]['dim']-fd[str(lo)]['dim']==k,'Wrong residual rank')
   edges.add((lo,hi,k));touched.update((a,b));hdr[d]=b
   if op=='ZERO_Q':need(rows[d]==0,'Free Q on nonzero function')
   else:paid[k]+=1
  else:raise ValueError('Unknown '+op)
  peak=max(peak,len(active))
 expected=[0 if i in owned else(1<<i)^((1<<(i-111))if 111<=i<222 else 0)for i in range(n)]
 need(rows==expected,'All660 raw/dirty input-column endpoint')
 need(hdr==base['start']+[None,None],'All660 output headers')
 return paid,ops,edges,touched,peak
def main():
 base=read(SRC/'inputs/BASELINE-LOCAL.json.gz');fd=read(SRC/'inputs/FRAMES.json')['frames'];word=read(CAND/'WORD.json.gz')
 owned=set(word['owned']);need(owned==set(range(469,478))|{658,659},'Owned identity')
 need(all(base['start'][i]==0 and base['final'][i]==1 for i in range(469,478)),'All nine target debits are complete rank8 helpers')
 partial=[i for i in range(222,658)if fd[str(base['final'][i])]['dim']!=8]
 need(not(set(partial)&owned),'No partial helper double debit')
 paid,ops,edges,touched,peak=replay(word,base,fd)
 touched.update(base['start']);touched.update(base['final'])
 for f in touched:
  d=fd[str(f)];a,b=d['A'],d['B'];need(len(a)==8-d['dim']and len(b)==d['dim'],'Frame dimensions')
  need(rank(a+b)==8 and orth(a,b),'Exact rational direct orthogonal decomposition')
 for lo,hi,k in edges:need(orth(fd[str(lo)]['B'],fd[str(hi)]['A']),'Exact rational projector nesting')
 # In each main port P is the rank-one entrance; K the rank-seven exit.
 # Orthogonal direct sum gives commuting induced D_P,D_K and D_PD_K=D_I.
 for i in range(111):
  p,k=base['start'][i],base['final'][111+i]
  need(fd[str(p)]['dim']==1 and fd[str(k)]['dim']==7 and orth(fd[str(p)]['B'],fd[str(k)]['B']),'Main complementary P/K')
  need(rank(fd[str(p)]['B']+fd[str(k)]['B'])==8,'Main P+K=I')
  need(base['final'][i]==1 and base['start'][111+i]==0,'Main exact birth/exit')
 need(paid==Counter({1:1309,2:1342,3:77,4:40,5:102,6:10,7:9}),'Complete local paid histogram')
 failures={}
 for name,index in [('missing_pivot_entry_clear',next(i for i,e in enumerate(word['records'])if e[0]=='ERASE'and e[1]==469)),('missing_pivot_exit_clear',max(i for i,e in enumerate(word['records'])if e[0]=='ERASE'and e[1]==469)),('changed_relation',next(i for i,e in enumerate(word['records'])if e[0]=='ADD'and e[1]==469))]:
  bad=dict(word);bad['records']=word['records'][:index]+word['records'][index+1:]
  try:replay(bad,base,fd)
  except ValueError as e:failures[name]=str(e)
  else:raise ValueError('Mutation accepted '+name)
 files=[SRC/'inputs/BASELINE-LOCAL.json.gz',SRC/'inputs/FRAMES.json',SRC/'provider/data/INVERSE.json.gz',CAND/'WORD.json.gz',CAND/'local_relations.py']
 out={'status':'PASS_INDEPENDENT_LOCAL_LITERAL_660_COLUMNS_QQ_FRAME_NESTING','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':[{'path':p.relative_to(CAND).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files],
 'retained_originals':649,'owned_allocated':11,'owned_live_nonzero_upper':peak,'paid':dict(sorted(paid.items())),'operation_counts':dict(ops),'rational_frames':len(touched),'rational_nested_edges':len(edges),'partial_helper_roles':partial,'negative_controls':failures,
 'proof':'Exact QQ orthogonal frame decomposition + nesting proves decoded row induction at every native Q. Same-frame XOR preserves it; paid owned ERASE gives whole-function zero, so ZERO_Q is valid. All660 independent symbols prove all retained arbitrary functions and arbitrary initial owned storage. Tensor I_f preserves these identities for every f. For main ports D_P D_K=D_I and each D is involutive, giving the same symmetric 2x2 physical endpoint forward/reverse; each partial helper D_P is likewise involutive.',
 'remaining':['Global caller must bind swapped inverse headers/routes explicitly for all18calls.','Recompute complete target debit, owned lifetime/allocation, all fees and ordinary compiler/cover/bootstrap constants.','No full global cold replay or ordinary acceptance performed here.'],'evidence_kind':'Separate internal AI audit, not external verification.'}
 (HERE/'LOCAL-REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:out[k]for k in('status','retained_originals','owned_allocated','rational_frames','rational_nested_edges','partial_helper_roles','negative_controls')},ensure_ascii=True))
if __name__=='__main__':main()
