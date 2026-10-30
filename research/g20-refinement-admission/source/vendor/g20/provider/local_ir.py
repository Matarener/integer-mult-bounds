"""Local physical ARRAY IR and exact types; portable standard library only."""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from math import gcd

N=658;OWNED=(658,659);EXPECTED={1:1318,2:1342,3:77,4:40,5:102,6:10,7:18}
def need(c,m):
 if not c:raise ValueError(m)
def transpose_rows(a,n=N):return [sum(((r>>j)&1)<<i for i,r in enumerate(a))for j in range(n)]
def combo(a,mask):
 x=0
 while mask:b=mask&-mask;x^=a[b.bit_length()-1];mask^=b
 return x
def rowproduct(a,b):return [combo(b,r)for r in a]
def baseline_program(word,reverse=False):
 out=[]
 for op,d,s,c,f,z in reversed(word['records'])if reverse else word['records']:
  if op==0:out.append(['Q',d,c if reverse else s,s if reverse else c,f])
  elif op==1:out.append(['ADD',d,s,f])
  elif op==(3 if reverse else 2):out.append(['COPY',s,d,c,7])
  else:out.append(['TICKET_CLEAR',s,d,c])
 return out
def ad_inverse(program,birth,exit):
 source=[]
 for e in program:
  op=e[0]
  if op=='ADD':source.append(['ADD',e[1],e[2]])
  elif op=='Q':source.append(e)
  elif op=='COPY':source.extend([['COPY',e[1],e[2]],['Q',e[1],e[3],0,e[4]]])
  else:need(op in('INIT','CLEAR','TICKET_CLEAR'),'Known local inverse operation');source.append(['CLEAR',e[1]])
 raw=[]
 for e in reversed(source):
  if e[0]=='ADD':raw.append(['ADD',e[2],e[1]])
  elif e[0]=='Q':raw.append(['Q',e[1],e[3],e[2],e[4]])
  elif e[0]=='COPY':raw.extend([['ADD',e[2],e[1]],['CLEAR',e[1]]])
  else:raw.append(e)
 raw.extend(['CLEAR',d]for d in OWNED)
 st=birth[:]+[None,None];zero=[False]*N+[True,True];out=[];retags=[]
 def header(d,f,k):
  need(d in OWNED and zero[d],'Only known entire-functionzero can be reheadered')
  if st[d]!=f:out.append(['INIT',d,f]);retags.append({'raw_instruction':k,'owner':d,'from':st[d],'to':f});st[d]=f
 for k,e in enumerate(raw):
  op,d=e[:2]
  if op=='CLEAR':need(d in OWNED,'No original CLEAR');out.append(e);zero[d]=True;st[d]=None
  elif op=='Q':
   if d in OWNED and zero[d]:header(d,e[2],k)
   need(st[d]==e[2],'AD actual QUERY inputframe');out.append(e);st[d]=e[3]
  else:
   s=e[2]
   if d in OWNED and zero[d]and st[s]is not None:header(d,st[s],k)
   if s in OWNED and zero[s]and st[d]is not None:header(s,st[d],k)
   if st[d]is None and st[s]is None:header(d,0,k);header(s,0,k)
   need(st[d]==st[s]and st[d]is not None,'AD commonactualFRAME');out.append(['ADD',d,s,st[d]]);zero[d]=zero[d]and zero[s]
 need(st==exit+[None,None]and all(zero[d]for d in OWNED),'AD originalflags/ownedreturn')
 return out,retags

class Geometry:
 def __init__(self,frames):self.frames=frames;self.dims={int(k):v['dim']for k,v in frames.items()}
 @lru_cache(None)
 def nested(self,s,t,k):
  lo,hi=(s,t)if self.dims[s]<self.dims[t]else(t,s)
  need(0<k<8 and self.dims[hi]-self.dims[lo]==k,'Proper actual residual rank, not FRAME id')
  need(all(sum(F(v)*F(w)for v,w in zip(a,b))==0 for a in self.frames[str(lo)]['B']for b in self.frames[str(hi)]['A']),'ExactQQ nested residual')
  return lo,hi
 @lru_cache(None)
 def project_mod(self,f,m):
  b=[[F(v).numerator*pow(F(v).denominator,-1,m)%m for v in row]for row in self.frames[str(f)]['B']]
  if not b:return tuple(tuple(0 for _ in range(8))for _ in range(8))
  def mm(a,b):return [[sum(x*y for x,y in zip(r,c))%m for c in zip(*b)]for r in a]
  size=len(b);bt=list(map(list,zip(*b)));gram=mm(b,bt);a=[r[:]+[int(i==j)for j in range(size)]for i,r in enumerate(gram)]
  for j in range(size):
   p=next(i for i in range(j,size)if gcd(a[i][j],m)==1);a[j],a[p]=a[p],a[j];v=pow(a[j][j],-1,m);a[j]=[x*v%m for x in a[j]]
   for i in range(size):
    if i!=j:
     v=a[i][j];a[i]=[(x-v*y)%m for x,y in zip(a[i],a[j])]
  return tuple(map(tuple,mm(mm(bt,[r[size:]for r in a]),b)))
 @lru_cache(None)
 def residual_mod(self,s,t,k,m):
  lo,hi=self.nested(s,t,k);return tuple(tuple((x-y)%m for x,y in zip(a,b))for a,b in zip(self.project_mod(hi,m),self.project_mod(lo,m)))
 @staticmethod
 @lru_cache(None)
 def move(p,x,m):
  diff=[(x[i]-x[15-i])%m for i in range(8)];z=[sum(v*w for v,w in zip(r,diff))%m for r in p];out=list(x)
  for i in range(8):out[i]=(out[i]-z[i])%m;out[15-i]=(out[15-i]+z[i])%m
  return tuple(out)

