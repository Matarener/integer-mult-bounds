#!/usr/bin/env python3
"""Portable replay of the byte-preserved P104 forward caller audit.

Chris R/Clear1nsight with substantial OpenAI Codex assistance, Apache-2.0.
Retained compiler, native and construction notices remain in the capsule.
"""
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'canonical live input '+row['path'])
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'canonical source object '+row['path'])
    inventory = json.loads((HERE/'CAPSULE-INVENTORY.json').read_text())['files']
    actual = {str(p.relative_to(HERE)) for folder in ('capsule', 'expected', 'original-evidence')
              for p in (HERE/folder).rglob('*') if p.is_file()}
    need(actual == set(inventory), 'complete capsule inventory')
    for name, sha in inventory.items():
        p = HERE/name
        need(not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest() == sha, 'frozen capsule byte '+name)
    bindings = [
        ('outputs/p104-native-contact-audit-20261025/sources/clifford_exact.py', 'research/p104-native-channel/vendor/clifford_exact.py'),
        ('outputs/p104-native-contact-audit-20261025/sources/native_verify.py', 'research/p104-native-channel/vendor/native_verify.py'),
        ('outputs/p104-caller-route-audit-v2-20261025/sources/native_inventory.py', 'research/pr4359-p7-padding/native_inventory.py'),
        ('outputs/p104-caller-route-audit-v2-20261025/sources/DATA-PHASES.json', 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'),
    ]
    for local, canonical in bindings:
        need((HERE/'capsule'/local).read_bytes() == (ROOT/canonical).read_bytes(), 'canonical capsule binding '+canonical)


def main():
    authenticate()
    expected = gzip.decompress((HERE/'expected/caller.json.gz').read_bytes())
    need(hashlib.sha256(expected).hexdigest() == 'b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009', 'complete original scientific output')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('P104_TRACE_FILE', None)
    script = HERE/'capsule/outputs/p104-caller-route-audit-v2-20261025/check.py'
    with tempfile.TemporaryDirectory(prefix='p104-caller-replay-') as temporary:
        command = [sys.executable, '-X', 'pycache_prefix='+temporary+'/bytecode']
        command += ['-O'] if sys.flags.optimize else []
        command += ['-B', str(script)]
        # A fresh bytecode namespace also isolates the separately launched child.
        with (Path(temporary)/'stdout.json').open('wb+') as out, (Path(temporary)/'stderr.txt').open('wb+') as err:
            run = subprocess.run(command, cwd=HERE/'capsule', env=env, stdout=out, stderr=err, timeout=70)
            out.seek(0); actual = out.read()
            err.seek(0); errors = err.read()
        need(run.returncode == 0 and not errors, 'scientific subprocess failed: '+errors.decode(errors='replace')[:4000])
        need(actual == expected, 'complete frozen scientific output equality')
    result = json.loads(actual)
    need(result['status'] == 'PASS_SCOPED_CALLER_AND_TARGET_BINDING' and result['kappa_claim'] is None, 'scoped result only')
    authenticate()
    print('PASS_P104_FORWARD_CALLER_INDEPENDENT_AUDIT')
    print(json.dumps({'contacts':len(result['route_recipes'])*4, 'main_fields':len(result['main_targets']),
                      'fresh_helpers':result['native_checks']['fresh_helpers'],
                      'paid_jobs':sum(result['paid'].values()), 'productive_fields':sum(result['targets'].values()),
                      'complete_original_output_sha256':hashlib.sha256(actual).hexdigest(),
                      'full_parent_admitted':False, 'new_kappa':None}, sort_keys=True))


if __name__ == '__main__':
    main()
