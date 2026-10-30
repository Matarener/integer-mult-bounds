"""Exercise the real optimized CLI against isolated byte-copy corruptions."""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copy_bytes(source, destination):
    before = source.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
            'source must be an owned regular file')
    raw = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        require(stream.write(raw) == len(raw), 'short export write')
    after = destination.lstat()
    require(stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid()
            and (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
            'export must have a distinct owned regular inode')
    require(destination.read_bytes() == raw, 'export bytes differ')


def invoke(root, success, message=None):
    target = root / PACKAGE.relative_to(ROOT) / 'verify.py'
    result = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B', str(target)],
                            cwd=root, text=True, capture_output=True, timeout=120)
    require((result.returncode == 0) == success, 'wrong CLI exit: ' + result.stderr)
    if message:
        require(message in result.stderr, 'wrong rejection: ' + result.stderr)
    return dict(exit=result.returncode, stdout_sha256=hashlib.sha256(
                result.stdout.encode()).hexdigest(), stderr=result.stderr)


def main():
    require(not sys.argv[1:], 'controls accept no arguments')
    pins = json.loads((PACKAGE / 'SOURCES.json').read_text())
    inputs = [ROOT / r['path'] for r in pins['files'] if r['usage'] == 'input']
    members = sorted(p for p in PACKAGE.iterdir() if p.is_file()) + inputs
    mutations = [
        ('wrong branch', 'branch = location[i, h]', 'branch = location[i, 0]'),
        ('branch in lower index', 'for v in range(h)) + (0,)',
         'for v in range(h)) + (location[i, h],)'),
        ('wrong shift', 'tuple(reversed(total)) + (0,) * (ell - h)',
         '(0,) + tuple(reversed(total)) + (0,) * (ell - h - 1)'),
        ('wrong direction', 'if not opposite:', 'if opposite:'),
        ('lost incoming carry', "carry = gate(gates, inputs, 'xor', both, incoming)",
         "carry = gate(gates, inputs, 'xor', both, 0)"),
        ('wrong branch mask', "gate(gates, len(slots), 'and', branch, location[i, v])",
         "gate(gates, len(slots), 'xor', branch, location[i, v])"),
    ]
    with tempfile.TemporaryDirectory(prefix='twiddle-controls-') as temporary:
        root = Path(temporary)
        for path in members:
            copy_bytes(path, root / path.relative_to(ROOT))
        results = {'valid optimized CLI': invoke(root, True)}
        code = root / PACKAGE.relative_to(ROOT) / 'circuit.py'
        original = code.read_text()
        for name, old, new in mutations:
            require(original.count(old) == 1, 'ambiguous mutation')
            code.write_text(original.replace(old, new))
            message = 'gate count differs' if name == 'wrong direction' else 'header differs'
            results[name] = invoke(root, False, message)
            code.write_text(original)
        receipt = root / PACKAGE.relative_to(ROOT) / 'RESULT.json'
        original_receipt = receipt.read_bytes()
        receipt.write_text('{}\n')
        results['changed receipt'] = invoke(root, False, 'scientific receipt differs')
        receipt.write_bytes(original_receipt)
        source = root / inputs[0].relative_to(ROOT)
        original_source = source.read_bytes()
        source.write_bytes(original_source + b'\n')
        results['changed source'] = invoke(root, False, 'changed or missing source')
        source.unlink()
        results['missing source'] = invoke(root, False, 'changed or missing source')
        source.write_bytes(original_source)
        for path in members:
            require(path.read_bytes() == (root / path.relative_to(ROOT)).read_bytes(),
                    'control failed to restore bytes')
    print(json.dumps(dict(status='PASS_TWIDDLE_CLI_CONTROLS', cases=results), sort_keys=True))


if __name__ == '__main__':
    main()
