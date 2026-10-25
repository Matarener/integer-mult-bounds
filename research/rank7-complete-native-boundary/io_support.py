# SPDX-License-Identifier: Apache-2.0
"""Authenticate explicit inputs before loading credited checking/producer code."""

import gzip
import hashlib
import json
import sys
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PRIOR = "research/rank7-v45-native-cone-seed78/"
PEER = "research/rank7-peer-private-free-audit/"
LIMIT = 64 * 1024 * 1024


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def unique(pairs):
    value = dict(pairs)
    require(len(value) == len(pairs), "duplicate JSON key")
    return value


def read(path):
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "input byte capacity")
    return raw


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inputs(root=ROOT):
    pins = decode(read(PACKAGE / "SOURCES.json"))["files"]
    declared = decode(read(PACKAGE / "VERIFY.json"))["inputs"]
    active = [r for r in pins if r["usage"] == "input"]
    require(len(active) == len(declared) == len(set(declared)), "unique source closure")
    require(
        len(active) <= 32 and {r["path"] for r in active} == set(declared),
        "exact declared source closure",
    )
    blobs = {}
    for row in active:
        path = root / row["path"]
        require(path.is_file() and not path.is_symlink(), "regular source file")
        raw = read(path)
        require(sha(raw) == row["sha256"], "source SHA256: " + row["path"])
        blobs[row["path"]] = raw
    return blobs


def result(provider):
    path = PACKAGE / ("RESULT-" + provider + ".json.gz")
    with gzip.open(path, "rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "decoded result capacity")
    return decode(raw)


def load(blobs, path, name):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    sys.modules[name] = module
    exec(compile(blobs[path], str(ROOT / path), "exec"), module.__dict__)
    return module


def modules(blobs):
    result = {
        name: load(blobs, PRIOR + name + ".py", "complete_native_" + name)
        for name in ("source", "native", "audit", "support")
    }
    result["algebra"] = load(blobs, PEER + "lifetimes.py", "complete_native_algebra")
    result["endpoints"] = load(
        blobs,
        "research/rank7-v45-native-endpoint/endpoints.py",
        "complete_native_source_covectors",
    )
    result["kernel"] = load(blobs, result["support"].KERNEL, "complete_native_kernel")
    return result
