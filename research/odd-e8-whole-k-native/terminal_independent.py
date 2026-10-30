"""Independent retained-path and old-gauge corroboration; default read-only."""
import argparse,gzip,hashlib,importlib.util,json,sys
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode=True

def need(q,s):
 if not q:raise ValueError(s)
def par(x):return x.bit_count()&1
def dot(x,y):return par(x&y)
def apply(cols,x):
 y=0
 for j,c in enumerate(cols):
  if x>>j&1:y^=c
 return y
def rows(cols):return [sum(((c>>j)&1)<<i for i,c in enumerate(cols))for j in range(len(cols))]
def comp(A,B):
 ac,ah=A;bc,bh=B
 return ([apply(ac,c)for c in bc],bh^sum(dot(ah,c)<<j for j,c in enumerate(bc)))
def invert(A):
 c,h=A;n=len(c);r=[v|(1<<(n+j))for j,v in enumerate(rows(c))]
 for j in range(n):
  p=next(i for i in range(j,n)if r[i]>>j&1);r[p],r[j]=r[j],r[p]
  for i in range(n):
   if i!=j and r[i]>>j&1:r[i]^=r[j]
 ic=rows([v>>n for v in r])
 return ic,sum(dot(h,v)<<j for j,v in enumerate(ic))
def rank(vs):
 piv={}
 for v in vs:
  while v:
   j=v.bit_length()-1
   if j not in piv:piv[j]=v;break
   v^=piv[j]
 return len(piv)
def emb(A,stage,L):
 c,h=A;n=1+8*L
 def lift(x):return (x&1)|((x>>1)<<(1+8*stage))
 out=[1<<j for j in range(n)]
 out[0]=lift(c[0])
 for j in range(1,9):out[8*stage+j]=lift(c[j])
 return out,lift(h)
def local_from_port(p):
 c=rows(p['G_rows']);z=p['Z_mask']
 return c,sum(dot(z,v)<<j for j,v in enumerate(c))
