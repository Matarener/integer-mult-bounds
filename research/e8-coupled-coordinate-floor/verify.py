#!/usr/bin/env python3
"""Source-bound replay for the coupled E8 COPY theorem.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
Checks certify finite premises and constructions; universal assembly is written.
"""

import argparse
import gc
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
REPOSITORY = PACKAGE.parent.parent
sys.path.insert(0, str(PACKAGE))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.loads(json.dumps(value, sort_keys=True))


def source_hashes():
    result = {}
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path == PACKAGE / "RESULT.json":
            continue
        require(not path.is_symlink(), "package contains a source symlink")
        result[path.relative_to(PACKAGE).as_posix()] = sha256(path.read_bytes()).hexdigest()
    return result


def authenticate():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = []
    for item in pins["files"]:
        if item.get("usage") == "input":
            path = REPOSITORY / item["path"]
            require(path.is_file() and not path.is_symlink(), "missing or aliased live source input")
            require(sha256(path.read_bytes()).hexdigest() == item["sha256"], "live source pin mismatch")
            live.append(item["path"])
    refs = json.loads((PACKAGE / "REFERENCES.json").read_text())
    for item in refs["snapshots"]:
        path = PACKAGE / item["local_path"]
        require(path.is_file() and not path.is_symlink(), "missing or aliased retained source")
        require(sha256(path.read_bytes()).hexdigest() == item["sha256"], "retained source pin mismatch")
    return {"live_input_count": len(live), "live_inputs": live,
            "retained_pending_source_files": len(refs["snapshots"]),
            "pending_commit_required_at_runtime": False}


