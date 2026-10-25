"""Declared files only, Git-free optimized replay and fail-closed controls."""
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def run_export():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)/'export';package=root/'research'/HERE.name;package.mkdir(parents=True)
        for p in HERE.iterdir():
            if p.is_file():shutil.copyfile(p,package/p.name)
        inputs=json.loads((HERE/'VERIFY.json').read_text())['inputs']
        for name in inputs:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        env=dict(os.environ);env['PYTHONPYCACHEPREFIX']=str(Path(td)/'cache')
        command=[sys.executable,'-O','-B',str(package/'verify.py'),'--quick']
        result=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=60)
        need(result.returncode==0,result.stdout+result.stderr)
        target=root/inputs[2];data=target.read_bytes()
        for mode in ('changed','missing','symlink','receipt'):
            if mode=='changed':target.write_bytes(data+b'\n')
            elif mode=='missing':target.unlink()
            elif mode=='symlink':
                elsewhere=Path(td)/'original.py';elsewhere.write_bytes(data);target.unlink();target.symlink_to(elsewhere)
            else:
                receipt=package/'RESULT.json';old=receipt.read_bytes();receipt.write_text('{}')
            test=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=60)
            need(test.returncode!=0,'export control accepted '+mode)
            if mode=='receipt':receipt.write_bytes(old)
            else:
                if target.exists() or target.is_symlink():target.unlink()
                target.write_bytes(data)
        print('Git-free optimized replay and four corruption controls PASS')
