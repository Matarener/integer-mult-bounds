"""Boundary, counter and optimized CLI faults. Nick Petalas, Apache-2.0."""

from pathlib import Path
import json
import os
import stat
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controller as c
from checks import ROOT, PACKAGE, load_oracle, run_controller


def rejects(call, label):
    try:
        call()
    except (ValueError, TypeError):
        return
    raise ValueError('failed rejection: ' + label)


def counter(value, width=4):
    result = c.Binary(width, c.Tape('^' + '1' * (width - 2) + '$'))
    for _unused in range(value):
        result.change()
    return result


def counter_controls():
    cases = 0
    for a in range(16):
        for b in range(16):
            left, right = counter(a), counter(b)
            c.require(left.compare(right) == (a > b) - (a < b), 'binary comparison differs')
            left.copy(right)
            c.require(left.value() == b and right.value() == b, 'binary copy differs')
            if a + b < 16:
                left = counter(a)
                left.add(right)
                c.require(left.value() == a + b, 'binary addition differs')
            if a >= b:
                left = counter(a)
                left.sub(right)
                c.require(left.value() == a - b, 'binary subtraction differs')
            c.require(left.tape.head == right.tape.head == 0, 'counter head return differs')
            cases += 1
        scratch = counter(a)
        scratch.erase()
        c.require(not any(scratch.tape.cells) and scratch.tape.head == 0, 'counter erase differs')
    rejects(lambda: counter(15).change(), 'counter overflow')
    rejects(lambda: counter(0).change(True), 'counter underflow')
    return cases


def boundary_controls():
    text = c.encode(4, 2, 2, (True, False))
    bits = (0,) * 7
    bad = ['', text[:-1], text + '#', text.replace('L', 'X'), text.replace('-', '?'),
           text.replace('1111#', '11#', 1), '1#1##L#-#',
           '11#11##L#-#', '11#1#11#L#-#', '11#1###-#', '1' * 117]
    for item in bad:
        rejects(lambda item=item: c.Controller(item, bits), 'malformed descriptor')
    rejects(lambda: c.Controller(text, (False,) * 7), 'Boolean address masquerading as integer')
    rejects(lambda: c.Controller(text, (0,) * 6), 'address extent')
    rejects(lambda: c.encode(True, 1, 0, (True,)), 'Boolean ell')
    rejects(lambda: c.encode(4, 2, 2, (1,)), 'integer axis flag')
    # Poisoning the diagnostic decoder leaves real control execution unchanged.
    old = c.Binary.value
    try:
        c.Binary.value = lambda self: (_ for _ in ()).throw(ValueError('decoded counter used'))
        run_controller(load_oracle(), (4, 2, 2, (True, False), False), (1,) * 7)
    finally:
        c.Binary.value = old
    return len(bad) + 4


def copy_regular(source, target):
    info = source.lstat()
    c.require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid(), 'unsafe copy source')
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = source.read_bytes()
    with target.open('xb') as stream:
        written = stream.write(raw)
        c.require(written == len(raw), 'partial byte copy')
    after = target.lstat()
    c.require(stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid() and
              (info.st_dev, info.st_ino) != (after.st_dev, after.st_ino), 'copy aliases source')


def fault_controls():
    faults = (
        ('controller.py', "b['carry'] = b['branch'] & b['pending']",
         "b['carry'] = b['branch'] ^ b['pending']"),
        ('controller.py', "b['branch'] = b['input']", "b['branch'] = 0"),
        ('controller.py', "b['pending'] = b['input']", "b['pending'] = 0"),
        ('controller.py', "self.tape.write(b)", "self.tape.write(a)"),
        ('controller.py', "self.c['b'].sub(self.c['k'])", "self.c['b'].zero()"),
        ('controller.py', "self.emit('write', role, 'zero')", "self.emit('write', role, 'one')"),
        ('controller.py', "self.counts['move'] += 1", "self.counts['move'] += 0"),
        ('controller.py', "counter.erase()", "counter.zero()"),
        ('RESULT.json', 'PASS_ENCODED_TWIDDLE_CONTROLLER', 'CHANGED_RECEIPT'),
        ('input', 'changed source', ''),
    )
    root = Path(os.environ.get('TMPDIR', tempfile.gettempdir())).resolve()
    c.require(root.is_dir(), 'private TMPDIR must exist')
    with tempfile.TemporaryDirectory(prefix='encoded-controller-controls-', dir=root) as work:
        export = Path(work)
        for source in sorted(PACKAGE.rglob('*')):
            if source.is_file() and '__pycache__' not in source.parts:
                copy_regular(source, export / source.relative_to(ROOT))
        manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
        for row in manifest['files']:
            if row['usage'] == 'input':
                copy_regular(ROOT / row['path'], export / row['path'])
        package = export / PACKAGE.relative_to(ROOT)
        command = [sys.executable, '-I', '-O', '-Werror', '-B', str(package / 'verify.py')]
        positive = subprocess.run(command, cwd=export, capture_output=True, text=True, timeout=120)
        c.require(positive.returncode == 0, 'optimized positive CLI failed: ' + positive.stderr)
        for name, before, after in faults:
            target = (export / 'research/synthetic-twiddle-circuit/PROOF.md'
                      if name == 'input' else package / name)
            raw = target.read_bytes()
            if name == 'input':
                changed = raw + b'\nchanged source\n'
            else:
                c.require(raw.count(before.encode()) == 1, 'ambiguous fault anchor')
                changed = raw.replace(before.encode(), after.encode())
            target.write_bytes(changed)
            result = subprocess.run(
                command, cwd=export, capture_output=True, text=True, timeout=120)
            target.write_bytes(raw)
            c.require(result.returncode != 0, 'optimized CLI accepted fault ' + before)
        # A missing mathematical input must also fail before any science is accepted.
        target = export / 'upstream/build/sections/06-transforms.tex'
        target.unlink()
        result = subprocess.run(command, cwd=export, capture_output=True, text=True, timeout=120)
        c.require(result.returncode != 0, 'optimized CLI accepted missing mathematical input')
    return len(faults) + 1


def main():
    result = {'counter_pairs': counter_controls(), 'boundary_cases': boundary_controls(),
              'optimized_cli_faults': fault_controls()}
    print('PASS_ENCODED_CONTROLLER_CONTROLS ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
