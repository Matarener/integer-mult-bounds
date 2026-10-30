"""Actual optimized CLI mutants and boundary/cleanup checks.

Nick Petalas. Apache-2.0. Copies are owned regular bytes, never mode copies.
"""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

from runpy import run_path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(path):
    s = path.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_uid == os.getuid(), 'unowned regular file')
    return dict(device=str(s.st_dev), inode=str(s.st_ino), mode=s.st_mode,
                uid=s.st_uid, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def copy_regular(source, target):
    before = identity(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as f:
        f.write(source.read_bytes())
    after = identity(target)
    require((before['device'], before['inode']) != (after['device'], after['inode']),
            'copy aliases source')
    require(before['sha256'] == after['sha256'] and identity(source) == before,
            'copy changed source')


def boundary(v):
    m = v['load']('boundary_machine', PACKAGE / 'sweep.py')
    failures = 0
    cases = [(1, 1, (True,), 0), (4, 0, (True,), 1), (4, 4, (True,), 1),
             (4, 2, (), 1), (4, 2, (1,), 1), (4, 2, [True], 1),
             (4, 2, (True,), 4), (True, 1, (True,), 0)]
    for args in cases:
        try:
            m.Shape(*args)
        except ValueError:
            failures += 1
        else:
            raise ValueError('malformed shape accepted')
    for count in (0, -1, True, 17, 4097):
        try:
            m.Sweep(m.Shape(4, 2, (True,), 2)).run(count, lambda _: None)
        except ValueError:
            failures += 1
        else:
            raise ValueError('malformed count accepted')
    runner = m.Sweep(m.Shape(4, 2, (False, True), 2))
    seen = 0

    def interrupted(_):
        nonlocal seen
        seen += 1
        if seen == 5:
            raise RuntimeError('consumer interruption')

    try:
        runner.run(16, interrupted)
    except RuntimeError as exc:
        require(str(exc) == 'consumer interruption', 'wrong failure')
    else:
        raise ValueError('interruption lost')
    require(seen == 5 and all(t.head == 0 and not any(t.cells) for t in
                (runner.address, runner.bank, runner.total, runner.output)),
            'failed-run private return differs')
    try:
        runner.run(1, lambda _: None)
    except ValueError:
        failures += 1
    else:
        raise ValueError('single-use gate lost')
    return dict(boundary_rejections=failures, interrupted_headers=seen)


def child(root):
    code = (
        "import runpy; from pathlib import Path; "
        "v=runpy.run_path('research/twiddle-address-sweep/verify.py',run_name='control'); "
        "c=v['sources'](); p=Path('research/twiddle-address-sweep'); "
        "m=v['load']('control_machine',p/'sweep.py'); "
        "o=v['load']('control_oracle',p/'independent.py'); "
        "v['check_stream'](m.Shape(4,2,(False,True),2),128,m,o,c); "
        "print('PASS_OPTIMIZED_SWEEP_SMOKE')"
    )
    argv = [sys.executable, '-I', '-O', '-W', 'error', '-B', '-c', code]
    proc = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=30)
    return dict(argv=argv, exit=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def arithmetic_mutants(root, target, original):
    mutations = [
        ('subtract', 'carry = self.xor(self.and_(z, addend), self.and_(mixed, carry))',
         'carry = 0', 'named exponent differs'),
        ('branch', 'if position == h and t < h:',
         'if False:', 'named exponent differs'),
        ('mask', 'beta = self.bank.read()',
         'beta = self.bank.read() ^ 1', 'named exponent differs'),
        ('movement', 'self.moves += 1', 'self.moves += 0', 'exact data invoice differs'),
        ('clear', 'self.cells[self.head] = bit',
         'self.cells[self.head] = bit if bit else self.cells[self.head]',
         'named exponent differs'),
    ]
    records = []
    for label, old, new, message in mutations:
        require(original.decode().count(old) == 1, 'ambiguous mutation')
        target.write_bytes(original.replace(old.encode(), new.encode()))
        record = child(root)
        require(record['exit'] != 0 and message in record['stderr'],
                'mutant did not fail at expected gate: ' + label)
        records.append(dict(name=label, **record))
        target.write_bytes(original)
    return records


def cli_controls():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    paths = [p.relative_to(ROOT) for p in PACKAGE.iterdir() if p.is_file()]
    paths += [Path(r['path']) for r in manifest['files'] if r['usage'] == 'input']
    before = {str(p): identity(ROOT / p) for p in paths}
    root = Path(tempfile.mkdtemp(prefix='sweep-controls-'))
    try:
        for path in paths:
            copy_regular(ROOT / path, root / path)
        target = root / 'research/twiddle-address-sweep/sweep.py'
        records = arithmetic_mutants(root, target, target.read_bytes())
        source = root / 'research/synthetic-twiddle-circuit/circuit.py'
        raw = source.read_bytes()
        source.write_bytes(raw + b'\n# changed input\n')
        record = child(root)
        require(record['exit'] != 0 and 'input hash differs' in record['stderr'],
                'changed source accepted')
        records.append(dict(name='source_hash', **record))
        source.unlink()
        record = child(root)
        require(record['exit'] != 0 and 'missing regular input' in record['stderr'],
                'missing source accepted')
        records.append(dict(name='missing_source', **record))
        with source.open('xb') as f:
            f.write(raw)
        record = child(root)
        require(record['exit'] == 0 and 'PASS_OPTIMIZED_SWEEP_SMOKE' in record['stdout'],
                'valid optimized retry failed')
        records.append(dict(name='valid_retry', **record))
        require({str(p): identity(ROOT / p) for p in paths} == before,
                'control changed source bytes or identity')
    finally:
        # Only paths created by this invocation; lstat before unlink, no chmod.
        for path in paths:
            p = root / path
            if p.exists():
                identity(p)
                p.unlink()
        for directory in sorted((p for p in root.rglob('*') if p.is_dir()),
                                key=lambda p: len(p.parts), reverse=True):
            s = directory.lstat()
            require(stat.S_ISDIR(s.st_mode) and s.st_uid == os.getuid(), 'unowned directory')
            directory.rmdir()
        root.rmdir()
    return records


def run():
    v = run_path(str(PACKAGE / 'verify.py'), run_name='controls')
    result = dict(status='PASS_SWEEP_CONTROLS', boundary=boundary(v), cli=cli_controls())
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    run()
