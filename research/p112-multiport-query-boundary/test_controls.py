"""Optimized CLI fault controls on owned, regular, inode-disjoint byte copies."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copy_file(source, target):
    before = source.lstat()
    require(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular input",
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as handle:
        handle.write(source.read_bytes())
    after = target.lstat()
    require(
        after.st_uid == os.getuid() and after.st_nlink == 1, "owned single-link copy"
    )
    require(
        (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
        "inode-disjoint copy",
    )
    require(source.read_bytes() == target.read_bytes(), "copy bytes")


def run(root, success, expected):
    messages = expected if isinstance(expected, tuple) else (expected, expected)
    for script, message in zip(("verify.py", "independent.py"), messages, strict=True):
        command = [
            sys.executable,
            "-I",
            "-O",
            "-Werror",
            "-B",
            str(root / PACKAGE.relative_to(REPO) / script),
        ]
        result = subprocess.run(
            command, cwd=root, capture_output=True, text=True, timeout=30, check=False
        )
        print(
            json.dumps(
                {
                    "argv": command,
                    "cwd": str(root),
                    "expected_success": success,
                    "exit": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
                sort_keys=True,
            )
        )
        require((result.returncode == 0) == success, f"control exit: {script}")
        require(
            message in result.stdout + result.stderr, f"control predicate: {script}"
        )


def mutate(root, mode):
    package = root / PACKAGE.relative_to(REPO)
    name = "RESULT.json" if mode == "result" else "WITNESS.json"
    if mode in ("source", "repinned-source"):
        path = root / "research/p112-query-series-transfer/PREDECESSOR-TEMPLATES.json"
    else:
        path = package / name
    data = json.loads(path.read_bytes())
    if mode == "result":
        data["safe"] += 1
    elif mode == "witness":
        data["readers"][0][0] += 1
    else:
        data["points"][0][3] = [1, 0, 0]
    path.write_text(json.dumps(data))
    if mode == "repinned-source":
        pins = json.loads((package / "SOURCES.json").read_bytes())
        for row in pins["files"]:
            if row["path"] == path.relative_to(root).as_posix():
                row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        (package / "SOURCES.json").write_text(json.dumps(pins))


def main():
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    inputs = [REPO / row["path"] for row in pins["files"] if row["usage"] == "input"]
    files = [p for p in PACKAGE.iterdir() if p.is_file() and not p.is_symlink()]
    require(len(files) <= 24 and len(inputs) == 4, "copy capacity")
    hashes = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files + inputs
    }
    with tempfile.TemporaryDirectory(prefix="multiport-controls-") as temporary:
        root = Path(temporary)
        for source in files + inputs:
            copy_file(source, root / source.relative_to(REPO))
        run(root, True, "PASS_")
        for mode, expected in (
            ("result", "result"),
            ("witness", ("literal product", "endpoint")),
            ("source", "source hash"),
            ("repinned-source", "base transfer"),
        ):
            # Restore all authenticated bytes between independent fault cases.
            for source in files + inputs:
                (root / source.relative_to(REPO)).write_bytes(source.read_bytes())
            mutate(root, mode)
            run(root, False, expected)
        for source in files + inputs:
            (root / source.relative_to(REPO)).write_bytes(source.read_bytes())
        run(root, True, "PASS_")
    require(
        hashes
        == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files + inputs},
        "canonical bytes unchanged",
    )
    print("PASS_MULTIPORT_CONTROLS: 8 rejecting and 4 positive optimized CLI runs")


if __name__ == "__main__":
    main()
