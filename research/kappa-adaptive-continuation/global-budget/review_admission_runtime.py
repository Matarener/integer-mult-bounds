#!/usr/bin/env python3
"""Review the repaired source extension and rerun both modern outer engines.

The active release workspace is read only. Outer scripts run unchanged in a
new private copy, with the endpoint/profile from native_owner_invoice.py.
This does not replace the parent task's full release invocation.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from argparse import ArgumentParser
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
UP = HERE.parent/'sources/PR3815/research/staged544-producer-return'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--invoice', type=Path, default=HERE/'receiver-sharing/RESULT.json')
    ap.add_argument('--out', type=Path, default=HERE/'admission-review-low-memory')
    args = ap.parse_args()
    need(not args.out.exists(), 'fresh review output directory')
    work = args.work.resolve()
    source = work/'inputs/source'
    package = work/'admission/package'
    invoice = read(args.invoice)
    need(invoice['status'] == 'PASS_LITERAL_CHANGED_NATIVE_OWNERS_AND_TWO_ENGINE_INVOICE', 'finite invoice gate')
    need(invoice['script_sha256'] == sha(HERE/'native_owner_invoice.py'), 'invoice implementation pin')
    for paths in invoice['supplied_native_inputs'].values():
        for rel, expected in paths.items():
            need(sha(REPO/rel) == expected, 'actual changed native input pin')
    original_pins = read(UP/'REPLAY-INPUTS.json')
    archive_path = UP/'REPLAY-INPUTS.tar.gz'
    need(sha(archive_path) == original_pins['archive_sha256'], 'original full replay archive')
    adaptation_path = work/'SOURCE-ADAPTATION.json'
    adaptation = read(adaptation_path)
    adapter_path = work/'ADMISSION-ADAPTER.json'
    adapter = read(adapter_path)
    runtime_review_path = HERE.parent/'runtime-repair/REVIEW-INVOICE.json'
    runtime_review = read(runtime_review_path)
    need(runtime_review['status'] == 'PASS_INDEPENDENT_RUNTIME_SOURCE_AND_CONTROL_REVIEW', 'independent runtime review gate')
    need(runtime_review['script_sha256'] == sha(HERE/'review_runtime.py'), 'runtime review implementation')
    need(runtime_review['adapter_sha256'] == sha(HERE.parent/'runtime-repair/audit_fast.py'), 'runtime review adapter binding')
    with tarfile.open(archive_path) as archive:
        def original(name):
            data = archive.extractfile('source/'+name).read()
            need(hashlib.sha256(data).hexdigest() == original_pins['files']['source/'+name], 'archive member pin')
            return data
        original_manifest_bytes = original('MANIFEST.json')
        original_manifest = json.loads(original_manifest_bytes)
        need(hashlib.sha256(original_manifest_bytes).hexdigest() == adaptation['predecessor_manifest_sha256'],
             'source adaptation starts at pinned predecessor')
        current_manifest = read(source/'MANIFEST.json')
        current = {p.relative_to(source).as_posix(): sha(p) for p in source.rglob('*')
                   if p.is_file() and p != source/'MANIFEST.json'}
        need(current == current_manifest and sha(source/'MANIFEST.json') == adaptation['current_manifest_sha256'],
             'current immutable source manifest')
        need(set(original_manifest) <= set(current), 'all original source files retained')
        delta = {name: {'before': original_manifest.get(name), 'after': current[name]}
                 for name in current if original_manifest.get(name) != current[name]}
        need(delta == adaptation['files'], 'complete source change census')
        need(len(current) == adaptation['source_file_count'] == 664, 'exact expanded source file count')
        exact_patches = []
        for patch in adaptation['exact_patches']:
            name = patch['path']
            text = original(name).decode().replace('\r\n', '\n').replace('\r', '\n')
            need(hashlib.sha256(original(name)).hexdigest() == patch['before_sha256'], 'patch original hash')
            need(text.count(patch['old']) == 1, 'unique source patch preimage')
            changed = text.replace(patch['old'], patch['new'])
            need(changed == (source/name).read_text(), 'source patch has no additional edits')
            need(sha(source/name) == patch['after_sha256'], 'source patch final hash')
            exact_patches.append(name)
        need(set(exact_patches) == {'new/rebuild_borrow.py', 'new/borrow/review_staged544.py', 'verify.py'},
             'only declared predecessor source control-flow changes')
        expected_delta = set(exact_patches) | {
            'audit_fast.py', 'new/BORROW-PROVIDERS.json',
            'new/borrow/receiver_share.py', 'new/borrow/review_receiver_share.py',
            'new/borrow/receiver-share-parent/BORROW-WORD-43base.json.gz',
            'new/borrow/receiver-share-parent/BORROW-WORD-43extra.json.gz',
            'new/borrow/words/BORROW-WORD-43base.json.gz',
            'new/borrow/words/BORROW-WORD-43extra.json.gz'}
        need(set(delta) == expected_delta, 'every changed source path is explicitly reviewed')
        runtime = adaptation['runtime_adapter']
        need(runtime['path'] == 'audit_fast.py', 'only the bulk runtime wrapper is replaced')
        need(hashlib.sha256(original('audit_fast.py')).hexdigest() == runtime['before_sha256'], 'original runtime wrapper preimage')
        need(sha(source/'audit_fast.py') == runtime['after_sha256'] == runtime_review['adapter_sha256'], 'exact independently reviewed runtime wrapper')
        need(sha(source/'code/audit_allcold.py') == runtime['original_scientific_auditor_sha256'] == runtime_review['auditor_sha256'], 'unchanged scientific auditor remains source-bound')
        need(sha(source/'code/emit_allcold.py') == runtime['unchanged_emitter_sha256'] == runtime_review['emitter_sha256'], 'unchanged emitter remains source-bound')
        need(runtime['control_mode'] == 'fork' and runtime['preserved_scientific_assertions'] == 76 and
             runtime['equivalent_streamed_digest_assertions'] == 1 and runtime['preserved_mutator_call_sites'] == 27,
             'runtime semantics and complete mutation call-site census')
        need(runtime['failure_mode_fixtures_sha256'] == sha(HERE.parent/'runtime-repair/FIXTURES.json'), 'runtime failure fixtures binding')
        for tag in ('base', 'extra'):
            name = 'BORROW-WORD-43'+tag+'.json.gz'
            retained = source/'new/borrow/receiver-share-parent'/name
            need(retained.read_bytes() == original('new/borrow/words/'+name), 'old staged544 review retains exact old word')
            need((source/'new/borrow/words'/name).read_bytes() ==
                 (HERE.parent/'native-alternatives/candidate'/name).read_bytes(), 'new source word is native-audited candidate')
        providers = json.loads(original('new/BORROW-PROVIDERS.json'))
        expected = deepcopy(providers)
        for pid in ('gauge44', 'extra'):
            expected[pid]['actual_paid_profile'] = invoice['provider_local_profiles'][pid]
        need(read(source/'new/BORROW-PROVIDERS.json') == expected, 'provider metadata changes only actual paid profile')
    for name in ('receiver_share.py', 'review_receiver_share.py'):
        need((source/'new/borrow'/name).read_bytes() == (HERE.parent/'admission'/name).read_bytes(),
             'new source edit and review are the reviewed implementations')
    old_adapter = work/'inputs/admit544.py'
    new_adapter = work/'admit_receiver_share.py'
    need(sha(old_adapter) == adapter['original_sha256'] == original_pins['files']['admit544.py'], 'original admission machinery hash')
    text = old_adapter.read_text()
    need(len(adapter['exact_replacements']) == 2, 'two immutable source identity replacements')
    for old, new in adapter['exact_replacements']:
        need(text.count(old) == 1, 'unique admission adapter preimage')
        text = text.replace(old, new)
    need(text == new_adapter.read_text() and sha(new_adapter) == adapter['adapted_sha256'],
         'no admission assertion, charge, rejection control or cost formula changed')
    # Arithmetic-only outer replay. This copy supplies an independently checked
    # endpoint and profile now, while full supplier discovery/release continues.
    spec_path = package/'new/SPEC.json'
    spec = read(spec_path)
    original_spec = deepcopy(spec)
    lower = F(invoice['root']['rational'][0])
    upper = F(invoice['root']['rational'][1])
    previous = F(read(HERE/'PR3815-INDEPENDENT-REVIEW.json')['conditional_kappa'])
    spec['expected'].update(complex_lower=str(lower), global_profile=invoice['profile'],
                            live=invoice['productive_families'], kappa=str(previous))
    need(spec['geometry']['dimension'] == 73 and spec['geometry']['replicas'] == 360, 'unchanged outer geometry')
    need(spec['outer_refinement']['endpoint_digits'] == 24, 'same outer precision family')
    args.out.mkdir(parents=True)
    (args.out/'outer').mkdir()
    (args.out/'new').mkdir()
    (args.out/'new/SPEC.json').write_text(json.dumps(spec, sort_keys=True, indent=2)+'\n')
    shutil.copyfile(package/'CLAIM.json', args.out/'CLAIM.json')
    b = dict(b=str(lower-F(1, 10**104)), b_above_endpoint=str(upper),
             profile=invoice['profile'], live=invoice['productive_families'])
    (args.out/'outer/B.json').write_text(json.dumps(b, sort_keys=True, indent=2)+'\n')
    scripts, runs = {}, []
    for name in ('check_ledger.py', 'independent_check.py'):
        path = package/'outer'/name
        scripts[name] = sha(path)
        shutil.copyfile(path, args.out/'outer'/name)
        with (args.out/(name+'.log')).open('w') as stream:
            run = subprocess.run([sys.executable, '-B', str(args.out/'outer'/name)],
                                 stdout=stream, stderr=subprocess.STDOUT,
                                 env=dict(os.environ, PYTHONOPTIMIZE='', PYTHONDONTWRITEBYTECODE='1'))
        need(run.returncode == 0, 'modern outer engine: '+name)
        runs.append({'script': name, 'sha256': scripts[name], 'exit_code': run.returncode})
    ledger, independent = read(args.out/'outer/LEDGER.json'), read(args.out/'outer/INDEPENDENT.json')
    need(ledger['status'] == 'PASS_FINE_PRIME_PADDING_EXACT_ARITHMETIC', 'full modern outer ledger')
    need(independent['status'] == 'PASS_INDEPENDENT_BALANCE_DERIVATION', 'independent modern outer balance')
    row = ledger['rows']['struct_boundary_radix_union']
    kappa = F(row['kappa']['rational'])
    need(kappa == F(independent['rows']['struct_boundary_radix_union']['kappa']) == lower-F(1, 10**46)-F(1, 10**70),
         'both modern outer engines produce the same exact headline')
    need(len(row['strict_checks']) == 63 and all(F(value['rational']) > 0 for value in row['strict_checks'].values()),
         'all original strict outer inequalities')
    controls = ledger['rejecting_controls']['struct_boundary_radix_union']
    need(len(controls) == 17 and all(controls.values()), 'all original outer rejecting controls')
    result = {
        'status': 'PASS_REPAIRED_SOURCE_EXTENSION_ADAPTER_AND_BOTH_MODERN_OUTER_ENGINES',
        'script_sha256': sha(Path(__file__)), 'invoice_sha256': sha(args.invoice),
        'source_adaptation_sha256': sha(adaptation_path), 'admission_adapter_sha256': sha(adapter_path),
        'source_manifest_sha256': sha(source/'MANIFEST.json'),
        'runtime_adapter_sha256': runtime_review['adapter_sha256'],
        'runtime_independent_review_sha256': sha(runtime_review_path),
        'runtime_adaptation': runtime,
        'source_changed_files': delta, 'reviewed_source_patches': exact_patches,
        'admission_adapter_replacements': adapter['exact_replacements'],
        'source_archive_sha256': sha(archive_path), 'modern_outer_scripts': scripts, 'modern_outer_runs': runs,
        'outer_spec_source_sha256': hashlib.sha256(json.dumps(original_spec, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        'outer_spec_explicit_replacements': {'expected.complex_lower': str(lower), 'expected.global_profile': invoice['profile'],
                                             'expected.live': invoice['productive_families'], 'expected.kappa': str(previous)},
        'outer_strict_checks': 63, 'outer_rejecting_controls': sorted(controls),
        'complex_root': invoice['root']['rational'], 'conditional_kappa': str(kappa),
        'strict_gain_over_adopted_ceiling': str(kappa-previous),
        'below_retained_bit_cap': kappa < F('0.001733427039589844234749'),
        'full_supplier_release_replaced': False,
        'scope': ('Byte-exact review of the explicit source extension, independently reviewed memory repair, and identity-only admission adapter; '
                  'fresh executions of both unchanged modern outer engines, using the separately verified '
                  'complete physical invoice. This does not substitute for the ongoing full supplier discovery '
                  'and release pipeline. All inherited all-size, realization, precision/recovery, analytic '
                  'and BIT premises remain.')
    }
    (args.out/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'kappa', row['kappa']['decimal'], 'checks', 63, 'controls', 17)


if __name__ == '__main__':
    main()
