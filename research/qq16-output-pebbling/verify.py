#!/usr/bin/env python3
"""Output-slot pebbling of the actual PR3985 recovery word.
Chris R / Clear1nsight, substantial OpenAI Codex assistance, Apache-2.0.
Source algebra/native methods credited to ywz65, Arham Tahir and QQ16 lineage.
"""
import argparse,gzip,hashlib,io,json,tarfile,types
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,why):
 if not ok:raise ValueError(why)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def read(path):
 def unique(pairs):
  out={}
  for k,v in pairs:need(k not in out,'duplicate JSON key');out[k]=v
  return out
 return json.loads(path.read_text(),object_pairs_hook=unique)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def module(path,name):
 m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def authenticate():
 pins={}
 for r in read(HERE/'SOURCES.json')['files']:
  if r['usage']=='input':
   b=(ROOT/r['path']).read_bytes();need(sha(b)==r['sha256'],'source SHA256:'+r['path']);need(blob(b)==r['git_blob'],'source Git blob:'+r['path']);pins[r['path']]=sha(b)
 b=(HERE/'vendor/pr3985/WORD.json').read_bytes()
 need(sha(b)=='a854f516f1d80635fb3414734f9e1c6d1251a5d79ef12e137c143fc6b0b51722' and blob(b)=='1518ddc9b61aa6bede045d20f0d5e8cf664863fa','retained PR3985 word authentication')
 return pins,json.loads(b)
def source_fusion(P,R,old):
 """Independently regenerate the pinned rectangular source from canonical2707."""
 start=next(i for i,e in enumerate(old) if e[0]=='map' and e[2]==2)
 stop=max(i for i,e in enumerate(old) if e[0]=='map' and e[2]==2)+1
 w=[]
 for p in P.U+P.T:w += [['clear','D'+str(p),'current'],['add','D'+str(p),'W'+str(p),'1'],['map','D'+str(p),2,p,False],['line','D'+str(p),p,-1]]
 w += [['clear','D'+str(p),'query2'] for p in P.A]+[['begin','rectangular_future_correction',8]]
 for k in range(8):
  w.append(['clear','F'+str(k),'query2'])
  for p in P.U+P.T:
   if R[k][p]:w.append(['add','F'+str(k),'D'+str(p),str(R[k][p])])
 for p in P.A:
  for k in range(8):
   if R[k][p]:w.append(['add','D'+str(p),'F'+str(k),str(-R[k][p]/4)])
 w += [['clear','F'+str(k),'identity'] for k in range(8)]+[['end','rectangular_future_correction',8]]
 for p in P.A:w += [['line','D'+str(p),p,1],['map','D'+str(p),2,p,True],['add','W'+str(p),'D'+str(p),'1']]
 w += [['clear','D'+str(p),'identity'] for p in range(112)]
 return old[:start]+w+old[stop:]
def refs(e):
 if e[0]=='add':return {e[1],e[2]}
 if e[0] in ('clear','line','map','stage'):return {e[1]}
 return set()
