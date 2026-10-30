#!/usr/bin/env python3
"""Run optimized CLI corruption controls on private regular byte copies. Apache-2.0."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).absolute().parent
DATA = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def copy_bytes(source, destination):
    before = source.lstat()
    check(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular source",
    )
    check(before.st_size <= 1048576, "copy capacity")
    raw = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        written = stream.write(raw)
    after = destination.lstat()
    check(written == len(raw), "short copy")
    check((before.st_dev, before.st_ino) != (after.st_dev, after.st_ino), "inode alias")
    check(
        stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid(),
        "owned regular destination",
    )
    check(source.lstat() == before and destination.read_bytes() == raw, "copy drift")


def remove_owned(root):
    for parent, dirs, files in os.walk(root, topdown=False, followlinks=False):
        for name in files + dirs:
            path = Path(parent) / name
            info = path.lstat()
            check(info.st_uid == os.getuid(), "cleanup ownership")
            if stat.S_ISDIR(info.st_mode):
                path.rmdir()
            else:
                path.unlink()
    root.rmdir()


def replay(root, success, reason=None):
    script = root / "research" / HERE.name / "verify.py"
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-O",
            "-Werror",
            "-B",
            str(script),
            "--case",
            "6",
            "24",
            "25",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    check((result.returncode == 0) == success, "unexpected CLI exit")
    if reason is not None:
        check(reason in result.stderr, "wrong rejection")
    return {"exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def mutations(root, package):
    receipts = []
    result_file = package / "RESULT.json"
    saved = result_file.read_bytes()
    result = json.loads(saved)
    row = next(r for r in result["classes"] if r["targets"] == [6, 24, 25])
    row["minimum"] = 15
    result_file.write_text(json.dumps(result))
    receipts.append(replay(root, False, "case mismatch"))
    result_file.write_bytes(saved)
    for path in (
        root / DATA,
        package / "RETAINED-RANK32.json",
        package / "RETAINED-PREDECESSOR-PROOF.md",
    ):
        raw = path.read_bytes()
        path.write_bytes(raw + b" ")
        receipts.append(replay(root, False, "source drift"))
        path.write_bytes(raw)
    fixture = package / "RETAINED-RANK32.json"
    renamed = fixture.with_suffix(".saved")
    fixture.rename(renamed)
    fixture.symlink_to(renamed.name)
    receipts.append(replay(root, False, "source symlink"))
    fixture.unlink()
    renamed.rename(fixture)
    receipts.append(replay(root, True))
    return receipts


def main():
    sources = sorted(p for p in HERE.iterdir() if p.is_file()) + [
        HERE.parents[1] / DATA
    ]
    check(
        len(sources) <= 16 and all(p.lstat().st_size <= 1048576 for p in sources),
        "source capacity",
    )
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    root = Path(tempfile.mkdtemp(prefix="p112-affine-controls-"))
    try:
        package = root / "research" / HERE.name
        for source in sources:
            destination = (
                root / DATA
                if source == HERE.parents[1] / DATA
                else package / source.name
            )
            copy_bytes(source, destination)
        receipts = mutations(root, package)
    finally:
        remove_owned(root)
    check(
        {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources} == hashes,
        "source mutation",
    )
    print(
        "PASS_AFFINE_CONTROLS",
        json.dumps(
            {"rejected": 5, "restored_positive": 1, "receipts": receipts},
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