def run():
    sources = authenticate()
    # Pending-source bytes are authenticated before importing their code.
    import finite_inputs
    import factors
    import independent_model
    import cut_basis_audit
    import dimension_audit
    import partial_fixture
    import cut_excluded_fixture
    import neighbor_primary
    import neighbor_audit
    import root_low_primary
    import root_low_audit
    import a9_strict_fixture

    certificate = json.loads((PACKAGE / "vendor/pr3755/CERTIFICATE.json").read_text())
    model, roots, finite = finite_inputs.run(certificate)
    independent_roots, independent_labels = independent_model.root_model()
    require(tuple(roots) == tuple(independent_roots), "independent root ordering/orientation differs")
    require(tuple(model["labels"]) == tuple(independent_labels), "independent dense labels differ")
    primary = factors.run(model, roots)
    second = independent_model.verify()
    for field, record in primary.items():
        other = second["fields"][field]["extension_family"]
        require(len(other) == len(record["coordinate_family"]) == 8, "fixture inventory mismatch")
        for left, right in zip(record["coordinate_family"], other):
            for key in ("k", "terms", "ranks", "costs"):
                require(left[key] == right[key], "independent sharp construction disagrees: " + key)
    cuts = cut_basis_audit.verify()
    partial = partial_fixture.verify()
    cut_excluded = cut_excluded_fixture.verify()
    strict_fixture = a9_strict_fixture.verify()
    relative = neighbor_primary.run(roots, model["labels"])
    relative_second = neighbor_audit.calculate(include_details=False)
    require(relative["minimum_nonroot_neighbor_deletions"]
            == relative_second["minimum_nonroot_neighbor_deletions"] == 27,
            "independent relative nonroot threshold differs")
    require(relative_second["minimum_critical_root_mismatch_deletions"] == 24,
            "relative root mismatch classification boundary")
    require(relative_second["matching_root_cases"] == 56
            and relative_second["complement_nonroot_minimum"] == 35,
            "relative exceptional character coverage")
    nonroot_low = neighbor_primary.low_weight_run(roots, model["labels"])
    nonroot_low_second = neighbor_audit.low_weight_calculate()
    require(nonroot_low["minimum"] == nonroot_low_second["minima"]["nonroot"] == 55,
            "independent nonroot low-word threshold differs")
    root_low = root_low_primary.run(roots, model["labels"])
    root_low_second = root_low_audit.run()
    require(root_low["minimum_root_weight_seven_neighbor_deletions"]
            == root_low_second["minimum_deletions_for_root_weight_at_most_seven"] == 29,
            "independent root low-weight neighbor threshold differs")
    # Keep one concrete minimizer, not 56 repeated orbit attainers. Bind the
    # complete lists by canonical digest; calculate() can emit full details.
    minimizers = relative_second["minimum_nonroot_witnesses"]
    relative_second["minimum_nonroot_witness_count"] = len(minimizers)
    relative_second["all_minimizers_sha256"] = sha256(
        json.dumps(canonical(minimizers), sort_keys=True).encode()).hexdigest()
    relative_second["minimum_nonroot_witnesses"] = minimizers[:1]
    edges = relative_second["transport"].pop("root_tree_edges")
    relative_second["transport"]["root_tree_edge_count"] = len(edges)
    relative_second["transport"]["root_tree_edges_sha256"] = sha256(
        json.dumps(edges).encode()).hexdigest()
    dimensions = []
    for dimension in range(23, 73):
        bill, profile, states = dimension_audit.minimum_relaxation_bill(dimension)
        require(bill == sum(profile) and tuple(sorted(profile)) == profile,
                "independent relaxed optimum reconstruction")
        require(bill >= (72 if dimension == 23 else 73), "independent strict dimension screen")
        dimensions.append({"dimension": dimension, "minimum_relaxed_bill": bill,
                           "memoized_states": states})
        gc.collect()
    require(dimensions[0]["minimum_relaxed_bill"] == 72
            and dimensions[1]["minimum_relaxed_bill"] == 73,
            "dimension23/24 boundary controls")
    math_faults = sum(x["product_fault_controls"] for x in primary.values())
    math_faults += sum(x["failure_controls"] for x in partial["fields"].values())
    math_faults += sum(x["failure_controls"] for x in cut_excluded["fields"].values())
    math_faults += sum(x["failed_product_controls"] for x in strict_fixture["fields"].values())
    return canonical({
        "schema_version": 1,
        "scope": "Finite E8 inputs, exact constructions and source binding; written theorem assembly",
        "sources": sources, "finite_inputs": finite, "primary_factorizations": primary,
        "separate_model": {"root_lines": second["root_lines"],
            "gram_pairing_checks": second["gram_pairing_checks"], "fields": list(second["fields"]),
            "coordinate_fixtures": 32, "additional_eleven_term_fixtures": 4,
            "agreement_on_all_coordinate_profiles": True},
        "actual_basis_cut_audit": {"actual_equality_bases": cuts["basis_count"],
            "root_character_cuts": cuts["root_cut_count"],
            "vanishing_membership_and_copy_checks": cuts["vanishing_membership_and_copy_checks"],
            "false_universal_minimum_basis_controls": {
                field: data["minimum_basis_countercontrol"] for field, data in cuts["fields"].items()}},
        "independent_dimension_relaxation": dimensions,
        "noncoordinate_partial_fixture": partial,
        "cut_excluded_partial_fixture": cut_excluded,
        "strict_basis73_copy72_fixture": strict_fixture,
        "relative_neighbor_threshold": relative,
        "root_low_neighbor_threshold": root_low,
        "nonroot_low_neighbor_threshold": nonroot_low,
        "separate_full_support_stratum_certificate": nonroot_low_second,
        "separate_root_low_plane_certificate": root_low_second,
        "separate_relative_kernel_certificate": relative_second,
        "product_fault_controls": math_faults,
        "actual_space_contract_controls": sum(x["actual_space_contract_controls"] for x in primary.values()),
        "package_sha256": source_hashes(),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="write a local receipt for the exact current sources")
    args = parser.parse_args()
    result_path = PACKAGE / "RESULT.json"
    expected = None
    if not args.emit:
        expected = json.loads(result_path.read_text())
        require(expected.get("package_sha256") == source_hashes(), "receipt source binding differs; explicit re-emit required")
    # -B prevents cache writes, not reads. Route all package imports through a
    # fresh empty namespace so direct and Git-free runs use authenticated source.
    old_prefix, old_write = sys.pycache_prefix, sys.dont_write_bytecode
    with tempfile.TemporaryDirectory(prefix="e8-coupled-pycache-") as cache:
        sys.pycache_prefix = cache
        sys.dont_write_bytecode = True
        try:
            actual = run()
        finally:
            sys.pycache_prefix, sys.dont_write_bytecode = old_prefix, old_write
    if args.emit:
        result_path.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        # Python container equality identifies True with 1. Preserve JSON
        # types as well as mathematical counters in the exact semantic receipt.
        require(json.dumps(actual, sort_keys=True, separators=(",", ":"), allow_nan=False)
                == json.dumps(expected, sort_keys=True, separators=(",", ":"), allow_nan=False),
                "semantic replay receipt differs")
    print("PASS_E8_COUPLED_COORDINATE_FLOOR", json.dumps({
        "roots": 120, "fields": ["Q", "F3", "F5", "F7"],
        "actual_equality_bases": actual["actual_basis_cut_audit"]["actual_equality_bases"],
        "root_cuts": actual["actual_basis_cut_audit"]["root_character_cuts"],
        "relative_nonroot_threshold": 27, "neighbor_support_limit": 28,
        "strict_dimension_cases": 49, "noncoordinate_sharp_fixture": True,
        "receipt_emitted": args.emit,
    }, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_E8_COUPLED_COORDINATE_FLOOR:", error, file=sys.stderr)
        raise SystemExit(1) from error
