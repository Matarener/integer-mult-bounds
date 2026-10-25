"""Independent immutable-source/typed-receipt boundary controls."""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
p=Path(__file__).resolve().parent
def need(q,s):
 if not q:raise ValueError(s)
for opt in ([],['-O']):
 with tempfile.TemporaryDirectory()as tmp:
  q=Path(tmp)/'package';shutil.copytree(p,q)
  for x in [q]+list(q.rglob('*')):x.chmod(0o700 if x.is_dir()else 0o600)
  def run():return subprocess.run([sys.executable,'-I']+opt+['-B',str(q/'verify.py')],capture_output=True,text=True,timeout=15)
  r=run();need(r.returncode==0,'baseline '+r.stderr)
  src=q/'source/NORMALIZERS.json';old=src.read_bytes();d=json.loads(old);d['mode_columns'][0][0]=2;src.write_text(json.dumps(d));r=run();need(r.returncode and 'source authentication' in r.stderr,'actual source corruption');src.write_bytes(old)
  rec=q/'RESULT.json';old=rec.read_bytes();d=json.loads(old);d['E_inverse_diagonal']=1;rec.write_text(json.dumps(d));r=run();need(r.returncode and 'typed receipt equality' in r.stderr,'typed scalar receipt rejection');rec.write_bytes(old)
  d=json.loads(old);d['columnwise_nonmembership_from_f']=4197;rec.write_text(json.dumps(d));r=run();need(r.returncode and 'typed receipt equality' in r.stderr,'strict threshold mutation')
print('PASS_ODD_E8_BOUNDARY_CONTROLS_NORMAL_OPTIMIZED')
