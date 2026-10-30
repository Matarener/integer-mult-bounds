"""Authenticate complete canonical and retained bytes before inherited execution."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,why):
 if not ok:raise ValueError(why)
def unique(pairs):
 d={}
 for k,v in pairs:
  need(k not in d,'duplicate JSON key:'+k);d[k]=v
 return d
def parse(raw):return json.loads(raw,object_pairs_hook=unique)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def gitblob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def typed(v):
 if isinstance(v,dict):return ('dict',tuple((k,typed(x)) for k,x in sorted(v.items())))
 if isinstance(v,list):return ('list',tuple(map(typed,v)))
 return (type(v).__name__,v)
def authenticate():
 result={}
 for name,expected in MANIFESTS.items():
  raw=(HERE/name).read_bytes();need(sha(raw)==expected,'manifest integrity:'+name)
  records=parse(raw)['files']
  for r in records:
   if name=='SOURCES.json' and r['usage']!='input':continue
   path=ROOT/r['path'] if name=='SOURCES.json' else HERE/r['local']
   data=path.read_bytes();need(sha(data)==r['sha256'] and gitblob(data)==r['git_blob'],'source integrity:'+str(path))
   result[str(path.relative_to(ROOT))]=sha(data)
 return result
MANIFESTS={'SOURCES.json': 'd4b3343f6f6b1d08a2879df693e6d2ab89246615f20fb978a4e9cbfd5ee2e26d', 'PREDECESSORS.json': '209170a530f2ec5897edb102c029863bada01409fb2f838132a94127ff768315'}
