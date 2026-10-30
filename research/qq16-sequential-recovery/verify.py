#!/usr/bin/env python3
"""Paired-source QQ16 recovery. Chris R / Clear1nsight with OpenAI; Apache-2.0.
Canonical decoder: ywz65 PR2707, Arham Tahir PR2681. See PREDECESSORS.json.
"""
import argparse,hashlib,json,types
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
STATUS='PASS_QQ16_PAIRED_SOURCE_RECOVERY'
def need(ok,why):
 if not ok:raise ValueError(why)
def unique_pairs(pairs):
 out={}
 for k,v in pairs:
  need(k not in out,'duplicate JSON key:'+k);out[k]=v
 return out
def parse(raw):return json.loads(raw,object_pairs_hook=unique_pairs)
def typed(x):
 if isinstance(x,dict):return ('dict',tuple((k,typed(v)) for k,v in sorted(x.items())))
 if isinstance(x,list):return ('list',tuple(map(typed,x)))
 return (type(x).__name__,x)
def module(path,name):
 m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def authenticate():
 raw=(HERE/'SOURCES.json').read_bytes()
 need(hashlib.sha256(raw).hexdigest()=='e92bb29a19f214f4bfa87d561c4be19747e17adeecc8d0ee97280cccb10b1457','source manifest integrity')
 pins={}
 for r in parse(raw)['files']:
  if r['usage']!='input':continue
  data=(ROOT/r['path']).read_bytes()
  need(hashlib.sha256(data).hexdigest()==r['sha256'],'source hash:'+r['path'])
  need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['git_blob'],'source blob:'+r['path'])
  pins[r['path']]=r['sha256']
 need(len(pins)==22,'complete canonical runtime input set')
 raw=(HERE/'PREDECESSORS.json').read_bytes()
 need(hashlib.sha256(raw).hexdigest()=='e1eab4b994bab3077f96bf943129bad2158e829426a12bb6e91ceee7b20d4271','predecessor manifest integrity')
 for r in parse(raw)['files']:
  if r['pr']==4015 and r['path'].endswith(('/replay.py','/native.py')):
   need(hashlib.sha256((HERE/Path(r['path']).name).read_bytes()).hexdigest()==r['sha256'],'copied executable integrity:'+r['path'])
 for pr,sha in [(3985,'a854f516f1d80635fb3414734f9e1c6d1251a5d79ef12e137c143fc6b0b51722'),(4015,'272d8c1bd172c29044eb227ec6d67a882501250978234685e035158f4479aa58')]:
  need(hashlib.sha256((HERE/f'vendor/PR{pr}-WORD.json').read_bytes()).hexdigest()==sha,'retained word integrity:'+str(pr))
 return pins
