#!/usr/bin/env python3
"""Two explicit dirty-ancilla QQ16 schedules; no global admission. Apache-2.0.
Chris R / Clear1nsight with substantial OpenAI assistance.
Canonical native/replay lineage: ywz65 PR2707 and Arham Tahir PR2681.
"""
import argparse,hashlib,json,types
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from copy import deepcopy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,why):
 if not ok:raise ValueError(why)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def module(path):
 m=types.ModuleType(path.stem);m.__file__=str(path)
 exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def authenticate():
 need(hashlib.sha256((HERE/'SOURCES.json').read_bytes()).hexdigest()=='e07c9ced6625c59a74cf18ffb39d1836f09b99cad7dea431ac3f631535c5a6dd','source manifest binding')
 need(hashlib.sha256((HERE/'PREDECESSORS.json').read_bytes()).hexdigest()=='ba001c9783f21e3031137539b00bd89428a4505852147d3b320e161f21ac4d94','predecessor manifest binding')
 data=json.loads((HERE/'SOURCES.json').read_text())
 for p in data['files']:
  if p['usage']!='input':continue
  raw=(ROOT/p['path']).read_bytes()
  need(hashlib.sha256(raw).hexdigest()==p['sha256'],'source SHA256')
  need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==p['git_blob'],'source Git blob')
 for p in json.loads((HERE/'PREDECESSORS.json').read_text())['retained_data']:
  raw=(HERE/p['local_path']).read_bytes()
  need(hashlib.sha256(raw).hexdigest()==p['sha256'],'retained SHA256')
  need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==p['git_blob'],'retained Git blob')
 return {p['path']:p['sha256'] for p in data['files'] if p['usage']=='input'}
def invoice(w):
 c=Counter(e[0] for e in w)
 for e in w:
  if e[0]=='add':
   q=abs(Q(e[3]));need(q in (1,Q(1,4)),'unpriced coefficient');c['unit_ADD' if q==1 else 'quarter_ADD']+=1
 c['native_wrappers']=2*c['line'];c['scalar_allowance']=8*c['unit_ADD']+12*c['quarter_ADD']+2*c['clear']
 return dict(sorted(c.items()))
def construct(P,R,old,pivot=False):
 lo=next(i for i,e in enumerate(old) if e[0]=='map' and e[2]==2)
 hi=max(i for i,e in enumerate(old) if e[0]=='map' and e[2]==2)+1
 w=[];marks={}
 def emit(*x):w.append(list(x))
 def align(n,p,inverse):
  if inverse:emit('line',n,p,1);emit('map',n,2,p,True)
  else:emit('map',n,2,p,False);emit('line',n,p,-1)
 def addquery(n,p,sign):
  for k in range(8):
   if R[k][p]:emit('add','Q'+str(k),n,str(sign*R[k][p]))
 def response(sign):
  for p in P.A:
   for k in range(8):
    if R[k][p]:emit('add','S','Q'+str(k),str(R[k][p]/4))
   align('S',p,True);emit('add','W'+str(p),'S',str(sign));align('S',p,False)
   for k in range(8):
    if R[k][p]:emit('add','S','Q'+str(k),str(-R[k][p]/4))
 def query(sign):
  for p in P.U+P.T:
   if pivot:
    if sign==1:align('W'+str(p),p,False)
    addquery('W'+str(p),p,sign)
    if sign==-1:align('W'+str(p),p,True)
   else:
    addquery('S',p,-sign);align('S',p,True)
    emit('add','S','W'+str(p),'1');align('S',p,False);addquery('S',p,sign)
    align('S',p,True);emit('add','S','W'+str(p),'-1');align('S',p,False)
 marks['response_before']=len(w);response(1);marks['compute_query']=len(w)
 query(1);marks['response_after']=len(w);response(-1);marks['uncompute_query']=len(w)
 query(-1);marks['end']=len(w)
 need(not any(e[0]=='clear' for e in w),'no clear in dirty block')
 if not pivot:need(not any(e[1].startswith('W') and int(e[1][1:]) in P.U+P.T for e in w),'query W never modified')
 return old[:lo]+w+old[hi:],{'start':lo,'stop_exclusive':hi,'marks':marks,'old_invoice':invoice(old[lo:hi]),'block_invoice':invoice(w)},w

