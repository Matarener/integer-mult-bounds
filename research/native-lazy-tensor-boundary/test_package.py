"""Optimized Git-free replay and actual on-disk rejection controls."""
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent

def run(p,accept):
    env=dict(os.environ,PATH='',PYTHONDONTWRITEBYTECODE='1')
    out=subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py')],cwd=p.parent,env=env,capture_output=True,text=True,timeout=30)
    if (out.returncode==0)!=accept:raise ValueError(out.stdout+out.stderr)

def main():
    with tempfile.TemporaryDirectory() as temp:
        q=Path(temp)/'package';shutil.copytree(P,q,ignore=shutil.ignore_patterns('__pycache__'))
        run(q,True)
        path=q/'source'/'BOUNDARY.json';raw=path.read_bytes();path.write_bytes(raw+b'\n');run(q,False);path.write_bytes(raw)
        path=q/'RESULT.json';raw=path.read_bytes();record=json.loads(raw);record['status']=False;path.write_text(json.dumps(record));run(q,False);path.write_bytes(raw)
        path=q/'routing.py';raw=path.read_text()
        if raw.count('phases[k]=(phases[k]-a+b)&3')!=1:raise ValueError('science mutation anchor')
        path.write_text(raw.replace('phases[k]=(phases[k]-a+b)&3','phases[k]=(phases[k]+a+b)&3'));run(q,False)
    print('PASS_PACKAGE_GITFREE_MUTATIONS controls=3 optimized_git_free=true')
if __name__=='__main__':main()
