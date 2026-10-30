#!/usr/bin/env python3
"""Compact B07 source-selection and acceptance controls.

No route census or independent general-B replay is run here.
The fixed small hybrid word supplies one semantic inverse control.
Prepared for Ross with substantial OpenAI Codex assistance. Apache-2.0.
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


HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_verifier(package):
    path = package / "verify.py"
    raw = path.read_bytes()
    module = types.ModuleType("b07_control_verifier")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module, sha(raw)


def reject(name, action, expected, records):
    try:
        action()
    except (ValueError, AssertionError, FileNotFoundError) as error:
        need(expected in str(error), f"wrong rejection for {name}: {error}")
        records.append({"name": name, "reason": str(error)})
    else:
        raise ValueError("control accepted: " + name)


def fixture(directory, entries, original=None):
    root = Path(directory).resolve()
    root.mkdir(parents=True)
    hashes, origins = {}, {}
    for name, raw in entries.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        hashes[name] = sha(raw)
        origins[name] = {"sha256": sha(raw)}
        if original and name in original:
            origins[name]["original_sha256"] = sha(original[name])
    (root / "FROZEN-SHA256.json").write_text(json.dumps(hashes))
    (root / "ORIGINS.json").write_text(json.dumps(origins))
    return root


def source_checks(v, temporary):
    source = (
        b'import a_module_that_does_not_exist\n'
        b'raise RuntimeError("ORIGINAL_TOP_LEVEL_RAN")\n'
        b'def chosen(x=3):\n    return x + 4\n'
        b'def assertion():\n    assert False, "EXTRACTED_ASSERT"\n'
        b'def nested():\n    def inner():\n        assert False, "NESTED_ASSERT"\n'
        b'    return inner()\n'
        b'def main():\n    raise RuntimeError("ORIGINAL_MAIN_RAN")\n'
        b'if __name__ == "__main__":\n    main()\n'
    )
    root = fixture(temporary / "source", {
        "frozen/source.py": source,
        "frozen/duplicate.py": b"def duplicate():\n    return 1\n"
                               b"def duplicate():\n    return 2\n",
        "frozen/module.py": b'assert False, "MODULE_ASSERT"\n',
        "frozen/module_main.py": b'VALUE = 7\n'
                                  b'if __name__ == "__main__":\n'
                                  b'    raise RuntimeError("ORIGINAL_MAIN_RAN")\n',
    })
    f = v.Frozen(root)
    f.check_all()
    chosen = f.functions("frozen/source.py", ["chosen"], {})
    need(chosen.chosen() == 7 and set(vars(chosen)) == {"chosen"},
         "only declared functions should be exported")
    need(f.executed == {"frozen/source.py": ["chosen"]}, "selected-source receipt")
    rejected = []
    reject("direct_runtime_gate_under_parent_flags",
           lambda: v.need(False, "DIRECT_RUNTIME_GATE"), "DIRECT_RUNTIME_GATE", rejected)
    reject("extracted_assert_under_parent_flags",
           lambda: f.functions("frozen/source.py", ["assertion"], {}).assertion(),
           "EXTRACTED_ASSERT", rejected)
    reject("nested_assert_under_parent_flags",
           lambda: f.functions("frozen/source.py", ["nested"], {}).nested(),
           "NESTED_ASSERT", rejected)
    reject("authenticated_module_assert_under_parent_flags",
           lambda: f.module("frozen/module.py"), "MODULE_ASSERT", rejected)
    module = f.module("frozen/module_main.py")
    need(module["VALUE"] == 7 and module["__name__"] == "authenticated_review",
         "independent module main exclusion")
    (root / "frozen/module.py").write_bytes(b"VALUE = 99\n")
    reject("changed_authenticated_module",
           lambda: f.module("frozen/module.py"), "frozen input changed", rejected)
    reject("missing_named_definition",
           lambda: f.functions("frozen/source.py", ["absent"], {}),
           "function selection changed", rejected)
    reject("duplicate_source_definition",
           lambda: f.functions("frozen/duplicate.py", ["duplicate"], {}),
           "function selection changed", rejected)
    reject("duplicate_requested_name",
           lambda: f.functions("frozen/source.py", ["chosen", "chosen"], {}),
           "function selection changed", rejected)
    reject("unregistered_source",
           lambda: f.functions("frozen/unknown.py", ["chosen"], {}),
           "unregistered frozen input", rejected)
    (root / "frozen/source.py").write_bytes(b"def chosen():\n    return 99\n")
    reject("changed_authenticated_source",
           lambda: f.functions("frozen/source.py", ["chosen"], {}),
           "frozen input changed", rejected)
    (root / "frozen/source.py").unlink()
    reject("missing_registered_source",
           lambda: f.functions("frozen/source.py", ["chosen"], {}),
           "source.py", rejected)
    return {"imports_top_level_and_main_excluded": True, "rejections": rejected}


def nested_source_checks(v, temporary):
    import ast
    entries = {
        "frozen/recipe.py": b'import unavailable_original_dependency\n'
                            b'raise RuntimeError("ORIGINAL_TOP_LEVEL_RAN")\n'
                            b'def recipe(K):\n    return K + 19\n',
        "frozen/assert_recipe.py": b'def recipe(K):\n'
                                   b'    def inner():\n'
                                   b'        assert False, "NESTED_RECIPE_ASSERT"\n'
                                   b'    return inner()\n',
        "frozen/duplicate.py": b'def recipe(K):\n    return 1\n'
                               b'def recipe(K):\n    return 2\n',
        "frozen/absent.py": b'def other(K):\n    return 0\n',
    }
    root = fixture(temporary / "nested", entries)
    f = v.Frozen(root)
    mapping = {"source/" + name.split("/")[-1]: name for name in entries}
    mapping["source/unregistered.py"] = "frozen/unregistered.py"
    source = v.SourcePath(f, mapping)
    path = source / "source" / "recipe.py"
    need(path.read_bytes() == entries["frozen/recipe.py"], "exact mapped source bytes")
    need(not hasattr(path, "write_bytes") and not hasattr(path, "write_text"),
         "source path should expose no write interface")
    def nested(name):
        raw = (source / "source" / name).read_bytes()
        tree = v.recipe_tree(raw)
        definition = next(n for n in tree.body
                          if isinstance(n, ast.FunctionDef) and n.name == "recipe")
        namespace = {}
        exec(v.compile_checked(ast.Module(body=[definition], type_ignores=[]),
                               str(source / "source" / name), "exec"), namespace)
        return namespace["recipe"](4)
    need(nested("recipe.py") == 23, "nested recipe positive control")
    rejected = []
    reject("undeclared_logical_read", lambda: (source / "missing").read_bytes(),
           "undeclared historical source read", rejected)
    reject("absolute_path_escape", lambda: (source / "/etc/passwd").read_bytes(),
           "undeclared historical source read", rejected)
    reject("relative_path_escape", lambda: (source / "../outside").read_bytes(),
           "undeclared historical source read", rejected)
    reject("mapped_unregistered_input", lambda: (source / "source/unregistered.py").read_bytes(),
           "unregistered frozen input", rejected)
    reject("nested_recipe_assert_under_parent_flags", lambda: nested("assert_recipe.py"),
           "NESTED_RECIPE_ASSERT", rejected)
    reject("duplicate_nested_recipe", lambda: nested("duplicate.py"),
           "recipe definition must be unique", rejected)
    reject("missing_nested_recipe", lambda: nested("absent.py"),
           "recipe definition must be unique", rejected)
    (root / "frozen/recipe.py").write_bytes(b'def recipe(K):\n    return 99\n')
    reject("mapped_changed_bytes", path.read_bytes, "frozen input changed", rejected)
    (root / "frozen/recipe.py").unlink()
    reject("mapped_missing_file", path.read_bytes, "recipe.py", rejected)
    return {"only_authenticated_mapped_reads": True,
            "original_imports_and_top_level_excluded": True, "rejections": rejected}


def literal_pin_checks(v, package):
    frozen = v.Frozen(package)
    value = v.literal_raw_sha(frozen.raw("frozen/provenance/bit_cap_copy_local.py"))
    need(value == frozen.hashes["frozen/geometry/R438.json.gz"],
         "actual cap-copy constant and R438 digest")
    valid = b"RAW_SHA = '" + b"a" * 64 + b"'\n"
    need(v.literal_raw_sha(valid) == "a" * 64, "literal pin positive fixture")
    rejected = []
    reject("missing_literal_pin", lambda: v.literal_raw_sha(b"OTHER = 1\n"),
           "original RAW_SHA binding must be unique", rejected)
    reject("duplicate_literal_pin", lambda: v.literal_raw_sha(valid + valid),
           "original RAW_SHA binding must be unique", rejected)
    reject("wrong_literal_pin_type", lambda: v.literal_raw_sha(b"RAW_SHA = 123\n"),
           "original RAW_SHA is not a digest", rejected)
    reject("executable_pin_expression", lambda: v.literal_raw_sha(b"RAW_SHA = side_effect()\n"),
           "malformed node or string", rejected)
    return {"actual_original_pin_matches": True, "rejections": rejected}


def receipt_checks(v, temporary):
    value = {"integer": 1, "boolean": True, "nested": {"ordered": [1, 2, 3]}}
    root = fixture(temporary / "receipt", {
        "frozen/receipt.json": json.dumps(value).encode(),
    })
    f = v.Frozen(root)
    f.check_all()
    f.compare("frozen/receipt.json", copy.deepcopy(value))
    rejected = []
    mutations = {
        "boolean_for_integer": dict(value, integer=True),
        "float_for_integer": dict(value, integer=1.0),
        "integer_for_boolean": dict(value, boolean=1),
        "nested_omission": dict(value, nested={}),
        "list_reordering": dict(value, nested={"ordered": [1, 3, 2]}),
        "list_truncation": dict(value, nested={"ordered": [1, 2]}),
    }
    for name, altered in mutations.items():
        reject(name, lambda altered=altered: f.compare("frozen/receipt.json", altered),
               "complete receipt mismatch", rejected)
    (root / "frozen/receipt.json").unlink()
    reject("missing_fixed_receipt", lambda: f.compare("frozen/receipt.json", value),
           "receipt.json", rejected)
    need(not (root / "frozen/receipt.json").exists(), "missing receipt was regenerated")
    (root / "frozen/receipt.json").write_bytes(json.dumps(value).encode())
    saved = v.need
    try:
        v.need = lambda ok, message: (
            None if message.startswith("complete receipt mismatch") else saved(ok, message))
        try:
            reject("disabled_receipt_gate",
                   lambda: f.compare("frozen/receipt.json", mutations["boolean_for_integer"]),
                   "complete receipt mismatch", [])
        except ValueError as error:
            need(str(error) == "control accepted: disabled_receipt_gate",
                 "receipt check deletion sensitivity")
        else:
            raise ValueError("receipt mutation survived deletion of its target check")
    finally:
        v.need = saved
    return {"rejections": rejected, "deleted_named_check_detected": True}


def compression_checks(v, temporary):
    plain = b'{"all":"original bytes","ordered":[1,2,3]}\n'
    name = "frozen/original.json.gz"
    root = fixture(temporary / "compression",
                   {name: gzip.compress(plain, mtime=0)}, {name: plain})
    f = v.Frozen(root)
    f.check_all()
    need(f.decoded(name) == plain, "complete decompression")
    rejected = []
    changed = gzip.compress(b'{"all":"different bytes","ordered":[1,2,3]}\n', mtime=0)
    (root / name).write_bytes(changed)
    reject("changed_compressed_bytes", f.check_all, "frozen input changed", rejected)
    # Both manifests must agree about storage bytes before the separate
    # original-byte binding can be reached.
    f.hashes[name] = sha(changed)
    reject("origin_container_hash_mismatch", f.check_all,
           "origin container binding differs", rejected)
    origins = json.loads((root / "ORIGINS.json").read_bytes())
    origins[name]["sha256"] = sha(changed)
    (root / "ORIGINS.json").write_text(json.dumps(origins))
    reject("changed_decompressed_original", f.check_all,
           "compressed original bytes changed", rejected)
    equivalent = gzip.compress(plain, mtime=17)
    (root / name).write_bytes(equivalent)
    f.hashes[name] = sha(equivalent)
    origins[name]["sha256"] = sha(equivalent)
    (root / "ORIGINS.json").write_text(json.dumps(origins))
    f.check_all()
    need(f.decoded(name) == plain, "equivalent compression rejected")
    (root / "ORIGINS.json").write_text("{}")
    reject("origin_inventory_omission", f.check_all,
           "origin and frozen inventories differ", rejected)
    (root / "ORIGINS.json").write_text(json.dumps(origins))
    f.check_all()
    return {"rejections": rejected, "equivalent_storage_with_same_original_accepted": True}


def mathematical_checks(v, package):
    import ast
    import hashlib
    from types import SimpleNamespace
    frozen = v.Frozen(package)
    frozen.check_all()
    source = v.SourcePath(frozen, {"recipe.py": "frozen/upstream/global_k.py"})
    api = SimpleNamespace(parse=v.recipe_tree, FunctionDef=ast.FunctionDef, Module=ast.Module)
    names = ["need", "reduce_word", "inverse_word", "add", "left", "identity", "serial",
             "recipe", "old_word", "hybrid_word", "apply", "evaluate", "transpose_operator_word",
             "transpose_operators", "product", "receipt"]
    hybrid = frozen.functions("frozen/hybrid/closed_hybrid.py", names,
                              {"ast": api, "compile": v.compile_checked,
                               "sha256": hashlib.sha256, "RECIPE": source / "recipe.py",
                               "PIN": "20ecf2891d80b5acf18d980b2164fb44ea7faa90"})
    good = hybrid.receipt()
    frozen.compare("frozen/hybrid/CLOSED-HYBRID.json", good)
    namespace = hybrid.receipt.__globals__
    original_apply, original_need = namespace["apply"], namespace["need"]
    fault = {"used": False}
    def changed_inverse(rows, event, backwards=False):
        if backwards and event["kind"] == "code" and not fault["used"]:
            fault["used"] = True
            return original_apply(rows, event, backwards=False)
        return original_apply(rows, event, backwards)
    rejected = []
    try:
        namespace["apply"] = changed_inverse
        reject("one_actual_inverse_code_runs_forward", hybrid.receipt,
               "literal reverse-inverse cleanup", rejected)
        need(fault["used"], "actual inverse-code fault was not reached")
        namespace["need"] = lambda ok, message: (
            None if message == "literal reverse-inverse cleanup" else original_need(ok, message))
        fault["used"] = False
        try:
            reject("disabled_literal_inverse_gate", hybrid.receipt,
                   "literal reverse-inverse cleanup", [])
        except ValueError as error:
            need(str(error) == "control accepted: disabled_literal_inverse_gate",
                 "mathematical check deletion sensitivity")
        else:
            raise ValueError("inverse mutation survived deletion of its target check")
        need(fault["used"], "deleted-gate fault was not reached")
    finally:
        namespace["apply"], namespace["need"] = original_apply, original_need
    independent = frozen.module("frozen/reviews/recipe/check.py")
    def fail(message):
        raise ValueError(message)
    accepted = independent["reject"]("intended_fixture", lambda: fail("INTENDED"), "INTENDED")
    need(accepted["rejection"] == "INTENDED", "independent intended-gate fixture")
    reject("independent_control_rejects_unrelated_error",
           lambda: independent["reject"](
               "unrelated_fixture", lambda: fail("UNRELATED"), "INTENDED"),
           "wrong rejection for unrelated_fixture", rejected)
    return {"actual_authenticated_function": "closed_hybrid.receipt",
            "formal_input_rows": 8, "coefficient_ring": good["coefficient_ring"],
            "one_literal_inverse_code_direction_changed_after_authentication": True,
            "rejections": rejected, "deleted_named_check_detected": True}


def real_receipts(v, package):
    frozen = v.Frozen(package)
    names = [
        "frozen/hybrid/CLOSED-HYBRID.json",
        "frozen/hybrid/EARLY-PROMOTION.json",
        "frozen/recipe/BIT-NILPOTENT-RECIPE.json",
        "frozen/reviews/recipe/CHECKS.json.gz",
        "frozen/reviews/hybrid/CHECKS.json.gz",
    ]
    result = []

    def leaves(value, path=()):
        if isinstance(value, dict):
            for key in sorted(value):
                yield from leaves(value[key], path + (key,))
        elif isinstance(value, list):
            for key, item in enumerate(value):
                yield from leaves(item, path + (key,))
        else:
            yield path, value

    for name in names:
        value = frozen.data(name)
        frozen.compare(name, copy.deepcopy(value))
        need(type(value) is dict and len(value) > 1, "real receipt structure")
        changed = copy.deepcopy(value)
        path, old = max(leaves(value), key=lambda item: len(item[0]))
        need(len(path) > 1, "real receipt nested coverage")
        parent = changed
        for key in path[:-1]:
            parent = parent[key]
        if type(old) is bool:
            parent[path[-1]] = not old
        elif type(old) is int:
            parent[path[-1]] = old + 1
        elif type(old) is str:
            parent[path[-1]] = old + "-MUTATED"
        else:
            parent[path[-1]] = {"mutated": True}
        rejected = []
        reject("real_nested_field_mutation",
               lambda: frozen.compare(name, changed), "complete receipt mismatch", rejected)
        omitted = copy.deepcopy(value)
        parent = omitted
        for key in path[:-1]:
            parent = parent[key]
        del parent[path[-1]]
        reject("real_nested_field_omission",
               lambda: frozen.compare(name, omitted), "complete receipt mismatch", rejected)
        result.append({"receipt": name, "sha256": sha(frozen.raw(name)),
                       "mutated_nested_path": list(path), "rejections": rejected})
    return result


def child(package):
    v, verifier_hash = load_verifier(package)
    with tempfile.TemporaryDirectory(prefix="b07-controls-") as temp:
        temporary = Path(temp).resolve()
        result = {
            "source_selection": source_checks(v, temporary),
            "nested_sources": nested_source_checks(v, temporary),
            "literal_source_pin": literal_pin_checks(v, package),
            "receipt_contract": receipt_checks(v, temporary),
            "compressed_original_binding": compression_checks(v, temporary),
            "mathematical_controls": mathematical_checks(v, package),
            "complete_real_receipts": real_receipts(v, package),
        }
    return {"parent_optimization": sys.flags.optimize, "verifier_sha256": verifier_hash, **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    package = args.package.resolve()
    if args.child:
        print(canonical(child(package)))
        return
    before = {name: sha((package / name).read_bytes())
              for name in ("verify.py", "FROZEN-SHA256.json", "ORIGINS.json")}
    results = []
    for optimized in (False, True):
        command = [sys.executable, "-I", "-B"]
        if optimized:
            command.append("-O")
        command += [str(Path(__file__).resolve()), "--package", str(package), "--child"]
        proc = subprocess.run(command, capture_output=True, text=True)
        need(proc.returncode == 0, proc.stderr + proc.stdout)
        results.append(json.loads(proc.stdout))
    need(all(sha((package / name).read_bytes()) == expected for name, expected in before.items()),
         "verification core changed during compact controls")
    need(all(x["verifier_sha256"] == before["verify.py"] for x in results),
         "mixed verifier versions")
    report = {"status": "PASS_B07_COMPACT_SOURCE_AND_MATHEMATICAL_GATES",
              "source_hashes": before, "runs": results,
              "route_census_or_general_B_replayed": False,
              "small_fixed_hybrid_word_replayed": True, "no_new_kappa": True}
    if args.output:
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(canonical(report))


if __name__ == "__main__":
    main()
