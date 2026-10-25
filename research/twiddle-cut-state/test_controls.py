#!/usr/bin/env python3
"""Actual optimized CLI rejection controls. Nick Petalas. Apache-2.0."""

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
    raw = source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        require(stream.write(raw) == len(raw), 'partial byte copy')
    after = source.lstat()
    dest = target.lstat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'source changed')
    require(stat.S_ISREG(dest.st_mode) and dest.st_uid == os.getuid()
            and (dest.st_dev, dest.st_ino) != (before.st_dev, before.st_ino), 'aliased copy')
    require(hashlib.sha256(target.read_bytes()).digest() == hashlib.sha256(raw).digest(), 'copy differs')


def fixture(root):
    own_files = sorted(path for path in HERE.iterdir() if path.is_file() and not path.is_symlink())
    require(len(own_files) <= 20, 'package file limit')
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    inputs = [ROOT / row['path'] for row in sources if row['usage'] == 'input']
    for path in own_files + inputs:
        copy_regular(path, root / path.relative_to(ROOT))
    return root / HERE.relative_to(ROOT)


def call(package):
    completed = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B', str(package / 'verify.py')],
                               capture_output=True, text=True, timeout=90,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    return completed.returncode, completed.stdout + completed.stderr


def changed_cli(package, filename, old, new, diagnostic):
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
    with tempfile.TemporaryDirectory(prefix='twiddle-cut-controls-') as temporary:
        package = fixture(Path(temporary))
        mutations = [
            ('states.py', 'return bands * (tail + 1)', 'return bands', 'physical residual count differs'),
            ('states.py', 'comb(d, active) * constants(active, h, low, bottom)',
             'constants(active, h, low, bottom)', 'physical residual count differs'),
            ('states.py', 'd * ((1 << h) - 1) + 1', 'd * ((1 << h) - 1)', 'physical residual count differs'),
            ('states.py', "return (count_states(d, h, low, bottom) - 1).bit_length()",
             'return count_states(d, h, low, bottom).bit_length()', 'sharp bit bound differs'),
            ('states.py', 'return tops + axes * low + axes * width * chunks, low, bottom',
             'return tops + axes * low + axes * width * chunks, 0, bottom', 'physical residual count differs'),
        ]
        for mutation in mutations:
            changed_cli(package, *mutation)
        source = package.parents[1] / 'research/synthetic-twiddle-circuit/circuit.py'
        raw = source.read_bytes()
        source.write_bytes(raw + b'\n')
        code, output = call(package)
        require(code != 0 and 'source bytes differ' in output, 'changed source accepted')
        source.unlink()
        code, output = call(package)
        require(code != 0 and 'missing source input' in output, 'missing source accepted')
        source.write_bytes(raw)
        changed_cli(package, 'RESULT.json', '"PASS_TWIDDLE_CUT_STATES"',
                    '"FALSE_RECEIPT"', 'evidence receipt differs')
        code, output = call(package)
        require(code == 0 and 'PASS_TWIDDLE_CUT_STATES' in output, 'valid retry failed: ' + output[-800:])
    print('PASS_TWIDDLE_CUT_CONTROLS fault_groups=8 valid_retry=1 optimized_cli=true')


if __name__ == '__main__':
    main()
