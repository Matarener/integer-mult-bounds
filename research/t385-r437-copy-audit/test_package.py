#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Real exported CLI checks: no Git, altered source/result, missing and linked inputs."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = Path("research/t385-r437-copy-audit")


def call(root, expected, message=None):
    process = subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(root / PACKAGE / "verify.py")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=240,
    )
    if (process.returncode == 0) != expected:
        raise ValueError("unexpected CLI outcome: " + process.stdout + process.stderr)
    if message is not None and message not in process.stdout + process.stderr:
        raise ValueError("wrong failure reason: " + process.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix="r437-export-") as directory:
        root = Path(directory)
        package = root / PACKAGE
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        if (root / ".git").exists():
            raise ValueError("export unexpectedly has Git")
        # This runs the actual public CLI with only the published directory.
        call(root, True, "PASS_R437_ARBITRARY_STREAM_AND_FINITE_COPY_COST_AUDIT")
        source = package / "inputs/r437-word.json.gz"
        original = source.read_bytes()
        source.write_bytes(original + b"changed")
        call(root, False, "input SHA")
        source.write_bytes(original)
        source.unlink()
        call(root, False, "input missing/linked")
        outside = root / "outside-word.json.gz"
        outside.write_bytes(original)
        source.symlink_to(outside)
        call(root, False, "input missing/linked")
        source.unlink()
        source.write_bytes(original)
        receipt = package / "RESULT.json"
        saved = receipt.read_bytes()
        altered = json.loads(saved)
        altered["finite_cost"]["ERASE_linear_episodes"] = 0
        receipt.write_text(json.dumps(altered))
        call(root, False, "recomputed result differs")
        receipt.write_bytes(saved)
        if (
            hashlib.sha256(source.read_bytes()).digest()
            != hashlib.sha256(original).digest()
        ):
            raise ValueError("control did not restore source")
    print("PASS_R437_EXPORTED_CLI controls=4 positive=1 Git_free=true optimized=true")


if __name__ == "__main__":
    main()
