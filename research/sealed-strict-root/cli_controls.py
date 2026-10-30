"""Run real optimized child CLIs on exclusive regular byte copies."""

import json
import os
import stat
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(path):
    info = path.lstat()
    require(
        stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid(),
        "owned regular source",
    )
    return {
        "uid": info.st_uid,
        "mode": stat.S_IMODE(info.st_mode),
        "device": str(info.st_dev),
        "inode": str(info.st_ino),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def copy_inputs(target):
    sources = json.loads((HERE / "SOURCES.json").read_text())["files"]
    paths = [ROOT / row["path"] for row in sources if row["usage"] == "input"] + sorted(
        HERE.iterdir()
    )
    require(len(paths) <= 64, "bounded CLI copy inventory")
    before = {}
    for source in paths:
        row = identity(source)
        relative = source.relative_to(ROOT)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as output:
            raw = source.read_bytes()
            require(output.write(raw) == len(raw), "complete exclusive copy")
        copied = identity(destination)
        require(
            (row["device"], row["inode"]) != (copied["device"], copied["inode"]),
            "inode-disjoint copy",
        )
        require(copied["sha256"] == row["sha256"], "same copied bytes")
        before[str(source)] = row
    return before


def child(root, extra, code, text):
    command = [
        sys.executable,
        "-I",
        "-O",
        "-W",
        "error",
        "-B",
        str(root / "research/sealed-strict-root/verify.py"),
        "--suite",
        "controls",
        *extra,
    ]
    result = subprocess.run(
        command, cwd=root, text=True, capture_output=True, timeout=30
    )
    require(result.returncode == code and text in result.stderr, "actual CLI rejection")
    return {
        "argv": command,
        "exit": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main():
    with TemporaryDirectory(prefix="strict-root-controls-") as temporary:
        target = Path(temporary)
        before = copy_inputs(target)
        receipts = [child(target, ["--unknown"], 2, "unrecognized arguments")]
        mutant = target / "research/encoded-strict-borrowing/strict_selector.py"
        original = mutant.read_bytes()
        mutant.write_bytes(original + b"\n# controlled source drift\n")
        receipts.append(child(target, [], 1, "source hash"))
        mutant.write_bytes(original)
        archive = target / "research/sealed-strict-root/pr3542.tar"
        raw = archive.read_bytes()
        archive.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
        receipts.append(child(target, [], 1, "retained premise hash"))
        require(
            all(identity(Path(path)) == row for path, row in before.items()),
            "original source unchanged",
        )
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "source_identities": before,
                    "controls": receipts,
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
