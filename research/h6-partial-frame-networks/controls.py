#!/usr/bin/env python3
"""Compact C03 source, record, shared-geometry and semantic gate controls.

Adapted from the independently reviewed C02 source controls. All mutated
files use fresh system temporary directories. No full science stage runs.
Substantial OpenAI Codex assistance; Apache-2.0.
"""


import argparse
import ast
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def load_module(path, raw=None, name="reviewed_controls_module"):
    source = path.read_bytes() if raw is None else raw
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module

def reject(label, action, expected, records, exact=True):
    try:
        action()
    except (ValueError, AssertionError) as error:
        message = str(error)
        require(message == expected if exact else expected in message,
                "wrong rejection for " + label + ": " + message)
        records.append({"name": label, "intended_gate": expected})
    else:
        raise ValueError("control accepted: " + label)

def fixture(root, files, originals=None):
    root.mkdir(parents=True)
    hashes, origins = {}, {}
    for name, raw in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        hashes[name] = sha(raw)
        origins[name] = {"sha256": sha(raw)}
        if originals and name in originals:
            origins[name]["original_sha256"] = sha(originals[name])
    (root / "FROZEN-SHA256.json").write_text(json.dumps(hashes))
    (root / "ORIGINS.json").write_text(json.dumps(origins))
    return root

def loader_checks(v, temporary):
    positive = (
        b"import json, sys\nfrom pathlib import Path\n"
        b"assert __debug__ and sys.flags.optimize == 0, 'CHILD_OPTIMIZATION'\n"
        b"assert __file__ == sys.argv[0], 'SCRIPT_FILE_ARGUMENT'\n"
        b"Path(sys.argv[-1]).write_text(json.dumps(sys.argv[1:-1]))\n"
    )
    files = {
        "script with spaces.py": positive,
        "direct.py": b"assert False, 'DIRECT_ASSERT'\n",
        "nested.py": b"def inner():\n    assert False, 'NESTED_ASSERT'\ninner()\n",
        "notfinite.json": b'{"a":NaN}',
    }
    root = fixture(temporary / "loader", files)
    frozen, rejected = v.Frozen(root), []
    frozen.check_all()
    output = temporary / "literal argument result.json"
    frozen.run("script with spaces.py", ["argument with spaces", output])
    require(json.loads(output.read_text()) == ["argument with spaces"], "preserved script arguments")
    for name, marker in (("direct.py", "DIRECT_ASSERT"), ("nested.py", "NESTED_ASSERT")):
        reject(name, lambda name=name: frozen.run(name, []),
               "AssertionError: " + marker, rejected, exact=False)
    # This disposable source is changed only after Frozen.raw has returned.
    # The script passed to the interpreter must remain the captured old bytes.
    original_path, calls = frozen.path, {"count": 0}
    def changed_path(name):
        path = original_path(name)
        calls["count"] += 1
        if calls["count"] == 2:
            path.write_bytes(b"raise RuntimeError('REOPENED_CHANGED_SOURCE')\n")
        return path
    frozen.path = changed_path
    try:
        frozen.run("script with spaces.py", ["captured bytes", output])
        require(calls["count"] == 2 and json.loads(output.read_text()) == ["captured bytes"],
                "captured authenticated source execution")
    finally:
        frozen.path = original_path
        (root / "script with spaces.py").write_bytes(positive)
    (root / "direct.py").write_bytes(b"PASS = True\n")
    reject("changed_executable_source", lambda: frozen.run("direct.py", []),
           "changed frozen input: direct.py", rejected)
    (root / "direct.py").unlink()
    reject("missing_executable_source", lambda: frozen.run("direct.py", []),
           "missing regular input: direct.py", rejected)
    reject("unregistered_source", lambda: frozen.run("absent.py", []),
           "unregistered input: absent.py", rejected)
    reject("absolute_path", lambda: frozen.path("/etc/passwd"), "unsafe package path", rejected)
    reject("parent_escape", lambda: frozen.path("../outside"), "unsafe package path", rejected)
    (root / "link.py").symlink_to(root / "nested.py")
    reject("symlink_input", lambda: frozen.path("link.py"),
           "missing regular input: link.py", rejected)
    outside = temporary / "external"
    outside.mkdir()
    (outside / "data.json").write_text("{}")
    (root / "outside").symlink_to(outside, target_is_directory=True)
    reject("ancestor_symlink_escape", lambda: frozen.path("outside/data.json"),
           "input escapes package", rejected)
    reject("direct_runtime_requirement", lambda: v.require(False, "DIRECT_RUNTIME_GATE"),
           "DIRECT_RUNTIME_GATE", rejected)
    return {"rejections": rejected, "captured_source_survives_disposable_path_change": True,
            "child_assertions_enabled": True, "file_and_argument_semantics_preserved": True}

