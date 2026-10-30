"""Emit and independently replay dyadic words; no modular implementation claims."""
from joint import *

def scalar_cost(e):
 if e[0]=='MOVE':return 0
 if e[0] in ('INIT','CLEAR'):return 2
 q=Q(e[-2]);a,b=abs(q.numerator),q.denominator
 return 2*(abs(a.bit_length()-b.bit_length())+(q<0)) if e[0]=='SCALE' else 2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)

def audit(w):
 n=w['public'];N=n+w['owned_fields'];rows=[{r:Q(1)} for r in range(N)];ch=w['initial']+[None]*w['owned_fields'];fs=[span(x) for x in w['frames']];active=set();unwritten=set();paid=Counter();peak=life=0
 for i,e in enumerate(w['program']):
  op,r=e[:2];need(0<=r<N,'role index')
  if op=='INIT':
   need(r>=n and ch[r] is None,'owned INIT');ch[r]=e[2];active.add(r);unwritten.add(r);peak=max(peak,len(active));life+=1
  elif op=='CLEAR':need(r in active and ch[r]==e[2],'owned CLEAR');ch[r]=None;active.remove(r);unwritten.discard(r)
  elif op=='MOVE':
   need(ch[r]==e[2] and e[4]==(r in active),'MOVE source/ownership')
   need(fs[e[3]]<fs[e[2]] if e[4] else fs[e[2]]<fs[e[3]],'MOVE containment')
   ch[r]=e[3];paid[abs(len(w['frames'][e[2]])-len(w['frames'][e[3]]))]+=1
  else:
   need(ch[r]==e[-1],'scalar destination frame');q=Q(e[-2]);a,b=abs(q.numerator),q.denominator
   need(q and b&(b-1)==0 and abs(q)+1<2**16,'dyadic scalar coefficient')
   if op=='SCALE':need(a&(a-1)==0,'SCALE dyadic unit')
   else:
    need(e[2]!=r and 0<=e[2]<N and ch[e[2]]==e[-1],'scalar source frame')
    if op=='COPY':need(r in unwritten,'owned first COPY')
   unwritten.discard(r)
  apply(rows,e)
 need(not active and ch[:n]==w['final'],'final frame/ownership')
 for r,row in enumerate(rows):
  target={r:Q(1)} if r<n else {}
  if r-112 in w['live']:target[r-112]=Q(1)
  need(row==target,'endpoint '+str(r))
 main=set(w['live'])|{r+112 for r in w['live']}
 targets=Counter(len(w['frames'][w['final'][r]])-len(w['frames'][w['initial'][r]]) for r in range(n) if r not in main)
 return dict(columns=N,paid=dict(paid),targets=dict(targets),scalar=sum(map(scalar_cost,w['program'])),owned_peak=peak,owned_lifetimes=life)

def normalize_group(rows,desired,roles,frame):
 # Reduce actual and desired matrices by identical canonical row elimination.
 # If inversions are not dyadic units the emitter stops, even if Q rowspaces agree.
 def reduce(vals):
  vals={r:dict(vals[r]) for r in roles};ops=[];used=[]
  for col in sorted(set().union(*(set(v) for v in vals.values()))):
   possible=[r for r in roles if r not in used and vals[r].get(col)]
   if not possible:continue
   r=possible[0];q=vals[r][col]
   if q!=1:
    inv=1/q;need(abs(inv.numerator)&(abs(inv.numerator)-1)==0 and inv.denominator&(inv.denominator-1)==0,'non-unit pivot')
    vals[r]=scale(vals[r],inv);ops.append(['SCALE',r,str(inv),frame])
   for s in roles:
    if s!=r and vals[s].get(col):
     q=-vals[s][col];need(q.denominator&(q.denominator-1)==0,'non-dyadic elimination')
     add(vals[s],vals[r],q);ops.append(['ADD',s,r,str(q),frame])
   used.append(r)
  return vals,used,ops
 va,ua,oa=reduce(rows);vd,ud,od=reduce(desired)
 # Matching pivot rows may require permutation. Emit swaps as three ADDs and a sign.
 need(len(ua)==len(roles)==len(ud),'full group rank')
 for src,dst in zip(ua,ud):
  if src==dst:continue
  # In current normalized va, move row with same canonical functional to target slot.
  holder=next(r for r in roles if va[r]==vd[dst])
  if holder==dst:continue
  oa.extend([['ADD',dst,holder,'1',frame],['ADD',holder,dst,'-1',frame],['ADD',dst,holder,'1',frame],['SCALE',holder,'-1',frame]])
  va[dst],va[holder]=va[holder],va[dst]
 need(va==vd,'canonical same-rowspace')
 inv=[]
 for e in reversed(od):
  x=list(e);x[-2]=str(1/Q(e[-2]) if e[0]=='SCALE' else -Q(e[-2]));inv.append(x)
 return oa+inv

def construct(w,c,extra=()):
 n=w['public'];N=n+w['owned_fields'];p=c['pivot'];out=deepcopy(w);out['public']=n+1;out['initial']=w['initial']+[c['frame']];out['final']=w['final']+[w['final'][p]];out['final'][p]=c['frame']
 k0=dict(c['c']);add(k0,{p:Q(1)},-1);program=[];u=w['initial'][p]
 for r,q in sorted(k0.items()):program.append(['ADD',p,r,str(-q),u])
 for r,q in sorted(c['beta'].items()):
  if r!=p:program.append(['ADD',r,p,str(q),u])
 def ren(r,i):
  if r>=n:return r+1
  if i>c['cut'] and r==p:return n
  return r
 extras=defaultdict(list)
 for i,e in extra:extras[i].append(e)
 for i,orig in enumerate(w['program']):
  e=list(orig);e[1]=ren(e[1],i)
  if e[0] in ('ADD','COPY'):e[2]=ren(e[2],i)
  program.append(e)
  if i==c['cut']:
   for r,q in c['a'].items():
    if r!=p:program.append(['ADD',p,r,str(q),c['frame']])
  for e0 in extras[i]:
   e=list(e0);e[1]=n if e[1]==N else e[1]+(e[1]>=n)
   if e[0] in ('ADD','COPY'):e[2]=n if e[2]==N else e[2]+(e[2]>=n)
   program.append(e)
 out['program']=program
 rows=[{r:Q(1)} for r in range(N+1)]
 for e in program:apply(rows,e)
 desired=[{r:Q(1)} if r<n+1 else {} for r in range(N+1)]
 for r in w['live']:desired[r+112][r]=Q(1)
 groups=defaultdict(list)
 for r,f in enumerate(out['final']):groups[f].append(r)
 for f,roles in groups.items():
  if any(rows[r]!=desired[r] for r in roles):
   ops=normalize_group(rows,desired,roles,f);program.extend(ops)
   for e in ops:apply(rows,e)
 out['schema']='p104-joint-neutral-search/1';return out

def main():
 w=load('word5713.json.gz');cuts=json.loads((HERE/'results/contacts5713.json').read_text())['cuts'];c=next(c for c in cuts if c['cut']==14330 and c['pivot']==708 and c['a']=={'708':'1','154':'1/2'})
 for k in ('a','c','h0','d','beta'):c[k]=unrow(c[k])
 out=construct(w,c);receipt=audit(out);receipt.update(source_sha256=PINS['word5713.json.gz'],cut=c['cut'],pivot=c['pivot'],status='positive_control_emitted_exact_dyadic_word')
 (HERE/'results/positive-word.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0));(HERE/'results/positive.json').write_text(json.dumps(fmt(receipt),indent=2)+'\n');print(receipt)
if __name__=='__main__':main()
