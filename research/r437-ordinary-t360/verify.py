"""Read-only bounded replay of the scoped R437 enabling evidence. Apache-2.0."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_bytes())
    paths=set()
    for row in manifest['files']:
        path=HERE/row['path'];need(path.is_file() and not path.is_symlink(),'regular retained source')
        need(hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],'pinned source '+row['path'])
        need(row['path'] not in paths,'unique input path');paths.add(row['path'])
    observed={p.relative_to(HERE).as_posix() for p in (HERE/'sources').rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc')}
    need(observed==paths,'complete retained source inventory')
    receipt=json.loads((HERE/'evidence/R437-COLD-REPLAY.json').read_bytes())
    expected=json.loads((HERE/'sources/r437/EXPECTED.json').read_bytes())
    need(len(receipt['commands'])==13 and all(x['exit_code']==0 for x in receipt['commands'])
         and receipt['program_sha256']==expected['program_sha256']
         and receipt['word_content_sha256']==expected['word_content_sha256']
         and receipt['whole_kappa_changed'] is False,'retained cold replay scope')


def main():
    authenticate();runs=[]
    env=os.environ.copy();env.pop('PYTHONPATH',None);env.pop('PYTHONOPTIMIZE',None)
    for script,name in [('certificate.py','certificate.json'),('check_adapter.py','adapter.json'),('check_profile.py','profile.json')]:
        start=time.monotonic()
        with tempfile.TemporaryDirectory(prefix='r437-replay-') as cache:
            result=subprocess.run([sys.executable,'-E','-B','-X','pycache_prefix='+cache,str(HERE/script)],
                                  capture_output=True,text=True,env=env,cwd=HERE,timeout=180)
        need(result.returncode==0,script+': '+result.stderr[-3000:])
        value=json.loads(result.stdout);expected=json.loads((HERE/'evidence'/name).read_bytes())
        need(value==expected,'complete evidence equality '+script)
        runs.append({'script':script,'status':value['status'],'seconds':time.monotonic()-start})
    print(json.dumps({'status':'PASS_R437_ORDINARY_T360_SCOPED_EVIDENCE','checks':runs,
                      'conclusion':'LOCAL_PROGRESS; no new multiplication kappa'},indent=2))


if __name__=='__main__':main()