def record_checks(v, temporary):
    value = {"integer": 1, "boolean": True, "nested": {"ordered": [1, 2, 3]}}
    raw = json.dumps(value).encode()
    root = fixture(temporary / "record", {"expected.json": raw})
    frozen, rejected = v.Frozen(root), []
    frozen.compare("expected.json", raw)
    mutations = {
        "boolean_for_integer": dict(value, integer=True),
        "float_for_integer": dict(value, integer=1.0),
        "integer_for_boolean": dict(value, boolean=1),
        "nested_omission": dict(value, nested={}),
        "ordered_list_reorder": dict(value, nested={"ordered": [1, 3, 2]}),
        "ordered_list_truncate": dict(value, nested={"ordered": [1, 2]}),
    }
    for label, changed in mutations.items():
        reject(label, lambda changed=changed: frozen.compare("expected.json", json.dumps(changed).encode()),
               "complete typed record mismatch: expected.json", rejected)
    reject("duplicate_json_key", lambda: v.data(b'{"a":1,"a":2}'),
           "duplicate JSON key: a", rejected)
    reject("nested_duplicate_json_key", lambda: v.data(b'{"n":{"a":1,"a":2}}'),
           "duplicate JSON key: a", rejected)
    for value_ in ("NaN", "Infinity", "-Infinity"):
        reject("nonfinite_" + value_, lambda value_=value_: v.data(value_.encode()),
               "nonfinite JSON constant: " + value_, rejected)
    (root / "expected.json").unlink()
    reject("missing_expected_record", lambda: frozen.compare("expected.json", raw),
           "missing regular input: expected.json", rejected)
    require(not (root / "expected.json").exists(), "missing expected record regenerated")
    (root / "expected.json").write_bytes(raw)
    saved = v.require
    try:
        v.require = lambda ok, message: None if message.startswith("complete typed record mismatch:") else saved(ok, message)
        try:
            reject("deleted_record_gate",
                   lambda: frozen.compare("expected.json", json.dumps(mutations["boolean_for_integer"]).encode()),
                   "complete typed record mismatch: expected.json", [])
        except ValueError as error:
            require(str(error) == "control accepted: deleted_record_gate", "record check-deletion sensitivity")
        else:
            raise ValueError("record check deletion not detected")
    finally:
        v.require = saved
    return {"rejections": rejected, "named_record_gate_deletion_detected": True}

def compression_checks(v, temporary):
    name, plain = "original.json.gz", b'{"original":[1,2,3]}\n'
    root = fixture(temporary / "compression", {name: gzip.compress(plain, mtime=0)}, {name: plain})
    frozen, rejected = v.Frozen(root), []
    frozen.check_all()
    changed = gzip.compress(b'{"original":[1,2,4]}\n', mtime=0)
    (root / name).write_bytes(changed)
    reject("changed_compressed_input", frozen.check_all,
           "changed frozen input: " + name, rejected)
    frozen.hashes[name] = sha(changed)
    reject("changed_container_origin", frozen.check_all,
           "origin digest mismatch: " + name, rejected)
    frozen.origins[name]["sha256"] = sha(changed)
    reject("changed_original_after_transport_rebinding", frozen.check_all,
           "original decoded bytes changed: " + name, rejected)
    same = gzip.compress(plain, mtime=17)
    (root / name).write_bytes(same)
    frozen.hashes[name] = frozen.origins[name]["sha256"] = sha(same)
    frozen.check_all()
    saved = frozen.origins
    frozen.origins = {}
    reject("omitted_origin", frozen.check_all, "frozen/origin inventory mismatch", rejected)
    frozen.origins = saved
    return {"rejections": rejected, "equivalent_recompression_accepted": True}


