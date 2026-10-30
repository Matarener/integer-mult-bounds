"""Real optimized CLI source-binding failure controls; no repeated science."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
PACKAGE=Path('research/physical-block-core-return')


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    with tempfile.TemporaryDirectory(prefix='two-column-integrity-') as directory:
        root=Path(directory);package=root/PACKAGE;package.mkdir(parents=True)
        for p in HERE.iterdir():
            if p.is_file():shutil.copyfile(p,package/p.name)
        for name in json.loads((HERE/'VERIFY.json').read_text())['inputs']:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        command=[sys.executable,'-I','-O','-B',str(package/'verify.py'),'--quick']
        def reject(fragment):
            result=subprocess.run(command,cwd=root,text=True,capture_output=True,timeout=10)
            need(result.returncode!=0 and fragment in result.stderr,'real CLI rejection: '+fragment)
        source=root/'research/physical-boundary-pages/boundary_pages.py';raw=source.read_bytes()
        source.write_bytes(raw+b'\n# changed predecessor\n');reject('source pin ')
        source.unlink();reject('FileNotFoundError');source.write_bytes(raw)
        for name in ('rhs_layout.py','source_fixture.py'):
            local=package/name;raw=local.read_bytes();local.write_bytes(raw+b'\n# changed retained helper\n')
            reject('retained helper pin');local.write_bytes(raw)
        command.pop()  # Receipt type checks run before science in the normal CLI.
        receipt=package/'RESULT.json';original=receipt.read_text()
        for key,value,fragment in [('total',True,'strict receipt count type'),('retain',1,'strict receipt schedule type')]:
            data=json.loads(original);data['case']['schedules'][0][key]=value
            receipt.write_text(json.dumps(data));reject(fragment)
        receipt.write_text(original)
        need(not (root/'.git').exists(),'actual Git-free failure relocation')
    print('PASS_BLOCK_CORE_CLI_INTEGRITY four source-binding and two receipt-type rejections')


if __name__=='__main__':main()
