# Standalone standard-library physical owner audit, adapted from credited PR3638 predicates.
from pathlib import Path
from collections import Counter,defaultdict
import gzip,json,hashlib
P=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def rank(U):
 piv={}
 for x in U:
  while x:
   b=x.bit_length()
   if b in piv:x^=piv[b]
   else:piv[b]=x;break
 return len(piv)
def audit(mutator=None):
 D=P/'inputs';T=360;order=read(D/'ORDER.json');dispatch=read(D/'DISPATCH.json');N=9*T
 need(len(order)==N and set(map(tuple,order))=={(s,r) for s in range(9) for r in range(T)},'call coverage')
 clock={tuple(v):i for i,v in enumerate(order)}
 need(all([clock[s,r] for s in range(9)]==sorted(clock[s,r] for s in range(9)) for r in range(T)),'source order')
 providers={(s,r):pid for s,r,pid in dispatch};need(len(providers)==len(dispatch)==N and set(providers)==set(clock),'dispatch')
 plan=read(D/'PLAN.json.gz');template=read(D/'TEMPLATE.json.gz');children={c['child']:c['rank'] for c in template['idle_children']};K=max(children)+1
 windows={}
 for owner in range(T):
  touched={};t=None
  for ev in template['execution_schedule']:
   kind=ev['kind']
   if kind in ('bank_padding_cover_sweep','translate_every_live_family'):continue
   if kind=='local_cover_sweep':t=clock[ev['stage'],owner];touched[next(x['pair'] for x in template['recipe'] if x['kind']=='local' and x['stage']==ev['stage'])]=t
   elif kind=='bridge':
    need(t is not None,'bridge source');touched[ev['src']]=t;touched[ev['dst']]=t
   elif kind=='idle_cover_sweep':
    need(t is not None,'idle source')
    for c in ev['child_indices']:
     if c in children:
      need((owner,c) not in windows,'unique child');windows[owner,c]=(children[c],touched.get(ev['pair'],-1),t)
   else:need(kind in ('terminal_Y_translations','terminal'),'source event')
  need(all((owner,c) in windows for c in children),'complete windows')
 families={c:2*plan['pairs'][str(c)]+plan['sides'][str(c)] for c in children}
 fwin=defaultdict(list)
 for (o,c),(cap,lo,hi) in windows.items():fwin[o,families[c]].append((lo,hi))
 for rows in fwin.values():need(all(max(a,c)>=min(b,d) for j,(a,b) in enumerate(rows) for c,d in rows[j+1:]),'source family windows disjoint')
 widths={};local=None
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  w=read(D/f'NATIVE-{tag}.json.gz');need(w['R']==408 and len(w['zero_buffers'])==91,'native stock')
  widths[pid]=[rank(w['frames'][w['final'][r]])-rank(w['frames'][w['start'][r]]) for r in range(224,632)]
  need(Counter(widths[pid])=={4:26,5:2,6:18,7:53,8:96,9:213},'native widths')
  loc={int(r):n for r,n in w['local_profile'].items()};need(local is None or local==loc,'provider paid profiles');local=loc
 need(local=={1:2440,2:725,3:224,4:102,5:20,8:8},'changed local bill')
 fill=read(D/'FILL.json.gz')
 if mutator:mutator(fill['rows'])
 need(fill['columns']==['time','helper','owner_replica','child','port','offset'] and fill['dispatch_overrides']==[],'literal schema')
 need(len(fill['rows'])==N*408,'role count');used=Counter();callfamilies=set()
 for j,row in enumerate(fill['rows']):
  need(len(row)==6 and all(type(x)is int for x in row),'integer role')
  t,h,o,c,p,z=row;need(t==j//408 and h==j%408,'ordered complete helper identities')
  if h==0:callfamilies=set()
  need((o,c) in windows and 0<=p<112,'owner child port')
  cap,lo,hi=windows[o,c];need(lo<t<=hi,'strict lower and closed upper window')
  family=o*896+families[c]*112+p;need(family not in callfamilies,'same-call physical family uniqueness');callfamilies.add(family)
  w=widths[providers[tuple(order[t])]][h];key=(o*K+c)*112+p
  need(z==used[key] and z+w<=cap,'compact chronological prefix and capacity');used[key]+=w
 idle=Counter()
 for (o,c),(cap,lo,hi) in windows.items():
  for p in range(112):
   left=cap-used[(o*K+c)*112+p];need(left>=0,'bin overflow')
   if left:idle[left]+=1
 profile=Counter({r:N*n for r,n in local.items()});profile.update(idle)
 expected={int(r):n for r,n in read(D/'PROFILE.json').items()};need(dict(profile)==expected,'complete paid histogram')
 need(sum(r*n for r,n in profile.items())==65088*T,'mass deficit')
 return dict(status='PASS_STANDARD_LIBRARY_INDEPENDENT_LITERAL_AUDIT',replicas=T,calls=N,roles=N*408,physical=896*T+408+8+91+2,idle=dict(idle),profile=dict(profile))
def controls():
 def reused_family(rows):
  rows[1][2:5]=rows[0][2:5]
 def duplicate_helper(rows):rows[1][1]=rows[0][1]
 def unpaid_hole(rows):rows[0][5]+=1
 results=[]
 for name,mutator,phrase in [('same_call_family',reused_family,'same-call physical family uniqueness'),('duplicate_helper',duplicate_helper,'ordered complete helper identities'),('unpaid_hole',unpaid_hole,'compact chronological prefix')]:
  try:audit(mutator)
  except ValueError as ex:
   need(phrase in str(ex),'wrong owner rejection: '+str(ex));results.append(name)
  else:raise ValueError('owner mutant accepted '+name)
 return results
if __name__=='__main__':print(json.dumps(dict(positive=audit(),controls=controls()),sort_keys=True),flush=True)
