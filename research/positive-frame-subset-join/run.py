"""Source-bound complete replay adapter. Produced by Nick Petalas, Apache-2.0."""

import argparse
import hashlib
import json
from pathlib import Path
from types import ModuleType

from fast_support import direct_support_regression, require


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = "research/bit-two-positive-frames-seven-call/verify.py"


def authenticated_bytes(path, expected):
    require(path.stat().st_size <= 1 << 20, "source exceeds one MiB")
    payload = path.read_bytes()
    require(hashlib.sha256(payload).hexdigest() == expected,
            "source hash mismatch: " + str(path))
    return payload


def load_source(root=ROOT):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    require(len(manifest["files"]) <= 16, "too many source rows")
    code = None
    for row in manifest["files"]:
        if row["usage"] == "input":
            payload = authenticated_bytes(root / row["path"], row["sha256"])
            if row["path"] == SOURCE:
                code = payload
    require(code is not None, "missing source program")
    module = ModuleType("positive_frame_source")
    module.__file__ = str(root / SOURCE)
    exec(compile(code, module.__file__, "exec"), module.__dict__)
    return module


def replay(baseline=False):
    source = load_source()
    if not baseline:
        def replacement(profiles, grid=8):
            return direct_support_regression(source, profiles, grid)
        source.direct_support_regression = replacement
    source.main()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true",
                        help="execute every original predicate unchanged")
    args = parser.parse_args()
    replay(args.baseline)


if __name__ == "__main__":
    main()
