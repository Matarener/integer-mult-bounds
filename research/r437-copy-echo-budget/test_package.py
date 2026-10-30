#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Actual optimized export and source/invoice rejection subprocesses."""
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)
def invoke(p,ok):
    r=subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py')],cwd=p.parent,
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
    need((r.returncode==0)==ok,'export subprocess status '+r.stdout+r.stderr)
    if ok:need('PASS_COPY_ECHO_BUDGET' in r.stdout,'positive scientific marker')
with tempfile.TemporaryDirectory(prefix='copy-echo-export-') as t:
    root=Path(t);p=root/'package';shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
    for f in p.rglob('*'):
        if f.is_file():f.chmod(0o444)
    invoke(p,True)
    for f in p.rglob('*'):
        if f.is_file():f.chmod(0o644)
    source=p/'inputs/r437-word.json.gz';b=source.read_bytes()
    source.write_bytes(b+b'changed');invoke(p,False);source.write_bytes(b)
    source.unlink();invoke(p,False);source.write_bytes(b)
    other=root/'source-copy.gz';other.write_bytes(b);source.unlink();source.symlink_to(other)
    invoke(p,False);source.unlink();source.write_bytes(b)
    result=p/'RESULT.json';saved=result.read_bytes();d=json.loads(saved);d['budget']['excess']=0
    result.write_text(json.dumps(d));invoke(p,False);result.write_bytes(saved)
print('PASS_COPY_ECHO_EXPORT_AND_FOUR_REJECTIONS')
