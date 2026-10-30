"""Independent Hamming lattice and all nine punctured capture hyperplanes."""
from pathlib import Path
from itertools import combinations,product
import ast,json,gzip,hashlib,shutil
import sys
H=Path(sys.argv[1]).resolve();PKG=Path(__file__).resolve().parents[1];I=PKG/'data'
p=PKG/'vendor/e8.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='721d859a6517d665ca84d03ef89668da3aae7433ffb0ee47faf37f2aeb85450e'
target=p
tree=ast.parse(target.read_text(encoding='utf8'))
f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_roots_hamming')
assignment=next(n for n in f.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='g' for t in n.targets))
g=ast.literal_eval(assignment.value);masks=[sum(x<<j for j,x in enumerate(row)) for row in g]
code=[]
for a in product((0,1),repeat=4):
 mask=0
 for x,row in zip(a,masks):
  if x:mask^=row
 code.append(mask)
assert len(set(code))==16
assert all(x.bit_count()%4==0 for x in code)
assert all((x&y).bit_count()%2==0 for x in code for y in code)
full=[tuple(2*int(i==j) for i in range(8)) for j in range(8)]
for mask in code:
 if mask.bit_count()!=4:continue
 pos=[j for j in range(8) if mask>>j&1]
 for tail in product((1,-1),repeat=3):
  v=[0]*8
  for j,s in zip(pos,(1,)+tail):v[j]=s
  full.append(tuple(v))
assert len(full)==len(set(full))==120
independent={tuple(2*int(i==j) for i in range(8)) for j in range(8)}
for pos in combinations(range(8),4):
 if pos[0]^pos[1]^pos[2]^pos[3]:continue
 for tail in product((1,-1),repeat=3):
  v=[0]*8
  for j,s in zip(pos,(1,)+tail):v[j]=s
  independent.add(tuple(v))
assert independent==set(full)
w=json.loads(gzip.decompress((I/'r0028/FINAL-R438-WORD.json.gz').read_bytes()))
assert [list(full[p]) for p in w['ports_geom']]==w['lines']
result=json.loads((H/'RESULT.json').read_bytes());mapping=[];rows=[]
for z in result['ledger']['COPY']:
 fr=set(w['frames'][z['frame']]);matches=[]
 for p in w['punctured']:
  normal=full[p]
  expected={i for i,ray in enumerate(w['lines']) if sum(a*b for a,b in zip(normal,ray))==0}
  if expected==fr:matches.append(p)
 assert len(matches)==1
 mapping.append({'capture':z['capture'],'frame':z['frame'],'punctured_full_SOURCE':matches[0]})
 rows.append(int(z['SOURCE_row_hex'],16))
assert {z['punctured_full_SOURCE'] for z in mapping}==set(w['punctured'])
rank=0;work=rows[:]
for col in range(111):
 j=next((j for j in range(rank,9) if work[j]>>col&1),None)
 if j is None:continue
 work[rank],work[j]=work[j],work[rank]
 for j in range(rank+1,9):
  if work[j]>>col&1:work[j]^=work[rank]
 rank+=1
 if rank==9:break
assert rank==9
out={'status':'PASS_INDEPENDENT_HAMMING_LATTICE_FULL120_AND_NINE_CAPTURE_HYPERPLANES',
 'source_sha256':sha(target),'full_catalog_payload_sha256':hashlib.sha256(json.dumps(full,separators=(',',':')).encode()).hexdigest(),
 'Hamming_code_dimension':4,'Hamming_doubly_even_and_self_orthogonal':True,'roots':240,'rays':120,'live111_exact_order':True,
 'lattice_proof':'L={z in Z^8:z mod2 in H}, index16. In <x,y>/2 metric covolume16/(sqrt2)^8=1; binary self-orthogonality gives integral pairings and doubly-evenness gives even norms. Raw norm4 vectors are exactly ±2e_i and four ±1 entries on the fourteen weight4 code supports. No numpy closure or producer executed.',
 'capture_SOURCE_row_rank':rank,'capture_punctured_normal_mapping':mapping,'native_supplier_admitted':False}
with (H/'CATALOG-RESULT.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
print(out['status'])
