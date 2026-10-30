#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Chris R / Clear1nsight with substantial OpenAI Codex assistance.
"""Actual read-only, Git-free package replay and semantic failure controls."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(p):return {str(x.relative_to(p)):hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob('*') if x.is_file()}
def run(p,good,needle=''):
    result=subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py')],cwd=p,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
    need((result.returncode==0)==good,'replay outcome '+result.stdout[-1200:])
    if needle:need(needle in result.stdout,'wrong rejection '+result.stdout[-1200:])
with tempfile.TemporaryDirectory(prefix='r437-affine-export-') as td:
    p=Path(td)/'package';shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    before=digest(p)
    for f in p.rglob('*'):
        if f.is_file():f.chmod(0o444)
    for d in sorted((x for x in p.rglob('*') if x.is_dir()),reverse=True):d.chmod(0o555)
    p.chmod(0o555)
    run(p,True,'PASS_AFFINE_TWO_CHILD_SCOPED_BOUND');need(digest(p)==before,'read-only bytes unchanged')
    for d in [p]+[x for x in p.rglob('*') if x.is_dir()]:d.chmod(0o755)
    for f in p.rglob('*'):
        if f.is_file():f.chmod(0o644)
    source=p/'inputs/pr4010-RESULT.json';raw=source.read_bytes();source.write_bytes(raw+b' ')
    run(p,False,'source SHA256');source.write_bytes(raw)
    source.unlink();run(p,False,'missing or linked source');source.write_bytes(raw)
    outside=Path(td)/'linked.json';outside.write_bytes(raw);source.unlink();source.symlink_to(outside)
    run(p,False,'missing or linked source');source.unlink();source.write_bytes(raw)
    result=p/'RESULT.json';data=json.loads(result.read_text());data['budget']['minimum_integer_rank_pair']=[7,1];result.write_text(json.dumps(data))
    run(p,False,'committed receipt equality')
print('PASS_AFFINE_EXPORT_AND_FOUR_FAILURE_CONTROLS')
