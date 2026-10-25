#!/usr/bin/env python3
"""Exact rounded-operation DAG equivalence of PR3985 and PR4015.
Chris R / Clear1nsight, with OpenAI Codex assistance. Apache-2.0.
No inherited executable, native idealization, or reassociation is used.
"""
import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINNED = {
 'vendor/PR3985-WORD.json': 'a854f516f1d80635fb3414734f9e1c6d1251a5d79ef12e137c143fc6b0b51722',
 'vendor/PR4015-WORD.json': '272d8c1bd172c29044eb227ec6d67a882501250978234685e035158f4479aa58',
 'vendor/PR3652-PROOF.md': '0edd900b2bf312c532f0e5067cb27a14495bf0c8a2ccddd25073ef4c592989e4',
}

def need(ok, message):
 if not ok:
  raise ValueError(message)

def canon(value):
 return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def typed(value):
 if isinstance(value, dict):
  return ('dict', tuple((k, typed(v)) for k, v in sorted(value.items())))
 if isinstance(value, list):
  return ('list', tuple(map(typed, value)))
 return (type(value).__name__, value)

def authenticate():
 records = json.loads((HERE/'SOURCES.json').read_text())['files']
 seen = {}
 for row in records:
  if row['usage'] != 'input':
   continue
  raw = (ROOT/row['path']).read_bytes()
  need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash: '+row['path'])
  need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'source blob')
  seen[row['path']] = row['sha256']
 for name, expected in PINNED.items():
  raw = (HERE/name).read_bytes()
  need(hashlib.sha256(raw).hexdigest() == expected, 'retained source hash: '+name)
 return seen

class Arena:
 """Structural tuple equality, not digest equality, is the decision procedure."""
 def __init__(self):
  self.nodes = []
  self.ids = {}
 def make(self, key):
  if key not in self.ids:
   self.ids[key] = len(self.nodes)
   self.nodes.append(key)
  return self.ids[key]

def trace(word, arena, format_tag='common-format'):
 need(isinstance(word, list) and len(word) < 5000, 'word bounds')
 borrowed = {s+str(p) for s in ('X','Y') for p in range(112)}
 owned = {s+str(p) for s in ('Z','W','D') for p in range(112)}
 state = {n: arena.make(('input', n)) for n in sorted(borrowed)}
 original = dict(state)
 active = set(); zero = arena.make(('zero', format_tag))
 frames = {}; events = []; reads = []; initialized = set(); cuts = []
 def read(n, i):
  need(n in borrowed | owned | active, 'read ownership at '+str(i))
  need(n in state, 'read before CLEAR at '+str(i)+': '+n)
  reads.append((i, n))
  return state[n]
 for i, e in enumerate(word):
  need(isinstance(e, list) and e, 'event schema')
  op = e[0]
  if op == 'begin':
   need(len(e)==3 and not active and e[2] in (8,16), 'private begin')
   active = {s+str(k) for s in (('F','G') if e[2]==16 else ('F',)) for k in range(8)}
   for n in active:
    state.pop(n, None); frames.pop(n, None)
  elif op == 'end':
   need(len(active)==e[2], 'private end')
   need(all(state.get(n)==zero and frames.get(n)=='identity' for n in active), 'private zero/identity return')
   for n in active:
    state.pop(n); frames.pop(n)
   active = set()
  elif op == 'clear':
   need(len(e)==3 and e[1] in owned | active, 'CLEAR ownership')
   need(e[2] in ('current','wide','identity','query2') or e[2].startswith('hole'), 'CLEAR frame')
   state[e[1]] = zero; frames[e[1]] = e[2]; initialized.add(e[1])
  elif op == 'add':
   need(len(e)==4 and e[1] in owned | active and e[1]!=e[2], 'ADD ownership')
   need(e[3] in ('1','-1','1/4','-1/4'), 'ADD coefficient')
   state[e[1]] = arena.make(('add', format_tag, e[3], read(e[1],i), read(e[2],i)))
   events.append((i, e[1], state[e[1]]))
  elif op in ('line','map'):
   need(not active and e[1] in owned, 'native/map workspace overlap')
   if op=='line':
    need(len(e)==4 and type(e[2]) is int and 0<=e[2]<112 and e[3] in (-1,1), 'line schema')
   else:
    need(len(e)==5 and e[2] in (1,2) and type(e[3]) is int and 0<=e[3]<112 and type(e[4]) is bool, 'map schema')
   state[e[1]] = arena.make((op, format_tag, *e[2:], read(e[1],i)))
   events.append((i,e[1],state[e[1]]))
  elif op == 'checkpoint':
   need(not active, 'checkpoint private leak')
   cuts.append((i,{n:state[n] for n in sorted(owned) if n.startswith(('Z','W'))}))
  else:
   raise ValueError('unknown event '+str(e))
 need(not active, 'private leak')
 need(all(state[n]==v for n,v in original.items()), 'borrowed write')
 outputs = {s+str(p):state[s+str(p)] for s in ('Z','W') for p in range(112)}
 for n in owned:
  if n.startswith('D') and n in state:
   need(state[n]==zero and frames[n]=='identity', 'old temporary zero/identity return')
 return {'outputs':outputs,'events':events,'reads':reads,'cuts':cuts,'initialized':sorted(initialized)}

