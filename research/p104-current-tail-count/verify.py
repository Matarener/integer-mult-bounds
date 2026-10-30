#!/usr/bin/env python3
"""Portable byte-preserved PR5580 isolated-tail count certificate.

Chris R/Clear1nsight, substantial OpenAI Codex assistance, Apache-2.0.
All source authors and mathematical predecessors retain credit.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
AUDIT='outputs/continuous-kappa-process-20261026/tail-count-qualification-5580'
REQUEST_SHA='8fc281dbc1a4e5868fb1085005eec5813ad2c34a628b8679a36f593790c49ced'
RESULT_SHA='f0ab2ed10f91a5acd76c1c6753d970c59e51e83c3d0b96fe8a6a3a6c3f80e9de'


def need(condition,message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(root,name):
    path=Path(name)
    need(not path.is_absolute() and path.as_posix()==name and '..' not in path.parts,'canonical relative file '+name)
    current=root
    for part in path.parts:
        current=current/part
        need(not current.is_symlink(),'symlink component '+name)
    need(current.is_file(),'regular file '+name)
    return current


def authenticate():
    inventory=json.loads(regular(HERE,'PAYLOAD-INVENTORY.json').read_bytes())['files']
    actual=set()
    for path in HERE.rglob('*'):
        need(not path.is_symlink(),'symlink package member '+str(path))
        if path.is_file() and path!=HERE/'PAYLOAD-INVENTORY.json':
            actual.add(path.relative_to(HERE).as_posix())
    need(actual==set(inventory),'complete package inventory')
    for name,row in inventory.items():
        raw=regular(HERE,name).read_bytes()
        need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'frozen package byte '+name)
    capsule=HERE/'capsule'
    request_raw=regular(capsule,AUDIT+'/REQUEST.json').read_bytes()
    need(sha(request_raw)==REQUEST_SHA,'original frozen5580 request')
    request=json.loads(request_raw)
    need(request['total_seconds']==150 and request['memory_mib']==512 and request['per_child_seconds']==60,
         'original frozen resource limits')
    for name,expected in request['files'].items():
        need(sha(regular(capsule,name).read_bytes())==expected,'original frozen input '+name)
    normal=regular(capsule,AUDIT+'/RESULT-normal.json').read_bytes()
    optimized=regular(capsule,AUDIT+'/RESULT-optimized.json').read_bytes()
    need(normal==optimized and sha(normal)==RESULT_SHA,'original complete normal/optimized scientific bytes')
    pair=json.loads(regular(capsule,AUDIT+'/PAIR-RECEIPT.json').read_bytes())
    need(pair['result_sha256']==RESULT_SHA and pair['request_sha256']==REQUEST_SHA and
         pair['complete_output_equal'] is True and pair['scientific_fields_excluded']==0,
         'original exact request/result/pair join')
    guard=json.loads(regular(HERE,'original-evidence/GUARD-RECEIPT.json').read_bytes())
    log=regular(HERE,'original-evidence/GUARD-STDOUT.log').read_bytes()
    need(guard['exit_code']==0 and guard['termination'] is None and
         guard['memory_limit_mib']==512 and guard['timeout_seconds']==150 and
         sha(log)==guard['log_sha256'],'original guard/log custody')
    result=json.loads(normal)
    need(result['status']=='PASS_SCOPED_PR5580_SINGLE_USE_TAIL_COUNT_CERTIFICATE' and
         result['reviewed_head']=='6efa248cf456d6101d757e9d09ba29711d18a13a' and
         result['physical_witness'] is False and result['new_kappa'] is None and result['selected_promotion'] is False,
         'original scoped scientific result')
    need(len(result['mutation_controls'])==25 and all(row['outcome']=='rejected' for row in result['mutation_controls'].values()),
         'all25 original classified controls')
    return normal


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))


def main():
    expected=authenticate()
    if sys.argv[1:]==['--integrity-only']:
        print('PASS_P104_CURRENT_TAIL_COUNT_INTEGRITY_ONLY_NO_SCIENCE')
        return
    need(not sys.argv[1:],'unsupported verifier arguments')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
    script=HERE/'capsule'/AUDIT/'check.py'
    with tempfile.TemporaryDirectory(prefix='p104-current-tail-count-') as folder:
        command=[sys.executable,'-I','-X','pycache_prefix='+folder+'/bytecode']
        command+=['-O'] if sys.flags.optimize else []
        command+=['-B',str(script)]
        with (Path(folder)/'stdout.json').open('wb+') as out,(Path(folder)/'stderr.txt').open('wb+') as err:
            child=subprocess.run(command,cwd=HERE/'capsule',env=env,stdout=out,stderr=err,timeout=60,preexec_fn=child_limits)
            out.seek(0);actual=out.read();err.seek(0);errors=err.read()
        need(child.returncode==0 and not errors,'scientific child failed: '+errors.decode(errors='replace')[:4000])
        need(actual==expected,'complete original scientific output equality')
    result=json.loads(actual)
    authenticate()
    print('PASS_P104_CURRENT_TAIL_COUNT')
    print(json.dumps({'reviewed_head':result['reviewed_head'],'complete_original_output_sha256':sha(actual),
      'classified_controls_rejected':25,'two_point_count_minima':{'all_controller_relaxation':146,'fixed18_relaxation':147},
      'physical_witness':False,'new_kappa':None,'selected_promotion':False},sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