def replay(program,birth,exit,geometry,modulus=None,mutant=None):
 st=birth[:]+[None,None];rows=[1<<i for i in range(N)]+[0,0];norm=[1]*N+[0,0];versions=[0]*660;knownzero=[False]*N+[True,True];tickets={};counts=Counter();paid=Counter();peak=1;privatepeak=0;epochs=[0]*660;retag_count=0;changed=False
 fields=None
 if modulus:
  point=tuple(v%modulus for v in(1,2,4,8,16,32,64,128,3,5,7,11,13,17,19,23));fields=[{point:1<<i}for i in range(N)]+[{},{}]
 def transform(field,p):return {geometry.move(p,x,modulus):v for x,v in field.items()}
 for ix,orig in enumerate(program):
  e=orig[:];op,d=e[:2]
  if mutant=='wrong_rank4'and op=='Q'and d==464 and set(e[2:4])=={0,507}and not changed:e[4]=3;changed=True
  if mutant=='omit_shadow_clear'and op=='CLEAR'and d==659 and not changed:changed=True;continue
  if mutant=='wrong_shadow_frame'and op=='INIT'and d==659 and not changed:e[2]=0;changed=True
  counts[op]+=1
  if op=='Q':
   s,t,k=e[2:];need(st[d]==s,'Actual currentSOURCE frame');geometry.nested(s,t,k);need(not any(v[0]==d for v in tickets.values()),'SOURCE notmoved during immutableCOPYlease');st[d]=t;versions[d]+=1;paid[k]+=1
   if fields is not None:fields[d]=transform(fields[d],geometry.residual_mod(s,t,k,modulus))
  elif op=='ADD':
   s,f=e[2:];need(d!=s and st[d]==st[s]==f,'Actualaligned commonFRAME ADD');need(not any(v[0]==d for v in tickets.values()),'ImmutableSOURCE notVALUEwritten');rows[d]^=rows[s];norm[d]+=norm[s];peak=max(peak,norm[d]);knownzero[d]=knownzero[d]and knownzero[s];versions[d]+=1
   if fields is not None:
    for x,v in fields[s].items():
     z=fields[d].get(x,0)^v
     if z:fields[d][x]=z
     else:fields[d].pop(x,None)
  elif op=='COPY':
   s,f,k=e[2:];need(d in OWNED and knownzero[d]and not rows[d]and st[d]is None and d not in tickets,'WholeownedfreshzeroCOPY');need(st[s]==f and k==geometry.dims[f]==7,'Actualrank7capture SOURCE');rows[d]=rows[s];norm[d]=norm[s];st[d]=0;knownzero[d]=False;tickets[d]=(s,versions[s],f,rows[s]);paid[k]+=1;versions[d]+=1;epochs[d]+=1
   if fields is not None:fields[d]=transform(fields[s],geometry.project_mod(f,modulus))
  elif op=='TICKET_CLEAR':
   s,f=e[2:];need(tickets[d]==(s,versions[s],f,rows[s])and st[s]==f and rows[d]==rows[s]and st[d]==0,'FreshcurrentimmutableSOURCE guard');tickets.pop(d);rows[d]=norm[d]=0;knownzero[d]=True;st[d]=None;versions[d]+=1
   if fields is not None:need(fields[d]==transform(fields[s],geometry.project_mod(f,modulus)),'Wholefunction COPYguard');fields[d]={}
  elif op=='INIT':
   f=e[2];need(d in OWNED and knownzero[d]and rows[d]==0 and d not in tickets,'Only wholeknownzero ownedreheader');st[d]=f;epochs[d]+=1;retag_count+=1
  else:
   need(op=='CLEAR'and d in OWNED and d not in tickets,'Paid fullownedpayloadCLEAR, notoriginal/inverseSOURCE');rows[d]=norm[d]=0;knownzero[d]=True;st[d]=None;versions[d]+=1
   if fields is not None:fields[d]={}
  privatepeak=max(privatepeak,sum(st[p]is not None for p in OWNED))
 need(st==exit+[None,None]and not tickets and rows[N:]==[0,0]and all(knownzero[p]for p in OWNED),'All658originalFLAGs and ownedwholepayloadreturn')
 if fields is not None:
  for out in range(N):
   expected={};mask=rows[out]
   while mask:
    b=mask&-mask;raw=b.bit_length()-1;y=geometry.move(geometry.project_mod(exit[out],modulus),geometry.move(geometry.project_mod(birth[raw],modulus),point,modulus),modulus);expected[y]=expected.get(y,0)^b;mask^=b
   need(fields[out]=={x:v for x,v in expected.items()if v},'ALL658symbol fullphysicalFUNCTION endpoint factor')
  need(all(not fields[p]for p in OWNED),'EveryownednativeFUNCTIONzero')
 return rows[:N],{'paid':dict(sorted(paid.items())),'rankmass':sum(k*v for k,v in paid.items()),'operation_counts':dict(counts),'private_allocated':2,'private_peak':privatepeak,'owned_header_acquisitions':retag_count,'majorant_bits':peak.bit_length(),'majorant':str(peak),'epochs':{str(p):epochs[p]for p in OWNED},'native_all658_symbols':modulus},fields
