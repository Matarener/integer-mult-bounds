#!/usr/bin/env python3
"""Bounded, source-bound replay of the restored P104 coefficient caller.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
All package modules are compiled from captured source bytes, without local
bytecode imports. Inherited theorems and reused implementations are identified
in SOURCES.json; the second literal implementation imports none of that code.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
IMPLEMENTATIONS = ("verify.py", "sources.py", "primary.py", "independent.py",
                   "direct.py", "observability.py")


def bootstrap():
    captured = {}
    for name in IMPLEMENTATIONS:
        path = PACKAGE / name
        if not path.is_file() or any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError("regular implementation required: " + name)
        captured[name] = path.read_bytes()
    source = ModuleType("restored_query_sources")
    source.__file__ = str(PACKAGE / "sources.py")
    exec(compile(captured["sources.py"], source.__file__, "exec"), source.__dict__)
    modules = {"sources": source}
    for name in IMPLEMENTATIONS[2:]:
        modules[name[:-3]] = source.module_from_bytes(
            captured[name], PACKAGE / name, "restored_query_" + name[:-3])
    return modules, captured


def authenticate_manifest(source):
    paths = {"SOURCES.json": PACKAGE / "SOURCES.json",
             "VERIFY.json": PACKAGE / "VERIFY.json",
             "PROOF.md": PACKAGE / "PROOF.md", "COSTS.md": PACKAGE / "COSTS.md"}
    captured = {name: source.read_regular(path) for name, path in paths.items()}
    manifest = source.strict_json(captured["SOURCES.json"])
    source.require(manifest["schema_version"] == 1, "source manifest schema")
    live = []
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        name = row["path"]
        path = ROOT / name
        source.require(type(name) is str and Path(name).as_posix() == name
                       and not Path(name).is_absolute() and ".." not in Path(name).parts,
                       "canonical source input path")
        source.require(name not in captured, "duplicate live input")
        data = source.read_regular(path)
        source.require(hashlib.sha256(data).hexdigest() == row["sha256"]
                       and len(data) == row["bytes"], "source manifest mismatch: " + name)
        captured[name], paths[name] = data, path
        live.append(name)
    declared = source.strict_json(captured["VERIFY.json"])["inputs"]
    source.require(set(live) <= set(declared), "every live pin must be declared")
    prefix = PACKAGE.relative_to(ROOT).as_posix() + "/"
    for name, expected in source.PINNED.items():
        relative = name if name.startswith("research/") else prefix + name
        source.require(relative in live, "execution input missing from live pins: " + relative)
        source.check_pinned_bytes(captured[relative], expected, relative)
    for name in ("PR3467_PROOF.md", "PR3467_README.md", "PR3467_COSTS.md",
                 "PR3382_PROOF.md", "PR3416_PROOF.md", "PR3426_PROOF.md", "ORIGINS.json"):
        source.require(prefix + "inputs/" + name in live,
                       "retained proof/credit missing from live pins: " + name)
    return captured, paths


def compare_implementations(source, primary, independent):
    checks = ("initial_y", "returned_y", "returned_coefficients", "returned_dirty",
              "output_q", "cut")
    for name in checks:
        source.require(primary[name] == independent[name],
                       "independent full-array disagreement: " + name)
    source.require(primary["receipt"]["terminal_slots"] ==
                   independent["receipt"]["terminal_slots"], "independent terminal slots")
    return {"full_array_equalities": list(checks),
            "prepared_and_returned_Y_banks_per_check": 52,
            "coefficient_banks": 52, "dirty_D_banks": 5,
            "producer_cut_banks": 6, "Gaussian_entries_per_bank": 512,
            "comparison_method": "Actual integer arrays, before taking receipt hashes."}


def expected_rejection(source, callback, message):
    try:
        callback()
    except (ValueError, OSError, KeyError) as error:
        return {"rejected": True, "reason": str(error)}
    raise source.SourceError(message)


def admission_controls(source, primary_module, primary):
    initial = {**primary["initial_y"], **primary["initial_dirty"]}
    short = {name: value[:] for name, value in initial.items()}
    short["Q7"] = short["Q7"][:256]
    boolean = {name: value[:] for name, value in initial.items()}
    boolean["Q7"][0] = (True, 0)
    results = {}
    for name, data in (("wrong_source_rank", short), ("boolean_source_component", boolean)):
        results[name] = expected_rejection(
            source, lambda data=data: primary_module.execute(primary["context"], data),
            "invalid source entrance accepted")
    return results


def format_controls(source):
    results = {}
    for name, data in (("duplicate_key", b'{"x":1,"x":2}'),
                       ("floating_number", b'{"x":1.0}'),
                       ("nonfinite_number", b'{"x":NaN}')):
        results[name] = expected_rejection(
            source, lambda data=data: source.strict_json(data), "malformed receipt accepted")
    source.require(not source.typed_equal({"x": [1]}, {"x": [True]}),
                   "Boolean/integer receipt ambiguity")
    results["boolean_integer_distinction"] = {"rejected": True}
    with tempfile.TemporaryDirectory(prefix="p104-query-source-") as directory:
        root = Path(directory)
        results["missing_source"] = expected_rejection(
            source, lambda: source.read_regular(root / "missing"), "missing source accepted")
        (root / "actual").write_bytes(b"unchanged")
        (root / "alias").symlink_to(root / "actual")
        results["source_symlink"] = expected_rejection(
            source, lambda: source.read_regular(root / "alias"), "source symlink accepted")
        (root / "folder").mkdir()
        (root / "folder" / "input").write_bytes(b"unchanged")
        (root / "folder-alias").symlink_to(root / "folder", target_is_directory=True)
        results["source_parent_symlink"] = expected_rejection(
            source, lambda: source.read_regular(root / "folder-alias" / "input"),
            "source parent symlink accepted")
        changing = root / "changing"
        changing.write_bytes(b"after")
        result = expected_rejection(
            source, lambda: source.recheck_inputs({"captured": {"fixture": b"before"},
                    "paths": {"fixture": changing}}), "changed captured input accepted")
        source.require(result["reason"] == "source changed during replay: fixture",
                       "change control failed for the wrong reason")
        results["changed_captured_input"] = result
    name = "research/p104-rounded-collector/inputs/WORD.json"
    bad = source.read_regular(ROOT / name) + b" "
    result = expected_rejection(
        source, lambda: source.check_pinned_bytes(bad, source.PINNED[name], "WORD control"),
        "wrong scientific bytes accepted")
    source.require(result["reason"] == "source digest mismatch: WORD control",
                   "scientific hash control failed for the wrong reason")
    results["wrong_scientific_bytes"] = result
    # Temporary paths are nondeterministic and are not part of the scientific receipt.
    for name in ("missing_source", "source_symlink", "source_parent_symlink"):
        results[name] = {"rejected": results[name]["rejected"]}
    return results


def calculate(modules, captured_implementations, captured_manifest):
    source = modules["sources"]
    context = source.capture_inputs()
    first = modules["primary"].analyze(context, run_negative_controls=True)
    second = modules["independent"].analyze(
        context["word"], context["native"], first["parameters"], first["initial_dirty"],
        run_negative_controls=True)
    comparison = compare_implementations(source, first, second)
    direct = {}
    for mode in ("zero", "inplace"):
        result = modules["direct"].run_direct(
            first["parameters"], first["initial_dirty"]["Q7"],
            first["receipt"]["terminal_slots"], mode)
        source.require(result["query"] == first["output_q"], "direct query differs from caller")
        source.require(result["coefficients"] == first["returned_coefficients"],
                       "direct coefficient return differs from caller")
        direct[mode] = result["receipt"]
    receipt = {
        "schema_version": 1, "status": "PASS_P104_RESTORED_QUERY",
        "scope": "Rank9 coefficient caller: codec,257-event cone,15-event collector,"
                 "252-event selective return,inverse codec. No omitted original histories.",
        "implementation_sha256": {name: hashlib.sha256(data).hexdigest()
                                  for name, data in captured_implementations.items()},
        "authenticated_input_and_proof_sha256": {
            name: hashlib.sha256(data).hexdigest() for name, data in captured_manifest.items()},
        "primary_literal": first["receipt"], "independent_literal": second["receipt"],
        "independence": "The primary reuses authenticated predecessor code. The second derives "
                        "Y paths and native arithmetic separately, imports no predecessor executable, "
                        "and credits adapted arithmetic from PR3467; both inherit written theorems.",
        "cross_implementation": comparison, "direct_schedules": direct,
        "observable_quotient": modules["observability"].analyze(first, modules["direct"]),
        "direct_arithmetic_and_ownership_controls": modules["direct"].verify_controls(),
        "caller_entrance_controls": admission_controls(source, modules["primary"], first),
        "source_and_typed_receipt_controls": format_controls(source),
        "claims_excluded": ["Full2025-event prefix", "5398-event whole word", "675 external ports",
                            "physical caller or tape implementation", "new supplier or kappa",
                            "independent human review or formal proof-kernel verification"],
    }
    source.recheck_inputs(context)
    return source.strict_json(source.canonical(receipt))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true",
                        help="Explicitly write this package's generated receipt after all checks")
    args = parser.parse_args()
    modules, implementations = bootstrap()
    source = modules["sources"]
    manifest, paths = authenticate_manifest(source)
    receipt_path = PACKAGE / "RECEIPT.json"
    expected_bytes = None if args.write_receipt else source.read_regular(receipt_path)
    expected = None if expected_bytes is None else source.strict_json(expected_bytes)
    actual = calculate(modules, implementations, manifest)
    for name, data in implementations.items():
        source.require(source.read_regular(PACKAGE / name) == data,
                       "implementation changed during replay: " + name)
    for name, data in manifest.items():
        source.require(source.read_regular(paths[name]) == data,
                       "input or proof changed during replay: " + name)
    if args.write_receipt:
        source.require(not receipt_path.is_symlink(), "receipt destination must not be a symlink")
        receipt_path.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        source.require(source.read_regular(receipt_path) == expected_bytes,
                       "receipt changed during replay")
        source.require(source.typed_equal(actual, expected), "typed deterministic receipt mismatch")
    print(json.dumps({"status": actual["status"], "caller_events": 524,
                      "native_pairs_per_literal_implementation": 184832,
                      "restored_coefficient_banks": 52,
                      "query_sha256": actual["primary_literal"]["output_q_sha256"],
                      "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest()},
                     sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_P104_RESTORED_QUERY: " + str(error), file=sys.stderr)
        sys.exit(1)
