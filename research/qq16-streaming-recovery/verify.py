#!/usr/bin/env python3
"""Source-bound streamed future-logger correction for full QQ16 recovery.
Chris R / Clear1nsight with OpenAI assistance. Apache-2.0.
"""
import argparse,hashlib,json,types
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,why):
 if not ok:raise ValueError(why)
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def typed(obj):
 if isinstance(obj,dict):return ('dict',tuple((k,typed(v)) for k,v in sorted(obj.items())))
 if isinstance(obj,list):return ('list',tuple(map(typed,obj)))
 return (type(obj).__name__,obj)
def load_module(path,name):
 m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def authenticate():
 pins=json.loads((HERE/'SOURCES.json').read_text())
 for item in pins['files']:
  if item['usage']!='input':continue
  raw=(ROOT/item['path']).read_bytes()
  need(hashlib.sha256(raw).hexdigest()==item['sha256'],'source hash:'+item['path'])
  need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob'],'source blob:'+item['path'])
 return {r['path']:r['sha256'] for r in pins['files'] if r['usage']=='input'}
def materialized(P,R,original):
 start=next(i for i,e in enumerate(original) if e[0]=='map' and e[2]==2)
 stop=max(i for i,e in enumerate(original) if e[0]=='map' and e[2]==2)+1
 old=original[start:stop]
 need(sum(e[0]=='line' for e in old)==224,'future native window')
 w=[]
 def emit(*e):w.append(list(e))
 # Query sources are read into disposable owned copies. All originals stay F17.
 for p in P.U+P.T:
  emit('clear','D'+str(p),'current');emit('add','D'+str(p),'W'+str(p),'1')
  emit('map','D'+str(p),2,p,False);emit('line','D'+str(p),p,-1)
 for p in P.A:emit('clear','D'+str(p),'query2')
 emit('begin','rectangular_future_correction',8)
 for k in range(8):
  emit('clear','F'+str(k),'query2')
  for p in P.U+P.T:
   if R[k][p]:emit('add','F'+str(k),'D'+str(p),str(R[k][p]))
 for p in P.A:
  for k in range(8):
   if R[k][p]:emit('add','D'+str(p),'F'+str(k),str(-R[k][p]/4))
 for k in range(8):emit('clear','F'+str(k),'identity')
 emit('end','rectangular_future_correction',8)
 for p in P.A:
  emit('line','D'+str(p),p,1);emit('map','D'+str(p),2,p,True)
  emit('add','W'+str(p),'D'+str(p),'1')
 for p in range(112):emit('clear','D'+str(p),'identity')
 return original[:start]+w+original[stop:],{'start':start,'stop_exclusive':stop,'old':old,'new':w}
def invoice(w):
 c=Counter(e[0] for e in w)
 for e in w:
  if e[0]=='add':
   q=abs(Q(e[3]));need(q in (1,Q(1,4)),'unpriced scalar')
   c['unit_ADD' if q==1 else 'quarter_ADD']+=1
 c['native_wrappers']=2*c['line'];c['scalar_allowance']=8*c['unit_ADD']+12*c['quarter_ADD']+2*c['clear']
 return dict(sorted(c.items()))
def streamed(P,R,original):
 start=next(i for i,e in enumerate(original) if e[0]=='map' and e[2]==2)
 stop=max(i for i,e in enumerate(original) if e[0]=='map' and e[2]==2)+1
 w=[]
 def emit(*e):w.append(list(e))
 for k in range(8):emit('clear','Q'+str(k),'query2')
 for p in P.U+P.T:
  emit('clear','D','current');emit('add','D','W'+str(p),'1')
  emit('map','D',2,p,False);emit('line','D',p,-1)
  for k in range(8):
   if R[k][p]:emit('add','Q'+str(k),'D',str(R[k][p]))
 for p in P.A:
  emit('clear','D','query2')
  for k in range(8):
   if R[k][p]:emit('add','D','Q'+str(k),str(-R[k][p]/4))
  emit('line','D',p,1);emit('map','D',2,p,True)
  emit('add','W'+str(p),'D','1')
 emit('clear','D','identity')
 for k in range(8):emit('clear','Q'+str(k),'identity')
 return original[:start]+w+original[stop:],{'start':start,'stop_exclusive':stop,'old':original[start:stop],'new':w}

