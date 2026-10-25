"""Semantic and actual optimized-CLI controls. Apache-2.0."""

import json
import os
from itertools import islice
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from algebra import (HERE, WIDTH, ZERO, in_newton, load, monomial,
                     native, need, plan, wrapper)
from verify import exact_window, quarter


def rejection(operation, expected):
    try:
        operation()
    except ValueError as exc:
        need(expected in str(exc), 'wrong rejection boundary')
    else:
        raise ValueError('expected rejection was absent')


def arithmetic_controls():
    _, recipes = load()
    recipe = recipes[1092]
    rejection(lambda: exact_window(monomial(0, 3), recipe), 'nonintegral quarter')
    rejection(lambda: exact_window(monomial(1, 4), recipe), 'nonintegral ideal pair')
    w = monomial(2, 4)
    v = wrapper(w, plan(recipe['right']), inverse=True)
    incoming = quarter(v)
    dirty = monomial(511, 9)
    need(in_newton(dirty), 'dirty B9 control')
    summed = [(a[0] + b[0], a[1] + b[1])
              for a, b in zip(dirty, incoming, strict=True)]
    observed = native(summed, recipe)
    source = quarter(native(v, recipe))
    restored = [(a[0] - b[0], a[1] - b[1])
                for a, b in zip(observed, source, strict=True)]
    need(restored == native(dirty, recipe), 'arbitrary dirty translation control')
    wrong = [(a[0] + b[0], a[1] + b[1])
             for a, b in zip(native(incoming, recipe), source, strict=True)]
    need(any(z != ZERO for z in wrong), 'wrong correlation sign really fails')
    need(not in_newton(incoming), 'exact intermediate can leave B9')
    need(len(restored) == WIDTH, 'fixed output capacity')


def copy_export(destination):
    package = destination / 'research' / HERE.name
    for count, path in enumerate(islice(HERE.rglob('*'), 65), start=1):
        need(count <= 64, 'bounded package export inventory')
        need(not path.is_symlink(), 'owned package has no symlink')
        if path.is_file():
            target = package / path.relative_to(HERE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    inputs = destination / 'research/p104-rounded-collector/inputs'
    inputs.mkdir(parents=True)
    for name in ('WORD.json', 'NATIVE.json.gz'):
        source = HERE.parents[1] / 'research/p104-rounded-collector/inputs' / name
        need(source.is_file() and not source.is_symlink(), 'regular export source')
        shutil.copyfile(source, inputs / name)
    return package, inputs


def cli_controls():
    # TMPDIR is session-owned in the documented replay. No modes are changed.
    with tempfile.TemporaryDirectory(prefix='p104-module-', dir=os.environ.get('TMPDIR')) as tmp:
        package, inputs = copy_export(Path(tmp))
        command = [sys.executable, '-O', '-W', 'error', '-B', str(package / 'verify.py')]
        def run(accept):
            result = subprocess.run(command, check=False, capture_output=True,
                                    text=True, timeout=120)
            need((result.returncode == 0) == accept, 'actual optimized CLI boundary')
            if accept:
                need('PASS_P104_CORRELATED_EXACT_MODULE' in result.stdout, 'CLI success marker')
            else:
                need('ValueError' in result.stderr, 'explicit CLI rejection')
        run(True)
        receipt = package / 'RESULT.json'
        original = receipt.read_bytes()
        changed = json.loads(original)
        changed['maximal_module']['index_B9_log2'] = True
        receipt.write_text(json.dumps(changed))
        run(False)
        receipt.write_bytes(original)
        word = inputs / 'WORD.json'
        source = word.read_bytes()
        word.write_bytes(source + b' ')
        run(False)
        word.unlink()
        run(False)


def main():
    arithmetic_controls()
    cli_controls()
    print('PASS_P104_MODULE_CONTROLS arithmetic=6 optimized_cli=4')


if __name__ == '__main__':
    main()
