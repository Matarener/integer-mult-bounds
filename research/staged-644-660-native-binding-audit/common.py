# SPDX-License-Identifier: Apache-2.0
"""Bounded source loading for the staged 644/660 native-binding audit.

Adapted from research/rank7-group-d-native-widths-audit/common.py (Wentao Li).
"""

import gzip
import hashlib
import io
import json
import sys
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = "research/staged-644-660-native-binding-audit/inputs/"
SNAPSHOT = "research/staged-644-660-width-reduction/"
PR3605 = "3efbb5de06a49ffeea6684482f2d3fe48cdca3fb"
PR3642 = "6568db75adbb61437190545f6fef1534c70e91e5"
PR3653 = "607a09ff441c79b215a8127a81f4cc70021d0d9b"
PR3682 = "431e6c6023ef352c41696469de7fb614cd4ded8c"
# Consumer words that retime the 644/660 releases: package copy stem -> the same
# bytes pinned at each PR head under its original path ({tag} is the provider).
CONSUMERS = {
    "RETIMED644-660": {
        PR3642: "research/staged-release-retiming-t530/local-audit/words/RETIMED644-660-{tag}.json.gz",
        PR3653: "research/retimed-t488-composition/local-audit/words/RETIMED644-660-{tag}.json.gz"},
    "DELAYED": {PR3682: "research/staged-donor-release/lead1-words/DELAYED-{tag}.json.gz"},
}
# LOCAL-CHECKS.json receipts recorded by each consumer's own native run.
RECEIPTS = {
    "RETIMED644-660": {PR3642: "research/staged-release-retiming-t530/local-audit/receipts/"
                               "native-{tag}/native/local/LOCAL-CHECKS.json"},
    "DELAYED": {PR3682: "research/staged-donor-release/evidence/native-{tag}/LOCAL-CHECKS.json"},
}
# The release donors whose climbs the consumer words merge.
DONORS = (640, 656)
PARENT = "research/rank7-coupled-586-588-carrier-fold/edits/"
ENGINE = "research/t74-native-fast/vendor/native/new/code/borrow/"
COMPILER = ENGINE + "vendor/clifford/clifford_exact.py"
KERNEL = "research/frontier1094-recipes-exact-seed76/clifford.py"
PROVIDERS = ("base", "extra")
HELPERS = (644, 660)
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
ENTRANCE = [429, 30]
PARENT_ENTRANCE = [30]
# Same dimension as ENTRANCE and in reduced echelon form; it contains 429 but not 30.
WRONG_ENTRANCE = [429, 18]
# The contained line 429 (dimension one, so a different native width).
CONTAINED_LINE = [429]
LIMIT = 64 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def decode(raw, compressed=False):
    if compressed:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "decoded input capacity")
    return json.loads(raw, object_pairs_hook=unique)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def authenticate(root=ROOT):
    rows = decode((PACKAGE / "SOURCES.json").read_bytes())["files"]
    pins = {r["path"]: r["sha256"] for r in rows if r["usage"] == "input"}
    declared = set(decode((PACKAGE / "VERIFY.json").read_bytes())["inputs"])
    require(set(pins) == declared and len(pins) <= 16, "exact live input inventory")
    # Package-local copies of PR3605's and the consumers' words: their bytes must
    # equal the provenance rows pinned at each PR head under the original path.
    for tag in PROVIDERS:
        pins[staged_name(tag)] = pinned(rows, PR3605, SNAPSHOT + f"STAGED644-660-{tag}.json.gz")
        for stem in CONSUMERS:
            pins[consumer_name(stem, tag)] = agreed(rows, CONSUMERS[stem], tag)
    blobs = {}
    for name, sha in pins.items():
        path = root / name
        require(path.stat().st_size <= LIMIT, "raw input capacity")
        raw = path.read_bytes()
        require(digest(raw) == sha, "source SHA256: " + name)
        blobs[name] = raw
    return blobs


def pinned(rows, head, origin):
    row = [r for r in rows if r["path"] == origin]
    require(len(row) == 1 and row[0]["usage"] == "provenance" and
            row[0].get("pin") == f"head:{head}:{origin}", "snapshot provenance pin")
    return row[0]["sha256"]


def agreed(rows, origins, tag):
    """One SHA-256 shared by every PR head that carries the same file."""
    shas = {pinned(rows, head, path.format(tag=tag)) for head, path in origins.items()}
    require(len(shas) == 1, "identical bytes at every pinned PR head")
    return shas.pop()


def recorded_receipts():
    rows = decode((PACKAGE / "SOURCES.json").read_bytes())["files"]
    return {stem: {tag: agreed(rows, RECEIPTS[stem], tag) for tag in PROVIDERS}
            for stem in CONSUMERS}


def staged_name(tag):
    return LOCAL + f"STAGED644-660-{tag}.json.gz"


def consumer_name(stem, tag):
    return LOCAL + f"{stem}-{tag}.json.gz"


def parent_name(tag):
    return PARENT + f"FINAL-WORD-{tag}.json.gz"


def module(raw, name):
    """Compile authenticated bytes directly, without consulting a .pyc file."""
    result = types.ModuleType(name)
    sys.modules[name] = result
    exec(compile(raw, name, "exec"), result.__dict__)
    return result


def reject(action, reason):
    try:
        action()
    except (ValueError, AssertionError) as error:
        return str(error)
    raise ValueError("control accepted: " + reason)
