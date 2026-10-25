#!/usr/bin/env python3
"""Optimized CLI failure controls. Nick Petalas. Apache-2.0."""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copy_regular(source, target):
    before = source.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(), 'unowned source')
    require(before.st_size <= 2097152, 'copy source size limit')
    raw = source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        require(stream.write(raw) == len(raw), 'partial byte copy')
    after, dest = source.lstat(), target.lstat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'source changed')
    require(stat.S_ISREG(dest.st_mode) and dest.st_uid == os.getuid()
            and (dest.st_dev, dest.st_ino) != (before.st_dev, before.st_ino), 'aliased copy')
    require(hashlib.sha256(target.read_bytes()).digest() == hashlib.sha256(raw).digest(), 'copy differs')


def fixture(root):
    own_files = sorted(p for p in HERE.iterdir() if p.is_file() and not p.is_symlink())
    require(len(own_files) <= 20, 'package file limit')
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    inputs = [ROOT / r['path'] for r in rows if r['usage'] == 'input']
    for path in own_files + inputs:
        copy_regular(path, root / path.relative_to(ROOT))
    return root / HERE.relative_to(ROOT)


def call(package):
    completed = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B', str(package / 'verify.py')],
                               capture_output=True, text=True, timeout=120,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    return completed.returncode, completed.stdout + completed.stderr


def mutation(package, filename, old, new, diagnostic):
    path = package / filename
    original = path.read_bytes()
    text = original.decode()
    require(text.count(old) == 1, 'fault target differs')
    path.write_text(text.replace(old, new))
    try:
        code, output = call(package)
        require(code != 0 and diagnostic in output, 'fault missed intended gate: ' + output[-800:])
    finally:
        path.write_bytes(original)


def main():
    with tempfile.TemporaryDirectory(prefix='streaming-twiddle-controls-') as temporary:
        package = fixture(Path(temporary))
        faults = [
            ('stream.py', 'bank[axis] |= bit << position', 'bank[axis] |= 0',
             'stream/direct exponent differs'),
            ('stream.py', 'add_bits(total, bank[axis], bit, ops)', 'add_bits(total, bank[axis], 1, ops)',
             'stream/direct exponent differs'),
            ('stream.py', 'bank[axis] = bit', 'bank[axis] = 0', 'stream/direct exponent differs'),
            ('stream.py', 'ops.and_(mixed, carry)', 'ops.and_(mixed, 0)', 'stream/direct exponent differs'),
            ('stream.py', 'return 1 << (axes * low)', 'return 1 << axes',
             'prefix residual count differs'),
            ('stream.py', 'bank[j] = 0', 'bank[j] = bank[j]', 'private registers not clear'),
            ('stream.py', 'mixed = ops.xor(left, right)', 'mixed = left ^ right',
             'Boolean gate bill differs')]
        for fault in faults:
            mutation(package, *fault)
        source = package.parents[1] / 'research/synthetic-twiddle-circuit/circuit.py'
        raw = source.read_bytes()
        source.write_bytes(raw + b'\n')
        code, output = call(package)
        require(code != 0 and 'source bytes differ' in output, 'changed source accepted')
        source.unlink()
        code, output = call(package)
        require(code != 0 and 'missing source input' in output, 'missing source accepted')
        source.write_bytes(raw)
        mutation(package, 'RESULT.json', '"PASS_STREAMING_TWIDDLE_HEADER"',
                 '"FALSE_RECEIPT"', 'evidence receipt differs')
        code, output = call(package)
        require(code == 0 and 'PASS_STREAMING_TWIDDLE_HEADER' in output, 'valid retry failed: ' + output[-800:])
    print('PASS_STREAMING_TWIDDLE_CONTROLS fault_groups=10 valid_retry=1 optimized_cli=true')


if __name__ == '__main__':
    main()
