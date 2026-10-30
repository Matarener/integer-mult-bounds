"""Actual optimized CLI faults on exclusively created regular byte copies."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = (
    "CONFIG.json",
    "WITNESS.json",
    "RESULT.json",
    "ORIGINS.json",
    "PREDECESSOR-MAPS.json",
    "verify.py",
    "independent.py",
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def copy_regular(source, destination):
    before = source.lstat()
    require(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular source",
    )
    payload = source.read_bytes()
    with destination.open("xb") as stream:
        require(stream.write(payload) == len(payload), "complete byte copy")
    after, copied = source.lstat(), destination.lstat()
    require(
        (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino),
        "stable source identity",
    )
    require(
        (before.st_dev, before.st_ino) != (copied.st_dev, copied.st_ino),
        "distinct destination inode",
    )
    require(
        stat.S_ISREG(copied.st_mode) and copied.st_uid == os.getuid(),
        "owned regular destination",
    )
    require(destination.read_bytes() == payload, "byte-copy equality")


def run(root, script, expected):
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONPYCACHEPREFIX"] = str(root / "private-bytecode")
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-O",
            "-X",
            "pycache_prefix=" + str(root / "private-bytecode"),
            "-Werror",
            "-B",
            str(root / script),
        ],
        cwd=root,
        check=False,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if expected is None:
        require(
            result.returncode == 0 and "PASS_TWO_HUB" in result.stdout,
            "positive CLI: " + result.stderr,
        )
    else:
        require(
            result.returncode != 0 and expected in result.stderr,
            "fault diagnostic: " + result.stderr,
        )


def faults():
    return (
        ("CONFIG.json", "geometry", "two-hub geometry"),
        ("CONFIG.json", "premise", "complete obstruction premises"),
        ("WITNESS.json", "reader", "literal reader identity"),
        ("WITNESS.json", "coverage", "literal premise coverage"),
        ("PREDECESSOR-MAPS.json", "star", "retained predecessor bytes"),
        ("RESULT.json", "result", "result mismatch"),
    )


def corrupt(data, kind):
    if kind == "geometry":
        data["queries"][7][4] = 0
    elif kind == "premise":
        data["premises"]["source"].pop()
    elif kind == "reader":
        data["readers"][0][0] = "0"
    elif kind == "coverage":
        data["rows"][0][2] = "g"
    elif kind == "star":
        data["cases"][7]["star_queries"][1][3] = 0
    elif kind == "result":
        data["literal"]["bill"] = 42
    else:
        raise ValueError("unknown fault")


def main():
    originals = {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in FILES
    }
    with tempfile.TemporaryDirectory(prefix="two-hub-controls-") as directory:
        root = Path(directory)
        for name in FILES:
            copy_regular(HERE / name, root / name)
        rejected = positive = 0
        for script in ("verify.py", "independent.py"):
            run(root, script, None)
            positive += 1
            for name, kind, diagnostic in faults():
                path = root / name
                original = path.read_bytes()
                data = json.loads(original)
                corrupt(data, kind)
                path.write_text(json.dumps(data))
                run(root, script, diagnostic)
                rejected += 1
                path.write_bytes(original)
                run(root, script, None)
                positive += 1
        require(
            all(
                hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest
                for name, digest in originals.items()
            ),
            "unchanged source bytes",
        )
    require(rejected == 12 and positive == 14, "control coverage")
    print("PASS_TWO_HUB_CONTROLS rejected=12 positive=14 owned_regular_byte_copies")


if __name__ == "__main__":
    main()