def compute():
 pins=authenticate();L=module(ROOT/'research/qq16-line-normalized-decoder/verify.py');P,R,routes,labels,_=L.load_source()
 old=json.loads((ROOT/'research/qq16-line-normalized-decoder/WORD.json').read_text());need(canonical(old)==canonical(L.lower(P,R)),'original regeneration')
 V=module(HERE/'replay.py')
 original=[[{(side+str(p),P.AXES):Q(1)} for p in range(112)] for side in ('x','y')]
 x2,y2,x1,y1=P.forward(R,routes,*original)
 independent=[[{(side+str(p),P.AXES):Q(1)} for p in range(112)] for side in ('X','Y')]
 expected=P.inverse_formula(R,routes,*independent)
 result={};words={}
 for pivot,name in [(False,'fixed_query_frame'),(True,'aligned_query_pivot')]:
  word,window,block=construct(P,R,old,pivot)
  V.replay(P,word,routes,labels,x2,y2,original,(x1,y1))
  counts=V.replay(P,word,routes,labels,*independent,expected)
  bill=invoice(word);need(bill['line']==(352 if pivot else 976),'full native invoice')
  need(counts['unit_ADD']==bill['unit_ADD'] and counts['quarter_ADD']==bill['quarter_ADD'],'interpreter invoice')
  result[name]={'window':window,'full_invoice':bill,'word_events':len(word),'word_sha256':hashlib.sha256(canonical(word).encode()).hexdigest()};words[name]=word
 # Dirty terms are independent symbols throughout; all9 returned before exit.
 controls=[]
 def reject(label,mutate,name='fixed_query_frame'):
  w=deepcopy(words[name]);mutate(w,result[name]['window'])
  try:V.replay(P,w,routes,labels,*independent,expected)
  except (ValueError,KeyError):controls.append(label);return
  raise ValueError('accepted mutant:'+label)
 reject('clear borrowed query',lambda w,z:w.insert(z['start'],['clear','Q0','query2']))
 reject('omit old-dirt response',lambda w,z:w.__delitem__(slice(z['start'],z['start']+z['marks']['compute_query'])))
 reject('omit query uncompute',lambda w,z:w.__delitem__(slice(z['start']+z['marks']['uncompute_query'],z['start']+z['marks']['end'])))
 reject('omit dirty scratch subtraction',lambda w,z:w.pop(next(i for i in range(z['start'],z['start']+z['marks']['end']) if w[i]==['add','S','W'+str(P.U[0]),'-1'])))
 reject('omit affine payload shift',lambda w,z:w[next(i for i in range(z['start'],z['start']+z['marks']['end']) if w[i][0]=='map')].append('omit_shift'))
 reject('wrong after-response sign',lambda w,z:w.__setitem__(next(i for i in range(z['start']+z['marks']['response_after'],z['start']+z['marks']['uncompute_query']) if w[i][:2]==['add','W'+str(P.A[0])]),['add','W'+str(P.A[0]),'S','1']))
 native=L.kernel_checks(P,labels,old)
 signed={(r['port'],r['sign']) for r in native['signed_rank_one_recipes']}
 for word in words.values():need(all((e[2],e[3]) in signed for e in word if e[0]=='line'),'signed recipe binding')
 baseline_word=json.loads((HERE/'vendor/pr3985/WORD.json').read_text())
 baseline=json.loads((HERE/'vendor/pr3985/RESULT.json').read_text())
 need(invoice(baseline_word)==baseline['new_full_invoice'],'retained224 invoice')
 need(len({e[1] for e in baseline_word if e[1].startswith('D')})==112,'retained ownedD inventory')
 cap=json.loads((HERE/'vendor/pr3976/RESULT.json').read_text())['conditional_screens']['strict_integer_native_H1_cap_per_stage1_module']
 need(cap==553 and result['fixed_query_frame']['full_invoice']['line']>cap,'conditional native-cap comparison')
 witness_port=next(p for p in P.A if R[0][p])
 result.update(dirty_baseline_witness={'initial_Q0':'constant1','other_Q_and_S':'zero','query_source_W_J':'zero','missing_positive_response_future_W_port':witness_port,'spurious_future_W_constant':str(-R[0][witness_port]/4),'meaning':'If the first response is omitted, Q dirt reaches this A output even when the desired query is zero.'},rectangular_baseline_invoice=invoice(baseline_word),conditional_cap_comparison={'cap':cap,'fixed_native':976,'excess':976-cap,'scope':'PR3976 fixedcoverage553 screen only; not globaladmission or universalminimum'},status='PASS_QQ16_DIRTY_COMMUTATOR no_new_kappa',source_pins=pins,old_full_invoice=invoice(old),
  borrowed_contract={'extra_full_cover_banks':9,'entry_and_return_frame':'F16 axes9..24','contents':'arbitrary independent; restored exactly','clear_operations':0,'additional_owned_full_cover_temporaries':0,'unchanged_owned_outputs':224,'unchanged_private_peak':16},
  verification={'independent_current_fields':224,'original_input_fields':224,'independent_auxiliary_dirt':9,'phase_coordinates':73,'signed_native_columns':native['basis_columns'],'semantic_controls':controls},
  decision='Fixed-query-frame dirty replacement costs976H1, exceeds PR3976 conditional553cap. Aligned-query pivot costs352H1, is dominated by original336H1 zero-D word in native/additional-owned storage counts; no improved decoder or global kappa claimed.')
 return words,result

def check_receipts(words,result):
 need(canonical(json.loads((HERE/'WORDS.json').read_text()))==canonical(words),'whole words mismatch')
 need(canonical(json.loads((HERE/'RESULT.json').read_text()))==canonical(result),'whole typed result mismatch')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 if args.write:need(not (HERE/'WORDS.json').exists() and not (HERE/'RESULT.json').exists(),'refuse overwrite')
 words,result=compute()
 if args.write:
  need(not (HERE/'RESULT.json').exists() and not (HERE/'WORDS.json').exists(),'refuse overwrite')
  (HERE/'WORDS.json').write_text(json.dumps(words,separators=(',',':'))+'\n');(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:check_receipts(words,result)
 print(result['status']);print(json.dumps({k:result[k]['full_invoice'] for k in words},sort_keys=True))
if __name__=='__main__':main()
