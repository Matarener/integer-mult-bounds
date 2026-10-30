"""Portable serial scientific replay; sealed source files are never regenerated."""
from pathlib import Path
from hashlib import sha256
import argparse,json,subprocess,sys
D=Path(__file__).resolve().parent
def need(q,s):
 if not q:raise ValueError(s)
def inventory():
 mf=json.loads((D/'FROZEN.json').read_bytes())['files'];actual={str(p.relative_to(D))for p in D.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
 need(actual==set(mf)|{'FROZEN.json'},'complete package inventory')
 for rel,m in mf.items():
  b=(D/rel).read_bytes();need(len(b)==m['bytes']and sha256(b).hexdigest()==m['sha256'],'unchanged file '+rel)
 return len(mf)
def main(part):
 count=inventory();base='components/';entries=[]
 if part in ['author','all']:
  entries+=[base+'full-e8-cube-cover-20261025-structural/orbit_cover.py',base+'full-e8-cube-cover-20261025-structural/normalizers120.py',base+'full-e8-native120-20261025-structural/native120.py',base+'full-e8-odd3-native120-20261025-structural/family_geometry120.py',base+'full-e8-odd3-native120-20261025-structural/core.py']
 if part in ['peer','all']:entries+=['peer/check.py','peer/affine_replay.py','peer/odd_budget.py']
 for rel in entries:
  cmd=[sys.executable,'-I','-W','error','-B']+(['-O']if sys.flags.optimize else[])+[str(D/rel)]
  r=subprocess.run(cmd,cwd=D,capture_output=True,timeout=240);need(r.returncode==0,rel+'\n'+r.stderr.decode(errors='replace'));print(r.stdout.decode(),end='',flush=True)
 inventory();print(json.dumps({'status':'PASS_FULL120_E8_NATIVE_'+part.upper(),'scientific_scripts':len(entries),'payload_files_unchanged':count,'new_kappa':False,'scientific_admission':False},sort_keys=True))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--part',choices=['author','peer','all'],default='all');a=ap.parse_args();main(a.part)
