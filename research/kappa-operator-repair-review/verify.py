#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portable fresh core/native replay; preserve the complete submitted evidence.

Native gzip payloads are exact. Derived container digests are authenticated
against their own files before comparing all other receipt fields. The long
full release and BIT execution remain retained evidence, not fresh execution.
Substantial OpenAI Codex assistance.
"""
import argparse
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = ROOT/'research/kappa-operator-repair'
LATE = PACKAGE/'late-staged-composition'
NAMES = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
         'INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-REVIEW.json', 'RESIDUAL-ADAPTERS.json')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def receipt_view(value, container_hashes, phase=False):
    value = deepcopy(value)
    need(value.pop('canonical_word_sha256') == container_hashes['CANONICAL-WORD.json.gz'], 'actual canonical container pin')
    if not phase:
        need(value.pop('local_programs_sha256') == container_hashes['LOCAL-PROGRAMS.json.gz'], 'actual programs container pin')
    else:
        seconds = value.pop('seconds')
        need(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0, 'valid runtime field')
    return value


def equal_payload(a, b):
    need(gzip.decompress(a) == gzip.decompress(b), 'exact decompressed native payload')


def controls():
    rejected = []
    for name, fn in [
        ('changed-payload', lambda: equal_payload(gzip.compress(b'a'), gzip.compress(b'b'))),
        ('forged-container-pin', lambda: receipt_view({'canonical_word_sha256':'wrong'}, {'CANONICAL-WORD.json.gz':'actual'})),
        ('invalid-runtime', lambda: receipt_view({'canonical_word_sha256':'ok','seconds':float('nan')}, {'CANONICAL-WORD.json.gz':'ok'}, True)),
    ]:
        try:
            fn()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control accepted: '+name)
    equal_payload(gzip.compress(b'same',mtime=0), gzip.compress(b'same',mtime=1))
    return rejected


def main():
    need(__debug__, 'assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(args.out.is_absolute(), 'absolute output path')
    out = args.out.resolve()
    need(not out.exists() and not out.is_relative_to(ROOT), 'fresh output outside checkout')
    out.mkdir(parents=True)
    started = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE', None)
    stages, comparisons = [], []
    def run(name, script, arguments):
        command = [sys.executable, '-B', str(script), *map(str,arguments)]
        log = out/(name+'.log'); start = time.monotonic()
        with log.open('xb') as handle:
            result = subprocess.run(command,cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=handle,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,command=command,exit_code=result.returncode,seconds=time.monotonic()-start,log_sha256=digest(log)))
        (out/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
        need(result.returncode == 0, 'failed '+name+'; see '+str(log))
        print('PASS',name,flush=True)
    # Bind every imported byte before executing the retained scripts.
    run('source-import',HERE/'check_import.py',[])
    run('core',PACKAGE/'replay_latest.py',['--out',out/'core'])
    core = read(out/'core/VALIDATION.json')
    need(core['status']=='PASS_PORTABLE_OPERATOR_GUARDED_KAPPA_REPLAY' and len(core['stages'])==12 and len(core['comparisons'])==17, 'complete fresh core')
    compiler = PACKAGE/'sources/PR3945/research/staged544-terminal-gap-fill/native/run_native.py'
    for tag in ('base','extra'):
        word = LATE/'candidate'/('BORROW-WORD-43'+tag+'.json.gz')
        fresh = out/('native-'+tag); retained = LATE/('native-'+tag)
        run('native-'+tag,compiler,[word,fresh,'--engine','sparse'])
        actual, expected = read(fresh/'RESULT.json'),read(retained/'RESULT.json')
        need(actual['status']==expected['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY', 'complete native status')
        need(actual['word_sha256']==expected['word_sha256']==digest(word), 'exact input word')
        need(actual['source_sha256']==expected['source_sha256'], 'same executed native sources')
        for directory, receipt in ((fresh,actual),(retained,expected)):
            for name, pin in receipt['source_sha256'].items():
                need(digest(directory/'source'/name)==pin,'actual native source pin')
            need([s['step'] for s in receipt['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in receipt['steps']), 'all five native stages')
        left,right = fresh/'native/local',retained/'native/local'
        hashes = [{n:digest(d/n) for n in NAMES[:2]} for d in (left,right)]
        for name in NAMES:
            a,b = left/name,right/name
            row = dict(provider=tag,file=name,actual_sha256=digest(a),expected_sha256=digest(b))
            if name.endswith('.gz'):
                equal_payload(a.read_bytes(),b.read_bytes())
                row.update(mode='exact_decompressed_payload',payload_sha256=sha256(gzip.decompress(a.read_bytes())).hexdigest())
            elif name in ('INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json'):
                phase = name=='CLIFFORD-REVIEW.json'
                av,bv = receipt_view(read(a),hashes[0],phase),receipt_view(read(b),hashes[1],phase)
                need(av==bv,'every other native scientific field: '+name)
                row.update(mode='exact_json_after_authenticating_container_pins',omitted_fields=['canonical_word_sha256']+(['seconds'] if phase else ['local_programs_sha256']),scientific_payload_sha256=sha256(json.dumps(av,sort_keys=True,separators=(',',':')).encode()).hexdigest())
            else:
                need(a.read_bytes()==b.read_bytes(),'exact native receipt bytes: '+name)
                row['mode']='byte_identity'
            comparisons.append(row)
    result = dict(status='PASS_PORTABLE_REPAIR_CORE_AND_NATIVE', core_stages=12,native_provider_stages=2,
        core_comparisons=17,native_comparisons=comparisons, total_comparisons=29,
        fresh_native_executed=True,fresh_full_release_executed=False,fresh_bit_execution=False,
        stages=stages,elapsed_seconds=time.monotonic()-started,claim=core['claim'],
        core_receipt_sha256=digest(out/'core/VALIDATION.json'),
        rejecting_controls=controls(), scope=__doc__)
    (out/'VALIDATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],'14 scientific stages, 29 comparisons',flush=True)


if __name__=='__main__':
    main()
