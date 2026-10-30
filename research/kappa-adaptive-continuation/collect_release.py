#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Collect complete-release evidence and a source-bound conditional claim.

The large generated template trees remain reproducible from pinned inputs.
Their full file inventory is hashed; concise receipts, control logs and the
actual executed runner are retained in this package. No status is promoted
unless the original complete admission and release both passed.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import shutil

P = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--executed-runner', type=Path, required=True,
                        help='byte-identical saved source of the entry point used for this completed run')
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError('Python assertions must be enabled; collection cannot run with -O')
    work = args.work.resolve()
    result = read(work / 'RESULT.json')
    admission = read(work / 'admission/RESULT.json')
    release = read(work / 'admission/release/RELEASE-RECEIPT.json')
    assert result['status'] == 'PASS_RECEIVER_SHARING_COMPLETE_CONDITIONAL_RELEASE'
    assert sha(args.executed_runner) == result['runner_sha256'], 'retained source is the actual executed release runner'
    assert admission['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
    assert release['status'] == 'PASS_RELEASE'
    assert sha(work / 'admission/RESULT.json') == result['admission_result_sha256']
    assert sha(work / 'admission/release/RELEASE-RECEIPT.json') == result['release_receipt_sha256']
    assert sha(work / 'DEPENDENCIES.json') == result['dependency_record_sha256']
    assert sha(work / 'ACTUAL-NATIVE-SOURCES.json') == result['actual_native_sources_sha256']
    assert sha(work / 'NATIVE-RECEIPT.json') == result['native_receipt_sha256']
    assert sha(work / 'inputs/source/MANIFEST.json') == result['source_manifest_sha256']
    assert sha(work / 'admission/package/MANIFEST.json') == admission['package_manifest_sha256'] == release['manifest_sha256']
    assert read(work / 'STAGES.json') == result['stages']
    assert read(work / 'admission/STAGES.json') == admission['stages']
    assert all(stage['exit_code'] == 0 for stage in result['stages'])
    stage_names = {stage['name'] for stage in result['stages']}
    fresh_stages = {'fresh-native-base', 'fresh-native-extra'}
    if stage_names & fresh_stages:
        assert fresh_stages <= stage_names, 'both native providers must have completed fresh execution'
        assert not (work / 'REUSED-NATIVE-AUTH.json').exists(), 'unambiguous fresh-native mode'
        native_mode = 'both complete native providers freshly executed in this run'
        native_required = {'native-base/RESULT.json', 'native-extra/RESULT.json'}
    else:
        assert read(work / 'REUSED-NATIVE-AUTH.json')['status'] == 'PASS_EXACT_SHIPPED_NATIVE_REUSE'
        native_mode = 'exact authenticated reuse of both shipped completed native runs'
        native_required = {'REUSED-NATIVE-AUTH.json'}
    lower = Q('0.001730739780298357321619')
    upper = Q('0.001730739780298357321620')
    kappa = lower - Q(1, 10**46) - Q(1, 10**70)
    assert Q(result['kappa_rational']) == Q(admission['kappa']) == Q(release['kappa_decimal']) == kappa
    invoice_path = P / 'global-budget/receiver-sharing/RESULT.json'
    invoice = read(invoice_path)
    assert list(map(Q, invoice['root']['rational'])) == [lower, upper]
    assert result['global_profile'] == admission['profile'] == invoice['profile']
    out = P / 'evidence/full-release'
    assert not out.exists(), 'fresh retained evidence directory'
    out.mkdir(parents=True)
    # Preserve all concise proof receipts in the run and its current admission,
    # excluding archival/cache inputs and bulk owner/template inventories.
    exact = {
        'RESULT.json', 'STAGES.json', 'SOURCE-ADAPTATION.json', 'ADMISSION-ADAPTER.json',
        'NATIVE-RECEIPT.json', 'independent-receiver-word.log', 'complete-admission.log',
        'DEPENDENCIES.json', 'ACTUAL-NATIVE-SOURCES.json',
        'inputs/source/MANIFEST.json', 'admit_receiver_share.py',
        'admission/RESULT.json', 'admission/STAGES.json',
        'admission/package/MANIFEST.json', 'admission/package/CLAIM.json',
        'admission/package/new/SPEC.json',
        'admission/release/RELEASE-RECEIPT.json', 'admission/release/verify/RESULT.json',
        'admission/release/verify/strict/ASSEMBLY.json',
    }
    exact |= native_required
    indexed, retained = {}, {}
    for path in sorted(work.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        name = path.relative_to(work).as_posix()
        size = path.stat().st_size
        checksum = sha(path)
        indexed[name] = dict(bytes=size, sha256=checksum)
        concise = (name.startswith(('admission/discovery/', 'admission/release/'))
                   and not any(x in path.parts for x in ('hosted', 'source', 'data', 'new-data', 'rebuilt-parent', 'rebuilt-owners', 'native-cache'))
                   and path.suffix in ('.json', '.log', '.jsonl')
                   and size <= 2 * 1024 * 1024)
        outer = name.startswith('admission/package/outer/') and path.name in (
            'B.json', 'LEDGER.json', 'INDEPENDENT.json', 'OUTER-CLAIM.json',
            'check_ledger.py', 'independent_check.py', 'run_outer.py')
        fresh_native = bool(stage_names & fresh_stages) and name.startswith(('native-base/', 'native-extra/'))
        if name in exact or concise or outer or fresh_native:
            target = out / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            assert sha(target) == checksum
            retained[name] = indexed[name]
    assert exact <= set(retained), 'all mandatory release receipts retained'
    for prefix in ('inputs/source/', 'admission/package/'):
        actual = {name[len(prefix):]: record['sha256'] for name, record in indexed.items()
                  if name.startswith(prefix) and name != prefix + 'MANIFEST.json'}
        assert actual == read(work / prefix / 'MANIFEST.json'), 'every actual source/package byte matches its authoritative manifest'
    shutil.copy2(args.executed_runner, out / 'RUNNER-EXECUTED.py')
    write(out / 'FILE-INVENTORY.json', dict(
        status='PASS_COMPLETE_RUN_FILE_HASH_INVENTORY', files=indexed, retained_files=retained,
        native_execution_mode=native_mode,
        executed_runner_sha256=sha(args.executed_runner),
        scope='Every regular non-bytecode file in the completed run is hashed. Large reconstructed templates and ancestral sources can be reproduced from the pinned archive and source adaptation; concise evidence is retained here.'))
    baseline = Q('0.001730448360207635461740')
    clock = Q('0.001730578437266246818740')
    write(P / 'CLAIM.json', dict(
        status='PASS_COMPLETE_LOCAL_CONDITIONAL_KAPPA_INCREASE',
        root_lower_decimal='0.001730739780298357321619',
        root_upper_decimal='0.001730739780298357321620',
        root_interval_rational=[str(lower), str(upper)],
        kappa_rational=str(kappa), kappa_decimal=release['kappa_decimal'],
        outer_loss_rational=str(Q(1, 10**46) + Q(1, 10**70)),
        adopted_clock_gain_rational=str(clock - baseline),
        new_word_gain_rational=str(lower - clock),
        total_gain_over_attached_root_rational=str(lower - baseline),
        relative_saving_increase_percent_rational=str(100 * (lower - baseline) / baseline),
        dimension=73, replicas=360, local_calls=3240,
        productive_families=322560, physical_families=323069,
        complete_profile=invoice['profile'],
        new_local_profile=invoice['provider_local_profiles'],
        source_manifest_sha256=result['source_manifest_sha256'],
        physical_invoice_sha256=sha(invoice_path),
        complete_run_result_sha256=sha(out / 'RESULT.json'),
        original_full_release_receipt_sha256=result['release_receipt_sha256'],
        independent_outer_review_sha256=sha(P / 'global-budget/admission-review-low-memory/RESULT.json'),
        native_bindings_sha256=sha(P / 'native-alternatives/NATIVE-SUMMARY.json'),
        concluded_utc=datetime.now(timezone.utc).isoformat(),
        qualification='Finite changed native construction and complete conditional release. The inherited all-size/compiler, physical realization, hosting, precision/recovery, analytic and BIT premises remain. This local continuation does not update the selected repository frontier or claim universal priority.'))
    print('PASS complete conditional claim and release evidence collection', len(indexed), 'run files,', len(retained), 'retained')


if __name__ == '__main__':
    main()
