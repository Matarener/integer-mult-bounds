#!/usr/bin/env python3
"""Source-bound rectangular future-logger correction for full QQ16 recovery.
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
def fused(P,R,original):
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
def compute():
 pins=authenticate()
 L=load_module(ROOT/'research/qq16-line-normalized-decoder/verify.py','canonical_line_decoder')
 P,R,routes,labels,_=L.load_source()
 old=json.loads((ROOT/'research/qq16-line-normalized-decoder/WORD.json').read_text())
 need(canonical(old)==canonical(L.lower(P,R)),'canonical word regenerated')
 word,window=fused(P,R,old)
 Replay=load_module(HERE/'replay.py','fusion_replay')
 original=[[{(side+str(p),P.AXES):Q(1)} for p in range(112)] for side in ('x','y')]
 x2,y2,x1,y1=P.forward(R,routes,*original)
 counts=Replay.replay(P,word,routes,labels,x2,y2,original,(x1,y1))
 independent=[[{(side+str(p),P.AXES):Q(1)} for p in range(112)] for side in ('X','Y')]
 expected=P.inverse_formula(R,routes,*independent)
 Replay.replay(P,word,routes,labels,*independent,expected)
 # The source-independent-current and original-input checks establish both sides
 # of the inverse under inherited routed/native algebra. No owner is commuted.
 controls=[]
 def reject(label,mutate):
  changed=deepcopy(word);mutate(changed)
  try:Replay.replay(P,changed,routes,labels,*independent,expected)
  except (ValueError,KeyError):controls.append(label);return
  raise ValueError('accepted mutant:'+label)
 reject('omit negative query line',lambda w:w.pop(next(i for i,e in enumerate(w) if e[:2]==['line','D'+str(P.U[0])])) )
 reject('wrong response sign',lambda w:w.__setitem__(next(i for i,e in enumerate(w) if e[:2]==['add','D'+str(P.A[0])]),['add','D'+str(P.A[0]),'F0','1/4']))
 reject('drop inverse response map',lambda w:w.pop(next(i for i,e in enumerate(w) if e[:2]==['map','D'+str(P.A[0])])) )
 reject('omit query affine shift',lambda w:w[next(i for i,e in enumerate(w) if e[:2]==['map','D'+str(P.U[0])])].append('omit_shift'))
 reject('remove temporary final clear',lambda w:w.pop(max(i for i,e in enumerate(w) if e[:2]==['clear','D'+str(P.U[0])])) )
 reject('borrowed output alias',lambda w:w.__setitem__(next(i for i,e in enumerate(w) if e[:2]==['add','W'+str(P.A[0])] and i>window['start']),['add','Y'+str(P.A[0]),'D'+str(P.A[0]),'1']))
 # Entry dirt: remove one query-copy clear (its ADD must not silently initialize).
 reject('omit owned-dirt clear',lambda w:w.pop(next(i for i,e in enumerate(w) if e[:2]==['clear','D'+str(P.U[0])])) )
 # All native recipe signs are inherited; source verifier exhausts real kernels.
 Native=load_module(HERE/'native.py','fusion_native')
 native=Native.kernel_checks(P,labels,word)
 try:Native.kernel_checks(P,labels,word,wrong_negative_offset=True)
 except ValueError:controls.append('wrong negative native wrapper offset')
 else:raise ValueError('accepted wrong negative wrapper offset')
 oldbill,newbill=invoice(old),invoice(word)
 need(newbill['line']==224 and newbill['map']==352,'native invoice')
 need(newbill['unit_ADD']==1920 and newbill['quarter_ADD']==896 and newbill['clear']==536,'scalar invoice')
 need(newbill['scalar_allowance']==27184,'full scalar allowance')
 need(newbill['unit_ADD']==counts['unit_ADD'] and newbill['quarter_ADD']==counts['quarter_ADD'],'interpreter invoice')
 B=load_module(HERE/'budget.py','local_budget');interval=B.show(B.moment(decoder_pair=224,retained_h8_pair=0))
 need(interval['decision']=='strict_fail','optimistic budget must reject224')
 result={'status':'PASS_QQ16_RECTANGULAR_FUTURE_CORRECTION','source_pins':pins,
  'output_contract':'All224 original x0/y0 arrays inF17;224currentXY borrowed untouched;noearlyrecords',
  'word_events':len(word),'word_sha256':hashlib.sha256(canonical(word)).hexdigest(),
  'source_window':{'start':window['start'],'stop_exclusive':window['stop_exclusive'],'old_invoice':invoice(window['old']),'new_invoice':invoice(window['new'])},
  'old_full_invoice':oldbill,'new_full_invoice':newbill,'native_lowering':native,
  'storage':{'owned_outputs':224,'additional_owned_full_cover_temporaries':112,'private_peak':16,'temporary_return':'all112zero inidentity','borrowed_current_fields':224,'early_retained_fields':0},
  'checks':{'independent_current_routed_arrays':224,'original_input_routed_arrays':224,'complete_frame_coordinates':73,'signed_rank1_native_basis_columns':native['basis_columns'],'signed_rank1_recipes':len(native['signed_rank_one_recipes']),'semantic_controls':controls},
  'conditional_budget':{'pair_decoder_H1':224,'H8':0,'moment':interval,'121':B.show(B.moment(decoder_pair=121,retained_h8_pair=0)),'122':B.show(B.moment(decoder_pair=122,retained_h8_pair=0))},
  'scope':'Local algebraic same-output improvement with paid primitive invoice.224H1isnotoptimality.Conditional fixedcoverage pair screen fails at the oldhypotheticalpairrate before positive physical overhead; not an actual-global rejection. Nochangedglobalincidence/familycoverage,precision,hosting orsupplier admission.'}
 return word,result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if a.write:need(not (HERE/'RESULT.json').exists() and not (HERE/'WORD.json').exists(),'refuse overwrite')
 word,result=compute()
 if a.write:
  need(not (HERE/'RESULT.json').exists() and not (HERE/'WORD.json').exists(),'refuse overwrite')
  (HERE/'WORD.json').write_text(json.dumps(word,separators=(',',':'))+'\n');(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:
  need(typed(json.loads((HERE/'WORD.json').read_text()))==typed(word),'whole word mismatch')
  need(typed(json.loads((HERE/'RESULT.json').read_text()))==typed(result),'whole typed receipt mismatch')
 print(result['status']);print(json.dumps(result['new_full_invoice'],sort_keys=True));print(result['conditional_budget']['moment'])
