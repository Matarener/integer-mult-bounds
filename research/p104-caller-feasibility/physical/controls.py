#!/usr/bin/env python3
"""Actual isolated CLI controls for the source-complete format component.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
Only disposable copies are mutated. No predecessor verifier is executed.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def snapshot(directory):
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_file():
            result[str(path.relative_to(directory))] = [
                hashlib.sha256(path.read_bytes()).hexdigest(),
                stat.S_IMODE(path.stat().st_mode), path.stat().st_size]
    return result


def populate(root, destination):
    destination.mkdir()
    for name in ('verify_format.py', 'FORMAT_RESULT.json', 'SOURCE_MANIFEST.json', 'FORMAT_PROOF.md'):
        shutil.copy2(root / name, destination / name)
    shutil.copytree(root / 'inputs', destination / 'inputs', copy_function=shutil.copy2)


def command(directory, optimized):
    flags = ['-I', '-Werror', '-B']
    if optimized:
        flags.insert(1, '-O')
    start = time.perf_counter()
    process = subprocess.run([sys.executable, *flags, str(directory / 'verify_format.py')],
                             cwd=directory, text=True, capture_output=True, timeout=20)
    return process, time.perf_counter()-start


def valid_case(root, work, optimized):
    destination = work / ('optimized' if optimized else 'normal')
    populate(root, destination)
    before = snapshot(destination)
    process, seconds = command(destination, optimized)
    need(process.returncode == 0 and process.stdout.startswith('PASS_PR3609_FORMAT_TRANSFER:'),
         'valid actual CLI failed: ' + process.stderr[-2000:])
    need(snapshot(destination) == before, 'valid CLI changed source bytes or modes')
    return {'status': 'PASS', 'returncode': 0, 'regular_files_unchanged': len(before),
            'seconds': round(seconds, 6), 'optimized': optimized}


def mutate(directory, name):
    word = directory / 'inputs' / 'WORD.json'
    if name == 'missing_WORD':
        word.unlink()
        return 'missing or oversized pinned input: research/p104-rounded-collector/inputs/WORD.json'
    if name == 'corrupt_WORD':
        word.write_bytes(word.read_bytes() + b'\n')
        return 'input hash: research/p104-rounded-collector/inputs/WORD.json'
    need(name == 'Boolean_receipt', 'unknown control')
    receipt = directory / 'FORMAT_RESULT.json'
    value = json.loads(receipt.read_bytes())
    value['schema_version'] = True
    receipt.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    return 'receipt type mismatch at receipt.schema_version'


def invalid_case(root, work, name):
    destination = work / name
    populate(root, destination)
    expected = mutate(destination, name)
    before = snapshot(destination)
    process, seconds = command(destination, True)
    need(process.returncode != 0 and expected in process.stderr
         and 'PASS_PR3609_FORMAT_TRANSFER:' not in process.stdout,
         'actual CLI failed to reject the intended ' + name + ' control')
    need(snapshot(destination) == before, 'rejected CLI made an extra mutation')
    return {'status': 'REJECT_AS_EXPECTED', 'returncode': process.returncode,
            'diagnostic': expected, 'regular_files_unchanged_after_mutation': len(before),
            'seconds': round(seconds, 6)}


def run_controls(root=ROOT, work=None):
    protected = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                 for name in ('verify_format.py', 'FORMAT_RESULT.json', 'SOURCE_MANIFEST.json', 'FORMAT_PROOF.md')}
    input_before = snapshot(root / 'inputs')
    with tempfile.TemporaryDirectory(prefix='p104-format-controls-', dir=work) as temporary:
        private = Path(temporary)
        positive = [valid_case(root, private, False), valid_case(root, private, True)]
        negative = {name: invalid_case(root, private, name)
                    for name in ('missing_WORD', 'corrupt_WORD', 'Boolean_receipt')}
    need(snapshot(root / 'inputs') == input_before, 'original inputs changed')
    need(all(hashlib.sha256((root/name).read_bytes()).hexdigest() == expected
             for name, expected in protected.items()), 'original scientific files changed')
    return {'schema_version': 1, 'status': 'PASS_PR3609_FORMAT_CLI_CONTROLS',
            'positive': positive, 'negative': negative,
            'original_input_files_unchanged': len(input_before),
            'protected_source_sha256': protected,
            'scope': 'Actual normal/optimized and three rejecting disposable CLI copies; no historical suite.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run_controls(args.root, args.work)
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    print('PASS_PR3609_FORMAT_CLI_CONTROLS: normal/O immutable, missing/corrupt WORD and Boolean receipt rejected')


if __name__ == '__main__':
    main()
