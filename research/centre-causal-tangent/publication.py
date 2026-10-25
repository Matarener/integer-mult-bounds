#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Actual Git-free derivative/secant replay and CLI corruption controls.

Clear1nsight with substantial OpenAI assistance. Only isolated copies change.
This is portability and rejection evidence, not native supplier admission.
"""
from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE='research/community-frontier1094-audit/selected-replay.tar.gz'


def need(ok,message):
    if not ok: raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)):[sha256(p.read_bytes()).hexdigest(),stat.S_IMODE(p.stat().st_mode)]
            for p in sorted(root.rglob('*')) if p.is_file()}


def execute(package,env,script,success,reason=None):
    run=subprocess.run([sys.executable,'-I','-O','-B',str(package/script)],cwd=package.parents[1],
                       env=env,capture_output=True,text=True,timeout=150)
    if success:
        need(run.returncode==0,'portable replay failed: '+run.stderr[-2000:])
        prefix='RESULT_JSON=' if script=='verify.py' else 'SECANT_JSON='
        lines=[line[len(prefix):] for line in run.stdout.splitlines() if line.startswith(prefix)]
        need(len(lines)==1,'one substantive portable receipt')
        raw=json.dumps(json.loads(lines[0]),sort_keys=True,separators=(',',':')).encode()
        return sha256(raw).hexdigest()
    need(run.returncode!=0 and reason in run.stderr,'CLI mutation did not fail at the expected guard')
    return None


def main():
    need((ROOT/ARCHIVE).is_file(),'original archive required')
    with tempfile.TemporaryDirectory(prefix='causal-portable-') as tmp:
        root=Path(tmp); package=root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        source=root/ARCHIVE; source.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/ARCHIVE,source)
        env=dict(os.environ,PATH='',PYTHONDONTWRITEBYTECODE='1')
        need(not (root/'.git').exists() and shutil.which('git',path='') is None,'Git unavailable')
        before=inventory(root)
        hashes={script:execute(package,env,script,True) for script in ('verify.py','secant.py')}
        need(before==inventory(root),'portable replay changed exported bytes or modes')
        for filename,script,reason in (('RESULT.json','verify.py','typed result mismatch'),
                                       ('SECANT.json','secant.py','typed secant receipt differs')):
            path=package/filename; saved=path.read_bytes(); value=json.loads(saved)
            need(value['schema_version']==1,'version-one scientific receipt')
            value['schema_version']=True; path.write_text(json.dumps(value))
            try: execute(package,env,script,False,reason)
            finally: path.write_bytes(saved)
        held=source.with_name(source.name+'.held'); source.rename(held)
        try: execute(package,env,'verify.py',False,'regular selected archive')
        finally: held.rename(source)
        with source.open('r+b') as stream:
            first=stream.read(1); stream.seek(0); stream.write(bytes([first[0]^1]))
        try: execute(package,env,'verify.py',False,'selected archive hash')
        finally: shutil.copy2(ROOT/ARCHIVE,source)
        need(before==inventory(root),'corruption controls failed to restore their private copies')
        print('PASS_GIT_FREE_CAUSAL_PUBLICATION files='+str(len(before))+' cli_rejections=4 bytes_and_modes_unchanged=true')
        print('PUBLICATION_RECEIPTS='+json.dumps(hashes,sort_keys=True))


if __name__=='__main__': main()