def allocate(P,source):
 start=next(i for i,e in enumerate(source) if e[0]=='clear' and e[1].startswith('D'))
 final_clear=[i for i,e in enumerate(source) if e[0]=='clear' and e[1].startswith('D') and e[2]=='identity']
 stop=max(final_clear)+1;prefix=source[:start];block=source[start:stop];suffix=source[stop:]
 free=list(P.U+P.A);query=list(P.U+P.T);response=list(P.A)
 need(len(free)==len(query)==104 and len(response)==8,'allocation cardinalities')
 qmap={'D'+str(p):'Z'+str(z) for p,z in zip(query,free)}
 rmap={'D'+str(p):'Z'+str(z) for p,z in zip(response,P.U[:8])};mapping=qmap|rmap
 # Capture the complete prefix dependency sets before deferring a definition.
 zreads=sorted({int(e[2][1:]) for e in prefix if e[0]=='add' and e[2].startswith('Z')})
 need(zreads==sorted(P.T),'exact pre-logger Z read set')
 deferred={};kept=[]
 for i,e in enumerate(prefix):
  hit=refs(e)&{'Z'+str(p) for p in free}
  if hit:
   need(len(hit)==1 and e[1] in hit,'unexpected read of deferred output')
   deferred.setdefault(e[1],[]).append((i,e))
  else:kept.append(e)
 for p in free:
  want=[['clear','Z'+str(p),'current'],['add','Z'+str(p),'X'+str(p),'1']]
  if p in P.A:want.append(['add','Z'+str(p),'W'+str(p),'1'])
  need([e for _,e in deferred['Z'+str(p)]]==want,'exact deferred definition')
 # W_A is unchanged between its normalization and the response ADDs.
 for p in P.A:
  writes=[(i,e) for i,e in enumerate(prefix) if e[0] in ('clear','add','line','map') and e[1]=='W'+str(p)]
  need([e[0] for _,e in writes]==['clear','add','line','map','map'],'W_A stability')
 moved_response_clears=[];new=[];inserted=False;restored_A=False
 first_response=next(i for i,e in enumerate(block) if e[0]=='add' and e[1] in rmap and e[2].startswith('F'))
 query_reads=[i for i,e in enumerate(block) if e[0]=='add' and e[2] in qmap]
 need(max(query_reads)<first_response,'all queries precede response writes')
 for i,e in enumerate(block):
  if e[0]=='clear' and e[1] in rmap and e[2]=='query2':moved_response_clears.append(e);continue
  if e[0]=='clear' and e[1].startswith('D') and e[2]=='identity':continue
  if i==first_response:
   need(len(moved_response_clears)==8,'response initialization census');new+=moved_response_clears;inserted=True
  new.append(e)
  if e[:2]==['end','rectangular_future_correction']:
   # Only query-only Z_A slots are overwritten here, before W_A changes.
   need(not (set(rmap.values())&{'Z'+str(p) for p in P.A}),'response/output conflict')
   for p in P.A:new += [e for _,e in deferred['Z'+str(p)]]
   restored_A=True
 need(inserted and restored_A,'lifetime boundaries')
 renamed=[]
 for e in new:
  renamed.append([mapping.get(v,v) if isinstance(v,str) else v for v in e])
 out=kept+renamed
 for p in P.U:out += [e for _,e in deferred['Z'+str(p)]]
 out+=suffix
 need(not any(n.startswith('D') for e in out for n in refs(e)),'no external D bank')
 record={'source_window':[start,stop],'prefix_Z_read_ports':zreads,'deferred_output_ports':free,
 'query_assignment':qmap,'response_assignment':rmap,'last_query_read_in_block':max(query_reads),'first_response_write_in_block':first_response,
 'deferred_definition_events':{n:[i for i,_ in rows] for n,rows in sorted(deferred.items())},
 'proof':'All query operands captured before response reuse; Z_A restored while W_A remains unchanged; Z_U restored after response last use.'}
 begin=next(i for i,e in enumerate(out) if e[:2]==['begin','rectangular_future_correction'])
 end=next(i for i,e in enumerate(out) if e[:2]==['end','rectangular_future_correction'])
 intervals=[]
 for d,z in qmap.items():
  initial=next(i for i,e in enumerate(out) if e==['clear',z,'current'])
  reads=[i for i,e in enumerate(out) if begin<i<end and e[0]=='add' and e[2]==z and e[1].startswith('F')]
  output=max(i for i,e in enumerate(out) if e==['clear',z,'current'])
  need(reads and initial<min(reads)<=max(reads)<output,'query/output lifetime order')
  r=next((key for key,value in rmap.items() if value==z),None)
  entry={'physical_slot':z,'query_role':d,'query_initialize':initial,'query_first_read':min(reads),'query_last_read':max(reads),'output_initialize':output,'response_role':r}
  if r is not None:
   init=next(i for i,e in enumerate(out) if e==['clear',z,'query2'])
   use=next(i for i,e in enumerate(out) if i>end and e[0]=='add' and e[2]==z and e[1]=='W'+r[1:])
   need(max(reads)<init<end<use<output,'response lifetime order');entry.update(response_initialize=init,response_last_read=use)
  intervals.append(entry)
 record['literal_physical_lifetimes']=intervals
 return out,record

