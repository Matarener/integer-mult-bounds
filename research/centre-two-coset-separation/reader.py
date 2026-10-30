"""Extract only the reader needed by the additional column-plane test.

The archived prefix and query convention are credited to PR3071/3828.
No predecessor verifier, group census or single-block kernel replay runs.
Produced by Nick Petalas. SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction
from hashlib import sha256
import gzip
import io
import json
import tarfile

from linear import need, rank

ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_HASH = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
MEMBER_HASH = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"


def source_word(root):
    path = root / ARCHIVE
    need(path.is_file() and not path.is_symlink(), "regular archive")
    need(path.stat().st_size <= 8_000_000, "archive size limit")
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == ARCHIVE_HASH, "archive source hash")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        members = archive.getmembers()
        need(len(members) <= 10_000, "archive member limit")
        matches = [member for member in members if member.name == MEMBER]
        need(len(matches) == 1 and matches[0].isfile(), "unique regular word")
        need(matches[0].size <= 2_000_000, "compressed word limit")
        stream = archive.extractfile(matches[0])
        need(stream is not None, "word stream")
        with stream:
            packed = stream.read()
    need(sha256(packed).hexdigest() == MEMBER_HASH, "word source hash")
    decoded = gzip.decompress(packed)
    need(len(decoded) <= 8_000_000, "decoded word limit")
    return json.loads(decoded)


def reader_rows(word):
    prefix = word["precondition"] + word["compensation"] + word["A"]
    need(len(prefix) == 10851 and len(word["centers"]) == 8, "prefix contract")
    result = []
    for center in word["centers"]:
        need(type(center) is int and 0 <= center < 704, "center range")
        row = [Fraction(0)] * 704
        row[center] = Fraction(1)
        for event in reversed(prefix):
            need(event[0] in ("add", "scale"), "prefix instruction")
            target = event[1]
            need(type(target) is int and 0 <= target < 704, "target range")
            if event[0] == "scale":
                need(len(event) == 5 and event[3] != 0, "scale shape")
                row[target] *= Fraction(event[2], event[3])
            else:
                need(len(event) == 6 and event[4] != 0, "addition shape")
                source = event[2]
                need(type(source) is int and 0 <= source < 704, "source range")
                row[source] += Fraction(event[3], event[4]) * row[target]
        result.append(row[:112])
    return result


def plane_certificate(root):
    rows = reader_rows(source_word(root))
    a, b, c = 0, 6, 85
    need(all(r[a] == r[b] + r[c] for r in rows), "distinguished relation")
    need(rank([[r[a], r[b]] for r in rows]) == 2, "triple plane rank")
    outside = []
    for port in range(112):
        value = rank([[r[a], r[b], r[port]] for r in rows])
        need(value == (2 if port in (a, b, c) else 3), "column-plane separation")
        if port not in (a, b, c):
            outside.append(port)
    encoded = json.dumps([[str(x) for x in r] for r in rows], separators=(",", ":"))
    return {"plane_ports": [a, b, c], "outside_plane_columns": len(outside),
            "reader_sha256": sha256(encoded.encode()).hexdigest()}
