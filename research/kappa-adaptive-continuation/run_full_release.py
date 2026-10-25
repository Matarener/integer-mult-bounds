#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Adopt the exact PR3815 allocation into a fresh PR3734 replay copy.

Only ORDER, FILL, PROFILE and PRICE change. All published source files remain
immutable. The original complete-admission wrapper runs without edits.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

P = Path(__file__).resolve().parent
S = P / 'sources/PR3815'
BASE = S / 'research/staged544-producer-return'
CLOCK = S / 'research/staged544-clock-ceiling'
CHANGED = ['PRICE.json', 'inputs/FILL.json.gz', 'inputs/ORDER.json', 'inputs/PROFILE.json']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def verify_source():
    pins = read(P / 'sources/UPSTREAM.json')
    for name, pin in pins['pr3815_files'].items():
        content = (S / name).read_bytes()
        assert hashlib.sha256(content).hexdigest() == pin['sha256'], name
        assert hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == pin['git_blob_sha1'], name
    return pins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--fresh-native', action='store_true',
                        help='rebuild both native providers; default authenticates unchanged cached native evidence')
    parser.add_argument('--assemble-only', action='store_true')
    args = parser.parse_args()
    assert __debug__, 'assertions required'
    work = args.work.resolve()
    assert not work.exists(), 'fresh external work directory required'
    assert not work.is_relative_to(S), 'source directory is immutable'
    pins = verify_source()
    from check_clock import check
    independent = check()
    work.mkdir(parents=True)
    write(work / 'INDEPENDENT-CLOCK.json', independent)
    candidate = work / 'candidate'
    shutil.copytree(BASE, candidate)
    for name in CHANGED:
        shutil.copy2(CLOCK / name, candidate / name)
    base_files = {f.relative_to(BASE).as_posix(): sha(f) for f in BASE.rglob('*') if f.is_file()}
    current_files = {f.relative_to(candidate).as_posix(): sha(f) for f in candidate.rglob('*') if f.is_file()}
    assert set(base_files) == set(current_files)
    actual_changes = sorted(name for name in base_files if base_files[name] != current_files[name])
    assert actual_changes == CHANGED, actual_changes
    bindings = dict(status='PASS_EXACT_FOUR_FILE_CLOCK_ADOPTION',
                    source_commit=pins['pr3815_commit'],
                    wrapper_sha256=sha(candidate / 'full_replay.py'),
                    replay_archive_sha256=sha(candidate / 'REPLAY-INPUTS.tar.gz'),
                    changed_files={name: dict(before=base_files[name], after=current_files[name]) for name in CHANGED},
                    unchanged_file_count=len(base_files) - len(CHANGED),
                    fresh_native=args.fresh_native)
    write(work / 'ADOPTION.json', bindings)
    if args.assemble_only:
        print(bindings['status'], flush=True)
        return
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
                       PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    environment.pop('PYTHONOPTIMIZE', None)
    command = [sys.executable, '-B', str(candidate / 'full_replay.py'), '--work', str(work / 'full')]
    if not args.fresh_native:
        command.append('--reuse-current-native')
    started = time.monotonic()
    with (work / 'FULL-REPLAY.log').open('w') as log:
        process = subprocess.run(command, env=environment, stdout=log, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL)
    elapsed = time.monotonic() - started
    run = dict(command=command, elapsed_seconds=elapsed, exit_code=process.returncode,
               python=sys.version, platform=platform.platform(), log_sha256=sha(work / 'FULL-REPLAY.log'))
    write(work / 'RUN.json', run)
    assert process.returncode == 0, 'full replay failed; inspect FULL-REPLAY.log'
    result = read(work / 'full/RESULT.json')
    assert result['status'] == 'PASS_STAGED544_COMPLETE_CONDITIONAL_RELEASE'
    target = Fraction(read(CLOCK / 'PRICE.json')['root_lower']) - Fraction(1, 10**46) - Fraction(1, 10**70)
    old = Fraction(read(BASE / 'PRICE.json')['root_lower']) - Fraction(1, 10**46) - Fraction(1, 10**70)
    assert Fraction(result['kappa']) == target and target > old
    verify_source()
    write(work / 'RESULT.json', dict(status='PASS_ADOPTED_CLOCK_COMPLETE_CONDITIONAL_RELEASE',
          kappa_rational=str(target), gain_rational=str(target - old),
          root_lower=read(CLOCK / 'PRICE.json')['root_lower'],
          root_upper=read(CLOCK / 'PRICE.json')['root_upper'],
          full_replay_result=result, adoption=bindings, run=run,
          scope='Fresh complete admission for a changed clock/fill. Unchanged native providers and retained ancestry are authenticated from pinned receipts unless --fresh-native is supplied. All inherited theorem assumptions remain.'))
    print('PASS_ADOPTED_CLOCK_COMPLETE_CONDITIONAL_RELEASE', flush=True)


if __name__ == '__main__':
    main()
