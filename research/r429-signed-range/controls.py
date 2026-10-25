#!/usr/bin/env python3
"""Compact B04 source-selection and acceptance controls.

No historical search or complete word replay is run here.
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
    module = types.ModuleType("b04_control_verifier")
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
    # Advance only the storage digest in this disposable fixture. The
    # unchanged original digest must independently detect altered payload.
    f.hashes[name] = sha(changed)
    reject("changed_decompressed_original", f.check_all,
           "compressed original bytes changed", rejected)
    equivalent = gzip.compress(plain, mtime=17)
    (root / name).write_bytes(equivalent)
    f.hashes[name] = sha(equivalent)
    f.check_all()
    need(f.decoded(name) == plain, "equivalent compression rejected")
    return {"rejections": rejected, "equivalent_storage_with_same_original_accepted": True}


def mathematical_checks(v, package):
    frozen = v.Frozen(package)
    frozen.check_all()
    _, scalar, _, _, _ = v.retained_functions(frozen)
    word = [[1, 0, 1, 1, 0, 23], [1, 1, 2, 1, 0, 23]]
    records, rows, prefix, norms = scalar.code(word)
    need(records == word and prefix == [2, 3] and norms == [2, 3],
         "two-ADD source-code positive control")
    need(rows[0][0] == {0: 1, 1: 1} and rows[1][0] == {0: 1, 1: -1, 2: 1},
         "noncommuting fixture endpoints")
    rejected = []
    reject("self_source_add", lambda: scalar.code([[1, 0, 0, 1, 0, 23]]),
           "source code not inplace", rejected)
    reject("source_coordinate_outside_bank", lambda: scalar.code([[1, 0, 111, 1, 0, 23]]),
           "source code not inplace", rejected)
    namespace = scalar.code.__globals__
    saved_add, saved_need = namespace["add"], namespace["need"]
    try:
        # Source authentication has completed. This is an arithmetic defect
        # injected into the executed primitive, not a modified pinned file.
        namespace["add"] = lambda a, b, coefficient: saved_add(a, b, abs(coefficient))
        reject("inverse_subtraction_replaced_by_addition", lambda: scalar.code(word),
               "signed source-code literal inverse", rejected)
        namespace["need"] = lambda ok, message: (
            None if message == "signed source-code literal inverse" else saved_need(ok, message))
        try:
            reject("disabled_inverse_gate", lambda: scalar.code(word),
                   "signed source-code literal inverse", [])
        except ValueError as error:
            need(str(error) == "control accepted: disabled_inverse_gate",
                 "mathematical check deletion sensitivity")
        else:
            raise ValueError("inverse mutation survived deletion of its target check")
    finally:
        namespace["add"], namespace["need"] = saved_add, saved_need
    independent = frozen.module("frozen/reviews/integer/check_integer.py")
    def fail(message):
        raise ValueError(message)
    intended = independent["rejected"](
        "intended_fixture", "INTENDED_GATE", lambda: fail("INTENDED_GATE"))
    need(intended["expected_semantic_gate_matched"] is True,
         "independent control intended-gate acceptance")
    reject("independent_control_rejects_unrelated_exception",
           lambda: independent["rejected"](
               "unrelated_fixture", "INTENDED_GATE", lambda: fail("UNRELATED_GATE")),
           "negative control reached an unintended gate", rejected)
    return {"actual_authenticated_function": "bit_signed_audit.code",
            "arbitrary_source_columns": 111, "positive_prefix_norms": prefix,
            "rejections": rejected, "deleted_named_check_detected": True}


def real_receipts(v, package):
    frozen = v.Frozen(package)
    names = [
        "frozen/candidate/RESULT.json",
        "frozen/candidate/GROWTH.json",
        "frozen/historical/REPLAY.json",
        "frozen/reviews/integer/CHECKS.json.gz",
        "frozen/reviews/range/CHECKS.json.gz",
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
    with tempfile.TemporaryDirectory(prefix="b04-controls-") as temp:
        temporary = Path(temp).resolve()
        result = {
            "source_selection": source_checks(v, temporary),
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
    report = {"status": "PASS_B04_COMPACT_SOURCE_AND_MATHEMATICAL_GATES",
              "source_hashes": before, "runs": results,
              "full_word_or_search_replayed": False, "no_new_kappa": True}
    if args.output:
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(canonical(report))


if __name__ == "__main__":
    main()
