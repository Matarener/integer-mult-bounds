"""Full exact PR5643/PR5644 composition replay.

Prepared for zxv with substantial OpenAI Codex assistance; Apache-2.0.
Ali Romman's cleanup constructor/checker and all P104, native, controller,
compiler, BIT and analytic notices remain. The A2 identity retains its earlier
Chris R/Clear1nsight, ToikY and scoped-audit attribution.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from hashlib import sha256,sha1
import argparse,gzip,importlib.util,json,sys,tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
A2=HERE/'inputs/pr5643'
CLEANUP=HERE/'inputs/pr5644'
REPLAY_SOURCES_SHA256='a2b96619a65cfdd99d6651d65626793f27e6a7fbc13e97f01d66b7634817fc92'
A2_PAYLOAD='c7545eab4e1394ba942a7ac8e4d70860d172cabda151a559fd566478aa38204b'
COMPOSED_PAYLOAD='42fe73e3240340aa185aab3cf976f8f6b783603b4d5513345519a260c1253d4a'

def need(ok,why):
 if not ok:raise ValueError(why)
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def read(path):
 raw=path.read_bytes();return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)
def blob(raw):return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def check_bytes(raw,row):
 need(len(raw)==row['size'] and sha256(raw).hexdigest()==row['sha256'],'Exact retained source SHA256 '+row.get('path',row.get('local_path','')))
 if 'git_blob'in row:need(blob(raw)==row['git_blob'],'Exact retained source Git blob')
def authenticate():
 raw=(HERE/'REPLAY-SOURCES.json').read_bytes()
 need(sha256(raw).hexdigest()==REPLAY_SOURCES_SHA256,'Frozen exact retained source inventory')
 pins=json.loads(raw)
 need(pins['sources']=={'pr5643':'a3ff5c628bfc8825553d62d913f3e91f75d6825f','pr5644':'c5871955d89bf73506fd68b0a5bf1cf2b3153c02'},'Exact submitted source heads')
 for row in pins['files']:check_bytes((HERE/row['local_path']).read_bytes(),row)
 need(sha256(gzip.decompress((A2/'WORD.json.gz').read_bytes())).hexdigest()==A2_PAYLOAD,'Exact submitted A2 candidate payload')
 return pins

def changes(a,b):
 d=Counter(a);d.subtract(b);return{r:c for r,c in d.items()if c}
def reject(f):
 try:f()
 except ValueError as e:return str(e)
 raise ValueError('Malformed composition control accepted')
def make_word(L,C):
 A=load(A2/'construct.py','retained_a2_construct')
 a2_payload,_=A.construct()
 need(a2_payload==gzip.decompress((A2/'WORD.json.gz').read_bytes()),'Exact PR5643 regeneration')
 a2,source=json.loads(a2_payload),read(A2/'inputs/pr5627-WORD.json.gz')
 witnesses=read(CLEANUP/'WITNESS.json')
 cleaned,_,_=C.construct(source,witnesses,L)
 need(cleaned==read(CLEANUP/'WORD.json.gz'),'Exact PR5644 reconstruction')
 word,receipts,local=C.construct(a2,witnesses,L)
 word['schema']='p104-a2-helper-cleanup-composition/1'
 payload=json.dumps(word,separators=(',',':')).encode()
 need(sha256(payload).hexdigest()==COMPOSED_PAYLOAD,'Entire composed candidate payload')
 need(gzip.decompress((HERE/'WORD.json.gz').read_bytes())==payload,'Saved composed payload')
 old={name:L.replay(w)for name,w in [('pr5627',source),('pr5643',a2),('pr5644',cleaned)]}
 need(changes(local['paid'],old['pr5644']['paid'])=={2:1,3:-1,5:-1,6:1},'A2 paid exchange survives all cleanup edits')
 need(changes(local['paid'],old['pr5643']['paid'])=={1:-3,5:-3,6:3},'Three cleanup paid exchanges survive A2')
 need(all(local['helpers']==x['helpers']for x in old.values()),'Every target retained against all sources')
 need(all(word[k]==a2[k]for k in ('public','owned_fields','initial','final','ports','live','frames')),'All endpoint/native boundary inventories retained')
 need(C.owned_events(word)==C.owned_events(a2),'All owned instructions and order retained')
 need(local['real_scalar_allowance']==220220,'All additional ordinary work included')
 return word,receipts,local,old,witnesses

def run(quick=False):
 authenticate()
 S=load(CLEANUP/'sources.py','composition_framework_sources')
 L=load(A2/'inputs/pr5627-local.py','local')
 C=load(CLEANUP/'construct.py','retained_cleanup')
 word,receipts,local,old,witnesses=make_word(L,C)
 print('PASS actual common word: all arbitrary-input rows, frames, fixed boundaries and full local paid-target delta',flush=True)
 if quick:return {'status':'PASS_P104_COMPOSITION_QUICK'}
 with S.sources()as(prior,framework):
  L.ROOT=framework
  foundation=[]
  need((prior/'local.py').read_bytes()==(A2/'inputs/pr5627-local.py').read_bytes(),'Identical exported PR5627 local checker')
  for row in read(prior/'SOURCES.json')['files']:
   path=framework/row['path']
   if path.is_file():
    need(sha256(path.read_bytes()).hexdigest()==row['sha256'],'Exact scientific foundation '+row['path']);foundation.append(row['path'])
  need(len(foundation)==19,'Complete retained manifest rows available in exact export')
  transpose=L.reverse_columns(word)
  print('PASS every dense transpose column',transpose['columns'],flush=True)
  native=L.native(word)
  print('PASS every native map and exact phase',native['distinct_maps'],flush=True)
  caller_module=load(framework/'research/p104-productive-controller/caller.py','composed_caller')
  caller=caller_module.construct()
  need(caller==read(framework/'research/p104-productive-controller/CONTROLLER.json'),'Exact retained complete caller')
  physical=caller_module.physical(caller,word)
  print('PASS full composed physical caller',flush=True)
  original=(CLEANUP/'pricing.py').read_text()
  edits=[("Q('.00310626335'), Q('.003106263355')","Q('.00310644468'), Q('.003106444685')"),("PREVIOUS = Q('.00310440546')","PREVIOUS = Q('.00310626335')"),("'kappa_decimal':'.00310626335'","'kappa_decimal':'.00310644468'")]
  for before,after in edits:
   need(original.count(before)==1,'One literal price adaptation');original=original.replace(before,after)
  need((HERE/'pricing.py').read_text()==original,'No changed mathematical pricing predicate')
  P=load(HERE/'pricing.py','composed_price')
  price=P.run(local,native,caller,physical)
  print('PASS two exact moment engines, compiler, BIT stock and all58 outer conditions',price['raw_root_interval'],flush=True)
  controls=caller_module.controls(caller)
  bad=deepcopy(witnesses[0]);key=next(iter(bad['cancel']));bad['cancel'][key]=str(L.Q(bad['cancel'][key])+1)
  controls['false_cleanup_cancellation']=reject(lambda:C.relation(read(A2/'WORD.json.gz'),bad,L))
  bad=deepcopy(witnesses[0]);bad['cut']+=1
  controls['wrong_cleanup_cut']=reject(lambda:C.relation(read(A2/'WORD.json.gz'),bad,L))
  bad=deepcopy(word);bad['program'].pop(0)
  controls['missing_input_basis']=reject(lambda:L.replay(bad))
  gate=['ADD',340,715,'-4',396]
  bad=deepcopy(word);need(bad['program'].count(gate)==1,'Unique A2 correction');bad['program'].remove(gate)
  controls['missing_A2_correction']=reject(lambda:L.replay(bad))
  bad=deepcopy(word);i=bad['program'].index(gate);bad['program'][i][-1]=825
  controls['wrong_A2_contact_frame']=reject(lambda:L.replay(bad))
  bad=deepcopy(word);bad['program'].pop(max(i for i,e in enumerate(bad['program'])if e[0]=='CLEAR'))
  controls['missing_owned_erasure']=reject(lambda:L.replay(bad))
  bad=deepcopy(local);bad['helpers'][1]+=1
  controls['extra_target_credit']=reject(lambda:P.assemble(bad,native,caller,physical))
  bad=deepcopy(local);bad['paid'][1]-=1
  controls['unpaid_query']=reject(lambda:P.assemble(bad,native,caller,physical))
  bad=deepcopy(local);bad['paid'][2]+=1;bad['paid'][3]-=1
  controls['undercharged_A2_child']=reject(lambda:P.assemble(bad,native,caller,physical))
  # Byte-mutation controls use temporary bytes; immutable source files are never changed.
  for row in read(HERE/'REPLAY-SOURCES.json')['files']:
   raw=(HERE/row['local_path']).read_bytes()
   if raw:
    controls['source_byte_mutation_'+row['local_path']]=reject(lambda raw=raw,row=row:check_bytes(bytes([raw[0]^1])+raw[1:],row))
  result=P.encode({'status':'PASS_P104_COMPOSED_KAPPA_00310644468','sources':{'pr5643':'a3ff5c628bfc8825553d62d913f3e91f75d6825f','pr5644':'c5871955d89bf73506fd68b0a5bf1cf2b3153c02'},'foundation_files':foundation,'local':local,'previous_local':old,'cleanup_changes':receipts,'delta_vs_pr5627':changes(local['paid'],old['pr5627']['paid']),'delta_vs_pr5643':changes(local['paid'],old['pr5643']['paid']),'delta_vs_pr5644':changes(local['paid'],old['pr5644']['paid']),'target_delta':{},'transpose':transpose,'native':native,'physical':physical,'complete_cost':price,'controls':controls,'candidate_payload_sha256':COMPOSED_PAYLOAD})
 return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--quick',action='store_true');ap.add_argument('--write',action='store_true');args=ap.parse_args()
 with tempfile.TemporaryDirectory(prefix='p104-compose-bytecode-')as cache:
  sys.pycache_prefix=cache;result=run(args.quick)
 if not args.quick:
  target=HERE/'FULL-RESULT.json'
  if args.write:target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
  else:need(read(target)==result,'Exact saved complete composition receipt')
 print(result['status'],flush=True)
if __name__=='__main__':main()
