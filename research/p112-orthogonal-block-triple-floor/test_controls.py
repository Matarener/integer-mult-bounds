"""Optimized actual-CLI rejection controls on owned byte copies. Apache-2.0."""

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
PACKAGE = HERE.relative_to(ROOT)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def copy_regular(source, destination):
    before = source.lstat()
    need(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular source",
    )
    need(
        source.absolute() == source.resolve() and before.st_size <= 1048576,
        "source alias/capacity",
    )
    raw = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        need(stream.write(raw) == len(raw), "complete copy")
    after = destination.lstat()
    need(
        stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid(),
        "owned regular destination",
    )
    need(
        (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
        "inode-disjoint copy",
    )
    current = source.lstat()
    need(
        (
            current.st_dev,
            current.st_ino,
            current.st_mode,
            current.st_uid,
            current.st_size,
            current.st_mtime_ns,
        )
        == (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_uid,
            before.st_size,
            before.st_mtime_ns,
        ),
        "stable source identity",
    )
    need(
        source.read_bytes() == raw and destination.read_bytes() == raw,
        "stable byte copy",
    )


def inputs():
    manifest = json.loads((HERE / "VERIFY.json").read_bytes())
    paths = list(HERE.iterdir()) + [ROOT / p for p in manifest["inputs"]]
    need(1 <= len(paths) <= 32 and all(p.is_file() for p in paths), "control inventory")
    return sorted(set(paths))


def run(root, script, error=None):
    cmd = [sys.executable, "-I", "-O", "-Werror", "-B", str(root / PACKAGE / script)]
    result = subprocess.run(
        cmd, cwd=root, capture_output=True, text=True, timeout=60, check=False
    )
    if error is None:
        need(
            result.returncode == 0 and result.stdout.startswith("PASS_"),
            "positive actual CLI",
        )
    else:
        need(
            result.returncode != 0 and error in result.stderr,
            "negative actual CLI: " + error,
        )


def mutate(root, name):
    package = root / PACKAGE
    # Every mutation target is an exclusive owned regular byte copy.
    if name in ("gram", "plane", "partial"):
        path = package / "FIXTURES.json"
        data = json.loads(path.read_bytes())
        if name == "gram":
            data[0]["groups"][0]["basis"][0] = data[0]["groups"][0]["basis"][1]
        elif name == "plane":
            data[1]["groups"][0]["planes"][:2] = [[0, 2], [1, 3]]
        else:
            data[1]["groups"][0]["atom_ids"][0] = 1
        path.write_text(json.dumps(data))
    elif name == "result":
        path = package / "RESULT.json"
        data = json.loads(path.read_bytes())
        data["fixtures"][0]["minimum"] += 1
        path.write_text(json.dumps(data))
    elif name == "pattern":
        path = package / "verify.py"
        raw = path.read_text()
        old = "(3, 12), (5, 10), (6, 9)"
        need(raw.count(old) == 1, "pattern mutation site")
        path.write_text(raw.replace(old, "(1, 12), (5, 10), (6, 9)"))
    elif name == "coefficient":
        path = package / "independent.py"
        raw = path.read_text()
        need(raw.count("2 * w)") == 1, "coefficient mutation site")
        path.write_text(raw.replace("2 * w)", "3 * w)"))
    else:
        path = (
            package / "RETAINED-PR3549-PROOF.md"
            if name == "retained"
            else root / "research/p112-matroid-reader-transfer/PROOF.md"
        )
        path.write_bytes(b"changed\n" + path.read_bytes())


def main():
    paths = inputs()
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    faults = [
        ("gram", "group Gram-I"),
        ("plane", "plane crosses block"),
        ("partial", "complete block basis"),
        ("result", "result drift"),
        ("pattern", "local table"),
        ("coefficient", "integer target identity"),
        ("retained", "retained drift"),
        ("source", "source drift"),
    ]
    with tempfile.TemporaryDirectory(prefix="orthogonal-block-controls-") as directory:
        base = Path(directory)
        positive = base / "positive"
        for path in paths:
            copy_regular(path, positive / path.relative_to(ROOT))
        run(positive, "verify.py")
        for index, (name, error) in enumerate(faults):
            root = base / str(index)
            for path in paths:
                copy_regular(path, root / path.relative_to(ROOT))
            mutate(root, name)
            run(root, "independent.py" if name == "coefficient" else "verify.py", error)
        run(positive, "independent.py")
    need(
        before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "source unchanged after controls",
    )
    print(
        "PASS_ORTHOGONAL_BLOCK_CONTROLS",
        len(faults),
        "optimized CLI faults; two positives; source unchanged",
    )


if __name__ == "__main__":
    main()
