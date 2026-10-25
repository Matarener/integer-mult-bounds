"""Actual optimized CLI faults on private regular byte copies. Nick Petalas, Apache-2.0."""

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copy_bytes(source, destination):
    before = source.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
            'copy source must be owned regular bytes')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        count = stream.write(source.read_bytes())
    after = destination.lstat()
    require(count == before.st_size and stat.S_ISREG(after.st_mode)
            and after.st_uid == os.getuid()
            and (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
            'private copy ownership/identity differs')


def invoke(root, succeeds):
    path = root / PACKAGE.relative_to(ROOT) / 'verify.py'
    process = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B', str(path)],
                             cwd=root, capture_output=True, text=True, timeout=90)
    require((process.returncode == 0) == succeeds,
            'unexpected optimized CLI result: ' + process.stdout + process.stderr)
    if succeeds:
        require('PASS_DIRECT_TWIDDLE_TAPES' in process.stdout, 'success marker absent')


def main():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    paths = [p for p in PACKAGE.iterdir() if p.is_file()]
    paths += [ROOT / row['path'] for row in sources['files'] if row['usage'] == 'input']
    require(len(paths) <= 32, 'copy inventory too large')
    faults = [('tapes.py', 'carry = branch & bit', 'carry = branch ^ bit'),
              ('tapes.py', 'self.bank.write(bit)', 'self.bank.write(0)'),
              ('tapes.py', 'self.bank.read(), bit, v', '0, bit, v'),
              ('tapes.py', 'self.address.seek(0)', 'self.address.seek(1)'),
              ('tapes.py', 'self.moves += 1', 'self.moves += 0'),
              ('tapes.py', 'self.bank.erase()', 'self.bank.seek(0)'),
              ('checks.py', 'else h - 1', 'else h'),
              ('RESULT.json', '"addresses":', '"wrong_addresses":')]
    with tempfile.TemporaryDirectory(prefix='direct-twiddle-controls-') as directory:
        root = Path(directory)
        for source in paths:
            copy_bytes(source, root / source.relative_to(ROOT))
        invoke(root, True)
        for name, before, after in faults:
            target = root / PACKAGE.relative_to(ROOT) / name
            original = target.read_bytes()
            text = original.decode()
            require(before in text, 'fault target absent: ' + name)
            target.write_text(text.replace(before, after, 1))
            invoke(root, False)
            target.write_bytes(original)
        source = root / 'research/synthetic-twiddle-circuit/circuit.py'
        original = source.read_bytes()
        source.write_bytes(original + b'\n# changed source\n')
        invoke(root, False)
        source.unlink()
        invoke(root, False)
        with source.open('xb') as stream:
            require(stream.write(original) == len(original), 'source restore incomplete')
        invoke(root, True)
    print('PASS_DIRECT_TWIDDLE_CONTROLS', len(faults) + 2, 'fault groups; valid retry')


if __name__ == '__main__':
    main()
