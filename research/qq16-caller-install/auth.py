"""Authenticate canonical and retained input bytes before inherited execution.

Chris R / Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
"""
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
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def typed(v):
 if isinstance(v,dict):return ('dict',tuple((k,typed(x)) for k,x in sorted(v.items())))
 if isinstance(v,list):return ('list',tuple(map(typed,v)))
 return (type(v).__name__,v)
def authenticate():
 result={}
 for name,digest in MANIFESTS.items():
  raw=(HERE/name).read_bytes();need(sha(raw)==digest,'manifest integrity:'+name)
  rows=parse(raw)['files'];seen=set()
  for r in rows:
   if name=='SOURCES.json' and r['usage']!='input':continue
   rel=r['path'] if name=='SOURCES.json' else r['local']
   need(rel not in seen,'duplicate source path:'+rel);seen.add(rel)
   path=(ROOT if name=='SOURCES.json' else HERE)/rel
   b=path.read_bytes();need(sha(b)==r['sha256'] and blob(b)==r['git_blob'],'source integrity:'+str(path))
   result[str(path.relative_to(ROOT))]=sha(b)
 return result
MANIFESTS={'SOURCES.json': '3ba36d49185c81691dc8c5a87f3f80a0540579bfd8b97658a52037aaa62274a6', 'PREDECESSORS.json': '57440a9f5cae02f123b38ad68e43928b694e7ca4e6569098c7904d7fe846b0c4'}
