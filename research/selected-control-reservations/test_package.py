#!/usr/bin/env python3
"""Git-free source/receipt controls for the raw reservation binding.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import shutil
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(script, optimized):
    env = dict(os.environ, PATH='', PYTHONDONTWRITEBYTECODE='1')
    args = [sys.executable, '-I', '-B'] + (['-O'] if optimized else []) + [str(script)]
    return subprocess.run(args, cwd='/', env=env, capture_output=True, text=True, timeout=15)


def main():
    checks = []
    with TemporaryDirectory(prefix='selected-controls-') as directory:
        root = Path(directory)
        package = root / 'research' / PACKAGE.name
        shutil.copytree(PACKAGE, package)
        manifest = json.loads((PACKAGE / 'VERIFY.json').read_text())
        for name in manifest['inputs']:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        script = package / 'verify.py'
        for optimized in (False, True):
            result = run(script, optimized)
            require(result.returncode == 0 and 'PASS_SELECTED_CONTROL_RESERVATIONS' in result.stdout,
                    'portable replay failed: '+result.stderr)
            checks.append('git_free_empty_PATH_' + ('optimized' if optimized else 'normal'))
        source = root / next(x for x in manifest['inputs'] if x.endswith('WHOLECALLER-PLAN-v1.json'))
        original = source.read_bytes()
        source.write_bytes(original + b'\n')
        for optimized in (False, True):
            result = run(script, optimized)
            require(result.returncode != 0 and 'source hash:' in result.stderr, 'source mutation survived')
            checks.append('source_hash_rejection_' + ('optimized' if optimized else 'normal'))
        source.write_bytes(original)
        receipt = package / 'RESULT.json'
        data = json.loads(receipt.read_text());data['swaps'] -= 1
        receipt.write_text(json.dumps(data))
        for optimized in (False, True):
            result = run(script, optimized)
            require(result.returncode != 0 and 'receipt changed' in result.stderr, 'receipt mutation survived')
            checks.append('receipt_rejection_' + ('optimized' if optimized else 'normal'))
        receipt.unlink()
        for optimized in (False, True):
            result = run(script, optimized)
            require(result.returncode != 0 and 'missing result receipt' in result.stderr, 'missing receipt accepted')
            checks.append('missing_receipt_rejection_' + ('optimized' if optimized else 'normal'))
        data = json.loads((PACKAGE / 'RESULT.json').read_text())
        data['placement_families'][0]['f'] = True
        receipt.write_text(json.dumps(data))
        for optimized in (False, True):
            result = run(script, optimized)
            require(result.returncode != 0 and 'receipt changed' in result.stderr, 'bool/int receipt accepted')
            checks.append('typed_receipt_rejection_' + ('optimized' if optimized else 'normal'))
    print(json.dumps({'status': 'PASS_PORTABLE_RESERVATION_CONTROLS', 'checks': checks}, indent=2))


if __name__ == '__main__':
    main()
