#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare separately reconstructed source certificates to the committed result.

Clear1nsight, substantial OpenAI assistance. No native or supplier admission.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def parse(text):
    return json.loads(text, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def strict_equal(left, right):
    need(canonical(left) == canonical(right), "typed scientific receipt differs")


def execute(script, prefix):
    command = [sys.executable, "-I", "-B"]
    if sys.flags.optimize:
        command.append("-O")
    command.append(str(HERE / script))
    run = subprocess.run(command, check=True, capture_output=True, text=True, timeout=120)
    rows = [line[len(prefix):] for line in run.stdout.splitlines() if line.startswith(prefix)]
    need(len(rows) == 1, "one substantive result from " + script)
    return parse(rows[0])


def project(primary, other):
    need(primary["source_mode"] == "authenticated archive and credited PR3071 extractor", "primary archive mode")
    need(other["source_mode"] == "independently parsed pinned archive", "independent archive mode")
    need(other["status"] == "PASS_INDEPENDENT_CENTRE_SHEAF", "independent pass marker")
    need(primary["status"] == "PASS_CENTRE_SHEAF_FIBRE", "primary pass marker")
    strict_equal(other["right_coset_classes"], [row["ports"] for row in primary["right_coset_classes"]])
    for key in ("owners", "geometry_sha256", "class_size_histogram"):
        strict_equal(primary[key], other[key])
    need(primary["old_rank"] == other["old_rank_mod101"] * other["owners"], "old-rank agreement")
    need(primary["full_joint_kernel_dimension"] == other["joint_kernel_dimension"], "kernel agreement")
    need(primary["additional_linear_observations_required"] == other["additional_linear_observations"], "observation agreement")
    need(primary["spanning_tree_edges"] == other["compatibility_rank"], "graph-rank agreement")
    keys = ("owners", "ports", "active_dimension", "full_variables", "old_rank", "old_kernel_dimension",
            "full_joint_kernel_dimension", "additional_linear_observations_required", "class_size_histogram",
            "deficient_coset_classes", "compatibility_vertices", "compatibility_edges", "spanning_tree_edges",
            "spanning_tree_sha256", "subgroup_sha256", "geometry_sha256", "primitive_move_positive_entries",
            "primitive_move_negative_entries", "primitive_move_support", "constant_count_constraint_kills_kernel")
    result = {key: primary[key] for key in keys}
    result.update(schema_version=1, status="PASS_CENTRE_SHEAF_COMMITTED_RECEIPT",
                  right_coset_classes_sha256=sha256(canonical(primary["right_coset_classes"])).hexdigest(),
                  right_coset_class_count=len(primary["right_coset_classes"]),
                  independent_old_rank_mod101=other["old_rank_mod101"],
                  independent_nonzero_later_residuals=other["nonzero_later_residuals"],
                  independent_dropped_owner_nonzero_outputs=other["dropped_owner_nonzero_outputs"])
    return result


def controls(reference):
    strict_equal(reference, deepcopy(reference))
    variants = []
    for field, value in (("full_joint_kernel_dimension", True), ("owners", 4079),
                         ("additional_linear_observations_required", 424318),
                         ("constant_count_constraint_kills_kernel", 1),
                         ("independent_dropped_owner_nonzero_outputs", 0)):
        mutant = deepcopy(reference)
        mutant[field] = value
        variants.append(mutant)
    mutant = deepcopy(reference)
    mutant["class_size_histogram"]["1"] = 108
    variants.append(mutant)
    for mutant in variants:
        try:
            strict_equal(reference, mutant)
        except ValueError:
            pass
        else:
            raise ValueError("receipt mutant was accepted")
    for text in ('{"a":1,"a":1}', '{"a":NaN}'):
        try:
            parse(text)
        except ValueError:
            pass
        else:
            raise ValueError("malformed JSON accepted")
    return len(variants) + 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls-only", action="store_true", help="Typed fixture checks only; no source replay")
    args = parser.parse_args()
    path = HERE / "RESULT.json"
    need(path.is_file() and not path.is_symlink(), "regular committed result")
    reference = parse(path.read_text())
    count = controls(reference)
    if args.controls_only:
        print("PASS_GENERIC_TYPED_RECEIPT_CONTROLS", count, "source_replay=false")
        return
    primary = execute("verify.py", "RESULT_JSON=")
    other = execute("independent.py", "INDEPENDENT_JSON=")
    actual = project(primary, other)
    strict_equal(actual, reference)
    print("RESULT_JSON=" + canonical(actual).decode())
    print("PASS_CENTRE_SHEAF_COMMITTED_RECEIPT", "controls=" + str(count),
          "optimised=" + str(bool(sys.flags.optimize)), "sha256=" + sha256(canonical(actual)).hexdigest())


if __name__ == "__main__":
    main()
