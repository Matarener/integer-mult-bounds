"""Actual optimized CLI mutations on private copies. Nick Petalas. Apache-2.0."""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copied_tree(package, target):
    root = package.parent.parent
    inputs = json.loads((package / 'VERIFY.json').read_text())['inputs']
    paths = sorted(p for p in package.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths += [root / name for name in inputs]
    require(len(paths) <= 64, 'copy file limit')
    for source in paths:
        before = source.lstat()
        require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
                'source must be an owned regular file')
        require(before.st_size <= 1_000_000, 'copy byte limit')
        data = source.read_bytes()
        destination = target / source.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            require(stream.write(data) == len(data), 'short copy write')
        after = destination.lstat()
        require((before.st_dev, before.st_ino) != (after.st_dev, after.st_ino), 'aliased copy')
        require(hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256(data).digest(),
                'copy differs')
    return target / package.relative_to(root)


def replay(package):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B',
                             str(package / 'verify.py')], capture_output=True, text=True,
                            timeout=300, env=env)
    return result.returncode, result.stdout + result.stderr


def replace(path, old, new):
    text = path.read_text()
    require(text.count(old) == 1, 'mutation target is not unique')
    path.write_text(text.replace(old, new))


def main():
    package = Path(__file__).resolve().parent
    mutations = [
        ('arithmetic', 'else a ^ b', 'else a & b', 'wrong circuit value'),
        ('move-count', 'self.counts[2] += 1', 'self.counts[2] += 2', 'primitive invoice mismatch'),
        ('counter', "counter.write('0' if symbol == '1' else '1')",
         "counter.write('1' if symbol == '1' else '0')", 'counter underflow'),
        ('erasure', "tape.write('_')", "tape.write('0')", 'return invariant failed'),
        ('program-head', '    home(program)\n', '    program.read()\n', 'return invariant failed')]
    passed = []
    with tempfile.TemporaryDirectory(prefix='compact-tape-controls-') as temporary:
        base = Path(temporary)
        for name, old, new, expected in mutations:
            local = copied_tree(package, base / name)
            replace(local / 'machine.py', old, new)
            code, output = replay(local)
            require(code != 0 and expected in output, name + ' did not fail at intended gate: ' + output)
            passed.append(name)
        for name in ('changed-source', 'missing-source', 'receipt'):
            local = copied_tree(package, base / name)
            source = local.parent / 'synthetic-twiddle-circuit/circuit.py'
            if name == 'changed-source':
                source.write_bytes(source.read_bytes() + b'\n# changed control\n')
            elif name == 'missing-source':
                source.unlink()
            else:
                data = json.loads((local / 'RESULT.json').read_text())
                data['rejections'] += 1
                (local / 'RESULT.json').write_text(json.dumps(data))
            code, output = replay(local)
            expected = 'scientific receipt differs' if name == 'receipt' else 'source '
            require(code != 0 and expected in output, name + ' did not reject: ' + output)
            passed.append(name)
        local = copied_tree(package, base / 'valid-retry')
        code, output = replay(local)
        require(code == 0 and 'PASS_COMPACT_TWIDDLE_TAPES' in output, 'valid optimized retry failed')
    print(json.dumps({'optimized_cli_faults_rejected': passed, 'valid_optimized_retry': True}))


if __name__ == '__main__':
    main()
