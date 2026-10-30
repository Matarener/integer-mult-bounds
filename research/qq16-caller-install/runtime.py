"""One authenticated physical cohort; raw canonical modules, no timestamp pyc.

All source execution follows auth.authenticate. Compile-time geometry and test
oracles are separate from encoded runtime descriptors and payload instructions.
"""
import importlib.abc,importlib.util,sys,types
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def module(name,path):
 result=types.ModuleType(name);result.__file__=str(path)
 sys.modules[name]=result
 exec(compile(path.read_bytes(),str(path),'exec'),result.__dict__)
 return result
def cold():
 auth=module('qq16_auth',HERE/'auth.py');auth.authenticate()
 rows=auth.parse((HERE/'SOURCES.json').read_bytes())['files']
 entries={Path(r['path']).stem:(ROOT/r['path'],r['sha256']) for r in rows
          if r['usage']=='input' and r['path'].startswith('research/physical-complex-controller/') and r['path'].endswith('.py')}
 class RawLoader(importlib.abc.Loader):
  def __init__(self,path,digest):self.path,self.digest=path,digest
  def create_module(self,spec):return None
  def exec_module(self,m):
   raw=self.path.read_bytes();auth.need(auth.sha(raw)==self.digest,'canonical executable integrity')
   m.__file__=str(self.path);exec(compile(raw,str(self.path),'exec'),m.__dict__)
 class Finder(importlib.abc.MetaPathFinder):
  def find_spec(self,name,path=None,target=None):
   if name in entries:
    p,d=entries[name];return importlib.util.spec_from_file_location(name,p,loader=RawLoader(p,d))
   return None
 sys.meta_path.insert(0,Finder())
 sys.path.insert(0,str(ROOT/'research/physical-complex-controller'))
 import cohort
 cohort.activate()
 return cohort
def cleanup():
 import tempfile
 seen=set()
 for m in list(sys.modules.values()):
  if m is None:continue
  for v in list(vars(m).values()):
   if isinstance(v,tempfile.TemporaryDirectory) and id(v) not in seen:
    seen.add(id(v));v.cleanup()
