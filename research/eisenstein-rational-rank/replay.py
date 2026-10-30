"""Optional complete replay, keeping the predecessor K adapter in both modes."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from rational_rank import rank, require

SOURCE = "research/eisenstein-reduction-copy-floor/verify.py"
K_SOURCE = "research/eisenstein-integer-rank/integer_rank.py"
EXPECTED_CALLS = {"K": 359, "F4": 311, "Q": 209}


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA: " + row["path"])
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(blob == row["git_blob"], "source blob: " + row["path"])


def load_module(name, path):
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None, "missing loader")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def load():
    authenticate()
    return load_module("original_floor", ROOT / SOURCE), load_module("integer_k_rank", ROOT / K_SOURCE)


def install(old, k_engine, original_mode=False):
    original = old.rank
    calls = dict.fromkeys(EXPECTED_CALLS, 0)

    def dispatch(matrix, field="K"):
        require(field in calls, "unexpected coefficient field")
        calls[field] += 1
        if field == "K":
            return k_engine.rank(matrix)
        if field == "Q" and not original_mode:
            return rank(matrix)
        return original(matrix, field)

    old.rank = dispatch
    return calls


def execute(original_mode=False):
    old, k_engine = load()
    calls = install(old, k_engine, original_mode)
    old.main()
    require(calls == EXPECTED_CALLS, "complete rank-call coverage changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", action="store_true", help="retain original Q-rank")
    args = parser.parse_args()
    execute(args.original)


if __name__ == "__main__":
    main()
