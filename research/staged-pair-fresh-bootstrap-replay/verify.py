#!/usr/bin/env python3
"""Check the retained PR3605 fresh-bootstrap transcript, not rerun its solvers.

roger-sato, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from datetime import datetime
from fractions import Fraction as Q
import hashlib
import io
import json
from pathlib import Path
import tarfile

from historical import WORDS, check_delta

HERE = Path(__file__).resolve().parent
HEAD = '3efbb5de06a49ffeea6684482f2d3fe48cdca3fb'
WRAPPER = '3c19c5a8f7f833af42c41e58d60deaeb0424bd33759ff28122eb0f7da0ff2a44'
SOURCE = 'adb145b4f36ca330c34c0dbdb847351dafdc4ca9cd7bb4e1de01ed634d96bfe1'
BOOT_SOURCE = 'c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
PARENT = 'e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
KAPPA = Q('0.001730006549538841847005') - Q(1, 10**46) - Q(1, 10**70)
PROFILE = {'1':16417896, '2':4835160, '3':1540174, '4':679321,
           '5':143992, '6':3, '8':53280, '48':283185}
TOP = ['exact-predecessor-exports-and-recipe', 'export-pr2894', 'export-pr2833',
       'fresh-retained-bootstrap', 'four-kernel-stage', 'preload-stage',
       'parent-paired-stage', 'paired-extension-stage', 'rank7-overlay-stage',
       'declared-edit-stage', 'staged-source-overlay', 'complete-source-word-rebuild',
       'staged-independent-word-controls', 'closed-source-adapters',
       'fresh-changed-native', 'fresh-literal-owners', 'complete-admission',
       'fresh-independent-owner-moment-outer']
BOOT = ['native-base', 'native-extra', 'native-retained-base',
        'native-retained-extra', 'retained-parent']
PARENT_STAGES = ['literal-word-base', 'literal-word-extra', 'independent-local-base',
    'fusion-controls-base', 'x54-controls-base', 'kernel543-controls-base',
    'kernel-controls-base', 'leaver-premise-base', 'independent-local-extra',
    'fusion-controls-extra', 'x54-controls-extra', 'kernel543-controls-extra',
    'kernel-controls-extra', 'leaver-premise-extra', 'literal-construct', 'strict-global']
ADMISSION = ['owners', 'parent-lift', 'rebind', 'discovery',
             'outer-check_ledger.py', 'outer-independent_check.py', 'release']
NATIVE = ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
SUPPLIER = ['fine-engine-oracle', 'retained-provider-and-parent-admission',
    'rebuild-words-566', 'reconstruct-owners', 'lift-parent', 'rebuild-borrow-words',
    'shared-kernel-independent-review', 'preload-move-independent-review',
    'two-sided-helper408-review', 'paired-extension-review', 'declared-edit-review',
    'staged-pair-independent-audit', 'audit-local-566-base', 'audit-local-566-extra',
    'rebind-566', 'lemmag-labels', 'strict-t74', 'geometry-controls']
INDEPENDENT = ['integer-primal-and-controls', 'literal-expansion', 'transport-base',
               'transport-extra', 'independent-whole-literal', 'rigorous-moment-and-outer']
NATIVE_FILES = {'STEPS.json', 'local/CANONICAL-WORD.json.gz', 'local/CLIFFORD-RECIPES.json',
    'local/CLIFFORD-REVIEW.json', 'local/FULL-WORD.json.gz', 'local/INDEPENDENT-LOCAL-REPLAY.json',
    'local/LOCAL-CHECKS.json', 'local/LOCAL-PROGRAMS.json.gz', 'local/RESIDUAL-ADAPTERS.json',
    'local/SCALAR-FRAME-AUDIT.json', 'local/WARP-RECIPE-CHECKS.json', 'local/WRAPPER-CHECKS.json'}
FAST_COMMANDS = ['native-bw_transport.py', 'ledgers-bw_emit.py',
    'local-replay-bw_audit_local.py', 'wrappers-bw_adapters.py',
    'phases-bw_phases.py', 'phases-bw_check_recipes.py']
R = 'runtime/'
B = R + 'source-stages/retained/'
C = R + 'candidate/'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def obj(files, name):
    return json.loads(files[name])


def log_name(name):
    return {'fresh-current-base':'native-base', 'fresh-current-extra':'native-extra'}.get(name, name) + '.log'


def stages(files, directory, expected, key='name', filename='STAGES.json', no_log=()):
    rows = obj(files, directory + filename)
    need([row[key] for row in rows] == expected, 'stage inventory: ' + directory)
    for row in rows:
        name = row[key]
        need(row['exit_code'] == 0, 'failed stage: ' + name)
        need(row['seconds'] >= 0, 'negative stage duration')
        if name not in no_log:
            need(sha(files[directory + log_name(name)]) == row['log_sha256'],
                 'stage log binding: ' + name)
        else:
            need(row.get('reused_receipt') == PARENT, 'same-run parent reuse identity')
        if 'script_sha256' in row:
            need(sha(files['scripts/' + row['script_sha256'] + '.py']) == row['script_sha256'],
                 'stage script binding: ' + name)
    return rows


def check(files):
    run = obj(files, 'attempt/RUN.json')
    before = obj(files, 'attempt/source-before.json')
    after = obj(files, 'attempt/source-after.json')
    need(run.get('exit_code') == 0 and run.get('completed_at'), 'unfinished attempt')
    need(datetime.fromisoformat(run['completed_at']) > datetime.fromisoformat(run['started_at'])
         and run['elapsed_seconds'] > 0, 'attempt timing')
    need(run['source_head'] == before['head'] == HEAD and before == after
         and not before['tracked_status'] and run['source_unchanged'], 'source changed')
    command = run['command']
    source_repo = command[command.index('--repo') + 1]
    runtime = command[command.index('--work') + 1]
    package = 'research/staged-644-660-conditional-release/'
    need(command == [command[0], '-B', source_repo + '/' + package + 'reproduce.py',
         '--repo', source_repo, '--word-package', source_repo + '/research/staged-644-660-width-reduction',
         '--work', runtime, '--jobs', '1'], 'full fresh command')
    need(run['environment']['GIT_NO_REPLACE_OBJECTS'] == '1'
         and {'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'PYTHONOPTIMIZE'}
         <= set(run['cleared_environment']), 'Git/interpreter environment')
    need(sha(files['attempt/stdout.log']) == run['stdout_sha256']
         and sha(files['attempt/stderr.log']) == run['stderr_sha256'], 'attempt log binding')
    need(sha(files['original/reproduce.py']) == WRAPPER
         == before['files'][package + 'reproduce.py']['sha256'], 'original wrapper identity')
    for name in ('CLAIM.json', 'FETCH.txt', 'STAGE-SCOPE.json'):
        data = files['original/' + name]
        pin = before['files'][package + name]
        need(sha(data) == pin['sha256'] and len(data) == pin['size'], 'original source identity: ' + name)
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == pin['git_blob'], 'original Git blob: ' + name)
    claim = obj(files, 'original/CLAIM.json')
    need(Q(claim['kappa']) == KAPPA and claim['profile'] == PROFILE, 'pinned claim')
    top = stages(files, R, TOP, key='stage')
    result = obj(files, R + 'RESULT.json')
    need(result['status'] == 'PASS_STAGED_PAIR_COMPLETE_CONDITIONAL_REPLAY'
         and result['fresh_retained_bootstrap'] is True
         and result['explicit_retained_reuse'] is False and result['stages'] == top,
         'complete fresh wrapper result')
    need(sha(files[R + 'source/MANIFEST.json']) == SOURCE == result['source_manifest_sha256']
         and len(obj(files, R + 'source/MANIFEST.json')) == 648, 'source648 manifest')
    need(sha(files[R + 'pr3133/MANIFEST.json']) ==
         '609209f577c9185b16825dd2e8bb30f0891205fddd2571a8f76c558e3cb1f70e',
         'exact PR3133 source export')
    need(sha(files[R + 'source-stages/pr2833/MANIFEST.json']) == BOOT_SOURCE
         and len(obj(files, R + 'source-stages/pr2833/MANIFEST.json')) == 541,
         'bootstrap541 manifest')
    bootstrap_stages = stages(files, B, BOOT)
    boot_result = obj(files, B + 'RESULT.json')
    boot = obj(files, B + 'NATIVE-RECEIPT.json')
    need(boot_result['environment_sha256'] == sha(files[B+'ENVIRONMENT.json'])
         and obj(files, B+'ENVIRONMENT.json')['assertions_enabled'] is True, 'bootstrap environment')
    need(boot_result['status'] == 'PASS_PR2833_FRESH_NATIVE_PREPARATION'
         and boot_result['stages'] == bootstrap_stages
         and boot_result['native_receipt_sha256'] == sha(files[B + 'NATIVE-RECEIPT.json'])
         and boot_result['source_manifest_sha256'] == BOOT_SOURCE
         and boot_result['source_file_count'] == 541, 'bootstrap result binding')
    need(boot['manifest_sha256'] == BOOT_SOURCE
         and boot['fresh_current_provider_count'] == 2
         and boot['fresh_retained_native_count'] == 2
         and boot['reused_retained_native_count'] == 0
         and boot['fresh_retained_parent'] is True
         and boot['reused_retained_parent'] is False
         and boot['retained_reuse_receipt_sha256'] is None, 'external retained reuse')
    parent_dir = B + 'native-cache/_receipts/' + PARENT + '/'
    parent = obj(files, parent_dir + 'RECEIPT.json')
    parent_stages = stages(files, B + 'retained-parent/', PARENT_STAGES)
    need(sha(files[parent_dir + 'RECEIPT.json']) == boot['retained_parent_receipt_sha256']
         and parent['vendor_manifest_sha256'] == PARENT, 'parent receipt binding')
    for name in ('RESULT.json', 'STAGES.json'):
        need(sha(files[parent_dir + name]) == parent['files'][name]
             and files[parent_dir + name] == files[B + 'retained-parent/' + name],
             'fresh parent receipt artifacts')
    need(obj(files, parent_dir + 'STAGES.json') == parent_stages, 'parent stage link')
    need(sha(files[R + 'source-stages/pr2833/vendor/pr1297/MANIFEST.json']) == PARENT
         and sha(files[R + 'source-stages/pr2833/vendor/pr1297/CLAIM.json']) == parent['claim_sha256'],
         'parent source and claim')
    parent_result = obj(files, parent_dir + 'RESULT.json')
    need(parent_result['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION',
         'parent admission status')
    need(Q(parent_result['kappa']) == Q(obj(files, R +
         'source-stages/pr2833/vendor/pr1297/CLAIM.json')['kappa']), 'parent exact endpoint')
    final = obj(files, R + 'native/NATIVE-RECEIPT.json')
    need(final['retained_reuse_receipt_sha256'] == sha(files[B + 'NATIVE-RECEIPT.json'])
         and final['retained_parent_receipt_sha256'] == boot['retained_parent_receipt_sha256'],
         'bootstrap-to-final native receipt link')
    need(final['manifest_sha256'] == SOURCE and final['fresh_current_provider_count'] == 2
         and final['fresh_retained_native_count'] == 0
         and final['reused_retained_native_count'] == 2
         and final['fresh_retained_parent'] is False
         and final['reused_retained_parent'] is True, 'same-run native reuse')
    native_stages = stages(files, R + 'native/', ['fresh-current-base', 'fresh-current-extra'])
    native_result = obj(files, R + 'native/RESULT.json')
    need(native_result['status'] == 'PASS_TWO_FRESH_SHARED_KERNEL_NATIVE_CHAINS_AUTHENTICATED_PARENT_REUSE'
         and native_result['environment_sha256'] == sha(files[R+'native/ENVIRONMENT.json'])
         and native_result['native_receipt_sha256'] == sha(files[R + 'native/NATIVE-RECEIPT.json'])
         and native_result['stages'] == native_stages
         and native_result['source_manifest_sha256'] == SOURCE, 'changed native result binding')
    # Each receipt binds a complete cache map; retained five-stage receipts are
    # checked against those maps, not inferred from the top-level fresh flag.
    for directory, receipt in ((B, boot), (R + 'native/', final)):
        need(set(receipt['providers']) == {'base', 'extra'}, 'native provider inventory')
        source_manifest = obj(files, R + ('source-stages/pr2833/MANIFEST.json'
                              if directory == B else 'source/MANIFEST.json'))
        need(all(receipt['providers'][tag]['word_sha256'] == source_manifest[
             'new/borrow/words/BORROW-WORD-43'+tag+'.json.gz'] for tag in ('base','extra')),
             'native provider source word binding')
        need(parent['words'] == {tag:obj(files, R+'source-stages/pr2833/MANIFEST.json')[
             'vendor/pr1297/'+name] for tag,name in (('base','gauge44-word.json.gz'),
             ('extra','extra-word.json.gz'))}, 'retained source word binding')
        words = {p['word_sha256'] for p in receipt['providers'].values()}
        words.update(parent['words'].values())
        need(len(words) == 4, 'four native cache entries')
        cache_members = {'_receipts/' + PARENT + '/' + name for name in
                         ('RECEIPT.json', 'RESULT.json', 'STAGES.json')}
        for word in words:
            expected_files = ((NATIVE_FILES - {'local/WARP-RECIPE-CHECKS.json'})
                | {step + '.log' for step in NATIVE}) if word in parent['words'].values() else NATIVE_FILES
            cache_members.update(word + '/' + name for name in expected_files | {'CACHE.json'})
            entry = directory + 'native-cache/' + word + '/'
            cache = obj(files, entry + 'CACHE.json')
            need(cache['word_sha256'] == word and set(cache['files']) == expected_files
                 and cache['files'] == {name[len(word)+1:]:digest
                    for name,digest in receipt['cache_files'].items()
                    if name.startswith(word + '/') and name != word + '/CACHE.json'}
                 and sha(files[entry+'CACHE.json']) == receipt['cache_files'][word+'/CACHE.json'],
                 'native cache member binding')
            steps = obj(files, entry + 'STEPS.json')
            need([r['step'] for r in steps] == NATIVE and all(r['exit_code'] == 0 for r in steps),
                 'five native steps')
            need(receipt['cache_files'][word + '/STEPS.json'] == sha(files[entry + 'STEPS.json']),
                 'native steps cache binding')
        need(set(receipt['cache_files']) == cache_members, 'complete cache inventory')
        for relative, digest in receipt['cache_files'].items():
            retained = directory + 'native-cache/' + relative
            if retained in files:
                need(sha(files[retained]) == digest, 'retained native cache byte binding')
        need(all(receipt['cache_files']['_receipts/'+PARENT+'/'+name] == sha(files[parent_dir+name])
             for name in ('RECEIPT.json', 'RESULT.json', 'STAGES.json')), 'same-run parent cache receipt binding')
        for provider in receipt['providers'].values():
            pin = provider['complete_native_files']
            prefix = provider['word_sha256'] + '/'
            need(len(pin) > 5 and pin == {k[len(prefix):]:v for k,v in receipt['cache_files'].items()
                 if k.startswith(prefix) and k != prefix + 'CACHE.json'}, 'complete provider map')
        for tag in ('base', 'extra'):
            fast = directory + ('fast-' if directory == B else 'fresh-') + tag + '/'
            commands = obj(files, fast + 'COMMANDS.json')
            need([row['step'] for row in commands] == FAST_COMMANDS
                 and all(row['exit_code'] == 0 for row in commands), 'six sparse native commands')
            fast_result = obj(files, fast + 'RESULT.json')
            if directory != B:
                row = next(row for row in native_stages if row['name'] == 'fresh-current-' + tag)
                need(row['result_sha256'] == sha(files[fast+'RESULT.json']), 'changed provider result link')
            provider = receipt['providers'][tag]
            need(fast_result['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY'
                 and fast_result['word_sha256'] == provider['word_sha256']
                 and fast_result['steps'] == obj(files, directory + 'native-cache/' +
                     provider['word_sha256'] + '/STEPS.json'), 'sparse native result binding')
            need(all(fast + name + '.log' in files for name in FAST_COMMANDS), 'sparse command logs')
    stages(files, C, ADMISSION)
    admitted = obj(files, C + 'RESULT.json')
    released = obj(files, C + 'release/RELEASE-RECEIPT.json')
    need(admitted['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and released['status'] == 'PASS_RELEASE', 'final release status')
    need(result['release_receipt_sha256'] == admitted['release_receipt_sha256']
         == sha(files[C + 'release/RELEASE-RECEIPT.json'])
         and admitted['native_receipt_sha256'] == sha(files[R + 'native/NATIVE-RECEIPT.json']),
         'terminal receipt link')
    manifest = files[C + 'package/MANIFEST.json']
    need(sha(manifest) == admitted['package_manifest_sha256'] == released['manifest_sha256']
         and len(json.loads(manifest)) == 652,
         'generated package manifest binding')
    for name in ('SPEC.json', 'new/SPEC.json'):
        need(sha(files[C+'package/'+name]) == json.loads(manifest)[name], 'generated SPEC byte binding')
    independent = obj(files, R + 'independent/RESULT.json')
    independent_stages = stages(files, R + 'independent/', INDEPENDENT, key='stage')
    need(independent['status'] == 'PASS_FRESH_FINITE_OWNER_MOMENT_AND_OUTER'
         and independent['stages'] == independent_stages and independent['roles'] == 2717280
         and independent['profile'] == PROFILE
         and [Q(x) for x in independent['root_interval']] == [Q(x) for x in claim['root_interval']],
         'independent complete owners and profile')
    need(all(Q(x) == KAPPA for x in (result['kappa'], admitted['kappa'],
         released['kappa_decimal'], independent['kappa'])), 'exact pinned endpoint')
    owner = obj(files, R+'independent/INDEPENDENT-OWNERS.json')
    arithmetic = obj(files, R+'independent/arithmetic/RESULT.json')
    profile = obj(files, R+'independent/literal/PROFILE.json')
    need(owner['status'] == 'PASS_INDEPENDENT_LITERAL_OWNER_WINDOWS_FAMILIES_PREFIXES_AND_INVOICE'
         and owner['roles'] == independent['roles'] == 2717280 and owner['calls'] == 6660
         and owner['replicas'] == 740 and owner['physical'] == 663549
         and owner['profile'] == profile == independent['profile'] == PROFILE
         and owner['idle'] == independent['idle'], 'independent owner leaf')
    need(arithmetic['status'] == 'PASS_FRESH_LITERAL_OWNER_MOMENT_AND_CONDITIONAL_OUTER_ARITHMETIC'
         and arithmetic['owner_result_sha256'] == sha(files[R+'independent/INDEPENDENT-OWNERS.json'])
         and arithmetic['profile_sha256'] == sha(files[R+'independent/literal/PROFILE.json'])
         and arithmetic['actual_profile'] == PROFILE and arithmetic['stock_live'] == 663040
         and arithmetic['dimension'] == 73
         and [Q(x) for x in arithmetic['root_interval']] == [Q(x) for x in independent['root_interval']]
         and Q(arithmetic['kappa']) == Q(arithmetic['kappa_decimal']) == KAPPA,
         'independent arithmetic leaf')
    spec = obj(files, C + 'package/SPEC.json')
    new_spec = obj(files, C + 'package/new/SPEC.json')
    need(spec['geometry']['replicas'] == new_spec['geometry']['replicas'] == 740
         and new_spec['expected']['global_profile'] == PROFILE
         and new_spec['expected']['mutations_rejected'] == 25
         and new_spec['outer_refinement']['endpoint_digits'] == 24, 'generated SPEC geometry and controls')
    async_audit = obj(files, C + 'discovery/global/audit/ASYNC-AUDIT.json')
    need(async_audit['complex_profile'] == PROFILE and async_audit['complex_live'] == 663040
         and async_audit['physical'] == 663549 and async_audit['complex_hosted_residuals'] == 2717280
         and async_audit['complete_invocations'] == 6660, 'complete profile and geometry')
    need(len(async_audit['mutations_rejected']) == 25 and async_audit['mutation_controls_run'],
         'actual controller controls')
    supplier = obj(files, C + 'release/verify/RESULT.json')
    supplier_stages = stages(files, C + 'release/verify/', SUPPLIER,
         no_log=('retained-provider-and-parent-admission',))
    need(supplier['status'] == 'PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION'
         and supplier['stages'] == supplier_stages and supplier['roles'] == 2717280
         and supplier['prefix_bits'] == 1479 and supplier['charged_prefix_bits'] == 2048,
         'supplier admission')
    # The original summary's controller count is historical; retain it verbatim.
    need(supplier['controls']['controller'] == 15, 'inherited summary changed')
    collected = obj(files, 'COLLECTION.json')
    need(collected['predecessor'] == obj(files, R + 'pr3133/MANIFEST.json')
         and collected['source648'] == obj(files, R + 'source/MANIFEST.json')
         and collected['bootstrap541'] == obj(files, R + 'source-stages/pr2833/MANIFEST.json')
         and collected['generated_package'] == json.loads(manifest)
         and collected['bootstrap_cache'] == boot['cache_files']
         and collected['final_cache'] == final['cache_files'], 'collected full-byte inventory binding')
    check_delta(files)
    return {'status':'PASS_RECORDED_PR3605_FRESH_BOOTSTRAP_EVIDENCE',
        'source_head':HEAD, 'top_stages':len(top), 'bootstrap_chains':4,
        'fresh_retained_parent_stages':len(parent_stages), 'changed_native_chains':2,
        'admission_stages':len(ADMISSION), 'supplier_stages':len(supplier_stages),
        'kappa':str(KAPPA), 'wall_seconds':run['elapsed_seconds'],
        'scope':'Recorded local transcript integrity/coverage only; no solvers rerun.'}


def controls(files):
    passed = []
    def reject(name, mutate, error):
        changed = deepcopy(files)
        mutate(changed)
        try:
            check(changed)
        except ValueError as exc:
            need(error in str(exc), name + ': wrong rejection: ' + str(exc))
            passed.append(name)
        else:
            raise ValueError('accepted invalid evidence: ' + name)
    def change(f, path, mutate):
        data = obj(f, path)
        mutate(data)
        f[path] = json.dumps(data).encode()
    def reused_bootstrap(f):
        change(f, B+'NATIVE-RECEIPT.json', lambda d:d.update(reused_retained_native_count=1))
        change(f, B+'RESULT.json', lambda d:d.update(native_receipt_sha256=sha(f[B+'NATIVE-RECEIPT.json'])))
    def missing_native_gate(f):
        receipt = obj(f, R+'native/NATIVE-RECEIPT.json')
        word = receipt['providers']['base']['word_sha256']
        change(f, R+'native/native-cache/'+word+'/STEPS.json', lambda d:d.pop())
    def empty_providers(f):
        change(f, R+'native/NATIVE-RECEIPT.json', lambda d:d.update(providers={}))
        change(f, R+'native/RESULT.json', lambda d:d.update(native_receipt_sha256=sha(f[R+'native/NATIVE-RECEIPT.json'])))
    def unpinned_endpoint(f):
        wrong = '0.0017301'
        change(f, C+'release/RELEASE-RECEIPT.json', lambda d:d.update(kappa_decimal=wrong))
        receipt_hash = sha(f[C+'release/RELEASE-RECEIPT.json'])
        change(f, R+'RESULT.json', lambda d:d.update(kappa=wrong, release_receipt_sha256=receipt_hash))
        change(f, C+'RESULT.json', lambda d:d.update(kappa=wrong, kappa_decimal=wrong, release_receipt_sha256=receipt_hash))
        change(f, R+'independent/RESULT.json', lambda d:d.update(kappa=wrong, kappa_decimal=wrong))
    def contradictory_owner(f):
        change(f, R+'independent/INDEPENDENT-OWNERS.json', lambda d:d.update(roles=2717279))
        change(f, R+'independent/arithmetic/RESULT.json',
            lambda d:d.update(owner_result_sha256=sha(f[R+'independent/INDEPENDENT-OWNERS.json'])))
    def rebound_phase_timing(f):
        path = R+'native/native-cache/'+WORDS['gauge44']+'/local/CLIFFORD-REVIEW.json'
        old = sha(f[path])
        change(f, path, lambda d:d.update(seconds=d['seconds']+1))
        new = sha(f[path])
        def rebind(report):
            report['phase_changes'][0]['current_raw_sha256'] = new
            edges = report['reconstruction'][0]['replacements']
            edges[new] = edges.pop(old)
        change(f, 'HISTORICAL-COMPARISON.json', rebind)
    reject('phase_timing_rebound_without_native_receipt', rebound_phase_timing,
        'retained native cache byte binding')
    reject('expanded_historical_replacement_claim',
        lambda f:change(f, 'HISTORICAL-COMPARISON.json',
            lambda d:d['reconstruction'][0]['replacements'].update({'0'*64:'1'*64})),
        'exact recorded replacement edges')
    reject('owner_leaf_contradicts_summary_with_rebound_hash', contradictory_owner, 'independent owner leaf')
    reject('arithmetic_leaf_contradicts_summary',
        lambda f:change(f, R+'independent/arithmetic/RESULT.json', lambda d:d.update(kappa='0.0017301')),
        'independent arithmetic leaf')
    reject('reused_bootstrap_despite_top_fresh_flag', reused_bootstrap, 'external retained reuse')
    reject('missing_native_phase_gate', missing_native_gate, 'five native steps')
    reject('unfinished_attempt', lambda f: change(f, 'attempt/RUN.json', lambda d:d.pop('completed_at')), 'unfinished attempt')
    reject('external_retained_argument', lambda f: change(f, 'attempt/RUN.json', lambda d:d['command'].extend(['--retained','external'])), 'full fresh command')
    reject('missing_bootstrap_stage', lambda f: change(f, R+'STAGES.json', lambda d:d.pop(3)), 'stage inventory')
    reject('missing_parent_stage', lambda f: change(f, B+'retained-parent/STAGES.json', lambda d:d.pop()), 'stage inventory')
    reject('corrupt_top_log', lambda f:f.update({R+TOP[-1]+'.log':b'PASS altered'}), 'stage log binding')
    reject('stale_bootstrap_link', lambda f: change(f, R+'native/NATIVE-RECEIPT.json', lambda d:d.update(retained_reuse_receipt_sha256='0'*64)), 'bootstrap-to-final')
    reject('consistent_unpinned_endpoint_above_wrapper_floor', unpinned_endpoint, 'exact pinned endpoint')
    reject('empty_final_provider_map', empty_providers, 'native provider inventory')
    reject('changed_complete_profile', lambda f: change(f, C+'discovery/global/audit/ASYNC-AUDIT.json', lambda d:d['complex_profile'].update({'6':0})), 'complete profile')
    return passed


def load_evidence():
    expected = json.loads((HERE/'EXPECTED.json').read_bytes())
    data = (HERE/'evidence.tar.gz').read_bytes()
    need(sha(data) == expected['archive_sha256'], 'retained archive bytes')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for member in archive.getmembers():
            need(member.isfile() and member.name not in files and not Path(member.name).is_absolute()
                 and '..' not in Path(member.name).parts, 'archive member')
            files[member.name] = archive.extractfile(member).read()
    need({name:sha(data) for name,data in files.items()} == expected['members'], 'retained member inventory')
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    files = load_evidence()
    result = check(files)
    result['negative_controls'] = controls(files)
    text = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.out:
        args.out.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
