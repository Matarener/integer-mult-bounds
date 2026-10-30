#!/usr/bin/env python3
"""Bounded replay of the marked d=0 proof inputs and actual-decoder controls.

Prepared by conorholds, with substantial OpenAI Codex assistance. Apache-2.0.
The mathematical theorem is in PROOF.md; replay is not a proof assistant.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_receipt(receipt, actual):
    # Python equality identifies True,1 and1.0. A scientific receipt must
    # retain JSON types as well as values; object-key order is immaterial.
    def canonical(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    require(canonical(receipt) == canonical(actual), "committed scientific receipt differs")


def receipt_controls():
    expected = {"nested": [{"count": 1}]}
    check_receipt(json.loads('{"nested":[{"count":1}]}'), expected)
    for wrong in (True, 1.0, "1", 2):
        try:
            check_receipt({"nested": [{"count": wrong}]}, expected)
        except ValueError:
            continue
        raise ValueError("receipt accepted a wrong count or JSON type")
    return {"integer_positive": True, "boolean_float_string_wrong_count_rejected": True}


def load_source(name, path):
    """Execute authenticated source bytes without reading any .pyc cache."""
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def run():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "live input source hash mismatch: " + row["path"])
    predecessor = ROOT / "research/e8-d0-root-swaps"
    old_geometry = load_source("geometry_audit", predecessor / "geometry_audit.py")
    extension = load_source("marked_predecessor_extension", predecessor / "extension_check.py")
    algebra = load_source("marked_predecessor_algebra", predecessor / "verify.py")
    geometry = load_source("marked_geometry", PACKAGE / "geometry.py")
    independent = load_source("marked_independent", PACKAGE / "independent.py")
    fixtures = load_source("marked_fixtures", PACKAGE / "fixtures.py")
    independent_fixture = load_source("marked_independent_fixture", PACKAGE / "independent_fixture.py")
    sharp_control = load_source("marked_sharp_control", PACKAGE / "sharp_control.py")
    inherited_geometry = old_geometry.run_audit()
    inherited_extension = extension.run_checks()
    model = old_geometry.CartanModel()
    first = geometry.check(model, old_geometry.binary_rank)
    independent_model = independent.Checks("full", 60)
    second = independent_model.run("all")
    second.pop("elapsed_seconds")
    require(second["full_finite_coverage"], "independent checker did not complete its domain")
    independent_results = second["results"]
    require(independent_results["carrier_triples"]["triples"] == first["carrier_triples"],
            "carrier triple algorithms disagree")
    require(independent_results["restricted_axes"]["minimum_cuts"]
            == {1: 24, 2: 34, 3: 28}, "independent carrying minima disagree")
    # Bind both algorithms to the same root lines, fixed frame and binary
    # matroid. Rank nine of the label graph proves a linear isomorphism of
    # their two nine-dimensional label spaces, not just agreement of minima.
    mapping, signs = [], []
    for root in model.roots:
        raw = model.to_doubled(root)
        canonical = old_geometry.canonical(raw)
        require(canonical in independent_model.index, "independent root inventory differs")
        mapping.append(independent_model.index[canonical])
        signs.append(1 if tuple(raw) == canonical else -1)
    require(len(set(mapping)) == 120, "root-line map is not a bijection")
    require({mapping[i] for i in model.frame} == set(independent_model.frame_ids),
            "the two models puncture different frames")
    graph = [label | (independent_model.labels[mapping[i]] << 9)
             for i, label in enumerate(model.labels)]
    require(old_geometry.binary_rank(model.labels)
            == independent.binary_rank(independent_model.labels) == 9,
            "both label projections must have rank nine")
    require(old_geometry.binary_rank(graph) == 9, "label matroids are not linearly isomorphic")
    for i in range(120):
        for j in range(120):
            require(4 * signs[i] * signs[j] * model.gram[i][j]
                    == independent_model.dots[mapping[i]][mapping[j]], "root Gram isometry fails")
    actual = fixtures.run(model, algebra)
    other_fixture = independent_fixture.run(independent)
    independent_sharp = sharp_control.run(independent, independent_fixture)
    expected_paid = {"invoice": 64, "epsilon": 1, "pivot_cost": 1,
                     "actual_cost": 64, "rank_P": 9, "rank_Q": 11}
    for field, value in expected_paid.items():
        require(actual["paid_pivot_sharp"][field] == other_fixture["paid_pivot_sharp"][field]
                == value, "paid-pivot equality algorithms disagree: " + field)
    require(actual["paid_pivot_sharp"]["actual_nonpivot_cost"] == 63,
            "paid equality control does not need its pivot toll")
    scientific = {str(path.relative_to(PACKAGE)): sha256(path.read_bytes()).hexdigest()
                  for path in sorted(PACKAGE.rglob("*"))
                  if path.is_file() and path.suffix in (".py", ".md", ".lean")}
    return {"schema_version": 1, "inherited_geometry": inherited_geometry,
            "inherited_extension": inherited_extension, "cartan_new_geometry": first,
            "independent_gram_geometry": second, "actual_factorization_controls": actual,
            "independent_omitted_witness_control": other_fixture,
            "independent_sharp_actual_controls": independent_sharp,
            "coordinate_binding": {"root_bijection": 120, "same_frame": 8,
                                   "label_graph_rank": 9, "gram_pairs": 14400},
            "receipt_controls": receipt_controls(),
            "scientific_sha256": scientific}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="write the deterministic result receipt")
    args = parser.parse_args()
    try:
        result = json.loads(json.dumps(run(), sort_keys=True))
        path = PACKAGE / "RESULT.json"
        if args.emit:
            path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        else:
            require(path.exists(), "missing RESULT.json; generate it explicitly with --emit")
            check_receipt(json.loads(path.read_text()), result)
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print("FAIL_MARKED_D0_INVOICE: " + str(error), file=sys.stderr)
        return 1
    print("PASS_MARKED_D0_INVOICE inputs=authenticated geometry=two-algorithms "
          "actual_factorizations=11 independent_sharp_actuals=3 marked_witness_counterexample=1 "
          "scope=finite-inputs-and-controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
