#!/usr/bin/env python3
"""Exercise Git-free optimized replay and corrupted-input/receipt rejection.

Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
All mutations take place in a disposable export, never in source inputs.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def main():
    manifest = json.loads((HERE / 'VERIFY.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='stage-zero-cold-') as tmp:
        dest = Path(tmp).resolve()
        if not dest.is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise ValueError('Export is outside the temporary directory')
        shutil.copytree(HERE, dest / REL, ignore=shutil.ignore_patterns('__pycache__'))
        for entry in manifest['inputs']:
            target = dest / entry
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / entry, target)
        command = [sys.executable, '-I', '-O', '-B', str(dest / REL / 'verify.py')]

        def run():
            return subprocess.run(command, cwd=dest, capture_output=True,
                                  text=True, encoding='utf-8', timeout=120)

        good = run()
        if good.returncode:
            raise ValueError(good.stderr)
        if json.loads(good.stdout) != json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8')):
            raise ValueError('Export receipt mismatch')
        source = dest / next(p for p in manifest['inputs'] if p.endswith('/DATA-PHASES.json'))
        original = source.read_bytes()
        source.write_bytes(original + b' ')
        bad_source = run()
        if bad_source.returncode == 0 or 'Changed source:' not in bad_source.stderr:
            raise ValueError('Source-corruption control did not reject')
        source.write_bytes(original)
        receipt = dest / REL / 'RESULT.json'
        result = json.loads(receipt.read_text(encoding='utf-8'))
        result['ports'] = 111
        receipt.write_text(json.dumps(result), encoding='utf-8')
        bad_receipt = run()
        if bad_receipt.returncode == 0 or 'Changed expected result' not in bad_receipt.stderr:
            raise ValueError('Receipt-corruption control did not reject')
    print('PASS_GIT_FREE_OPTIMIZED_EXPORT exact_receipt=1 changed_source_rejected=1 changed_receipt_rejected=1')


if __name__ == '__main__':
    main()