STAGES = ('cyclic', 'pauli', 'independent')


def deletion(v, action, gate):
    saved = v.require
    try:
        v.require = lambda ok, message: None if message == gate else saved(ok, message)
        try:
            reject('deleted_'+gate, action, gate, [])
        except ValueError as error:
            require(str(error) == 'control accepted: deleted_'+gate, 'intended check deletion')
        else:
            raise ValueError('deleted gate still rejected: '+gate)
    finally:
        v.require = saved


def real_records(v, package):
    frozen, records = v.Frozen(package), []
    names = sorted(set().union(*(v.expected_records(stage) for stage in STAGES)))
    def leaves(value, path=()):
        if isinstance(value, dict):
            for key in sorted(value):
                yield from leaves(value[key], path+(key,))
        elif isinstance(value, list):
            for i, child in enumerate(value):
                yield from leaves(child, path+(i,))
        else:
            yield path, value
    for name in names:
        raw = frozen.raw(name)
        value = v.data(raw)
        frozen.compare(name, json.dumps(value).encode())
        path, old = max(leaves(value), key=lambda item: len(item[0]))
        require(len(path) > 1, 'real nested record coverage')
        changed, omitted = copy.deepcopy(value), copy.deepcopy(value)
        parent, other = changed, omitted
        for key in path[:-1]:
            parent, other = parent[key], other[key]
        parent[path[-1]] = not old if type(old) is bool else old+1 if type(old) is int else {'changed': True}
        del other[path[-1]]
        rejected = []
        for label, candidate in (('deep_field_changed', changed), ('deep_field_omitted', omitted)):
            reject(label, lambda candidate=candidate: frozen.compare(name, json.dumps(candidate).encode()),
                   'complete typed record mismatch: '+name, rejected)
        records.append({'record': name, 'sha256': sha(raw), 'nested_path': list(path), 'rejections': rejected})
    require(len(records) == 3, 'three complete scientific records')
    return records


def coverage_checks(v, temporary):
    require(set(v.STAGES) == set(STAGES), 'exact three science stages')
    rejected, counts = [], {}
    for stage in STAGES:
        names = sorted(v.expected_records(stage))
        v.check_coverage(stage, names)
        counts[stage] = len(names)
        for label, changed in (('omitted', []), ('duplicated', names+names), ('extra', names+['extra.json'])):
            reject(stage+'_'+label, lambda stage=stage, changed=changed: v.check_coverage(stage, changed),
                   'complete stage record coverage changed: '+stage, rejected)
    require(counts == dict.fromkeys(STAGES, 1), 'three singleton complete records')

    class Tiny:
        def __init__(self, omit=False):
            self.root, self.compared, self.scripts, self.omit = temporary, [], [], omit
        def raw(self, name):
            require(name in ('cyclic/CHECKS.json.gz', 'pauli/CHECKS.json.gz'), 'only declared dependent records read')
            return gzip.compress(b'{}', mtime=0)
        def path(self, name):
            return self.root/name
        def run(self, script, arguments):
            self.scripts.append(script)
            require(arguments.count('--output') == 1, 'one external output argument')
            output = Path(arguments[arguments.index('--output')+1])
            require(output.is_relative_to(temporary), 'dispatch external scratch')
            if script.startswith('independent/'):
                require(Path(arguments[arguments.index('--source-dir')+1]) == self.root/'cyclic/frozen',
                        'independent historical source argument')
                for label, name in (('cyclic', 'cyclic/CHECKS.json.gz'), ('pauli', 'pauli/CHECKS.json.gz')):
                    require(Path(arguments[arguments.index('--'+label+'-receipt')+1]) == self.root/name,
                            'independent full receipt argument')
                    require(arguments[arguments.index('--'+label+'-sha256')+1] == sha(self.raw(name)),
                            'independent receipt digest comes from authenticated bytes')
            else:
                require(arguments == ['--output', output], 'direct production checker arguments')
            output.write_text('{}')
        def compare(self, name, raw):
            require(raw == b'{}', 'generated fixture reaches complete comparison')
            if not self.omit:
                self.compared.append(name)

    for stage in STAGES:
        scratch = temporary/('dispatch-'+stage)
        scratch.mkdir()
        tiny = Tiny()
        v.replay(tiny, scratch, stage)
        v.check_coverage(stage, tiny.compared)
        require(tiny.scripts == [v.STAGES[stage][0]], 'one declared checker selected')
    scratch = temporary/'dispatch-omitted-compare'
    scratch.mkdir()
    tiny = Tiny(True)
    v.replay(tiny, scratch, 'pauli')
    action = lambda: v.check_coverage('pauli', tiny.compared)
    gate = 'complete stage record coverage changed: pauli'
    reject('omitted_actual_compare', action, gate, rejected)
    deletion(v, action, gate)
    return {'rejections': rejected, 'stage_counts': counts, 'real_dispatch_covered_with_tiny_receipts': True,
            'executed_check_deletions': 1}


