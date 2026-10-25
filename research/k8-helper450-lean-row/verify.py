#!/usr/bin/env python3
"""Check source bindings and the retained Lean receipt; no fresh Lean invocation.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

import argparse
from pathlib import Path
import json
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source

ROOTS = {
    "Helper450Row.inverse_adds_restore", "Helper450Row.inverse_adds_unit_row",
    "Helper450Concrete.helper450_restored", "Helper450Concrete.helper450_unit_row",
    "Helper450Concrete.helper450_hS",
}
PACKAGE_FILES = {"source.py", "check_lean.py", "Helper450Row.lean", "Helper450Concrete.lean"}
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def compute():
    inputs = {name: source.digest(data) for name, data in source.authenticate().items()}
    with tempfile.TemporaryDirectory(prefix="helper450-replay-") as directory:
        _, result = source.emit_existing(directory)
    kernel = source.decoded((source.HERE / "KERNEL.json").read_bytes())
    source.require(kernel["status"] == "PASS_K8_HELPER450_LEAN_KERNEL", "kernel status")
    source.require(kernel["inputs"] == inputs, "kernel source input binding")
    source.require(kernel["generated_sha256"] == result["generated_sha256"],
                   "kernel generated source binding")
    package_hashes = kernel["package_sha256"]
    source.require(PACKAGE_FILES <= package_hashes.keys(), "kernel package inventory")
    for name, expected in package_hashes.items():
        source.require(Path(name).name == name, "kernel package path")
        source.require(source.digest((source.HERE / name).read_bytes()) == expected,
                       "kernel package source changed: " + name)
    source.require(ROOTS <= kernel["axioms"].keys(), "missing theorem roots")
    source.require(set(kernel["control_axioms"]) == {
        "Controls." + name for name in ("wrong_sign_value", "clear_partner_value",
                                        "alias_value", "relabel_row", "row_not_column")
    }, "missing kernel control roots")
    source.require(kernel["controls"] == {
        "rejected": ["alias_source", "clear_partner", "wrong_sign"],
        "positive": ["relabel_row", "row_not_column"]
    }, "kernel control inventory")
    for name, axioms in (kernel["axioms"] | kernel["control_axioms"]).items():
        source.require(set(axioms) <= ALLOWED_AXIOMS, "unapproved axioms: " + name)
    source.require(inputs == {n: source.digest(d) for n, d in source.authenticate().items()},
                   "inputs changed during replay")
    return dict(result, status="PASS_K8_HELPER450_LEAN_ROW_BINDING", inputs=inputs,
                kernel_receipt_sha256=source.digest(source.encoded(kernel)),
                fresh_lean_build=False,
                scope="Forward scalar output row450 of the exact retained typed word. "
                      "No column isolation, physical recipe or full supplier claim.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.write_result:
        with args.write_result.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = source.decoded((source.HERE / "RESULT.json").read_bytes())
        source.require(result == expected, "result receipt mismatch")
    print(result["status"] + " events=24757 registers=1024 fresh_lean_build=false")


if __name__ == "__main__":
    main()
