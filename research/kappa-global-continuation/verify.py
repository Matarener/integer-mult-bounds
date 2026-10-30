#!/usr/bin/env python3
"""Authenticate and replay the attached-repository kappa continuation.

Every replay uses a fresh workspace-shaped copy. The retained followup is
vendored and authenticated, so no network or original attachment is needed.

SPDX-License-Identifier: Apache-2.0
Substantial OpenAI assistance under the user's direction.
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
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REL = Path('research/kappa-global-continuation')
EXEMPT = {'MANIFEST.json', 'VALIDATION.json'}
SCOPE = (
    'Source-bound native local words and transitions; nine-stage data gauges; '
    'actual helper allocation and complete preconsumer arithmetic; alternating '
    'routed record image; ordered residual-inverse algebra; scoped normalization '
    'obstruction. Native residual query/image interfaces and their complete '
    'supplier bill remain open. No new kappa or selected certificate.'
)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def canonical(path):
    raw = path.read_bytes()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    return json.dumps(json.loads(raw), sort_keys=True,
                      separators=(',', ':'), ensure_ascii=True).encode('ascii')


def authenticate():
    manifest = json.loads((HERE/'MANIFEST.json').read_text())
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts
              and p.suffix != '.pyc'
              and p.relative_to(HERE).as_posix() not in EXEMPT}
    need(actual == set(manifest['files']), 'File set differs from manifest')
    for base, entries in ((HERE, manifest['files']),
                          (REPO, manifest['repository_dependencies'])):
        for rel, expected in entries.items():
            p = base/rel
            need(p.resolve().is_relative_to(base) and not p.is_symlink(),
                 f'Unsafe manifest path: {rel}')
            need(p.stat().st_size == expected['bytes'], f'Size differs: {rel}')
            need(digest(p) == expected['sha256'], f'SHA-256 differs: {rel}')
    for item in manifest['regenerated_artifacts']:
        need(sha256(canonical(HERE/item['path'])).hexdigest()
             == item['canonical_json_sha256'],
             f'Stored canonical proof differs: {item["path"]}')
    return manifest


def commands(scope, followup, work, include_baseline):
    specs = []
    if include_baseline:
        specs.append(('retained_followup_replay', followup/'verify.py',
                      ['--work', str(work/'retained-replay')]))
    def add(name, script, *args):
        specs.append((name, scope/script, list(map(str, args))))
    sym = scope/'symmetric-transition/evidence'
    norm = scope/'normalization/RESULT.json'
    helper = scope/'helper-consumer/evidence'
    invoice = scope/'invoice-analysis/evidence'
    add('normalization', 'normalization/check_normalization.py',
        '--followup', followup, '--out', norm)
    add('native_transition', 'symmetric-transition/transition.py',
        '--followup', followup, '--out', sym)
    add('routed_residual_witness', 'symmetric-transition/residual_witness.py',
        '--followup', followup, '--evidence', sym)
    add('native_alternating_signs', 'symmetric-transition/alternating_sign.py',
        '--followup', followup, '--evidence', sym)
    add('owner_coupled_factors', 'helper-consumer/owner_coupled_factors.py',
        '--followup', followup, '--out', helper)
    add('unipotent_pair', 'helper-consumer/unipotent_pair.py',
        '--followup', followup, '--out', helper)
    add('alternating_records', 'helper-consumer/alternating_records.py',
        '--followup', followup, '--transition', scope/'symmetric-transition',
        '--out', helper)
    add('complete_invoice', 'invoice-analysis/invoice.py',
        '--followup', followup, '--out', invoice, '--emit-fill')
    add('independent_phase_review', 'invoice-analysis/review_transition.py',
        '--transition-evidence', sym, '--out', invoice/'PHASE-REVIEW.json')
    add('independent_normalization_review', 'invoice-analysis/review_normalization.py',
        '--followup', followup, '--normalization-result', norm,
        '--out', invoice/'NORMALIZATION-REVIEW.json')
    add('independent_record_review', 'helper-consumer/review_records.py',
        '--followup', followup, '--package', scope/'helper-consumer')
    add('terminal_workspace', 'terminal-workspace/check_workspace.py',
        '--followup', followup, '--continuation', scope,
        '--out', scope/'terminal-workspace/RESULT.json')
    add('whole_replica_padding_screen', 'terminal-workspace/screen_padding.py')
    return specs


def main():
    need(__debug__, 'Run with assertions enabled; do not use python -O')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', required=True, type=Path,
                    help='New replay directory outside the delivered package')
    ap.add_argument('--skip-baseline', action='store_true',
                    help='Authenticate but do not rerun the eight retained commands')
    args = ap.parse_args()
    work = args.work.expanduser().resolve()
    need(not work.exists(), '--work must name a new directory')
    need(not work.is_relative_to(HERE), '--work must be outside this package')
    manifest = authenticate()
    print(f'PASS source authentication: {len(manifest["files"])} files', flush=True)
    replay_repo = work/'integer-mult-bounds'
    replay_scope = replay_repo/REL
    shutil.copytree(HERE, replay_scope,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for rel in manifest['repository_dependencies']:
        dest = replay_repo/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO/rel, dest)
    # Remove every expected output. A missing writer must not pass by using
    # the delivered receipt that happened to be copied into the work tree.
    for item in manifest['regenerated_artifacts']:
        (replay_scope/item['path']).unlink()
    followup = replay_scope/'inputs/kappa-consumer-followup'
    logs = work/'logs'
    logs.mkdir()
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    env['PYTHONPYCACHEPREFIX'] = str(work/'bytecode-cache')
    started = time.monotonic()
    receipt = {
        'status': 'RUNNING', 'scope': SCOPE,
        'manifest_sha256': digest(HERE/'MANIFEST.json'),
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'environment': {'python': sys.version, 'platform': platform.platform(),
                        'assertions_enabled': True},
        'authenticated_files': len(manifest['files']),
        'baseline_replayed': not args.skip_baseline,
        'commands': [], 'regenerated_artifacts': []}
    receipt_path = work/'REPLAY.json'
    def save():
        receipt['elapsed_seconds'] = round(time.monotonic()-started, 3)
        receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    try:
        for name, script, argv in commands(replay_scope, followup, work,
                                            not args.skip_baseline):
            print(f'RUN  {name}', flush=True)
            log_path = logs/f'{name}.log'
            t0 = time.monotonic()
            with log_path.open('w') as log:
                result = subprocess.run([sys.executable, '-B', str(script), *argv],
                    cwd=replay_repo, stdout=log, stderr=subprocess.STDOUT,
                    env=env, check=False, text=True)
            receipt['commands'].append({
                'name': name, 'script': str(script.relative_to(replay_repo)),
                'source_sha256': digest(script), 'exit_code': result.returncode,
                'elapsed_seconds': round(time.monotonic()-t0, 3),
                'log': str(log_path.relative_to(work)),
                'log_sha256': digest(log_path)})
            save()
            if result.returncode:
                print(log_path.read_text()[-16000:], flush=True)
            need(result.returncode == 0, f'Replay failed: {name}; see {log_path}')
            print(f'PASS {name}', flush=True)
        for item in manifest['regenerated_artifacts']:
            value = sha256(canonical(replay_scope/item['path'])).hexdigest()
            need(value == item['canonical_json_sha256'],
                 f'Regenerated canonical payload differs: {item["path"]}')
            receipt['regenerated_artifacts'].append({
                'path': item['path'], 'canonical_json_sha256': value,
                'matches_delivered_payload': True})
        receipt['status'] = 'PASS_SCOPED_KAPPA_CONTINUATION_REPLAY'
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
