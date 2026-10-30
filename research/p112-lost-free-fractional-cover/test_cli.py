#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Real optimized CLI failures on owned copies; frozen inputs are never edited."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = "research/p112-lost-free-fractional-cover"
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
BUDGET = "research/plane-port-copy-budgets/RESULT.json"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    originals = {p: p.read_bytes() for p in HERE.rglob("*") if p.is_file()}
    archive_hash = hashlib.sha256((ROOT / ARCHIVE).read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="p112-fractional-cli-") as directory:
        root = Path(directory)
        package = root / PACKAGE
        shutil.copytree(HERE, package)
        # Copies may inherit read-only export modes. Only these owned fault
        # fixtures become writable; the original package stays untouched.
        for path in package.rglob("*"):
            if path.is_file():
                path.chmod(path.stat().st_mode | stat.S_IWUSR)
        target = root / ARCHIVE
        target.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / ARCHIVE, target)
        budget = root / BUDGET
        budget.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / BUDGET, budget)

        def run(name, success, reason=None):
            proc = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")],
                                  cwd=root, capture_output=True, text=True, timeout=15)
            require((proc.returncode == 0) == success, "unexpected CLI result: " + name)
            if success:
                require("PASS_P112_COMPACT_FRACTIONAL_COVER" in proc.stdout and not proc.stderr, "positive marker")
            else:
                require("PASS_P112_COMPACT_FRACTIONAL_COVER" not in proc.stdout and reason in proc.stderr,
                        "wrong failure: " + name)

        run("initial positive", True)
        cert = package / "COVER.json"
        cert_bytes = cert.read_bytes()
        changed = json.loads(cert_bytes)
        changed["frames"][0]["weight"] = str(Fraction(changed["frames"][0]["weight"]) + Fraction(1, 2**100))
        cert.write_text(json.dumps(changed))
        run("sub-float rational error", False, "exact per-port coverage")
        cert.write_bytes(cert_bytes)
        cert.write_bytes(cert_bytes.replace(b'"dimension": 9', b'"dimension": 9, "dimension": 9', 1))
        run("duplicate JSON declaration", False, "duplicate JSON key")
        cert.write_bytes(cert_bytes)
        receipt = package / "RESULT.json"
        receipt_bytes = receipt.read_bytes()
        changed = json.loads(receipt_bytes)
        changed["lost_free_upper_bound"] = 55
        receipt.write_text(json.dumps(changed))
        run("stronger false receipt", False, "result receipt mismatch")
        receipt.write_bytes(receipt_bytes)
        witness = package / "inputs/pr3625-best-32.json"
        witness_bytes = witness.read_bytes()
        witness.write_bytes(witness_bytes + b" ")
        run("unbound predecessor witness", False, "retained byte length")
        witness.write_bytes(witness_bytes)
        source = target.read_bytes()
        target.write_bytes(bytes([source[0] ^ 1]) + source[1:])
        run("unbound selected archive", False, "archive hash")
        target.write_bytes(source)
        run("restored final positive", True)
    require(all(p.read_bytes() == data for p, data in originals.items()), "package inputs changed")
    require(hashlib.sha256((ROOT / ARCHIVE).read_bytes()).hexdigest() == archive_hash, "selected archive changed")
    print("PASS_COMPACT_COVER_REAL_CLI controls=5 positives=2 inputs_unchanged no_new_kappa")


if __name__ == "__main__":
    main()
