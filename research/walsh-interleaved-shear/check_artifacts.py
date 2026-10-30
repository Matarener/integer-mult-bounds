#!/usr/bin/env python3
"""Portable CLI and damaged-artifact controls; Jerry Chen/Codex, Apache-2.0."""
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def snapshot(root):
    return {str(p.relative_to(root)): (sha256(p.read_bytes()).hexdigest(),
                                      p.stat().st_mode & 0o777)
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='walsh-shear-') as directory:
        root = Path(directory)
        package = root / 'relocated-package'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        before = snapshot(package)
        environment = os.environ.copy()
        environment['PATH'] = ''
        environment.pop('PYTHONPATH', None)
        environment.pop('PYTHONOPTIMIZE', None)
        argv = [sys.executable, '-I', '-O', '-W', 'error', '-B',
                str(package / 'verify.py')]

        def replay():
            return subprocess.run(argv, cwd=root, env=environment, text=True,
                                  capture_output=True, timeout=120, check=False)

        good = replay()
        require(good.returncode == 0, 'Git-free portable replay: ' + good.stderr)
        require(json.loads(good.stdout)['status'] == 'PASS_WALSH_INTERLEAVED_SHEAR',
                'portable success marker')
        require(snapshot(package) == before, 'portable replay changed files or modes')

        receipt = json.loads((package / 'RESULT.json').read_text())
        receipt['no_new_kappa'] = 1  # True == 1 in Python; the receipt must be typed.
        certificate = json.loads((package / 'WITNESSES.json').read_text())
        certificate['rows'] = certificate['rows'][:-1]
        cases = (
            ('context-bit-flip', 'context/pr6129-PROOF.md', b'corrupted\n',
             'context source hash'),
            ('missing-context', 'context/pr6140-README.md', None,
             'FileNotFoundError'),
            ('missing-witness-cli', 'WITNESSES.json', json.dumps(certificate).encode(),
             'witness count'),
            ('boolean-as-integer-receipt', 'RESULT.json', json.dumps(receipt).encode(),
             'committed result differs from computed result'),
        )
        rejected = []
        for name, path, replacement, reason in cases:
            file = package / path
            original = file.read_bytes()
            mode = file.stat().st_mode & 0o777
            if replacement is None:
                file.unlink()
            else:
                file.write_bytes(replacement)
            try:
                bad = replay()
                require(bad.returncode != 0 and reason in bad.stderr,
                        'wrong failure for ' + name + ': ' + bad.stderr)
                require('PASS_WALSH_INTERLEAVED_SHEAR' not in bad.stdout,
                        'damaged artifact printed success: ' + name)
                rejected.append(name)
            finally:
                file.write_bytes(original)
                file.chmod(mode)
        require(snapshot(package) == before, 'private controls did not restore bytes/modes')
    print(json.dumps({'status': 'PASS_WALSH_SHEAR_ARTIFACT_CONTROLS',
                      'git_free_optimized_replay': True, 'unchanged_bytes_and_modes': True,
                      'rejected': rejected}, sort_keys=True))


if __name__ == '__main__':
    main()
