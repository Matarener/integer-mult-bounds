#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise the real standalone CLI on a Git-free source export and corruptions."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise RuntimeError(message)


def snapshots(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix="rematch-block-export-") as tmp:
        root = Path(tmp)
        package = root / "research/rematch-block-rank-audit"
        package.mkdir(parents=True)
        for name in ("verify.py", "SOURCES.json", "RESULT.json", "PR3335-CERTIFICATE.json"):
            shutil.copyfile(HERE / name, package / name)
        archive_name = "research/community-frontier1094-audit/selected-replay.tar.gz"
        archive = root / archive_name
        archive.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / archive_name, archive)
        env = dict(os.environ, PATH="", PYTHONOPTIMIZE="2")
        script = package / "verify.py"

        def run(args=(), expected=None):
            before = snapshots(root)
            result = subprocess.run(
                [sys.executable, "-I", "-O", "-B", "-Werror", str(script), *args],
                cwd=root, env=env, text=True, encoding="utf-8", capture_output=True,
                timeout=30, check=False,
            )
            need(snapshots(root) == before, "standalone replay changed exported bytes")
            if expected is None:
                need(result.returncode == 0 and "PASS_REMATCH_BLOCK_RANK_AUDIT" in result.stdout,
                     result.stdout + result.stderr)
            else:
                need(result.returncode != 0 and expected in result.stderr,
                     "CLI failed to reject the intended cause: " + result.stdout + result.stderr)

        run()
        # Normal replay cannot depend on Git, PATH, PYTHONPATH or a writable source tree.
        for p in root.rglob("*"):
            if p.is_file():
                p.chmod(0o444)
        run()
        for p in root.rglob("*"):
            if p.is_file():
                p.chmod(0o644)

        saved = archive.read_bytes()
        archive.write_bytes(bytes([saved[0] ^ 1]) + saved[1:])
        run(expected="source bytes: " + archive_name)
        archive.write_bytes(saved)

        cert = package / "PR3335-CERTIFICATE.json"
        saved = cert.read_bytes()
        cert.write_bytes(saved + b"\n")
        run(expected="source bytes: research/rematch-block-rank-audit/PR3335-CERTIFICATE.json")
        cert.write_bytes(saved)

        receipt = package / "RESULT.json"
        saved = receipt.read_bytes()
        altered = json.loads(saved)
        altered["channels"] = 34.0
        receipt.write_text(json.dumps(altered), encoding="utf-8")
        run(expected="exact typed result receipt")
        altered["channels"] = 34
        altered["finite_rank_checks"]["1"]["2"] = True
        receipt.write_text(json.dumps(altered), encoding="utf-8")
        run(expected="exact typed result receipt")
        receipt.write_bytes(saved)
        run(args=("--write",), expected="usage: verify.py [--emit]")
        run()
    print("PASS_REMATCH_BLOCK_INTEGRITY git_free_readonly=true corruptions_rejected=5")


if __name__ == "__main__":
    main()
