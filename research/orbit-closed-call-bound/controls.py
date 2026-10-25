#!/usr/bin/env python3
"""Compact source, complete-record and real semantic controls for C09 orbit calls.

Adapted from the reviewed C07 wrapper controls. All mutations are disposable.
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

STAGES = ('orbit', 'independent')

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
    require(len(records) == 2, 'two complete scientific records')
    return records

def coverage_checks(v, temporary):
    require(set(v.STAGES) == set(STAGES), 'exact two science stages')
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
    require(counts == dict.fromkeys(STAGES, 1), 'two singleton complete records')

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
    v.replay(tiny, scratch, 'orbit')
    action = lambda: v.check_coverage('orbit', tiny.compared)
    gate = 'complete stage record coverage changed: orbit'
    reject('omitted_actual_compare', action, gate, rejected)
    deletion(v, action, gate)
    return {'rejections': rejected, 'stage_counts': counts,
            'actual_dispatch_tested_with_tiny_receipts': True,
            'executed_check_deletions': 1}

def output_checks(v, package, temporary):
    rejected, argv = [], sys.argv
    existing = temporary/'existing output.json'
    existing.write_text('preserved')
    def invoke(output):
        sys.argv = ['verify.py', '--stage', 'orbit', '--output', str(output)]
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
    with tempfile.TemporaryDirectory(prefix='C09 orbit compact controls ') as directory:
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


def source_checks(v, package, temporary):
    frozen, rejected = v.Frozen(package), []
    orbit = load_module(package/'orbit/check.py', frozen.raw('orbit/check.py'))
    blobs = {name: frozen.raw('orbit/'+name) for name in orbit.PINS}
    original = blobs['frozen/history/geometry_derivative.py']
    changed = dict(blobs)
    changed['frozen/history/geometry_derivative.py'] = original+b"\ndef nested_assertion():\n    assert False, 'HISTORICAL_NESTED_ASSERT'\nnested_assertion()\n"
    reject('captured_historical_nested_assertion', lambda: orbit.captured_history(changed),
           'HISTORICAL_NESTED_ASSERT', rejected)
    literal = "SOURCE = Path('/Users/ross/git/math/integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz')"
    for label, value in (('duplicate', original+b'\n'+literal.encode()+b'\n'),
                         ('missing', original.replace(literal.encode(), b'# removed SOURCE literal'))):
        candidate = dict(blobs)
        candidate['frozen/history/geometry_derivative.py'] = value
        reject(label+'_historical_adapter',
               lambda candidate=candidate: orbit.captured_history(candidate),
               'unique historical adaptation', rejected)
    candidate = dict(blobs)
    candidate['frozen/history/geometry_derivative.py'] = original+b'\nEXTRA_READ = SOURCE.read_bytes()\n'
    reject('undeclared_additional_source_read', lambda: orbit.captured_history(candidate),
           'captured root read count', rejected)
    source_dir = temporary/'orbit sources'
    for name, value in blobs.items():
        target = source_dir/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value)
    (source_dir/'INPUTS.json').write_bytes(frozen.raw('orbit/INPUTS.json'))
    source_name = 'frozen/source/bitE8-r865.json.gz'
    original_here = orbit.HERE
    try:
        orbit.HERE = source_dir
        (source_dir/source_name).write_bytes(blobs[source_name]+b' ')
        reject('changed_actual_root_source', orbit.run,
               'authenticated input: '+source_name, rejected)
    finally:
        orbit.HERE = original_here
    return {'rejections': rejected, 'historical_assertions_execute_with_optimization_zero': True,
            'all_mutations_in_disposable_bytes_or_directory': True,
            'no_path_import_or_pyc_execution': True,
            'full_scientific_stages_replayed': False}


def scientific_checks(v, package):
    frozen, rejected = v.Frozen(package), []
    independent = load_module(package/'independent/check.py',
                              frozen.raw('independent/check.py'))
    controls = independent.controls()
    require(len(controls) == 9 and all(row['same_guard_deletion'] == 'ACCEPTED' for row in controls),
            'complete independent orbit controls')
    rejected.extend({'name': row['name'], 'intended_gate': row['intended_guard']} for row in controls)
    orbit = load_module(package/'orbit/check.py', frozen.raw('orbit/check.py'))
    events = orbit.word(1, 1)
    orbit.endpoint(orbit.ring_word(1, 1, events), 1, 1, 2)
    omitted_query = copy.deepcopy(events)
    del omitted_query[next(index for index, event in enumerate(omitted_query) if event['op'] == 'query')]
    bad_public = orbit.ring_word(1, 1, omitted_query)
    bad_private = orbit.ring_word(1, 1, events[:-1])
    cases = [
        ('actual orbit query omitted', 'public every-coefficient endpoint',
         lambda deleted: orbit.endpoint(bad_public, 1, 1, 2, deleted)),
        ('actual borrowed spectator return omitted', 'dirty spectator every-coefficient endpoint',
         lambda deleted: orbit.endpoint(bad_private, 1, 1, 2, deleted)),
        ('full common transform violates actual local alphabet', 'local first-order capacity',
         lambda deleted: orbit.local_capacity(orbit.target(4, 3, 2), deleted)),
    ]
    for name, guard, probe in cases:
        result = orbit.reject_delete(name, guard, probe)
        require(result['same_guard_deletion_accepts'], 'actual orbit production gate deletion')
        rejected.append({'name': name, 'intended_gate': guard})
    return {'rejections': rejected, 'executed_check_deletions': 12,
            'actual_mathematical_mutations_after_authentication': True,
            'deletion_scope': 'the same named production predicate',
            'full_scientific_stages_replayed': False}

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
             'orbit/check.py', 'independent/check.py']
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
    result = {'status': 'PASS_C09_ORBIT_COMPACT_SOURCE_RECORD_AND_SEMANTIC_CONTROLS',
              'source_hashes': before, 'control_source_sha256': sha(Path(__file__).read_bytes()),
              'runs': results, 'normal_and_optimized_receipts_equal_except_mode': True,
              'intended_rejections_per_mode': count,
              'executed_check_deletions_per_mode': deletions,
              'full_scientific_receipts_compared': 2,
              'full_scientific_stages_replayed': False, 'no_new_kappa': True}
    if args.output:
        with args.output.open('x') as destination:
            destination.write(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('status', 'intended_rejections_per_mode',
                      'executed_check_deletions_per_mode', 'full_scientific_receipts_compared')}, sort_keys=True))


if __name__ == '__main__':
    main()
