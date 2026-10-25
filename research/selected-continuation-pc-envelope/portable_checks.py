"""Cold standard-library replay and fail-closed receipt/source controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix='continuation-envelope-') as directory:
        root=Path(directory);package=root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        paths=json.loads((HERE/'VERIFY.json').read_text())['inputs']
        for name in paths:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HERE.parent.parent/name,target)
        command=[sys.executable,'-I','-O','-B',str(package/'verify.py')]
        def run(ok,marker):
            result=subprocess.run(command,capture_output=True,text=True,env={'PATH':''},timeout=20)
            if (result.returncode==0)!=ok or marker not in result.stdout+result.stderr:
                raise ValueError('control failed '+marker+' '+result.stderr)
        run(True,'PASS_SOURCE_CONTINUATION_PC_ENVELOPE')
        receipt=package/'RESULT.json';raw=receipt.read_bytes()
        receipt.unlink();run(False,'FileNotFoundError')
        changed=json.loads(raw);changed['header']['length_overflow_rejected']=1
        if changed!=json.loads(raw):raise ValueError('bool/int corruption must demonstrate coercion')
        receipt.write_text(json.dumps(changed));run(False,'typed receipt')
        receipt.write_bytes(raw)
        source=root/paths[0];source.write_bytes(source.read_bytes()+b'\n')
        run(False,'source drift')
    print('PASS_PORTABLE_CONTINUATION_ENVELOPE: optimized cold replay, missing receipt, bool/int, source bytes')


if __name__=='__main__':main()
