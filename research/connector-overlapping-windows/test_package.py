#!/usr/bin/env python3
"""Relocated replay and actual corruption controls; Apache-2.0."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def ensure(ok, why):
    if not ok:
        raise RuntimeError(why)


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def run(package, ok, message=None, extra=()):
    out = subprocess.run([sys.executable, "-I", "-O", "-B", str(package/"verify.py"), *extra],
                         cwd=package, text=True, capture_output=True, timeout=60)
    ensure((out.returncode == 0) == ok, "unexpected replay result: " + out.stdout + out.stderr)
    if message:
        ensure(message in out.stdout + out.stderr, "wrong rejection: " + out.stderr)


def main():
    source = json.loads((HERE/"SOURCES.json").read_text())
    with tempfile.TemporaryDirectory(prefix="connector-window-check-") as tmp:
        root = Path(tmp)
        p = root/"research"/HERE.name
        shutil.copytree(HERE, p, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for row in source["files"]:
            if row["usage"] == "input":
                target = root/row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT/row["path"]).read_bytes())
        before = inventory(root)
        run(p, True, "PASS_CONNECTOR_OVERLAPPING_WINDOWS")
        ensure(before == inventory(root), "ordinary replay wrote files")
        # Explicit exclusive output creation must not destroy an existing receipt.
        run(p, False, "FileExistsError", ("--write-receipt",))
        ensure(before == inventory(root), "exclusive write changed receipt")
        receipt = p/"RESULT.json"
        original = receipt.read_bytes()
        bad = json.loads(original)
        bad["pilot"]["persistent"]["xor_writes"] -= 1
        receipt.write_text(json.dumps(bad))
        bad_bytes = receipt.read_bytes()
        run(p, False, "RESULT.json mismatch")
        ensure(receipt.read_bytes() == bad_bytes, "failed run replaced a bad receipt")
        receipt.write_bytes(original)
        live = root/next(row["path"] for row in source["files"] if row["usage"] == "input")
        original_live = live.read_bytes()
        live.write_bytes(original_live + b"\nCORRUPTED\n")
        run(p, False, "source SHA256 mismatch")
        live.write_bytes(original_live)
        # Actual algorithm corruption: suppress final restoration parity.
        program = p/"verify.py"
        text = program.read_text()
        needle = "if parity == 0)"
        ensure(text.count(needle) == 1, "parity mutation anchor changed")
        program.write_text(text.replace(needle, "if True)"))
        run(p, False, "multiset oracle disagreement")
        program.write_text(text)
        # Drop the deadline test. A late, cheap source call must not service
        # an already delivered output even though the final map can agree.
        needle = "if new_last < due[slot]:"
        ensure(text.count(needle) == 1, "deadline mutation anchor changed")
        program.write_text(text.replace(needle, "if False:"))
        run(p, False, "multiset oracle disagreement")
        program.write_text(text)
        ensure(before == inventory(root), "test fixture not restored")
    print("PASS_WINDOW_PACKAGE_CONTROLS optimized_git_free=1 readonly=1 corruption_rejections=4 exclusive_write=1")


if __name__ == "__main__":
    main()
