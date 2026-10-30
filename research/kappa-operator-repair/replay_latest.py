#!/usr/bin/env python3
"""Reexecute both operator-guarded improvements and admit the stronger one.

The default reexecutes exact core certificates and both complete invoices.
--native also recompiles the stronger supplier; --full additionally reruns
its inherited release. Frozen native receipts remain immutable inputs to
that source-closed release after the fresh native outputs are compared.
Apache-2.0. Substantial OpenAI assistance.
"""
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LATE = HERE / 'late-staged-composition'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def word_payload(p):
    return gzip.decompress(p.read_bytes())


def construction_view(data, directory, expected_directory, late):
    """Remove only generated container hashes, after authenticating each one."""
    data = deepcopy(data)
    generated = {}
    for tag in ['base', 'extra']:
        row = data['providers'][tag]
        p = directory / row['word']
        need(row.pop('word_sha256') == sha(p), 'Constructor authenticates its actual generated container')
        payload_key = 'canonical_sha256' if late else 'word_payload_sha256'
        need(row[payload_key] == hashlib.sha256(word_payload(p)).hexdigest(), 'Constructor authenticates its actual payload')
        if late:
            key = (expected_directory / p.name).relative_to(REPO).as_posix()
            need(data['input_files'].pop(key) == sha(p), 'Exact generated-word source binding')
        generated[tag] = dict(container_sha256=sha(p), payload_sha256=row[payload_key])
    return data, generated


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--native', action='store_true')
    ap.add_argument('--full', action='store_true')
    a = ap.parse_args()
    need(__debug__, 'Assertions enabled')
    sys.dont_write_bytecode = True
    out = a.out.resolve()
    need(not out.exists(), 'Fresh output directory required')
    out.mkdir(parents=True)
    manifest = read(HERE / 'MANIFEST.json')
    paths = []
    byte_count = 0
    for base, key in [(HERE, 'files'), (REPO, 'repository_dependencies')]:
        for name, row in manifest[key].items():
            p = base / name
            need(p.is_file() and not p.is_symlink() and p.stat().st_size == row['bytes'] and sha(p) == row['sha256'],
                 'Manifest input mismatch ' + str(p))
            paths.append(p)
            byte_count += row['bytes']
    need(len(paths) == len(set(paths)), 'Disjoint manifest namespaces')
    print('PASS manifest', len(paths), 'files', flush=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE', None)
    stages = []
    comparisons = []

    def run(name, script, args=(), cwd=REPO):
        command = [sys.executable, '-B', str(script), *map(str, args)]
        log = out / (name + '.log')
        started = time.monotonic()
        with log.open('w') as f:
            proc = subprocess.run(command, env=env, stdout=f, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, cwd=cwd)
        stages.append(dict(name=name, command=command, exit_code=proc.returncode,
                           seconds=time.monotonic() - started, log_sha256=sha(log)))
        (out / 'STAGES.json').write_text(json.dumps(stages, indent=2, sort_keys=True) + '\n')
        need(proc.returncode == 0, 'Failed ' + name + '; see ' + str(log))
        print('PASS', name, flush=True)

    def compare(actual, expected):
        need(sha(actual) == sha(expected), 'Fresh certificate differs from retained bytes ' + str(expected))
        comparisons.append(dict(expected=expected.relative_to(REPO).as_posix(),
                                comparison_mode='byte_identity', sha256=sha(expected)))

    def compare_word(actual, expected):
        need(word_payload(actual) == word_payload(expected), 'Exact canonical word payload identity')
        comparisons.append(dict(expected=expected.relative_to(REPO).as_posix(),
                                comparison_mode='exact_decompressed_payload',
                                payload_sha256=hashlib.sha256(word_payload(expected)).hexdigest(),
                                actual_container_sha256=sha(actual), expected_container_sha256=sha(expected),
                                container_byte_identity=sha(actual) == sha(expected)))

    def compare_construction(actual, expected, late=False):
        left, left_words = construction_view(read(actual), actual.parent, expected.parent, late)
        right, right_words = construction_view(read(expected), expected.parent, expected.parent, late)
        need(left == right, 'Every scientific constructor field agrees')
        payload = json.dumps(right, sort_keys=True, separators=(',', ':')).encode()
        omitted = ['providers.base.word_sha256', 'providers.extra.word_sha256']
        if late:
            omitted += ['input_files.' + (expected.parent / ('BORROW-WORD-43' + tag + '.json.gz')).relative_to(REPO).as_posix()
                        for tag in ['base', 'extra']]
        comparisons.append(dict(expected=expected.relative_to(REPO).as_posix(),
                                comparison_mode='exact_json_except_authenticated_generated_container_hashes',
                                actual_sha256=sha(actual), expected_sha256=sha(expected),
                                omitted_fields=omitted, scientific_payload_sha256=hashlib.sha256(payload).hexdigest(),
                                actual_generated_words=left_words, expected_generated_words=right_words))

    def compare_phase(actual, expected):
        left, right = read(actual), read(expected)
        for value in [left, right]:
            elapsed = value.pop('seconds')
            need(isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool)
                 and math.isfinite(elapsed) and elapsed >= 0, 'Valid phase-review runtime')
        need(left == right, 'Every scientific phase-review field agrees')
        comparisons.append(dict(expected=expected.relative_to(REPO).as_posix(),
                                comparison_mode='exact_json_except_top_level_runtime_seconds',
                                omitted_top_level_fields=['seconds'], actual_sha256=sha(actual), expected_sha256=sha(expected),
                                scientific_payload_sha256=hashlib.sha256(json.dumps(right, sort_keys=True, separators=(',', ':')).encode()).hexdigest()))

    for name, script, receipt in [
        ('full-operator', 'full_operator.py', 'FULL-OPERATOR.json'),
        ('inverse-correction', 'correction.py', 'CORRECTION.json'),
        ('gaussian-bridge', 'gaussian_bridge_rigidity.py', 'GAUSSIAN-BRIDGE-RIGIDITY.json'),
        ('actual-t360-operator', 't360_admission.py', 'T360-OPERATOR-ADMISSION.json'),
    ]:
        result = out / receipt
        run(name, HERE / 'operator-correction' / script, ['--output', result])
        compare(result, HERE / 'operator-correction' / receipt)
    run('composed-word', HERE / 'composed-supplier/construct.py', ['--out', out / 'candidate'])
    for tag in ['base', 'extra']:
        name = 'BORROW-WORD-43' + tag + '.json.gz'
        compare_word(out / 'candidate' / name, HERE / 'composed-supplier/candidate' / name)
    compare_construction(out / 'candidate/CONSTRUCTION.json', HERE / 'composed-supplier/candidate/CONSTRUCTION.json')
    run('complete-invoice', HERE / 'composed-supplier/invoice.py', ['--out', out / 'invoice'])
    compare(out / 'invoice/RESULT.json', HERE / 'composed-supplier/invoice/RESULT.json')
    run('target-budget', HERE / 'budget.py', ['--out', out / 'TARGET-BUDGET.json'])
    compare(out / 'TARGET-BUDGET.json', HERE / 'TARGET-BUDGET.json')
    run('primary-headline-conjunction', HERE / 'build_claim.py', ['--out', out / 'PRIMARY-CLAIM.json'])
    compare(out / 'PRIMARY-CLAIM.json', HERE / 'CLAIM.json')

    # The late constructor records canonical repository-relative output paths.
    # A fresh owned copy lets it regenerate those exact paths without changing
    # the caller's immutable candidate/native evidence or the original repo.
    clone = out / 'isolated/integer-mult-bounds'
    clone.mkdir(parents=True)
    regenerated = {
        LATE / 'candidate/BORROW-WORD-43base.json.gz',
        LATE / 'candidate/BORROW-WORD-43extra.json.gz',
        LATE / 'candidate/CONSTRUCTION.json',
        LATE / 'invoice/RESULT.json',
        LATE / 'T360-OPERATOR-ADMISSION.json',
        LATE / 'CLAIM.json',
    }
    need(regenerated.issubset(set(paths)), 'Every regenerated output has authenticated expected evidence')
    for p in paths:
        # Never seed then delete an expected output: a synchronized filesystem
        # can restore the seeded version while the fresh computation runs.
        # Expected bytes remain in the authenticated caller tree for comparison.
        if p in regenerated:
            continue
        dest = clone / p.relative_to(REPO)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dest)
        need(sha(dest) == sha(p), 'Authenticated isolated source copy')
    selected = clone / LATE.relative_to(REPO)
    need(selected.is_relative_to(out), 'Only newly owned replay copies may be rebuilt')
    need(not (selected / 'candidate').exists(), 'Unseeded fresh canonical candidate directory')
    run('staged-composed-word', selected / 'construct.py', cwd=clone)
    for tag in ['base', 'extra']:
        name = 'BORROW-WORD-43' + tag + '.json.gz'
        compare_word(selected / 'candidate' / name, LATE / 'candidate' / name)
    compare_construction(selected / 'candidate/CONSTRUCTION.json', LATE / 'candidate/CONSTRUCTION.json', late=True)
    # Preserve the source-closed native input containers after proving their
    # entire payload and all construction fields. Timed native receipts are
    # never regenerated or relabelled merely to make a hash comparison pass.
    for name in ['BORROW-WORD-43base.json.gz', 'BORROW-WORD-43extra.json.gz', 'CONSTRUCTION.json']:
        shutil.copyfile(LATE / 'candidate' / name, selected / 'candidate' / name)
    need(not (selected / 'invoice').exists(), 'Unseeded fresh canonical invoice directory')
    need(not (selected / 'T360-OPERATOR-ADMISSION.json').exists(), 'Unseeded fresh operator output')
    run('staged-complete-invoice-and-operator', selected / 'invoice.py', cwd=clone)
    compare(selected / 'invoice/RESULT.json', LATE / 'invoice/RESULT.json')
    compare(selected / 'T360-OPERATOR-ADMISSION.json', LATE / 'T360-OPERATOR-ADMISSION.json')
    run('staged-target-budget', selected / 'budget.py', ['--out', out / 'STAGED-TARGET-BUDGET.json'], cwd=clone)
    compare(out / 'STAGED-TARGET-BUDGET.json', LATE / 'TARGET-BUDGET.json')
    need(not (selected / 'CLAIM.json').exists(), 'Unseeded fresh claim output')
    run('strongest-headline-conjunction', selected / 'build_claim.py', cwd=clone)
    compare(selected / 'CLAIM.json', LATE / 'CLAIM.json')

    if a.native or a.full:
        compiler = HERE / 'sources/PR3945/research/staged544-terminal-gap-fill/native/run_native.py'
        for tag in ['base', 'extra']:
            word = LATE / 'candidate' / ('BORROW-WORD-43' + tag + '.json.gz')
            current = LATE / ('native-' + tag)
            fresh = out / 'fresh-native' / ('native-' + tag)
            run('staged-native-' + tag, compiler, [word, fresh, '--engine', 'sparse'])
            value, retained = read(fresh / 'RESULT.json'), read(current / 'RESULT.json')
            need(value['status'] == retained['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY'
                 and value['word_sha256'] == sha(word) and value['source_sha256'] == retained['source_sha256'],
                 'Exact freshly executed native source and word')
            need([x['step'] for x in value['steps']] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
                 and all(x['exit_code'] == 0 for x in value['steps']), 'All five fresh native stages')
            for name in ['CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
                         'INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-REVIEW.json', 'RESIDUAL-ADAPTERS.json']:
                comparator = compare_phase if name == 'CLIFFORD-REVIEW.json' else compare
                comparator(fresh / 'native/local' / name, current / 'native/local' / name)
        if a.full:
            work = selected / 'release-work/replayed-full'
            run('strongest-full-conditional-release', selected / 'run_release.py', ['--work', work], cwd=clone)
            fresh = read(work / 'RESULT.json')
            need(fresh['status'] == 'PASS_STAGED_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE'
                 and fresh['kappa_rational'] == read(LATE / 'CLAIM.json')['conditional_kappa']['value'],
                 'Fresh complete strongest conditional release')
    claim = read(LATE / 'CLAIM.json')
    result = dict(status='PASS_PORTABLE_OPERATOR_GUARDED_KAPPA_REPLAY',
                  manifest_sha256=sha(HERE / 'MANIFEST.json'), authenticated_files=len(paths), authenticated_bytes=byte_count,
                  stages=stages, comparisons=comparisons, fresh_native_executed=bool(a.native or a.full),
                  fresh_full_release_executed=bool(a.full), selected_supplier='late-staged-composition',
                  primary_claim_sha256=sha(HERE / 'CLAIM.json'), claim_sha256=sha(LATE / 'CLAIM.json'),
                  retained_full_release_sha256=sha(LATE / 'evidence/full-release/RESULT.json'),
                  claim=claim['conditional_kappa'],
                  fresh_full_release_native_receipt_mode='Immutable source-closed native receipts, after independently reexecuting and comparing all native scientific outputs.' if a.full else 'Retained research-round execution, authenticated only in this default core replay.',
                  scope='Both exact operator-guarded improvements freshly rechecked. All constructor payloads and scientific fields are compared; only authenticated generated container hashes may differ. The stronger owner/operator invoice and claim are rebuilt at canonical paths in a fresh owned copy. Optional native/full execution is recorded explicitly.')
    (out / 'VALIDATION.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], len(stages), 'stages', len(comparisons), 'comparisons', flush=True)


if __name__ == '__main__':
    main()
