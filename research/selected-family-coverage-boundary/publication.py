#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Actual Git-free replay and CLI failure controls for this package.

Clear1nsight with substantial OpenAI assistance. Copies only this package and
its declared source archive into an isolated temporary tree. No original input
is edited. This verifies portability and rejection, not native semantics.
"""
from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inventory(root):
    return {str(path.relative_to(root)): [sha256(path.read_bytes()).hexdigest(),
                stat.S_IMODE(path.stat().st_mode)]
            for path in sorted(root.rglob('*')) if path.is_file()}


def execute(package, env, success, reason=None):
    run = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                         cwd=package.parents[1], env=env, capture_output=True,
                         text=True, timeout=150)
    if success:
        need(run.returncode == 0, 'portable replay failed: '+run.stderr[-2000:])
        lines = [line[12:] for line in run.stdout.splitlines() if line.startswith('RESULT_JSON=')]
        need(len(lines) == 1, 'one portable scientific result')
        canonical = json.dumps(json.loads(lines[0]), sort_keys=True, separators=(',', ':'))
        return sha256(canonical.encode()).hexdigest()
    need(run.returncode != 0 and reason in run.stderr, 'CLI mutant not rejected by expected guard')
    return None


def main():
    need((ROOT/ARCHIVE).is_file(), 'original source archive required')
    with tempfile.TemporaryDirectory(prefix='research-portable-') as temp:
        root = Path(temp)
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        source = root/ARCHIVE
        source.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/ARCHIVE, source)
        need(not (root/'.git').exists(), 'export has no Git metadata')
        env = dict(os.environ, PATH='', PYTHONDONTWRITEBYTECODE='1')
        need(shutil.which('git', path=env['PATH']) is None, 'Git unavailable to replay')
        before = inventory(root)
        receipt = execute(package, env, True)
        need(before == inventory(root), 'portable replay changed exported bytes or modes')
        expected = package/'RESULT.json'
        original_result = expected.read_bytes()
        value = json.loads(original_result)
        need(value['schema_version'] == 1, 'version-one receipt')
        value['schema_version'] = True
        expected.write_text(json.dumps(value))
        execute(package, env, False, 'typed result mismatch')
        expected.write_bytes(original_result)
        held = source.with_name(source.name+'.held')
        source.rename(held)
        try:
            execute(package, env, False, 'regular')
        finally:
            held.rename(source)
        with source.open('r+b') as stream:
            first = stream.read(1)
            stream.seek(0)
            stream.write(bytes([first[0] ^ 1]))
        try:
            execute(package, env, False, 'archive hash')
        finally:
            shutil.copy2(ROOT/ARCHIVE, source)
        need(before == inventory(root), 'controls did not restore their isolated snapshot')
        print('PASS_GIT_FREE_PUBLICATION package='+HERE.name+' files='+str(len(before))+
              ' canonical_receipt_sha256='+receipt+' cli_rejections=3 bytes_and_modes_unchanged=true')


if __name__ == '__main__':
    main()
