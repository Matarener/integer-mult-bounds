#!/usr/bin/env python3
"""Review the final selector without running invoices, native or full release.

Execute only the actual isolated comparison functions on generated transport
and scientific-change fixtures. Authenticate the late portable input closure
and the unchanged primary packaging scripts. No frozen input is modified.
Apache-2.0. Substantial OpenAI assistance.
"""
import ast
from copy import deepcopy
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
REPO = SCOPE.parents[1]
LATE = SCOPE / 'late-staged-composition'
EXPECTED = {
    'replay_latest.py': '64786bee1c5c56328ca09c98bd9828af92732a373d49bb95ef56e2d514c60a6c',
    'freeze_latest_manifest.py': '28ba1ec8264be5b5ebdeb8aff6a060780f0734e64ede7c842bb5a83c9d46f7d3',
    'package_latest.py': '7531df51fa569e2174a0beebe495671f14d32f698d0e2237639eaf5b565201fe',
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def write(path, data):
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + '\n')


def comparator_controls():
    path = SCOPE / 'replay_latest.py'
    parsed = ast.parse(path.read_text())
    main = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    functions = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in ('word_payload', 'construction_view')]
    functions += [n for n in main.body if isinstance(n, ast.FunctionDef) and n.name in ('compare_word', 'compare_construction', 'compare_phase')]
    need(len(functions) == 5, 'Exact reviewed comparator functions')
    isolated = ast.Module(body=functions, type_ignores=[])
    ast.fix_missing_locations(isolated)
    comparisons = []
    namespace = dict(need=need, read=read, sha=sha, REPO=REPO, gzip=gzip, hashlib=hashlib,
                     json=json, math=math, deepcopy=deepcopy, comparisons=comparisons)
    exec(compile(isolated, str(path), 'exec'), namespace)
    fixtures = HERE / 'latest-fixtures'
    fixtures.mkdir(exist_ok=True)
    controls = []

    def constructor(name, late, change=None, accept=False):
        expected = (LATE if late else SCOPE / 'composed-supplier') / 'candidate'
        directory = fixtures / name
        directory.mkdir(exist_ok=True)
        data = read(expected / 'CONSTRUCTION.json')
        for tag in ('base', 'extra'):
            row = data['providers'][tag]
            word = directory / row['word']
            payload = gzip.decompress((expected / row['word']).read_bytes())
            # Deliberately different valid container for the exact original
            # canonical payload, exercising an actual transport difference.
            word.write_bytes(gzip.compress(payload, compresslevel=1, mtime=123456))
            need(sha(word) != sha(expected / row['word']), 'Container truly changed')
            row['word_sha256'] = sha(word)
            if late:
                key = (expected / row['word']).relative_to(REPO).as_posix()
                data['input_files'][key] = sha(word)
        if change is not None:
            change(data, directory, expected)
        receipt = directory / 'CONSTRUCTION.json'
        write(receipt, data)
        before = len(comparisons)
        try:
            for tag in ('base', 'extra'):
                name_word = data['providers'][tag]['word']
                namespace['compare_word'](directory / name_word, expected / name_word)
            namespace['compare_construction'](receipt, expected / 'CONSTRUCTION.json', late=late)
        except (ValueError, KeyError, TypeError):
            accepted = False
        else:
            accepted = True
        need(accepted == accept, (name, accepted, accept))
        record = dict(name=name, accepted=accepted, fixture_sha256=sha(receipt),
                      expected_sha256=sha(expected / 'CONSTRUCTION.json'))
        if accepted:
            record['comparison_records'] = comparisons[before:]
        controls.append(record)

    constructor('primary_container_only', False, accept=True)
    constructor('late_four_container_bindings_only', True, accept=True)
    constructor('unbound_generated_container', True,
                lambda d, p, e: d['providers']['base'].update(word_sha256='0' * 64))
    constructor('unbound_generated_source_entry', True,
                lambda d, p, e: d['input_files'].update({(e / d['providers']['base']['word']).relative_to(REPO).as_posix(): '0' * 64}))
    constructor('changed_canonical_payload_hash', True,
                lambda d, p, e: d['providers']['base'].update(canonical_sha256='0' * 64))
    constructor('changed_paid_profile', True,
                lambda d, p, e: d['local_profile'].update({'1': d['local_profile']['1'] + 1}))
    constructor('extra_nested_seconds_is_scientific', True,
                lambda d, p, e: d['providers']['base'].update(extra_check={'seconds': 7}))
    constructor('changed_original_source_pin', False,
                lambda d, p, e: d['source_pins'].update({next(iter(d['source_pins'])): '0' * 64}))

    def change_word(data, directory, expected):
        row = data['providers']['base']
        path_word = directory / row['word']
        word = read(path_word)
        word['B'][683][3] *= -1
        payload = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
        path_word.write_bytes(gzip.compress(payload, mtime=123456))
        row.update(word_sha256=sha(path_word), canonical_sha256=hashlib.sha256(payload).hexdigest())
        data['input_files'][(expected / row['word']).relative_to(REPO).as_posix()] = sha(path_word)
    constructor('changed_actual_receiver_sign', True, change_word)

    phase_expected = LATE / 'native-base/native/local/CLIFFORD-REVIEW.json'
    phase_original = read(phase_expected)
    def phase(name, change, accept=False):
        data = deepcopy(phase_original)
        change(data)
        receipt = fixtures / (name + '.json')
        write(receipt, data)
        try:
            namespace['compare_phase'](receipt, phase_expected)
        except (ValueError, KeyError, TypeError):
            accepted = False
        else:
            accepted = True
        need(accepted == accept, (name, accepted, accept))
        controls.append(dict(name=name, accepted=accepted, fixture_sha256=sha(receipt)))
    phase('phase_runtime_only', lambda d: d.update(seconds=d['seconds'] + 0.75), True)
    phase('phase_changed_word', lambda d: d.update(canonical_word_sha256='0' * 64))
    phase('phase_negative_runtime', lambda d: d.update(seconds=-1))
    phase('phase_nonfinite_runtime', lambda d: d.update(seconds=float('inf')))
    phase('phase_bool_runtime', lambda d: d.update(seconds=False))
    phase('phase_nested_seconds', lambda d: d.update(extra={'seconds': 1}))
    return controls


