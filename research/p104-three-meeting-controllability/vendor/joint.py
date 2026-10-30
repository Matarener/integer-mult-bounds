"""Finite exact neutral ADD search with one existing MOVE retimed inside a touch gap.

State keeps every input coefficient. Up to two ADDs at first meeting, one at
second, and a favorable terminal normalization test. No monotone repair filter.
"""
from preflight import *
from copy import deepcopy

def renamed(e,p,fresh):
 e=list(e)
 if e[1]==p:e[1]=fresh
 if e[0] in ('ADD','COPY') and e[2]==p:e[2]=fresh
 return e

def raw(w,c,sites):
 n=w['public'];N=n+w['owned_fields'];p=c['pivot'];fresh=N
 _,_,k,_,_=endpoints(w,c)
 rows=[{r:Q(1)} for r in range(N)]+[{}];ch=w['initial']+[None]*w['owned_fields']+[c['frame']]
 for r in range(N):
  add(rows[r],k,c['beta'].get(r,0))
  if r==p:add(rows[r],{p:Q(1)},-1)
 saved={}
 for i,orig in enumerate(w['program']):
  e=renamed(orig,p,fresh) if i>c['cut'] else orig
  apply(rows,e);charts_step(ch,e)
  if i==c['cut']:rows[p]={p:Q(1)};rows[fresh]={fresh:Q(1)};ch[p]=ch[fresh]=c['frame']
  if i in sites:saved[i]=([dict(z) for z in rows],list(ch))
 return saved

def responses(w,p,site,roles,stop=None):
 N=w['public']+w['owned_fields'];fresh=N;cols=[{r:Q(1)} for r in range(N+1)]
 end=len(w['program']) if stop is None else stop+1
 for orig in reversed(w['program'][site+1:end]):
  e=renamed(orig,p,fresh);op,r=e[:2]
  if op in ('INIT','CLEAR'):cols[r]={}
  elif op=='SCALE':cols[r]=scale(cols[r],Q(e[-2]))
  elif op!='MOVE':
   add(cols[e[2]],cols[r],Q(e[-2]))
   if op=='COPY':cols[r]={}
 return {r:cols[r] for r in roles}

def terminal_groups(w,c):
 N=w['public']+w['owned_fields'];p=c['pivot'];ch=w['final']+[None]*w['owned_fields']+[w['final'][p]];ch[p]=c['frame'];groups=defaultdict(list)
 for r,f in enumerate(ch):
  if f is not None:groups[f].append(r)
 return groups

def groups_check(base,desired,groups,updates,fast=None):
 for f,roles in groups.items():
  if fast is not None and f not in fast:continue
  changed={}
  for d,s,a in updates:
   for r,v in d.items():
    if r in roles:
     if r not in changed:changed[r]=dict(base[r])
     add(changed[r],s,a*v)
  if not changed:actual=lambda r:base[r]
  else:actual=lambda r:changed.get(r,base[r])
  if all(actual(r)==desired[r] for r in roles):continue
  b=basis(actual(r) for r in roles)
  if any(rem(desired[r],b) for r in roles):return False
 return True

def actions(roles):
 return [(r,s,a) for r in roles for s in roles if r!=s for a in (Q(-2),Q(-1),Q(-1,2),Q(1,2),Q(1),Q(2))]

