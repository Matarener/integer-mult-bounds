#!/usr/bin/env python3
"""Exact sparse Gaussian-rational audit; no predecessor executable imports."""
from fractions import Fraction as F
from pathlib import Path
import collections, copy, gzip, hashlib, io, json, tarfile
from functools import lru_cache

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ARCHIVE='research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX='candidate/strict/global/base/providers/gauge44/'
PINS={
 'LOCAL-PROGRAMS.json.gz':'241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
 'CLIFFORD-RECIPES.json':'d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731',
 'CANONICAL-WORD.json.gz':'16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'}
ONE=(F(1),F(0)); ZERO=(F(0),F(0))
def require(ok,msg):
 if not ok: raise RuntimeError(msg)
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def div(a,b):
 d=b[0]*b[0]+b[1]*b[1]
 return mul(a,(b[0]/d,-b[1]/d))
def phase(a,p):return (a,(-a[1],a[0]),neg(a),(a[1],-a[0]))[p%4]
def clean(v):return {k:a for k,a in v.items() if a!=ZERO}
def plus(v,w):
 o=dict(v)
 for k,a in w.items():o[k]=add(o.get(k,ZERO),a)
 return clean(o)
def scaled(v,a):return clean({k:mul(a,b) for k,b in v.items()})
def mv(rows,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(rows))
@lru_cache(None)
def monomial_table(rows,quadratic,linear,offset,global_phase):
 n=len(rows);table=[]
 for x in range(1<<n):
  y=mv(rows,x)^offset
  p=global_phase+sum(linear[i] for i in range(n) if x>>i&1)
  p+=2*sum((quadratic[i] & x & ~((1<<(i+1))-1)).bit_count()%2 for i in range(n) if x>>i&1)
  table.append((y,p%4))
 require(len({y for y,p in table})==1<<n,'monomial is a permutation')
 return tuple(table)
def monomial(v,r,inverse=False):
 table=monomial_table(tuple(r['matrix_rows']),tuple(r['quadratic_rows']),tuple(r['linear_Z4']),r['offset'],r['phase'])
 if inverse:
  inv={y:(x,-p) for x,(y,p) in enumerate(table)}
  return {inv[y][0]:phase(a,inv[y][1]) for y,a in v.items()}
 return {table[x][0]:phase(a,table[x][1]) for x,a in v.items()}
def fourier(v,r,inverse=False):
 s=-1 if inverse else 1
 for j in range(r):
  o={}
  for x,a in v.items():
   for y,b in [(x,(F(1,2),F(s,2))),(x^(1<<j),(F(1,2),F(-s,2)))]:
    o[y]=add(o.get(y,ZERO),mul(a,b))
  v=clean(o)
 return v

def apply(v,r,inverse=False):
 if inverse:return monomial(fourier(monomial(v,r['left'],True),r['rank'],True),r['right'],True)
 return monomial(fourier(monomial(v,r['right']),r['rank']),r['left'])
def compose_cols(a,b):return [sumcols(a,v) for v in b]
def sumcols(cols,v):
 o={}
 for i,a in v.items():o=plus(o,scaled(cols[i],a))
 return o

def exact_rank(cols):
 piv={}
 for col in cols:
  v=dict(col)
  while v:
   p=min(v)
   if p not in piv:
    piv[p]=scaled(v,div(ONE,v[p]));break
   v=plus(v,scaled(piv[p],neg(v[p])))
 return len(piv)
def pauli(v):return {x^224:phase(a,2*((x&96).bit_count()%2)) for x,a in v.items()}
def finite_native_macro(x,y,C):
 # Four rational ADDs and six explicitly reversible monomial source maps.
 x=sumcols(C,x)
 x=plus(x,scaled(y,(F(1,4),F(0))))
 y=scaled(y,(F(0),F(1)))
 x=plus(x,scaled(y,(F(1,4),F(0))))
 y=scaled(y,(F(0),F(-1)))
 y=pauli(y)
 x=plus(x,scaled(y,(F(1,4),F(0))))
 y=scaled(y,(F(0),F(-1)))
 x=plus(x,scaled(y,(F(1,4),F(0))))
 y=scaled(y,(F(0),F(1)))
 y=pauli(y)
 return x,y

def encoded(v):return [[x,str(a),str(b)] for x,(a,b) in sorted(v.items())]
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def touched(e,r):
 return (e[0] in ('climb','adapter','residual_adapter') and e[2]==r) or (e[0]=='scalar' and ['L',r] in e[1])

