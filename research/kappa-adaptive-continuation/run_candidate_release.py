#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fully admit the receiver-sharing word with PR3815's exact clock and fill.

Rebuild the pinned PR3734 source archive in a fresh workspace, append the
literal edit to its original reconstruction chain, preserve every earlier
review, authenticate fresh five-stage native providers, and execute the
original admission machinery with an explicitly pinned new source profile.
All source adaptations are recorded with exact before/after hashes.
The pinned bulk-audit runtime wrapper reduces allocations and isolates the
original mutation controls without changing scientific assertions or inputs.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import time

from run_full_release import verify_source

P = Path(__file__).resolve().parent
UP = P / 'sources/PR3815/research/staged544-producer-return'
CLOCK = P / 'sources/PR3815/research/staged544-clock-ceiling'
LABEL = 'receiver-share-672-676-v1'
LOWER = Q('0.001730739780298357321619')
UPPER = Q('0.001730739780298357321620')
PROFILE = {'1': 2439, '2': 724, '3': 225, '4': 102, '5': 20, '8': 8}
RUNTIME_PREDECESSOR_SHA256 = '26950da76589b13cd9c452fdee1b0c354806977f881299bd94073f00e4646fcd'
RUNTIME_ADAPTER_SHA256 = '30a39a3612efde96a0db189c14053afe5e012e56de1a89863596a078a8b64381'
NATIVE_AUTH_SHA256 = 'd1beca6a4d65c71b3e507a2b2490639b998daee3f3b021a1280e8c2c7171db80'
OUTER_WHEELS = {
    'sympy-1.14.0-py3-none-any.whl': 'e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5',
    'mpmath-1.3.0-py3-none-any.whl': 'a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def tree(path, exclude=()):
    return {f.relative_to(path).as_posix(): sha(f) for f in sorted(path.rglob('*'))
            if f.is_file() and f.relative_to(path).as_posix() not in exclude}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--reuse-native-root', type=Path,
                        help='exact byte-preserving copy of shipped native-base and native-extra runs; default rebuilds both')
    parser.add_argument('--python-deps', type=Path,
                        help='existing local dependency directory; otherwise install pinned pure-Python outer wheels into the fresh work directory')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    if not __debug__: raise RuntimeError('Python assertions must be enabled')
    verify_source()
    work = args.work.resolve()
    assert not work.exists() and not work.is_relative_to(P / 'sources'), 'fresh external workspace'
    work.mkdir(parents=True)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
                       PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                       AUDIT_RUNTIME_CONTROLS='fork' if hasattr(os, 'fork') else 'pickle')
    environment.pop('PYTHONOPTIMIZE', None)
    stages = []

    def run(name, command):
        started = time.monotonic()
        log = work / (name + '.log')
        with log.open('w') as stream:
            result = subprocess.run(command, env=environment, stdout=stream,
                                    stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        stages.append(dict(name=name, command=command, seconds=time.monotonic() - started,
                           exit_code=result.returncode, log_sha256=sha(log)))
        write(work / 'STAGES.json', stages)
        assert result.returncode == 0, 'failed ' + name + '; inspect ' + str(log)
        print('PASS', name, flush=True)

    # Fail before expensive scientific work if the complete release runtime is
    # unavailable. Its pinned SymPy evidence requires exactly version 1.14.0.
    # Install only the two shipped, hash-authenticated pure-Python wheels, into
    # this fresh workspace; never alter the interpreter's global packages.
    run('numpy-preflight', [sys.executable, '-B', '-c',
        "import numpy,sys; assert sys.version_info >= (3,11); print('NumPy',numpy.__version__)"])
    wheel_dir = P / 'replay-support/wheels'
    for name, expected in OUTER_WHEELS.items():
        assert sha(wheel_dir / name) == expected, 'exact full-release dependency wheel'
    dependency_dir = args.python_deps.resolve() if args.python_deps else work / 'python-deps'
    if not args.python_deps:
        run('install-outer-dependencies', [sys.executable, '-B', '-m', 'pip', 'install',
            '--disable-pip-version-check', '--root-user-action=ignore', '--no-compile',
            '--no-index', '--no-deps', '--target', str(dependency_dir),
            *[str(wheel_dir / name) for name in sorted(OUTER_WHEELS)]])
    assert dependency_dir.is_dir(), 'local dependency directory'
    environment['PYTHONPATH'] = str(dependency_dir) + (
        os.pathsep + environment['PYTHONPATH'] if environment.get('PYTHONPATH') else '')
    run('complete-dependency-preflight', [sys.executable, '-B', '-c',
        "import json,numpy,sympy,mpmath; assert sympy.__version__=='1.14.0'; assert mpmath.__version__=='1.3.0'; print(json.dumps({'numpy':numpy.__version__,'sympy':sympy.__version__,'mpmath':mpmath.__version__},sort_keys=True))"])
    dependency_record = dict(wheels=OUTER_WHEELS, mode='explicit local directory' if args.python_deps else 'offline install of pinned wheels',
                             versions=json.loads((work / 'complete-dependency-preflight.log').read_text()))
    write(work / 'DEPENDENCIES.json', dependency_record)
    auth_path = P / 'replay-support/native_auth.py'
    assert sha(auth_path) == NATIVE_AUTH_SHA256
    auth_spec = importlib.util.spec_from_file_location('receiver_release_native_auth', auth_path)
    native_auth = importlib.util.module_from_spec(auth_spec)
    auth_spec.loader.exec_module(native_auth)
    if args.reuse_native_root:
        write(work / 'REUSED-NATIVE-AUTH.json', native_auth.authenticate_reused(args.reuse_native_root.resolve()))
        print('PASS exact shipped native source and output authentication', flush=True)

    archive = UP / 'REPLAY-INPUTS.tar.gz'
    pins = read(UP / 'REPLAY-INPUTS.json')
    assert sha(archive) == pins['archive_sha256']
    inputs = work / 'inputs'
    inputs.mkdir()
    seen = set()
    with tarfile.open(archive) as stream:
        for member in stream:
            assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            assert member.name not in seen and member.name in pins['files']
            data = stream.extractfile(member).read()
            assert hashlib.sha256(data).hexdigest() == pins['files'][member.name]
            destination = inputs / member.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            seen.add(member.name)
    assert seen == set(pins['files'])
    source, cache = inputs / 'source', inputs / 'native-cache'
    original_source = tree(source, ('MANIFEST.json',))
    assert original_source == read(source / 'MANIFEST.json')
    original_manifest_sha = sha(source / 'MANIFEST.json')
    borrow = source / 'new/borrow'
    parent_words = borrow / 'receiver-share-parent'
    parent_words.mkdir()
    patches = []

    def patch(relative, old, new):
        path = source / relative
        before = sha(path)
        text = path.read_text()
        assert text.count(old) == 1, 'exact patch preimage: ' + relative
        path.write_text(text.replace(old, new))
        patches.append(dict(path=relative, before_sha256=before, after_sha256=sha(path),
                            old=old, new=new))

    for name in ('receiver_share.py', 'review_receiver_share.py'):
        shutil.copy2(P / 'admission' / name, borrow / name)
    sys.path.insert(0, str(borrow))
    spec = importlib.util.spec_from_file_location('release_receiver_share', borrow / 'receiver_share.py')
    edit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(edit)
    changed_words = {}
    for tag in ('base', 'extra'):
        name = 'BORROW-WORD-43' + tag + '.json.gz'
        word_path = borrow / 'words' / name
        shutil.copy2(word_path, parent_words / name)
        word = edit.apply(read(word_path))
        payload = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
        candidate_path = P / 'native-alternatives/candidate' / name
        assert payload == gzip.decompress(candidate_path.read_bytes()), 'exact reconstructed canonical native payload'
        shutil.copy2(candidate_path, word_path)
        assert word == read(word_path) and sha(word_path) == sha(candidate_path)
        changed_words[tag] = dict(parent_sha256=sha(parent_words / name), candidate_sha256=sha(word_path))
    patch('new/rebuild_borrow.py',
          "    final=json.loads(gzip.decompress(shipped.read_bytes()))",
          "    import receiver_share\n"
          "    assert chain[-1]==json.loads(gzip.decompress((D/'receiver-share-parent'/f'BORROW-WORD-43{wt}.json.gz').read_bytes()))\n"
          "    chain.append(receiver_share.apply(chain[-1]));steps.append('receiver-share-672-676-v1')\n"
          "    final=json.loads(gzip.decompress(shipped.read_bytes()))")
    patch('new/borrow/review_staged544.py',
          "w=load(P/'words'/f'BORROW-WORD-43{tag}.json.gz')",
          "w=load(P/'receiver-share-parent'/f'BORROW-WORD-43{tag}.json.gz')")
    patch('verify.py',
          "run('staged544-independent-word-review',P/'new/borrow/review_staged544.py')",
          "run('staged544-independent-word-review',P/'new/borrow/review_staged544.py')\n"
          "run('receiver-sharing-independent-word-review',P/'new/borrow/review_receiver_share.py')")

    receipt = read(inputs / 'NATIVE-RECEIPT.json')
    assert tree(cache) == receipt['cache_files'], 'original native cache bindings'
    provider_description = read(source / 'new/BORROW-PROVIDERS.json')
    actual_native_sources = {}
    for tag, provider in [('base', 'gauge44'), ('extra', 'extra')]:
        word_path = borrow / 'words' / ('BORROW-WORD-43' + tag + '.json.gz')
        if args.reuse_native_root:
            native_run = args.reuse_native_root.resolve() / ('native-' + tag)
        else:
            native_run = work / ('native-' + tag)
            run('fresh-native-' + tag, [sys.executable, '-B', str(source / 'new/fastnative/run_native.py'),
                                        str(word_path), str(native_run)])
        actual_native_sources[tag] = native_auth.authenticate_fresh_native(native_run, tag)
        result = read(native_run / 'RESULT.json')
        assert result['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY'
        assert result['word_sha256'] == sha(word_path)
        assert result['source_sha256'] == read(UP / 'evidence' / ('NATIVE-' + tag + '.json'))['source_sha256']
        assert all(x['exit_code'] == 0 for x in result['steps'])
        entry = cache / sha(word_path)
        shutil.copytree(native_run / 'native', entry)
        for path in entry.rglob('*'):
            if path.is_file() and path.suffix in ('.json', '.log', '.txt'):
                path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
        assert read(entry / 'local/FULL-WORD.json.gz') == read(word_path)
        native_steps = read(entry / 'STEPS.json')
        assert [x['step'] for x in native_steps] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
        assert all(x['exit_code'] == 0 for x in native_steps)
        checks = read(entry / 'local/LOCAL-CHECKS.json')
        assert all(checks[direction]['paid_profile'] == PROFILE for direction in ('forward', 'backward'))
        canonical = read(entry / 'local/CANONICAL-WORD.json.gz')
        widths = [len(canonical['frames'][canonical['final'][r]]) - len(canonical['frames'][canonical['start'][r]])
                  for r in range(224, 224 + canonical['R'])]
        assert canonical['R'] == 408 and len(canonical.get('zero_buffers', [])) == 91
        assert widths == provider_description[provider]['widths'], 'ordered helper interface unchanged'
        provider_description[provider]['actual_paid_profile'] = checks['forward']['paid_profile']
        write(entry / 'CACHE.json', dict(word_sha256=sha(word_path), files=tree(entry, ('CACHE.json',))))
        receipt['providers'][tag] = dict(word_sha256=sha(word_path), complete_native_files=tree(entry, ('CACHE.json',)))
    write(source / 'new/BORROW-PROVIDERS.json', provider_description)
    write(work / 'ACTUAL-NATIVE-SOURCES.json', actual_native_sources)
    runtime_path = P / 'runtime-repair/audit_fast.py'
    runtime_fixtures = read(P / 'runtime-repair/FIXTURES.json')
    assert sha(source / 'audit_fast.py') == RUNTIME_PREDECESSOR_SHA256
    assert sha(runtime_path) == RUNTIME_ADAPTER_SHA256 == runtime_fixtures['adapter_sha256']
    assert runtime_fixtures['status'] == 'PASS_RUNTIME_ADAPTER_FAILURE_MODES'
    assert len(runtime_fixtures['checks']) == 19
    shutil.copy2(runtime_path, source / 'audit_fast.py')
    runtime_adaptation = dict(
        path='audit_fast.py', before_sha256=RUNTIME_PREDECESSOR_SHA256,
        after_sha256=RUNTIME_ADAPTER_SHA256,
        original_scientific_auditor_sha256='fa3488b62efdf8a0c37de0ca0caba587b4b036c5f068e002eb04c71c12b9e9b4',
        unchanged_emitter_sha256='549603ca6d28b163a43b2dfaaaa788161c73d7952ab9190289407caca5418c71',
        failure_mode_fixtures_sha256=sha(P / 'runtime-repair/FIXTURES.json'),
        preserved_scientific_assertions=76, equivalent_streamed_digest_assertions=1,
        preserved_mutator_call_sites=27, control_mode=environment['AUDIT_RUNTIME_CONTROLS'],
        scope='Pinned runtime-only source transformation: release unused ancestral owner tails, stream the identical payload hash, remove dead bookkeeping and isolate unchanged mutators. Actual current owners and all scientific assertions remain checked; abnormal children fail.')
    write(source / 'MANIFEST.json', tree(source, ('MANIFEST.json',)))
    manifest = sha(source / 'MANIFEST.json')
    receipt.update(source_commit=LABEL, manifest_sha256=manifest, cache_files=tree(cache))
    native_receipt = work / 'NATIVE-RECEIPT.json'
    write(native_receipt, receipt)
    after = tree(source, ('MANIFEST.json',))
    delta = {name: dict(before=original_source.get(name), after=after[name]) for name in after
             if original_source.get(name) != after[name]}
    assert set(original_source) <= set(after), 'no predecessor source deleted'
    write(work / 'SOURCE-ADAPTATION.json', dict(
        status='PASS_EXPLICIT_SOURCE_EXTENSION_WITH_PREDECESSOR_REVIEWS_RETAINED',
        predecessor_manifest_sha256=original_manifest_sha, current_manifest_sha256=manifest,
        source_file_count=len(after), source_label=LABEL, changed_words=changed_words,
        files=delta, exact_patches=patches, runtime_adapter=runtime_adaptation,
        scope='Appends the new word edit and new independent review; preceding staged544 review runs on its retained exact parent word. The pinned bulk-audit wrapper changes memory lifetime and mutation isolation only. Every scientific and release check remains.'))
    run('independent-receiver-word', [sys.executable, '-B', str(borrow / 'review_receiver_share.py')])

    adapter_source = inputs / 'admit544.py'
    body = adapter_source.read_text()
    old_profile = "    'staged544': dict(commit='staged544-literal-v1',manifest='4c4f7067b1b5404b59213f480e9d91c96ffc79b5458e2736b159f5a522ed2dc3',helpers=408,source_file_count=660,upstream_head='431e6c6023ef352c41696469de7fb614cd4ded8c'),"
    new_profile = f"    '{LABEL}': dict(commit='{LABEL}',manifest='{manifest}',helpers=408,source_file_count={len(after)},upstream_head='fa041037a3374eaa08feeca0b26a5d6893194147'),"
    old_cli = "ap.add_argument('--source-profile', choices=['staged544'], default='staged544')"
    new_cli = f"ap.add_argument('--source-profile', choices=['{LABEL}'], default='{LABEL}')"
    assert body.count(old_profile) == body.count(old_cli) == 1
    adapted = body.replace(old_profile, new_profile).replace(old_cli, new_cli)
    adapter = work / 'admit_receiver_share.py'
    adapter.write_text(adapted)
    write(work / 'ADMISSION-ADAPTER.json', dict(original_sha256=sha(adapter_source), adapted_sha256=sha(adapter),
         exact_replacements=[[old_profile, new_profile], [old_cli, new_cli]],
         scope='Only the immutable source identity and its sole CLI selector change. No assertion, audit, control, cost, precision, or comparison gate is removed.'))
    command = [sys.executable, '-B', str(adapter)]
    options = {'source': source, 'fill': CLOCK / 'inputs/FILL.json.gz', 'order': CLOCK / 'inputs/ORDER.json',
               'dispatch': UP / 'inputs/DISPATCH.json', 'native-cache': cache, 'native-receipt': native_receipt,
               'work': work / 'admission', 'replica-helper-dir': inputs / 'helpers',
               'reconstructor': inputs / 'helpers/reconstruct_replica.py',
               'comparison-claim': UP / 'inputs/PR3682-CLAIM.json',
               'blocknorm-checker': inputs / 'extension_blocknorm.py'}
    for key, value in options.items():
        command += ['--' + key, str(value)]
    command += ['--source-profile', LABEL, '--comparison-profile', 'pr3682', '--jobs', '1']
    if args.prepare_only:
        command.append('--prepare-only')
    run('complete-admission' if not args.prepare_only else 'prepare-admission', command)
    result = read(work / 'admission/RESULT.json')
    if args.prepare_only:
        assert result['status'] == 'PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED'
        print(result['status'], flush=True)
        return
    assert result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
    expected = LOWER - Q(1, 10**46) - Q(1, 10**70)
    assert Q(result['complex_lower']) == LOWER and Q(result['kappa']) == expected
    expected_profile = read(CLOCK / 'inputs/PROFILE.json')
    for r, change in {'1': -3240, '2': -3240, '3': 3240}.items():
        expected_profile[r] += change
    assert result['profile'] == expected_profile
    assert Q(result['kappa']) > Q(read(CLOCK / 'PRICE.json')['root_lower'])
    assert tree(source, ('MANIFEST.json',)) == after
    verify_source()
    write(work / 'RESULT.json', dict(status='PASS_RECEIVER_SHARING_COMPLETE_CONDITIONAL_RELEASE',
          kappa_rational=str(expected), root_lower=str(LOWER), root_upper=str(UPPER),
          global_profile=expected_profile, source_manifest_sha256=manifest,
          native_receipt_sha256=sha(native_receipt), admission_result_sha256=sha(work / 'admission/RESULT.json'),
          release_receipt_sha256=result['release_receipt_sha256'], stages=stages,
          dependency_record_sha256=sha(work / 'DEPENDENCIES.json'),
          actual_native_sources_sha256=sha(work / 'ACTUAL-NATIVE-SOURCES.json'),
          runner_sha256=sha(Path(__file__)),
          python=sys.version, platform=platform.platform(),
          scope='Fresh changed-word complete admission; both current native providers authenticated from fresh complete five-stage runs. Unchanged retained ancestry and all inherited theorem assumptions remain.'))
    print('PASS_RECEIVER_SHARING_COMPLETE_CONDITIONAL_RELEASE', flush=True)


if __name__ == '__main__':
    main()
