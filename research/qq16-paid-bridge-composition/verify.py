#!/usr/bin/env python3
"""Paid query and bridge composition, Apache-2.0, Chris R / Clear1nsight.
Substantial OpenAI Codex assistance. No predecessor executable imports.
Exact routed/Z4 primitives adapt credited QQ16, PR2681 and PR2707 methods.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip,hashlib,io,json,tarfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
AXES=tuple(1<<i for i in range(73))
F17=tuple((v,1) for v in AXES[:17])
MEMBERS={
't16/global/hosted/GLOBAL-TEMPLATE.json.gz':'73f47a1e60b1e4ea66dbca9a497c411c8e6adc7984e276a437a10a9a7a13b47a',
't16/global/base/work/complex-nine-native/DATA-PHASES.json':'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'}
def need(ok,why):
 if not ok:raise ValueError(why)
def read(path):
 def unique(pairs):
  out={}
  for k,v in pairs:need(k not in out,'duplicate JSON key');out[k]=v
  return out
 return json.loads(path.read_text(),object_pairs_hook=unique)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(x):return hashlib.sha256(x).hexdigest()
def load():
 raw={}
 for row in read(HERE/'SOURCES.json')['files']:
  if row['usage']=='input':
   data=(ROOT/row['path']).read_bytes();need(sha(data)==row['sha256'],'input hash '+row['path'])
   need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'input Git blob '+row['path']);raw[row['path']]=data
 packet=json.loads(gzip.decompress(raw['research/joint-query/certificate.json.gz']));decoded={}
 with tarfile.open(fileobj=io.BytesIO(raw['research/community-frontier1042-audit/selected-replay.tar.gz']),mode='r:gz') as archive:
  for name,pin in MEMBERS.items():
   matches=[m for m in archive.getmembers() if m.name==name]
   need(len(matches)==1 and matches[0].isfile(),'unique archive member')
   data=archive.extractfile(matches[0]).read();need(sha(data)==pin,'member pin')
   decoded[name]=json.loads(gzip.decompress(data) if name.endswith('.gz') else data)
 r=read(HERE/'PREDECESSORS.json')['retained_pending_sources'][0]
 need(r['head']=='996ff698d3efd0bdce606e240f3b00e6ab91e7fc','retained head')
 data=(HERE/r['local_path']).read_bytes()
 need(sha(data)==r['sha256']=='f513d235b8206211a4716d013a6dacf34aaebda6839da721b0231981cb8b905e','retained word SHA256')
 need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['git_blob'],'retained blob')
 return packet,decoded,json.loads(data),{p:sha(v) for p,v in raw.items()}
def act(g,v):
 out=0
 while v:bit=v&-v;out^=g[bit.bit_length()-1];v^=bit
 return out
@lru_cache(None)
def product(g,h):return tuple(act(g,v) for v in h)
def plus(a,b,c=Q(1)):
 out=dict(a)
 for key,value in b.items():
  out[key]=out.get(key,Q(0))+c*value
  if out[key]==0:del out[key]
 return out
def routed(g,row):return {(name,product(g,h)):q for (name,h),q in row.items()}
@lru_cache(None)
def phase(terms):
 linear=[0]*73;cross=[0]*73
 for v,c in terms:
  bits=[i for i in range(73) if v>>i&1]
  for i in bits:
   linear[i]=(linear[i]+c)%4
   if c%2:
    for j in bits:
     if j>i:cross[i]^=1<<j
 return tuple(linear),tuple(cross)
def move(terms,g,b):return tuple((act(g,v),c) for v,c in terms)+((b,2),)
def frame_shift(g):
 before,after=phase(F17),phase(move(F17,g,0));need(before[1]==after[1],'quadratic map discrepancy')
 delta=[(a-b)%4 for a,b in zip(before[0],after[0])];need(all(x in (0,2) for x in delta),'odd map discrepancy')
 b=sum((x//2)<<i for i,x in enumerate(delta));need(phase(move(F17,g,b))==before,'full map frame');return b
def kernels(labels,U):
 columns=0;negative_controls=0
 for p,q in enumerate(labels):
  pivot=(q&-q).bit_length()-1;basis=(q,)+tuple(1<<i for i in range(9) if i!=pivot)
  inverse={act(basis,z):z for z in range(512)};need(len(inverse)==512,'line wrapper bijection')
  for sign in ((1,-1) if p in U else (1,)):
   for address in range(512):
    z=inverse[address];offset=q if sign<0 else 0
    actual={act(basis,z)^offset:(1,1),act(basis,z^1)^offset:(1,-1)}
    expected={address:(1,sign),address^q:(1,-sign)}
    need(actual==expected,'signed native Gaussian column');columns+=1
   if sign<0:
    wrong={0:(1,1),q:(1,-1)};need(wrong!={0:(1,-1),q:(1,1)},'missing negative translation control');negative_controls+=1
 return {'signed_basis_columns':columns,'positive_ports':112,'negative_ports':len(U),'negative_translation_controls':negative_controls,'normalization':'common Gaussian denominator2; tensor extension by products'}
def geometry(packet,decoded):
 A,T,U=map(tuple,(packet['A_ports'],packet['T_ports'],packet['U_ports']))
 need((len(A),len(T),len(U))==(8,8,96) and set(A+T+U)==set(range(112)),'port partition')
 R=[[Q(row.get(str(p),0)) for p in range(112)] for row in packet['R_rows']]
 need(all(sum(R[k][p]**2 for k in range(8))==4 for p in range(112)),'four terms per port')
 records=decoded['t16/global/base/work/complex-nine-native/DATA-PHASES.json']['recipes']
 registry={tuple(v['owner_right_matrix_columns']) for v in packet['map_registry'].values()}
 routes=[];labels=[];shifts=[]
 for p,r in enumerate(records):
  q=r['q'];basis=r['idle_children'][0]['orthogonal_axes'][:8]
  need(r['port']==p and q<512 and q.bit_count()%2==1,'port label')
  need(all((a&b).bit_count()%2==(i==j) for i,a in enumerate([q]+basis) for j,b in enumerate([q]+basis)),'orthonormal basis')
  swaps=[b^AXES[9+i] for i,b in enumerate(basis)]
  g=tuple(v^act(swaps,sum(((v&s).bit_count()%2)<<i for i,s in enumerate(swaps))) for v in AXES)
  need(g in registry and product(g,g)==AXES and act(g,q)==q,'actual route')
  routes.append(g);labels.append(q);shifts.append(frame_shift(g))
 need(len(routes)==112,'all routes');return A,T,U,R,routes,labels,shifts
def projection(R,U,V):
 w=[]
 for p in range(112):w += [['clear','W'+str(p),'hole'+str(p)],['add','W'+str(p),'Y'+str(p),'1'],['line','W'+str(p),p,1]]
 w += [['map','W'+str(p),1,p,False] for p in range(112)]
 w += [['begin','B1_current_query',8]]
 for k in range(8):
  w.append(['clear','F'+str(k),'wide'])
  for p in range(112):
   if R[k][p]:w.append(['add','F'+str(k),'W'+str(p),str(R[k][p])])
 for p in U:
  for k in range(8):
   if R[k][p]:w.append(['add','W'+str(p),'F'+str(k),str(-R[k][p]/4)])
 w += [['clear','F'+str(k),'identity'] for k in range(8)]+[['end','B1_current_query',8]]
 w += [['map','W'+str(p),1,p,True] for p in U]
 w += [['clear','W'+str(p),'identity'] for p in V]
 return w
def words(source,R,U):
 producer=[['clear','Q'+str(k),'current'] for k in range(8)];copied=False
 for e in source:
  if not copied and e[0]=='add' and e[1].startswith('W') and e[2].startswith('F'):
   producer += [['add','Q'+str(k),'F'+str(k),'1'] for k in range(8)];copied=True
  producer.append(e)
 need(copied,'query output cut')
 consumer=[['map','W'+str(p),1,p,False] for p in U]
 for p in U:
  for k in range(8):
   if R[k][p]:consumer.append(['add','W'+str(p),'Q'+str(k),str(R[k][p]/4)])
 consumer += [['map','W'+str(p),1,p,True] for p in U]
 for p in U:consumer += [['line','W'+str(p),p,-1],['add','B'+str(p),'W'+str(p),'-1'],['clear','W'+str(p),'identity']]
 consumer += [['clear','Q'+str(k),'identity'] for k in range(8)]
 direct=[['add','B'+str(p),'Y'+str(p),'-1'] for p in U]
 same=direct+[['clear','W'+str(p),'identity'] for p in range(112)]+[['clear','Q'+str(k),'identity'] for k in range(8)]
 return producer,consumer,direct,same
def invoice(w):
 c=Counter(e[0] for e in w)
 for e in w:
  if e[0]=='add':
   q=abs(Q(e[3]));need(q in (1,Q(1,4)),'unpriced ADD');c['unit_ADD' if q==1 else 'quarter_ADD']+=1
 out={k:c[k] for k in ('line','map','unit_ADD','quarter_ADD','clear','begin','end')}
 out.update(native_wrappers=2*c['line'],scalar_allowance=8*c['unit_ADD']+12*c['quarter_ADD']+2*c['clear']);return out
def replay(w,U,routes,labels,shifts,checkpoint=None):
 owned={'W'+str(p) for p in range(112)}|{'Q'+str(k) for k in range(8)}
 targets={'B'+str(p) for p in U};borrowed={'Y'+str(p) for p in range(112)}
 rows={n:{(n,AXES):Q(1)} for n in owned|targets|borrowed};frames={n:() for n in owned}
 for n in targets|borrowed:frames[n]=F17+((labels[int(n[1:])],-1),)
 original={n:dict(rows[n]) for n in borrowed};active=set();checks=0
 for i,e in enumerate(w):
  op=e[0]
  if op=='begin':
   need(not active and e[2]==8,'private lifetime');active={'F'+str(k) for k in range(8)}
   for n in active:rows[n]={(n,AXES):Q(1)};frames[n]=()
  elif op=='end':
   need(all(not rows[n] and phase(frames[n])==phase(()) for n in active),'private scratch leak')
   for n in active:del rows[n],frames[n]
   active=set()
  elif op=='clear':
   _,n,f=e;need(n in owned|active,'clear ownership');rows[n]={};frames[n]=() if f=='identity' else F17
   if f.startswith('hole'):frames[n]=F17+((labels[int(f[4:])],-1),)
  elif op=='add':
   _,dst,src,c=e;need(dst in owned|targets|active and dst!=src and src in rows,'ADD ownership')
   need(phase(frames[dst])==phase(frames[src]),'ADD frame mismatch '+str(i));checks+=1;rows[dst]=plus(rows[dst],rows[src],Q(c))
  elif op=='line':
   _,n,p,sign=e;need(not active and n in owned and sign in (-1,1),'native boundary');frames[n]+=((labels[p],sign),)
  elif op=='map':
   _,n,stage,p,inverse=e[:5];need(not active and stage==1 and n in owned,'map boundary')
   g=routes[p];b=act(g,shifts[p]) if inverse else shifts[p]
   if len(e)>5 and e[5]=='omit_shift':b=0
   frames[n]=move(frames[n],g,b);rows[n]=routed(g,rows[n])
  else:raise ValueError('unknown instruction')
  if checkpoint is not None and i+1==checkpoint[0]:checkpoint[1](rows,frames)
 need(not active,'unfinished private lifetime')
 need(all(rows[n]==original[n] and frames[n]==F17+((labels[int(n[1:])],-1),) for n in borrowed),'borrowed source changed')
 return rows,frames,checks
def compute():
 packet,decoded,source,pins=load();A,T,U,R,routes,labels,shifts=geometry(packet,decoded)
 need(projection(R,U,A+T)==source,'complete projection regeneration')
 producer,consumer,direct,same=words(source,R,U)
 Y=[{('Y'+str(p),AXES):Q(1)} for p in range(112)];query=[{} for _ in range(8)]
 for k in range(8):
  for p in range(112):
   if R[k][p]:query[k]=plus(query[k],routed(routes[p],Y[p]),R[k][p])
 projected=[]
 for p in U:
  row=Y[p]
  for k in range(8):
   if R[k][p]:row=plus(row,routed(routes[p],query[k]),-R[k][p]/4)
  projected.append(row)
 def boundary(rows,frames):
  for p,want in zip(U,projected):need(rows['W'+str(p)]==want and phase(frames['W'+str(p)])==phase(F17),'projected output')
  for k,want in enumerate(query):need(rows['Q'+str(k)]==want and phase(frames['Q'+str(k)])==phase(F17),'query output')
  need(all(not rows['W'+str(p)] and phase(frames['W'+str(p)])==phase(()) for p in A+T),'selected temporary cleanup')
 joined=producer+consumer;actual,af,checks=replay(joined,U,routes,labels,shifts,(len(producer),boundary));fused,ff,_=replay(same,U,routes,labels,shifts)
 need(actual==fused and all(phase(af[n])==phase(ff[n]) for n in af),'complete symbolic/frame fusion')
 need(all(not actual[n] and phase(af[n])==phase(()) for n in actual if n[0] in ('W','Q')),'owned cleanup')
 for p in U:
  n='B'+str(p);need(actual[n]=={(n,AXES):Q(1),('Y'+str(p),AXES):Q(-1)},'bridge output')
 template=decoded['t16/global/hosted/GLOBAL-TEMPLATE.json.gz'];events=[e for e in template['execution_schedule'] if e.get('replica')==0][:5]
 need([e['kind'] for e in events]==['local_cover_sweep','local_cover_sweep','idle_cover_sweep','bridge','local_cover_sweep'],'physical prefix')
 need([e['source_event'] for e in events]==list(range(5)) and events[3]['src']==1 and events[3]['dst']==0 and events[3]['coefficient']==1,'actual bridge event3')
 bad=deepcopy(joined);at=next(i for i in range(len(producer),len(bad)) if bad[i][0]=='add' and bad[i][2].startswith('Q'));bad[at][3]=str(-Q(bad[at][3]))
 got,_,_=replay(bad,U,routes,labels,shifts);need(any(got['B'+str(p)]!=actual['B'+str(p)] for p in U),'wrong query sign control')
 bad=deepcopy(joined);at=next(i for i,e in enumerate(bad) if e[0]=='map' and shifts[e[3]]!=0);bad[at].append('omit_shift');rejected=False
 try:replay(bad,U,routes,labels,shifts)
 except ValueError as exc:rejected='frame mismatch' in str(exc)
 need(rejected,'wrong affine shift control')
 bad=deepcopy(joined);at=next(i for i in range(len(producer),len(bad)) if bad[i][0]=='line');del bad[at];rejected=False
 try:replay(bad,U,routes,labels,shifts)
 except ValueError as exc:rejected='frame mismatch' in str(exc)
 need(rejected,'omitted inverse line control')
 bad=deepcopy(joined);bad.pop();got,_,_=replay(bad,U,routes,labels,shifts);need(bool(got['Q7']),'omitted query cleanup control')
 need(all(sum(R[i][p]*R[j][p] for p in U)==48*(i==j) for i in range(8) for j in range(8)),'eight query directions')
 invoices={n:invoice(w) for n,w in [('projection',source),('augmented_producer',producer),('consumer',consumer),('serial_composition',joined),('direct_bridge',direct),('direct_same_workspace',same)]}
 need(invoices['serial_composition']['line']==208 and invoices['serial_composition']['map']==400 and invoices['serial_composition']['scalar_allowance']==15040,'serial invoice')
 need(invoices['direct_bridge']['scalar_allowance']==768 and invoices['direct_same_workspace']['scalar_allowance']==1008,'direct invoices')
 wout={'augmented_producer':producer,'consumer':consumer,'direct_bridge':direct,'direct_same_workspace':same}
 result={'status':'PASS_QQ16_PAID_BRIDGE_COMPOSITION','no_new_kappa':True,'source_pins':pins,'archive_members':MEMBERS,'actual_bridge_physical_prefix':events,'native_kernel_checks':kernels(labels,U),
 'equation':'Y2_U=h+K_(1,U)a; h=Y2_U-K_(1,U)R_1Y2; a=R_1Y2',
 'typed_contract':{'borrowed_current_Y':112,'mutable_other_pair_Y_U':96,'owned_intermediate_outputs':{'h_F17':96,'a_F17':8},'owned_full_cover_workspace':120,'private_scratch_peak':8,'early_retention':0,'owned_workspace_final':'all zero/I','borrowed_sources':'unchanged','mutable_target_frame':'F17 C_q^-1 before and after','global_owner_placement':'not established for complete QQ16 substitution'},
 'checks':{'arbitrary_independent_data_fields':208,'independent_owned_dirt_fields':120,'intermediate_projected_routed_terms':sum(map(len,projected)),'query_routed_terms':sum(map(len,query)),'scalar_frame_equalities':checks,'full_mod4_phase_coordinates':73,'literal_projection_events':len(source),'regenerated_projection_matches':True,'exact_final_operator_and_frames_equal_direct':True},
 'invoices':invoices,'word_sha256':{k:sha(canonical(v).encode()) for k,v in wout.items()},
 'negative_controls':['wrong query sign changes exact routed bridge output','omit affine shift rejects frame mismatch','omit inverse C_q rejects target frame mismatch','omit query clear leaves nonzero owned output'],
 'source_work_replaced':{'ordinary_Y_bridge_unit_ADDs':96,'ordinary_X_bridge':'unchanged and outside replacement','additional_source_ADDs_eliminated':0},
 'decision':'stop serial decode/query/reconstitute route for this bridge-only demand: fusion yields existing direct Y bridge, not source saving',
 'scope':'Constructive local native contract and exact operator/frame proof. Global placement, movement, coverage, precision and recursive admission remain open. No optimality theorem for changed producers/shared consumers.'}
 return result,wout
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 if args.write:need(not (HERE/'RESULT.json').exists() and not (HERE/'WORDS.json').exists(),'refuse overwrite of existing RESULT/WORDS')
 result,wout=compute()
 if args.write:
  (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');(HERE/'WORDS.json').write_text(json.dumps(wout,indent=2)+'\n')
 else:
  need(canonical(read(HERE/'RESULT.json'))==canonical(result),'complete typed receipt mismatch');need(canonical(read(HERE/'WORDS.json'))==canonical(wout),'complete word mismatch')
 print('PASS_QQ16_PAID_BRIDGE_COMPOSITION no_new_kappa')
if __name__=='__main__':main()
