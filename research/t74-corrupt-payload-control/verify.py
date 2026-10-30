#!/usr/bin/env python3
"""Audit the T74 corrupted-word control's container digest.

research/t74-pivot566-kernel/verify.py corrupt() recompresses a one-byte
mutation and requires that container digest to equal the committed gauge44
pin. On this zlib the same recompression of the unmutated payload already
misses the pin, so the control does not witness the byte flip. Payload
equality accepts the original word and a level-1 recompression, and rejects
the mutant. The pinned verifier is not edited.
"""

import gzip
import hashlib
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD = "research/t74-pivot566-kernel/inputs/gauge44-word-566.json.gz"
PINS = "research/t74-pivot566-kernel/PINS.json"
VERIFIER = "research/t74-pivot566-kernel/verify.py"
PIN_KEY = "inputs/gauge44-word-566.json.gz"
CORRUPT = (
    "def corrupt():\n"
    "    raw = bytearray(gzip.decompress(words['gauge44'].read_bytes())); "
    "i = raw.index(b'\"B\"') + 40; raw[i] = (raw[i] + 1) % 256\n"
    "    assert hashlib.sha256(gzip.compress(bytes(raw), mtime=0)).hexdigest() "
    "== pins['package']['inputs/gauge44-word-566.json.gz']\n"
)
MARKER = (
    "PASS_T74_CORRUPT_PAYLOAD_CONTROL "
    "unmutated_recompress_matches_pin=false "
    "level1_same_payload=true "
    "mutation_changes_payload=true "
    "no_new_kappa=true"
)


def fail(message):
    raise SystemExit("FAIL_T74_CORRUPT_PAYLOAD_CONTROL " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == {WORD, PINS, VERIFIER}, "input inventory changed")
    for path, row in pinned.items():
        require(file_sha256(ROOT / path) == row["sha256"], "input drift " + path)
    text = (ROOT / VERIFIER).read_text(encoding="utf-8")
    require(CORRUPT in text, "corrupt() no longer matches the audited source")
    pins = json.loads((ROOT / PINS).read_text(encoding="utf-8"))
    require(pins["package"][PIN_KEY] == pinned[WORD]["sha256"], "PINS.json drifted from the word")
    require(pins["package"]["verify.py"] == pinned[VERIFIER]["sha256"], "PINS.json drifted from verify.py")
    return pins["package"][PIN_KEY]


def historical_accepts(payload, pin):
    """Same comparison as corrupt(): recompress with mtime 0 and match the pin."""
    return sha256(gzip.compress(bytes(payload), mtime=0)) == pin


def payload_equal(payload, container):
    return bytes(payload) == gzip.decompress(container)


def mutate(payload):
    raw = bytearray(payload)
    index = raw.index(b'"B"') + 40
    require(0 <= index < len(raw), "mutation index is outside the payload")
    raw[index] = (raw[index] + 1) % 256
    return bytes(raw)


def evaluate(pin):
    container = (ROOT / WORD).read_bytes()
    require(sha256(container) == pin, "the committed container is not the pin")
    require(container[:4] == b"\x1f\x8b\x08\x00", "the committed header is not a gzip member")
    original = gzip.decompress(container)
    mutated = mutate(original)
    level1 = gzip.compress(original, compresslevel=1, mtime=0)
    require(mutated != original, "the one-byte edit did not change the payload")
    require(not historical_accepts(original, pin), "unmutated recompression reproduced the pin")
    require(not historical_accepts(mutated, pin), "mutated recompression reproduced the pin")
    require(gzip.compress(mutated, mtime=0) != gzip.compress(original, mtime=0), "the edit did not change the recompressed container")
    require(payload_equal(original, container), "payload equality rejected the committed word")
    require(payload_equal(original, level1), "payload equality rejected the level-1 recompression")
    require(sha256(level1) != pin, "level-1 recompression matched the committed container")
    require(not payload_equal(mutated, container), "payload equality accepted the mutant")
    require(not payload_equal(mutated, level1), "payload equality accepted the mutant against the recompression")
    # The container test would call the faithful level-1 word a mismatch.
    require(sha256(level1) != sha256(container), "level-1 bytes unexpectedly matched the committed container")
    return {
        "zlib": zlib.ZLIB_VERSION,
        "payload_bytes": len(original),
        "committed_bytes": len(container),
        "level1_bytes": len(level1),
        "unmutated_recompress_matches_pin": False,
        "level1_same_payload": True,
        "mutation_changes_payload": True,
        "no_new_kappa": True,
    }


def main():
    pin = authenticate()
    observed = evaluate(pin)
    require(observed["zlib"] == zlib.ZLIB_VERSION, "zlib identity drifted during the check")
    print(MARKER, flush=True)


if __name__ == "__main__":
    main()
