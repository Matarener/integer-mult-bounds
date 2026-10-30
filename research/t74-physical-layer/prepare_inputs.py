# SPDX-License-Identifier: Apache-2.0
"""Prepare T74 controller inputs through the retained source emitter.

This bounded data-preparation prefix excludes supplier/outer admission.
It preserves the derived source and both native input directories.
"""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[2]
ALLOCATION = ROOT / "research/rank7-joint-endframes/allocation"
HELPERS = ROOT / "research/shared-kernel-repacking/vendor/pr2839"
SOURCE_MANIFEST = "751b46364742cbb947f7db07c130ff09085b38b52c520d3b47f2dadc1e21ba80"
HELPER_PINS = {
    "reconstruct_replica.py": "5472811c24aef3852dc7e189dff5060076a6c0b25bfde928da50dcfe9b5bdc15",
    "lift_parent.py": "9a1edd7d4ab4a2f2ac8d15b42b7e40f93653d65026bac59e4c1ce80b486bd60e",
    "replica_parent.py": "48bdbf28f59d80edb266803ec61bf5e22e8fb5e5a0e2b88004b6039147589bd4",
}
BASE_PREFIX = "demotions1148-round43/baseline-replay/parent/t16/parent558/complex-global/base/"
BASE_MEMBERS = {
    "work/complex-nine-native/DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "split-centres/CANONICAL-WORD.json.gz": "66d3c3c70983224650643a0a05a21ac6c6959f84d0f4528650601016f5a76844",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def inventory(path):
    return {p.relative_to(path).as_posix(): digest(p) for p in path.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "native-base", "native-extra", "work"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    source, work = args.source.resolve(), args.work.resolve()
    native = {"gauge44": args.native_base.resolve(), "extra": args.native_extra.resolve()}
    need(not work.exists() and not work.is_relative_to(source) and
         all(not work.is_relative_to(p) for p in native.values()), "fresh separate output")
    source_before = inventory(source)
    need(digest(source / "MANIFEST.json") == SOURCE_MANIFEST and
         {k: v for k, v in source_before.items() if k != "MANIFEST.json"} == read(source / "MANIFEST.json"),
         "complete immutable 637-file derived source")
    native_before = {pid: inventory(path) for pid, path in native.items()}
    for name, pin in HELPER_PINS.items():
        need(digest(HELPERS / name) == pin, "retained helper: " + name)
    work.mkdir()
    package = work / "input-package"
    shutil.copytree(source, package)
    # This is a derived working package, not the frozen source inventory.
    (package / "MANIFEST.json").unlink()
    shutil.copy2(HELPERS / "reconstruct_replica.py", package / "reconstruct.py")
    for name in ("FILL.json.gz", "ORDER.json", "DISPATCH.json"):
        shutil.copy2(ALLOCATION / name, package / "new/borrow-fill" / name)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    for key in ("PYTHONOPTIMIZE", "PYTHONPATH", "WITNESS_SPEC", "WITNESS_RECORD", "WITNESS_DISCOVER"):
        env.pop(key, None)
    stages = []

    def run(name, script, *arguments):
        start = time.monotonic()
        command = [sys.executable, "-B", str(script), *map(str, arguments)]
        with (work / (name + ".log")).open("w") as log:
            result = subprocess.run(command, cwd=work, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=180)
        stages.append(dict(stage=name, exit_code=result.returncode, seconds=time.monotonic()-start,
                           command=command, log_sha256=digest(work / (name + ".log"))))
        write(work / "STAGES.json", stages)
        need(result.returncode == 0, "failed " + name + ": " + str(work / (name + ".log")))
        print("PASS", name, flush=True)

    owners, parent, rebound = (work / name for name in ("owners", "parent", "rebound"))
    run("owners", package / "reconstruct.py", "--out", owners)
    run("parent", HELPERS / "lift_parent.py", "--package", package, "--owners", owners, "--out", parent)
    for path in parent.iterdir():
        if path.is_file():
            shutil.copy2(path, package / path.name)
    spec = read(parent / "SPEC.json")
    spec["expected"]["live"] = 66304
    spec["width_spot_helpers"] = read(source / "new/SPEC.json")["width_spot_helpers"]
    write(package / "new/SPEC.json", spec)
    run("rebind", source / "new/rebind.py", package, native["gauge44"], native["extra"], rebound)
    spec = read(rebound / "SPEC.json")
    plan = read(rebound / "PLAN.json")
    # PR2530's established admission correction: include actual private Z stock.
    zeros = max(len(read(path / "CANONICAL-WORD.json.gz")["zero_buffers"]) for path in native.values())
    need(zeros == 91, "actual changed private stock")
    spec["expected"]["physical"] = 66304 + 408 + 8 + zeros + 2
    spec["providers"] = {}
    for pid, path in native.items():
        word, checks = read(path / "CANONICAL-WORD.json.gz"), read(path / "LOCAL-CHECKS.json")
        widths = [len(word["frames"][word["final"][r]]) - len(word["frames"][word["start"][r]])
                  for r in range(224, 632)]
        spec["providers"][pid] = dict(inventory={str(k): v for k, v in Counter(widths).items()},
            native_negative_controls=len(read(path / "INDEPENDENT-LOCAL-REPLAY.json")["negative_controls_rejected"]),
            phase_edges=read(path / "CLIFFORD-REVIEW.json")["directed_edges"],
            expected_profile=checks["forward"]["paid_profile"],
            artifact_semantic_sha256=plan["provider_registry"][pid]["artifact_semantic_sha256"])
    spec_path = package / "new/CONTROLLER-SPEC.json"
    write(spec_path, spec)
    env["WITNESS_SPEC"] = str(spec_path)
    baseline = work / "baseline"
    base = baseline / "complex-global/base"
    with tarfile.open(source / "vendor/pr1297/upstream-layout.tar.gz", "r:gz") as archive:
        for suffix, pin in BASE_MEMBERS.items():
            member = archive.getmember(BASE_PREFIX + suffix)
            need(member.isfile(), "regular baseline member")
            raw = archive.extractfile(member).read()
            need(sha256(raw).hexdigest() == pin, "exact baseline phase/canonical input")
            target = base / suffix
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    shutil.copy2(parent / "GLOBAL-TEMPLATE.json.gz", base / "split-centres/GLOBAL-TEMPLATE.json.gz")
    bound = work / "bound"
    run("bind", source / "code/bind_providers_portable.py", "--baseline", baseline,
        "--provider", "gauge44=" + str(native["gauge44"]), "--provider", "extra=" + str(native["extra"]),
        "--plan", rebound / "PLAN.json", "--out", bound)
    hosted = work / "hosted"
    run("emit", source / "code/emit_allcold.py", "--base", bound / "base", "--owners", rebound / "OWNERS.json.gz",
        "--plan", bound / "PLAN.json", "--out", hosted)
    run("audit", source / "code/audit_allcold.py", bound / "base", hosted, work / "CONTROLLER-AUDIT.json")
    need(inventory(source) == source_before and
         all(inventory(path) == native_before[pid] for pid, path in native.items()), "immutable input preservation")
    template = read(hosted / "GLOBAL-TEMPLATE.json.gz")
    need((template["live"], template["physical"]) == (66304, 66813) and
         len(template["calls"]) == 666 and len(template["execution_schedule"]) == 2222,
         "complete changed controller dimensions")
    write(work / "RESULT.json", dict(status="PASS_T74_CONTROLLER_SOURCE_PREPARATION",
        source_manifest=SOURCE_MANIFEST, stages=stages,
        template_sha256=digest(hosted / "GLOBAL-TEMPLATE.json.gz"),
        scope="Fresh source-native binding, emitted finite controller and retained audit only; no physical recursive execution or supplier/outer admission."))
    print("PASS_T74_CONTROLLER_SOURCE_PREPARATION", flush=True)


if __name__ == "__main__":
    main()
