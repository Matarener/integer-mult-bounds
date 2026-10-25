"""Real optimized CLI source-binding failure controls; no repeated science."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
PACKAGE=Path('research/physical-two-column-boundary-kernel')


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
        source.write_bytes(raw+b'\n# changed predecessor\n');reject('bound source:')
        source.unlink();reject('FileNotFoundError');source.write_bytes(raw)
        for name in ('rhs_layout.py','source_fixture.py'):
            local=package/name;raw=local.read_bytes();local.write_bytes(raw+b'\n# changed retained helper\n')
            reject('retained caller source bytes');local.write_bytes(raw)
        need(not (root/'.git').exists(),'actual Git-free failure relocation')
    print('PASS_PAIR_KERNEL_CLI_INTEGRITY four source-binding rejections')


if __name__=='__main__':main()
