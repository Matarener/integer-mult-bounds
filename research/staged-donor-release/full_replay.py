"""Portable complete release; fresh changed providers, explicit retained parent reuse."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,tarfile
P=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def tree(p,exclude=()):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f.relative_to(p).as_posix() not in exclude}
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def extract(target):
 pins=read(P/'REPLAY-INPUTS.json');archive=P/'REPLAY-INPUTS.tar.gz';need(sha(archive)==pins['archive_sha256'],'source archive pin');target.mkdir()
 with tarfile.open(archive) as tf:
  names=set()
  for m in tf:
   need(m.isfile() and m.name in pins['files'] and m.name not in names and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts,'source member')
   raw=tf.extractfile(m).read();need(hashlib.sha256(raw).hexdigest()==pins['files'][m.name],'source member hash');names.add(m.name);f=target/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
 need(names==set(pins['files']),'complete source archive')
 if (target/'V2-DERIVATION.json').exists():
  deriv=read(target/'V2-DERIVATION.json');v1=target/'_provenance/v1/source';oldmanifest=read(v1/'MANIFEST.json')
  need(sha(v1/'MANIFEST.json')==deriv['old_manifest'],'reused source predecessor manifest')
  current=read(target/'source/MANIFEST.json');need(set(current)-set(oldmanifest)==set(deriv['added_files']),'source addition coverage')
  for rel,h in oldmanifest.items():
   source=(v1/rel) if rel in deriv['modified_files'] else (target/'source'/rel)
   need(sha(source)==h,'reconstructed exact preparatory source '+rel)
 return target

def main():
 need(__debug__,'enabled assertions required');ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--reuse-current-native',action='store_true');ap.add_argument('--extract-only',action='store_true');a=ap.parse_args();work=a.work.resolve();need(not work.exists(),'fresh output required');work.mkdir();inputs=extract(work/'inputs')
 if a.extract_only:print('PASS_SELF_CONTAINED_SOURCE_EXPORT');return
 source=inputs/'source';cache=inputs/'native-cache';receipt=read(inputs/'NATIVE-RECEIPT.json');stages=[]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
 # Platform-neutral scientific command; optional APFS adapter only affects copies.
 env.pop('PYTHONPATH',None)
 def run(name,cmd):
  with (work/(name+'.log')).open('w') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
  stages.append(dict(name=name,command=cmd,exit_code=r.returncode,log_sha256=sha(work/(name+'.log'))));write(work/'STAGES.json',stages);need(r.returncode==0,'failed '+name+'; see '+str(work/(name+'.log')));print('PASS',name,flush=True)
 if not a.reuse_current_native:
  fresh=work/'native-cache';fresh.mkdir();newkeys={v['word_sha256'] for v in receipt['providers'].values()}
  for f in cache.iterdir():
   if f.name not in newkeys:shutil.copytree(f,fresh/f.name)
  for tag in ('base','extra'):
   word=source/'new/borrow/words'/f'BORROW-WORD-43{tag}.json.gz';out=work/('native-'+tag);run('fresh-native-'+tag,[sys.executable,'-B',str(source/'new/fastnative/run_native.py'),str(word),str(out)])
   res=read(out/'RESULT.json');need(res['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and res['word_sha256']==sha(word),'fresh native result');need(res['source_sha256']==read(P/'evidence'/('native-'+tag)/'RESULT.json')['source_sha256'],'same native scientific engine')
   entry=fresh/sha(word);shutil.copytree(out/'native',entry);write(entry/'CACHE.json',dict(word_sha256=sha(word),files=tree(entry)));receipt['providers'][tag]=dict(word_sha256=sha(word),complete_native_files=tree(entry,('CACHE.json',)))
  cache=fresh;receipt['cache_files']=tree(cache)
 native_receipt=work/'NATIVE-RECEIPT.json';write(native_receipt,receipt)
 cmd=[sys.executable,'-B',str(inputs/'admit.py')]
 for k,v in {'source':source,'fill':inputs/'FILL.json.gz','order':inputs/'ORDER.json','dispatch':inputs/'DISPATCH.json','native-cache':cache,'native-receipt':native_receipt,'work':work/'admission','replica-helper-dir':inputs/'helpers','reconstructor':inputs/'helpers/reconstruct_replica.py','comparison-claim':inputs/'PR2969-CLAIM.json','blocknorm-checker':inputs/'extension_blocknorm.py'}.items():cmd+=['--'+k,str(v)]
 cmd+=['--source-profile','staged3605','--comparison-profile','pr2969','--jobs','1'];run('complete-admission',cmd)
 result=read(work/'admission/RESULT.json');need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete release');need(result['profile']==read(P/'LEAD1-PRICE.json')['profile'],'exact full profile')
 from fractions import Fraction as Q
 exp=Q(read(P/'LEAD1-PRICE.json')['root_interval'][0])-Q(1,10**46)-Q(1,10**70);need(Q(result['kappa'])==exp,'exact endpoint');need(exp>Q(read(P/'sources/T360-PRICE.json')['root_interval'][1]),'strict current comparator gain')
 write(work/'RESULT.json',dict(status='PASS_DELAYED_RELEASE_COMPLETE_CONDITIONAL_RELEASE',kappa=str(exp),kappa_decimal=result['kappa_decimal'],reuse_current_native=a.reuse_current_native,retained_parent_reused=True,source_archive_sha256=sha(P/'REPLAY-INPUTS.tar.gz'),release_receipt_sha256=sha(work/'admission/release/RELEASE-RECEIPT.json'),scope=result['scope']))
 print('PASS_DELAYED_RELEASE_COMPLETE_CONDITIONAL_RELEASE',result['kappa_decimal'])
if __name__=='__main__':main()
