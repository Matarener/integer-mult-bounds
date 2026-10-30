# SPDX-License-Identifier: Apache-2.0
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PACKAGE=HERE.relative_to(ROOT)
def need(ok,why):
    if not ok:raise ValueError(why)
def main():
    with tempfile.TemporaryDirectory(prefix='raw-binary-cold-') as directory:
        root=Path(directory);out=root/PACKAGE
        shutil.copytree(HERE,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],target)
        env=dict(os.environ,PATH=str(root/'no-git'))
        def run(expect,marker):
            result=subprocess.run([sys.executable,'-I','-O','-B',str(out/'verify.py')],cwd=root,env=env,capture_output=True,text=True,timeout=25)
            need((result.returncode==0)==expect and marker in result.stdout+result.stderr,'CLI control '+marker)
        run(True,'PASS_RAW_BINARY_SHUTTLE_BRIDGE')
        target=root/'research/binary-elementary-interchange/binary_machine.py';raw=target.read_bytes();target.unlink()
        run(False,'FileNotFoundError');target.write_bytes(raw+b'\n# changed input\n');run(False,'source changed');target.write_bytes(raw)
        receipt=out/'RESULT.json';value=json.loads(receipt.read_text());value['actual_bank_invoice']['caller_descriptors']=True;receipt.write_text(json.dumps(value))
        run(False,'typed receipt')
    print('PASS_RAW_BINARY_INTEGRITY Git-free light replay, missing/changed source and typed receipt')
if __name__=='__main__':main()
