#!/usr/bin/env python3
"""Predicate checks for a one-byte mtime mismatch."""

import gzip
import hashlib

from verify import container_matches, payload_matches


def main():
    raw = b"ab"
    pinned = gzip.compress(raw, compresslevel=9, mtime=0)
    alternate = gzip.compress(raw, compresslevel=9, mtime=1)
    digest = hashlib.sha256(raw).hexdigest()
    assert payload_matches(alternate, digest)
    assert not container_matches(alternate, hashlib.sha256(pinned).hexdigest())
    print("PASS_GZIP_MTIME_PAYLOAD_TEST")


if __name__ == "__main__":
    main()