def rank_pivots(matrix):
 a=[list(map(Q,row)) for row in matrix];r=0;pivots=[]
 for c in range(len(a[0])):
  pivot=next((i for i in range(r,len(a)) if a[i][c]),None)
  if pivot is None:continue
  a[r],a[pivot]=a[pivot],a[r];scale=a[r][c];a[r]=[x/scale for x in a[r]]
  for i in range(len(a)):
   if i!=r:
    scale=a[i][c];a[i]=[x-scale*y for x,y in zip(a[i],a[r])]
  pivots.append(c);r+=1
  if r==len(a):break
 return r,pivots

def host_output_banks(P,word,ports=None):
 ports=P.U[:9] if ports is None else ports
 need(len(set(ports))==9 and all(type(p) is int and 0<=p<112 for p in ports),'host nine distinct output banks')
 aliases=dict(zip(['Q'+str(k) for k in range(8)]+['D'],['Z'+str(p) for p in ports]))
 start=next(i for i,e in enumerate(word) if e==['clear','Q0','query2'])
 stop=next(i for i,e in enumerate(word) if e==['clear','Q7','identity'])+1
 definitions={};skip=set()
 for name in aliases.values():
  refs=[i for i,e in enumerate(word[:stop]) if name in e[1:3]]
  expected=[['clear',name,'current'],['add',name,'X'+name[1:],'1']]
  need([word[i] for i in refs]==expected and refs[-1]<start,'deferred output def-use contract '+name)
  definitions[name]={'source_events':refs,'word':expected};skip.update(refs)
 out=[];restores={}
 for i,e in enumerate(word):
  if i in skip:continue
  if e[0]=='clear' and e[1] in aliases and e[2]=='identity':continue
  if i==stop:
   for name in aliases.values():
    restores[name]=[len(out),len(out)+1];out.extend(definitions[name]['word'])
  out.append([aliases.get(x,x) if isinstance(x,str) else x for x in e])
 return out,{'aliases':aliases,'deferred_definitions':definitions,'restore_events':restores,'source_window':[start,stop],
  'removed_terminal_clears':9,'temporary_abi':'Aliased roles end by paid CLEAR/X-copy into their output banks, not independent zero-return buffers'}