def portable_inputs():
    previous = REPO / 'research/kappa-1745-continuation'
    inventory = read(previous / 'MANIFEST.json')
    available = {}
    for base, field in ((previous, 'files'), (REPO, 'repository_dependencies')):
        for rel, record in inventory[field].items():
            available[(base / rel).relative_to(REPO).as_posix()] = record['sha256']
    extra = 'research/shared-phase-repair-rank/vendor/PR3220-PROOF.md'
    available[extra] = sha(REPO / extra)
    late_inventory = read(LATE / 'REPLAY-INPUTS.json')
    exclusions = {'release-work', '__pycache__', 'python-deps', 'replay-output', 'full-replay-output', 'native-replay-output'}
    outside, missing = [], []
    for rel, digest in late_inventory['input_files'].items():
        path = REPO / rel
        need(sha(path) == digest, 'Exact late replay input ' + rel)
        if path.is_relative_to(SCOPE):
            need(not any(x in exclusions for x in path.relative_to(SCOPE).parts), 'Required file excluded from current scope')
        else:
            outside.append(rel)
            if available.get(rel) != digest:
                missing.append(rel)
    need(not missing, 'Complete late portable dependency closure')
    return dict(catalogue_sha256=sha(LATE / 'REPLAY-INPUTS.json'), inputs=len(late_inventory['input_files']),
                external_inputs=len(outside), missing_or_mismatched=missing)


def main():
    for rel, digest in EXPECTED.items():
        need(sha(SCOPE / rel) == digest, 'Exact final reviewed selector ' + rel)
    primary = read(HERE / 'PRIMARY-REVIEW.json')
    for name in ('replay.py', 'freeze_manifest.py', 'package.py'):
        key = (SCOPE / name).relative_to(REPO).as_posix()
        need(sha(SCOPE / name) == primary['reviewed_files'][key], 'Frozen primary script remains unchanged')
    controls = comparator_controls()
    dependency = portable_inputs()
    files = [SCOPE / rel for rel in EXPECTED]
    files += [HERE / 'PRIMARY-REVIEW.json', LATE / 'REPLAY-INPUTS.json', LATE / 'RELEASE-STATIC-REVIEW.json', Path(__file__)]
    result = dict(status='PASS_SCOPED_INDEPENDENT_LATEST_SELECTION_REVIEW', acceptance_defects_found=False,
                  reviewed_files={p.relative_to(REPO).as_posix(): sha(p) for p in files},
                  default_stage_count=12, default_comparison_count=17,
                  comparator_controls=controls, late_dependency_coverage=dependency,
                  findings=[
                      'All manifest bytes are authenticated before scientific subprocesses. The12 default stages freshly reconstruct both words, reexecute both exact owner/operator invoices, and rerun both complete headline conjunctions. All17 comparisons retain scientific content.',
                      'Constructor transport normalization authenticates each actual container and its canonical payload. The primary path removes only two generated container hashes. The late path additionally removes their two exact canonical-path input bindings. Every other scalar, frame, source, proof, profile and status field must remain equal.',
                      'The isolated canonical clone copies only manifest-authenticated regular files, checks the copies, and rebuilds only its owned candidate/invoice/operator/claim paths. After complete payload and constructor proof equality, it restores the immutable native-bound containers. No native PASS receipt is regenerated or relabelled to manufacture hash agreement.',
                      'Optional native execution checks both providers, allfive ordered stages, the same exact word and compiler source map, and allsix native scientific outputs. Only the validated finite nonnegative top-level phase runtime is ignored; new nested fields and altered word bindings reject.',
                      'Optional full mode runs both native providers and the complete late source reconstruction/admission in a fresh cloned release-work/replayed-full directory. Its admission uses the original exact source-closed native receipts after fresh output equality, and VALIDATION explicitly describes this receipt mode. Fresh-native and fresh-full flags represent actual executed stages.',
                      'The new manifest requires completed evidence and conjunctive claims for both generations, and selects the late claim hash. The new package requires matching final manifest, late selected_supplier and exact late claim hash. Standalone claim and complete invoice files select the late paths. The prior archive preservation code is unchanged from the reviewed primary packager.',
                  ],
                  source_modified=False,
                  limitations=[
                      'This review executed only focused comparator controls and source/dependency authentication. The default12-stage portable replay, optional natives/full release and final archive packaging are separate root-owned executions.',
                      'Optional native output comparison remains deliberately strict about the native serialized files apart from phase runtime. Cross-runtime differences in native gzip streams or hashes can conservatively reject; the broader generated-container normalization is limited to the constructor paths.',
                      'Historical withdrawn claims remain authenticated history. The selected conditional improvement remains below.001745 and does not remove inherited all-size interfaces or assert formal kernel acceptance.',
                  ])
    write(HERE / 'LATEST-REVIEW.json', result)
    print(result['status'], len(controls), 'focused controls', dependency['inputs'], 'late inputs', flush=True)


if __name__ == '__main__':
    main()
