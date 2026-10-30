"""Actual optimized CLI rejection controls in owned regular byte copies."""

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copy_regular(source, target):
    before = source.lstat()
    require(stat.S_ISREG(before.st_mode), 'source is not regular')
    require(before.st_uid == os.getuid(), 'source not owned by current user')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as handle:
        require(handle.write(source.read_bytes()) == before.st_size, 'partial copy')
    after = target.lstat()
    require(after.st_uid == os.getuid() and stat.S_ISREG(after.st_mode), 'unsafe copy')
    require((before.st_dev, before.st_ino) != (after.st_dev, after.st_ino), 'inode alias')


def run_cli(root, success, reason):
    script = root / 'research/synthetic-twiddle-tapes/verify.py'
    result = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B', str(script)],
                            cwd=root, capture_output=True, text=True, timeout=120)
    require((result.returncode == 0) == success, 'unexpected CLI status: ' + reason)
    if reason:
        require(reason in result.stderr, 'CLI failed for an unexpected reason')
    return {'control': reason or 'valid optimized CLI', 'exit': result.returncode}


def main():
    rows = []
    with tempfile.TemporaryDirectory(prefix='twiddle-tapes-controls-') as directory:
        root = Path(directory)
        package = root / 'research/synthetic-twiddle-tapes'
        for path in sorted(HERE.iterdir()):
            if path.is_file() and not path.is_symlink():
                copy_regular(path, package / path.name)
        pins = json.loads((HERE / 'SOURCES.json').read_text())
        for row in pins['files']:
            if row['usage'] == 'input':
                copy_regular(HERE.parents[1] / row['path'], root / row['path'])
        rows.append(run_cli(root, True, ''))
        path = package / 'machine.py'
        original = path.read_text()
        changes = [
            ('a & b if op == \'A\' else a ^ b', 'a ^ b if op == \'A\' else a & b',
             'sequential result mismatch'),
            ('self.moves += 1', 'self.moves += 2', 'operation invoice mismatch'),
            ('    clear_private(wires)\n', '    rewind(wires)\n', 'tape return invariant failed'),
            ('    rewind(program)\n', '    # Fault: program head not restored.\n',
             'tape return invariant failed'),
        ]
        for old, new, reason in changes:
            require(original.count(old) == 1, 'ambiguous mutation')
            path.write_text(original.replace(old, new))
            rows.append(run_cli(root, False, reason))
            path.write_text(original)
        source = root / 'research/synthetic-twiddle-circuit/circuit.py'
        data = source.read_bytes()
        source.write_bytes(data + b'\n# Source fault.\n')
        rows.append(run_cli(root, False, 'source hash mismatch'))
        source.unlink()
        rows.append(run_cli(root, False, 'missing source'))
        with source.open('xb') as handle:
            require(handle.write(data) == len(data), 'partial source restoration')
        receipt = package / 'RESULT.json'
        data = receipt.read_bytes()
        receipt.write_text('{}\n')
        rows.append(run_cli(root, False, 'committed result mismatch'))
        receipt.write_bytes(data)
        rows.append(run_cli(root, True, ''))
        # The temporary root contains only files/directories created in this call.
        for path in root.rglob('*'):
            info = path.lstat()
            require(info.st_uid == os.getuid() and not stat.S_ISLNK(info.st_mode),
                    'unexpected temporary ownership or link')
    print(json.dumps({'status': 'PASS_TWIDDLE_TAPE_CLI_CONTROLS', 'runs': rows}))


if __name__ == '__main__':
    main()