def contract_checks(v, package):
    frozen = v.Frozen(package)
    original = {name: v.data(frozen.raw(name)) for name in ('cyclic/CHECKS.json.gz', 'pauli/CHECKS.json.gz')}
    baseline = v.check_contracts(frozen)
    class Candidate:
        def __init__(self, values):
            self.values = values
        def raw(self, name):
            return json.dumps(self.values[name]).encode()
    rejected = []
    definitions = [('frame_array_changed', 'complete tiling frame arrays differ'),
                   ('frame_scalar_type_changed', 'complete tiling frame arrays differ'),
                   ('frame_order_changed', 'complete tiling frame arrays differ'),
                   ('frame_count_both_truncated', 'complete tiling frame count'),
                   ('declared_digest_changed', 'complete tiling frame digest mismatch')]
    definitions += [('shared_'+key, 'complete shared geometry differs: '+key) for key in (
        'canonical_roots', 'a_triples', 'b_orthogonal_involution_pairs', 'triple_gauge_signs')]
    key_map = {'canonical_roots': 'canonical_roots', 'a_triples': 'tiling_a_triples',
               'b_orthogonal_involution_pairs': 'tiling_b_pairs', 'triple_gauge_signs': 'tiling_gauge_signs'}
    for name, gate in definitions:
        changed = copy.deepcopy(original)
        left = changed['cyclic/CHECKS.json.gz']['complete_tiling']['frame_cases']
        p = changed['pauli/CHECKS.json.gz']
        right = p['tiling_frame_cases']
        if name == 'frame_array_changed':
            right[0]['labels'][0] ^= 1
        elif name == 'frame_scalar_type_changed':
            right[0]['labels'][0] = True
        elif name == 'frame_order_changed':
            right[0], right[1] = right[1], right[0]
        elif name == 'frame_count_both_truncated':
            left.pop(); right.pop()
            p['tiling_frame_cases_sha256'] = sha(v.canonical(left).encode())
        elif name == 'declared_digest_changed':
            p['tiling_frame_cases_sha256'] = '0'*64
        else:
            p[key_map[name.removeprefix('shared_')]][0][0] += 1
        action = lambda changed=changed: v.check_contracts(Candidate(changed))
        reject(name, action, gate, rejected)
        deletion(v, action, gate)
    return {'rejections': rejected, 'authenticated_original_contract': baseline,
            'mutations_after_authentication': True, 'executed_check_deletions': len(definitions)}


