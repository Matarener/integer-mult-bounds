#!/usr/bin/env python3
"""Portable exact replay of the frozen PR5545 native subset.

Chris R/Clear1nsight with substantial OpenAI Codex assistance, Apache-2.0.
Retained native compiler, circuit definitions and dense interpreter keep credit.
"""
from pathlib import Path
import gzip
import hashlib
import json
import os
import resource
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT_SHA256 = 'fa2fe7ce93e72569f611ca810f440e6b77d92221350c51b7b6ab19ca34d6c64b'
AUDIT = 'outputs/p104-uncovered-native-audit-20261025'
BINDINGS = [
    ('outputs/p104-native-contact-audit-20261025/sources/clifford_exact.py', 'research/p104-native-channel/vendor/clifford_exact.py'),
    ('outputs/p104-native-contact-audit-20261025/sources/native_verify.py', 'research/p104-native-channel/vendor/native_verify.py'),
]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(root, name):
    path = Path(name)
    need(not path.is_absolute() and path.as_posix() == name and '..' not in path.parts, 'canonical relative file '+name)
    current = root
    for part in path.parts:
        current = current/part
        need(not current.is_symlink(), 'symlink component '+name)
    need(current.is_file(), 'regular file '+name)
    return current


def authenticate():
    sources = json.loads(regular(HERE, 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            raw = regular(ROOT, row['path']).read_bytes()
            need(sha(raw) == row['sha256'], 'canonical live input '+row['path'])
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'canonical source object '+row['path'])
    inventory = json.loads(regular(HERE, 'CAPSULE-INVENTORY.json').read_text())['files']
    actual = set()
    for folder in ('capsule', 'expected', 'original-evidence'):
        need(not (HERE/folder).is_symlink(), 'symlink frozen folder '+folder)
        for path in (HERE/folder).rglob('*'):
            need(not path.is_symlink(), 'symlink frozen member '+str(path))
            if path.is_file():
                actual.add(path.relative_to(HERE).as_posix())
    need(actual == set(inventory), 'complete capsule inventory')
    for name, expected in inventory.items():
        need(sha(regular(HERE,name).read_bytes()) == expected, 'frozen capsule byte '+name)
    for local, canonical in BINDINGS:
        need(regular(HERE, 'capsule/'+local).read_bytes() == regular(ROOT,canonical).read_bytes(), 'canonical capsule binding '+canonical)
    base = HERE/'capsule'/AUDIT
    request = json.loads((base/'REQUEST.json').read_text())
    for filename, key in [('check.py','code_sha256'),('CONTRACT.md','contract_sha256'),('INPUTS.json','inputs_sha256'),('run_pair.py','runner_sha256'),('inventory.py','inventory_code_sha256'),('INVENTORY.json','inventory_sha256'),('NOMINATION.json','nomination_sha256')]:
        need(sha((base/filename).read_bytes()) == request[key], 'original frozen request '+filename)
    expected = gzip.decompress(regular(HERE,'expected/native-subset.json.gz').read_bytes())
    need(sha(expected) == RESULT_SHA256, 'complete original scientific output')
    return expected


def child_limits():
    # POSIX virtual-address cap complements the root executor's RSS guard.
    resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))


def main():
    expected = authenticate()
    if sys.argv[1:] == ['--integrity-only']:
        print('PASS_P104_NATIVE_SUBSET_INTEGRITY_ONLY_NO_SCIENCE')
        return
    need(not sys.argv[1:], 'unsupported verifier arguments')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('P104_NATIVE_TRACE', None)
    env.pop('PYTHONOPTIMIZE', None)
    script = HERE/'capsule'/AUDIT/'check.py'
    with tempfile.TemporaryDirectory(prefix='p104-native-subset-replay-') as temporary:
        command = [sys.executable, '-I', '-X', 'pycache_prefix='+temporary+'/bytecode']
        command += ['-O'] if sys.flags.optimize else []
        command += ['-B', str(script)]
        with (Path(temporary)/'stdout.json').open('wb+') as out, (Path(temporary)/'stderr.txt').open('wb+') as err:
            run = subprocess.run(command, cwd=HERE/'capsule', env=env, stdout=out, stderr=err, timeout=70, preexec_fn=child_limits)
            out.seek(0); actual = out.read()
            err.seek(0); errors = err.read()
        need(run.returncode == 0 and not errors, 'scientific subprocess failed: '+errors.decode(errors='replace')[:4000])
        need(actual == expected, 'complete frozen scientific output equality')
    result = json.loads(actual)
    need(result['status'] == 'PASS_SCOPED_HIGH_RANK_AND_PRIVATE_NATIVE_MAPS' and result['kappa_claim'] is None, 'scoped result only')
    authenticate()
    print('PASS_P104_NATIVE_SUBSET_INDEPENDENT_AUDIT')
    print(json.dumps({'coverage':{k:v for k,v in result['coverage'].items() if k != 'remaining_pairs_list'}, 'complete_original_output_sha256':sha(actual), 'full_parent_admitted':False, 'new_kappa':None},sort_keys=True))


if __name__ == '__main__':
    main()
