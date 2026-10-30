"""Full120 E8 projective roots: exact Weyl cube orbit and exact cover.
Apache-2.0; retained P112/E8 lineage, substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,deque
from hashlib import sha256
from itertools import product
import argparse,json,time
HERE=Path(__file__).resolve().parent
PIN='ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'
NEW_Q=[7,25,42,52,76,82,97,127]
def need(a,b):
 if not a:raise ValueError(b)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def binarydot(a,b):return(a&b).bit_count()&1
def oriented(r):
 r=tuple(r)
 return tuple(-x for x in r)if next(x for x in r if x)<0 else r
def basis(rows):
 p={}
 for x in rows:
  for j in sorted(p,reverse=True):
   if x>>j&1:x^=p[j]
  if x:p[x.bit_length()-1]=x
 return tuple(p[j]for j in sorted(p,reverse=True))
def calculate():
 start=time.monotonic();raw=(HERE/'inputs/NORMALIZERS112.json').read_bytes();need(sha256(raw).hexdigest()==PIN,'actual112 input pin');d=json.loads(raw)
 M=[tuple(r)for r in zip(*d['mode_columns'])]+[tuple(2*int(i==j)for j in range(8))for i in range(8)]
 q=[p['q']for p in d['ports']]+NEW_Q;roots={oriented(r):i for i,r in enumerate(M)}
 need(len(M)==len(q)==len(roots)==len(set(q))==120,'full120 roots and binarylabels distinct')
 need(all(dot(r,r)==4 for r in M)and all(binarydot(x,x)==1 for x in q),'norms')
 need(all(sum(M[k][i]*M[k][j]for k in range(120))==60*int(i==j)for i,j in product(range(8),repeat=2)),'full real mode Gram60I')
 pairtypes=Counter()
 for i,j in product(range(120),repeat=2):
  rdot=dot(M[i],M[j]);qd=binarydot(q[i],q[j]);pairtypes[rdot,qd,i==j]+=1
  need((not qd)==(i!=j and rdot!=0),'full A exact nonzero support iff q orthogonal')
 # Every projective Weyl reflection is an actual full120 permutation.
 perms=[]
 for r in M:
  perm=[]
  for s in M:
   a=dot(s,r);need(a%2==0,'integral E8 reflection coefficient');t=oriented(tuple(x-a//2*y for x,y in zip(s,r)));need(t in roots,'actual full E8 reflection closes');perm.append(roots[t])
  need(sorted(perm)==list(range(120))and all(perm[perm[j]]==j for j in range(120)),'actual involutory root permutation');perms.append(tuple(perm))
 initial={}
 for i,row in enumerate(M[:112]):initial.setdefault(tuple(j for j,x in enumerate(row)if x),[]).append(i)
 seeds=[tuple(ps)for _,ps in sorted(initial.items())];need(len(seeds)==14 and all(len(s)==8 for s in seeds),'actual14 original cubes')
 # The orbit under all projective root reflections, not a root-support guess.
 seen=set(seeds);todo=list(seeds);parents={s:None for s in seeds};pos=0
 while pos<len(todo):
  cube=todo[pos];pos+=1
  for ri,p in enumerate(perms):
   nxt=tuple(sorted(p[i]for i in cube))
   if nxt not in seen:seen.add(nxt);todo.append(nxt);parents[nxt]=(cube,ri)
  if pos%1000==0:print('orbit',pos,len(todo),flush=True)
 print('orbit_complete',len(todo),round(time.monotonic()-start,3),flush=True)
 cubes=sorted(seen);records=[]
 for cube in cubes:
  C=[[F(dot(M[i],M[j]),4)for j in cube]for i in cube];K=[[F(i==j)-C[a][b]for b,j in enumerate(cube)]for a,i in enumerate(cube)]
  need(all(sum(C[i][j]*C[j][k]for j in range(8))==2*C[i][k]for i,k in product(range(8),repeat=2)),'orbitcube C square2C')
  need(all(K[i][i]==0 and sum(bool(z)for z in K[i])==4 and all(z in [0,F(1,2),F(-1,2)]for z in K[i])for i in range(8)),'actual K half4 support')
  # Bipartition the actual nonzero K graph; no inherited signparity labels.
  colors={0:0};queue=[0]
  for i in queue:
   for j in range(8):
    if not K[i][j]:continue
    if j not in colors:colors[j]=1-colors[i];queue.append(j)
    else:need(colors[j]!=colors[i],'actual cube graph bipartite')
  need(len(colors)==8,'actual K graph connected');sides=[[cube[i]for i in range(8)if colors[i]==p]for p in [0,1]]
  bs=[basis(q[i]for i in side)for side in sides]
  good=len(sides[0])==len(sides[1])==4 and len(bs[0])==len(bs[1])==3 and all(not binarydot(a,b)for a in bs[0]for b in bs[1])
  records.append({'ports':cube,'source_parity_classes':sides,'binary_span_bases':bs,'native_geometry_good':good})
 good=[i for i,r in enumerate(records)if r['native_geometry_good']]
 need(len(good)>0,'actual nativegood cube candidates')
 # Algorithm X with smallest uncovered column, deterministic exact cover.
 masks={i:sum(1<<p for p in records[i]['ports'])for i in good};byport=[[i for i in good if masks[i]>>p&1]for p in range(120)];ALL=(1<<120)-1;nodes=[0]
 def search(used,chosen):
  nodes[0]+=1
  if used==ALL:return chosen
  best=None
  missing=ALL^used
  while missing:
   b=missing&-missing;missing-=b;p=b.bit_length()-1
   options=[i for i in byport[p]if not masks[i]&used]
   if not options:return None
   if best is None or len(options)<len(best):best=options
   if len(best)==1:break
  for i in best:
   out=search(used|masks[i],chosen+[i])
   if out is not None:return out
  return None
 cover=search(0,[])
 need(cover is not None and len(cover)==15,'actual15-cube exact cover exists')
 need(sorted(p for ci in cover for p in records[ci]['ports'])==list(range(120)),'cover every actual root once')
 coverrecords=[]
 for ci in cover:
  rec=dict(records[ci]);s=tuple(rec['ports']);route=[]
  while parents[s]is not None:
   prev,ri=parents[s];route.append(ri);s=prev
  rec['original_seed_cube']=s;rec['weyl_reflection_route']=list(reversed(route));coverrecords.append(rec)
 payload={'schema':'full120-E8-Weyl-cube-native-cover/v1','status':'PASS_FULL120_CLOSED_E8_15_NATIVE_CUBE_EXACT_COVER','source_pin':PIN,'root_M120x8':M,'q120':q,'new_axis_roots_q':NEW_Q,'M_transpose_M':'60I8','A':'I-MM^T/4','A_spectrum':{'1':112,'-14':8},'A_inverse':'(A+13I)/14','reflection_permutations':perms,'initial14_cubes':seeds,'all_orbit_cube_ports':cubes,'native_geometry_good_cubes':len(good),'orbit_size':len(cubes),'cover15':coverrecords,'exact_cover_search_nodes':nodes[0],'base_native_paid_profile':{'2':120,'3':120,'5':120,'6':120},'base_K':'block_diag(I-C_cube), each K^2=I and K M=-M','global_C_eigenvalue':15,'odd3':{'ports':120**3,'ambient25':25,'C_rank':3*8**2*112+8**3,'C_rank_per_owner':str(F(3*8**2*112+8**3,120**3)),'C_spectrum':{'225/2':3*8**2*112,'-1350':8**3},'new_kappa':False},'scope':'Actual full120 E8 roots, all Weyl-reflection closure and cube orbit, exact15-cube partition, actual q parity-class rank3/orthogonality. Native paid ranks follow the retained generic source/read canonical-frame construction; phase-complete full120 normalized words, terminal decoder and whole caller admission remain separate.','new_kappa':False}
 return payload
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();d=calculate();p=HERE/'COVER.json'
 if a.write:p.write_bytes(canon(d))
 else:need(json.loads(p.read_bytes())==json.loads(canon(d)),'read-only exactcover receipt')
 print(json.dumps({k:d[k]for k in ['status','orbit_size','native_geometry_good_cubes','exact_cover_search_nodes','base_native_paid_profile','odd3','new_kappa']},sort_keys=True))
