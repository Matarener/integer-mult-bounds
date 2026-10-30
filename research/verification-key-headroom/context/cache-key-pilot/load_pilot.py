"""Cold compiler/loader. Called only by the parent's single guarded child."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import sysconfig

ROOT = Path(__file__).resolve().parent


def verify_sources() -> dict:
    manifest = json.loads((ROOT / "FROZEN-SOURCE.json").read_text())
    base = ROOT.parent.parent if ROOT.parent.name == "stages" else ROOT.parent
    groups = ((ROOT, manifest["files_sha256"]),
              (base, manifest["reference_files_sha256"]))
    for directory, pins in groups:
        for relative, expected in pins.items():
            path = directory / relative
            if path.is_symlink() or not path.is_file():
                raise RuntimeError(f"source is absent or symlink: {relative}")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                raise RuntimeError(f"source pin mismatch: {relative}")
    return manifest


def compile_and_load(destination: Path):
    manifest = verify_sources()
    build = destination / "build"
    build.mkdir()  # Existing directory is an error; never reuse a built answer.
    source = ROOT / "keypilot.c"
    copied = build / "keypilot.c"
    copied.write_bytes(source.read_bytes())
    copied_sha256 = hashlib.sha256(copied.read_bytes()).hexdigest()
    if copied_sha256 != manifest["files_sha256"]["keypilot.c"]:
        raise RuntimeError("compiler snapshot differs from the declared C source pin")
    suffix = sysconfig.get_config_var("EXT_SUFFIX")
    if not isinstance(suffix, str) or not suffix:
        raise RuntimeError("missing extension suffix")
    extension = build / ("_keypilot" + suffix)
    compiler = shlex.split(sysconfig.get_config_var("CC") or "cc")
    command = compiler + ["-O3", "-std=c11", "-fPIC", "-shared", "-Wall", "-Wextra", "-Werror"]
    for directory in sorted({sysconfig.get_path("include"), sysconfig.get_path("platinclude")}):
        if directory:
            command.extend(["-I", directory])
    command.extend([str(copied), "-o", str(extension)])
    receipt = {"command": command, "cwd": str(ROOT), "python": sys.version,
               "executable": sys.executable, "platform": sys.platform,
               "source_sha256": copied_sha256,
               "source_manifest": manifest}
    (build / "BUILD.json").write_text(json.dumps(receipt, indent=2) + "\n")
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                               check=False, timeout=60)
    (build / "stdout.txt").write_text(completed.stdout)
    (build / "stderr.txt").write_text(completed.stderr)
    receipt["returncode"] = completed.returncode
    receipt["stdout_bytes"] = len(completed.stdout.encode())
    receipt["stderr_bytes"] = len(completed.stderr.encode())
    if completed.returncode or completed.stdout or completed.stderr:
        (build / "BUILD.json").write_text(json.dumps(receipt, indent=2) + "\n")
        raise RuntimeError("single compiler attempt failed or emitted output; see retained BUILD.json and compiler logs")
    if hashlib.sha256(copied.read_bytes()).hexdigest() != copied_sha256:
        raise RuntimeError("compiler snapshot changed during the single build")
    receipt["extension_sha256"] = hashlib.sha256(extension.read_bytes()).hexdigest()
    (build / "BUILD.json").write_text(json.dumps(receipt, indent=2) + "\n")
    verify_sources()
    spec = importlib.util.spec_from_file_location("_keypilot", extension)
    if spec is None or spec.loader is None:
        raise RuntimeError("extension has no loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, receipt
