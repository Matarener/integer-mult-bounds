#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Actual optimized CLI: clean export, source corruption and stale invoice."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent


def run(root, expected, label):
    environment=dict(os.environ)
    environment['PATH']='/nonexistent'
    environment['PYTHONDONTWRITEBYTECODE']='1'
    command=[sys.executable,'-I','-O','-B',str(root/'verify.py')]
    result=subprocess.run(command,cwd=root,env=environment,capture_output=True,text=True,timeout=30)
    if (result.returncode==0)!=expected:
        raise ValueError(label+': '+result.stdout+result.stderr)
    if expected and 'PASS_PARABOLIC_COPY_RELATIVE_CONSTRUCTION' not in result.stdout:
        raise ValueError('missing positive marker')


def main():
    with tempfile.TemporaryDirectory(prefix='parabolic-export-') as tmp:
        tmp=Path(tmp)
        clean=tmp/'clean';shutil.copytree(HERE,clean,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for p in clean.rglob('*'):
            p.chmod(0o555 if p.is_dir() else 0o444)
        clean.chmod(0o555)
        run(clean,True,'Git-free read-only positive')
        for mutation in ['altered-source','missing-source','symlink-source','stale-invoice','boolean-invoice']:
            clone=tmp/mutation;shutil.copytree(clean,clone)
            clone.chmod(0o755)
            for p in clone.rglob('*'):
                p.chmod(0o755 if p.is_dir() else 0o644)
            source=clone/'inputs/r437-word.json.gz'
            if mutation=='altered-source':source.write_bytes(source.read_bytes()+b'bad')
            elif mutation=='missing-source':source.unlink()
            elif mutation=='symlink-source':
                source.unlink();source.symlink_to(clean/'inputs/r437-word.json.gz')
            else:
                p=clone/'RESULT.json';data=json.loads(p.read_text())
                data['ambient64_invoice']['swap']=41832 if mutation=='stale-invoice' else True
                p.write_text(json.dumps(data))
            run(clone,False,mutation)
        # Make the owned temporary export removable on all supported POSIX users.
        clean.chmod(0o755)
        for p in clean.rglob('*'):
            if p.is_dir():p.chmod(0o755)
    print('PASS_OPTIMIZED_EXPORT_AND_FIVE_CLI_REJECTIONS')

if __name__=='__main__':main()
