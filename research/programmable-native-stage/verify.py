"""Authenticate and replay constructive native-stage interfaces. Apache-2.0."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys,secrets
ROOT=Path(__file__).resolve().parent
def need(ok,msg):
 if not ok:raise ValueError(msg)
def integrity():
 records=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf8'))['files'];expected={r['path']:r for r in records}
 actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}-{'MANIFEST.json'}
 need(actual==set(expected),'Package inventory differs')
 for name,r in expected.items():
  p=Path(name);need(not p.is_absolute() and '..'not in p.parts,'Unsafe path');raw=(ROOT/p).read_bytes();need(len(raw)==r['size'] and sha256(raw).hexdigest()==r['sha256'],'Changed bytes: '+name)
 return len(expected)+1
def main():
 count=integrity();checks=[]
 for name in ['native/verify_intertwiners.py','native/programmable_stage.py','fusion/verify.py','precision/verify.py']:
  cache=ROOT/('.bytecode-'+secrets.token_hex(16));need(not cache.exists(),'Fresh bytecode namespace required')
  argv=[sys.executable,'-I','-B','-X','pycache_prefix='+str(cache)]+(['-O']if not __debug__ else[])+[str(ROOT/name)]
  p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
  if p.returncode:
   sys.stderr.buffer.write(p.stderr);sys.stdout.buffer.write(p.stdout);raise RuntimeError('Scientific check failed: '+name)
  checks.append({'component':name,'status':'PASS'})
 print(json.dumps({'status':'PASS_PROGRAMMABLE_NATIVE_STAGE','files':count,'optimized':not __debug__,'checks':checks,'new_kappa':False},indent=2))
if __name__=='__main__':main()
