#!/usr/bin/env python3
"""Compact C07 source, complete-record, coverage and semantic gate controls.

Adapted from the reviewed C03 loader controls. All mutations use disposable
external directories or in-memory candidates after original authentication.
Substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types

STAGES = ('frame', 'counterexamples', 'independent')

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
        for label, changed in (('omitted', []), ('duplicated', names+names),
                               ('extra', names+['extra.json'])):
            reject(stage+'_'+label,
                   lambda stage=stage, changed=changed: v.check_coverage(stage, changed),
                   'complete stage record coverage changed: '+stage, rejected)
    require(counts == dict.fromkeys(STAGES, 1), 'three singleton complete records')

    class Tiny:
        def __init__(self, omit=False):
            self.compared, self.scripts, self.omit = [], [], omit
        def run(self, script, arguments):
            self.scripts.append(script)
            require(len(arguments) == 2 and arguments[0] == '--output',
                    'exact declared output argument')
            output = Path(arguments[1])
            require(output.is_relative_to(temporary), 'external dispatch scratch')
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
    scratch = temporary/'dispatch-omitted-comparison'
    scratch.mkdir()
    tiny = Tiny(True)
    v.replay(tiny, scratch, 'frame')
    action = lambda: v.check_coverage('frame', tiny.compared)
    gate = 'complete stage record coverage changed: frame'
    reject('omitted_actual_compare', action, gate, rejected)
    deletion(v, action, gate)
    return {'rejections': rejected, 'stage_counts': counts,
            'actual_dispatch_tested_with_tiny_receipts': True,
            'executed_check_deletions': 1}


def source_checks(v, package, temporary):
    frozen, rejected = v.Frozen(package), []
    frame = load_module(package/'frame/check.py', frozen.raw('frame/check.py'))
    counter = load_module(package/'counterexamples/check.py',
                          frozen.raw('counterexamples/check.py'))
    nested = b"def nested():\n    assert False, 'CAPTURED_NESTED_ASSERT'\nnested()\n"
    reject('frame_nested_assertion', lambda: frame.execute('fixture', nested),
           'CAPTURED_NESTED_ASSERT', rejected)
    reject('counter_nested_assertion', lambda: counter.module('fixture', nested),
           'CAPTURED_NESTED_ASSERT', rejected)
    positive = b'assert __debug__\nVALUE=713\n'
    require(frame.execute('positive', positive).VALUE == 713,
            'frame captured byte execution preserves assertions')
    require(counter.module('positive_counter', positive).VALUE == 713,
            'counter captured byte execution preserves assertions')
    for label, value in (('duplicate', 'x x'), ('missing', 'y')):
        reject(label+'_literal_adapter', lambda value=value: frame.replace_once(value, 'x', 'z'),
               'unique declared source adaptation', rejected)
    for label, value in (('duplicate', 'def f(): pass\ndef f(): pass\n'),
                         ('missing', 'def g(): pass\n')):
        reject(label+'_function_adapter',
               lambda value=value: frame.replace_function(value, 'f', 'def f(): return 1'),
               'unique adapted function f', rejected)
    source_dir = temporary/'frame inputs'
    source_dir.mkdir()
    manifest_raw = frozen.raw('frame/INPUTS.json')
    manifest = v.data(manifest_raw)
    manifest_path = source_dir/'INPUTS.json'
    manifest_path.write_bytes(manifest_raw)
    for entry in manifest.values():
        target = source_dir/entry['storage']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(frozen.raw('frame/'+entry['storage']))
    argv = sys.argv
    output = temporary/'never emitted frame receipt.json'
    def invoke():
        sys.argv = ['check.py', '--inputs', str(source_dir), '--output', str(output)]
        frame.main()
    try:
        manifest_path.write_bytes(manifest_raw+b' ')
        reject('changed_nested_manifest', invoke, 'authenticated input manifest', rejected)
        manifest_path.write_bytes(manifest_raw)
        name = 'clifford_exact.py'
        target = source_dir/manifest[name]['storage']
        original = target.read_bytes()
        target.write_bytes(original+b'\n')
        reject('changed_nested_compiler', invoke, 'authenticated transport '+name, rejected)
        target.write_bytes(original)
    finally:
        sys.argv = argv
    require(not output.exists(), 'source failure emitted no scientific receipt')
    return {'rejections': rejected, 'captured_bytes_compiled_optimize_zero': True,
            'no_path_import_or_pyc_execution': True,
            'full_scientific_stages_replayed': False}


def scientific_checks(v, package):
    frozen, rejected = v.Frozen(package), []
    independent = load_module(package/'independent/check.py',
                              frozen.raw('independent/check.py'))
    formal_controls = independent.controls()
    require(len(formal_controls) == 6 and all(row['same_guard_deletion_accepts']
                                            for row in formal_controls),
            'complete heterogeneous semantic controls')
    for row in formal_controls:
        rejected.append({'name': row['name'], 'intended_gate': row['guard']})
    counter = load_module(package/'counterexamples/check.py',
                          frozen.raw('counterexamples/check.py'))
    ce = counter.module('compact_c07_compiler',
                        frozen.raw('counterexamples/frozen/clifford_exact.py'))
    n = 4
    cp, past = ce.cgate(n, 1), ce.cgate(n, 4)
    dx = past.then(cp)
    swap = ce.perm(n, [1, 2, 8, 4])
    actual_dressed = dx.then(swap).then(dx.adjoint())
    pull = lambda logical: dx.adjoint().then(logical).then(dx)
    counter.accept_equal(counter.matrix(pull(actual_dressed)), counter.matrix(swap),
                         'fresh X exact pullback')
    bad_phase = actual_dressed.then(ce.Op(n, ce.identity(n), [('phase', 1)]))
    candidates = [
        ('phase changes actual dressed pullback',
         lambda: counter.accept_equal(counter.matrix(pull(bad_phase)),
                                      counter.matrix(swap), 'fresh X exact pullback'),
         'fresh X exact pullback'),
        ('undressed physical pullback is not monomial',
         lambda: counter.accept_monomial(counter.matrix(pull(swap)),
                                         'simultaneous X monomial admission'),
         'simultaneous X monomial admission'),
    ]
    op = ce.perm(2, [2, 3])
    a = counter.transpose_columns(counter.matrix(op), 4)
    b = counter.transpose_columns(counter.matrix(op.adjoint()), 4)
    wrong = counter.transpose_columns(counter.matrix(op.then(op)), 4)
    right = counter.transpose_columns(counter.matrix(op.then(op).adjoint()), 4)
    counter.accept_endpoint(counter.decode(a, b, right), 4)
    candidates.append(('generic normalization requires inverse square',
                       lambda: counter.accept_endpoint(counter.decode(a, b, wrong), 4),
                       'all arbitrary two-field decoder columns'))
    for name, action, gate in candidates:
        result = counter.reject(name, action, gate)
        require(result['same_guard_deleted'] == 'ACCEPTED', 'actual counterexample guard deletion')
        rejected.append({'name': name, 'intended_gate': gate,
                         'discrepancy': result['discrepancy']})
    return {'rejections': rejected, 'executed_check_deletions': 9,
            'mutated_mathematics_after_authentication': True,
            'deletion_scope': 'same production acceptance predicate',
            'full_scientific_stages_replayed': False}


def output_checks(v, package, temporary):
    rejected, argv = [], sys.argv
    existing = temporary/'existing output.json'
    existing.write_text('preserved')
    def invoke(output):
        sys.argv = ['verify.py', '--stage', 'frame', '--output', str(output)]
        v.main()
    try:
        reject('relative_output', lambda: invoke(Path('relative.json')),
               'output must be absolute', rejected)
        reject('existing_output', lambda: invoke(existing), 'output already exists', rejected)
        reject('internal_output', lambda: invoke(package/'forbidden.json'),
               'output must be external', rejected)
        original_replay = v.replay
        race_output = temporary/'racing output.json'
        def racing_replay(frozen, scratch, stage):
            frozen.compared.extend(sorted(v.expected_records(stage)))
            race_output.write_text('race winner preserved')
        v.replay = racing_replay
        try:
            try:
                invoke(race_output)
            except FileExistsError:
                require(race_output.read_text() == 'race winner preserved',
                        'exclusive creation preserves racing output')
                rejected.append({'name': 'output created during replay',
                                 'intended_gate': 'exclusive output creation FileExistsError'})
            else:
                raise ValueError('racing output overwritten')
        finally:
            v.replay = original_replay
    finally:
        sys.argv = argv
    require(existing.read_text() == 'preserved', 'existing output retained')
    return {'rejections': rejected, 'early_output_guards': True,
            'exclusive_output_creation_exercised': True}


def child(package):
    v = load_module(package/'verify.py')
    v.Frozen(package).check_all()
    with tempfile.TemporaryDirectory(prefix='C07 compact controls ') as directory:
        temporary = Path(directory)
        result = {'loader': loader_checks(v, temporary), 'record_gate': record_checks(v, temporary),
                  'compression': compression_checks(v, temporary),
                  'coverage': coverage_checks(v, temporary),
                  'sources': source_checks(v, package, temporary),
                  'scientific': scientific_checks(v, package),
                  'output': output_checks(v, package, temporary),
                  'real_records': real_records(v, package)}
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
    names = ['verify.py', 'FROZEN-SHA256.json', 'ORIGINS.json',
             'frame/check.py', 'counterexamples/check.py', 'independent/check.py']
    before = {name: sha((package/name).read_bytes()) for name in names}
    results = []
    for optimized in (False, True):
        command = [sys.executable, '-I', '-B']+(['-O'] if optimized else [])
        command += [str(Path(__file__).resolve()), '--package', str(package), '--child']
        completed = subprocess.run(command, capture_output=True, text=True)
        require(completed.returncode == 0, completed.stdout+completed.stderr)
        results.append(json.loads(completed.stdout))
    require(before == {name: sha((package/name).read_bytes()) for name in names},
            'reviewed source changed during controls')
    comparable = [{k: value for k, value in row.items() if k != 'parent_optimization'}
                  for row in results]
    require(comparable[0] == comparable[1], 'normal and optimized controls differ')
    count = sum(len(row.get('rejections', [])) for row in results[0].values()
                if isinstance(row, dict))
    count += sum(len(row['rejections']) for row in results[0]['real_records'])
    deletions = 1+sum(row.get('executed_check_deletions', 0)
                      for row in results[0].values() if isinstance(row, dict))
    result = {'status': 'PASS_C07_COMPACT_SOURCE_RECORD_AND_SEMANTIC_CONTROLS',
              'source_hashes': before, 'control_source_sha256': sha(Path(__file__).read_bytes()),
              'runs': results, 'normal_and_optimized_receipts_equal_except_mode': True,
              'intended_rejections_per_mode': count,
              'executed_check_deletions_per_mode': deletions,
              'full_scientific_receipts_compared': 3,
              'full_scientific_stages_replayed': False, 'no_new_kappa': True}
    if args.output:
        with args.output.open('x') as destination:
            destination.write(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('status', 'intended_rejections_per_mode',
                      'executed_check_deletions_per_mode', 'full_scientific_receipts_compared')}, sort_keys=True))


if __name__ == '__main__':
    main()
