"""Normal/optimized read-only science replay; transient logs outside packet."""
import argparse,concurrent.futures,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
CASES=[['e_adapter.py'],['owned_e.py'],['n3.py'],['backward512.py'],['checkpoint120.py','--mode','base120'],['checkpoint120.py','--mode','root512'],['modes120.py'],['macros120.py'],['precision120.py']]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--jobs',type=int,default=1);a=ap.parse_args();logdir=Path(tempfile.mkdtemp(prefix='full-e8-E120-normal-O-'))
 def run(item):
  optimized,args=item;flags=['-O']if optimized else[];cmd=[sys.executable,*flags,'-I','-B',*args];r=subprocess.run(cmd,cwd=HERE,capture_output=True)
  key=('-'.join(args)).replace('/','_')+('-O'if optimized else'-normal');(logdir/(key+'.stdout')).write_bytes(r.stdout);(logdir/(key+'.stderr')).write_bytes(r.stderr)
  if r.returncode:raise RuntimeError(str(cmd)+' failed; logs '+str(logdir)+' '+r.stderr.decode(errors='replace')[-2000:])
  return {'command':['python3',*flags,'-I','-B',*args],'returncode':r.returncode,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest()}
 items=[(o,args)for args in CASES for o in[False,True]]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs)as pool:results=list(pool.map(run,items))
 r={'schema':'full120-E-positive-science-normal-O-replay/v1','status':'PASS_ALL18_READONLY_SCIENCE_REPLAYS','cases':results,'no_scientific_assertions_required':True,'scope':'Read-only exact recomputation against retained receipts and primitive payloads; no negative terminal decoder or caller admission.'}
 if a.write:(HERE/'REPLAY.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 else:
  old=json.loads((HERE/'REPLAY.json').read_bytes())
  if old!=r:raise ValueError('read-only replay report mismatch')
 print(r['status']);print('transient_logs='+str(logdir))
if __name__=='__main__':main()
