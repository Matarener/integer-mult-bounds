#!/usr/bin/env python3
"""Rebind the archived kernel receipt; this command does not invoke Lean.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
import generate
import check_lean


def compute():
    inputs = {name: source.digest(data) for name, data in source.authenticate().items()}
    with tempfile.TemporaryDirectory(prefix="k8-recipe-rebind-") as directory:
        _, retained = source.emit_existing(directory)
        paths, binding = generate.emit(directory)
        generated = {path.name: source.digest(path.read_bytes()) for path in paths}
    generated["PrintAxioms.lean"] = source.digest(check_lean.axiom_source().encode())
    kernel = source.decoded((source.HERE / "KERNEL.json").read_bytes())
    source.require(kernel["status"] == "PASS_K8_RECIPE_DISPATCH_KERNEL", "kernel status")
    source.require(kernel["inputs"] == inputs, "kernel input binding")
    source.require(kernel["binding"] == retained, "retained word binding")
    source.require(kernel["retained_sha256"] == retained["generated_sha256"],
                   "retained module inventory")
    source.require(kernel["dispatch_binding"] == binding, "recipe dispatch binding")
    source.require(kernel["generated_sha256"] == generated, "generated proof source binding")
    package = {name: source.digest((source.HERE / name).read_bytes())
               for name in check_lean.PACKAGE_FILES}
    source.require(kernel["package_sha256"] == package, "kernel package source binding")
    roots = check_lean.ROOTS + check_lean.CONTROL_ROOTS
    source.require(set(kernel["axioms"]) == set(roots), "kernel theorem/control roots")
    for name, axioms in kernel["axioms"].items():
        source.require(set(axioms) <= check_lean.ALLOWED_AXIOMS, "unapproved axioms: " + name)
    prefix = "import DispatchControls\nopen K8RecipeDispatch DispatchControls\n"
    controls = {"Reject_" + name + ".lean": source.digest((prefix + body).encode())
                for name, body in check_lean.REJECTS.items()}
    source.require(kernel["control_sources_sha256"] == controls, "false claim source binding")
    source.require(kernel["rejected"] == sorted(check_lean.REJECTS), "false claim inventory")
    source.require(inputs == {name: source.digest(data)
                              for name, data in source.authenticate().items()},
                   "inputs changed during replay")
    return {"status": "PASS_K8_RECIPE_DISPATCH_BINDING", "inputs": inputs,
            "retained": retained, "dispatch": binding,
            "kernel_receipt_sha256": source.digest(source.encoded(kernel)),
            "fresh_lean_build": False,
            "scope": "Ordered source-bound dispatch and conditional forward RecipesExact; "
                     "used child identities and serialized operator denotation remain open."}


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
    print(result["status"] + " relabels=5064 children=2888 fresh_lean_build=false")


if __name__ == "__main__":
    main()
