"""Regenerate the464-deletion word from immutable selected589. Apache-2.0."""
from pathlib import Path
import copy,gzip,hashlib,io,json,sys
P=Path(__file__).resolve().parents[1];out=Path(sys.argv[1]).resolve()
base=P/'data/SELECTED589.json.gz'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
w=json.loads(gzip.decompress(base.read_bytes()));v=w['v'];removed=464
assert w['R']==439 and w['A'][224]==[56,464,[54]]
def role(r):
 assert r!=removed
 return r-int(r>removed)
def gates(gs):return [[f,role(d),[role(s) for s in ss]] for f,d,ss in gs]
node=json.loads((P/'data/NEW-NODE.json').read_bytes())
t=copy.deepcopy(w);t['R']=438
t['A']=gates([z for j,z in enumerate(w['A'][:1986]) if j!=224])+node+gates(w['A'][1989:])
t['B']=gates(w['B']);t['ret']=[role(r) for r in w['ret']]
for key in ('start','final'):t[key]=[f for r,f in enumerate(w[key]) if r!=removed]
t['C']=[[1,d,ss[:]] for f,d,ss in reversed(t['A']+t['B']) if not v<=d<2*v]
# Full raw dirty response, not a SOURCE-only projection.
a=[1<<i for i in range(2*v+t['R'])]
def run(gs):
 for f,d,ss in gs:
  for s in ss:a[d]^=a[s]
run(t['A']);capture=[a[r] for r in t['ret']]
for target,indices in enumerate(t['scatter']):
 for j in indices:a[v+target]^=capture[j]
run(t['B']);d0=[]
for target in range(v):
 assert a[v+target]&((1<<(2*v))-1)==(1<<target)^(1<<(v+target))
 ss=[j for j in range(2*v,len(a)) if a[v+target]>>j&1]
 if ss:d0.append([0,v+target,ss])
t['D']=d0;t['stats']['extra_carriers']=9
raw=json.dumps(t,sort_keys=True,separators=(',',':')).encode()
expected=json.loads((P/'EXPECTED.json').read_bytes())
assert hashlib.sha256(raw).hexdigest()==expected['word_content_sha256']
committed=json.loads(gzip.decompress((P/'data/r0028/FINAL-R438-WORD.json.gz').read_bytes()))
assert committed==t
b=io.BytesIO()
with gzip.GzipFile(filename='',fileobj=b,mode='wb',mtime=0) as f:f.write(raw)
(out/'WORD.json.gz').write_bytes(b.getvalue())
print(json.dumps({'status':'REGENERATED_ALL_CANONICAL_WORD_FIELDS','canonical_sha256':hashlib.sha256(raw).hexdigest(),
 'generated_gzip_sha256':hashlib.sha256(b.getvalue()).hexdigest(),'gzip_container_is_not_mathematical_equality_test':True}))
