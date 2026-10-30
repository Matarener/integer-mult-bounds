"""Reproduce this finite local package, with expensive searches only under --full."""
from pathlib import Path
import argparse, gzip, hashlib, json, subprocess, sys, time
HERE=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)
def semantic(x):
 if isinstance(x,dict):return {k:semantic(v) for k,v in x.items() if k!='seconds'}
 if isinstance(x,list):return [semantic(v) for v in x]
 return x

def run(script,args=(),receipt=None):
 expected=semantic(json.loads((HERE/'results'/receipt).read_text())) if receipt else None
 p=subprocess.run([sys.executable,'-B',str(HERE/script),*args],text=True,capture_output=True)
 need(p.returncode==0,script+' failed:\n'+p.stdout+'\n'+p.stderr)
 if receipt:need(semantic(json.loads((HERE/'results'/receipt).read_text()))==expected,'semantic receipt changed: '+receipt)
 print('PASS',script,*args,flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');a=ap.parse_args()
 manifest=json.loads((HERE/'MANIFEST.json').read_text())
 for row in manifest['files']:
  data=(HERE/row['path']).read_bytes()
  if row['hash_type']=='json_semantic':data=json.dumps(semantic(json.loads(data)),sort_keys=True,separators=(',',':')).encode()
  elif row['hash_type']=='json_gzip_semantic':data=json.dumps(semantic(json.loads(gzip.decompress(data))),sort_keys=True,separators=(',',':')).encode()
  else:need(row['hash_type']=='raw','unknown hash type')
  need(hashlib.sha256(data).hexdigest()==row['sha256'],'changed frozen file '+row['path'])
 for name,result in [('word5713.json.gz','contacts5713.json'),('word5718.json.gz','contacts5718.json')]:run('search.py',['--word',name,'--out',result],result)
 run('controls.py',receipt='controls.json');run('invoice.py',receipt='invoice.json')
 counts=[]
 for label in ('a','b','c'):
  for route in ('fixed','retimed'):
   file='joint680-'+label+'-'+route+'.json' if label!='a' or route=='fixed' else 'joint680-cut-retimed.json'
   d=json.loads((HERE/'results'/file).read_text());need(not d['truncated'] and not d['survivors'],'completed negative receipt');counts.append(d['tested'])
 need(sum(counts)==4887150,'complete three-ADD coverage')
 two=json.loads((HERE/'results/two-two680.json').read_text());need(two['literal_program_pairs']==43430473 and two['matrix_pairs']==30919369 and two['probe_pass']==0 and not two['survivors'],'complete four-ADD coverage')
 if a.full:
  run('preflight.py',receipt='preflight5718.json');run('reachability.py',receipt='reach5718.json')
  for index,first,label in [(1196,13920,'a'),(1199,13922,'b'),(1200,13922,'c')]:
   for route in ('fixed','retimed'):
    file='joint680-'+label+'-'+route+'.json' if label!='a' or route=='fixed' else 'joint680-cut-retimed.json'
    args=['--index',str(index),'--first',str(first),'--second',str(16651 if route=='fixed' else 16652),'--first-frame','1049','--second-frame','164','--first-roles','680,753,679,682,685,686','--depth','2','--cap','1250000','--out',file]
    if route=='retimed':args+=['--move','16655','--after','16649']
    run('joint.py',args,file)
  run('two_two.py',receipt='two-two680.json')
 print(json.dumps(dict(status='PASS',full=a.full,three_ADD_program_pairs=sum(counts),four_ADD_program_pairs=two['literal_program_pairs'],new_kappa=False)))
if __name__=='__main__':main()
