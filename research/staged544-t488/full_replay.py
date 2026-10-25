# SPDX-License-Identifier: Apache-2.0
"""Complete fresh allocation and ordinary/outer release with authenticated native reuse.
Both unchanged native providers and retained ancestry are explicitly reused from PR3734.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,sys,tarfile,types
P=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 need(__debug__,'assertions enabled');ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--jobs',type=int,default=1);a=ap.parse_args();work=a.work.resolve();need(not work.exists() and a.jobs>0,'fresh work and positive jobs')
 v=types.ModuleType('package_verify');v.__dict__['__file__']=str(P/'verify.py');exec(compile((P/'verify.py').read_bytes(),str(P/'verify.py'),'exec'),v.__dict__);v.authenticate()
 subprocess.run([sys.executable,'-B','-c',"import numpy,scipy,sympy,mpmath; assert sympy.__version__=='1.14.0'"],check=True)
 work.mkdir(parents=True);inputs=work/'inputs';inputs.mkdir();meta=read(P/'source3734/REPLAY-INPUTS.json');archive=P/'source3734/REPLAY-INPUTS.tar.gz';need(sha(archive)==meta['archive_sha256'],'archive pin');seen=set()
 with tarfile.open(archive)as t:
  for m in t:
   need(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and m.name not in seen and m.name in meta['files'],'archive member')
   raw=t.extractfile(m).read();need(hashlib.sha256(raw).hexdigest()==meta['files'][m.name],'source member pin');seen.add(m.name);f=inputs/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
 need(seen==set(meta['files']),'complete archive inventory')
 cmd=[sys.executable,'-B',str(P/'admit_t488.py')]
 params={'source':inputs/'source','fill':P/'inputs/FILL.json.gz','order':P/'inputs/ORDER.json','dispatch':P/'inputs/DISPATCH.json','native-cache':inputs/'native-cache','native-receipt':inputs/'NATIVE-RECEIPT.json','work':work/'admission','replica-helper-dir':inputs/'helpers','reconstructor':inputs/'helpers/reconstruct_replica.py','comparison-claim':P/'source3734/CLAIM.json','blocknorm-checker':inputs/'extension_blocknorm.py'}
 for k,path in params.items():cmd+=['--'+k,str(path)]
 cmd+=['--source-profile','staged544','--comparison-profile','pr3734','--jobs',str(a.jobs)]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None)
 with (work/'admission.log').open('w')as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
 need(r.returncode==0,'complete admission failed; inspect admission.log')
 result=read(work/'admission/RESULT.json');price=read(P/'evidence/PRICE.json');endpoint=Q(price['root_lower'])-Q(1,10**46)-Q(1,10**70);native=read(inputs/'NATIVE-RECEIPT.json');v.check_release(result,endpoint,{int(k):n for k,n in price['profile'].items()},native['manifest_sha256'],sha(inputs/'NATIVE-RECEIPT.json'))
 receipt={'status':'PASS_T488_COMPLETE_CONDITIONAL_RELEASE','kappa':str(endpoint),'native_and_ancestry_reused':True,'changed_allocation_and_release_fresh':True,'admission_result_sha256':sha(work/'admission/RESULT.json')};(work/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],str(endpoint),flush=True)
if __name__=='__main__':main()
