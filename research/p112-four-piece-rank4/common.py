"""Authenticated P112 model, adapted from PR3418. Apache-2.0.

Retains its geometry/authentication adapter; imports no predecessor theorem.
"""

import hashlib
import json
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
DATA = "research/one-sided-six-multisets/data/data.txt"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    require(path.is_file() and path.stat().st_size <= 2_000_000, "JSON size/path")
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def same_json(left, right):
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def rank_labels(values):
    basis = [0] * 9
    for original in values:
        value = original
        for pivot in range(8, -1, -1):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(bool(row) for row in basis)


def authenticated_inputs():
    sources = read_json(HERE / "SOURCES.json")
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    require({row["path"] for row in rows} == {GEOMETRY, DATA}, "input inventory")
    content = {}
    for row in rows:
        path = ROOT
        for part in Path(row["path"]).parts:
            path /= part
            require(not path.is_symlink(), "linked source input")
        require(path.is_file() and path.stat().st_size <= 2_000_000, "source size/path")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source digest")
        content[row["path"]] = raw
    return content


def model():
    content = authenticated_inputs()
    geometry = types.ModuleType("authenticated_geometry")
    exec(compile(content[GEOMETRY], GEOMETRY, "exec"), geometry.__dict__)
    roots, live, live_labels, coordinates = geometry.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(c)) for c in coordinates
    )
    require(
        len(set(labels)) == 120 and rank_labels(labels) == 9,
        "full label rank/inventory",
    )
    rows = content[DATA].decode().splitlines()
    require(tuple(map(int, rows[0].split())) == live_labels, "literal labels")
    require(
        tuple(tuple(map(int, row.split())) for row in rows[2:114]) == live,
        "literal live roots",
    )
    return geometry, roots, live, labels, coordinates