def state(word,n,basis):
 a={basis:(1,0)};den=0
 for e in word:
  if e[0]=='M':
   c,h=e[1:];a={apply(c,x):((-u,-v)if dot(h,x)else(u,v))for x,(u,v)in a.items()}
  elif e[0]=='phase':
   a={x:((u,v),(-v,u),(-u,-v),(v,-u))[e[1]%4]for x,(u,v)in a.items()}
  else:
   need(e[0]=='C','primitive');q,s=e[1:];b={}
   for x in set(a)|{x^q for x in a}:
    u,v=a.get(x,(0,0));w,z=a.get(x^q,(0,0));pair=(u-s*v+w+s*z,v+s*u+z-s*w)
    if pair!=(0,0):b[x]=pair
   a=b;den+=1
  while den and all(not(u&1)and not(v&1)for u,v in a.values()):a={x:(u//2,v//2)for x,(u,v)in a.items()};den-=1
 return a,den

def calculate(package):
 d=json.loads((package/'inputs/NORMALIZERS.json').read_bytes());root=list(zip(*d['mode_columns']))
 ports=[i for i,r in enumerate(root)if tuple(j for j,x in enumerate(r)if x)==(0,1,2,3)]
 need(len(ports)==8,'actual base8 cube')
 K=[[Fraction(int(a==b))-Fraction(sum(x*y for x,y in zip(root[a],root[b])),4)for b in ports]for i,a in enumerate(ports)]
 need(all(sum(bool(x)for x in r)==4 for r in K),'four actual nonzero edges per owner')
 actual=json.loads(gzip.decompress((package/'TERMINAL-PATHS.json.gz').read_bytes()));new_count=0;coefficient_not_powered=0
 for block in actual:
  L=block['stages'];n=1+8*L
  for p in block['paths']:
   ow=p['owners'];c=Fraction(1)
   for a,b in zip(ow[1:],ow):c*=K[a][b]
   need(c==Fraction(*p['coefficient']),'actual retained scalar coefficient product once')
   if abs(c)!=1:need(c!=c*c,'width2 coefficient control rejects c^f');coefficient_not_powered+=1
   v=p['G_columns'][0];epsilon=p['Z_before_permutation']&1
   need(p['terminal_removed_directions']==[1,v]and not v&1 and dot(v,v),'retained pure fresh normone image')
   need(p['one_copy_scalar_phase']==(-epsilon)%4 and p['inverse_line_sign']==(1 if epsilon else -1),'retained absolute signed phase')
   B=[(1<<j)^(1 if j==0 else 0)^(v if v>>j&1 else 0)for j in range(n)]
   need(rank(B)==n-2,'independent rank of I+ee^T+vv^T')
   new_count+=1
 need(new_count==1344,'all actual new gauge path records')
 # The same actual base8 K edges in the frozen old physical gauges.
 Li=[local_from_port(d['ports'][i])for i in ports];old_count=0;sparse_count=0;eps_seen=set();old_records=[]
 for L in [1,2,3]:
  n=1+8*L;paths=[(i,([1<<j for j in range(n)],0),Fraction(1))for i in range(8)]
  for stage in range(L):
   nxt=[]
   for j,M,c in paths:
    for i in range(8):
     if K[i][j]:
      edge=comp(invert(emb(Li[i],stage,L)),emb(Li[j],stage,L))
      nxt.append((i,comp(edge,M),K[i][j]*c))
   paths=nxt
  need(len(paths)==8*4**L,'old gauge path count')
  for owner,M,c in paths:
   cols,h=M;v=cols[0];eps=h&1;eps_seen.add(eps)
   need(not v&1 and dot(v,v),'old gauge fresh orthogonal Pauli image')
   # Signed monomial exact commutation with R is checked directly modulo4.
   # Weight(Gx)-wt(x) = 2 h.x mod4, enough to check all degree<=2 coefficients.
   need(all((x.bit_count()-1-2*((h>>j)&1))%4==0 for j,x in enumerate(cols)),'old fullGaussian phase weight congruence')
   need(all(not dot(cols[i],cols[j])for i in range(n)for j in range(i)),'old binary orthogonal')
   B=[(1<<j)^(1 if j==0 else 0)^(v if v>>j&1 else 0)for j in range(n)]
   need(rank(B)==n-2,'old gauge same rank n-2')
   if L==1:
    left=[('C',1<<j,1)for j in range(1,n)]+[('M',cols,h),('C',1,-1)]
    right=[('M',cols,h),('C',v,1 if eps else -1),('C',1,-1)]+[('C',1<<j,1)for j in range(n)]+[('phase',(-eps)%4)]
    for b in [0,1,345]:need(state(left,n,b)==state(right,n,b),'old gauge sparse absolute phase identity');sparse_count+=1
   old_count+=1
  old_records.append({'stages':L,'n':n,'actual_paths':len(paths),'rank':n-2})
 need(old_count==672 and sparse_count==96,'old fixture coverage')
 return {'status':'PASS_SCOPED_INDEPENDENT_PATH_REVIEW','new_retained_paths':new_count,'actual_owner_coefficient_once_controls':coefficient_not_powered,'old_normalizer_gauge_paths':old_count,'old_sparse_absolute_phase_columns':sparse_count,'old_sign_values':sorted(eps_seen),'old_records':old_records,'review':'Generic proof valid for real signed linear orthogonal full-Gaussian-centralizing normalizers. r=n-2=d-1 remains permitted, not constructively decoded; single-cohort fixed finite expanded-monomial adapters cannot produce r>d-1 at all widths. Mixed cohorts, paid Gaussian adapters, overlapping stages, arbitrary algorithms outside scope.','sha256':{p:hashlib.sha256((package/p).read_bytes()).hexdigest()for p in ['TERMINAL-BOUND.md','terminal_bound.py','TERMINAL-RESULT.json','inputs/NORMALIZERS.json','inputs/clifford_exact.py']},'paths_canonical_sha256':hashlib.sha256((json.dumps(actual,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--write',action='store_true');args=ap.parse_args();r=calculate(args.package);here=Path(__file__).resolve().parent
 if args.write:(here/'TERMINAL-INDEPENDENT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 else:need(r==json.loads((here/'TERMINAL-INDEPENDENT.json').read_bytes()),'readonly independent receipt')
 print(json.dumps(r,sort_keys=True))
