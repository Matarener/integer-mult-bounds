# SPDX-License-Identifier: Apache-2.0
# Adapted from PR3605; retained attribution in UPSTREAM-SOURCE-CREDITS.md.
import sys
if not __debug__ or sys.flags.optimize:
 raise RuntimeError("Enabled assertions required before owner replay")
"""Path-adapted copy of the parent independent owner audit.
Original SHA256 1001cb1c8b4ee1f93c23b58b094565ec1b3931eee0ea091a23504696e380be9e.
Filesystem/source authentication and output paths adapted; mathematical predicates retained.
"""
"""Independent vectorized audit of the literal staged-pair owner journal.

No optimizer, producer, inherited owner checker or reconstructor is imported.
Uses the source execution template and the actual checked native frame tables.
"""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,os,sys
import numpy as np
R=Path(__file__).resolve().parent
if not __debug__:raise SystemExit('unoptimized Python required')
for _key in ('OWNER_SOURCE_REPO','OWNER_LITERAL_DIR','OWNER_NATIVE_DIR','OWNER_AUDIT_OUTPUT'):
 if not os.environ.get(_key):raise SystemExit('missing '+_key)
A=Path(os.environ['OWNER_LITERAL_DIR']).resolve()
NATIVE=Path(os.environ['OWNER_NATIVE_DIR']).resolve()
S=Path(os.environ['OWNER_SOURCE_REPO']).resolve()/'research/rank7-joint-endframes/allocation/vendor'
def need(v,m):
 if not v:raise ValueError(m)

def validate_owner_constraints(d):
 """The five owner rules, shared by full-journal validation and corrupt fixtures."""
 need(np.array_equal(d['times'],np.repeat(np.arange(d['calls']),d['helpers'])) and np.array_equal(d['helpers_by_row'],np.tile(np.arange(d['helpers']),d['calls'])),'complete literal ordered helper identities')
 need(np.all((d['lower']<d['window_times'])&(d['window_times']<=d['upper'])),'strict/closed actual source windows')
 keys=np.sort(d['family_keys']);need(np.all(keys[1:]!=keys[:-1]),'same-call physical family uniqueness')
 need(np.array_equal(d['offsets'],d['expected_offsets']),'every chronological pending mask is a compact prefix')
 need(dict(d['histogram'])==d['profile'] and sum(r*n for r,n in d['histogram'].items())==d['mass'],'independent complete histogram')
def owner_control_tests():
 from copy import deepcopy
 good=dict(times=np.array([0,0]),helpers_by_row=np.array([0,1]),calls=1,helpers=2,window_times=np.array([0,0]),lower=np.array([-1,-1]),upper=np.array([0,0]),family_keys=np.array([0,1]),offsets=np.array([0,0]),expected_offsets=np.array([0,0]),histogram={1:2},profile={1:2},mass=2)
 validate_owner_constraints(good)
 mutations=[('duplicate helper','helpers_by_row',np.array([0,0]),'complete literal ordered helper identities'),('strict lower endpoint used as available','window_times',np.array([-1,0]),'strict/closed actual source windows'),('same-call family reused','family_keys',np.array([0,0]),'same-call physical family uniqueness'),('unpaid chronological hole','offsets',np.array([1,0]),'every chronological pending mask is a compact prefix'),('one unpaid rank1 child','profile',{1:3},'independent complete histogram')]
 controls=[]
 for name,key,value,rule in mutations:
  bad=deepcopy(good);bad[key]=value
  try:validate_owner_constraints(bad)
  except ValueError as exc:need(str(exc)==rule,'wrong control rejection '+name)
  else:raise ValueError('control accepted '+name)
  controls.append(name)
 return controls

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def rank(v):
 piv={}
 for q in v:
  while q:
   h=q.bit_length()
   if h in piv:q^=piv[h]
   else:piv[h]=q;break
 return len(piv)
for rel,digest in read(R/'ARTIFACTS.json').items():
 f=R/rel;need(f.is_file() and not f.is_symlink() and sha(f)==digest,'frozen audit artifact '+rel)
