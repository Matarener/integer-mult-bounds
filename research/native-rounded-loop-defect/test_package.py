"""Isolated package-boundary faults; no shared source mutation."""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
def run(p,opt):return subprocess.run([sys.executable,'-I']+opt+['-B',str(p/'verify.py')],capture_output=True,text=True,timeout=15)
for opt in ([],['-O']):
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'package';shutil.copytree(HERE,p)
  for item in [p]+list(p.rglob('*')):item.chmod(0o700 if item.is_dir()else 0o600)
  result=run(p,opt);need(result.returncode==0,'isolated baseline '+result.stderr)
  source=p/'source/lifting.py';old=source.read_bytes();source.write_bytes(old+b'\nraise RuntimeError("UNAUTHENTICATED_CODE_EXECUTED")\n')
  result=run(p,opt);need(result.returncode!=0 and 'source authentication' in result.stderr and 'UNAUTHENTICATED_CODE_EXECUTED' not in result.stderr,'authenticate before executing source')
  source.write_bytes(old)
  receipt=p/'RESULT.json';old=receipt.read_bytes();data=json.loads(old);data['unexpected_field']='tampered';receipt.write_text(json.dumps(data))
  result=run(p,opt);need(result.returncode!=0 and 'receipt equality' in result.stderr,'typed whole receipt rejection');receipt.write_bytes(old)
  data=json.loads(old)
  if 'witness_input' in data:data['witness_input'][0][0]=True
  else:data['fused_gates']=float(data['fused_gates'])
  receipt.write_text(json.dumps(data));result=run(p,opt)
  need(result.returncode!=0 and 'receipt equality' in result.stderr,'bool/int or float/int receipt type rejection');receipt.write_bytes(old)
  if (p/'RECIPES.json').exists():
   q=p/'RECIPES.json';data=json.loads(q.read_text());data[0]['left']['phase']=(data[0]['left']['phase']+1)%4;q.write_text(json.dumps(data));result=run(p,opt)
   need(result.returncode!=0 and 'native recipe receipt' in result.stderr,'native recipe mutation rejection')
print('PASS_PACKAGE_BOUNDARY_CONTROLS normal and optimized')
