#!/usr/bin/env python3
"""Reproduce one historical direct-route obstruction. Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
EXPECTED='41a58dbab3a8aa8215d76c01c3b557e425604ec5aab6e15782c3f0eb88ca63a4'
ORIGINAL_CORE='b296855175e7d2cf84bbab07696b6b5b9589ffe4e1a9060174bb6d796f065304'
WORD_SHA='9e78864cd46fc443c6183674588c99c52cfb8e8e408c7ba09bb50cf4694463f6'
WORD_BLOB='9e68b7de6bfc23bc4fe9940c718dba350ba8a893'

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def safe(name):
    p=PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==name,'Canonical package-local payload path')
    f=HERE
    for bit in p.parts:
        f=f/bit;need(not f.is_symlink(),'No payload symlinks')
    need(f.is_file(),'Missing payload '+name);return f

def check_bytes(raw,row):
    need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'Payload size/SHA256')
    if 'git_blob' in row:
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'Payload Git blob')

def rejected(action):
    try:action()
    except ValueError:return 'rejected'
    raise ValueError('Integrity control accepted a mutation')

def main():
    manifest=json.loads((HERE/'PORTABLE.json').read_bytes())
    need(manifest['original_result_sha256']==EXPECTED and manifest['original_checker_sha256']==ORIGINAL_CORE,'Original evidence binding')
    for name,row in manifest['payloads'].items():check_bytes(safe(name).read_bytes(),row)
    original=safe('evidence/original-check.py').read_bytes();portable=safe('check.py').read_bytes()
    need(sha(original)==ORIGINAL_CORE and original.count(b'ROOT=HERE.parents[2]')==1 and
         original.replace(b'ROOT=HERE.parents[2]',b'ROOT=HERE')==portable,'Exactly one ROOT adaptation; unchanged scientific logic')
    need(sha(safe('evidence/RESULT-normal.json').read_bytes())==EXPECTED and
         safe('evidence/RESULT-normal.json').read_bytes()==safe('evidence/RESULT-optimized.json').read_bytes(),'Entire original result pair')
    word=safe('source/WORD.json.gz').read_bytes();row=manifest['payloads']['source/WORD.json.gz']
    need(row['bytes']==107909 and row['sha256']==WORD_SHA and row['git_blob']==WORD_BLOB,'Exact historical compressed source')
    controls={
      'corrupt_compressed_bytes':rejected(lambda:check_bytes(word[:-1]+bytes([word[-1]^1]),row)),
      'corrupt_scientific_core':rejected(lambda:check_bytes(portable+b'\n',manifest['payloads']['check.py']))}
    # Fresh cache isolates imports in the single separately launched core.
    # The package and export remain read-only; the cache lives outside them.
    with tempfile.TemporaryDirectory(prefix='p104-chart-cache-') as cache:
        command=[sys.executable,'-I','-B','-X','pycache_prefix='+cache]
        if sys.flags.optimize:command.append('-O' if sys.flags.optimize==1 else '-OO')
        command.append(str(HERE/'check.py'))
        env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
        done=subprocess.run(command,cwd=HERE,env=env,capture_output=True,timeout=55,check=False)
    need(done.returncode==0 and not done.stderr,'Core must complete without source/binding/resource errors')
    need(sha(done.stdout)==EXPECTED,'Entire scientific output must equal original SHA256; no excluded fields')
    value=json.loads(done.stdout)
    need(value['status']=='STOP_UNSUPPORTED_FORWARD_NESTING' and value['candidate_paid_invoice'] is None,'Completed physical stop; no priced candidate')
    need(value['instruction_count']==25448 and value['decompressed_hard_cap']==16777216,'Exact corpus count and unchanged abort cap')
    need(value['unique_final_block']['actual_program_indices']==[14187,14189,14192,14194],'Final four-gate binding')
    donor=value['donor_W_Z']
    need(donor['W']['event']==13554 and donor['W']['instruction']==['ADD',695,733,'1',597] and
         donor['Z']['event']==14397 and donor['Z']['instruction']==['ADD',132,733,'2',597] and
         donor['p']==donor['r']==1,'Exact neighboring donor reads')
    need(donor['spaces']=={'597':[82],'652':[82,268]},'Fixed ordered source spaces')
    need(any(e['old']==652 and e['new']==597 and e['rank']==-1 and e['strict_forward'] is False
             for e in value['unsupported_edges']['733']),'Forbidden 652-to-597 return')
    need(len(value['controls'])==7 and all(v['outcome']=='rejected' for v in value['controls'].values()),'Original seven controls reject')
    print(json.dumps({'status':'PASS_P104_FIXED_CHART_CONTACT_OBSTRUCTION','source_head':value['source_head'],
      'scientific_status':value['status'],'complete_scientific_output_sha256':sha(done.stdout),
      'required_donor_route':[597,652,597],'new_kappa':None,'candidate_paid_invoice':None,
      'core_executions':1,'original_controls_rejected':7,'portable_integrity_controls':controls,
      'core_adaptation':'One ROOT assignment only; source modules never imported.'},sort_keys=True,separators=(',',':')))

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'status':'FAIL_P104_CHART_OBSTRUCTION_REPLAY','failure':type(error).__name__+': '+str(error)},sort_keys=True,separators=(',',':')))
        sys.exit(1)
