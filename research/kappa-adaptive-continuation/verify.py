#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate the complete package and replay its bounded scientific checks.

Copies the exact manifest closure into a fresh repository-shaped workspace,
deletes every expected regenerated output, reruns the listed checks, and
compares their canonical payloads. Full native execution and ordinary release
are authenticated as completed evidence, not silently claimed to be rerun.
Use run_candidate_release.py for that separate, larger computation.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import zlib

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REL = Path('research/kappa-adaptive-continuation')
EXEMPT = {'MANIFEST.json', 'VALIDATION.json'}


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def digest(path):
    h = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(path):
    return json.dumps(read(path), sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii')


def authenticate():
    manifest = read(HERE / 'MANIFEST.json')
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'
              and p.relative_to(HERE).as_posix() not in EXEMPT}
    need(actual == set(manifest['files']), 'exact scoped file inventory')
    for base, entries in ((HERE, manifest['files']), (REPO, manifest['repository_dependencies'])):
        for name, expected in entries.items():
            path = base / name
            need(path.resolve().is_relative_to(base) and not path.is_symlink(), 'safe manifest path: ' + name)
            need(path.stat().st_size == expected['bytes'] and digest(path) == expected['sha256'],
                 'exact source/file identity: ' + name)
    for item in manifest['regenerated_artifacts']:
        need(sha256(canonical(HERE / item['path'])).hexdigest() == item['canonical_json_sha256'],
             'stored canonical proof identity: ' + item['path'])
    release = read(HERE / 'evidence/full-release/RESULT.json')
    need(release['status'] == 'PASS_RECEIVER_SHARING_COMPLETE_CONDITIONAL_RELEASE',
         'authenticated completed full release')
    return manifest


def command_list(scope, work):
    commands = []

    def add(name, path, *args):
        commands.append((name, scope / path, list(map(str, args))))

    add('independent_clock', 'check_clock.py', '--out', scope / 'evidence/CLOCK.json')
    add('literal_both_provider_constructor', 'native-alternatives/construct.py',
        '--out', work / 'reconstructed-candidates')
    add('independent_receiver_algebra_and_frames', 'architecture/review_receiver.py')
    add('complete_native_receipt_bindings', 'native-alternatives/verify.py')
    add('all_shipped_native_bytes_and_actual_sources', 'replay-support/native_auth.py',
        '--reuse-root', scope / 'native-alternatives', '--out', scope / 'replay-support/REUSED-NATIVE.json')
    add('upstream_clock_owners_and_independent_dual', 'global-budget/review_pr3815.py')
    add('new_word_actual_owners_and_two_engine_price', 'global-budget/native_owner_invoice.py',
        '--base-local', scope / 'native-alternatives/native-base/native/local',
        '--extra-local', scope / 'native-alternatives/native-extra/native/local',
        '--out', scope / 'global-budget/receiver-sharing')
    add('new_inventory_global_packing_ceiling', 'global-budget/receiver_packing_ceiling.py')
    add('literal_three_pair_native_geometry', 'architecture/seven_geometry.py',
        '--out', work / 'reconstructed-geometry')
    add('exact_three_pair_packing_ceiling', 'global-budget/p3_certificate.py')
    add('entire_pair_count_family_certificate', 'architecture/pair_count_certificate.py')
    add('current_inventory_gate', 'global-budget/current_inventory_screen.py',
        '--out', scope / 'global-budget/CURRENT-INVENTORY-SCREEN.json')
    add('exact_current_remaining_budget', 'global-budget/remaining_budget.py')
    add('runtime_failure_modes', 'runtime-repair/fixtures.py',
        '--audit-script', work / 'audit_allcold.py', '--out', scope / 'runtime-repair/FIXTURES.json')
    add('modern_outer_ledger', 'global-budget/admission-review-low-memory/outer/check_ledger.py')
    add('independent_modern_outer_balance', 'global-budget/admission-review-low-memory/outer/independent_check.py')
    return commands


def check_separate_reconstruction(name, scope, work):
    """Compare decoded content without replacing pinned gzip containers.

    gzip's metadata/deflate output may vary with Python, zlib or platform.
    Native receipt checks continue to authenticate the original file bytes.
    The only normalized constructor field is its newly emitted container hash,
    and that field is first checked against the actual new container.
    """
    checked = []
    if name == 'literal_both_provider_constructor':
        original = scope / 'native-alternatives/candidate'
        fresh = work / 'reconstructed-candidates'
        expected = read(original / 'CONSTRUCTION.json')
        rebuilt = read(fresh / 'CONSTRUCTION.json')
        for tag in ('base', 'extra'):
            filename = 'BORROW-WORD-43' + tag + '.json.gz'
            old_path, new_path = original / filename, fresh / filename
            need(canonical(old_path) == canonical(new_path), 'exact reconstructed native payload: ' + tag)
            need(rebuilt['providers'][tag]['word_sha256'] == digest(new_path), 'new gzip container hash')
            checked.append(dict(path='native-alternatives/candidate/' + filename,
                canonical_json_sha256=sha256(canonical(new_path)).hexdigest(),
                authenticated_container_sha256=digest(old_path), reconstructed_container_sha256=digest(new_path)))
            rebuilt['providers'][tag]['word_sha256'] = expected['providers'][tag]['word_sha256']
        need(rebuilt == expected, 'every constructor proof field agrees after the checked container-hash substitution')
    elif name == 'literal_three_pair_native_geometry':
        for filename in ('SEVEN57-GEOMETRY.json.gz', 'SEVEN57-RESULT.json'):
            old_path = scope / 'architecture/evidence' / filename
            new_path = work / 'reconstructed-geometry' / filename
            need(canonical(old_path) == canonical(new_path), 'exact reconstructed native geometry: ' + filename)
            checked.append(dict(path='architecture/evidence/' + filename,
                canonical_json_sha256=sha256(canonical(new_path)).hexdigest(),
                authenticated_container_sha256=digest(old_path), reconstructed_container_sha256=digest(new_path)))
    return checked


