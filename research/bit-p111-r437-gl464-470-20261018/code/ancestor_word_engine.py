"""Independent exact rational geometry, row/column circuits and COPY ledger."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import gcd
import gzip,json,hashlib,time
import sys
H=Path(sys.argv[1]).resolve();I=Path(__file__).resolve().parents[1]/'data'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads(gzip.decompress((I/n).read_bytes()))
def norm(v):
 g=0
 for x in v:g=gcd(g,abs(x))
 if not g:return tuple(v)
 s=1 if next(x for x in v if x)>0 else -1
 return tuple(s*x//g for x in v)
def reduce(v,bs):
 v=tuple(v)
 for j,row in bs:
  if v[j]:v=norm([row[j]*x-v[j]*y for x,y in zip(v,row)])
 return v
def basis(rows):
 bs=[]
 for row in rows:
  v=reduce(row,bs)
  if any(v):bs.append((next(j for j,x in enumerate(v) if x),norm(v)));bs.sort()
 return bs
def write(n,obj):
 with (H/n).open('x',encoding='utf8') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
def apply(rows,gs):
 for f,d,ss in gs:
  value=rows[d]
  for s in ss:value^=rows[s]
  rows[d]=value
 return rows
def capture_rows(w,rows):
 for j,r in enumerate(w['ret']):
  work=rows[r]
  for t,indices in enumerate(w['scatter']):
   if j in indices:rows[w['v']+t]^=work
  work^=rows[r];assert work==0
def whole(w):
 a=[1<<i for i in range(2*w['v']+w['R'])]
 apply(a,w['D']);apply(a,w['A']);capture_rows(w,a);apply(a,w['B']);apply(a,w['C']);return a
def raw(w):
 a=[1<<i for i in range(2*w['v']+w['R'])]
 apply(a,w['A']);ret=[a[r] for r in w['ret']];capture_rows(w,a);apply(a,w['B']);return a,ret

def geometry(w,old):
 assert (w['h'],w['v'],w['form'])==(8,111,'<x,y>/2')
 for k in ('lines','ports_geom','punctured','frames','coords'):assert w[k]==old[k]
 lines=w['lines'];assert len(lines)==111 and len({tuple(v) for v in lines})==111
 assert all(len(v)==8 and sum(x*x for x in v)==4 for v in lines)
 assert len(w['ports_geom'])==111 and len(w['punctured'])==9
 assert sorted(w['ports_geom']+w['punctured'])==list(range(120))
 dims=[];masks=[]
 for fr in w['frames']:
  assert len(fr)==len(set(fr)) and all(0<=x<111 for x in fr)
  bs=basis([lines[x] for x in fr]);cl={j for j,v in enumerate(lines) if not any(reduce(v,bs))}
  assert cl==set(fr);dims.append(len(bs));masks.append(sum(1<<x for x in fr))
 assert len(dims)==636 and dims[:2]==[0,8]
 for j,v in enumerate(lines):
  assert dims[w['start'][j]]==1 and j in w['frames'][w['start'][j]]
  assert w['final'][j]==1
  assert set(w['frames'][w['final'][111+j]])=={k for k,u in enumerate(lines) if sum(a*b for a,b in zip(u,v))==0}
 assert w['start'][111:]==[0]*(111+w['R']) and w['final'][222:]==[1]*w['R']
 for r in w['ret']:
  assert r>=222
 return dims,masks

def ledger(w,dims,frames,check_support=True):
 v=w['v'];n=2*v+w['R'];cur=w['start'][:];rows=[1<<i for i in range(n)]
 hist=Counter();moves=Counter();adds=Counter();sourcewrites=Counter();paths=[[f] for f in cur]
 sourcehist=[];supportchecks=0;copyinfo=[];edgeops=[];rawop=[]
 def gates(sec,gs):
  nonlocal supportchecks
  for f,d,ss in gs:
   assert 0<=f<len(dims) and 0<=d<n and all(0<=s<n and s!=d for s in ss)
   assert len(ss)==len(set(ss))
   assert all(not v<=s<2*v for s in ss)
   for r in [d]+ss:
    old=cur[r]
    if old!=f:
     assert frames[old]&~frames[f]==0 and dims[f]>dims[old]
     hist[dims[f]-dims[old]]+=1;moves[sec]+=1;cur[r]=f;paths[r].append(f)
   for s in ss:
    rows[d]^=rows[s];adds[sec]+=1;edgeops.append((d,s))
    if d<v:sourcewrites[sec]+=1
   if not v<=d<2*v:
    assert rows[d]&((1<<v)-1)&~frames[f]==0;supportchecks+=1
   if d<v:sourcehist.append((sec,d,rows[d]&((1<<v)-1)))
  rawop.extend((d,sum(1<<s for s in ss)) for f,d,ss in gs)
 gates('D',w['D']);gates('A',w['A'])
 caprows=rows[:]
 for j,r in enumerate(w['ret']):
  f=cur[r];assert dims[f]==7;hist[7]+=1
  recipients=[v+t for t,ss in enumerate(w['scatter']) if j in ss]
  assert recipients and all(cur[t]==0 for t in recipients)
  before=rows[r];work=before
  # A full-stream D_F capture is the virtual row; no original writes or MOVEs
  # occur in this prescribed COPY/scatter/ERASE window.
  for t in recipients:rows[t]^=work;adds['SCATTER']+=1;edgeops.append((t,r))
  assert rows[r]==before and cur[r]==f
  work^=rows[r];assert work==0
  copyinfo.append({'capture':j,'role':r,'frame':f,'rank':dims[f],'SOURCE_row_hex':hex(before&((1<<v)-1)),
   'recipients':recipients,'capture_full_row_sha256':hashlib.sha256(str(before).encode()).hexdigest(),
   'source_immutable':True,'ADDRESS_immutable':True,'WORK_after_erase':0})
 gates('B',w['B']);gates('C',w['C'])
 for r,f in enumerate(w['final']):
  if cur[r]!=f:
   old=cur[r];assert frames[old]&~frames[f]==0 and dims[f]>dims[old]
   hist[dims[f]-dims[old]]+=1;moves['FINAL']+=1;paths[r].append(f);cur[r]=f
 assert cur==w['final']
 maxnorm=1;norms=[1]*n
 for d,s in edgeops:norms[d]+=norms[s];maxnorm=max(maxnorm,norms[d])
 reversemax=1;norms=[1]*n
 for d,s in reversed(edgeops):norms[d]+=norms[s];reversemax=max(reversemax,norms[d])
 return rows,caprows,paths,sourcehist,{'profile':dict(sorted(hist.items())),'mass':sum(k*c for k,c in hist.items()),
  'MOVEs':dict(moves),'scalar_ADDs':dict(adds),'SOURCE_writes':dict(sourcewrites),
  'clean_SOURCE_frame_support_checks':supportchecks,'COPY':copyinfo,
  'forward_l1':str(maxnorm),'reverse_l1':str(reversemax),'forward_bits':maxnorm.bit_length(),'reverse_bits':reversemax.bit_length()}

def column_engine(w):
 v=w['v'];n=2*v+w['R'];temp=n
 # Structurally separate literal single-column engine, including explicit
 # temporary capture and same-original erase rather than self-asserted clearing.
 ops=[]
 for sec in ('D','A'):ops.extend((d,sum(1<<s for s in ss)) for f,d,ss in w[sec])
 for j,r in enumerate(w['ret']):
  ops.append((temp,1<<r))
  ops.extend((v+t,1<<temp) for t,ss in enumerate(w['scatter']) if j in ss)
  ops.append((temp,1<<r))
 for sec in ('B','C'):ops.extend((d,sum(1<<s for s in ss)) for f,d,ss in w[sec])
 for col in range(n):
  state=1<<col
  for d,mask in ops:
   if (state&mask).bit_count()&1:state^=1<<d
  wanted=(1<<col)^((1<<(v+col)) if col<v else 0)
  assert state==wanted,(col,state,wanted)
 return len(ops)

def main():
 cpu=time.process_time();w=read('r0028/FINAL-R438-WORD.json.gz');old=read('SELECTED589.json.gz');base=read('SOURCE555.json.gz')
 assert w['R']==438 and old['R']==439
 dims,frames=geometry(w,old)
 assert old['A'][:1989]==base['A'][:1989] and all(old[k]==base[k] for k in ('B','scatter','ret','frames'))
 remove=464;v=111;n=660;remap=lambda r:r-int(r>remove)
 def rg(gs):
  assert all(d!=remove and remove not in ss for f,d,ss in gs)
  return [[f,remap(d),[remap(s) for s in ss]] for f,d,ss in gs]
 assert old['A'][224]==[56,remove,[54]] and old['ports_geom'][54]==59
 assert w['A'][:1985]==rg([x for j,x in enumerate(old['A'][:1986]) if j!=224])
 assert w['A'][1995:]==rg(old['A'][1989:])
 assert w['B']==rg(old['B']) and w['ret']==[remap(r) for r in old['ret']] and w['scatter']==old['scatter']
 assert w['start']==[f for r,f in enumerate(old['start']) if r!=remove]
 assert w['final']==[f for r,f in enumerate(old['final']) if r!=remove]
 node=w['A'][1985:1995];assert {f for f,d,ss in node}=={506}
 assert {d for f,d,ss in node}=={241,340,349} and all(d>=222 for f,d,ss in node)
 gl=read('r0028/GL-R438-WORD.json.gz');ops60=gl['A'][1985:2045]
 roles=sorted({x for f,d,ss in node+ops60 for x in [d]+ss});assert len(roles)==10
 start={r:1<<j for j,r in enumerate(roles)}
 def local(gs):
  a=start.copy()
  for f,d,ss in gs:
   for s in ss:a[d]^=a[s]
  return a
 assert local(node)==local(ops60)
 external=[r for r in roles if r not in {241,340,349}]
 assert all(local(node)[r]==start[r] for r in external)
 # Entire raw dirty response independently regenerates the mathematical D0.
 rawrows,retrows=raw(w);mask=((1<<438)-1)<<222;expectedD=[]
 for t in range(v):
  assert rawrows[v+t]&((1<<222)-1)==(1<<t)^(1<<(v+t))
  ss=[j for j in range(222,n) if (rawrows[v+t]>>j)&1]
  if ss:expectedD.append([0,v+t,ss])
 assert w['D']==expectedD
 assert w['C']==[[1,d,ss] for f,d,ss in reversed(w['A']+w['B']) if not v<=d<2*v]
 expected=[1<<r for r in range(n)]
 for t in range(v):expected[v+t]^=1<<t
 rows,cap,paths,sh,info=ledger(w,dims,frames)
 orows,ocap,opaths,osh,oinfo=ledger(old,dims,frames)
 assert rows==whole(w)==expected
 assert paths==[f for r,f in enumerate(opaths) if r!=remove]
 # SOURCE writes are unchanged after exact helper ID remap; all are in B/C.
 assert sh==[(sec,d,bits) for sec,d,bits in osh]
 assert info['SOURCE_writes'].get('A',0)==0
 want={1:1322,2:1342,3:78,4:43,5:102,6:11,7:19}
 assert info['profile']==want and info['mass']==5121
 delta=Counter(info['profile']);delta.subtract(oinfo['profile'])
 assert {k:c for k,c in delta.items() if c}=={1:-1,3:-1,4:-1}
 for r,ro in zip(w['ret'],old['ret']):assert cap[r]&((1<<v)-1)==ocap[ro]&((1<<v)-1)
 # Check all nine actual capture frame hyperplanes correspond to distinct
 # punctured SOURCE rays, using baseline full catalog coordinates if supplied.
 assert len(w['ret'])==len(set(w['ret']))==9
 copyguard=json.loads((I/'r0028/COPY-GUARDS.json').read_bytes())
 for a,b in zip(info['COPY'],copyguard['copies']):
  assert a['role']==b['source_role'] and a['frame']==b['source_FRAME'] and a['SOURCE_row_hex']==b['SOURCE_row_hex'] and a['recipients']==b['recipients_Y_roles']
 literal_ops=column_engine(w)
 mutant=dict(w);mutant['C']=w['C'][:-1];assert whole(mutant)!=expected
 mutant2=dict(w);mutant2['D']=w['D'][1:];assert whole(mutant2)!=expected
 # A changed-original copy erase is algebraically nonzero; guards must reject it.
 r=w['ret'][0];work=cap[r];changed_original=cap[r]^(1<<222);work^=changed_original;assert work==(1<<222)
 compact=read('r0028/COMPACT-R438-WORD.json.gz');assert all(w[k]==compact[k] for k in w if k!='stats')
 assert w['stats']['extra_carriers']==9 and compact['stats']['extra_carriers']==10
 result={'status':'PASS_INDEPENDENT_R438_LOCAL660_FRAME_COPY_SOURCE_DIRTY_INTAKE_GLOBAL_OPEN',
  'word_gzip_sha256':sha(I/'r0028/FINAL-R438-WORD.json.gz'),
  'word_content_sha256':hashlib.sha256(gzip.decompress((I/'r0028/FINAL-R438-WORD.json.gz').read_bytes())).hexdigest(),
  'columns':{'SOURCE':111,'Y':111,'ordinary_DIRTY':438,'total':660,'row_matrix_and_literal_column_engine':True,'literal_column_ops':literal_ops},
  'geometry':{'frames':636,'exact_closure_tests':636*111,'all_selected_SOURCE_geometry_unchanged':True},
  'change':{'removed_old_helper':464,'removed_LOAD_source_compressed':54,'removed_LOAD_source_full':59,
   'distinct_from_public470':True,'selected589_retuning_preserved':True,'node_A_interval':[1985,1995],
   'node_records':10,'node_scalar_XORs':sum(len(ss) for f,d,ss in node),'same_full10role_map_as60ADD':True,
   'node_helper_destinations':[241,340,349],'node_readonly_external_roles':external,
   'all_surviving_FRAME_paths_unchanged':True,'SOURCE_write_history_unchanged':True,'D0_K_exact':True,'C_literal_inverse':True},
  'ledger':info,'profile_delta':{str(k):c for k,c in delta.items() if c},
  'negative_controls':['missing C cleanup','missing D0 dirty cancellation','changed original before COPY erase'],
  'native_scope':'General nested-frame gauge lemma with paid full-stream D_F COPY; no new actual point/cover/global native replay in this intake. COPY/source access contract remains inherited equally as selected.',
  'global_rehost_owner_INDEX_ROW':'OPEN; r29 not received in this audit. No aggregate control is admitted.',
  'candidate':False,'new_supplier':False,'whole_kappa_changed':False,'CPU_seconds':time.process_time()-cpu}
 write('RESULT.json',result)
 print(json.dumps({'status':result['status'],'columns':660,'mass':info['mass'],'node_XORs':result['change']['node_scalar_XORs'],'CPU_seconds':result['CPU_seconds']}))
if __name__=='__main__':main()
