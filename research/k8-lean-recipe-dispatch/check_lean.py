#!/usr/bin/env python3
"""Fresh Lean replay of the source-bound forward recipe dispatcher.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0

Read-only dependency replay follows PR3357 and Nick Petalas's PR2944 driver.
"""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
import generate

HERE, ROOT = source.HERE, source.ROOT
TOOLCHAIN = "leanprover/lean4:v4.21.0"
MATHLIB_REV = "308445d7985027f538e281e18df29ca16ede2ba3"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
ROOTS = ["K8RecipeDispatch.dispatch_exact", "K8RecipeDispatch.block_recipes_exact",
         "K8RecipeDispatch.block_raw_binding", "K8RecipeDispatch.rawRelabels_flatten",
         "K8.RecipeBinding.used_child_count", "K8.RecipeBinding.forward_dispatch_bound",
         "K8.RecipeBinding.forward_recipes_exact"]
CONTROL_ROOTS = ["DispatchControls." + name for name in (
    "source_route", "source_inverse_descriptor_rejected", "unbound_child_rejected",
    "identity_route", "prew450_codec", "wrong_stride_rejected", "wrong_terminal_rejected",
    "source_value", "inverse_value", "pre_order_value", "reversed_order_value",
    "child_order_value", "reversed_child_order_value")]
PACKAGE_FILES = ("source.py", "generate.py", "check_lean.py", "verify.py", "test_dispatch.py",
                 "K8RecipeDispatch.lean", "ForwardRecipeResult.lean",
                 "DispatchControls.lean", "SOURCE-DISPATCH.json", "SOURCES.json", "VERIFY.json")
FROZEN = {"LemmaG/Stream.lean": "research/e8-lemma-g-lean/LemmaG/Stream.lean",
          "TreeCheckpoint.lean": "research/k8-lean-label-instance/TreeCheckpoint.lean"}

REJECTS = {
    "source_inverse": "example : dispatch tables model 1006 2 (1,2) = (-1,2) := by\n"
                      "  rw [source_value]\n  decide +kernel\n",
    "operator_order": "example : tagOp tables model 1006 (1,2) = (2,-1) := by\n"
                      "  rw [pre_order_value]\n  decide +kernel\n",
    "terminal_frame": "example : transitionOK tables (decode 2) "
                      "(decode (999 + 1004*(1+450+712*3))) = true := by\n"
                      "  rw [wrong_terminal_rejected]\n  decide +kernel\n",
    "child_order": "example : evalRecipe childModel (.child ⟨0,2,7,8⟩) "
                   "(1,2) = (2,3) := by\n"
                   "  rw [child_order_value]\n  decide +kernel\n",
}


def axiom_source():
    return ("import ForwardRecipeResult\nimport DispatchControls\n" +
            "\n".join("#print axioms " + name for name in ROOTS + CONTROL_ROOTS) + "\n")

def command_result(command, directory, environment, timeout=180):
    source.require(os.name == "posix", "POSIX process groups are required")
    with subprocess.Popen(command, cwd=directory, env=environment, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          start_new_session=True) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=10)


def environment_for(project, inputs):
    project = Path(project).resolve()
    toolchain_bytes = (project / "lean-toolchain").read_bytes()
    toolchain = toolchain_bytes.decode().strip()
    source.require(toolchain_bytes == inputs["formal/lean/lean-toolchain"],
                   "cache toolchain differs from pinned source")
    source.require(toolchain == TOOLCHAIN, "Lean toolchain must be 4.21.0")
    manifest_bytes = (project / "lake-manifest.json").read_bytes()
    source.require(manifest_bytes == inputs["formal/lean/lake-manifest.json"],
                   "cache manifest differs from pinned source")
    manifest = source.decoded(manifest_bytes)
    packages = manifest["packages"]
    mathlib = [package for package in packages if package["name"] == "mathlib"]
    source.require(len(mathlib) == 1 and mathlib[0]["rev"] == MATHLIB_REV,
                   "Mathlib must match v4.21.0")
    package_root = project / manifest.get("packagesDir", ".lake/packages")
    for package in packages:
        head = command_result(["git", "rev-parse", "HEAD"], package_root / package["name"],
                              os.environ.copy(), 30)
        source.require(head.returncode == 0 and head.stdout.strip() == package["rev"],
                       "dependency checkout changed: " + package["name"])
    libraries = sorted((package_root / package["name"] / ".lake/build/lib/lean").resolve()
                       for package in packages
                       if (package_root / package["name"] / ".lake/build/lib/lean").is_dir())
    source.require((package_root / "mathlib/.lake/build/lib/lean/Mathlib").is_dir(),
                   "Mathlib compiled cache is missing; no download or build is attempted")
    elan_home = Path(os.environ.get("ELAN_HOME", str(Path.home() / ".elan")))
    lean = elan_home / "toolchains/leanprover--lean4---v4.21.0/bin/lean"
    source.require(lean.is_file(), "installed Lean 4.21.0 binary is missing")
    environment = dict(os.environ)
    for key in ("LEAN_PATH", "LEAN_SYSROOT", "LEAN_SRC_PATH", "PYTHONPATH", "PYTHONHOME"):
        environment.pop(key, None)
    version = command_result([str(lean), "--version"], project, environment, 30)
    source.require(version.returncode == 0 and "version 4.21.0" in version.stdout,
                   "wrong Lean compiler version")
    metadata = {"toolchain": toolchain, "lake_manifest_sha256": source.digest(manifest_bytes),
                "package_revisions": {package["name"]: package["rev"] for package in packages},
                "lean": version.stdout.strip()}
    return lean.resolve(), environment, libraries, metadata


