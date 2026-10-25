#!/usr/bin/env python3
"""Compact authenticated-source, full-record and exact paired-endpoint gates controls.

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
                                for stage in ("endpoints", "geometry"))))
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
    require(len(records) == 2, "both complete scientific records")
    return records


def coverage_checks(v, temporary):
    rejected, counts = [], {}
    for stage in ("endpoints", "geometry"):
        names = sorted(v.expected_records(stage))
        v.check_coverage(stage, names)
        counts[stage] = len(names)
        for suffix, changed in (("omission", []), ("duplicate", names + names),
                                ("extra", names + ["unexpected.json"])):
            reject(stage + "_" + suffix,
                   lambda changed=changed, stage=stage: v.check_coverage(stage, changed),
                   "complete stage record coverage changed: " + stage, rejected)
    require(counts == {"endpoints": 1, "geometry": 1}, "two fixed stage inventories")

    class GeneratedFixture:
        def __init__(self, omit=False):
            self.root, self.compared, self.omit = temporary, [], omit
            self.scripts, self.reads = [], []

        def raw(self, name):
            require(name == "frozen/history/ORDER3-GEOMETRY.json.gz",
                    "dispatch authenticates declared historical geometry")
            self.reads.append(name)
            return gzip.compress(b'{"contracts":"literal fixture"}', mtime=0)

        def run(self, script, arguments):
            self.scripts.append(script)
            require(arguments[:4] == [
                "--ports", self.root / "frozen/inputs/CANONICAL-WORD.json.gz",
                "--compiler", self.root / "frozen/inputs/clifford_exact.py"],
                "dispatch literal source arguments")
            if script == "check_endpoints.py":
                require(arguments[4:6] == [
                    "--template", self.root / "frozen/inputs/GLOBAL-TEMPLATE.json.gz"],
                    "endpoint template argument")
                geometry = Path(arguments[arguments.index("--geometry") + 1])
                require(geometry.read_bytes() == b'{"contracts":"literal fixture"}'
                        and geometry.is_relative_to(temporary),
                        "endpoint receives authenticated decoded original")
            Path(arguments[arguments.index("--output") + 1]).write_text("{}")

        def compare(self, name, raw):
            require(raw == b"{}", "tiny fixture output reached comparison")
            if not self.omit:
                self.compared.append(name)

    for stage in ("endpoints", "geometry"):
        scratch = temporary / ("dispatch-" + stage)
        scratch.mkdir()
        frozen = GeneratedFixture()
        v.replay(frozen, scratch, stage)
        v.check_coverage(stage, frozen.compared)
        require(frozen.scripts == [{"endpoints": "check_endpoints.py",
                                   "geometry": "check_geometry.py"}[stage]],
                "dispatch selects one declared checker")
    scratch = temporary / "dispatch-deleted-compare"
    scratch.mkdir()
    frozen = GeneratedFixture(omit=True)
    v.replay(frozen, scratch, "geometry")
    reject("deleted_actual_compare_call",
           lambda: v.check_coverage("geometry", frozen.compared),
           "complete stage record coverage changed: geometry", rejected)
    saved = v.require
    try:
        v.require = lambda ok, message: (
            None if message.startswith("complete stage record coverage changed:")
            else saved(ok, message))
        try:
            reject("deleted_coverage_gate",
                   lambda: v.check_coverage("geometry", frozen.compared),
                   "complete stage record coverage changed: geometry", [])
        except ValueError as error:
            require(str(error) == "control accepted: deleted_coverage_gate",
                    "coverage deletion sensitivity")
        else:
            raise ValueError("coverage check deletion not detected")
    finally:
        v.require = saved
    return {"rejections": rejected, "stage_counts": counts,
            "real_dispatch_with_tiny_fixtures_passes": True,
            "authenticated_historical_geometry_decoded_to_external_scratch": True,
            "named_coverage_gate_deletion_detected": True}


def selected_main_functions(raw, names, namespace):
    tree = ast.parse(raw)
    mains = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == "main"]
    require(len(mains) == 1, "unique reviewed main")
    selected = [node for node in mains[0].body
                if isinstance(node, ast.FunctionDef) and node.name in names]
    require(len(selected) == len(names) and {node.name for node in selected} == set(names),
            "exact production predicate selection")
    exec(compile(ast.Module(body=selected, type_ignores=[]),
                 "authenticated exact production predicates", "exec",
                 dont_inherit=True, optimize=0), namespace)
    return namespace


def endpoint_gates(v, package, temporary):
    frozen = v.Frozen(package)
    raw = frozen.raw("check_endpoints.py")
    endpoint = load_module(package / "check_endpoints.py", raw)
    geometry = load_module(package / "check_geometry.py", frozen.raw("check_geometry.py"))
    compiler = geometry.compiler_from_bytes(frozen.raw("frozen/inputs/clifford_exact.py"))
    namespace = dict(endpoint.__dict__, ce=compiler)
    selected_main_functions(raw, ("same", "chosen"), namespace)
    same, chosen = namespace["same"], namespace["chosen"]
    historical = v.data(frozen.raw("frozen/history/ORDER3-GEOMETRY.json.gz"))
    row = historical["contracts"][0]
    p = row["P"]
    require(p.bit_count() % 4 == 3, "actual nontrivial native adapter")
    expected, native = chosen((p,)), compiler.cgate(9, p)
    same(native.then(compiler.xgate(9, p)), expected, "valid_native_adapter")
    rejected = []
    reject("actual_native_adapter_omission",
           lambda: same(native, expected, "adapter"), "adapter_tableau", rejected)
    axes = (p,) + tuple(row["R"])
    actual = chosen(axes)
    bad = actual.then(compiler.Op(9, compiler.identity(9), [("phase", 1)]))
    require(bad.tab == actual.tab, "global phase defect preserves signed Pauli images")
    reject("actual_gauge_global_i", lambda: same(bad, actual, "phase"),
           "phase_phase", rejected)
    same(bad, actual, "phase", phase_guard=False)
    recipe = v.data(frozen.raw("frozen/inputs/GLOBAL-TEMPLATE.json.gz"))["recipe"]
    endpoint.accept_laurent(endpoint.laurent_word(recipe), endpoint.laurent_target())
    witnesses = {}
    for mutation in ("backward_inverse", "backward_sign", "bridge_sign"):
        try:
            endpoint.accept_laurent(endpoint.laurent_word(recipe, mutation),
                                    endpoint.laurent_target())
        except endpoint.CheckFailure as error:
            require(error.code == "laurent_endpoint", "intended Laurent rejection")
            require(error.witness["difference_integer_coefficient"] != 0,
                    "nonzero exact Laurent defect")
            witnesses[mutation] = error.witness
            rejected.append({"name": "actual_laurent_" + mutation,
                             "intended_gate": "laurent_endpoint"})
        else:
            raise ValueError("Laurent mutation survived: " + mutation)
    return {"rejections": rejected, "port": p, "laurent_defects": witnesses,
            "authenticated_production_predicates": ["same", "chosen", "accept_laurent"],
            "phase_guard_deletion_accepts_actual_global_i_defect": True,
            "valid_adapter_and_complete_signed_B4_laurent_word_accepted": True,
            "full_endpoint_stage_replayed": False}


def source_gates(v, package, temporary):
    frozen = v.Frozen(package)
    endpoint = load_module(package / "check_endpoints.py", frozen.raw("check_endpoints.py"))
    geometry = load_module(package / "check_geometry.py", frozen.raw("check_geometry.py"))
    rejected = []
    fake = b"def inner():\n    assert False, 'NESTED_COMPILER_ASSERT'\ninner()\n"
    fake_path = temporary / "fixture compiler.py"
    fake_path.write_bytes(fake)
    old_geometry = temporary / "authenticated original geometry.json"
    old_geometry.write_bytes(v.decoded(frozen.raw("frozen/history/ORDER3-GEOMETRY.json.gz")))
    output = temporary / "unwritten endpoint result.json"
    saved_argv, saved_pins = sys.argv, endpoint.PINS.copy()

    def endpoint_call():
        sys.argv = ["check_endpoints.py", "--ports",
                    str(package / "frozen/inputs/CANONICAL-WORD.json.gz"),
                    "--template", str(package / "frozen/inputs/GLOBAL-TEMPLATE.json.gz"),
                    "--geometry", str(old_geometry), "--compiler", str(fake_path),
                    "--output", str(output)]
        endpoint.main()

    try:
        output.write_text("{}")
        reject("endpoint_early_existing_output", endpoint_call,
               "output_already_exists", rejected)
        output.unlink()
        reject("endpoint_changed_compiler_bytes", endpoint_call, "input_byte_pins", rejected)
        endpoint.PINS["compiler"] = sha(fake)
        reject("endpoint_nested_compiler_assertion", endpoint_call,
               "NESTED_COMPILER_ASSERT", rejected)
    finally:
        sys.argv, endpoint.PINS = saved_argv, saved_pins
    require(not output.exists(), "failed endpoint fixture emitted a receipt")
    reject("geometry_changed_compiler_bytes",
           lambda: geometry.captured(fake_path, geometry.COMPILER_SHA),
           "input SHA256", rejected)
    reject("geometry_nested_compiler_assertion",
           lambda: geometry.compiler_from_bytes(fake),
           "NESTED_COMPILER_ASSERT", rejected)
    captured = geometry.compiler_from_bytes(b"assert __debug__\nCAPTURED = 713\n")
    require(captured.CAPTURED == 713, "geometry executes supplied compiler buffer")
    return {"rejections": rejected, "captured_compiler_assertions_enabled": True,
            "endpoint_fixture_pin_rebound_only_in_disposable_module": True,
            "full_scientific_stages_replayed": False}


def geometry_gates(v, package):
    frozen = v.Frozen(package)
    g = load_module(package / "check_geometry.py", frozen.raw("check_geometry.py"))
    receipt = v.data(frozen.raw("artifacts/GEOMETRY.json.gz"))
    ports, partners = receipt["ports"], receipt["partners"]
    full = g.frame_phase(tuple(1 << i for i in range(9)))
    rejected, records = [], []
    inventory, values = {}, {}
    g.intern_phase(inventory, values, g.ZERO, key="forced-index-collision")
    g.intern_phase(inventory, values, g.ZERO, key="forced-index-collision")
    reject("distinct_phase_maps_forced_same_index",
           lambda: g.intern_phase(inventory, values, bytes([1] * 512),
                                  key="forced-index-collision"),
           "phase digest collision", rejected)
    for rank in (2, 3):
        edge = next(row for row in receipt["edge_witnesses"] if row["minimal_rank"] == rank)
        p, q = ports[edge["source"]], partners[edge["source"]]
        pt, qt = ports[edge["target"]], partners[edge["target"]]
        common = tuple(edge["frame"])
        g.accept_frame(p, q, pt, qt, common)
        phases = (g.frame_phase((p,)), g.frame_phase((qt,)), g.frame_phase(common),
                  g.phase_product(full, g.phase_inverse(g.frame_phase((q,)))),
                  g.phase_product(full, g.phase_inverse(g.frame_phase((pt,)))))
        expected = g.expected_rows(g.transition(phases[0], phases[3]),
                                   g.transition(phases[1], phases[4]),
                                   g.transition(phases[0], phases[4]), 1)
        rows, ops, ranks = g.contact_word(phases, 1, rank)
        g.accept_boundary(rows, expected)
        g.accept_invoice(ops, ranks, rank)
        for mutation, field in (("omit_helper_return", 2), ("omit_precompensation", 1),
                                ("wrong_delivery_sign", 1), ("global_phase", 1)):
            bad, _, _ = g.contact_word(phases, 1, rank, mutation)
            defect = g.actual_difference(bad[field], expected[field])
            require(defect is not None and defect["difference_Gaussian"] != [0, 0],
                    "actual nonzero physical character defect")
            reject("rank" + str(rank) + "_" + mutation,
                   lambda bad=bad: g.accept_boundary(bad, expected),
                   "physical boundary field " + str(field), rejected)
            g.accept_boundary(bad, expected, omit=field)
            records.append({"rank": rank, "mutation": mutation, "defect": defect,
                            "same_guard_deleted_and_accepted": True})
        bad, ops, ranks = g.contact_word(phases, 1, rank, "extra_canceling_adds")
        g.accept_boundary(bad, expected)
        reject("rank" + str(rank) + "_positive_canceling_pair_cost",
               lambda: g.accept_invoice(ops, ranks, rank),
               "complete native and scalar invoice", rejected)
        g.accept_invoice(ops, ranks, rank, enabled=False)
        records.append({"rank": rank, "mutation": "extra_canceling_adds",
                        "exact_operator_preserved": True,
                        "same_guard_deleted_and_accepted": True})
    return {"rejections": rejected, "actual_word_controls": records,
            "executed_mathematical_guard_deletions": len(records),
            "full_geometry_stage_replayed": False}


def output_gates(v, package, temporary):
    rejected = []
    old_argv = sys.argv
    existing = temporary / "existing wrapper output"
    existing.write_text("preserved")
    def invoke(output):
        sys.argv = ["verify.py", "--stage", "geometry", "--output", str(output)]
        v.main()
    try:
        reject("wrapper_existing_output", lambda: invoke(existing),
               "output already exists", rejected)
        reject("wrapper_internal_output", lambda: invoke(package / "forbidden-new-output.json"),
               "output must be external", rejected)
    finally:
        sys.argv = old_argv
    require(existing.read_text() == "preserved", "existing output preserved")
    return {"rejections": rejected, "guards_precede_scientific_replay": True}


def contract_gates(v, package):
    frozen = v.Frozen(package)
    original = {name: v.data(frozen.raw(name)) for name in (
        "artifacts/ENDPOINTS.json.gz", "artifacts/GEOMETRY.json.gz")}
    v.check_contracts(frozen)
    class Candidate:
        def __init__(self, values):
            self.values = values
        def raw(self, name):
            return json.dumps(self.values[name]).encode()
    changed = copy.deepcopy(original)
    changed["artifacts/GEOMETRY.json.gz"]["contracts"][0]["R"][0] ^= 1
    typed = copy.deepcopy(original)
    typed["artifacts/GEOMETRY.json.gz"]["contracts"][0]["P"] = True
    omitted = copy.deepcopy(original)
    omitted["artifacts/GEOMETRY.json.gz"]["contracts"].pop()
    wrong_digest = copy.deepcopy(original)
    wrong_digest["artifacts/GEOMETRY.json.gz"]["geometry_contracts_sha256"] = "0" * 64
    rejected = []
    for label, values, message in (
            ("geometry_array_changed_original_digest_retained", changed, "paired contract arrays differ"),
            ("geometry_array_scalar_type_changed", typed, "paired contract arrays differ"),
            ("geometry_contract_omitted", omitted, "complete paired contract count"),
            ("geometry_declared_digest_changed", wrong_digest, "paired contract digest mismatch")):
        reject(label, lambda values=values: v.check_contracts(Candidate(values)), message, rejected)
    saved = v.require
    try:
        v.require = lambda ok, message: (
            None if message == "paired contract arrays differ" else saved(ok, message))
        v.check_contracts(Candidate(changed))
    finally:
        v.require = saved
    return {"rejections": rejected,
            "full_ordered_contracts": 112,
            "canonical_contract_digest": original["artifacts/ENDPOINTS.json.gz"][
                "geometry_contracts_sha256"],
            "named_array_guard_deletion_accepts_real_contract_defect": True,
            "mutation_performed_after_original_receipt_authentication": True}


def child(package):
    verifier = load_module(package / "verify.py")
    verifier.Frozen(package).check_all()
    with tempfile.TemporaryDirectory(prefix="C02 compact controls ") as directory:
        temporary = Path(directory)
        result = {
            "loader": loader_checks(verifier, temporary),
            "record_gate": record_checks(verifier, temporary),
            "compression": compression_checks(verifier, temporary),
            "coverage": coverage_checks(verifier, temporary),
            "endpoint_gates": endpoint_gates(verifier, package, temporary),
            "source_gates": source_gates(verifier, package, temporary),
            "geometry_gates": geometry_gates(verifier, package),
            "output_gates": output_gates(verifier, package, temporary),
            "contract_gates": contract_gates(verifier, package),
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
    names = ["verify.py", "check_endpoints.py", "check_geometry.py",
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
                          for section in results[0].values() if isinstance(section, dict))
    rejection_count += sum(len(record["rejections"]) for record in results[0]["real_records"])
    require(rejection_count == 64, "complete compact rejection count")
    result = {
        "status": "PASS_PAIRED_ENDPOINT_COMPACT_SOURCE_RECORD_AND_MATHEMATICAL_GATES",
        "source_hashes": before,
        "control_source_sha256": sha(Path(__file__).read_bytes()),
        "runs": results,
        "normal_and_optimized_receipts_equal_except_mode": True,
        "full_scientific_stages_replayed": False,
        "intended_rejections_per_mode": rejection_count,
        "executed_check_deletions_per_mode": 14,
        "full_scientific_receipts_compared": 2,
        "no_new_kappa": True,
    }
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "status", "intended_rejections_per_mode", "executed_check_deletions_per_mode",
        "full_scientific_receipts_compared", "normal_and_optimized_receipts_equal_except_mode")},
        sort_keys=True))


if __name__ == "__main__":
    main()