def invoice(w):
 c=Counter(e[0] for e in w)
 for e in w:
  if e[0]=='add':
   q=abs(Q(e[3]));need(q in (1,Q(1,4)),'unpriced ADD');c['unit_ADD' if q==1 else 'quarter_ADD']+=1
 return {**dict(sorted(c.items())),'native_wrappers':2*c['line'],'scalar_allowance':8*c['unit_ADD']+12*c['quarter_ADD']+2*c['clear']}
def caller():
 path=ROOT/'research/community-frontier1042-audit/selected-replay.tar.gz'
 name='t16/global/hosted/GLOBAL-TEMPLATE.json.gz'
 with tarfile.open(path,'r:gz') as a:b=a.extractfile(name).read()
 need(sha(b)=='73f47a1e60b1e4ea66dbca9a497c411c8e6adc7984e276a437a10a9a7a13b47a','hosted template member')
 t=json.loads(gzip.decompress(b));events=[e for e in t['execution_schedule'] if e.get('replica')==0][:5]
 need([e['source_event'] for e in events]==list(range(5)) and events[1]['kind']=='local_cover_sweep','first B1 source cut')
 calls=[c for c in t['calls'] if c['replica']==0 and c['stage'] in (0,1)]
 need(len(calls)==2 and [(c['stage'],c['orientation'],c['pair'],c['provider_id']) for c in calls]==[(0,'forward',0,'gauge44'),(1,'backward',0,'gauge44')],'actual F0/B1 gauge44 calls')
 need(events[0]['stage']==0 and events[1]['stage']==1 and events[0]['provider_id']==events[1]['provider_id']=='gauge44','actual hosted stages')
 need(events[2]['kind']=='idle_cover_sweep' and events[2]['pair']==1 and events[3]['kind']=='bridge' and events[3]['src']==1 and events[3]['dst']==0,'actual following continuation')
 return {'prefix':events,'boundary':'After replica0 physicalsource_event1 B1 and before event2 idle; retain current pair0 X/Y as borrowed. This adds a full recovery consumer under its explicit224-owned-output contract; those outputs are not certified free stock in the original gauge44 hosted template.','member_sha256':sha(b)}
