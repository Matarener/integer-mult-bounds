#!/usr/bin/env python3
"""Authenticate and replay the scoped PR3734 consumer research package.

Use a new --work directory outside this package. Every replay operates on an
isolated workspace-shaped copy, leaving the delivered evidence unchanged.

SPDX-License-Identifier: Apache-2.0
Substantial OpenAI Codex assistance under the user's direction.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
EXEMPT = {"MANIFEST.json", "VALIDATION.json"}
BASE = "integer-mult-bounds/research/kappa-consumer-followup"
COMMANDS = (
    ("modern_native", "recovered-involutory/modern_native_component.py"),
    ("baseline_outer_and_symmetric", f"{BASE}/baseline/replay.py"),
    ("rational_inverse", "recovered-involutory/rational_inverse_component.py"),
    ("retained_controller", f"{BASE}/controller/check_controller.py"),
    ("dirty_core_pair", f"{BASE}/controller/dirty_core_component.py"),
    ("physical_owner_audit", f"{BASE}/controller/check_retention_owners.py"),
    ("independent_symmetric_review", "recovered-involutory/review_symmetric_extension.py"),
    ("terminal_decoder", "recovered-involutory/terminal_native_decoder.py"),
)
SCOPE = (
    "Finite local native operators, exact complete cost arithmetic, physical "
    "owner audit, and a finite terminal inverse. No new kappa, selected "
    "certificate, all-size supplier, or full uniform precision/tape admission."
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_payload(path: Path) -> bytes:
    """Compare proof data, independent of gzip headers or compressor version."""
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    data = json.loads(raw)
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def authenticate() -> dict:
    manifest = json.loads((HERE / "MANIFEST.json").read_text())
    files = manifest["files"]
    actual = {
        p.relative_to(HERE).as_posix()
        for p in HERE.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
        and p.suffix != ".pyc" and p.relative_to(HERE).as_posix() not in EXEMPT
    }
    need(actual == set(files), "Delivered file set differs from MANIFEST.json")
    for relative, expected in files.items():
        path = HERE / relative
        need(path.resolve().is_relative_to(HERE), f"Manifest path escapes package: {relative}")
        need(not path.is_symlink(), f"Symlink is not an authenticated file: {relative}")
        need(path.stat().st_size == expected["bytes"], f"Size mismatch: {relative}")
        need(digest(path) == expected["sha256"], f"SHA-256 mismatch: {relative}")
    for item in manifest["regenerated_artifacts"]:
        need(sha256(canonical_payload(HERE / "artifact" / item["path"])).hexdigest()
             == item["canonical_json_sha256"],
             f"Stored canonical payload mismatch: {item['path']}")
    return manifest


def main() -> None:
    need(__debug__, "Assertions must be enabled; do not use python -O")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path,
                        help="New isolated replay directory outside this package")
    args = parser.parse_args()
    work = args.work.expanduser().resolve()
    need(not work.exists(), "--work must name a new directory")
    need(not work.is_relative_to(HERE), "--work must be outside this package")
    manifest = authenticate()
    print(f"PASS source authentication: {len(manifest['files'])} files", flush=True)
    shutil.copytree(HERE / "artifact", work,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    logs = work / "replay-logs"
    logs.mkdir()
    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    environment["PYTHONPYCACHEPREFIX"] = str(work / "replay-bytecode-cache")
    started = time.monotonic()
    receipt = {
        "status": "RUNNING",
        "scope": SCOPE,
        "manifest_sha256": digest(HERE / "MANIFEST.json"),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "assertions_enabled": True, "isolated_bytecode_cache": True},
        "authenticated_files": len(manifest["files"]),
        "commands": [],
        "regenerated_artifacts": [],
    }
    receipt_path = work / "REPLAY.json"

    def save() -> None:
        receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")

    try:
        for name, relative in COMMANDS:
            print(f"RUN  {name}", flush=True)
            command = [sys.executable, "-B", str(work / relative)]
            one_start = time.monotonic()
            log_path = logs / f"{name}.log"
            with log_path.open("w") as log:
                run = subprocess.run(command, cwd=work / "integer-mult-bounds",
                                     stdout=log, stderr=subprocess.STDOUT,
                                     text=True, check=False, env=environment)
            receipt["commands"].append({
                "name": name, "script": relative,
                "argv": ["python3", "-B", relative],
                "cwd": "integer-mult-bounds",
                "source_sha256": digest(work / relative),
                "exit_code": run.returncode,
                "elapsed_seconds": round(time.monotonic() - one_start, 3),
                "log": log_path.relative_to(work).as_posix(),
                "log_sha256": digest(log_path),
            })
            save()
            if run.returncode:
                print(log_path.read_text()[-16000:], flush=True)
            need(run.returncode == 0, f"Replay failed: {name}; see {log_path}")
            print(f"PASS {name}", flush=True)

        for item in manifest["regenerated_artifacts"]:
            relative = item["path"]
            actual_hash = sha256(canonical_payload(work / relative)).hexdigest()
            need(actual_hash == item["canonical_json_sha256"],
                 f"Regenerated proof payload differs: {relative}")
            receipt["regenerated_artifacts"].append({
                "path": relative,
                "canonical_json_sha256": actual_hash,
                "matches_delivered_payload": True,
            })
        receipt["status"] = "PASS_SCOPED_PORTABLE_REPLAY"
        receipt["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save()
    except Exception as exc:
        receipt["status"] = "FAIL"
        receipt["error"] = str(exc)
        save()
        raise
    print(f"PASS canonical payloads: {len(receipt['regenerated_artifacts'])}", flush=True)
    print(receipt["status"], flush=True)
    print(receipt_path, flush=True)


if __name__ == "__main__":
    main()