def run(w,c,first,second,first_frame,second_frame,depth=1,cap=30000,first_roles=None,second_roles=None):
 saved=raw(w,c,{first,second});R1,C1=saved[first];R2,C2=saved[second]
 g1=[r for r,f in enumerate(C1) if f==first_frame];g2=[r for r,f in enumerate(C2) if f==second_frame]
 if first_roles is not None:need(set(first_roles)<=set(g1),'first role frame');g1=first_roles
 if second_roles is not None:need(set(second_roles)<=set(g2),'second role frame');g2=second_roles
 need(len(g1)<=6 and len(g2)<=6,'bounded meeting size')
 groups=terminal_groups(w,c);base,desired,*_=endpoints(w,c)
 bad=[f for f,roles in groups.items() if not groups_check(base,desired,{f:roles},[])]
 D1=responses(w,c['pivot'],first,g1);D2=responses(w,c['pivot'],second,g2);mid=responses(w,c['pivot'],first,g1,second)
 a1=actions(g1);a2=[None]+actions(g2);tested=0;passfast=0;survivors=[];neutral=0
 # a fixed input list is the complete stated domain at each meeting.
 seqs=[()] + [(a,) for a in a1]
 if depth==2:seqs +=[(a,b) for a in a1 for b in a1]
 for seq in seqs:
  local={r:dict(R1[r]) for r in g1};up=[];midrows={r:dict(R2[r]) for r in g2}
  for r,s,a in seq:
   src=dict(local[s]);add(local[r],src,a);up.append((D1[r],src,a))
   for v,b in mid[r].items():
    if v in midrows:add(midrows[v],src,a*b)
  if seq and not groups_check(base,desired,groups,up,fast=bad):neutral+=1
  for action in a2:
   if tested>=cap:return dict(tested=tested,cap=cap,truncated=True,groups=[g1,g2],first_sequences=len(seqs),neutral_first_sequences=neutral,fast_survivors=passfast,survivors=survivors)
   updates=list(up)
   if action:
    r,s,a=action;updates.append((D2[r],midrows[s],a))
   tested+=1
   if not groups_check(base,desired,groups,updates,fast=bad):continue
   passfast+=1
   if groups_check(base,desired,groups,updates):
    survivors.append(dict(first=seq,second=action));print('SURVIVOR',fmt(survivors[-1]),flush=True)
 return dict(tested=tested,cap=cap,truncated=False,groups=[g1,g2],first_sequences=len(seqs),neutral_first_sequences=neutral,fast_survivors=passfast,survivors=survivors)

def retime(w,index,after):
 e=w['program'][index];need(e[0]=='MOVE' and not e[4],'public MOVE only');r=e[1]
 lo,hi=sorted((index,after));between=w['program'][lo+1:hi+1] if after>index else w['program'][lo+1:hi]
 need(all(x[1]!=r and not(x[0] in ('ADD','COPY') and x[2]==r) for x in between),'retiming crosses a role touch')
 out=deepcopy(w);p=out['program'];move=p.pop(index);at=after if after>index else after+1;p.insert(at,move)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--index',type=int,default=350);ap.add_argument('--first',type=int,default=13644);ap.add_argument('--second',type=int,default=16800);ap.add_argument('--first-frame',type=int,default=597);ap.add_argument('--second-frame',type=int,default=170);ap.add_argument('--depth',type=int,default=1);ap.add_argument('--cap',type=int,default=30000);ap.add_argument('--first-roles');ap.add_argument('--second-roles');ap.add_argument('--move',type=int);ap.add_argument('--after',type=int);ap.add_argument('--out',default='joint695.json');a=ap.parse_args()
 w=load('word5718.json.gz');c=json.loads((HERE/'results/contacts5718.json').read_text())['cuts'][a.index]
 for k in ('a','c','h0','d','beta'):c[k]=unrow(c[k])
 if a.move is not None:w=retime(w,a.move,a.after)
 t=time.monotonic();result=run(w,c,a.first,a.second,a.first_frame,a.second_frame,a.depth,a.cap,[int(v) for v in a.first_roles.split(',')] if a.first_roles else None,[int(v) for v in a.second_roles.split(',')] if a.second_roles else None);result.update(source_sha256=PINS['word5718.json.gz'],index=a.index,cut=c['cut'],pivot=c['pivot'],meetings=[a.first,a.second],frames=[a.first_frame,a.second_frame],depth=a.depth,route=dict(move=a.move,after=a.after),seconds=time.monotonic()-t)
 (HERE/'results'/a.out).write_text(json.dumps(fmt(result),indent=2)+'\n');print(json.dumps(fmt(result)),flush=True)
if __name__=='__main__':main()
