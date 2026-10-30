"""Isolated source-authenticated replay helpers; standard library only."""
from pathlib import Path
import gzip,hashlib,json,os,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
def need(c,m):
 if not c:raise ValueError(m)
def inventory(root):return sorted(p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'and p.relative_to(root).as_posix()!='MANIFEST.json')
def authenticate():
 m=json.loads((HERE/'MANIFEST.json').read_bytes());rows=m['files'];need(inventory(HERE)==sorted(x['path']for x in rows),'Complete package file inventory')
 for x in rows:
  p=HERE/x['path'];need(p.resolve().is_relative_to(HERE.resolve())and not p.is_symlink(),'Regular contained source')
  b=p.read_bytes();need(len(b)==x['bytes']and hashlib.sha256(b).hexdigest()==x['sha256'],'Source hash '+x['path'])
 return m
def canonical(x):
 if isinstance(x,dict):return{k:canonical(v)for k,v in x.items()if k not in('CPU_seconds','at_utc')}
 if isinstance(x,list):return[canonical(v)for v in x]
 return x
def read(path):return json.loads(gzip.decompress(path.read_bytes())if path.suffix=='.gz'else path.read_bytes())
def copy_and_run(scripts,outputs):
 manifest=authenticate()
 with tempfile.TemporaryDirectory(prefix='g20-nine-cold-')as tmp:
  scratch=Path(tmp)/'package';shutil.copytree(HERE,scratch,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  cache=Path(tmp)/'bytecode';env=os.environ.copy();env.pop('PYTHONPATH',None);env.pop('PYTHONOPTIMIZE',None)
  flags=['-B','-X','pycache_prefix='+str(cache)]
  if sys.flags.optimize:flags.insert(0,'-OO'if sys.flags.optimize>1 else'-O')
  for script in scripts:
   p=subprocess.run([sys.executable,*flags,str(scratch/script)],cwd=scratch,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
   need(p.returncode==0,script+' replay failed: '+p.stdout.decode(errors='replace')[-3000:])
  checks=[]
  for name in outputs:
   expected=HERE/name;actual=scratch/name
   need(actual.is_file(),'Missing output '+name)
   if name.endswith('.jsonl.gz'):need(gzip.decompress(expected.read_bytes())==gzip.decompress(actual.read_bytes()),'Canonical complete stream '+name)
   else:need(canonical(read(expected))==canonical(read(actual)),'Deterministic proof payload '+name)
   checks.append(name)
  # The input vendor is immutable even inside the scratch replay.
  for r in manifest['files']:
   if r['path'].startswith('vendor/'):
    need(hashlib.sha256((scratch/r['path']).read_bytes()).hexdigest()==r['sha256'],'Vendor changed during replay '+r['path'])
 return checks
