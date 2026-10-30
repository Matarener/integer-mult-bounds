#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise the real optimized CLI in a Git-free source export."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent


def run(package, good, message):
    r = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                       cwd=package.parent, capture_output=True, text=True, timeout=240)
    if (r.returncode == 0) != good or message not in r.stdout + r.stderr:
        raise ValueError("unexpected actual CLI response: " + r.stdout + r.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix="r437-copy-uniform-export-") as folder:
        root = Path(folder)
        package = root / "package"
        shutil.copytree(P, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if (root / ".git").exists():
            raise ValueError("export unexpectedly has Git")
        run(package, True, "PASS_UNIFORM_COPY_REDUCTION_WITH_EXPLICIT_BACKEND_PREMISES")
        word = package / "inputs/r437-word.json.gz"
        saved = word.read_bytes()
        word.write_bytes(saved + b"modified")
        run(package, False, "retained SHA")
        word.unlink()
        run(package, False, "missing/linked retained input")
        outside = root / "outside.gz"
        outside.write_bytes(saved)
        word.symlink_to(outside)
        run(package, False, "missing/linked retained input")
        word.unlink()
        word.write_bytes(saved)
        receipt = package / "RESULT.json"
        changed = json.loads(receipt.read_bytes())
        changed["invoice"]["ordinary_block_swap_calls_upper"] = 0
        receipt.write_text(json.dumps(changed))
        run(package, False, "recomputed result differs")
    print("PASS_ACTUAL_EXPORTED_CLI positive=1 controls=4 optimized=true Git_free=true")


if __name__ == "__main__":
    main()
