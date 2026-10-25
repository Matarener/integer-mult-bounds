#!/usr/bin/env python3
"""Compact authenticated-source, full-record and exact carrier-gate controls.

All mutated fixtures and outputs are external. This does not rerun any
complete scientific audit. Substantial OpenAI Codex assistance; Apache-2.0.
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


def real_records(v, package):
    frozen = v.Frozen(package)
    names = sorted(set().union(*(v.expected_records(stage)
                                for stage in ("native", "normalization", "stars"))))
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
    require(len(records) == 3, "all three complete scientific records")
    return records


def coverage_checks(v, temporary):
    rejected, counts = [], {}
    for stage in ("native", "normalization", "stars"):
        names = sorted(v.expected_records(stage))
        v.check_coverage(stage, names)
        counts[stage] = len(names)
        for suffix, changed in (
                ("omission", []), ("duplicate", names + names),
                ("extra", names + ["unexpected.json"])):
            reject(stage + "_" + suffix,
                   lambda changed=changed, stage=stage:
                       v.check_coverage(stage, changed),
                   "complete stage record coverage changed: " + stage, rejected)
    require(counts == {"native": 1, "normalization": 1, "stars": 1},
            "three fixed stage inventories")

    class GeneratedFixture:
        def __init__(self, omit=False):
            self.root, self.compared, self.omit = temporary, [], omit
            self.scripts = []

        def run(self, script, arguments):
            self.scripts.append(script)
            require(arguments[:4] == [
                "--geometry", self.root / "frozen/geometry/D4-BUS-INPUT.json",
                "--compiler", self.root / "frozen/compiler/clifford_exact.py"],
                "dispatch literal source arguments")
            Path(arguments[arguments.index("--output") + 1]).write_text("{}")

        def compare(self, name, raw):
            require(raw == b"{}", "tiny fixture output reached comparison")
            if not self.omit:
                self.compared.append(name)

    for stage in ("native", "normalization", "stars"):
        scratch = temporary / ("dispatch-" + stage)
        scratch.mkdir()
        frozen = GeneratedFixture()
        v.replay(frozen, scratch, stage)
        v.check_coverage(stage, frozen.compared)
        require(frozen.scripts == [{
            "native": "check_native.py",
            "normalization": "check_normalization.py",
            "stars": "check_stars.py"}[stage]],
            "dispatch selects one declared checker")
    scratch = temporary / "dispatch-deleted-compare"
    scratch.mkdir()
    frozen = GeneratedFixture(omit=True)
    v.replay(frozen, scratch, "normalization")
    reject("deleted_actual_compare_call",
           lambda: v.check_coverage("normalization", frozen.compared),
           "complete stage record coverage changed: normalization", rejected)
    saved = v.require
    try:
        v.require = lambda ok, message: (
            None if message.startswith("complete stage record coverage changed:")
            else saved(ok, message))
        try:
            reject("deleted_coverage_gate",
                   lambda: v.check_coverage("normalization", frozen.compared),
                   "complete stage record coverage changed: normalization", [])
        except ValueError as error:
            require(str(error) == "control accepted: deleted_coverage_gate",
                    "coverage deletion sensitivity")
        else:
            raise ValueError("coverage check deletion not detected")
    finally:
        v.require = saved
    return {"rejections": rejected, "stage_counts": counts,
            "real_dispatch_with_tiny_fixtures_passes": True,
            "named_coverage_gate_deletion_detected": True}


def actual_normalizer_gates(v, package, temporary):
    """Select the exact small predicates, without executing the main audit."""
    frozen = v.Frozen(package)
    raw = frozen.raw("check_normalization.py")
    normalizer = load_module(package / "check_normalization.py", raw)
    compiler_path = package / "frozen/compiler/clifford_exact.py"
    compiler_raw = frozen.raw("frozen/compiler/clifford_exact.py")
    compiler = normalizer.load_compiler(compiler_raw, compiler_path)
    witness = v.data(frozen.raw(
        "frozen/history/paired-pivot/COMMON-FRAME-INVERSE-SEARCH.json"))
    geometry = v.data(frozen.raw("frozen/geometry/D4-BUS-INPUT.json"))
    tree = ast.parse(raw)
    mains = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == "main"]
    require(len(mains) == 1, "unique reviewed normalizer main")
    names = {"same", "brank", "zero_native"}
    selected = [node for node in mains[0].body
                if isinstance(node, ast.FunctionDef) and node.name in names]
    require(len(selected) == len(names) and {node.name for node in selected} == names,
            "exact normalizer production predicate coverage")
    namespace = {"need": normalizer.need, "ce": compiler, "n": 7}
    exec(compile(ast.Module(body=selected, type_ignores=[]),
                 "authenticated normalizer production predicates", "exec",
                 dont_inherit=True, optimize=0), namespace)
    same, zero_native = namespace["same"], namespace["zero_native"]
    n = 7
    identity = compiler.ident(n)

    def product(*operators):
        result = identity
        for operator in reversed(operators):
            result = result.then(operator)
        return result

    row = witness["rows"][0]
    require((row["p"], row["q"]) == (117, 7), "fixed actual C-port")
    core = [group[0] for group in geometry["groups7"]]
    chart = compiler.perm(n, compiler.inv(
        compiler.transpose(core + [5, 53, 30, 96], n), n))
    D = chart.then(compiler.hadamard(n, [3, 4])).then(chart.adjoint()).then(
        compiler.Op(n, compiler.identity(n), [("phase", 3)]))
    VC = D.then(compiler.cgate(n, core[0])).then(compiler.cgate(n, core[1]))
    F = compiler.fourier(n).then(compiler.xgate(n, 33))
    Cp, Cq = compiler.cgate(n, row["p"]), compiler.cgate(n, row["q"])
    S = product(VC, Cp.adjoint())
    T = product(F, Cp.adjoint(), Cq.adjoint())
    P = compiler.perm(n, row["G"]).then(compiler.diag(n, row["Q"]))
    post = product(T, P.adjoint(), S.adjoint())
    accepted = product(post, S, P)
    same(accepted, T, "actual_normalization")
    zero_native(product(F, P, F.adjoint()), "actual_common_F_cut")
    phase_wrong = product(compiler.Op(
        n, compiler.identity(n), [("phase", 1)]), accepted)
    rejected = []
    reject("actual_output_global_phase",
           lambda: same(phase_wrong, T, "actual_output_global_phase"),
           "actual_output_global_phase: global phase", rejected)
    require(phase_wrong.tab == T.tab, "phase control preserves signed Pauli images")
    same(phase_wrong, T, "phase_guard_deleted", phase_guard=False)
    no_chirp = product(F, compiler.perm(n, row["G"]), F.adjoint())
    reject("actual_omitted_common_chirp",
           lambda: zero_native(no_chirp, "actual_omitted_common_chirp"),
           "actual_omitted_common_chirp: zero native rank", rejected)
    require(namespace["brank"](no_chirp) > 0, "actual omitted chirp changes rank")

    # The compiler loader must use its provided buffer and retain assertions,
    # even if its nominal filename points to unrelated or absent disk bytes.
    placeholder = temporary / "captured compiler source.py"
    placeholder.write_text("raise RuntimeError('PATH_WAS_REOPENED')\n")
    captured = normalizer.load_compiler(
        b"assert __debug__, 'COMPILER_OPTIMIZED'\nCAPTURED = 713\n", placeholder)
    require(captured.CAPTURED == 713, "compiler executes authenticated buffer")
    reject("nested_compiler_assertion",
           lambda: normalizer.load_compiler(
               b"def inner():\n    assert False, 'COMPILER_ASSERT'\ninner()\n",
               placeholder),
           "COMPILER_ASSERT", rejected)
    for raw_json in (b'{"a":1,"a":2}', b'{"n":{"a":1,"a":2}}'):
        reject("normalizer_duplicate_json",
               lambda raw_json=raw_json: normalizer.strict_json(raw_json),
               "duplicate JSON key", rejected)
    return {"rejections": rejected,
            "actual_port": [117, 7],
            "authenticated_production_predicates": sorted(names),
            "valid_normalization_and_common_F_cut_accepted": True,
            "phase_guard_deletion_accepts_actual_global_i_defect": True,
            "omitted_chirp_native_rank": namespace["brank"](no_chirp),
            "nested_compiler_assertions_enabled": True,
            "captured_compiler_bytes_execute_without_path_reopen": True,
            "full_normalizer_search_or_basis_audit_replayed": False,
            "deletion_scope": "The exact operator equality predicate, not the entire package."}


def native_source_gates(v, package, temporary):
    frozen = v.Frozen(package)
    raw = frozen.raw("check_native.py")
    native = load_module(package / "check_native.py", raw)
    normalizer = load_module(package / "check_normalization.py",
                             frozen.raw("check_normalization.py"))
    compiler = normalizer.load_compiler(
        frozen.raw("frozen/compiler/clifford_exact.py"),
        package / "frozen/compiler/clifford_exact.py")
    tree = ast.parse(raw)
    mains = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == "main"]
    require(len(mains) == 1, "unique reviewed native main")
    selected = [node for node in mains[0].body
                if isinstance(node, ast.FunctionDef) and node.name == "intern"]
    require(len(selected) == 1, "unique native production operator index")
    namespace = {"ops": {}, "fingerprints": {}, "need": native.need,
                 "digest": lambda payload: "forced index collision"}
    exec(compile(ast.Module(body=selected, type_ignores=[]),
                 "authenticated native operator-index predicate", "exec",
                 dont_inherit=True, optimize=0), namespace)
    intern = namespace["intern"]
    intern(compiler.ident(1))
    intern(compiler.ident(1))
    rejected = []
    reject("operator_index_collision_with_distinct_exact_payloads",
           lambda: intern(compiler.xgate(1, 1)),
           "operator_digest_collision", rejected)
    existing = temporary / "existing native output.json"
    existing.write_text("{}")
    fake_compiler = temporary / "fixture compiler.py"
    fake = b"def inner():\n    assert False, 'NATIVE_NESTED_COMPILER_ASSERT'\ninner()\n"
    fake_compiler.write_bytes(fake)
    saved_argv, saved_pin = sys.argv, native.COMPILER_SHA

    def invoke(compiler_path, output):
        sys.argv = ["check_native.py", "--geometry",
                    str(package / "frozen/geometry/D4-BUS-INPUT.json"),
                    "--compiler", str(compiler_path), "--output", str(output)]
        native.main()

    try:
        reject("native_early_existing_output",
               lambda: invoke(fake_compiler, existing),
               "output_already_exists", rejected)
        reject("native_changed_compiler_bytes",
               lambda: invoke(fake_compiler, temporary / "unwritten native output.json"),
               "compiler_pin", rejected)
        # Rebind only this disposable module's fixture pin so the actual native
        # loader reaches its compiler execution branch. No package byte changes.
        native.COMPILER_SHA = sha(fake)
        reject("native_nested_compiler_assertion",
               lambda: invoke(fake_compiler, temporary / "unwritten native output.json"),
               "NATIVE_NESTED_COMPILER_ASSERT", rejected)
    finally:
        sys.argv, native.COMPILER_SHA = saved_argv, saved_pin
    require(not (temporary / "unwritten native output.json").exists(),
            "failed native fixture emitted a receipt")
    return {"rejections": rejected,
            "same_exact_operator_payload_reuses_index": True,
            "distinct_operator_payloads_rejected_despite_forced_equal_index": True,
            "nested_assertion_fixture_pin_rebound_only_in_disposable_module": True,
            "native_mathematical_stage_replayed": False}


def star_source_gates(v, package, temporary):
    """Reach the new star compiler loader without replaying its math audit."""
    frozen = v.Frozen(package)
    raw = frozen.raw("check_stars.py")
    stars = load_module(package / "check_stars.py", raw)
    fake_compiler = temporary / "fixture star compiler.py"
    fake = b"def inner():\n    assert False, 'STAR_NESTED_COMPILER_ASSERT'\ninner()\n"
    fake_compiler.write_bytes(fake)
    output = temporary / "unwritten star output.json"
    rejected = []
    saved_argv, saved_pin = sys.argv, stars.COMPILER_SHA

    def invoke():
        sys.argv = ["check_stars.py", "--geometry",
                    str(package / "frozen/geometry/D4-BUS-INPUT.json"),
                    "--compiler", str(fake_compiler), "--output", str(output)]
        stars.main()

    try:
        reject("star_changed_compiler_bytes", invoke,
               "compiler SHA256", rejected)
        # Only this disposable module admits the fixture. The exact captured
        # compiler branch must execute its nested assertion even under -O.
        stars.COMPILER_SHA = sha(fake)
        reject("star_nested_compiler_assertion", invoke,
               "STAR_NESTED_COMPILER_ASSERT", rejected)
    finally:
        sys.argv, stars.COMPILER_SHA = saved_argv, saved_pin
    require(not output.exists(), "failed star fixture emitted a receipt")
    return {"rejections": rejected,
            "nested_assertion_fixture_pin_rebound_only_in_disposable_module": True,
            "star_mathematical_stage_replayed": False}


def child(package):
    verifier = load_module(package / "verify.py")
    verifier.Frozen(package).check_all()
    with tempfile.TemporaryDirectory(prefix="carrier compact controls ") as directory:
        temporary = Path(directory)
        result = {
            "loader": loader_checks(verifier, temporary),
            "record_gate": record_checks(verifier, temporary),
            "compression": compression_checks(verifier, temporary),
            "coverage": coverage_checks(verifier, temporary),
            "actual_normalizer_gates":
                actual_normalizer_gates(verifier, package, temporary),
            "native_source_gates": native_source_gates(verifier, package, temporary),
            "star_source_gates": star_source_gates(verifier, package, temporary),
            "real_records": real_records(verifier, package),
        }
    verifier.Frozen(package).check_all()
    return {"parent_optimization": sys.flags.optimize, **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    package = args.package.resolve()
    if args.output:
        require(not args.output.exists(), "control output already exists")
        require(not args.output.resolve().is_relative_to(package),
                "control output must be external")
    if args.child:
        print(json.dumps(child(package), sort_keys=True))
        return
    names = ["verify.py", "check_native.py", "check_normalization.py", "check_stars.py",
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
    comparable = [{key: value for key, value in result.items()
                   if key != "parent_optimization"} for result in results]
    require(comparable[0] == comparable[1], "normal and optimized control receipts differ")
    rejection_count = sum(len(section.get("rejections", []))
                          for section in results[0].values()
                          if isinstance(section, dict))
    rejection_count += sum(len(record["rejections"])
                           for record in results[0]["real_records"])
    require(rejection_count == 53, "complete compact rejection count")
    result = {
        "status": "PASS_CARRIER_COMPACT_SOURCE_RECORD_AND_MATHEMATICAL_GATES",
        "source_hashes": before,
        "control_source_sha256": sha(Path(__file__).read_bytes()),
        "runs": results,
        "normal_and_optimized_receipts_equal_except_mode": True,
        "full_scientific_stages_replayed": False,
        "actual_fixed_port_acceptance_gates_replayed": True,
        "intended_rejections_per_mode": rejection_count,
        "executed_check_deletions_per_mode": 3,
        "no_new_kappa": True,
    }
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "status": result["status"],
        "intended_rejections_per_mode": rejection_count,
        "executed_check_deletions_per_mode": 3,
        "full_scientific_receipts_compared": 3,
        "normal_and_optimized_equal": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
