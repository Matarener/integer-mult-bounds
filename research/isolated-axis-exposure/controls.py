#!/usr/bin/env python3
"""Actual optimized CLI controls using private regular byte copies."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def copy_regular(source: Path, destination: Path) -> None:
    before = source.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
         "owned regular source")
    raw = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output:
        need(output.write(raw) == len(raw), "complete byte copy")
    after = destination.lstat()
    need(stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid()
         and (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
         "owned inode-disjoint regular copy")
    need(hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256(raw).digest(),
         "copy byte identity")


def run(verifier: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-I", "-O", "-W", "error", "-B", str(verifier)],
                          capture_output=True, text=True, timeout=60, check=False)


def diagnostic(name: str, process: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return {"file": name, "argv": process.args, "exit": process.returncode,
            "stdout": process.stdout, "stderr": process.stderr}


def main() -> None:
    manifest = json.loads((PACKAGE / "VERIFY.json").read_text())
    own = tuple(path for path in PACKAGE.iterdir() if path.is_file())
    inputs = tuple(PACKAGE.parents[1] / name for name in manifest["inputs"])
    need(len(own) <= 16 and len(inputs) == 2, "bounded copy inventory")
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="exposure-controls-") as directory:
        root = Path(directory)
        for source in own + inputs:
            copy_regular(source, root / source.relative_to(PACKAGE.parents[1]))
        candidate = root / "research/isolated-axis-exposure"
        verifier = candidate / "verify.py"
        valid = run(verifier)
        need(valid.returncode == 0 and "PASS_ISOLATED_AXIS_EXPOSURE" in valid.stdout,
             "valid optimized CLI")
        mutations = (
            (candidate / "RESULT.json", b'"maximum_increase": 4', b'"maximum_increase": 3'),
            (verifier, b"MAX_BREAKS = 4", b"MAX_BREAKS = 3"),
            (verifier, b"augmented = (-1,) + order", b"augmented = order"),
            (root / "research/physical-ordinary-interchange/binary.py", b"class Binary:", b"class WrongBinary:"),
            (candidate / "SOURCES.json", b'"usage": "input"', b'"usage": "provenance"'),
        )
        for path, old, new in mutations:
            original = path.read_bytes()
            need(old in original, "exact mutation anchor")
            mutated = original.replace(old, new, 1)
            need(path.write_bytes(mutated) == len(mutated), "complete mutation write")
            rejected = run(verifier)
            need(rejected.returncode != 0 and "PASS_ISOLATED_AXIS_EXPOSURE" not in rejected.stdout,
                 "mutant CLI rejects")
            outcomes.append(diagnostic(str(path.relative_to(root)), rejected))
            need(path.write_bytes(original) == len(original), "complete restoration write")
        receipt = candidate / "RESULT.json"
        raw = receipt.read_bytes()
        receipt.unlink()
        missing = run(verifier)
        need(missing.returncode != 0 and not receipt.exists(), "missing receipt is not repaired")
        outcomes.append(diagnostic("missing RESULT.json", missing))
        need(receipt.write_bytes(raw) == len(raw), "complete receipt restoration")
    print(json.dumps({"status": "PASS_EXPOSURE_CLI_CONTROLS", "positive": 1,
                      "negative": outcomes}, sort_keys=True))


if __name__ == "__main__":
    main()
