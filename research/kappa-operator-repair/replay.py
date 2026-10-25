#!/usr/bin/env python3
"""Portable operator-guarded certificate replay, with optional full execution.

The default freshly reexecutes exact operator/correction/hosting proofs,
word construction, three-engine pricing and the headline conjunction.
--native additionally rebuilds both native providers. --full also reruns the
complete inherited resource/precision/outer admission in a fresh directory.
No historical or recorded PASS replaces the freshly selected core checks.
Apache-2.0. Substantial OpenAI assistance.
"""
import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def read(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def need(ok,why):
    if not ok:
        raise ValueError(why)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--native',action='store_true')
    ap.add_argument('--full',action='store_true')
    a=ap.parse_args()
    need(__debug__,'Assertions enabled')
    sys.dont_write_bytecode=True
    out=a.out.resolve()
    need(not out.exists(),'Fresh replay output directory')
    if a.full:
        need(out.is_relative_to(HERE),'Full replay work must be inside this continuation scope')
    out.mkdir(parents=True)
    manifest=read(HERE/'MANIFEST.json')
    files=0;byte_count=0
    for base,key in [(HERE,'files'),(REPO,'repository_dependencies')]:
        for name,record in manifest[key].items():
            p=base/name
            need(p.is_file() and p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],
                 'Manifest input mismatch '+str(p))
            files+=1;byte_count+=record['bytes']
    print('PASS manifest',files,'files',flush=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',
             OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE',None)
    stages=[];comparisons=[]
    def run(name,script,args=()):
        command=[sys.executable,'-B',str(script),*map(str,args)]
        log=out/(name+'.log');started=time.monotonic()
        with log.open('w') as f:
            result=subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,cwd=REPO)
        stages.append(dict(name=name,command=command,exit_code=result.returncode,
                           seconds=time.monotonic()-started,log_sha256=sha(log)))
        (out/'STAGES.json').write_text(json.dumps(stages,sort_keys=True,indent=2)+'\n')
        need(result.returncode==0,'Failed '+name+'; see '+str(log))
        print('PASS',name,flush=True)
    def compare(actual,expected):
        need(sha(actual)==sha(expected),'Fresh certificate differs from retained bytes '+str(expected))
        comparisons.append(dict(expected=expected.relative_to(REPO).as_posix(),sha256=sha(expected)))
    def compare_phase_receipt(actual,expected):
        fresh=read(actual);retained=read(expected)
        for value in [fresh,retained]:
            elapsed=value.pop('seconds')
            need(isinstance(elapsed,(int,float)) and not isinstance(elapsed,bool)
                 and math.isfinite(elapsed) and elapsed>=0,'Recorded phase-review runtime')
        need(fresh==retained,'Every scientific phase-review field agrees')
        canonical=json.dumps(retained,sort_keys=True,separators=(',',':')).encode()
        comparisons.append(dict(expected=expected.relative_to(REPO).as_posix(),
            expected_sha256=sha(expected),actual_sha256=sha(actual),
            comparison_mode='exact_json_except_top_level_runtime_seconds',
            omitted_top_level_fields=['seconds'],
            scientific_payload_sha256=hashlib.sha256(canonical).hexdigest()))
    proofs=[('full-operator','full_operator.py','FULL-OPERATOR.json'),
            ('inverse-correction','correction.py','CORRECTION.json'),
            ('gaussian-bridge','gaussian_bridge_rigidity.py','GAUSSIAN-BRIDGE-RIGIDITY.json'),
            ('actual-t360-operator','t360_admission.py','T360-OPERATOR-ADMISSION.json')]
    for name,script,receipt in proofs:
        result=out/receipt
        run(name,HERE/'operator-correction'/script,['--output',result])
        compare(result,HERE/'operator-correction'/receipt)
    run('composed-word',HERE/'composed-supplier/construct.py',['--out',out/'candidate'])
    for name in ['BORROW-WORD-43base.json.gz','BORROW-WORD-43extra.json.gz','CONSTRUCTION.json']:
        compare(out/'candidate'/name,HERE/'composed-supplier/candidate'/name)
    run('complete-invoice',HERE/'composed-supplier/invoice.py',['--out',out/'invoice'])
    compare(out/'invoice/RESULT.json',HERE/'composed-supplier/invoice/RESULT.json')
    run('target-budget',HERE/'budget.py',['--out',out/'TARGET-BUDGET.json'])
    compare(out/'TARGET-BUDGET.json',HERE/'TARGET-BUDGET.json')
    run('headline-conjunction',HERE/'build_claim.py',['--out',out/'CLAIM.json'])
    compare(out/'CLAIM.json',HERE/'CLAIM.json')
    if a.native or a.full:
        native_root=out/'fresh-native';native_root.mkdir()
        compiler=HERE/'sources/PR3945/research/staged544-terminal-gap-fill/native/run_native.py'
        for tag in ['base','extra']:
            word=HERE/'composed-supplier/candidate'/('BORROW-WORD-43'+tag+'.json.gz')
            current=HERE/'composed-supplier'/('native-'+tag)
            fresh=native_root/('native-'+tag)
            run('native-'+tag,compiler,[word,fresh,'--engine','sparse'])
            r=read(fresh/'RESULT.json');old=read(current/'RESULT.json')
            need(r['status']==old['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY'
                 and r['word_sha256']==sha(word) and r['source_sha256']==old['source_sha256'],
                 'Exact freshly executed native source/word')
            need([s['step'] for s in r['steps']]==['native','ledgers','local-replay','wrappers','phases']
                 and all(s['exit_code']==0 for s in r['steps']),'All fresh native stages')
            for name in ['CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json',
                         'INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json']:
                comparator=compare_phase_receipt if name=='CLIFFORD-REVIEW.json' else compare
                comparator(fresh/'native/local'/name,current/'native/local'/name)
        if a.full:
            run('full-conditional-release',HERE/'composed-supplier/run_release.py',
                ['--work',out/'full-release','--reuse-native-root',native_root])
            fresh=read(out/'full-release/RESULT.json');claim=read(HERE/'CLAIM.json')
            need(fresh['status']=='PASS_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE'
                 and fresh['kappa_rational']==claim['conditional_kappa']['value'],
                 'Fresh complete operator-compatible conditional release')
    result=dict(status='PASS_PORTABLE_OPERATOR_GUARDED_KAPPA_REPLAY',manifest_sha256=sha(HERE/'MANIFEST.json'),
                authenticated_files=files,authenticated_bytes=byte_count,stages=stages,comparisons=comparisons,
                fresh_native_executed=bool(a.native or a.full),fresh_full_release_executed=bool(a.full),
                retained_full_release_sha256=sha(HERE/'evidence/full-release/RESULT.json'),
                claim_sha256=sha(HERE/'CLAIM.json'),claim=read(HERE/'CLAIM.json')['conditional_kappa'],
                scope='Fresh exact core certificates and conjunctive source-bound admission. Optional native/full flags separately record heavy execution; retained full release was freshly executed during this research round.')
    (out/'VALIDATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],len(stages),'stages',len(comparisons),'comparisons',flush=True)

if __name__=='__main__':
    main()
