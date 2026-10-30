"""Complete conditional A2 replay; zxv with substantial OpenAI Codex assistance. Apache-2.0."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import sys,json,gzip,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE/'inputs/pr5612'))
from sources import sources,load,need,read
L=load(HERE/'inputs/pr5627-local.py','local')
manifest=read(HERE/'SOURCES.json')
for item in manifest['retained_inputs']:
 raw=(HERE/item['local_path']).read_bytes()
 need(len(raw)==item['size'] and sha256(raw).hexdigest()==item['sha256'],'Retained source '+item['local_path'])
quick='--quick' in sys.argv
with sources() as (prior,framework):
 L.ROOT=framework
 bindings=[]
 manifest=read(HERE/'inputs/pr5627-SOURCES.json')
 for row in manifest['files']:
  path=framework/row['path']
  if path.is_file():
   need(sha256(path.read_bytes()).hexdigest()==row['sha256'],'Latest declared foundation equals authenticated framework: '+row['path'])
   bindings.append(row['path'])
 source=read(HERE/'inputs/pr5627-WORD.json.gz')
 from construct import construct
 payload,construction=construct()
 word=json.loads(payload)
 before=L.replay(source);local=L.replay(word)
 delta=Counter(local['paid']);delta.subtract(before['paid'])
 need({r:c for r,c in delta.items() if c}=={2:1,3:-1,5:-1,6:1},'Exact full paid-rank exchange')
 need(local['helpers']==before['helpers'],'All productive targets retained')
 print('PASS exact source foundation bindings',len(bindings),'and all arbitrary-input/frame rows',flush=True)
 if quick:
  print('PASS_P104_A2_QUICK',flush=True)
  raise SystemExit(0)
 original=(HERE/'inputs/pr5627-pricing.py').read_text()
 for before,after in read(HERE/'PRICING-EDITS.json'):
  need(original.count(before)==1,'Unique declared pricing edit');original=original.replace(before,after)
 need(original==(HERE/'pricing.py').read_text(),'Only declared pricing edits')
 transpose=L.reverse_columns(word)
 print('PASS all dense transpose columns',transpose['columns'],flush=True)
 native=L.native(word)
 print('PASS all signed native maps and exact phases',native['distinct_maps'],flush=True)
 C=load(framework/'research/p104-productive-controller/caller.py','new_a2_caller')
 caller=C.construct();need(caller==read(framework/'research/p104-productive-controller/CONTROLLER.json'),'Unchanged complete caller')
 physical=C.physical(caller,word)
 print('PASS complete physical caller',flush=True)
 P=load(HERE/'pricing.py','a2_new_price')
 price=P.run(local,native,caller,physical)
 print('PASS two exact moment engines, compiler, BIT stock and58 outer predicates',price['raw_root_interval'],flush=True)
 controls=C.controls(caller)
 def reject(f):
  try:f()
  except ValueError as e:return str(e)
  raise ValueError('Malformed control accepted')
 bad=deepcopy(word);gate=['ADD',340,715,'-4',396];need(bad['program'].count(gate)==1,'Unique new A2 correction');bad['program'].remove(gate)
 controls['missing_A2_correction']=reject(lambda:L.replay(bad))
 bad=deepcopy(word);index=bad['program'].index(gate);bad['program'][index][-1]=825
 controls['wrong_new_contact_frame']=reject(lambda:L.replay(bad))
 bad=deepcopy(local);bad['paid'][2]+=1;bad['paid'][3]-=1
 controls['undercharged_child']=reject(lambda:P.assemble(bad,native,caller,physical))
 result=P.encode({'status':'PASS_P104_A2_KAPPA_00310458','source_pr':5627,'source_head':'ed4dc88a09a7d201971f6603b8c2074e95dd9c32','source_foundation_matches':bindings,'local':local,'transpose':transpose,'native':native,'physical':physical,'complete_cost':price,'controls':controls})
expected=read(HERE/'RESULT.json')
for key in ('local','transpose','native','physical','complete_cost','controls'):
 need(result[key]==expected[key],'Exact saved complete receipt '+key)
print(result['status'],flush=True)
