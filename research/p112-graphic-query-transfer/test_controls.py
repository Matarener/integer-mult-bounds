"""Optimized real-CLI controls on exclusive, owned, inode-disjoint copies."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
NAMES = ("verify", "independent")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def owned_copy(source, target):
    before = source.lstat()
    require(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular source",
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    with target.open("xb") as out:
        require(out.write(data) == len(data), "complete copy")
    after = target.lstat()
    require(
        stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid(),
        "owned regular destination",
    )
    require(
        (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino), "distinct inode"
    )
    require(target.read_bytes() == data, "byte equality")


def invoke(root, name, expected):
    argv = [
        sys.executable,
        "-I",
        "-O",
        "-Werror",
        "-B",
        str(root / PACKAGE.relative_to(ROOT) / (name + ".py")),
    ]
    completed = subprocess.run(
        argv, cwd=root, capture_output=True, text=True, timeout=60, check=False
    )
    require(
        (completed.returncode == 0) == expected,
        name + " control exit: " + completed.stdout + completed.stderr,
    )
    if expected:
        require("PASS_" in completed.stdout, "positive actual result")


def corrupt(path, kind):
    data = json.loads(path.read_text())
    if kind == "endpoint":
        data["readers"][0][0] += 1
    elif kind == "bill":
        data["charges"][0] += 1
        data["total"] += 1
    elif kind == "evidence":
        data["marked"][0]["source"] += 1
    elif kind == "template":
        data["points"][0][0] = [0, 0, 0]
    else:
        raise ValueError("unknown mutation")
    path.write_text(json.dumps(data, indent=2) + "\n")


def run_controls(root):
    local = root / PACKAGE.relative_to(ROOT)
    for name in NAMES:
        invoke(root, name, True)
    for kind, relative in (
        ("endpoint", "WITNESS.json"),
        ("bill", "WITNESS.json"),
        ("evidence", "RESULT.json"),
        ("template", "../p112-query-series-transfer/PREDECESSOR-TEMPLATES.json"),
    ):
        path = local / relative
        original = path.read_bytes()
        pins = local / "SOURCES.json"
        original_pins = pins.read_bytes()
        try:
            corrupt(path, kind)
            if kind == "template":
                data = json.loads(pins.read_text())
                for row in data["files"]:
                    if row["path"].endswith("PREDECESSOR-TEMPLATES.json"):
                        row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                pins.write_text(json.dumps(data, indent=2) + "\n")
            for name in NAMES:
                invoke(root, name, False)
        finally:
            path.write_bytes(original)
            pins.write_bytes(original_pins)
    for name in NAMES:
        invoke(root, name, True)


def main():
    inputs = [
        ROOT / row["path"]
        for row in json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
        if row["usage"] == "input"
    ]
    files = sorted(PACKAGE.iterdir()) + inputs
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with tempfile.TemporaryDirectory(prefix="graphic-controls-") as directory:
        root = Path(directory)
        for path in files:
            owned_copy(path, root / path.relative_to(ROOT))
        run_controls(root)
    require(
        all(
            hashlib.sha256(Path(p).read_bytes()).hexdigest() == value
            for p, value in hashes.items()
        ),
        "canonical sources unchanged",
    )
    print(
        "PASS_GRAPHIC_CONTROLS 4 mutations; 8 negative optimized CLI runs; 4 positive runs; canonical hashes unchanged"
    )


if __name__ == "__main__":
    main()