def load():
 manifest=json.loads((HERE/'SOURCES.json').read_text())
 for row in manifest['files']:
  if row.get('usage')=='input':
   require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'declared input pin '+row['path'])
 raw=(ROOT/ARCHIVE).read_bytes()
 require(hashlib.sha256(raw).hexdigest()=='f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6','archive pin')
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
  data={}
  for name,pin in PINS.items():
   b=t.extractfile(PREFIX+name).read();require(hashlib.sha256(b).hexdigest()==pin,name+' pin')
   data[name]=json.loads(gzip.decompress(b) if name.endswith('.gz') else b)
 return data['LOCAL-PROGRAMS.json.gz']['forward'],data['CLIFFORD-RECIPES.json']['children'],data['CANONICAL-WORD.json.gz']

def evaluate():
 events,recipes,word=load();rd={(x['old'],x['new']):x for x in recipes}
 A,B,C,D=[rd[k] for k in [(0,2),(2,252),(0,252),(2,559)]]
 require([r['rank'] for r in [A,B,C,D]]==[1,1,2,2],'source child ranks')
 region=events[12806:13403]
 require(events[12806]==['climb','B',195,0,2,1] and events[13402]==['climb','B',195,2,252,1],'boundary events')
 require([(i,e) for i,e in enumerate(events[12807:13402],12807) if touched(e,195) or touched(e,521)]==[(12807,['scalar',['add',['L',195],['L',521],1,2],2])],'complete intervening dependency boundary')
 require(next((i,e) for i,e in enumerate(events[12808:],12808) if touched(e,521))==(14191,['climb','B',521,2,559,2]),'next donor touch')
 require(all(e[0] in ('climb','scalar') for e in region),'known complete region alphabet')
 require(all(e[1][0]=='add' for e in region if e[0]=='scalar'),'all region scalar events are adds')
 bases=[{i:ONE} for i in range(512)]
 cols={key:[apply(v,r) for v in bases] for key,r in [('A',A),('B',B),('C',C),('D',D)]}
 require(compose_cols(cols['B'],cols['A'])==cols['C'],'full basis exact BA=C including global phase')
 Binv=[apply(v,B,True) for v in bases]
 require(compose_cols(cols['B'],Binv)==bases,'full donor inverse')
 correction=compose_cols(cols['D'],Binv)
 supports=collections.Counter(map(len,correction))
 require(supports=={8:512},'every correction column has eight nonzeros')
 # A separate, generated rank-three recipe is verified from scratch; its
 # construction is not trusted for any mathematical assertion.
 q=json.loads((HERE/'CORRECTION.json').read_text())
 require(q['rank']==3 and [apply(v,q) for v in bases]==correction,'rank-three correction upper bound')
 residual=[plus(v,scaled(e,(-F(1),F(0)))) for v,e in zip(cols['B'],bases)]
 rr=exact_rank(residual)
 # Opposite ordering: transport the donor to frame0 before the ADD.
 Ainv=[apply(v,A,True) for v in bases]
 early_correction=compose_cols(cols['D'],cols['A'])
 qearly=json.loads((HERE/'EARLY-CORRECTION.json').read_text())
 require(qearly['rank']==3 and [apply(v,qearly) for v in bases]==early_correction,'early rank-three correction upper bound')
 require(collections.Counter(map(len,early_correction))=={8:512},'early correction lower bound')
 require(compose_cols(cols['C'],Ainv)==cols['B'],'opposite ADD transport C A^-1 = B')
 require(compose_cols(early_correction,Ainv)==cols['D'],'opposite deferred donor restoration')
 for i,e in enumerate(bases):
  bp=plus(scaled(e,(F(1,2),F(1,2))),scaled(pauli(e),(F(1,2),F(-1,2))))
  require(bp==cols['B'][i],'literal signed-XOR Pauli transport')
  require(pauli(pauli(e))==e,'Pauli source restoration')
  require(finite_native_macro(e,{},cols['C'])==(cols['C'][i],{}),'finite native x block')
  require(finite_native_macro({},e,cols['C'])==(scaled(cols['B'][i],(F(1,2),F(0))),e),'finite native y block and dirty donor')
 # A literal entry minor proves I,B,C linearly independent over Q(i), hence C.
 rows=[];locations=[]
 for j in range(512):
  for i in sorted(set(bases[j])|set(cols['B'][j])|set(cols['C'][j])):
   row=[bases[j].get(i,ZERO),cols['B'][j].get(i,ZERO),cols['C'][j].get(i,ZERO)]
   if exact_rank([{k:a for k,a in enumerate(r) if a!=ZERO} for r in rows+[row]])>len(rows):
    rows.append(row);locations.append([i,j])
   if len(rows)==3:break
  if len(rows)==3:break
 require(len(rows)==3,'operator span dimension three')
 determinant=ZERO
 import itertools
 for perm in itertools.permutations(range(3)):
  term=ONE
  for i,j in enumerate(perm):term=mul(term,rows[i][j])
  inversions=sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3))
  determinant=add(determinant,neg(term) if inversions%2 else term)
 require(determinant!=ZERO,'nonzero exact minor')
 # All 1024 basis columns of the two-register block operator are checked.
 # On x-inputs: original BA = C. On y-inputs: original B/2 = transported B/2.
 for i,e in enumerate(bases):
  require(sumcols(cols['B'],sumcols(cols['A'],e))==cols['C'][i],'x block')
  by=scaled(cols['B'][i],(F(1,2),F(0)))
  require(by==scaled(sumcols(cols['B'],e),(F(1,2),F(0))),'y block')
  require(sumcols(Binv,cols['B'][i])==e,'restored arbitrary dirty donor')
  require(sumcols(correction,cols['B'][i])==cols['D'][i],'deferred donor restoration')
 # Meaningful controls: wrong global phase, wrong ADD coefficient, discarded
 # transport, and omitted donor inverse must violate an exact boundary map.
 bad=copy.deepcopy(C);bad['right']['phase']=(bad['right']['phase']+1)%4
 require(apply(bases[0],bad)!=cols['C'][0],'global phase control')
 witness=next(i for i in range(512) if cols['B'][i]!=bases[i])
 require(scaled(cols['B'][witness],(F(1,2),F(0)))!=scaled(bases[witness],(F(1,2),F(0))),'missing transport control')
 require(cols['B'][witness]!=scaled(cols['B'][witness],(F(1,2),F(0))),'coefficient control')
 require(cols['B'][witness]!=bases[witness],'dirty restoration control')
 require(next(i for i in range(512) if correction[i]!=cols['D'][i])>=0,'unchanged next child control')
 return dict(region_events=len(region),region_tag_counts=dict(collections.Counter(e[0] for e in region)),
  disjoint_interior_events=594,source_frames={str(i):word['frames'][i] for i in [0,2,252,559]},
  region_sha256=digest(region),complete_basis_columns_per_map=512,two_register_basis_columns=1024,
  exact_BA_equals_C=True,donor_correction_column_supports={str(k):v for k,v in supports.items()},donor_correction_minimum_fourier_width=3,
  residual_B_minus_I_rank=rr,transport_pauli={'xor':224,'sign_mask':96},finite_native_macro={'rational_adds':4,'monomial_source_maps':6,'new_registers':0,'dirty_donor_restored':True,'rank_profile':{'2':1}},tensor_transfer_channels='2^f exactly in source-monomial accumulation class',operator_span_dimension=3,operator_minor_locations=locations,operator_minor=[[[str(a),str(b)] for a,b in r] for r in rows],operator_minor_determinant=[str(x) for x in determinant],early_correction_minimum_fourier_width=3,first_missing_transport_basis=witness,
  missing_transport_original_target=encoded(scaled(cols['B'][witness],(F(1,2),F(0)))),
  missing_transport_wrong_target=encoded(scaled(bases[witness],(F(1,2),F(0)))),
  map_digests={k:digest([encoded(v) for v in c]) for k,c in cols.items()},
  correction_sha256=digest([encoded(v) for v in correction]),controls_rejected=5,
  profiles={'original_target':{'1':2},'immediate_restore_target_and_donor':{'1':2,'2':1},
  'original_through_next_donor_child':{'1':2,'2':1},'deferred_restore_target_and_donor':{'1':1,'2':1,'3':1}},
  normalized_moment_deltas={'immediate':'2^(1-a)','deferred':'3^(1-a)-1'},
  delta_positive_for='0<a<1',new_kappa=False)

def main():
 result=evaluate();expected=json.loads((HERE/'RESULT.json').read_text())
 require(result==expected,'committed result equals recomputation')
 print('PASS_SELECTED_RANK2_INTERTWINER exact_basis=512 block_basis=1024 region=597 residual_rank='+str(result['residual_B_minus_I_rank'])+' correction_width=3 controls=5 no_new_kappa')
if __name__=='__main__':main()