def compile_file(path, temporary, lean, environment):
    command = [str(lean), "--root=" + str(temporary), "-j1", "-DwarningAsError=true",
               "-o", str(path.with_suffix(".olean")), str(path)]
    result = command_result(command, temporary, environment)
    source.require(result.returncode == 0,
                   str(path.relative_to(temporary)) + " failed:\n" +
                   (result.stdout + result.stderr)[-6000:])
    print("CHECKED " + str(path.relative_to(temporary)), flush=True)
    return result.stdout + result.stderr


def axiom_reports(output, expected):
    reports = {}
    for name, axioms in re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]", output):
        reports[name] = sorted(set(axioms.replace(" ", "").replace("\n", "").split(",")) - {""})
    for name in re.findall(r"'([^']+)' does not depend on any axioms", output):
        reports[name] = []
    source.require(set(reports) == set(expected), "missing or unexpected live axiom root")
    for name, axioms in reports.items():
        source.require(set(axioms) <= ALLOWED_AXIOMS, "unexpected axiom: " + name)
    return reports


def validate_proof_source(data, name):
    text = re.sub(r"/-.*?-/", " ", data.decode(), flags=re.S)
    text = re.sub(r"--[^\n]*", " ", text)
    forbidden = re.search(r"\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern)\b", text)
    source.require(forbidden is None, "forbidden proof token in " + name)


def negative_controls(temporary, lean, environment):
    hashes = {}
    for name, body in REJECTS.items():
        path = temporary / ("Reject_" + name + ".lean")
        path.write_text("import DispatchControls\nopen K8RecipeDispatch DispatchControls\n" + body)
        result = command_result([str(lean), "--root=" + str(temporary), "-j1",
                                 "-DwarningAsError=true", str(path)], temporary, environment, 60)
        diagnostic = result.stdout + result.stderr
        source.require(result.returncode != 0 and "decide" in diagnostic and "false" in diagnostic,
                       "false kernel claim was not rejected: " + name + "\n" + diagnostic[-2000:])
        print("REJECTED " + path.name, flush=True)
        hashes[path.name] = source.digest(path.read_bytes())
    return hashes


def run(project, work_dir=None):
    inputs = source.authenticate()
    package = {name: (HERE / name).read_bytes() for name in PACKAGE_FILES}
    lean, environment, libraries, metadata = environment_for(project, inputs)
    if work_dir is not None:
        source.require(Path(work_dir).is_dir(), "--work-dir must exist")
    with tempfile.TemporaryDirectory(prefix="k8-recipe-dispatch-", dir=work_dir) as directory:
        temporary = Path(directory).resolve()
        environment["LEAN_PATH"] = os.pathsep.join(map(str, [temporary] + libraries))
        for name, origin in FROZEN.items():
            path = temporary / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(inputs[origin])
            compile_file(path, temporary, lean, environment)
        for name in ("K8RecipeDispatch.lean", "ForwardRecipeResult.lean", "DispatchControls.lean"):
            validate_proof_source(package[name], name)
            (temporary / name).write_bytes(package[name])
        compile_file(temporary / "K8RecipeDispatch.lean", temporary, lean, environment)
        retained, binding = source.emit_existing(temporary)
        generated, dispatch_binding = generate.emit(temporary)
        for path in retained + generated:
            compile_file(path, temporary, lean, environment)
        compile_file(temporary / "ForwardRecipeResult.lean", temporary, lean, environment)
        compile_file(temporary / "DispatchControls.lean", temporary, lean, environment)
        control_hashes = negative_controls(temporary, lean, environment)
        path = temporary / "PrintAxioms.lean"
        path.write_text(axiom_source())
        reports = axiom_reports(compile_file(path, temporary, lean, environment),
                                ROOTS + CONTROL_ROOTS)
        generated_hashes = {p.name: source.digest(p.read_bytes()) for p in generated + [path]}
    source.require(source.authenticate() == inputs, "inputs changed during Lean replay")
    source.require(all((HERE / name).read_bytes() == data for name, data in package.items()),
                   "package sources changed during Lean replay")
    return {"status": "PASS_K8_RECIPE_DISPATCH_KERNEL", "environment": metadata,
            "axioms": reports, "generated_sha256": generated_hashes,
            "control_sources_sha256": control_hashes, "rejected": sorted(REJECTS),
            "retained_sha256": binding["generated_sha256"],
            "binding": binding, "dispatch_binding": dispatch_binding,
            "inputs": {name: source.digest(data) for name, data in inputs.items()},
            "package_sha256": {name: source.digest(data) for name, data in package.items()},
            "scope": "Conditional RecipesExact for the complete retained forward word. "
                     "Used child identities and physical execution remain explicit."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake-project", type=Path, default=ROOT / "formal/lean")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    if args.write_receipt:
        source.require(not args.write_receipt.exists(), "receipt output already exists")
    began = time.monotonic()
    result = run(args.lake_project, args.work_dir)
    if args.write_receipt:
        with args.write_receipt.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = source.decoded((HERE / "KERNEL.json").read_bytes())
        actual_core, expected_core = dict(result), dict(expected)
        actual_core["environment"] = dict(result["environment"], lean="platform metadata")
        expected_core["environment"] = dict(expected["environment"], lean="platform metadata")
        source.require(actual_core == expected_core, "kernel receipt mismatch")
    print(result["status"] + " roots=" + str(len(result["axioms"])) +
          f" elapsed_seconds={time.monotonic() - began:.1f}")


if __name__ == "__main__":
    main()
