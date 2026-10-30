#!/usr/bin/env python3
"""Authenticate and replay the scoped kappa boundary continuation.

Every replay uses a fresh repository-shaped copy. It authenticates the
complete frozen predecessor and regenerates the listed new receipts.
No network or original attachment is required.

SPDX-License-Identifier: Apache-2.0
Substantial OpenAI assistance under the user's direction.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REL = Path('research/kappa-boundary-continuation')
EXEMPT = {'MANIFEST.json', 'VALIDATION.json'}
SCOPE = (
    'Exact common81 native phase geometry conditional on scalar residual '
    'cancellation; partial-chart tariff rejection; scalar pregather '
    'obstruction; exhaustive specified binary controller census; literal '
    'partial helper releases and all31 combined both-provider profiles; '
    'exact complete owner-tail pricing; two scoped owner exchange '
    'obstructions. No completed changed native supplier or new kappa.'
)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def canonical(path, ignored_root_keys=()):
    raw = path.read_bytes()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    value = json.loads(raw)
    for key in ignored_root_keys:
        need(isinstance(value, dict) and key in value, 'Missing telemetry field: '+key)
        value.pop(key)
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def authenticate():
    manifest = json.loads((HERE/'MANIFEST.json').read_text())
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts
              and p.suffix != '.pyc'
              and p.relative_to(HERE).as_posix() not in EXEMPT}
    need(actual == set(manifest['files']), 'File set differs from manifest')
    for base, entries in ((HERE, manifest['files']), (REPO, manifest['repository_dependencies'])):
        for rel, expected in entries.items():
            p = base/rel
            need(p.resolve().is_relative_to(base) and not p.is_symlink(), 'Unsafe path: '+rel)
            need(p.stat().st_size == expected['bytes'], 'Size differs: '+rel)
            need(digest(p) == expected['sha256'], 'SHA-256 differs: '+rel)
    for item in manifest['regenerated_artifacts']:
        value = canonical(HERE/item['path'], item.get('ignored_root_keys', []))
        need(sha256(value).hexdigest() == item['canonical_json_sha256'],
             'Stored proof differs: '+item['path'])
    return manifest


def commands(scope, followup, work, replay_predecessor):
    specs = []
    def add(name, script, *args):
        specs.append((name, scope/script, list(map(str, args))))
    if replay_predecessor:
        specs.append(('frozen_predecessor_replay', scope.with_name('kappa-global-continuation')/'verify.py',
                      ['--work', str(work/'predecessor-replay')]))
    add('known_helper544_control', 'entry-retiming/positive_control.py', '--followup', followup)
    add('native_uniform81_geometry', 'native-boundary/uniform_geometry.py')
    add('partial_chart_census', 'native-boundary/partial_geometry.py')
    add('scalar_pregather_obstruction', 'native-boundary/query_envelope.py')
    add('binary_control_census', 'control-search/search_controls.py')
    add('eight_partial_release_witnesses', 'coupled-boundary/verify_candidates.py')
    add('all31_combined_partial_words', 'coupled-boundary/combine_releases.py',
        '--followup', followup, '--emit-mask', 17)
    add('complete_tariff_targets', 'invoice-experiments/screen_tariffs.py')
    add('partial_chart_tariffs', 'invoice-experiments/partial_tariffs.py')
    add('all408_owner_tail_tariffs', 'invoice-experiments/retiming_invoice.py',
        '--followup', followup, '--out', scope/'invoice-experiments/RETIMING-SCREEN.json')
    add('five_actual_profile_tariffs', 'invoice-experiments/actual_profile_screen.py')
    add('all31_joint_profile_tariffs', 'invoice-experiments/joint_profile_screen.py',
        '--followup', followup, '--cases', REL/'coupled-boundary/combined-subsets/COMBINED-SUBSETS.json')
    add('single_swap_obstruction', 'invoice-experiments/single_swap_barrier.py', '--followup', followup)
    add('fresh_slot_unit_path_obstruction', 'invoice-experiments/augmenting_path.py',
        '--followup', followup, '--out', scope/'invoice-experiments/augmenting-path',
        '--seconds', 60, '--max-depth', 32)
    add('independent_control_column_and_price_review', 'review/review.py')
    return specs


def main():
    need(__debug__, 'Run with assertions enabled; do not use python -O')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', required=True, type=Path, help='A new directory outside this package')
    ap.add_argument('--replay-predecessor', action='store_true',
                    help='Also rerun the unchanged predecessor and its retained baseline; otherwise authenticate them')
    args = ap.parse_args()
    work = args.work.expanduser().resolve()
    need(not work.exists(), '--work must name a new directory')
    need(not work.is_relative_to(HERE), '--work must be outside this package')
    manifest = authenticate()
    print(f'PASS source authentication: {len(manifest["files"])} new-scope files, {len(manifest["repository_dependencies"])} retained dependencies', flush=True)
    replay_repo = work/'integer-mult-bounds'
    replay_scope = replay_repo/REL
    shutil.copytree(HERE, replay_scope, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for rel in manifest['repository_dependencies']:
        dest = replay_repo/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO/rel, dest)
    # Cached delivered evidence must never satisfy a missing output writer.
    for item in manifest['regenerated_artifacts']:
        (replay_scope/item['path']).unlink()
    followup = replay_scope.with_name('kappa-global-continuation')/'inputs/kappa-consumer-followup'
    logs = work/'logs'
    logs.mkdir()
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    env['PYTHONPYCACHEPREFIX'] = str(work/'bytecode-cache')
    started = time.monotonic()
    receipt = {
        'status':'RUNNING', 'scope':SCOPE, 'manifest_sha256':digest(HERE/'MANIFEST.json'),
        'started_utc':datetime.now(timezone.utc).isoformat(),
        'environment':{'python':sys.version, 'platform':platform.platform(),
                       'numpy':importlib.metadata.version('numpy'), 'assertions_enabled':True},
        'authenticated_scope_files':len(manifest['files']),
        'authenticated_repository_dependencies':len(manifest['repository_dependencies']),
        'predecessor_replayed_this_run':args.replay_predecessor,
        'retained_predecessor_validation_sha256':digest(replay_scope.with_name('kappa-global-continuation')/'VALIDATION.json'),
        'commands':[], 'regenerated_artifacts':[]}
    receipt_path = work/'REPLAY.json'
    def save():
        receipt['elapsed_seconds'] = round(time.monotonic()-started, 3)
        receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    try:
        for name, script, argv in commands(replay_scope, followup, work, args.replay_predecessor):
            print('RUN  '+name, flush=True)
            log_path = logs/(name+'.log')
            t0 = time.monotonic()
            with log_path.open('w') as log:
                result = subprocess.run([sys.executable, '-B', str(script), *argv],
                    cwd=replay_repo, stdout=log, stderr=subprocess.STDOUT,
                    env=env, check=False, text=True)
            receipt['commands'].append({
                'name':name, 'script':str(script.relative_to(replay_repo)),
                'source_sha256':digest(script), 'exit_code':result.returncode,
                'elapsed_seconds':round(time.monotonic()-t0, 3),
                'log':str(log_path.relative_to(work)), 'log_sha256':digest(log_path)})
            save()
            if result.returncode:
                print(log_path.read_text()[-16000:], flush=True)
            need(result.returncode == 0, 'Replay failed: '+name)
            print('PASS '+name, flush=True)
        for item in manifest['regenerated_artifacts']:
            value = sha256(canonical(replay_scope/item['path'], item.get('ignored_root_keys', []))).hexdigest()
            need(value == item['canonical_json_sha256'], 'Regenerated payload differs: '+item['path'])
            receipt['regenerated_artifacts'].append({
                'path':item['path'], 'canonical_json_sha256':value,
                'ignored_root_keys':item.get('ignored_root_keys', []), 'matches_delivered_payload':True})
        receipt['status'] = 'PASS_SCOPED_KAPPA_BOUNDARY_CONTINUATION_REPLAY'
        receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    except Exception as exc:
        receipt['status'] = 'FAIL'
        receipt['error'] = str(exc)
        save()
        raise
    print(f'PASS canonical payloads: {len(receipt["regenerated_artifacts"])}', flush=True)
    print(receipt['status'], flush=True)
    print(receipt_path, flush=True)


if __name__ == '__main__':
    main()
