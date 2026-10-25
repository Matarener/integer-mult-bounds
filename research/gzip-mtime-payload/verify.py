#!/usr/bin/env python3
"""Reproduce one gzip header mismatch and compare the payload.

Two containers of one payload differ in the four mtime bytes. A container
digest rejects the alternate container. The decompressed digest accepts it.
This checker does not import the historical balanced-split verifier.
"""

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_GZIP_MTIME_PAYLOAD container_check_rejects_alternate=true no_new_kappa"
PAYLOAD = b'{"word":' + b"1," * 200 + b'"end":1}\n'


def fail(message):
    raise SystemExit("FAIL_GZIP_MTIME_PAYLOAD " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def container_matches(blob, digest):
    return hashlib.sha256(blob).hexdigest() == digest


def payload_matches(blob, digest):
    return hashlib.sha256(gzip.decompress(blob)).hexdigest() == digest


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {"research/gzip-container-reproducibility/README.md"}
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    note = (ROOT / "research/gzip-container-reproducibility/README.md").read_text(encoding="utf-8")
    require(
        "1. **A check must compare payloads, not containers.**" in note,
        "the payload convention moved",
    )
    require(
        "asserts `digest(word) == meta['gzip_sha256']`" in note,
        "the required container digest moved",
    )
    pinned = gzip.compress(PAYLOAD, compresslevel=9, mtime=0)
    alternate = gzip.compress(PAYLOAD, compresslevel=9, mtime=1)
    payload_sha = hashlib.sha256(PAYLOAD).hexdigest()
    require(pinned[4:8] == b"\x00\x00\x00\x00", "the pinned header is not mtime zero")
    require(alternate[4:8] == b"\x01\x00\x00\x00", "the alternate header is not mtime one")
    require(
        not container_matches(alternate, hashlib.sha256(pinned).hexdigest()),
        "the container digest accepted the other mtime",
    )
    require(payload_matches(pinned, payload_sha) and payload_matches(alternate, payload_sha), "a payload check rejected the word")
    return {
        "payload_sha256": payload_sha,
        "mtime_bytes_differ": True,
        "container_check_rejects_alternate": True,
        "payload_check_accepts_alternate": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
