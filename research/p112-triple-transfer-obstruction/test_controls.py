#!/usr/bin/env python3
"""Actual optimized CLI faults on exclusive private copies. Apache-2.0."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def private_copy(source, target):
    before = source.lstat()
    require(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "regular owned source",
    )
    descriptor = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        actual = os.fstat(stream.fileno())
        require(
            (actual.st_dev, actual.st_ino) == (before.st_dev, before.st_ino),
            "source identity",
        )
        raw = stream.read(1048577)
    require(len(raw) <= 1048576, "private copy capacity")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        owned = os.fstat(stream.fileno())
        require(
            stat.S_ISREG(owned.st_mode) and owned.st_uid == os.getuid(),
            "private regular owner",
        )
        require(
            owned.st_nlink == 1
            and (owned.st_dev, owned.st_ino) != (actual.st_dev, actual.st_ino),
            "distinct private inode",
        )
        require(stream.write(raw) == len(raw), "complete private copy")
    require(target.read_bytes() == raw, "private byte equality")
    return hashlib.sha256(raw).hexdigest()


def run_cli(script, expected):
    command = [sys.executable, "-I", "-O", "-Werror", "-B", str(script)]
    run = subprocess.run(
        command, capture_output=True, text=True, timeout=60, check=False
    )
    require((run.returncode == 0) == expected, "unexpected actual CLI acceptance")
    if expected:
        require(
            "PASS_TRIPLE_TRANSFER_OBSTRUCTION" in run.stdout,
            "positive completion marker",
        )
    return {
        "argv": command,
        "exit": run.returncode,
        "stdout": run.stdout,
        "stderr": run.stderr,
    }


def corrupted_runs(package, data):
    receipts = []
    result_path = package / "RESULT.json"
    original = result_path.read_bytes()
    wrong = json.loads(original)
    wrong["literal_census"]["best"]["bill"] -= 1
    result_path.write_text(json.dumps(wrong))
    receipts.append(
        {
            "fault": "lowered recorded actual-reader bill",
            "run": run_cli(package / "verify.py", False),
        }
    )
    result_path.write_bytes(original)
    for path in (package / "RETAINED-RANK32.json", data):
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        receipts.append(
            {
                "fault": "pinned source byte drift",
                "path": path.name,
                "run": run_cli(package / "verify.py", False),
            }
        )
        path.write_bytes(original)
    script = package / "verify.py"
    original = script.read_text()
    require(original.count("tariff(q, u,") == 1, "reader fault injection anchor")
    script.write_text(original.replace("tariff(q, u,", "tariff(q, q,", 1))
    receipts.append(
        {
            "fault": "price the query instead of the actual reader",
            "run": run_cli(script, False),
        }
    )
    script.write_text(original)
    receipts.append({"fault": None, "run": run_cli(script, True)})
    return receipts


def main():
    files = [
        HERE / name for name in ("verify.py", "RESULT.json", "RETAINED-RANK32.json")
    ]
    files.append(HERE.parent.parent / DATA)
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with tempfile.TemporaryDirectory(prefix="triple-controls-") as temp:
        tree = Path(temp)
        package = tree / "research" / HERE.name
        for source in files[:3]:
            private_copy(source, package / source.name)
        private_copy(files[3], tree / DATA)
        try:
            private_copy(files[0], package / files[0].name)
        except FileExistsError:
            pass
        else:
            raise ValueError("exclusive-copy overwrite accepted")
        alias = tree / "source-alias"
        alias.symlink_to(files[0])
        try:
            private_copy(alias, tree / "must-not-exist")
        except ValueError:
            pass
        else:
            raise ValueError("symlink source accepted")
        alias.unlink()
        receipt = corrupted_runs(package, tree / DATA)
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    require(before == after, "source changed during private controls")
    print(
        json.dumps(
            {"runs": receipt, "source_sha256": before, "copy_controls": 2},
            sort_keys=True,
        )
    )
    print("PASS_TRIPLE_CONTROLS faults=4 positive=1 copy_controls=2 errors=0")


if __name__ == "__main__":
    main()