def main():
    need(__debug__, 'Python assertions must be enabled')
    need(sys.version_info >= (3, 11), 'Python 3.11 or later is required by the retained outer engines')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True, help='fresh directory outside this package')
    args = parser.parse_args()
    work = args.work.expanduser().resolve()
    need(not work.exists() and not work.is_relative_to(HERE), 'fresh external replay workspace')
    manifest = authenticate()
    print('PASS exact package and completed-release authentication', flush=True)
    replay_repo = work / 'integer-mult-bounds'
    scope = replay_repo / REL
    shutil.copytree(HERE, scope, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in manifest['repository_dependencies']:
        target = replay_repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / name, target)
    for item in manifest['regenerated_artifacts']:
        (scope / item['path']).unlink()
    source = scope / 'sources/PR3815/research/staged544-producer-return'
    archive_pins = read(source / 'REPLAY-INPUTS.json')
    archive_path = source / 'REPLAY-INPUTS.tar.gz'
    need(digest(archive_path) == archive_pins['archive_sha256'], 'pinned original replay archive')
    with tarfile.open(archive_path) as archive:
        name = 'source/code/audit_allcold.py'
        payload = archive.extractfile(name).read()
        need(sha256(payload).hexdigest() == archive_pins['files'][name], 'original scientific audit source')
        (work / 'audit_allcold.py').write_bytes(payload)
    logs = work / 'logs'
    logs.mkdir()
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
                       OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONINTMAXSTRDIGITS='0')
    environment.pop('PYTHONOPTIMIZE', None)
    started = time.monotonic()
    receipt = dict(
        status='RUNNING', manifest_sha256=digest(HERE / 'MANIFEST.json'),
        started_utc=datetime.now(timezone.utc).isoformat(),
        environment=dict(python=sys.version, platform=platform.platform(),
                         zlib=zlib.ZLIB_RUNTIME_VERSION, assertions_enabled=True),
        authenticated_scope_files=len(manifest['files']),
        authenticated_repository_dependencies=len(manifest['repository_dependencies']),
        completed_full_release_sha256=digest(HERE / 'evidence/full-release/RESULT.json'),
        full_native_and_ordinary_release_rerun_this_command=False,
        scope='Fresh bounded native identity/frame, full physical owner, exact pricing/dual, geometry, runtime-boundary and two modern outer checks. Complete native executions and ordinary release are separately authenticated delivered evidence; all inherited theorem premises remain.',
        commands=[], regenerated_artifacts=[], separate_canonical_reconstructions=[])

    def save():
        receipt['elapsed_seconds'] = round(time.monotonic() - started, 3)
        (work / 'REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')

    try:
        for name, script, args in command_list(scope, work):
            print('RUN ' + name, flush=True)
            logfile = logs / (name + '.log')
            begin = time.monotonic()
            with logfile.open('w') as log:
                result = subprocess.run([sys.executable, '-B', str(script), *args],
                                        cwd=replay_repo, env=environment, stdin=subprocess.DEVNULL,
                                        stdout=log, stderr=subprocess.STDOUT)
            receipt['commands'].append(dict(name=name, script=script.relative_to(replay_repo).as_posix(),
                script_sha256=digest(script), exit_code=result.returncode,
                elapsed_seconds=round(time.monotonic() - begin, 3),
                log=logfile.relative_to(work).as_posix(), log_sha256=digest(logfile)))
            save()
            if result.returncode:
                print(logfile.read_text()[-10000:], flush=True)
            need(result.returncode == 0, 'bounded replay failed: ' + name)
            receipt['separate_canonical_reconstructions'] += check_separate_reconstruction(name, scope, work)
            print('PASS ' + name, flush=True)
        for item in manifest['regenerated_artifacts']:
            value = sha256(canonical(scope / item['path'])).hexdigest()
            need(value == item['canonical_json_sha256'], 'regenerated payload differs: ' + item['path'])
            receipt['regenerated_artifacts'].append(dict(path=item['path'],
                canonical_json_sha256=value, matches_delivered_payload=True))
        # Published source objects and the frozen predecessor must remain exact.
        for name, expected in manifest['repository_dependencies'].items():
            need(digest(replay_repo / name) == expected['sha256'], 'frozen dependency modified: ' + name)
        receipt['status'] = 'PASS_ADAPTIVE_KAPPA_CONTINUATION_BOUNDED_REPLAY'
        receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    except Exception as error:
        receipt['status'] = 'FAIL'
        receipt['error'] = str(error)
        save()
        raise
    print(receipt['status'], flush=True)
    print(work / 'REPLAY.json', flush=True)


if __name__ == '__main__':
    main()