def scientific_gates(v, package, temporary):
    from fractions import Fraction
    frozen, rejected = v.Frozen(package), []
    cyclic = load_module(package/'cyclic/check.py', frozen.raw('cyclic/check.py'))
    modules, _, _ = cyclic.authenticated_modules(package/'cyclic/frozen', package/'cyclic/ORIGINS.json', temporary)
    m = modules['mixed_rectangle.py']
    receipt = v.data(frozen.raw('cyclic/CHECKS.json.gz'))
    fix = receipt['reports']['DYNAMIC-CYCLIC-RESULT.json']['cases'][1]['fixture']
    # The source fixture serializes tuple frames to lists. Restore that declared representation only.
    fix = copy.deepcopy(fix)
    fix['starts'] = {k: tuple(x) for k, x in fix['starts'].items()}
    fix['ends'] = {k: tuple(x) for k, x in fix['ends'].items()}
    m.replay(fix)
    gate = 'all-column exact identity with arbitrary dirt'
    action = lambda: m.replay(fix, False, 'comp_restore')
    reject('cyclic_actual_dirty_helper_cleanup', action, gate, rejected)
    cyclic.deletion_control(m, action, gate)
    gate = 'equal current frames'
    action = lambda: m.replay(fix, False, 'source_read_arc')
    reject('cyclic_actual_source_frame', action, gate, rejected)
    cyclic.deletion_control(m, action, gate)
    paid = copy.deepcopy(fix)
    first = next(e for e in paid['events'] if e['op'] == 'add')
    paid['events'][:0] = [dict(first, q='1'), dict(first, q='-1')]
    result = m.replay(paid)
    require(cyclic.operator_difference(result, False) is None, 'actual paid pair preserves cyclic operator')
    gate = 'complete scalar invoice'
    action = lambda: cyclic.accept_bill(result, 'dynamic', 3, False)
    reject('cyclic_actual_paid_cancelling_pair', action, gate, rejected)
    deletion(cyclic, action, gate)

    pauli = load_module(package/'pauli/check.py', frozen.raw('pauli/check.py'))
    pauli.m = pauli.load_geometry(frozen.raw('pauli/geometry.py'))
    case = v.data(frozen.raw('pauli/CHECKS.json.gz'))['cases'][1]
    pfix = copy.deepcopy(case['fixture'])
    pfix['starts'] = {k: tuple(x) for k, x in pfix['starts'].items()}
    pfix['ends'] = {k: tuple(x) for k, x in pfix['ends'].items()}
    pfix['K'] = [[Fraction(x) for x in row] for row in pfix['K']]
    pauli.replay(pfix)
    for tag, gate in (('cleanup', 'all arbitrary input and dirty centre columns'),
                      ('target_W', 'literal equal common frame')):
        action = lambda tag=tag: pauli.replay(pfix, False, tag)
        reject('pauli_actual_'+tag, action, gate, rejected)
        outcome = pauli.rejection('compact_'+tag, action, gate)
        require(outcome['named_guard_deletion'] == 'ACCEPTED', 'actual Pauli gate deletion')
    return {'rejections': rejected, 'executed_check_deletions': 5,
            'ordinary_corruption_tests_after_source_authentication': True,
            'one_r3_and_one_radical_diagnostic_only': True, 'full_science_stages_replayed': False}


