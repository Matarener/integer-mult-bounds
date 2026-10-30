#!/usr/bin/env python3
"""Compose integer-labels-v1 and xor-scatter-v1 before checking and export.

Apache-2.0. Prepared with substantial OpenAI Codex assistance. Label validation
is delegated unchanged to PR3100; XOR normalization and checked export retain
Nick Petalas's PR3273 implementation and its predecessor attribution.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SCHEMA = "integer-xor-scatter-v1"
MAX_BYTES = 5 * 1024 * 1024
LABELS = "research/label-coordinate-boundary-audit/boundary.py"
XOR = "research/xor-scatter-boundary/boundary.py"
XOR_PINS = "research/xor-scatter-boundary/SOURCES.json"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
DEPENDENCIES = (LABELS, XOR, XOR_PINS, CHECKER, EXPORTER)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path, compressed=False):
    require(path.stat().st_size <= MAX_BYTES, "input exceeds 5 MiB")
    opener = gzip.open if compressed else open
    with opener(path, "rb") as stream:
        body = stream.read(MAX_BYTES + 1)
    require(len(body) <= MAX_BYTES, "input exceeds 5 MiB")
    return body


def sources(root):
    """Read and authenticate all delegate bytes before executing any of them."""
    pins = json.loads(read_bounded(PACKAGE / "SOURCES.json"))["files"]
    require(type(pins) is list and len(pins) <= 16, "bounded source inventory")
    result = {}
    for path in DEPENDENCIES:
        rows = [row for row in pins if row["path"] == path and row["usage"] == "input"]
        require(len(rows) == 1, "unique source pin: " + path)
        body = read_bounded(root / path)
        require(
            hashlib.sha256(body).hexdigest() == rows[0]["sha256"],
            "source pin mismatch: " + path,
        )
        result[path] = body
    return result


def module(body, path):
    scope = {"__name__": "authenticated_boundary", "__file__": str(path)}
    exec(compile(body, str(path), "exec", optimize=0), scope)  # noqa: S102
    return scope


def execute(mode, input_path, output=None, root=ROOT, scratch=None):
    require(mode in ("check", "export"), "unknown mode")
    require((mode == "export") == (output is not None), "export needs output; check takes none")
    if output is not None:
        require(not output.exists() and not output.is_symlink(), "output already exists")
    raw = read_bounded(input_path, input_path.suffix == ".gz")
    word = json.loads(raw)
    bodies = sources(root)
    labels = module(bodies[LABELS], root / LABELS)
    labels["validate_labels"](word)
    with tempfile.TemporaryDirectory(prefix="integer-xor-", dir=scratch) as temporary:
        directory = Path(temporary)
        private_root = directory / "sources"
        for path, body in bodies.items():
            target = private_root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        snapshot = directory / "word.json.gz"
        snapshot.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
        xor = module(bodies[XOR], private_root / XOR)
        result = xor["execute"](mode, snapshot, output, root=private_root, scratch=directory)
    require(result["schema"] == "xor-scatter-v1", "delegate schema")
    return {**result, "schema": SCHEMA}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "export"))
    parser.add_argument("word", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--scratch", type=Path)
    args = parser.parse_args()
    try:
        result = execute(args.mode, args.word, args.output, scratch=args.scratch)
    except (ValueError, OSError, EOFError, RecursionError, subprocess.TimeoutExpired) as error:
        print(f"REJECT {SCHEMA}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
