#!/usr/bin/env python3
"""Replay one fixed PR5678 nearest-contact falsifier. Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
EXPECTED='18dac3a5092667ab5f5118ed6e953d65d558a8d11066e95cc728a069ec01f50f'
ORIGINAL_CORE='2c747e340f4818a1064608323a877d693b5885bd58a1774e9b82315033649525'
WORD_SHA='b56281a67f84832198be2f2ad36d87b75244d424f1e0a6f4dda2df74f20cc08d'
WORD_BLOB='8be2b3e1c2d02034d4579bef5d36df7761d826ff'

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def safe(name):
    p=PurePosixPath(name);need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==name,'Canonical local payload path')
    f=HERE
    for bit in p.parts:f=f/bit;need(not f.is_symlink(),'No payload symlink')
    need(f.is_file(),'Missing payload '+name);return f

def check_bytes(raw,row):
    need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'Payload size/SHA256')
    if 'git_blob' in row:need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'Payload Git blob')

def rejected(action):
    try:action()
    except ValueError:return 'rejected'
    raise ValueError('Integrity control accepted altered bytes')

def main():
    inventory=json.loads((HERE/'PORTABLE.json').read_bytes())
    need(inventory['original_result_sha256']==EXPECTED and inventory['original_checker_sha256']==ORIGINAL_CORE,'Original evidence binding')
    for name,row in inventory['payloads'].items():check_bytes(safe(name).read_bytes(),row)
    old=safe('evidence/original-check.py').read_bytes();core=safe('check.py').read_bytes()
    need(sha(old)==ORIGINAL_CORE and old.count(b'ROOT=HERE.parents[2]')==1 and old.replace(b'ROOT=HERE.parents[2]',b'ROOT=HERE')==core,'Exactly one ROOT adaptation; scientific core otherwise unchanged')
    normal=safe('evidence/RESULT-normal.json').read_bytes()
    need(sha(normal)==EXPECTED and normal==safe('evidence/RESULT-optimized.json').read_bytes(),'Entire original result pair')
    word=safe('source/WORD.json.gz').read_bytes();row=inventory['payloads']['source/WORD.json.gz']
    need(row['bytes']==120135 and row['sha256']==WORD_SHA and row['git_blob']==WORD_BLOB,'Exact published compressed WORD')
    controls={'corrupt_compressed_bytes':rejected(lambda:check_bytes(word[:-1]+bytes([word[-1]^1]),row)),
              'corrupt_scientific_core':rejected(lambda:check_bytes(core+b'\n',inventory['payloads']['check.py']))}
    with tempfile.TemporaryDirectory(prefix='pr5678-nearest-cache-') as cache:
        command=[sys.executable,'-I','-B','-X','pycache_prefix='+cache]
        if sys.flags.optimize:command.append('-O' if sys.flags.optimize==1 else '-OO')
        command.append(str(HERE/'check.py'));env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
        done=subprocess.run(command,cwd=HERE,env=env,capture_output=True,timeout=55,check=False)
    need(done.returncode==0 and not done.stderr,'Core must complete without source/binding/resource failure')
    need(sha(done.stdout)==EXPECTED,'Entire scientific result must match original SHA256, no excluded fields')
    value=json.loads(done.stdout)
    need(value['status']=='COMPLETED_FIXED_NEAREST_CONTACT_FALSIFIER' and value['nearest_predicate']['status']=='NEAREST_MISMATCH','Strict completed nearest-contact falsifier')
    expected=[{'access':['write'],'event':13344,'instruction':['ADD',144,317,'1',356]},
              {'access':['write'],'event':13463,'instruction':['ADD',144,530,'1',1035]}]
    need(value['nearest_predicate']['nearest_144_contacts']==expected,'Exact two immediately preceding semantic contacts')
    bound=value['unique_published_context']
    need(bound['R']=={'event':14893,'instruction':['ADD',140,438,'-1/2',794]} and
         bound['Y']=={'event':15473,'instruction':['ADD',144,438,'-1/2',911]},'Unique exact published R/Y contexts')
    need(value['complete_affected_route_extraction_performed'] is False and value['candidate_paid_invoice'] is None and
         value['pricing_or_numeric_powers_evaluated'] is False and value['new_kappa'] is None and
         value['changed_full_word_emitted'] is False and value['other_contact_pairs_queried'] is False,'Stop before corridor/routes/prices/construction or another pair')
    need('affected_role_routes' not in value and 'signed_affected_local_rank_histogram' not in value,'No conditional route branch ran')
    need(value['instruction_count']==25453 and value['decompressed_hard_cap']==16777216,'Exact corpus count and original abort cap')
    c=value['controls'];need(len(c)==10 and c['valid_synthetic_conditional_pattern']['outcome']=='accepted' and
        c['valid_synthetic_conditional_pattern']['exact_identity'] is True and
        all(v=='rejected' for k,v in c.items() if k!='valid_synthetic_conditional_pattern'),'Nine original rejections and exact positive semantic/algebra case')
    print(json.dumps({'status':'PASS_PR5678_FIXED_NEAREST_CONTACT_VERIFICATION','scientific_status':value['status'],
      'source_head':value['source_head'],'complete_scientific_output_sha256':sha(done.stdout),'nearest_contacts':expected,
      'core_executions':1,'original_negative_controls_rejected':9,'original_positive_control_accepted':True,
      'portable_integrity_controls':controls,'candidate_paid_invoice':None,'new_kappa':None,
      'core_adaptation':'One ROOT assignment only; source modules never imported.'},sort_keys=True,separators=(',',':')))

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'status':'FAIL_PR5678_NEAREST_CONTACT_REPLAY','failure':type(error).__name__+': '+str(error)},sort_keys=True,separators=(',',':')));sys.exit(1)