def compare(old, new):
 a = Arena(); left = trace(old,a); right = trace(new,a)
 need(left['outputs']==right['outputs'], 'output DAG mismatch')
 need([x[1] for x in left['cuts']]==[x[1] for x in right['cuts']], 'checkpoint DAG mismatch')
 buckets = defaultdict(deque)
 for i,d,n in right['events']:
  buckets[n].append((i,d))
 mapping=[]
 for i,d,n in left['events']:
  need(bool(buckets[n]), 'value-event DAG multiset mismatch')
  j,t=buckets[n].popleft();mapping.append([i,j,d,t,n])
 need(not any(buckets.values()), 'unmatched new value event')
 need(len(mapping)==3392, 'value-event census')
 # Complete instruction identities and occurrence multiplicity, not only roots.
 native_left=[(old[i][2:],n) for i,_,n in left['events'] if old[i][0]=='line']
 native_right=[(new[i][2:],n) for i,_,n in right['events'] if new[i][0]=='line']
 need(native_left==native_right, 'native sequence mismatch')
 return a,left,right,mapping

def signed(value, width, mode='trap'):
 lo,hi=-(1<<(width-1)),(1<<(width-1))-1
 if mode=='wrap':
  return (value-lo)%(1<<width)+lo
 if mode=='saturate':
  return min(hi,max(lo,value))
 need(lo<=value<=hi,'signed overflow')
 return value