paths=[A/n for n in ('FILL.json.gz','ORDER.json','DISPATCH.json','PROFILE.json')]+[S/'PLAN.json.gz',S/'TEMPLATE.json.gz']
paths += [NATIVE/f'checked-{p}/CANONICAL-WORD.json.gz' for p in ('base','extra')]
source_pins=read(R/'SOURCE-PINS.json')
repo=Path(os.environ['OWNER_SOURCE_REPO']).resolve()
for rel,digest in source_pins['repo_files'].items():need(sha(repo/rel)==digest,'retained source pin '+rel)
for tag in ('base','extra'):
 payload=gzip.decompress((NATIVE/f'checked-{tag}/CANONICAL-WORD.json.gz').read_bytes())
 need(hashlib.sha256(payload).hexdigest()==source_pins['native_canonical'][tag]['canonical_payload_sha256'],'actual native canonical payload pin')
pins={str(p):sha(p) for p in paths}
expected=read(R/'EXPECTED.json');need(hashlib.sha256(gzip.decompress(paths[0].read_bytes())).hexdigest()==expected['payload_sha256'],'freshT488payload')
baseorder=read(R/'ORDER37.json')+[[s,r+37]for s,r in read(R/'T8-ORDER.json')]+[[s,r+45]for s,r in read(R/'T16-ORDER.json')]
need(read(paths[1])==[[s,r+61*cp]for s,r in baseorder for cp in range(8)],'exactmixedsourceclock')
basedispatch={(s,r):p for s,r,p in read(R/'DISPATCH37.json')};basedispatch.update({(s,r+37):p for s,r,p in read(R/'T8-DISPATCH.json')});basedispatch.update({(s,r+45):p for s,r,p in read(R/'T16-DISPATCH.json')})
need(read(paths[2])==[[s,r+61*cp,basedispatch[s,r]]for s,r in baseorder for cp in range(8)],'exactsourceproviderdispatch')
order=read(paths[1]);dispatch=read(paths[2]);profile={int(k):v for k,v in read(paths[3]).items()};plan=read(paths[4]);template=read(paths[5])
T=488;N=9*T
need(len(order)==N and len(set(map(tuple,order)))==N,'call coverage')
clock={tuple(call):t for t,call in enumerate(order)}
need(set(clock)=={(s,r) for s in range(9) for r in range(T)},'exact source calls')
need(all([clock[s,r] for s in range(9)]==sorted(clock[s,r] for s in range(9)) for r in range(T)),'per-replica order')
D={(s,r):p for s,r,p in dispatch};need(len(dispatch)==N and set(D)==set(clock),'dispatch coverage')
need(Counter(D.values())=={'extra': 1680, 'gauge44': 2712},'provider count')
# Reconstruct source windows per replica from the actual source event sequence.
children={x['child']:x['rank'] for x in template['idle_children']};K=max(children)+1
cap=np.zeros((T,K),dtype=np.int64);lo=np.full((T,K),N,dtype=np.int64);hi=np.full((T,K),-2,dtype=np.int64)
local_pair={x['stage']:x['pair'] for x in template['recipe'] if x['kind']=='local'}
for r in range(T):
 touched={};t=None
 for ev in template['execution_schedule']:
  kind=ev['kind']
  if kind in ('bank_padding_cover_sweep','translate_every_live_family'):continue
  if kind=='local_cover_sweep':
   t=clock[ev['stage'],r];touched[local_pair[ev['stage']]]=t
  elif kind=='bridge':
   need(t is not None,'bridge source');touched[ev['src']]=t;touched[ev['dst']]=t
  elif kind=='idle_cover_sweep':
   need(t is not None,'idle source')
   for c in ev['child_indices']:
    if c in children:
     need(cap[r,c]==0,'unique source child');cap[r,c]=children[c];lo[r,c]=touched.get(ev['pair'],-1);hi[r,c]=t
  else:need(kind in ('terminal_Y_translations','terminal'),'known source event')
