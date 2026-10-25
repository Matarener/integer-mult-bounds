#!/usr/bin/env python3
"""Reject changed source and witness bytes in isolated exact replays."""
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    inputs = json.loads((PACKAGE / 'VERIFY.json').read_text())['inputs']
    checks = []
    with tempfile.TemporaryDirectory(prefix='two-band-width-mutations-') as temp:
        root = Path(temp)
        package = root / 'research' / PACKAGE.name
        shutil.copytree(PACKAGE, package, copy_function=shutil.copyfile,
                        ignore=shutil.ignore_patterns('__pycache__'))
        for name in inputs:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        source = root / inputs[0]
        certificate = package / 'WITNESSES.json.gz'
        original_source, original_certificate = source.read_bytes(), certificate.read_bytes()
        witness = json.loads(gzip.decompress(original_certificate))
        witness['calls'][0]['sites'][0]['helper_coefficient'] = '2'
        changed_certificate = gzip.compress(json.dumps(witness).encode(), mtime=0)
        mutations = [
            ('source_bytes', source, original_source[:-1] + bytes([original_source[-1] ^ 1]),
             'A pinned live source changed'),
            ('witness_coefficient', certificate, changed_certificate,
             'The retained exact receipt differs'),
        ]
        env = os.environ.copy()
        env.pop('PYTHONOPTIMIZE', None)
        for name, target, changed, message in mutations:
            for optimized in (False, True):
                source.write_bytes(original_source)
                certificate.write_bytes(original_certificate)
                target.write_bytes(changed)
                command = [sys.executable, '-I', '-B']
                if optimized:
                    command.append('-O')
                command.append(str(package / 'verify.py'))
                result = subprocess.run(command, cwd=root, env=env, capture_output=True,
                                        text=True, timeout=120)
                need(result.returncode != 0 and message in result.stderr,
                     'A changed scientific input was not rejected: ' + name)
                checks.append({'mutation': name, 'optimized': optimized, 'result': 'REJECT'})
    need(len(checks) == 4, 'The mutation coverage differs')
    print('PASS_TWO_FULL_WIDTH_MUTATIONS checks=4 normal_and_optimized=true')


if __name__ == '__main__':
    main()
