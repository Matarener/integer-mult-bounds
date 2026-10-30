#!/usr/bin/env python3
"""Read the first component of the published frame-1 vector.

Frame 1 is the stored nine coordinate axes. The formula returns the constant
vector for rank 9. The other 1,003 frames are not evaluated.
"""

import gzip
import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
NATIVE = ROOT / "research/qq16-native-dirty-fault/native.py"
CHECKER = ROOT / "research/qq16-native-dirty-fault/verify.py"
ARCHIVE = ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz"
MEMBER = "slots/local/CANONICAL-WORD.json.gz"
MEMBER_SHA = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
AXES = (256, 128, 64, 32, 16, 8, 4, 2, 1)
MARKER = "PASS_QQ16_FRAME1_COMPONENT first=1+0i no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_FRAME1_COMPONENT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            high = value.bit_length() - 1
            if high not in pivots:
                pivots[high] = value
                break
            value ^= pivots[high]
    return len(pivots)


def constant_branch(axes):
    """The published early return: rank 0 and rank 9 both fix the constant vector."""
    return len(axes) in (0, 9) and rank(axes) == len(axes) and all(0 < axis < 512 for axis in axes)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/qq16-native-dirty-fault/native.py",
        "research/qq16-native-dirty-fault/verify.py",
        "research/community-frontier1042-audit/selected-replay.tar.gz",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def frame_one():
    with tarfile.open(ARCHIVE) as archive:
        matches = [member for member in archive.getmembers() if member.name == MEMBER]
        require(len(matches) == 1 and matches[0].isfile(), "canonical word missing")
        raw = archive.extractfile(matches[0]).read()
    require(hashlib.sha256(raw).hexdigest() == MEMBER_SHA, "canonical word moved")
    word = json.loads(gzip.decompress(raw))
    return tuple(word["frames"][1])


def evaluate():
    authenticate()
    formula = NATIVE.read_text(encoding="utf-8")
    checker = CHECKER.read_text(encoding="utf-8")
    require("ONE = ((1,) * DIM, (0,) * DIM, 0)" in formula, "the constant vector moved")
    require("if r in (0, 9):\n        return ONE" in formula, "the rank-9 return moved")
    require('frames[0] == frames[1] == N.ONE' in checker, "the frame-1 binding moved")
    axes = frame_one()
    require(axes == AXES, "the stored frame-1 axes moved")
    require(constant_branch(axes), "frame 1 left the constant branch")
    return {
        "frame": 1,
        "axes": list(AXES),
        "rank": 9,
        "first_real": 1,
        "first_imag": 0,
        "exponent": 0,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
