"""Full changed-native and original ordinary/outer release; retained ancestry reused."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,tarfile
P=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
def tree(p,exclude=()):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f.relative_to(p).as_posix() not in exclude}
def main():
 need(__debug__,'assertions enabled');ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--reuse-current-native',action='store_true');ap.add_argument('--extract-only',action='store_true');a=ap.parse_args();work=a.work.resolve();need(not work.exists(),'fresh work directory');work.mkdir()
 pins=read(P/'REPLAY-INPUTS.json');archive=P/'REPLAY-INPUTS.tar.gz';need(sha(archive)==pins['archive_sha256'],'source archive digest');inputs=work/'inputs';inputs.mkdir();seen=set()
 with tarfile.open(archive) as t:
  for m in t:
   need(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and m.name not in seen and m.name in pins['files'],'source member')
   raw=t.extractfile(m).read();need(hashlib.sha256(raw).hexdigest()==pins['files'][m.name],'source file digest');seen.add(m.name);f=inputs/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
 need(seen==set(pins['files']),'complete source inventory')
 if a.extract_only:print('PASS_STAGED544_SELF_CONTAINED_SOURCE_EXPORT',flush=True);return
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None)
 if os.name=='nt':env['PYTHONPATH']=str(P/'runtime')
 # Fail before any heavy work if the inherited exact-evidence dependency is wrong.
 subprocess.run([sys.executable,'-B','-c',"import numpy,scipy,sympy,mpmath; assert sympy.__version__=='1.14.0', 'requires sympy==1.14.0'"],env=env,check=True)
 stages=[]
 def run(name,cmd):
  with (work/(name+'.log')).open('w',encoding='utf-8',newline='\n') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
  stages.append(dict(name=name,exit_code=r.returncode,log_sha256=sha(work/(name+'.log'))));write(work/'STAGES.json',stages);need(r.returncode==0,'failed '+name+'; inspect its log');print('PASS',name,flush=True)
 source=inputs/'source';cache=inputs/'native-cache';receipt=read(inputs/'NATIVE-RECEIPT.json')
 if not a.reuse_current_native:
  fresh=work/'native-cache';fresh.mkdir();current={v['word_sha256'] for v in receipt['providers'].values()}
  for d in cache.iterdir():
   if d.name not in current:shutil.copytree(d,fresh/d.name)
  for tag in ('base','extra'):
   word=source/'new/borrow/words'/f'BORROW-WORD-43{tag}.json.gz';native=work/('native-'+tag)
   run('fresh-native-'+tag,[sys.executable,'-B',str(source/'new/fastnative/run_native.py'),str(word),str(native)])
   res=read(native/'RESULT.json');need(res['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and res['word_sha256']==sha(word),'fresh native binding')
   need(res['source_sha256']==read(P/'evidence'/f'NATIVE-{tag}.json')['source_sha256'],'native scientific source binding')
   entry=fresh/sha(word);shutil.copytree(native/'native',entry)
   for f in entry.rglob('*'):
    if f.is_file() and f.suffix in ('.json','.log','.txt'):f.write_bytes(f.read_bytes().replace(b'\r\n',b'\n'))
   write(entry/'CACHE.json',dict(word_sha256=sha(word),files=tree(entry)))
   receipt['providers'][tag]=dict(word_sha256=sha(word),complete_native_files=tree(entry,('CACHE.json',)))
  cache=fresh;receipt['cache_files']=tree(cache)
 native_receipt=work/'NATIVE-RECEIPT.json';write(native_receipt,receipt)
 cmd=[sys.executable,'-B',str(inputs/'admit544.py')]
 for k,v in {'source':source,'fill':P/'inputs/FILL.json.gz','order':P/'inputs/ORDER.json','dispatch':P/'inputs/DISPATCH.json','native-cache':cache,'native-receipt':native_receipt,'work':work/'admission','replica-helper-dir':inputs/'helpers','reconstructor':inputs/'helpers/reconstruct_replica.py','comparison-claim':P/'inputs/PR3682-CLAIM.json','blocknorm-checker':inputs/'extension_blocknorm.py'}.items():cmd+=['--'+k,str(v)]
 cmd+=['--source-profile','staged544','--comparison-profile','pr3682','--jobs','1'];run('complete-admission',cmd)
 result=read(work/'admission/RESULT.json');need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete release')
 from fractions import Fraction as Q
 expected=Q(read(P/'PRICE.json')['root_lower'])-Q(1,10**46)-Q(1,10**70)
 need(Q(result['kappa'])==expected and result['profile']==read(P/'PRICE.json')['profile'],'exact headline and full profile')
 write(work/'RESULT.json',dict(status='PASS_STAGED544_COMPLETE_CONDITIONAL_RELEASE',kappa=str(expected),reuse_current_native=a.reuse_current_native,retained_ancestry_reused=True,release_receipt_sha256=sha(work/'admission/release/RELEASE-RECEIPT.json')));print('PASS_STAGED544_COMPLETE_CONDITIONAL_RELEASE',flush=True)
if __name__=='__main__':main()
