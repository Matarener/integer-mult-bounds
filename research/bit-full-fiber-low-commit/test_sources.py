#!/usr/bin/env python3
"""Fast fail-closed source tests in an independently copied Git-free closure."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
with tempfile.TemporaryDirectory(prefix='low-commit-source-') as temporary:
    root=Path(temporary)
    package=root/'research'/HERE.name
    shutil.copytree(HERE,package)
    inputs=json.loads((HERE/'VERIFY.json').read_text())['inputs']
    for name in inputs:
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,target)
    source=root/inputs[0]
    source.write_bytes(source.read_bytes()+b'\n')
    for options in ([],['-O']):
        run=subprocess.run([sys.executable,'-I',*options,'-B',str(package/'verify.py')],
                           capture_output=True,text=True,timeout=10)
        if run.returncode==0 or 'source SHA256' not in run.stderr:
            raise RuntimeError('modified source accepted or wrong failure: '+run.stderr)
print('PASS_LOW_COMMIT_SOURCE_CONTROLS git_free normal_optimized')
