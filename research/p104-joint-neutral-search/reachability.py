"""Favorable temporal span propagation, granting free mixing and unlimited retention.

A MOVE may convey the entire source frame span, a relaxation of its one-field
capacity. Every legal scalar sequence on this fixed itinerary is contained.
"""
from preflight import *

def reach_test(w,c,prefix,ch,program=None):
 n=w['public'];N=n+w['owned_fields'];p=c['pivot'];fresh=N
 _,desired,k,q,eta=endpoints(w,c)
 reach=defaultdict(int)
 for r,f in enumerate(ch):
  if f is not None:reach[f]|=1<<r
 # Old p is retired, and its continuation is the new independent input.
 reach[ch[p]]&=~(1<<p);reach[c['frame']]|=(1<<p)|(1<<fresh)
 for e in (program or w['program'])[c['cut']+1:]:
  if e[0]=='MOVE':reach[e[3]]|=reach[e[2]]
 actual=[]
 for r,row in enumerate(prefix):
  z=dict(row);add(z,k,sum(v*c['beta'].get(j,0) for j,v in row.items()));add(z,{p:Q(1)},-row.get(p,0));actual.append(z)
 actual[p]={p:Q(1)};actual.append({fresh:Q(1)})
 grouped=defaultdict(list)
 for r in (set(c['d'])-{p})|{fresh}:
  f=w['final'][p if r==fresh else r];grouped[f].append(r)
 fails=[];ranks={}
 for f,targets in grouped.items():
  mask=reach[f];b=basis(sorted((actual[r] for r in range(N+1) if mask>>r&1),key=len));ranks[f]=len(b)
  for r in targets:
   z=rem(desired[r],b)
   if z:fails.append(dict(role=r,frame=f,remainder=z,available_rank=len(b)))
 return fails,ranks

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--word',default='word5718.json.gz');ap.add_argument('--contacts',default='contacts5718.json');ap.add_argument('--out',default='reach5718.json');ap.add_argument('--max-defects',type=int,default=3);a=ap.parse_args()
 w=load(a.word);d=json.loads((HERE/'results'/a.contacts).read_text());need(d['source_sha256']==PINS[a.word],'source join');cuts=d['cuts'];by=defaultdict(list)
 for j,c in enumerate(cuts):
  if c['pivot']==440 or len(c['d'])>a.max_defects:continue
  for k in ('a','c','h0','d','beta'):c[k]=unrow(c[k])
  by[c['cut']].append((j,c))
 N=w['public']+w['owned_fields'];rows=[{r:Q(1)} for r in range(N)];ch=w['initial']+[None]*w['owned_fields'];out=[]
 for i,e in enumerate(w['program']):
  apply(rows,e);charts_step(ch,e)
  for j,c in by[i]:
   fails,ranks=reach_test(w,c,rows,ch);out.append(dict(index=j,cut=i,pivot=c['pivot'],trigger=c['trigger'],defects=len(c['d']),failed=fails,ranks=ranks))
   if len(out)%20==0: print(dict(completed=len(out),rejected=sum(bool(s['failed']) for s in out)),flush=True)
 (HERE/'results'/a.out).write_text(json.dumps(fmt(dict(source_sha256=PINS[a.word],max_defects=a.max_defects,results=out)),indent=2)+'\n')
 print(dict(tested=len(out),rejected=sum(bool(s['failed']) for s in out),survivors=sum(not s['failed'] for s in out)),flush=True)
 print([(s['index'],s['cut'],s['pivot'],s['defects']) for s in out if not s['failed']][:80],flush=True)
if __name__=='__main__':main()
