#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Real CLI, Git-free read-only transport and focused corruption controls."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import uuid

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
parent=Path(os.environ.get('TMP',os.environ.get('TEMP','.'))).resolve()
work=parent/('grid35-transport-'+uuid.uuid4().hex)
work.mkdir()
target=work/'research'/P.name
target.mkdir(parents=True)
paths=set()
for row in json.loads((P/'SOURCES.json').read_bytes())['files']:
    if row['usage']=='input':paths.add(row['path'])
paths.update(p.relative_to(ROOT).as_posix() for p in P.iterdir() if p.is_file())
for name in paths:
    destination=work/name;destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/name,destination)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(expect,extra=()):
    result=subprocess.run([sys.executable,'-B','-X','pycache_prefix='+str(parent/('grid35-pyc-'+uuid.uuid4().hex)),
                           *extra,str(target/'verify.py')],capture_output=True,text=True,cwd=work)
    if (result.returncode==0)!=expect:
        raise ValueError('unexpected transport/control result: '+result.stdout[-500:]+result.stderr[-1000:])
    return result

def mutation(path,change,reason):
    original=path.read_bytes()
    path.chmod(stat.S_IWRITE|stat.S_IREAD)
    path.write_bytes(change(original))
    result=run(False)
    if reason not in result.stderr:raise ValueError('wrong rejection reason: '+result.stderr[-1000:])
    path.write_bytes(original);path.chmod(stat.S_IREAD)

before={name:digest(work/name) for name in paths}
for name in paths:(work/name).chmod(stat.S_IREAD)
try:
    run(True)
    if before!={name:digest(work/name) for name in paths}:raise ValueError('read-only export source changed')
    mutation(work/'research/rank7-joint-endframes/tools/root.py',lambda raw:raw+b'\n# changed source\n','source drift')
    mutation(target/'SOURCES.json',lambda raw:raw.replace(b'"input"',b'"provenance"',1),'complete source manifest')
    def claim(raw):
        value=json.loads(raw);value['kappa']='1/100';return json.dumps(value).encode()
    mutation(target/'CLAIM.json',claim,'exact public claim')
    def receipt(raw):
        value=json.loads(raw);value['physical']=1;return json.dumps(value).encode()
    mutation(target/'RESULT.json',receipt,'fresh complete scoped result')
    run(False,('-O',))
    print('PASS_GRID35_GIT_FREE_READ_ONLY_AND_FIVE_REJECTION_CONTROLS')
finally:
    if work.parent!=parent or not work.name.startswith('grid35-transport-'):
        raise ValueError('unsafe private cleanup')
    for name in paths:(work/name).chmod(stat.S_IWRITE|stat.S_IREAD)
    shutil.rmtree(work)
