#!/usr/bin/env python3
"""Replay PR2947 with its single aliased-temporary-root fixture corrected.

All external executable inputs are authenticated before compilation. The
frozen package and production checker are never written. Stable checkout
inputs and POSIX directory/symlink permissions are required for full coverage.
Arham Tahir, OpenAI Codex assistance; retains Nick Petalas's replay and credit.
Apache-2.0.
"""
import importlib.machinery
import json
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/selected-inventory-fail-closed'


def source(name):
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    matches = [row for row in rows if row['path'] == name and row['usage'] == 'input']
    if len(matches) != 1:
        raise ValueError('missing unique live source pin: ' + name)
    raw = (ROOT / name).read_bytes()
    if sha256(raw).hexdigest() != matches[0]['sha256']:
        raise ValueError('live source differs: ' + name)
    return raw


def local_module(name, raw):
    module = ModuleType('_native_replay_' + name.replace('.', '_'))
    module.__file__ = str(ARCHIVE / name)
    original = importlib.machinery.SourceFileLoader.get_code

    def fresh_code(loader, fullname):
        if Path(loader.path).resolve() == ARCHIVE / 'check.py':
            return compile(source('research/selected-inventory-fail-closed/check.py'),
                           loader.path, 'exec')
        return original(loader, fullname)

    # test_inventory.py imports check.py through a SourceFileLoader. Load its
    # authenticated source too, so an adjacent pyc cannot replace the traversal.
    with mock.patch.object(importlib.machinery.SourceFileLoader, 'get_code', fresh_code):
        exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def adapter():
    module = ModuleType('_native_fixture_adapter')
    module.__file__ = str(HERE / 'fixture_adapter.py')
    exec(compile((HERE / 'fixture_adapter.py').read_bytes(), module.__file__, 'exec'),
         module.__dict__)
    return module


def archived_tests(repaired):
    raw = source('research/selected-inventory-fail-closed/test_inventory.py')
    return local_module('test_inventory.py', adapter().repair_fixture(raw) if repaired else raw)


def require_complete(result):
    if result.testsRun != 59 or result.skipped or not result.wasSuccessful():
        raise ValueError('native replay requires all 59 groups to pass without skips')


def replay():
    # Authenticate every live input before executing the archived replay.
    for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']:
        if row['usage'] == 'input':
            source(row['path'])
    run = local_module('verify.py', source('research/selected-inventory-fail-closed/verify.py'))

    def load(name):
        if name == 'test_inventory.py':
            return archived_tests(repaired=True)
        return local_module(name, source('research/selected-inventory-fail-closed/' + name))

    run.local_module = load

    class CompleteRunner(unittest.TextTestRunner):
        def run(self, suite):
            result = super().run(suite)
            require_complete(result)
            return result

    # Keep the archive's own exact suite count and require actual execution too.
    with mock.patch.object(run.unittest, 'TextTestRunner', CompleteRunner):
        run.main()
    print('PASS_SELECTED_INVENTORY_NATIVE_REPLAY fixture_statements_changed=1 no_new_kappa')


if __name__ == '__main__':
    replay()