def quarter(value, rounding):
 if rounding=='floor':
  return value//4
 if rounding=='trunc':
  return (1 if value>=0 else -1)*(abs(value)//4)
 raise ValueError('rounding policy')

def probes(old,new,mapping):
 paired={i:j for i,j,*_ in mapping}
 def stateful_signature(word):
  count=0;rows=[]
  for i,e in enumerate(word):
   if e[0]=='add':count+=1
   if e[0]=='line':rows.append((i,e[2:],count))
  return rows
 old_state,new_state=stateful_signature(old),stateful_signature(new)
 first=next((a,b) for a,b in zip(old_state,new_state) if a[2]!=b[2])
 need(first[0][0]==9 and first[1][0]==7 and first[0][2]==4 and first[1][2]==3,'first hidden-state divergence')
 stateful={'old_event':9,'new_event':7,'native_port':1,'sign':1,'old_prior_ADD_count':4,'new_prior_ADD_count':3,'example_hidden_additive_offset_mod2':[0,1],'scope':'Countermodel only: a kernel consulting global scalar-count parity violates declared-input determinism; not an observed defect of the actual native kernel.'}
 query=[i for i,e in enumerate(old) if e[0]=='add' and e[1]=='F0' and e[2].startswith('D')]
 need(old[query[0]]==['add','F0','D2','1'] and old[query[1]]==['add','F0','D9','1'], 'source-bound query fixture')
 qevent=next(i for i,e in enumerate(old) if e==['add','D0','F0','-1/4'])
 need(new[paired[qevent]][3]=='-1/4','paired quarter')
 try:signed(3+1,3)
 except ValueError:overflow=True
 else:overflow=False
 need(overflow and signed(3+1,4)==4,'overflow fixture')
 decisions=[]
 for x in range(-17,18):
  for y in range(-17,18):
   for c in (-1,1):
    for mode in ('floor','trunc'):
     product=quarter(c*y,mode)
     for width in (3,4,6):
      for overflow_mode in ('wrap','saturate'):
       v=signed(x+product,width,overflow_mode)
       # An independent exact-rational oracle checks signed rounding/overflow conventions.
       exact=Fraction(c*y,4)
       rounded=exact.numerator//exact.denominator if mode=='floor' else int(exact)
       total=x+rounded;lo,hi=-(1<<(width-1)),(1<<(width-1))-1
       if overflow_mode=='saturate':expected=max(lo,min(total,hi))
       else:
        bits=total & ((1<<width)-1);expected=bits-(1<<width) if bits & (1<<(width-1)) else bits
       need(v==expected,'signed rational oracle')
       decisions.append(v)
 need(quarter(-1,'floor')==-1 and quarter(-1,'trunc')==0,'signed quarter discrimination')
 return {'stateful_kernel_countermodel':stateful,'query_width_fixture':{'old_events':query[:2],'new_events':[paired[i] for i in query[:2]],'aligned_source_values':[3,1],'old_private_width':4,'new_owned_width':3,'after_first':[3,3],'after_second_old':4,'after_second_new':{'trap':'overflow','wrap':-4,'saturate':3},'scope':'Boundary primitive fixture at literal sites; no claim this is an admitted full producer trajectory.'},'quarter_policy_fixture':{'old_event':qevent,'new_event':paired[qevent],'coefficient':'-1/4','query_component':1,'initial_response':0,'product_floor':-1,'product_trunc':0,'scope':'Different primitive policies diverge; a common policy gives identical bits, without claiming exact division.'},'uniform_policy_control_decisions':len(decisions),'uniform_policy_control_sha256':hashlib.sha256(canon(decisions)).hexdigest()}

def compute():
 pins=authenticate()
 old=json.loads((HERE/'vendor/PR3985-WORD.json').read_text())
 new=json.loads((HERE/'vendor/PR4015-WORD.json').read_text())
 a,l,r,mapping=compare(old,new)
 controls=[]
 def reject(label,change):
  w=json.loads(json.dumps(new));change(w)
  try:compare(old,w)
  except (ValueError,KeyError):controls.append(label)
  else:raise ValueError('accepted mutant '+label)
 reject('missing first hosted query clear',lambda w:w.pop(next(i for i,e in enumerate(w) if e==['clear','Z1','query2'])))
 reject('missing recycled D clear',lambda w:w.pop([i for i,e in enumerate(w) if e==['clear','Z10','current']][1]))
 reject('early query clear',lambda w:w.insert(2580,['clear','Z1','query2']))
 reject('borrowed input clear',lambda w:w.insert(0,['clear','X0','current']))
 reject('missing deferred output copy',lambda w:w.pop(2601))
 reject('native hidden private overlap',lambda w:w.insert(1704,['begin','illegal',8]))
 reject('wrong signed native',lambda w:w.__setitem__(1707,['line','Z10',1,1]))
 reject('wrong quarter sign',lambda w:w.__setitem__(2585,[*w[2585][:3],'1/4']))
 # A commutative exact sum is not enough: swapping adjacent source additions is forbidden.
 def swap_query(w):
  i,j=[x for x,e in enumerate(w) if e[0]=='add' and e[1]=='Z1' and e[2]=='Z10'][:2]
  # Swap complete source copy/map/native/query runs, preserving all other primitive spellings.
  starts=[x for x,e in enumerate(w) if e==['clear','Z10','current']]
  x,y,z=starts[:3];w[x:z]=w[y:z]+w[x:y]
 reject('source accumulation order',swap_query)
 before,after=Counter(e[0] for e in old),Counter(e[0] for e in new)
 need(before['add']==after['add']==2816 and before['line']==after['line']==224 and before['map']==after['map']==352,'full arithmetic invoice')
 return {'status':'PASS_QQ16_ROUNDED_TRACE_EQUIVALENCE','canonical_inputs':pins,'retained_inputs':PINNED,'old_events':len(old),'new_events':len(new),'matched_value_events':len(mapping),'unique_structural_nodes':len(a.nodes),'event_mapping':mapping,'output_roots':l['outputs'],'checkpoint_event_pairs':[[x[0],y[0]] for x,y in zip(l['cuts'],r['cuts'])],'native_call_sequence_equal':True,'operation_counts':{'old':dict(sorted(before.items())),'new':dict(sorted(after.items()))},'removed_arithmetic_error_sites':0,'separate_stream_rescheduling_error_analysis_required_under_contract':False,'premise':'Common exact zero plus identical deterministic storage-independent ADD/map/native functions with identical argument order, widths, rounding/overflow policy and disjoint reset native workspace. No precision narrowing on persistent query stores. Whole-array primitives include actual ordered coordinate/native arithmetic.','format_binding':'PR3303/3652 certify only the literal F0/B1 producer. No retained3985 or4015 decoder width/range/interior certificate is supplied. Relative transfer only; PR2965 still needs epsD.','fixtures':probes(old,new,mapping),'semantic_controls':controls,'scope':'Exact operation DAG/occurrence equivalence under stated finite-primitive contract; not global chronological trace equality, decoder accuracy certification, physical movement tariff or supplier/kappa result.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 path=HERE/'RESULT.json'
 if args.write:need(not path.exists(),'refuse overwrite')
 result=compute()
 if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:need(typed(json.loads(path.read_text()))==typed(result),'whole typed receipt mismatch')
 print(result['status'])
 print(json.dumps({k:result[k] for k in ('matched_value_events','old_events','new_events','unique_structural_nodes','checkpoint_event_pairs','native_call_sequence_equal')},sort_keys=True))
if __name__=='__main__':main()
