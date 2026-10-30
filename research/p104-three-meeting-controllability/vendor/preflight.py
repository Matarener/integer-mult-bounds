"""Exact favorable endpoint availability, before scalar program search."""
from search import *

def basis(rows):
 out={}
 for row in rows:
  z=dict(row)
  while z:
   j=min(z)
   if j not in out:
    out[j]=scale(z,1/z[j]);break
   add(z,out[j],-z[j])
 return out

def rem(row,b):
 z=dict(row)
 while z and min(z) in b:add(z,b[min(z)],-z[min(z)])
 return z

def endpoints(w,c):
 n=w['public'];N=n+w['owned_fields'];p=c['pivot'];fresh=N
 k={p:Q(2)};add(k,c['c'],-1)
 q=dict(c['h0']);add(q,k,sum(v*c['beta'].get(j,0) for j,v in q.items()));add(q,{p:Q(1)},-c['h0'].get(p,0))
 eta=dict(k);add(eta,q,-1);eta[fresh]=Q(1)
 rows=[{r:Q(1)} if r<n else {} for r in range(N)]+[{fresh:Q(1)}]
 for r in w['live']:rows[r+112][r]=Q(1)
 desired=[dict(z) for z in rows]
 for r,v in c['d'].items():
  if r!=p:add(rows[r],eta,v)
 rows[p]={p:Q(1)};rows[fresh]=dict(eta)
 return rows,desired,k,q,eta

def terminal_test(w,c):
 rows,desired,*_=endpoints(w,c);n=w['public'];N=n+w['owned_fields'];p=c['pivot']
 ch=w['final']+[None]*w['owned_fields']+[w['final'][p]];ch[p]=c['frame']
 groups=defaultdict(list)
 for r,f in enumerate(ch):
  if f is not None:groups[f].append(r)
 failed=[]
 for f,roles in groups.items():
  if all(rows[r]==desired[r] for r in roles):continue
  b=basis(rows[r] for r in roles)
  for r in roles:
   z=rem(desired[r],b)
   if z:failed.append(dict(role=r,frame=f,remainder=z))
 return failed

def closed_tests(w,c,prefix,ch,last_inbound):
 n=w['public'];N=n+w['owned_fields'];p=c['pivot'];fresh=N
 _,desired,k,q,eta=endpoints(w,c)
 def rightB(row):
  out=dict(row);add(out,k,sum(v*c['beta'].get(j,0) for j,v in row.items()));add(out,{p:Q(1)},-row.get(p,0));return out
 defects=set(c['d'])-{p};defects.add(fresh)
 groups=defaultdict(list)
 for r in defects:
  f=w['final'][p if r==fresh else r]
  if last_inbound.get(f,-1)<=c['cut']:groups[f].append(r)
 failed=[]
 for f,targets in groups.items():
  vals=[rightB(prefix[r]) for r,g in enumerate(ch) if g==f and r!=p]
  if ch[p]==f:vals.append({fresh:Q(1)})
  if c['frame']==f:vals.append({p:Q(1)})
  b=basis(vals)
  for r in targets:
   z=rem(desired[r],b)
   if z:failed.append(dict(role=r,frame=f,remainder=z))
 return failed

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--word',default='word5718.json.gz');ap.add_argument('--contacts',default='contacts5718.json');ap.add_argument('--out',default='preflight5718.json');a=ap.parse_args()
 w=load(a.word);d=json.loads((HERE/'results'/a.contacts).read_text());need(d['source_sha256']==PINS[a.word],'source join')
 cuts=d['cuts']
 for c in cuts:
  for k in ('a','c','h0','d','beta'):c[k]=unrow(c[k])
 by=defaultdict(list)
 for j,c in enumerate(cuts):by[c['cut']].append(j)
 last={e[3]:i for i,e in enumerate(w['program']) if e[0]=='MOVE'}
 n=w['public'];N=n+w['owned_fields'];rows=[{r:Q(1)} for r in range(N)];ch=w['initial']+[None]*w['owned_fields'];out=[];counts=Counter()
 for i,e in enumerate(w['program']):
  apply(rows,e);charts_step(ch,e)
  for j in by[i]:
   c=cuts[j]
   # This explicitly omits the commissioned known-closed helper440 contract.
   if c['pivot']==440:counts['excluded_fixed440']+=1;continue
   fail=closed_tests(w,c,rows,ch,last);terminal=terminal_test(w,c)
   counts['tested']+=1;counts['closed_rejects']+=bool(fail);counts['terminal_rejects']+=bool(terminal)
   out.append(dict(index=j,cut=c['cut'],pivot=c['pivot'],trigger=c['trigger'],ranks=c['ranks'],defects=len(c['d']),closed_failed=fail,terminal_failed=terminal))
 (HERE/'results'/a.out).write_text(json.dumps(fmt(dict(source_sha256=PINS[a.word],counts=dict(counts),results=out)),indent=2)+'\n')
 print(dict(counts),flush=True)
 print('terminal survivors',[(s['index'],s['cut'],s['pivot'],s['defects']) for s in out if not s['terminal_failed']][:60],flush=True)
if __name__=='__main__':main()
