#!/usr/bin/env python3
"""Cold export and fail-closed input/certificate controls, standard library.

Jonathan Capalbo (jon314159), with OpenAI Codex assistance. Apache-2.0.
Only fresh temporary copies are modified; source packages remain unchanged.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELATIVE = Path('research') / HERE.name
WORD = Path('research/p104-helper470-twin-rung-removal/WORD.json.gz')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def replay(root, expected_failure=None):
    process = subprocess.run([sys.executable, '-I', '-O', '-B', str(root / RELATIVE / 'verify.py')],
                             cwd=root, capture_output=True, text=True, timeout=240)
    if expected_failure is None:
        need(process.returncode == 0 and 'PASS_P104_FIXED_WORD_NEGATIVE_SCREENS' in process.stdout,
             'cold export failed: ' + process.stdout[-1000:] + process.stderr[-2000:])
    else:
        need(process.returncode != 0 and expected_failure in process.stderr,
             'control did not reject for expected reason: ' + repr(expected_failure)
             + '\n' + process.stdout[-1000:] + process.stderr[-2000:])


def main():
    with tempfile.TemporaryDirectory(prefix='p104-negative-export-') as temporary:
        root = Path(temporary)
        destination = root / RELATIVE
        shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        word = root / WORD
        word.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / WORD, word)
        # No Git objects, scratch work, or network fetches are available here.
        replay(root)

        original = word.read_bytes()
        word.write_bytes(original + b'\x00')
        replay(root, 'selected WORD bytes do not match')
        word.write_bytes(original)

        vendor = destination / 'vendor/pr6045/leakfix.py'
        original = vendor.read_bytes()
        vendor.write_bytes(original + b'\n')
        replay(root, 'vendored source drift')
        vendor.write_bytes(original)

        expected = destination / 'EXPECTED.json'
        value = json.loads(expected.read_text(encoding='utf-8'))
        value['carrier']['leak_classes'] += 1
        expected.write_text(json.dumps(value), encoding='utf-8')
        replay(root, 'semantic replay differs from EXPECTED.json')
    print('PASS_P104_NEGATIVE_PACKAGE_CONTROLS cold_export word_drift vendor_drift semantic_receipt_drift')


if __name__ == '__main__':
    main()