need(np.all(cap[:,list(children)]>0),'all source windows')
fam=np.full(K,-1,np.int64)
for c in children:fam[c]=2*plan['pairs'][str(c)]+plan['sides'][str(c)]
widths={};L=None
for tag,pid in [('base','gauge44'),('extra','extra')]:
 w=read(NATIVE/f'checked-{tag}/CANONICAL-WORD.json.gz')
 need(w['R']==408 and len(w['zero_buffers'])==91,'native helper stock')
 widths[pid]=np.array([rank(w['frames'][w['final'][224+h]])-rank(w['frames'][w['start'][224+h]]) for h in range(408)],dtype=np.int64)
 need(Counter(widths[pid])=={4:26,5:2,6:18,7:52,8:97,9:213},'actual native widths')
 loc={int(k):v for k,v in w['local_profile'].items()}
 need(L is None or L==loc,'common actual native bill');L=loc
need(L=={1:2439,2:726,3:224,4:102,5:20,8:8},'new local bill')
bycall=np.stack([widths[D[tuple(call)]] for call in order])
j=read(A/'FILL.json.gz');need(j['columns']==['time','helper','owner_replica','child','port','offset'] and j['dispatch_overrides']==[],'journal schema')
need(all(len(row)==6 and all(type(v) is int for v in row) for row in j['rows']),'literal integer roles')
rows=np.array(j['rows'],dtype=np.int64);del j
need(rows.shape==(N*408,6),'literal role shape')
need(np.all((rows[:,0]>=0)&(rows[:,0]<N)&(rows[:,1]>=0)&(rows[:,1]<408)),'safe time/helper indexing bounds')
t,h,o,c,p,z=rows.T
need(np.all((o>=0)&(o<T)&(c>=0)&(c<K)&(p>=0)&(p<112)),'owner bounds')
need(np.all(cap[o,c]>0),'declared source child')
# The shared validator below checks the actual source windows.
family=o*896+fam[c]*112+p
key=t*(896*T)+family
# The shared validator below checks physical family keys.
w=bycall[t,h];need(np.all((z>=0)&(z+w<=cap[o,c])),'actual widths and capacity')
binid=(o*K+c)*112+p
idx=np.lexsort((t,binid));bins=binid[idx];ws=w[idx];starts=np.r_[True,bins[1:]!=bins[:-1]]
cs=np.cumsum(ws,dtype=np.int64)-ws;baseline=np.maximum.accumulate(np.where(starts,cs,0));expected=cs-baseline
# The shared validator below checks every chronological prefix.
used=np.zeros(T*K*112,np.int64);np.add.at(used,binid,w)
allcap=np.repeat(cap.reshape(-1),112);valid=allcap>0
need(np.all(used[~valid]==0) and np.all(used<=allcap),'full used-bin mass')
idle=Counter(map(int,(allcap-used)[valid]));idle.pop(0,None)
H=Counter({r:n*N for r,n in L.items()});H.update(idle)
validate_owner_constraints(dict(times=t,helpers_by_row=h,calls=N,helpers=408,window_times=t,lower=lo[o,c],upper=hi[o,c],family_keys=key,offsets=z[idx],expected_offsets=expected,histogram=H,profile=profile,mass=65088*T))
controls=owner_control_tests()
need(all(sha(Path(p))==v for p,v in pins.items()),'input drift')
result={'status':'PASS_INDEPENDENT_LITERAL_OWNER_WINDOWS_FAMILIES_PREFIXES_AND_INVOICE','replicas':T,'calls':N,'roles':len(rows),'physical':896*T+509,'idle':dict(sorted(idle.items())),'profile':dict(sorted(H.items())),'input_sha256':pins,'script_sha256':sha(Path(__file__)),'controls':controls,'scope':'Independent finite vectorized audit; no producer, solver, retained owner checker or reconstructor imports. Actual native frames are authenticated input data; their separate full operator proofs are required.'}
Path(os.environ['OWNER_AUDIT_OUTPUT']).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:result[k] for k in ('status','roles','idle','profile')},indent=2))
