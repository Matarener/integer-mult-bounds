from pathlib import Path
from hashlib import sha256
import argparse,json,subprocess,sys
D=Path(__file__).resolve().parent
def frozen():
 m=json.loads((D/'FROZEN.json').read_bytes())['files'];actual={str(p.relative_to(D))for p in D.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
 if actual!=set(m)|{'FROZEN.json'}:raise ValueError('frozen inventory')
 for n,r in m.items():
  b=(D/n).read_bytes()
  if len(b)!=r['bytes']or sha256(b).hexdigest()!=r['sha256']:raise ValueError('frozen payload '+n)
ap=argparse.ArgumentParser();ap.add_argument('--part',choices=['author','peer','all'],default='all');a=ap.parse_args();frozen()
author=[('author',x)for x in [['e_adapter.py'],['owned_e.py'],['n3.py'],['backward512.py'],['checkpoint120.py','--mode','base120'],['checkpoint120.py','--mode','root512'],['modes120.py'],['macros120.py'],['precision120.py'],['seal.py']]]
peer=[('peer',['check.py']),('',['portable_review.py'])]
for folder,argv in (author if a.part=='author'else peer if a.part=='peer'else author+peer):
 command=[sys.executable,'-I',*(['-O']if sys.flags.optimize else[]),'-W','error','-B',str(D/folder/argv[0]),*argv[1:]]
 subprocess.run(command,cwd=D,check=True,timeout=240);frozen()
print('PASS_FULL120_E_LOCAL_COMPONENT '+a.part)
