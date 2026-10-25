#!/usr/bin/env python3
"""Fresh direct Lean replay using an existing, read-only Mathlib cache.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0

Process cleanup and axiom checks follow Nick Petalas's retained PR2944 driver;
this driver invokes Lean directly and never runs Lake or updates dependencies.
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


HERE, ROOT = source.HERE, source.ROOT
TOOLCHAIN = "leanprover/lean4:v4.21.0"
MATHLIB_REV = "308445d7985027f538e281e18df29ca16ede2ba3"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
ROOTS = ["Helper450Row.inverse_adds_restore", "Helper450Row.inverse_adds_unit_row",
         "Helper450Concrete.helper450_restored", "Helper450Concrete.helper450_unit_row",
         "Helper450Concrete.helper450_hS"]
CONTROL_ROOTS = ["Controls." + name for name in
                 ("wrong_sign_value", "clear_partner_value", "alias_value",
                  "relabel_row", "row_not_column")]
PACKAGE_FILES = ("source.py", "check_lean.py", "Helper450Row.lean",
                 "Helper450Concrete.lean", "SOURCES.json")
FROZEN = {"LemmaG/Stream.lean": "research/e8-lemma-g-lean/LemmaG/Stream.lean",
          "TreeCheckpoint.lean": source.LABEL + "TreeCheckpoint.lean",
          "StreamShadowRowUpdate.lean":
              "research/stream-shadow-row-update/StreamShadowRowUpdate.lean"}

CONTROLS = """import Helper450Row
import Mathlib.Algebra.Field.Rat
namespace Controls
open LemmaG LemmaG.Stream
abbrev E := Event (Fin 3) Nat Rat
def wrongSign : List E := [.add 0 1 1, .add 0 1 1]
def clearPartner : List E := [.add 0 1 1, .clear 1 0, .add 0 1 (-1)]
def aliasSource : List E := [.add 0 0 1, .add 0 0 (-1)]
def relabels : List E := [.relabel 0 4 7, .add 0 1 1,
  .relabel 1 8 9, .add 0 1 (-1), .relabel 0 7 11]
def leakage : List E := [.add 1 0 1]
theorem wrong_sign_value : S wrongSign 0 1 = 2 := by decide +kernel
theorem clear_partner_value : S clearPartner 0 1 = 1 := by decide +kernel
theorem alias_value : S aliasSource 0 0 = 0 := by decide +kernel
theorem relabel_row : ∀ j : Fin 3,
    S relabels 0 j = if j = 0 then 1 else 0 := by decide +kernel
theorem row_not_column :
    (∀ j : Fin 3, S leakage 0 j = if j = 0 then 1 else 0) ∧
    S leakage 1 0 = 1 := by decide +kernel
end Controls
"""
NEGATIVE_CONTROLS = {
    "wrong_sign": ("S Controls.wrongSign 0 1 = 0", "wrong_sign_value"),
    "clear_partner": ("S Controls.clearPartner 0 1 = 0", "clear_partner_value"),
    "alias_source": ("S Controls.aliasSource 0 0 = 1", "alias_value")}


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


def write_sources(temporary, inputs, package):
    paths = []
    for name, origin in FROZEN.items():
        path = temporary / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(inputs[origin])
        paths.append(path)
    for name in ("Helper450Row.lean", "Helper450Concrete.lean"):
        validate_proof_source(package[name], name)
        (temporary / name).write_bytes(package[name])
    return paths


def controls(temporary, lean, environment):
    path = temporary / "Controls.lean"
    path.write_text(CONTROLS)
    compile_file(path, temporary, lean, environment)
    digests = {path.name: source.digest(path.read_bytes())}
    for name, (statement, value_theorem) in NEGATIVE_CONTROLS.items():
        path = temporary / ("Reject_" + name + ".lean")
        path.write_text("import Controls\nopen LemmaG LemmaG.Stream\n" +
                        "example : " + statement + " := by\n" +
                        "  rw [Controls." + value_theorem + "]\n  decide +kernel\n")
        result = command_result([str(lean), "--root=" + str(temporary), "-j1",
                                 "-DwarningAsError=true", str(path)], temporary, environment, 60)
        diagnostic = result.stdout + result.stderr
        source.require(result.returncode != 0 and "decide" in diagnostic and "false" in diagnostic,
                       "false kernel claim was not rejected: " + name + "\n" + diagnostic[-2000:])
        print("REJECTED " + path.name, flush=True)
        digests[path.name] = source.digest(path.read_bytes())
    return digests


def replay(temporary, lean, environment, inputs, package):
    frozen = write_sources(temporary, inputs, package)
    generated, binding = source.emit_existing(temporary)
    for path in frozen + generated + [temporary / "Helper450Row.lean",
                                      temporary / "Helper450Concrete.lean"]:
        compile_file(path, temporary, lean, environment)
    control_hashes = controls(temporary, lean, environment)
    path = temporary / "PrintAxioms.lean"
    path.write_text("import Helper450Concrete\nimport Controls\n" +
                    "\n".join("#print axioms " + name for name in ROOTS + CONTROL_ROOTS) + "\n")
    reports = axiom_reports(compile_file(path, temporary, lean, environment), ROOTS + CONTROL_ROOTS)
    control_hashes[path.name] = source.digest(path.read_bytes())
    return reports, control_hashes, binding


def run(project, work_dir=None):
    inputs = source.authenticate()
    package = {name: (HERE / name).read_bytes() for name in PACKAGE_FILES}
    lean, environment, libraries, metadata = environment_for(project, inputs)
    if work_dir is not None:
        source.require(Path(work_dir).is_dir(), "--work-dir must be an existing directory")
    with tempfile.TemporaryDirectory(prefix="k8-helper450-lean-", dir=work_dir) as directory:
        temporary = Path(directory).resolve()
        environment["LEAN_PATH"] = os.pathsep.join(map(str, [temporary] + libraries))
        reports, control_hashes, binding = replay(temporary, lean, environment, inputs, package)
    source.require(source.authenticate() == inputs, "inputs changed during Lean replay")
    source.require(all((HERE / name).read_bytes() == data for name, data in package.items()),
                   "package sources changed during Lean replay")
    return {"status": "PASS_K8_HELPER450_LEAN_KERNEL", "environment": metadata,
            "axioms": {name: reports[name] for name in ROOTS},
            "control_axioms": {name: reports[name] for name in CONTROL_ROOTS},
            "generated_sha256": binding["generated_sha256"],
            "control_sources_sha256": control_hashes, "binding": binding,
            "inputs": {name: source.digest(data) for name, data in inputs.items()},
            "package_sha256": {name: source.digest(data) for name, data in package.items()},
            "controls": {"rejected": sorted(NEGATIVE_CONTROLS),
                         "positive": ["relabel_row", "row_not_column"]},
            "scope": "Complete retained forward word scalar row for helper450; "
                     "not a proof of the JSON adapter, physical recipes or isolated columns."}


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
        observed_core, expected_core = dict(result), dict(expected)
        observed_core["environment"] = dict(result["environment"], lean="platform metadata")
        expected_core["environment"] = dict(expected["environment"], lean="platform metadata")
        source.require(source.encoded(observed_core) == source.encoded(expected_core),
                       "kernel receipt mismatch")
    print(result["status"] + " roots=" + str(len(result["axioms"])) +
          f" elapsed_seconds={time.monotonic() - began:.1f}")


if __name__ == "__main__":
    main()
