"""Search three-way stage splits through exact small matrix frames.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import itertools,json,time
from pathlib import Path
import multisplit_search as M

def eye(n):return tuple(1<<i for i in range(n))
def add(a,b):return tuple(x^y for x,y in zip(a,b))
def mul(a,b):
 out=[]
 for row in a:
  val=0
  for j in range(len(b)):
   if row>>j&1:val^=b[j]
  out.append(val)
 return tuple(out)
def rank(a):
 basis={}
 for v in a:
  while v:
   j=v.bit_length()-1
   if j not in basis:basis[j]=v;break
   v^=basis[j]
 return len(basis)
def inv(a):
 n=len(a);r=[x|(1<<(n+i)) for i,x in enumerate(a)]
 for j in range(n):
  k=next(i for i in range(j,n) if r[i]>>j&1);r[j],r[k]=r[k],r[j]
  for i in range(n):
   if i!=j and r[i]>>j&1:r[i]^=r[j]
 return tuple(x>>n for x in r)
def frame(a):
 b=inv(a)
 return [tuple(b[k] if row>>k&1 else 0 for row in a) for k in range(3)]
def poly_product(a,b):
 out={};z=(0,0,0)
 for i,ai in a.items():
  for j,bj in b.items():
   k=tuple(x+y for x,y in zip(i,j));out[k]=add(out.get(k,z),mul(ai,bj))
 return {k:v for k,v in out.items() if any(v)}
def word(fs):
 g=len(fs);base=(0,)*g;w={base:eye(3)}
 for h in range(3):
  for j in range(g):
   d=list(base);d[j]=1;w=poly_product({base:eye(3),tuple(d):fs[j][h]},w)
 return w=={x:eye(3) for x in itertools.product((0,1),repeat=g)}

def linear(fs):
 order=[(j,k) for k in range(3) for j in range(3)];names,eq=M.equations(3,order)
 fixed=[]
 for f in fs:fixed.extend((f[0],(0,0,0),f[1],(0,0,0)))
 unknowns=(len(names)-len(fixed))*9;rows=[]
 for label,p in eq:
  values=[0]*9
  for w in p:
   letters=[(i,fixed[i] if i<len(fixed) else None) for i in w]
   ui=[i for i,x in letters if x is None]
   if not ui:
    a=eye(3)
    for _,x in letters:a=mul(a,x)
    for r,c in itertools.product(range(3),repeat=2):values[3*r+c]^=((a[r]>>c)&1)<<unknowns
   else:
    if len(ui)!=1:raise ValueError('Not linear')
    v=ui[0];start=(v-len(fixed))*9
    for rr,cc in itertools.product(range(3),repeat=2):
     a=eye(3)
     for i,x in letters:a=mul(a,x if x is not None else tuple(1<<cc if r==rr else 0 for r in range(3)))
     for r,c in itertools.product(range(3),repeat=2):values[3*r+c]^=((a[r]>>c)&1)<<(start+3*rr+cc)
  rows.extend(values)
 basis={};mask=(1<<unknowns)-1
 for value in rows:
  while value&mask:
   j=(value&mask).bit_length()-1
   if j not in basis:basis[j]=value;break
   value^=basis[j]
  else:
   if value>>unknowns:return None
 solution=0
 for j,row in sorted(basis.items()):
  if ((row&solution).bit_count()^(row>>unknowns))&1:solution|=1<<j
 return [tuple((solution>>(9*k+3*r))&7 for r in range(3)) for k in range(unknowns//9)]

def main():
 start=time.monotonic();frames=[frame(a) for a in itertools.product(range(8),repeat=3) if rank(a)==3];base=frame(eye(3))
 compatible=[f for f in frames if word([base,f])];print('frames',len(frames),'pair-compatible',len(compatible),flush=True)
 count=0;surv=[]
 for a,b in itertools.product(compatible,repeat=2):
  fs=[base,a,b]
  if not word(fs):continue
  count+=1;sol=linear(fs)
  if sol is not None:surv.append({'frames':fs,'tails':sol});print('FOUND',len(surv),flush=True)
 print('FINAL',count,len(surv),'seconds',round(time.monotonic()-start,2),flush=True)
 Path(__file__).with_name('M3-FRAME-SEARCH.json').write_text(json.dumps({'frames':len(frames),'pair_compatible':len(compatible),'full_stage_words':count,'survivors':surv},indent=2)+'\n')
if __name__=='__main__':main()
