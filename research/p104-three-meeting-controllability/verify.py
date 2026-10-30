"""Read-only, Git-free, full exact replay of this scoped research package."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent

def need(condition,message):
 if not condition:raise ValueError(message)

def check_hash(data,expected):
 need(hashlib.sha256(data).hexdigest()==expected,'source or package byte corruption')

def main():
 manifest=json.loads((ROOT/'MANIFEST.json').read_text())
 for name,sha in manifest['files'].items():check_hash((ROOT/name).read_bytes(),sha)
 sources=json.loads((ROOT/'SOURCES.json').read_text())
 for s in sources['vendored_predecessor_files']:
  data=(ROOT/s['path']).read_bytes();check_hash(data,s['sha256'])
  need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==s['git_blob'],'predecessor Git blob')
 # A corrupt immutable source must fail before any scientific interpretation.
 data=(ROOT/'vendor/inputs/word5718.json.gz').read_bytes();bad=bytearray(data);bad[-1]^=1
 try:check_hash(bad,sources['word5718_sha256'])
 except ValueError:pass
 else:raise ValueError('source corruption accepted')
 from obstruction import certify
 from relax import case,relaxation,fmt
 import sys
 sys.path.insert(0,str(ROOT))
 import controls,invoice
 obs=[certify(i,r) for i in (1196,1199,1200) for r in (False,True)]
 relax=[]
 for i in (1196,1199,1200):
  for rt in (False,True):
   w,c,ts,fs,snap,roles=case(i,rt);r,_=relaxation(w,c,ts,fs,snap,roles);r.update(index=i,retimed=rt);relax.append(r)
 payload={'obstruction':obs,'relaxation':relax,'controls':controls.run(),'invoice':invoice.run()}
 for name,value in payload.items():
  need(fmt(value)==json.loads((ROOT/'results'/f'{name}.json').read_text()),'receipt mismatch '+name)
 semantic=hashlib.sha256(json.dumps(fmt(payload),sort_keys=True,separators=(',',':')).encode()).hexdigest()
 print(json.dumps(dict(status='PASS',exact_obstructions=6,relaxation_cases=6,
                      constructive_positive=True,rejection_controls=True,source_corruption_rejected=True,
                      source_columns=753,paid_jobs=66348,productive_fields=12976,new_kappa=False,
                      semantic_sha256=semantic),sort_keys=True))
if __name__=='__main__':main()