def source_checks(v, package, temporary):
    frozen, rejected = v.Frozen(package), []
    cyclic = load_module(package/'cyclic/check.py', frozen.raw('cyclic/check.py'))
    pauli = load_module(package/'pauli/check.py', frozen.raw('pauli/check.py'))
    reject('nested_geometry_assertion', lambda: pauli.load_geometry(
        b"def nested():\n    assert False, 'GEOMETRY_NESTED_ASSERT'\nnested()\n"),
        'GEOMETRY_NESTED_ASSERT', rejected)
    require(pauli.load_geometry(b'assert __debug__\nCAPTURED=713\n').CAPTURED == 713,
            'explicit geometry captured bytes execute with assertions')
    source_dir = temporary/'cyclic sources'
    source_dir.mkdir()
    manifest_raw = frozen.raw('cyclic/ORIGINS.json')
    manifest = json.loads(manifest_raw)
    manifest_path = temporary/'cyclic origins.json'
    manifest_path.write_bytes(manifest_raw)
    for row in manifest['files']:
        name = row.get('transport_path', row['path'])
        (source_dir/name).write_bytes(frozen.raw('cyclic/frozen/'+name))
    call = lambda: cyclic.authenticated_modules(source_dir, manifest_path, temporary)
    manifest_path.write_bytes(manifest_raw+b' ')
    reject('changed_nested_manifest', call, 'source manifest SHA256', rejected)
    manifest_path.write_bytes(manifest_raw)
    invoice = source_dir/'invoice.py'
    invoice_raw = invoice.read_bytes()
    invoice.write_bytes(invoice_raw+b"\ndef nested_control():\n    assert False, 'RETAINED_NESTED_ASSERT'\nnested_control()\n")
    reject('changed_retained_executable', call, 'authenticated source bytes: invoice.py', rejected)
    for row in manifest['files']:
        if row['path'] == 'invoice.py':
            row['bytes'], row['sha256'] = len(invoice.read_bytes()), sha(invoice.read_bytes())
    rebound = json.dumps(manifest).encode()
    manifest_path.write_bytes(rebound)
    old_pin = cyclic.ORIGINS_SHA
    cyclic.ORIGINS_SHA = sha(rebound)
    try:
        reject('retained_nested_assertion_with_disposable_pin', call, 'RETAINED_NESTED_ASSERT', rejected)
    finally:
        cyclic.ORIGINS_SHA = old_pin
        invoice.write_bytes(invoice_raw)
        manifest_path.write_bytes(manifest_raw)
    # The actual production loader has captured every input before its first
    # ModuleType creation. Mutate a disposable source at that exact cut.
    original_type = cyclic.types.ModuleType
    created = []
    def mutate_after_capture(name):
        if not created:
            invoice.write_bytes(b"raise RuntimeError('PATH_REOPENED_AFTER_AUTHENTICATION')\n")
        created.append(name)
        return original_type(name)
    cyclic.types.ModuleType = mutate_after_capture
    try:
        modules, captured, adaptations = call()
        require(captured['invoice.py'] == invoice_raw and len(modules) == 6,
                'retained loader executes captured original bytes')
    finally:
        cyclic.types.ModuleType = original_type
        invoice.write_bytes(invoice_raw)
    reject('duplicate_literal_adapter_match', lambda: cyclic.replace_once('x x', 'x', 'y'),
           'unique source adaptation', rejected)

    pauli_dir = temporary/'pauli inputs'
    for name in pauli.PINS:
        target = pauli_dir/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(frozen.raw('pauli/'+name))
    output = temporary/'no Pauli result.json'
    argv, pins = sys.argv, pauli.PINS.copy()
    def invoke():
        sys.argv = ['check.py', '--inputs', str(pauli_dir), '--output', str(output)]
        pauli.main()
    target = pauli_dir/'frozen/module_tiling.py'
    original = target.read_bytes()
    try:
        target.write_bytes(original+b'\nTRIPLES = []\n')
        reject('changed_selected_literal_source', invoke, 'authenticated source bytes', rejected)
        pauli.PINS['frozen/module_tiling.py'] = sha(target.read_bytes())
        reject('duplicate_selected_TRIPLES', invoke, 'unique frozen TRIPLES assignment', rejected)
        tree = ast.parse(original)
        assign = next(n for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(x, ast.Name) and x.id == 'TRIPLES' for x in n.targets))
        lines = original.decode().splitlines(keepends=True)
        target.write_text(''.join(lines[:assign.lineno-1]+lines[assign.end_lineno:]))
        pauli.PINS['frozen/module_tiling.py'] = sha(target.read_bytes())
        reject('missing_selected_TRIPLES', invoke, 'unique frozen TRIPLES assignment', rejected)
    finally:
        sys.argv, pauli.PINS = argv, pins
    require(not output.exists(), 'failed source control emitted no scientific receipt')
    return {'rejections': rejected, 'retained_module_count': len(modules),
            'retained_compile_optimization': [x['optimize'] for x in adaptations],
            'actual_captured_loader_survives_disposable_source_change': True,
            'no_path_import_or_pyc_execution_used': True, 'full_science_stages_replayed': False}


