#!/usr/bin/env python3
"""Behavioral publication controls in a closed, Git-free temporary tree."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
with tempfile.TemporaryDirectory(prefix='fivecall-proof-controls-') as tmp:
    root = Path(tmp)
    package = root/'research'/HERE.name
    shutil.copytree(HERE, package)
    inputs = json.loads((HERE/'VERIFY.json').read_text())['inputs']
    for name in inputs:
        target = root/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,target)
    def run(optimized=False):
        return subprocess.run([sys.executable,'-I',*(['-O'] if optimized else []),'-B',str(package/'verify.py')],
                              capture_output=True,text=True,timeout=10)
    for optimized in (False,True):
        result=run(optimized)
        if result.returncode or 'PASS_FIVECALL_DIRTY_BLOCK' not in result.stdout:
            raise RuntimeError(result.stdout+result.stderr)
    for name in ['PROOF.md','RESULT.json','verify.py']:
        target=package/name
        old=target.read_bytes()
        target.write_bytes(old+b'\n')
        for optimized in (False,True):
            if run(optimized).returncode == 0:
                raise RuntimeError('accepted changed '+name)
        target.write_bytes(old)
    target=root/inputs[0]
    target.write_bytes(target.read_bytes()+b'\n')
    for optimized in (False,True):
        result=run(optimized)
        if result.returncode == 0 or 'source hash mismatch' not in result.stderr:
            raise RuntimeError('source corruption did not fail closed')
print('PASS_FIVECALL_PUBLICATION_CONTROLS git_free normal_optimized four_corruptions')
