#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independently bind the completed final run to its scientific receipt chain.

This is a read-only review of an actual completed run, not another expensive
native or whole-owner semantic replay. It does not recover success from any
failed or interrupted attempt. Substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
RUNNER_SHA = '081c39ee0636890f2fa8ae2fa070c03c9d6d25cc4594759d7ece2fd79a173ae9'
SOURCE_SHA = '18acd9411cbca007d37c5058ecb12b45cc3b82c15ddd0833444fede8fc14473e'
LOWER = F('0.001730739780298357321619')
UPPER = F('0.001730739780298357321620')
KAPPA = LOWER-F(1, 10**46)-F(1, 10**70)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4*1024*1024), b''):
            result.update(chunk)
    return result.hexdigest()


def content_sha(path):
    result = hashlib.sha256()
    with gzip.open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(4*1024*1024), b''):
            result.update(chunk)
    return result.hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def tree(path, excludes=()):
    need(path.is_dir() and not path.is_symlink(), 'real input directory')
    result = {}
    for item in sorted(path.rglob('*')):
        need(not item.is_symlink(), 'no symbolic link in authenticated input tree')
        if item.is_file() and item.relative_to(path).as_posix() not in excludes:
            result[item.relative_to(path).as_posix()] = sha(item)
    return result


def main():
    need(__debug__, 'Run this review with Python assertions enabled')
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--executed-runner', type=Path, default=PACKAGE/'run_candidate_release.py',
                        help='The exact source snapshot executed by this completed run, including when the delivered entry point later receives a reviewed guard-only change.')
    parser.add_argument('--out', type=Path, default=HERE/'FINAL-RELEASE-REVIEW.json')
    args = parser.parse_args()
    work = args.work.resolve()
    top = read(work/'RESULT.json')
    need(top['status'] == 'PASS_RECEIVER_SHARING_COMPLETE_CONDITIONAL_RELEASE', 'final runner must have completed')
    need(top['runner_sha256'] == sha(args.executed_runner) == RUNNER_SHA, 'exact launched final runner snapshot')
    need(F(top['root_lower']) == LOWER and F(top['root_upper']) == UPPER and F(top['kappa_rational']) == KAPPA, 'actual final endpoint and outer kappa')
    source, cache = work/'inputs/source', work/'inputs/native-cache'
    source_map = tree(source, ('MANIFEST.json',))
    need(source_map == read(source/'MANIFEST.json') and len(source_map) == 664, 'all actual immutable source files')
    need(sha(source/'MANIFEST.json') == SOURCE_SHA == top['source_manifest_sha256'], 'source manifest pin')
    adaptation = read(work/'SOURCE-ADAPTATION.json')
    reviewed_adaptation = read(PACKAGE/'global-budget/admission-review-low-memory/RESULT.json')
    need(adaptation['current_manifest_sha256'] == reviewed_adaptation['source_manifest_sha256'] == SOURCE_SHA, 'same independently reviewed repaired scientific source')
    need(sha(work/'ADMISSION-ADAPTER.json') == reviewed_adaptation['admission_adapter_sha256'], 'same independently reviewed identity-only admission adapter')
    need(sha(work/'admit_receiver_share.py') == read(work/'ADMISSION-ADAPTER.json')['adapted_sha256'], 'actual executed admission adapter bytes')
    native_receipt = read(work/'NATIVE-RECEIPT.json')
    need(sha(work/'NATIVE-RECEIPT.json') == top['native_receipt_sha256'], 'top-level native receipt binding')
    need(tree(cache) == native_receipt['cache_files'], 'entire current and retained ancestor cache tree unchanged')
    auth_path = PACKAGE/'replay-support/native_auth.py'
    native_review = read(PACKAGE/'replay-support/REVIEW-INVOICE.json')
    need(native_review['status'] == 'PASS_INDEPENDENT_NATIVE_AUTH_SOURCE_PINS_AND_CONTROL_REVIEW', 'native authentication review gate')
    need(native_review['native_auth_sha256'] == sha(auth_path), 'reviewed native authentication implementation')
    spec = importlib.util.spec_from_file_location('final_release_native_auth', auth_path)
    auth = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auth)
    current_native_binding = auth.authenticate_admission_inputs(work)
    reused_native_binding = auth.authenticate_reused(PACKAGE/'native-alternatives')
    need(reused_native_binding == read(work/'REUSED-NATIVE-AUTH.json'), 'exact reused current native executions')
    actual_native_sources = read(work/'ACTUAL-NATIVE-SOURCES.json')
    need(sha(work/'ACTUAL-NATIVE-SOURCES.json') == top['actual_native_sources_sha256'], 'actual native source receipt binding')
    for tag in ('base', 'extra'):
        need(actual_native_sources[tag] == auth.authenticate_fresh_native(PACKAGE/'native-alternatives'/('native-'+tag), tag), 'actual source/input/output declarations of current native run')

    invoice_path = PACKAGE/'global-budget/receiver-sharing/RESULT.json'
    invoice = read(invoice_path)
    need(invoice['status'] == 'PASS_LITERAL_CHANGED_NATIVE_OWNERS_AND_TWO_ENGINE_INVOICE', 'independent actual owner and invoice gate')
    need(invoice['script_sha256'] == sha(PACKAGE/'global-budget/native_owner_invoice.py'), 'independent invoice implementation')
    expected_profile = {int(r): n for r, n in invoice['profile'].items()}
    native_profiles = {}
    for tag, provider in (('base', 'gauge44'), ('extra', 'extra')):
        key = current_native_binding['providers'][tag]['word_sha256']
        entry = cache/key
        word = read(entry/'local/CANONICAL-WORD.json.gz')
        need((word['v'], word['h'], word['R'], len(word['zero_buffers'])) == (112, 9, 408, 91), 'same complete native data and owned-work geometry')
        programs = read(entry/'local/LOCAL-PROGRAMS.json.gz')
        wanted = Counter({int(r): n for r, n in invoice['provider_local_profiles'][provider].items()})
        need(set(programs) == {'forward', 'backward'}, 'both native orientations')
        for direction, events in programs.items():
            actual = Counter(event[-1] for event in events if event[0] in ('climb', 'center'))
            need(actual == wanted, 'actual final cache native paid profile: '+provider+'/'+direction)
        native_profiles[provider] = dict(wanted)
    need(native_profiles['gauge44'] == native_profiles['extra'], 'same native bill for both providers')
    fill = read(work/'admission/owners/RESULT.json')
    need(fill['status'] == 'PASS_EXACT_BORROW_WORD_REPLICA_OWNER_FILL', 'actual final owner fill gate')
    need(fill['roles'] == 1321920 and fill['helpers_per_call'] == 408 and sum(fill['dispatch'].values()) == 3240, 'all actual helper roles and calls')
    derived_profile = Counter({int(r): n for r, n in fill['idle'].items()})
    derived_profile.update({r: 3240*n for r, n in native_profiles['gauge44'].items()})
    need(dict(derived_profile) == expected_profile == {int(r): n for r, n in top['global_profile'].items()}, 'independently compose complete local and physical idle invoice')
    need(sum(r*n for r, n in expected_profile.items()) == 23431680, 'complete raw rank mass')

    admission = read(work/'admission/RESULT.json')
    release = read(work/'admission/release/RELEASE-RECEIPT.json')
    supplier = read(work/'admission/release/verify/RESULT.json')
    strict_dir = work/'admission/release/verify/strict'
    strict = read(strict_dir/'RESULT.json')
    assembly = read(strict_dir/'ASSEMBLY.json')
    need(admission['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'complete ordinary admission')
    need(release['status'] == 'PASS_RELEASE', 'original ordinary release passes')
    need(supplier['status'] == 'PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION', 'fresh supplier verification')
    need(strict['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL', 'fresh strict invocation, owner and finite admission')
    need(assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and len(assembly['outer']) == 47, 'complete original strict assembly')
    need(sha(work/'admission/RESULT.json') == top['admission_result_sha256'], 'final admission receipt binding')
    need(sha(work/'admission/release/RELEASE-RECEIPT.json') == top['release_receipt_sha256'] == admission['release_receipt_sha256'], 'original release receipt binding')
    need(admission['source_manifest_sha256'] == SOURCE_SHA and admission['native_receipt_sha256'] == top['native_receipt_sha256'], 'complete admission source/cache identity')
    need(F(admission['complex_lower']) == F(assembly['complex_lower']) == LOWER and
         F(admission['kappa']) == F(release['kappa_decimal']) == KAPPA, 'source assembly supplies actual modern outer endpoint')
    need(F(assembly['bit_lower']) == F('0.001733427039589844234749'), 'retained BIT side bound')
    need({int(r): n for r, n in assembly['complex_profile'].items()} == expected_profile ==
         {int(r): n for r, n in admission['profile'].items()}, 'complete supplier and admission profile')
    package = work/'admission/package'
    package_manifest = sha(package/'MANIFEST.json')
    need(tree(package, ('MANIFEST.json',)) == read(package/'MANIFEST.json'), 'entire ordinary package immutable after verification')
    need(package_manifest == release['manifest_sha256'] == admission['package_manifest_sha256'] == supplier['manifest_sha256'], 'ordinary release manifest chain')

    actual_audit = strict_dir/'global/audit'
    owner = read(actual_audit/'OWNERS-AND-PROFILE.json')
    controller = read(actual_audit/'ASYNC-AUDIT.json')
    paid = read(actual_audit/'PREFIX-AND-INVOICE.json')
    need(owner['status'] == 'PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE' and controller['status'] == 'PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS', 'actual complete owner and chronology receipts')
    need(paid['status'] == 'PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE', 'actual scalar, coefficient and finite invoice')
    need((owner['live'], owner['physical'], owner['hosted_residuals']) == (322560, 323069, 1321920), 'actual productive denominator and total physical stock')
    need((paid['live'], paid['physical'], paid['helpers'], paid['centres'], paid['private_zero_buffers']) == (322560, 323069, 408, 8, 91), 'every owned reserve is included')
    need(paid['owner_audit_sha256'] == sha(actual_audit/'OWNERS-AND-PROFILE.json') and
         paid['controller_audit_sha256'] == owner['controller_audit_sha256'] == sha(actual_audit/'ASYNC-AUDIT.json'), 'finite invoice binds actual owner/controller files')
    need({int(r): n for r, n in owner['paid_profile'].items()} == expected_profile ==
         {int(r): n for r, n in controller['complex_profile'].items()}, 'actual fully checked physical profile')
    need(controller['complete_invocations'] == 3240 and controller['helper_busy_family_window_checks'] == 1321920 and
         controller['mutation_controls_run'] and controller['all_provider_program_phase_and_wrapper_bindings'], 'all physical/native bindings and chronology controls run')
    need(content_sha(strict_dir/'global/hosted/GLOBAL-TEMPLATE.json.gz') == controller['template_sha256'] == owner['template_sha256'] == paid['template_sha256'], 'actual final global template decompressed hash')
    need(paid['global_prefix_bits'] < paid['charged_prefix_bits'] == 2048 and all(paid['strict_checks'].values()), 'all finite and scalar-prefix side conditions')
    need(paid['blocknorm']['status'] == 'PASS_TENSOR_BLOCK_NORM_CERTIFICATE' and paid['blocknorm']['max_active_depth'] == 18, 'actual block norm charge')
    controls = {
        'admission': len(read(strict_dir/'ADMISSION-CONTROLS.json')['rejected_controls']),
        'bit': len(read(strict_dir/'BIT-CONTROLS.json')['rejected_controls']),
        'independent_owner': len(strict['independent']['controls_rejected']),
        'geometry': len(read(work/'admission/release/verify/GEOMETRY-CONTROLS.json')['rejected']),
        'actual_async_controller': len(controller['mutations_rejected'])}
    need({k: controls[k] for k in ('admission', 'bit', 'independent_owner', 'geometry')} ==
         {'admission': 139, 'bit': 12, 'independent_owner': 8, 'geometry': 6}, 'all original strict rejecting controls')
    need(controls['actual_async_controller'] == len(set(controller['mutations_rejected'])) == 25, 'all 25 distinct both-provider controller rejection cases')

    ledgers = {}
    for name in ('LEDGER.json', 'INDEPENDENT.json'):
        committed = package/'outer'/name
        fresh = work/'admission/release/outer-tmp/outer'/name
        need(read(committed) == read(fresh), 'fresh ordinary outer artifact equals its admitted artifact: '+name)
        ledgers[name] = read(fresh)
    need(ledgers['LEDGER.json']['status'] == 'PASS_FINE_PRIME_PADDING_EXACT_ARITHMETIC' and
         ledgers['INDEPENDENT.json']['status'] == 'PASS_INDEPENDENT_BALANCE_DERIVATION', 'both modern engines completed in original outer run')
    row = ledgers['LEDGER.json']['rows']['struct_boundary_radix_union']
    need(F(row['kappa']['rational']) == F(row['kappa']['decimal']) ==
         F(ledgers['INDEPENDENT.json']['rows']['struct_boundary_radix_union']['kappa']) == KAPPA, 'both modern outer engines agree exactly')
    need(len(row['strict_checks']) == 63 and all(F(v['rational']) > 0 for v in row['strict_checks'].values()), 'all 63 strict outer inequalities')
    outer_controls = ledgers['LEDGER.json']['rejecting_controls']['struct_boundary_radix_union']
    need(len(outer_controls) == 17 and all(outer_controls.values()), 'all 17 original outer rejection controls')
    need((work/'admission/release/outer.log').read_text().rstrip().endswith('PASS_OUTER'), 'the original outer run also completed its schedule, symbolic and finite evidence checks')

    stages = read(work/'STAGES.json')
    need(stages == top['stages'] and all(row['exit_code'] == 0 for row in stages), 'every final-run stage completed successfully')
    names = [row['name'] for row in stages]
    need(names[-1] == 'complete-admission' and {'numpy-preflight', 'complete-dependency-preflight', 'independent-receiver-word'} <= set(names), 'final run includes dependency preflight and actual complete admission')
    for row in stages:
        need(sha(work/(row['name']+'.log')) == row['log_sha256'], 'actual final runner stage log binding')
    need(sha(work/'DEPENDENCIES.json') == top['dependency_record_sha256'], 'final preflight dependency record')
    dependencies = read(work/'DEPENDENCIES.json')
    need(dependencies['versions']['sympy'] == '1.14.0' and dependencies['versions']['mpmath'] == '1.3.0', 'previous missing dependencies were present before this full run')

    paths = ['RESULT.json', 'STAGES.json', 'SOURCE-ADAPTATION.json', 'NATIVE-RECEIPT.json', 'ACTUAL-NATIVE-SOURCES.json',
             'REUSED-NATIVE-AUTH.json', 'DEPENDENCIES.json', 'admission/RESULT.json',
             'admission/release/RELEASE-RECEIPT.json', 'admission/release/verify/RESULT.json',
             'admission/release/verify/strict/RESULT.json', 'admission/release/verify/strict/ASSEMBLY.json',
             'admission/release/verify/strict/global/audit/ASYNC-AUDIT.json',
             'admission/release/verify/strict/global/audit/OWNERS-AND-PROFILE.json',
             'admission/release/verify/strict/global/audit/PREFIX-AND-INVOICE.json',
             'admission/release/outer-tmp/outer/LEDGER.json', 'admission/release/outer-tmp/outer/INDEPENDENT.json']
    result = {
        'status': 'PASS_INDEPENDENT_FINAL_COMPLETE_RELEASE_RECEIPT_CHAIN',
        'script_sha256': sha(Path(__file__)), 'work_directory_name': work.name,
        'executed_runner_sha256': RUNNER_SHA, 'scientific_source_manifest_sha256': SOURCE_SHA,
        'ordinary_package_manifest_sha256': package_manifest,
        'native_authentication_review_sha256': sha(PACKAGE/'replay-support/REVIEW-INVOICE.json'),
        'independent_actual_invoice_sha256': sha(invoice_path),
        'final_run_receipt_sha256': {name: sha(work/name) for name in paths},
        'global_profile': expected_profile, 'productive_fields': 322560, 'physical_fields': 323069,
        'helper_roles': 1321920, 'local_calls': 3240, 'paid_raw_rank_mass': 23431680,
        'complex_root': [str(LOWER), str(UPPER)], 'modern_outer_kappa': str(KAPPA),
        'strict_supplier_kappa': supplier['kappa'], 'strict_supplier_controls': controls,
        'modern_outer_strict_inequalities': 63, 'modern_outer_rejecting_controls': 17,
        'actual_prefix_bits': paid['global_prefix_bits'], 'charged_prefix_bits': paid['charged_prefix_bits'],
        'complete_run_stages': names,
        'current_native_executions_reused_exactly': True,
        'retained_ancestor_caches_authenticated_without_claiming_new_native_execution': True,
        'fresh_final_source_strict_admission_and_original_release_completed': True,
        'failed_or_interrupted_attempts_used_to_infer_pass': False,
        'semantic_replays_rerun_by_this_receipt_review': False,
        'scope': 'The actual final prepared workspace completed its fresh discovery, original supplier verification, strict whole-owner and finite admission, original outer run and PASS_RELEASE. Both current native providers are reused byte-for-byte from the separately completed five-stage runs, with actual source and cache identities checked. Retained ancestry is authenticated reuse. No failed or interrupted attempt contributes a success status. This is a receipt-chain review of the completed conditional release, not a rerun of its expensive semantic checks or an unconditional all-size multiplication theorem.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], 'kappa', ledgers['LEDGER.json']['rows']['struct_boundary_radix_union']['kappa']['decimal'],
          'actual controller controls', controls['actual_async_controller'])


if __name__ == '__main__':
    main()
