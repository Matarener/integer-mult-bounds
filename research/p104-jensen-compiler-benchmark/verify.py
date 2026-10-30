#!/usr/bin/env python3
"""Portable byte-preserved hypothetical Jensen145 compiler benchmark.

Chris R/Clear1nsight, substantial OpenAI Codex assistance, Apache-2.0.
Retain GamingPuzzled, DreamingOfClouds, zxv, Ali Romman and all predecessor attribution.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
AUDIT = 'outputs/continuous-kappa-process-20261026/jensen-split-compiler-feasibility-5565'
RESULT_SHA = '938f8b2fbbf60da5cccf257f47dd88c06aae7ad09c4fa8a2d87470b35a8797e2'
REQUEST_SHA = 'a16df47b5308cfab5de709db11a8707f81460446f4af6849c7962c497cccd641'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(root, name):
    path = Path(name)
    need(not path.is_absolute() and path.as_posix() == name and '..' not in path.parts,
         'canonical relative file '+name)
    current = root
    for part in path.parts:
        current = current/part
        need(not current.is_symlink(), 'symlink component '+name)
    need(current.is_file(), 'regular file '+name)
    return current


def authenticate():
    manifest = json.loads(regular(HERE,'PAYLOAD-INVENTORY.json').read_bytes())
    inventory = manifest['files']
    actual = set()
    for path in HERE.rglob('*'):
        need(not path.is_symlink(), 'symlink package member '+str(path))
        if path.is_file() and path != HERE/'PAYLOAD-INVENTORY.json':
            actual.add(path.relative_to(HERE).as_posix())
    need(actual == set(inventory), 'complete package inventory')
    for name, row in inventory.items():
        raw = regular(HERE,name).read_bytes()
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'frozen package byte '+name)
    capsule = HERE/'capsule'
    raw_request = regular(capsule,AUDIT+'/REQUEST.json').read_bytes()
    need(sha(raw_request) == REQUEST_SHA, 'original frozen request bytes')
    request = json.loads(raw_request)
    need(request['total_seconds'] == 150 and request['memory_mib'] == 512 and
         request['per_child_seconds'] == 60, 'original resource contract')
    for name, expected in request['files'].items():
        need(sha(regular(capsule,name).read_bytes()) == expected, 'original frozen request input '+name)
    expected = regular(HERE,'expected/qualification.json').read_bytes()
    need(sha(expected) == RESULT_SHA, 'original complete scientific output')
    receipt = json.loads(regular(HERE,'original-evidence/PAIR-RECEIPT.json').read_bytes())
    need(receipt['result_sha256'] == RESULT_SHA and receipt['request_sha256'] == REQUEST_SHA and
         receipt['complete_output_equal'] is True and receipt['scientific_fields_excluded'] == 0,
         'original exact pair receipt')
    for mode in ('normal','optimized'):
        need(regular(HERE,'original-evidence/RESULT-'+mode+'.json').read_bytes()==expected and
             regular(HERE,'original-evidence/STDERR-'+mode+'.txt').read_bytes()==b'',
             'preserved full original mode evidence '+mode)
    acceptance=json.loads(regular(HERE,'original-evidence/ROOT-ACCEPTANCE.json').read_bytes())
    review=json.loads(regular(HERE,'REVIEW.json').read_bytes())
    need(acceptance['request_sha256']==REQUEST_SHA and acceptance['new_kappa'] is None,
         'root acceptance and no new kappa')
    need(review['reviewed_request_sha256']==REQUEST_SHA and not review['blocking_findings'] and
         review['scientific_execution'] is False,'independent static review scope')
    return expected


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024,512*1024*1024))


def main():
    expected = authenticate()
    if sys.argv[1:] == ['--integrity-only']:
        print('PASS_P104_JENSEN_BENCHMARK_INTEGRITY_ONLY_NO_SCIENCE')
        return
    need(not sys.argv[1:], 'unsupported verifier arguments')
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE',None)
    script = HERE/'capsule'/AUDIT/'check.py'
    with tempfile.TemporaryDirectory(prefix='p104-jensen-benchmark-replay-') as temporary:
        command = [sys.executable,'-I','-X','pycache_prefix='+temporary+'/bytecode']
        command += ['-O'] if sys.flags.optimize else []
        command += ['-B',str(script)]
        with (Path(temporary)/'stdout.json').open('wb+') as out, (Path(temporary)/'stderr.txt').open('wb+') as err:
            run = subprocess.run(command,cwd=HERE/'capsule',env=env,stdout=out,stderr=err,
                                 timeout=60,preexec_fn=child_limits)
            out.seek(0); actual = out.read()
            err.seek(0); errors = err.read()
        need(run.returncode == 0 and not errors, 'scientific subprocess failed: '+errors.decode(errors='replace')[:4000])
        need(actual == expected, 'complete original scientific output equality')
    result = json.loads(actual)
    need(result['status'] == 'PASS_SCOPED_HYPOTHETICAL_145_SPLIT_COMPILER_FEASIBILITY' and
         result['profile_is_hypothetical'] is True and result['physical_word'] is None and result['new_kappa'] is None, 'scope marker')
    need(len(result['controls']) == 24 and
         all(v['outcome'] == 'rejected' for v in result['controls'].values()), 'all original mutation controls')
    authenticate()
    print('PASS_P104_JENSEN_COMPILER_BENCHMARK')
    print(json.dumps({'complete_original_output_sha256':sha(actual),
                      'points':result['points'],'uniform_threshold':result['uniform_threshold'],
                      'mutation_controls_rejected':24,'physical_word':None,
                      'new_kappa':None,'hypothetical_compiler_only':True},sort_keys=True,separators=(',',':')))


if __name__ == '__main__':
    main()
