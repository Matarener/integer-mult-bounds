#!/usr/bin/env python3
"""Compact C01 source, complete-record and mathematical acceptance controls.

Uses external temporary fixtures. Does not rerun the whole-word scalar audit
or the all-edge/all-helper census. Prepared with substantial Codex assistance.
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


def coverage_checks(v, temporary):
    rejected, counts = [], {}
    for stage in ("construction", "forest", "wholeword"):
        names = sorted(v.expected_records(stage))
        v.check_coverage(stage, names)
        counts[stage] = len(names)
        reject(stage + "_omission", lambda: v.check_coverage(stage, names[1:]),
               "complete stage record coverage changed: " + stage, rejected)
        reject(stage + "_duplicate", lambda: v.check_coverage(stage, names + names[:1]),
               "complete stage record coverage changed: " + stage, rejected)
        reject(stage + "_extra", lambda: v.check_coverage(stage, names + ["unexpected.json"]),
               "complete stage record coverage changed: " + stage, rejected)
    require(counts == {"construction": 13, "forest": 1, "wholeword": 1}, "stage inventory counts")
    # Invoke the real dispatch code with a non-mathematical output fixture.
    class GeneratedFixture:
        def __init__(self, extra=False, omit=None):
            self.root, self.compared, self.extra, self.omit = temporary, [], extra, omit
        def run(self, script, arguments):
            if script == "construct.py":
                output = Path(arguments[arguments.index("--out") + 1])
                output.mkdir()
                names = set(v.construction_names()) | ({"unexpected.json"} if self.extra else set())
                for name in names:
                    (output / name).write_text("{}")
            else:
                Path(arguments[arguments.index("--output") + 1]).write_text("{}")
        def compare(self, name, raw):
            if name != self.omit:
                self.compared.append(name)
    for stage in ("construction", "forest", "wholeword"):
        scratch = temporary / ("dispatch-" + stage)
        scratch.mkdir()
        f = GeneratedFixture()
        getattr(v, stage)(f, scratch)
        v.check_coverage(stage, f.compared)
    scratch = temporary / "dispatch-extra"
    scratch.mkdir()
    reject("extra_generated_construction_artifact",
           lambda: v.construction(GeneratedFixture(extra=True), scratch),
           "construction output inventory changed", rejected)
    scratch = temporary / "dispatch-omission"
    scratch.mkdir()
    f = GeneratedFixture(omit="artifacts/DESIGN.json")
    v.construction(f, scratch)
    reject("deleted_actual_compare_call", lambda: v.check_coverage("construction", f.compared),
           "complete stage record coverage changed: construction", rejected)
    saved = v.require
    try:
        v.require = lambda ok, message: None if message.startswith("complete stage record coverage changed:") else saved(ok, message)
        try:
            reject("deleted_coverage_gate", lambda: v.check_coverage("construction", f.compared),
                   "complete stage record coverage changed: construction", [])
        except ValueError as error:
            require(str(error) == "control accepted: deleted_coverage_gate", "coverage deletion sensitivity")
        else:
            raise ValueError("coverage check deletion not detected")
    finally:
        v.require = saved
    return {"rejections": rejected, "stage_counts": counts,
            "real_dispatch_with_tiny_fixtures_passes": True,
            "named_coverage_gate_deletion_detected": True}


def mathematical_checks(v, package):
    frozen = v.Frozen(package)
    mst = load_module(package / "independent_mst.py", frozen.raw("independent_mst.py"))
    source = v.data(frozen.raw("frozen/inputs/SOURCE-base.json.gz"))
    panel = v.data(frozen.raw("artifacts/TWO-SIDED-COMPENSATION-base.json.gz"))
    helpers = {event[2] for event in source["compensation"]}
    C = mst.sparse_matrix(source["compensation"], helpers)
    live = sorted(set(range(704)) - set(source["removed"]))
    expected = mst.expected_endpoint(C, live, "forward")
    mst.complete_endpoint_gate(mst.endpoint(panel, live, "forward"), expected)
    changed = copy.deepcopy(panel)
    changed[0][3] *= -1
    actual = mst.endpoint(changed, live, "forward")
    witness = mst.defect(actual, expected)
    require(witness is not None, "actual target-basis sign mutation ineffective")
    rejected = []
    reject("actual_target_basis_sign", lambda: mst.complete_endpoint_gate(actual, expected),
           "complete arbitrary-input panel endpoint", rejected)
    saved = mst.require
    try:
        mst.require = lambda ok, message: None if message == "complete arbitrary-input panel endpoint" else saved(ok, message)
        try:
            reject("deleted_actual_endpoint_gate", lambda: mst.complete_endpoint_gate(actual, expected),
                   "complete arbitrary-input panel endpoint", [])
        except ValueError as error:
            require(str(error) == "control accepted: deleted_actual_endpoint_gate", "actual endpoint deletion sensitivity")
        else:
            raise ValueError("actual endpoint check deletion not detected")
    finally:
        mst.require = saved
    return {"rejections": rejected, "actual_authenticated_candidate": True,
            "all_arbitrary_input_columns": len(live), "witness": witness,
            "named_endpoint_gate_deletion_detected": True}


def nested_producer_checks(v, package, temporary):
    frozen = v.Frozen(package)
    whole = load_module(package / "check_word.py", frozen.raw("check_word.py"))
    transport = temporary / "fixture transport.py"
    emitter = temporary / "fixture emitter.py"
    transport_raw = (
        b"from pathlib import Path\nimport gzip,json,sys\n"
        b"assert __debug__ and sys.flags.optimize == 0, 'NESTED_OPTIMIZATION'\n"
        b"p=Path(sys.argv[2]);p.mkdir()\n"
        b"(p/'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(b'{}',mtime=0))\n"
    )
    emitter_raw = (
        b"from pathlib import Path\nimport gzip,json,sys,hashlib\n"
        b"p=Path(sys.argv[1]);h=hashlib.sha256(b'[]').hexdigest()\n"
        b"(p/'LOCAL-PROGRAMS.json.gz').write_bytes(gzip.compress(json.dumps({'forward':[],'backward':[]}).encode(),mtime=0))\n"
        b"(p/'LOCAL-CHECKS.json').write_text(json.dumps({k:{'sha256':h} for k in ['forward','backward']}))\n"
    )
    transport.write_bytes(transport_raw)
    emitter.write_bytes(emitter_raw)
    whole.PRODUCER_HASHES = {"transport": sha(transport_raw), "emitter": sha(emitter_raw)}
    class ChangedAfterRead:
        def __init__(self, path, raw):
            self.path, self.raw, self.reads = path, raw, 0
        def __str__(self):
            return str(self.path)
        def read_bytes(self):
            self.reads += 1
            self.path.write_bytes(b"raise RuntimeError('NESTED_REOPENED_SOURCE')\n")
            return self.raw
    changing = ChangedAfterRead(transport, transport_raw)
    whole.produced_programs(temporary / "unused-word.json", changing, emitter, temporary / "nested-output")
    require(changing.reads == 1, "nested producer capture was not reached")
    bad = b"def inner():\n    assert False, 'NESTED_PRODUCER_ASSERT'\ninner()\n"
    transport.write_bytes(bad)
    whole.PRODUCER_HASHES["transport"] = sha(bad)
    rejected = []
    reject("nested_producer_assertion",
           lambda: whole.produced_programs(temporary / "unused-word.json", transport, emitter,
                                           temporary / "nested-never-written"),
           "AssertionError: NESTED_PRODUCER_ASSERT", rejected, exact=False)
    whole.PRODUCER_HASHES["transport"] = sha(transport_raw)
    reject("nested_producer_changed_source",
           lambda: whole.produced_programs(temporary / "unused-word.json", transport, emitter,
                                           temporary / "nested-never-written"),
           "producer execution buffer hash mismatch: transport", rejected)
    return {"rejections": rejected, "nested_captured_source_survives_path_change": True,
            "nested_producer_assertions_enabled": True}


def real_records(v, package):
    frozen = v.Frozen(package)
    names = sorted(set().union(*(v.expected_records(stage)
                                for stage in ("construction", "forest", "wholeword"))))
    def leaves(value, path=()):
        if isinstance(value, dict):
            for key in sorted(value):
                yield from leaves(value[key], path + (key,))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from leaves(child, path + (index,))
        else:
            yield path, value
    records = []
    for name in names:
        raw = frozen.raw(name)
        value = v.data(raw)
        frozen.compare(name, json.dumps(value).encode())
        path, old = max(leaves(value), key=lambda item: len(item[0]))
        require(len(path) > 1, "actual record nested coverage")
        changed, omitted = copy.deepcopy(value), copy.deepcopy(value)
        parent, deletion_parent = changed, omitted
        for key in path[:-1]:
            parent, deletion_parent = parent[key], deletion_parent[key]
        parent[path[-1]] = not old if type(old) is bool else old + 1 if type(old) is int else {"changed": True}
        del deletion_parent[path[-1]]
        rejected = []
        for label, candidate in (("nested_mutation", changed), ("nested_omission", omitted)):
            reject(label, lambda candidate=candidate: frozen.compare(name, json.dumps(candidate).encode()),
                   "complete typed record mismatch: " + name, rejected)
        records.append({"record": name, "sha256": sha(raw), "nested_path": list(path),
                        "rejections": rejected})
    require(len(records) == 15, "all fifteen complete records")
    return records


def child(package):
    v = load_module(package / "verify.py")
    v.Frozen(package).check_all()
    with tempfile.TemporaryDirectory(prefix="c01-compact-controls-") as directory:
        temporary = Path(directory)
        result = {
            "loader": loader_checks(v, temporary),
            "record_gate": record_checks(v, temporary),
            "compression": compression_checks(v, temporary),
            "coverage": coverage_checks(v, temporary),
            "actual_mathematics": mathematical_checks(v, package),
            "nested_producers": nested_producer_checks(v, package, temporary),
            "real_records": real_records(v, package),
        }
    v.Frozen(package).check_all()
    return {"parent_optimization": sys.flags.optimize, **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    package = args.package.resolve()
    if args.output:
        require(not args.output.resolve().is_relative_to(package), "control output must be external")
    if args.child:
        print(json.dumps(child(package), sort_keys=True))
        return
    names = ["verify.py", "independent_mst.py", "check_word.py",
             "FROZEN-SHA256.json", "ORIGINS.json"]
    before = {name: sha((package / name).read_bytes()) for name in names}
    results = []
    for optimized in (False, True):
        command = [sys.executable, "-I", "-B"] + (["-O"] if optimized else [])
        command += [str(Path(__file__).resolve()), "--package", str(package), "--child"]
        completed = subprocess.run(command, capture_output=True, text=True)
        require(completed.returncode == 0, completed.stdout + completed.stderr)
        results.append(json.loads(completed.stdout))
    require(before == {name: sha((package / name).read_bytes()) for name in names},
            "reviewed source changed during controls")
    comparable = [{key: value for key, value in run.items() if key != "parent_optimization"}
                  for run in results]
    require(comparable[0] == comparable[1], "normal and optimized control receipts differ")
    result = {"status": "PASS_C01_COMPACT_SOURCE_AND_MATHEMATICAL_GATES",
              "source_hashes": before, "runs": results,
              "normal_and_optimized_receipts_equal_except_mode": True,
              "full_wholeword_or_edge_census_replayed": False,
              "actual_single_compensation_panel_replayed": True, "no_new_kappa": True}
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
