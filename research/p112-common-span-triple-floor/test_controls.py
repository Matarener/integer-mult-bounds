"""Real optimized CLI failures on private byte copies. Apache-2.0."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def regular_copy(source, destination):
    before = source.lstat()
    need(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular source",
    )
    need(before.st_size <= 1048576, "copy capacity")
    raw = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        need(stream.write(raw) == len(raw), "complete private copy")
    copied = destination.lstat()
    need(
        stat.S_ISREG(copied.st_mode)
        and copied.st_uid == os.getuid()
        and copied.st_nlink == 1,
        "owned regular destination",
    )
    need(
        (before.st_dev, before.st_ino) != (copied.st_dev, copied.st_ino),
        "distinct source and destination inode",
    )
    after = source.lstat()
    identity = (
        "st_dev",
        "st_ino",
        "st_mode",
        "st_uid",
        "st_nlink",
        "st_size",
        "st_mtime_ns",
    )
    need(
        all(getattr(after, key) == getattr(before, key) for key in identity)
        and source.read_bytes() == raw
        and destination.read_bytes() == raw,
        "unchanged copy bytes and source",
    )


def inventory():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    names = {str(p.relative_to(ROOT)) for p in HERE.iterdir() if p.is_file()}
    names.update(row["path"] for row in manifest["files"] if row["usage"] == "input")
    need(len(names) <= 48, "control input inventory capacity")
    return sorted(names)


def hashes(names):
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names
    }


def run(path, ok):
    process = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(path / "verify.py")],
        capture_output=True,
        check=False,
        text=True,
        timeout=60,
    )
    need(
        (process.returncode == 0) == ok,
        "CLI control exit: " + process.stdout + process.stderr,
    )
    if ok:
        need("PASS_COMMON_SPAN_TRIPLE" in process.stdout, "positive CLI result")
    return process.stdout + process.stderr


def corrupt(path, index):
    if index == 0:
        file = path / "RESULT.json"
        data = json.loads(file.read_text())
        data["fixtures"][0]["families"]["MMM"]["minimum"] -= 1
        file.write_text(json.dumps(data))
    elif index in (1, 2, 3):
        file = path / "FIXTURES.json"
        data = json.loads(file.read_text())
        if index == 1:
            data[0]["groups"][1] = [4, 8]
        elif index == 2:
            data[0]["groups"][0][1] = data[0]["groups"][0][0]
        else:
            data[0]["targets"][1] = data[0]["targets"][0]
        file.write_text(json.dumps(data))
    elif index == 4:
        file = path / "verify.py"
        text = file.read_text()
        need("((3, 12), (5, 10), (6, 9))" in text, "support fault location")
        file.write_text(
            text.replace("((3, 12), (5, 10), (6, 9))", "((1, 12), (5, 10), (6, 9))", 1)
        )
    elif index == 5:
        file = path / "RETAINED-PR3538-PROOF.md"
        file.write_bytes(file.read_bytes() + b"\nchanged\n")
    else:
        file = path / "verify.py"
        text = file.read_text()
        need(
            "(1, 0, 1)" in text,
            "selective map fault location",
        )
        file.write_text(
            text.replace(
                "(1, 0, 1)",
                "(0, 0, 0)",
                1,
            )
        )
    return file


def main():
    names = inventory()
    before = hashes(names)
    with tempfile.TemporaryDirectory(prefix="common-span-controls-") as temporary:
        destination = Path(temporary)
        for name in names:
            regular_copy(ROOT / name, destination / name)
        package = destination / HERE.relative_to(ROOT)
        run(package, ok=True)
        diagnostics = []
        for index in range(7):
            originals = {
                p.name: p.read_bytes() for p in package.iterdir() if p.is_file()
            }
            changed = corrupt(package, index)
            diagnostics.append(run(package, ok=False))
            changed.write_bytes(originals[changed.name])
        run(package, ok=True)
        need(all(diagnostics), "preserved failure diagnostics")
    need(hashes(names) == before, "original sources unchanged by controls")
    print(json.dumps({"fault_diagnostics": diagnostics}, sort_keys=True))
    print(
        "PASS_COMMON_SPAN_CONTROLS optimized_faults=7 restored=2 sources_unchanged="
        + str(len(names))
    )


if __name__ == "__main__":
    main()
