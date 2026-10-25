"""Replay both exact outer arithmetic ledgers on their frozen admitted inputs."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile,uuid
P=Path(__file__).resolve().parent

def replay():
 source=P/'outer-replay';tmp=Path(tempfile.gettempdir()).resolve();work=tmp/('staged544-outer-'+uuid.uuid4().hex);work.mkdir()
 try:
  for f in source.rglob('*'):
   if f.is_file():
    target=work/f.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
  for name in ['LEDGER.json','INDEPENDENT.json']:(work/'outer'/name).unlink()
  for script in ['check_ledger.py','independent_check.py']:
   result=subprocess.run([sys.executable,'-B',str(work/'outer'/script)],capture_output=True,text=True)
   if result.returncode:raise ValueError(script+' failed: '+result.stderr[-1500:])
  for name in ['LEDGER.json','INDEPENDENT.json']:
   if json.loads((work/'outer'/name).read_text())!=json.loads((source/'outer'/name).read_text()):raise ValueError('regenerated outer artifact differs '+name)
 finally:
  assert work.resolve().parent==tmp and work.name.startswith('staged544-outer-')
  shutil.rmtree(work)
 print('PASS_REGENERATED_BOTH_EXACT_OUTER_LEDGERS',flush=True)
if __name__=='__main__':replay()
