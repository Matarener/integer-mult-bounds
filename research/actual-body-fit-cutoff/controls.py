"""Real optimized CLI rejection controls using private byte copies. Apache-2.0."""

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copy_regular(source, destination):
    before = source.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(), "owned regular source")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as handle:
        require(handle.write(source.read_bytes()) == before.st_size, "complete byte copy")
    after = destination.lstat()
    require(
        (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino), "distinct destination inode"
    )
    require(source.read_bytes() == destination.read_bytes(), "byte-identical copy")


def export(root):
    files = sorted(PACKAGE.glob("*"))
    require(len(files) <= 32, "package member capacity")
    for source in files:
        require(source.is_file() and not source.is_symlink(), "flat regular package")
        copy_regular(source, root / source.relative_to(ROOT))
    inputs = json.loads((PACKAGE / "VERIFY.json").read_text())["inputs"]
    require(type(inputs) is list and len(inputs) <= 16, "input capacity")
    for relative in inputs:
        copy_regular(ROOT / relative, root / relative)


def child(root, script, accepted):
    argv = [
        sys.executable,
        "-I",
        "-O",
        "-W",
        "error",
        "-B",
        str(root / "research/actual-body-fit-cutoff" / script),
    ]
    completed = subprocess.run(
        argv, cwd=root, text=True, capture_output=True, timeout=30, check=False
    )
    require((completed.returncode == 0) is accepted, "actual optimized CLI decision")
    if accepted:
        require(bool(completed.stdout.strip()), "positive control did real work")
    return dict(
        argv=argv, exit=completed.returncode, stdout=completed.stdout, stderr=completed.stderr
    )


def replacements(root):
    package = root / "research/actual-body-fit-cutoff"
    result = package / "RESULT.json"
    primary = package / "cutoff.py"
    oracle = package / "independent.py"
    source = root / "research/physical-ordinary-interchange/encoded.py"
    raw = result.read_bytes()
    return (
        (result, raw.replace(b'"cutoff": 245767', b'"cutoff": 245766'), "verify.py"),
        (result, raw.replace(b'"boundary": 245766', b'"boundary": 245766.0'), "verify.py"),
        (result, b'{"cutoff":245767,"cutoff":245767}', "verify.py"),
        (primary, primary.read_bytes().replace(b"witness=7", b"witness=2"), "verify.py"),
        (source, source.read_bytes() + b"\n# altered source\n", "verify.py"),
        (oracle, oracle.read_bytes().replace(b"* 42", b"* 41"), "independent.py"),
    )


def main():
    receipts = []
    with tempfile.TemporaryDirectory(prefix="actual-body-controls-") as temporary:
        root = Path(temporary)
        export(root)
        for script in ("verify.py", "independent.py"):
            receipts.append(child(root, script, True))
        for path, changed, script in replacements(root):
            original = path.read_bytes()
            require(changed != original, "mutant must change bytes")
            try:
                require(path.write_bytes(changed) == len(changed), "complete mutant write")
                receipts.append(child(root, script, False))
            finally:
                require(path.write_bytes(original) == len(original), "complete restoration")
    print(json.dumps(dict(accepted=2, rejected=6, children=receipts), sort_keys=True))


if __name__ == "__main__":
    main()
