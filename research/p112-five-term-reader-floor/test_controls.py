"""Optimized CLI fault controls. Nick Petalas. Apache-2.0."""

import itertools as it
import json
import os
import stat
import subprocess
import sys
import tempfile
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_bytes(path):
    with path.open("rb") as stream:
        raw = stream.read(131074)
    require(len(raw) <= 131072, "control input bound")
    return raw


def private_copy(source, destination, expected):
    original = source.lstat()
    require(stat.S_ISREG(original.st_mode), "copy regular source")
    with source.open("rb") as reader:
        opened = os.fstat(reader.fileno())
        require(
            (opened.st_dev, opened.st_ino) == (original.st_dev, original.st_ino),
            "copy stable source",
        )
        raw = reader.read(131073)
    require(len(raw) <= 131072, "copy input bound")
    require(sha256(raw).digest() == expected, "copy authenticated source")
    with destination.open("xb") as writer:
        copied = os.fstat(writer.fileno())
        require(
            stat.S_ISREG(copied.st_mode) and copied.st_uid == os.getuid(),
            "copy owned regular destination",
        )
        require(
            (copied.st_dev, copied.st_ino) != (original.st_dev, original.st_ino),
            "copy distinct inode",
        )
        require(writer.write(raw) == len(raw), "copy complete write")
    require(
        sha256(bounded_bytes(destination)).digest() == expected,
        "copy authenticated bytes",
    )
    after = source.lstat()
    require(
        (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        == (original.st_dev, original.st_ino, original.st_size, original.st_mtime_ns),
        "copy source identity",
    )
    require(sha256(bounded_bytes(source)).digest() == expected, "copy source unchanged")


def copy_controls(private, source, expected):
    existing = private / "existing"
    existing.write_bytes(b"retained")
    try:
        private_copy(source, existing, expected)
    except FileExistsError:
        require(bounded_bytes(existing) == b"retained", "exclusive copy preserved")
    else:
        raise ValueError("exclusive copy must reject")
    alias = private / "source-alias"
    alias.symlink_to(source)
    try:
        private_copy(alias, private / "forbidden", expected)
    except ValueError as error:
        require(str(error) == "copy regular source", "symlink copy diagnostic")
    else:
        raise ValueError("symlink copy must reject")
    alias.unlink()
    existing.unlink()


def invoke(package, script, expected=None):
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(package / script)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if expected is None:
        require(
            result.returncode == 0 and "PASS_" in result.stdout,
            "positive CLI: " + result.stderr,
        )
    else:
        require(
            result.returncode != 0 and expected in result.stderr,
            "negative CLI: " + result.stdout + result.stderr,
        )
    return result.returncode


def encode(value):
    return (json.dumps(value, indent=2) + "\n").encode()


def corrupt(package, fault):
    path = package / "TEMPLATES.json"
    data = json.loads(bounded_bytes(path))
    if fault == "missing-type":
        data["types"].pop()
    elif fault == "zero-point":
        data["types"][0]["points"][0] = [0, 0, 0]
    elif fault == "wrong-line":
        data["types"][0]["lines"] = [7]
    elif fault == "wrong-polynomial":
        data["polynomial"] = 17
    elif fault == "wrong-result":
        path = package / "RESULT.json"
        data = json.loads(bounded_bytes(path))
        data["primary"]["rank3_types"] = 22
        data["independent"]["labeled_systems"] = 8389
    elif fault == "nonfano-binary":
        path = package / "PREDECESSOR-TEMPLATES.json"
        data = json.loads(bounded_bytes(path))
        data["points"][0] = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
        ]
    elif fault == "oversized-input":
        path.write_bytes(b" " * 131073)
        return
    else:
        raise ValueError("unknown fault")
    raw = encode(data)
    path.write_bytes(raw)
    if fault == "nonfano-binary":
        receipt = package / "SOURCE-CLOSURE.json"
        rows = json.loads(bounded_bytes(receipt))
        for row in rows:
            if row["local_path"] == path.name:
                row["sha256"] = sha256(raw).hexdigest()
                row["git_blob"] = sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw,
                    usedforsecurity=False,
                ).hexdigest()
        receipt.write_bytes(encode(rows))


def main():
    sources = sorted(it.islice(HERE.iterdir(), 33))
    require(len(sources) <= 32, "package file capacity")
    require(
        all(stat.S_ISREG(p.lstat().st_mode) for p in sources), "package regular files"
    )
    originals = {p.name: bounded_bytes(p) for p in sources}
    cases = [
        ("missing-type", "rank-three template count", "independent template count"),
        ("zero-point", "template subset rank", "nonzero points"),
        (
            "wrong-line",
            "classification coverage",
            "independent classification coverage",
        ),
        ("wrong-polynomial", "field embedding", "independent polynomial"),
        ("wrong-result", "result receipt", "independent result receipt"),
        ("nonfano-binary", "reader implication", "independent reader transfer"),
        ("oversized-input", "input capacity", "input bound"),
    ]
    with tempfile.TemporaryDirectory(prefix="five-term-controls-") as directory:
        private = Path(directory)
        for source in sources:
            private_copy(
                source, private / source.name, sha256(originals[source.name]).digest()
            )
        copy_controls(private, sources[0], sha256(originals[sources[0].name]).digest())
        for script in ("verify.py", "independent.py"):
            invoke(private, script)
        for fault, primary, independent in cases:
            corrupt(private, fault)
            invoke(private, "verify.py", primary)
            invoke(private, "independent.py", independent)
            for name, raw in originals.items():
                (private / name).write_bytes(raw)
        for script in ("verify.py", "independent.py"):
            invoke(private, script)
    require(
        all(bounded_bytes(p) == originals[p.name] for p in sources),
        "source bytes preserved",
    )
    print(
        "PASS_FIVE_TERM_CONTROLS faults=7 optimized_cli=18 copy_controls=2 source_immutable"
    )


if __name__ == "__main__":
    main()