def compute():
 pins=authenticate() # All inherited runtime inputs bound before execution.
 L=module(ROOT/'research/qq16-line-normalized-decoder/verify.py','canonical_decoder')
 P,R,routes,labels,_=L.load_source()
 source=parse((ROOT/'research/qq16-line-normalized-decoder/WORD.json').read_text())
 need(typed(source)==typed(L.lower(P,R)),'canonical decoder regeneration')
 C=module(HERE/'construction.py','paired_construction');B=module(HERE/'cost.py','independent_cost')
 Replay=module(HERE/'replay.py','routed_replay');Native=module(HERE/'native.py','signed_native')
 Residual=module(HERE/'residual.py','ordered_residual')
 word,construction=C.construct(P,R,source)
 need(typed(parse((HERE/'WORD.json').read_text()))==typed(word),'whole word mismatch')
 need(typed(parse((HERE/'CONSTRUCTION.json').read_text()))==typed(construction),'construction receipt mismatch')
 ledger=B.compare(word,*[parse((HERE/f'vendor/PR{p}-WORD.json').read_text()) for p in (3985,4015)])
 bill=ledger['complete_literal_invoices']['candidate']
 need(tuple(bill[k] for k in ('scalar_allowance','unit_ADD','quarter_ADD','CLEAR','H1_children','cover_maps','native_wrappers','private_peak','word_events'))==(26144,1820,896,416,224,352,448,16,3713),'complete expected paid invoice')
 pairs=parse(json.dumps(B.pair_identity(R,[r['ports'] for r in construction['factoring']['pairs']],P.U+P.T)))
 need(pairs['query_unit_ADD_saving']==100,'pair improvement')
 acquisition=B.acquisition(source,P.U,P.T,P.A)
 selected=B.selected_acquisition(source,word,P.U,P.T,P.U[:10])
 preservation=B.preservation(source,word,P.U[:10])
 cost_controls=B.negative_controls(source,word,P.U,P.T,list(P.U[:10]))
 need(typed(parse((HERE/'ACQUISITION.json').read_text()))==typed(acquisition),'acquisition receipt mismatch')
 expected_ledger={'comparison':ledger,'pair_identity':pairs,'preservation':preservation,'selected_acquisition':selected,'negative_controls':cost_controls}
 need(typed(parse((HERE/'LEDGER.json').read_text()))==typed(expected_ledger),'ledger receipt mismatch')
 original=[[{(s+str(p),P.AXES):Q(1)} for p in range(112)] for s in ('x','y')]
 x2,y2,x1,y1=P.forward(R,routes,*original)
 counts=Replay.replay(P,word,routes,labels,x2,y2,original,(x1,y1))
 independent=[[{(s+str(p),P.AXES):Q(1)} for p in range(112)] for s in ('X','Y')]
 expected=P.inverse_formula(R,routes,*independent)
 Replay.replay(P,word,routes,labels,*independent,expected)
 need(counts['unit_ADD']==bill['unit_ADD'] and counts['quarter_ADD']==bill['quarter_ADD'],'independent interpreter invoice')
 residual=Residual.check(P,R,routes,labels,source,L)
 native=Native.kernel_checks(P,labels,word)
 controls=[]
 def reject(label,mutate):
  w=deepcopy(word);mutate(w)
  try:Replay.replay(P,w,routes,labels,*independent,expected)
  except (ValueError,KeyError):controls.append(label);return
  raise ValueError('accepted mutant:'+label)
 aliases=construction['hosting']['aliases'];d,e,q0=(aliases[x] for x in ('D','E','Q0'))
 reject('hold private query across native',lambda w:w.insert(w.index(['clear',q0,'query2']),['begin','illegal_query_hold',8]))
 reject('omit second source initialization',lambda w:w.pop(w.index(['clear',e,'current'])))
 reject('omit T native normalization',lambda w:w.pop(next(i for i,v in enumerate(w) if v[0]=='line' and v[2] in P.T and v[3]==-1)))
 reject('omit shared pair addition',lambda w:w.pop(w.index(['add',d,e,'1'])))
 def reorder(w):
  i=w.index(['add',d,e,'1']);w.insert(i-2,w.pop(i))
 reject('destructive sum before differing reads',reorder)
 reject('omit response inverse map',lambda w:w.pop(w.index(['map',d,2,P.A[0],True])))
 reject('omit tenth host restoration',lambda w:w.pop(construction['hosting']['restore_events'][e][1]))
 try:Native.kernel_checks(P,labels,word,wrong_negative_offset=True)
 except ValueError:controls.append('wrong negative native wrapper offset')
 else:raise ValueError('accepted wrong native wrapper offset')
 try:B.invoice([['add','a','b','1/2']])
 except ValueError:controls.append('unpriced scalar coefficient')
 else:raise ValueError('accepted unsupported tariff')
 return {'status':STATUS,'source_pins':pins,'word_sha256':hashlib.sha256((HERE/'WORD.json').read_bytes()).hexdigest(),
 'contract':'All224 original outputs F17; all224 borrowed current X/Y values and frames unchanged; arbitrary dirty owned storage; existing private scratch returned zero/identity.',
 'construction':construction,'ledger':ledger,'pair_identity':pairs,'acquisition':acquisition,'selected_acquisition':selected,'preservation':preservation,'residual':residual,'native_lowering':native,
 'validation':{'original_arrays':224,'arbitrary_current_arrays':224,'phase_coordinates':73,'semantic_controls':controls,'cost_controls':cost_controls},
 'storage':{'owned_outputs':224,'additional_owned':0,'deferred_output_hosts':10,'private_peak':16,'future_private_peak':0},
 'scope':'Exact logical scalar-allowance improvement800 vs PR4015,1040 vs PR3985. Arithmetic DAG changed; new numerical range/error proof required. Physical access, native workspace, supplier coverage, weighted recurrence and both caps unproved. No kappa change.'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();target=HERE/'RESULT.json'
 if a.write:need(not target.exists(),'refuse overwrite of existing receipt')
 result=compute()
 if a.write:
  with target.open('x') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:need(typed(parse(target.read_text()))==typed(result),'whole typed receipt mismatch')
 print(STATUS);print(json.dumps(result['ledger']['complete_literal_invoices']['candidate'],sort_keys=True))
if __name__=='__main__':main()