def compute():
 pins=authenticate()
 raw=(HERE/'vendor/PR3985-WORD.json').read_bytes()
 need(hashlib.sha256(raw).hexdigest()=='a854f516f1d80635fb3414734f9e1c6d1251a5d79ef12e137c143fc6b0b51722','retained PR3985 word hash')
 L=load_module(ROOT/'research/qq16-line-normalized-decoder/verify.py','canonical_line_decoder')
 P,R,routes,labels,_=L.load_source()
 old=json.loads((ROOT/'research/qq16-line-normalized-decoder/WORD.json').read_text())
 need(canonical(old)==canonical(L.lower(P,R)),'canonical word regenerated')
 previous,_=materialized(P,R,old)
 need(typed(json.loads(raw))==typed(previous),'PR3985 whole word regenerated')
 nine,window=streamed(P,R,old)
 word,hosting=host_output_banks(P,nine)
 Replay=load_module(HERE/'replay.py','stream_replay')
 original=[[{(side+str(p),P.AXES):Q(1)} for p in range(112)] for side in ('x','y')]
 x2,y2,x1,y1=P.forward(R,routes,*original)
 counts=Replay.replay(P,word,routes,labels,x2,y2,original,(x1,y1))
 independent=[[{(side+str(p),P.AXES):Q(1)} for p in range(112)] for side in ('X','Y')]
 expected=P.inverse_formula(R,routes,*independent)
 Replay.replay(P,word,routes,labels,*independent,expected)
 Replay.replay(P,nine,routes,labels,*independent,expected,extra_owned=['D']+['Q'+str(k) for k in range(8)])
 controls=[];d=hosting['aliases']['D'];q0=hosting['aliases']['Q0']
 def reject(label,mutate):
  changed=deepcopy(word);mutate(changed)
  try:Replay.replay(P,changed,routes,labels,*independent,expected)
  except (ValueError,KeyError):controls.append(label);return
  raise ValueError('accepted mutant:'+label)
 reject('hold private scratch across native call',lambda w:w.insert(next(i for i,e in enumerate(w) if e==['clear',q0,'query2']),['begin','illegal_private_query_hold',8]))
 reject('omit source native line',lambda w:w.pop(next(i for i,e in enumerate(w) if e==['line',d,P.U[0],-1])))
 reject('omit dirty query initialization',lambda w:w.pop(next(i for i,e in enumerate(w) if e==['clear',q0,'query2'])))
 reject('omit recycled source initialization',lambda w:w.pop([i for i,e in enumerate(w) if e==['clear',d,'current']][1]))
 reject('clear query before responses',lambda w:w.insert(next(i for i,e in enumerate(w) if e==['clear',d,'query2']),['clear',q0,'query2']))
 reject('drop inverse response map',lambda w:w.pop(next(i for i,e in enumerate(w) if e==['map',d,2,P.A[0],True])))
 reject('omit output reinitialization clear',lambda w:w.pop(hosting['restore_events'][q0][0]))
 reject('omit output restore copy',lambda w:w.pop(hosting['restore_events'][q0][1]))
 reject('borrowed output alias',lambda w:w.__setitem__(next(i for i,e in enumerate(w) if e==['add','W'+str(P.A[0]),d,'1']),['add','Y'+str(P.A[0]),d,'1']))
 try:host_output_banks(P,nine,[P.T[0]]+list(P.U[1:9]))
 except ValueError:controls.append('reject live selected output alias')
 else:raise ValueError('accepted live selected output')
 Native=load_module(HERE/'native.py','stream_native');native=Native.kernel_checks(P,labels,word)
 try:Native.kernel_checks(P,labels,word,wrong_negative_offset=True)
 except ValueError:controls.append('wrong negative native wrapper offset')
 else:raise ValueError('accepted wrong native wrapper offset')
 before,ninebill,after=invoice(previous),invoice(nine),invoice(word)
 need(after['line']==224 and after['map']==352,'native invoice')
 need(after['unit_ADD']==1920 and after['quarter_ADD']==896 and after['clear']==416,'scalar invoice')
 need(after['scalar_allowance']==26944 and len(word)==3813,'complete scalar allowance/word size')
 need(ninebill['clear']==425 and ninebill['scalar_allowance']==26962,'external nine-bank reference invoice')
 need(after['unit_ADD']==counts['unit_ADD'] and after['quarter_ADD']==counts['quarter_ADD'],'interpreter invoice')
 lifetime={}
 for role,name in hosting['aliases'].items():
  restore=hosting['restore_events'][name][0]
  refs=[i for i,e in enumerate(word[:restore]) if name in e[1:3]]
  need(word[refs[0]][:2]==['clear',name],'first hosted use initializes arbitrary dirt')
  lifetime[role]={'host':name,'first_clear':refs[0],'last_role_use':refs[-1],'output_clear':restore,'output_copy':restore+1,
   'native_calls_before_output_restore':sum(e[0]=='line' for e in word[refs[0]:restore])}
 rank_query,pivots=rank_pivots([[R[k][p] for p in P.U+P.T] for k in range(8)])
 rank_response,_=rank_pivots([[R[k][p] for p in P.A] for k in range(8)])
 need(rank_query==rank_response==8,'full rank query and response')
 nine_access=invoice(window['new'])
 host_begin=min(x['first_clear'] for x in lifetime.values())
 host_end=max(x[1] for x in hosting['restore_events'].values())+1
 host_access=invoice(word[host_begin:host_end])
 moved_access=invoice([e for x in hosting['deferred_definitions'].values() for e in x['word']])
 need((nine_access['add'],nine_access['clear'],nine_access['line'],nine_access['map'])==(560,129,112,112),'nine-bank scalar/native traversal census')
 need((host_access['add'],host_access['clear'],host_access['line'],host_access['map'])==(569,129,112,112),'hosted scalar/native traversal census')
 need((moved_access['add'],moved_access['clear'])==(9,9),'moved output definitions census')
 def traffic(c,include_native=True):
  out={'scalar_passes':c['add']+c['clear'],'reads_per_site':2*c['add'],'writes_per_site':c['add']+c['clear']}
  if include_native:out.update(native_calls=c['line'],cover_maps=c['map'])
  return out
 access={'model':'One whole-cover pass per ADD or CLEAR; ADD reads both operands and writes destination, CLEAR writes destination. Native/map/wrapper/address/control/bit costs excluded and unknown.',
  'nine_bank_block':traffic(nine_access),
  'hosted_block_including_nine_deferred_output_definitions':traffic(host_access),
  'moved_from_prefix':traffic(moved_access,False),
  'net_delta_vs_nine_bank':{k:traffic(after,False)[k]-traffic(ninebill,False)[k] for k in traffic(after,False)},
  'head_movement':'unknown','physical_storage_allocation_and_release':'unknown','numerical_precision_and_bit_cost':'unknown'}
 result={'status':'PASS_QQ16_HOSTED_STREAMING_RECOVERY','source_pins':pins,'word_events':len(word),'word_sha256':hashlib.sha256(canonical(word)).hexdigest(),
  'output_contract':'All224 original x0/y0 inF17; all224 currentXY borrowed untouched; only224 owned output banks plus existing owner-private scratch',
  'previous_full_invoice':before,'nine_bank_reference_invoice':ninebill,'new_full_invoice':after,'nine_bank_reference_word_sha256':hashlib.sha256((json.dumps(nine,separators=(',',':'))+'\n').encode()).hexdigest(),
  'hosting':hosting,'storage':{'owned_outputs':224,'previous_additional_owned':112,'nine_bank_reference_additional_owned':9,'new_additional_owned':0,'private_peak':16,'new_private_future_peak':0,'lifetime':lifetime,'return':'All nine aliased output banks are reinitialized by paid CLEAR/X-copy before the original suffix; final224outputs exact'},
  'native_lowering':native,'scalar_access_protocol':access,'query_rank':{'rank':rank_query,'pivot_ports':[(P.U+P.T)[i] for i in pivots],'response_rank':rank_response,'scope':'Rank of materialized query interface; not a general workspace lower bound'},
  'checks':{'original_routed_arrays':224,'independent_current_routed_arrays':224,'nine_bank_reference_independent_current_replay':224,'phase_coordinates':73,'semantic_controls':controls},
  'scope':'Exact hosted streamed module, primitive and bank-lifetime improvement. No new physical movement tariff, numerical error proof, supplier admission or kappa improvement.'}
 return word,result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if a.write:need(not (HERE/'RESULT.json').exists() and not (HERE/'WORD.json').exists(),'refuse overwrite')
 word,result=compute()
 if a.write:
  (HERE/'WORD.json').write_text(json.dumps(word,separators=(',',':'))+'\n');(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:
  need(typed(json.loads((HERE/'WORD.json').read_text()))==typed(word),'whole word mismatch')
  need(typed(json.loads((HERE/'RESULT.json').read_text()))==typed(result),'whole typed receipt mismatch')
 print(result['status']);print(json.dumps(result['new_full_invoice'],sort_keys=True));print(json.dumps(result['storage'],sort_keys=True))