def compute():
 pins,source=authenticate();L=module(ROOT/'research/qq16-line-normalized-decoder/verify.py','canonical2707');P,R,routes,labels,_=L.load_source()
 old=read(ROOT/'research/qq16-line-normalized-decoder/WORD.json');need(canonical(L.lower(P,R))==canonical(old),'canonical word regeneration')
 need(canonical(source_fusion(P,R,old))==canonical(source),'complete PR3985 source regeneration')
 word,allocation=allocate(P,source)
 independent=[[{(s+str(p),P.AXES):Q(1)} for p in range(112)] for s in ('X','Y')]
 want=P.inverse_formula(R,routes,*independent);counts=L.replay(P,word,routes,labels,*independent,want)
 original=[[{(s+str(p),P.AXES):Q(1)} for p in range(112)] for s in ('x','y')]
 x2,y2,x1,y1=P.forward(R,routes,*original);L.replay(P,word,routes,labels,x2,y2,original,(x1,y1))
 controls=[]
 def reject(label,mutator):
  w=deepcopy(word);mutator(w)
  try:L.replay(P,w,routes,labels,*independent,want)
  except (ValueError,KeyError):controls.append(label);return
  raise ValueError('accepted mutant:'+label)
 # Deferred slots are not free before their old live values have been removed.
 name=allocation['response_assignment']['D'+str(P.A[0])]
 reject('response clear before final query read',lambda w:w.insert(next(i for i,e in enumerate(w) if e[:2]==['begin','rectangular_future_correction'])+1,w.pop(next(i for i,e in enumerate(w) if e==['clear',name,'query2']))))
 reject('omit deferred output initialization',lambda w:w.pop(max(i for i,e in enumerate(w) if e==['clear','Z'+str(P.U[0]),'current'])))
 reject('borrowed output alias',lambda w:w.__setitem__(next(i for i,e in enumerate(w) if e[0]=='add' and e[1]==name),['add','X0',name,'1']))
 reject('wrong query frame',lambda w:w.__setitem__(next(i for i,e in enumerate(w) if e==['clear',name,'query2']),['clear',name,'current']))
 reject('restore A after correction',lambda w:delay_A(w,P))
 reject('omit first query initialization',lambda w:w.pop(next(i for i,e in enumerate(w) if e==['clear',name,'current'])))
 reject('overwrite live selected output',lambda w:w.insert(next(i for i,e in enumerate(w) if e[:2]==['begin','rectangular_future_correction'])+1,['clear','Z'+str(P.T[0]),'query2']))
 reject('private dirty return',lambda w:w.pop(next(i for i,e in enumerate(w) if e==['clear','F0','identity'])))
 Native=module(HERE/'native.py','native');native=Native.kernel_checks(P,labels,word)
 try:Native.kernel_checks(P,labels,word,wrong_negative_offset=True)
 except ValueError:controls.append('wrong negative native translation')
 else:raise ValueError('native negative control accepted')
 oldbill,newbill=invoice(source),invoice(word)
 need(newbill['line']==224 and newbill['map']==352 and newbill['scalar_allowance']==26960,'complete coalesced invoice')
 need(newbill['clear']==424 and newbill['unit_ADD']==1920 and newbill['quarter_ADD']==896,'complete scalar invoice')
 result={'status':'PASS_QQ16_OUTPUT_PEBBLING','no_new_kappa':True,'source_pins':pins,'source_head':'400df7fca8f60c19bf163c77564fe3fbe9154b04','source_word_events':len(source),'word_events':len(word),'allocation':allocation,'source_invoice':oldbill,'new_invoice':newbill,'storage':{'owned_outputs':224,'additional_full_cover_temporaries':0,'previous_additional_temporaries':112,'abstract_owned_full_cover_fields':224,'private_peak':16,'borrowed_current_XY':224,'borrowed_return':'identical values and frames','outputs':'all224 original arrays inF17','external_dirty_helpers':'none used'},'checks':{'independent_current_routed_fields':224,'independent_original_routed_fields':224,'arbitrary_owned_output_dirt':224,'phase_coordinates':73,'semantic_controls':controls,'native':native},'actual_caller':caller(),'scope':'Literal local output-bank allocation under the original224-owned-output contract. Six-tape placement, movement, precision, global family coverage and supplier admission remain open; no kappa or free selected stock claim.'}
 return word,result

def delay_A(w,P):
 p=P.A[0];seq=[['clear','Z'+str(p),'current'],['add','Z'+str(p),'X'+str(p),'1'],['add','Z'+str(p),'W'+str(p),'1']]
 start=next(i for i in range(len(w)-2) if w[i:i+3]==seq);del w[start:start+3]
 at=next(i for i,e in enumerate(w) if e[0]=='add' and e[1]=='W'+str(p) and e[2].startswith('Z') and i>start);w[at+1:at+1]=seq

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 if args.write:need(not (HERE/'WORD.json').exists() and not (HERE/'RESULT.json').exists(),'refuse overwrite')
 word,result=compute()
 if args.write:
  (HERE/'WORD.json').write_text(json.dumps(word,separators=(',',':'))+'\n');(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:need(canonical(read(HERE/'WORD.json'))==canonical(word),'complete word mismatch');need(canonical(read(HERE/'RESULT.json'))==canonical(result),'complete typed receipt mismatch')
 print(result['status']);print(json.dumps(result['new_invoice'],sort_keys=True))
if __name__=='__main__':main()