def output_checks(v, package, temporary):
    rejected, argv = [], sys.argv
    existing = temporary/'existing result'
    existing.write_text('preserved')
    def invoke(output):
        sys.argv = ['verify.py', '--stage', 'cyclic', '--output', str(output)]
        v.main()
    try:
        reject('relative_wrapper_output', lambda: invoke(Path('relative-output.json')),
               'output must be absolute', rejected)
        reject('existing_wrapper_output', lambda: invoke(existing), 'output already exists', rejected)
        reject('internal_wrapper_output', lambda: invoke(package/'forbidden-output.json'),
               'output must be external', rejected)
    finally:
        sys.argv = argv
    require(existing.read_text() == 'preserved', 'existing output retained')
    return {'rejections': rejected, 'guards_precede_scientific_replay': True}


def child(package):
    v = load_module(package/'verify.py')
    v.Frozen(package).check_all()
    with tempfile.TemporaryDirectory(prefix='C03 compact controls ') as directory:
        temporary = Path(directory)
        result = {'loader': loader_checks(v, temporary), 'record_gate': record_checks(v, temporary),
                  'compression': compression_checks(v, temporary), 'coverage': coverage_checks(v, temporary),
                  'contracts': contract_checks(v, package), 'scientific_gates': scientific_gates(v, package, temporary),
                  'nested_sources': source_checks(v, package, temporary),
                  'output': output_checks(v, package, temporary), 'real_records': real_records(v, package)}
    v.Frozen(package).check_all()
    return {'parent_optimization': sys.flags.optimize, **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--child', action='store_true')
    args = parser.parse_args()
    package = args.package.resolve()
    if args.output:
        require(args.output.is_absolute(), 'control output must be absolute')
        require(not args.output.exists(), 'control output already exists')
        require(not args.output.resolve().is_relative_to(package), 'control output must be external')
    if args.child:
        print(json.dumps(child(package), sort_keys=True))
        return
    names = ['verify.py', 'FROZEN-SHA256.json', 'ORIGINS.json', 'cyclic/check.py', 'pauli/check.py',
             'pauli/geometry.py', 'independent/independent_operator.py']
    before = {name: sha((package/name).read_bytes()) for name in names}
    results = []
    for optimized in (False, True):
        command = [sys.executable, '-I', '-B']+(['-O'] if optimized else [])
        command += [str(Path(__file__).resolve()), '--package', str(package), '--child']
        completed = subprocess.run(command, capture_output=True, text=True)
        require(completed.returncode == 0, completed.stdout+completed.stderr)
        results.append(json.loads(completed.stdout))
    require(before == {name: sha((package/name).read_bytes()) for name in names}, 'reviewed source changed during controls')
    comparable = [{k: value for k, value in result.items() if k != 'parent_optimization'} for result in results]
    require(comparable[0] == comparable[1], 'normal and optimized controls differ')
    count = sum(len(s.get('rejections', [])) for s in results[0].values() if isinstance(s, dict))
    count += sum(len(s['rejections']) for s in results[0]['real_records'])
    deletions = 1+sum(s.get('executed_check_deletions', 0) for s in results[0].values() if isinstance(s, dict))
    result = {'status': 'PASS_C03_COMPACT_SOURCE_RECORD_AND_SEMANTIC_CONTROLS',
              'source_hashes': before, 'control_source_sha256': sha(Path(__file__).read_bytes()),
              'runs': results, 'normal_and_optimized_receipts_equal_except_mode': True,
              'intended_rejections_per_mode': count, 'executed_check_deletions_per_mode': deletions,
              'full_scientific_receipts_compared': 3, 'full_scientific_stages_replayed': False, 'no_new_kappa': True}
    if args.output:
        with args.output.open('x') as handle:
            handle.write(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'intended_rejections_per_mode',
                      'executed_check_deletions_per_mode', 'full_scientific_receipts_compared')}, sort_keys=True))


if __name__ == '__main__':
    main()
