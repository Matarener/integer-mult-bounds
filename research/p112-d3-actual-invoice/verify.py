"""Scoped source-bound replay; conorholds, with OpenAI Codex assistance.

Apache-2.0. This verifies declared finite inputs and fixtures. It does not
formalize the written E8 invoice theorem or its predecessor dependencies.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_local(name):
    path = PACKAGE / (name + ".py")
    module = ModuleType("d3_replay_" + name)
    module.__file__ = str(path)
    # Execute these exact package bytes. Ambient module paths and existing
    # bytecode caches cannot substitute a different scientific implementation.
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def package_hashes():
    return {path.relative_to(PACKAGE).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in sorted(PACKAGE.rglob("*"))
            if path.is_file() and path.name != "RESULT.json"
            and "__pycache__" not in path.parts and path.suffix != ".pyc"}


def source_geometry():
    source = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [row for row in source["files"] if row["usage"] == "input"]
    require(len(inputs) == 1, "unexpected scientific live-input inventory")
    row = inputs[0]
    require(row["path"] == "research/p112-root-simplex-exclusion/geometry.py",
            "unexpected root geometry input")
    path = ROOT / row["path"]
    require(sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "live geometry source hash mismatch")
    return path


def rejected(name, action, expected):
    try:
        result = action()
    except ValueError as error:
        require(expected in str(error), f"{name}: wrong rejection: {error}")
        return {"mutation": name, "detected": True, "reason": str(error)}
    require(isinstance(result, dict) and result.get("status") == "failure",
            name + ": semantic mutation was not rejected")
    require("counterexample" in result, name + ": no geometric counterexample")
    return {"mutation": name, "detected": True,
            "counterexample": result["counterexample"],
            "rank": result["binary_rank"]}


def compute():
    geometry = source_geometry()
    profiles = load_local("profiles")
    frame = load_local("frame_pair_geometry")
    matched = load_local("matched_plane")
    actual = load_local("actual_d3_fixture")
    union = load_local("flat_union")
    canonical = load_local("canonical_union")
    arithmetic = profiles.report()
    frame_receipt = frame.checks(geometry)
    matched_receipt = matched.checks(geometry, "all", 50000)
    require(matched_receipt["status"] == "pass", "G4 exhaustive check failed")
    union_receipt = union.checks(geometry, PACKAGE / "frame_pair_geometry.py", True, True)
    require(union_receipt["status"] == "pass", "double-seven geometry check failed")
    canonical_receipt = canonical.checks()
    require({str(k): v for k, v in canonical_receipt["section_root_histogram"].items()}
            == union_receipt["census"]["all_sections"]["full_root_histogram"],
            "independent section spectra disagree")
    require({str(k): v for k, v in canonical_receipt["maximal_pair_intersection_histogram"].items()}
            == union_receipt["pairs"]["intersection_histogram"],
            "independent maximal-pair spectra disagree")
    require(union_receipt["universal_double_seven_full_union_bound"]
            == canonical_receipt["universal_union_bound"],
            "independent universal-union inferences disagree")
    fixture = actual.fixture(geometry, True, 4096, check_omitted_low=True)
    require(fixture["status"] == "pass" and fixture["true_T_certified"],
            "the actual nonadapted d3 positive fixture is uncertified")
    require((fixture["dimension_S"], fixture["dimension_T"],
             fixture["code_intersection_dimension"], fixture["r"],
             fixture["raw_weight_sum"], fixture["invoice"]) == (11, 6, 3, 1, 84, 83),
            "actual positive-control identity changed")
    controls = []
    for mutation, expected in (
            ("matched-live-label", "matched hyperplane is ker b_a"),
            ("common-ratio-sign", "common-neighbor ratio split"),
            ("omit-live-root", "56 live frame neighbors"),
            ("generic-coefficient", "wrong characteristic-zero support stratum")):
        controls.append(rejected("frame-" + mutation,
                                 lambda m=mutation: frame.checks(geometry, m), expected))
    controls.append(rejected("G4-matched-live-label",
                             lambda: matched.checks(geometry, mutation="matched-live-label"),
                             "unused: this control must exhibit a geometric counterexample"))
    controls.append(rejected("double-seven-wrong-normal-coset",
                             lambda: union.checks(geometry, PACKAGE / "frame_pair_geometry.py",
                                                  mutation="wrong-normal-coset"),
                             "third normal equation fails"))
    controls.append(rejected("canonical-wrong-mixed-coset",
                             lambda: canonical.checks("wrong-mixed-coset"),
                             "mixed fixture sections overlap in 16 roots"))
    return {
        "schema_version": 1,
        "status": "pass",
        "scope": "finite inputs and actual-basis controls; written invoice proof not formalized",
        "package_sha256": package_hashes(),
        "profile_arithmetic": arithmetic,
        "frame_pair_geometry": frame_receipt,
        "matched_two_axis_G4": matched_receipt,
        "actual_nonadapted_d3_fixture": fixture,
        "geometry_failure_controls": controls,
        "double_seven_full_root_union": union_receipt,
        "independent_canonical_union": canonical_receipt,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true",
                        help="regenerate this package's deterministic scientific receipt")
    args = parser.parse_args()
    # Compare the canonical JSON data model: JSON represents tuple values as
    # arrays and integer object keys as strings. This preserves every field
    # while avoiding a Python-container mismatch after a receipt round trip.
    result = json.loads(json.dumps(compute(), sort_keys=True))
    path = PACKAGE / "RESULT.json"
    if args.emit:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(path.is_file(), "missing RESULT.json; explicitly generate with --emit")
        expected = json.loads(path.read_text())
        require(result == expected, "scientific receipt or package bytes differ from RESULT.json")
    arithmetic = result["profile_arithmetic"]
    matched = result["matched_two_axis_G4"]
    summary = {
        "nonadapted_occurrences": arithmetic["actual_profile_occurrences"],
        "adapted_t2_profiles": arithmetic["adapted_t2_arithmetic"]["actual_profile_count"],
        "adapted_t3_high": arithmetic["adapted_t3_arithmetic"]["high_actual_candidate_count"],
        "adapted_t3_low": len(arithmetic["adapted_t3_arithmetic"][
            "all_low_actual_profiles_through_sum32"]),
        "maximal_section_pairs": result["double_seven_full_root_union"][
            "pairs"]["unordered_distinct_section_pairs"],
        "G4": matched["residual_checks"],
        "direct_deletions": matched["direct_deletions"]["individual_deletions"],
        "true_T_flats": result["actual_nonadapted_d3_fixture"][
            "low_space_certificate"]["counts"]["all_rank7_flats"],
    }
    print("PASS_P112_D3_ACTUAL_INVOICE "
          + " ".join(f"{key}={value}" for key, value in summary.items())
          + " scope=finite-inputs-and-controls")


if __name__ == "__main__":
    main()
