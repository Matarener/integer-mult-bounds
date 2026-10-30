"""Cheap source/receipt controls; no actual coefficient replay."""
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,why):
    if not ok:raise ValueError(why)
def main():
    count=0
    with tempfile.TemporaryDirectory(prefix='coefficient-controls-') as directory:
        root=Path(directory);p=root/'research'/HERE.name
        shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
        for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if r['usage']=='input':
                target=root/r['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r['path'],target)
        receipt=(p/'RESULT.json').read_bytes();source=root/'research/physical-gaussian-core/gaussian_exponentials.py';original=source.read_bytes();oracle=p/'oracle.py';frozen=oracle.read_bytes()
        for opt in ([],['-O']):
            command=[sys.executable,'-I','-B',*opt,str(p/'verify.py'),'--oracle-only']
            def run(ok,phrase):
                r=subprocess.run(command,cwd=root,env={**os.environ,'PATH':''},text=True,capture_output=True,timeout=10)
                need((r.returncode==0)==ok and phrase in r.stdout+r.stderr,phrase+' '+r.stdout+r.stderr)
            run(True,'PASS_ENCODED_GAUSSIAN_COEFFICIENT_AUDIT_ORACLE');count+=1
            (p/'RESULT.json').unlink();run(False,'FileNotFoundError');count+=1
            (p/'RESULT.json').write_bytes(receipt)
            d=json.loads(receipt);d['oracle_self_tests']['intervals']=float(d['oracle_self_tests']['intervals']);(p/'RESULT.json').write_text(json.dumps(d));run(False,'complete typed receipt mismatch');count+=1
            (p/'RESULT.json').write_bytes(receipt)
            source.write_bytes(original+b'\nraise RuntimeError("UNAUTHENTICATED_SOURCE_EXECUTED")\n');run(False,'source hash research/physical-gaussian-core/gaussian_exponentials.py');count+=1;source.write_bytes(original)
            oracle.write_bytes(frozen+b'\nraise RuntimeError("ALTERED_ORACLE_EXECUTED")\n');run(False,'frozen independent oracle');count+=1;oracle.write_bytes(frozen)
    print('PASS_COEFFICIENT_PACKAGE_CONTROLS '+str(count))
if __name__=='__main__':main()
