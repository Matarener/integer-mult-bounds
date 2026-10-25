"""Authenticated inputs and bounded exact arithmetic. Apache-2.0."""

import hashlib
import json
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"


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
    require(not path.is_symlink() and path.stat().st_size <= 524288, "JSON boundary")
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def checked_bytes(root, relative, digest):
    path = root
    for part in Path(relative).parts:
        require(
            part not in (".", "..") and not Path(relative).is_absolute(), "input path"
        )
        path = path / part
        require(not path.is_symlink(), "linked source")
    require(path.is_file() and path.stat().st_size <= 524288, "source boundary")
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, "changed source: " + relative)
    return data


def authenticate(root=ROOT, package=PACKAGE):
    sources = read_json(package / "SOURCES.json")
    rows = [row for row in sources["files"] if row.get("usage") == "input"]
    require(len(rows) == 1 and rows[0]["path"] == GEOMETRY, "geometry pin inventory")
    data = checked_bytes(root, GEOMETRY, rows[0]["sha256"])
    predecessors = read_json(package / "PREDECESSORS.json")
    require(len(predecessors["files"]) == 2, "predecessor inventory")
    for row in predecessors["files"]:
        checked_bytes(package, row["local"], row["sha256"])
    return data


def geometry():
    data = authenticate()
    module = ModuleType("authenticated_geometry")
    exec(compile(data, GEOMETRY, "exec"), module.__dict__)  # noqa: S102 -- pinned source, see ENGINEERING.md
    return module


def primitive(values):
    values = tuple(map(Fraction, values))
    denominator = lcm(*(x.denominator for x in values))
    integers = tuple(int(x * denominator) for x in values)
    divisor = gcd(*integers)
    require(divisor != 0, "zero projective direction")
    integers = tuple(x // divisor for x in integers)
    return max(integers, tuple(-x for x in integers))


def digest_rows(rows):
    encoded = "\n".join(",".join(str(x) for x in row) for row in sorted(rows)) + "\n"
    return hashlib.sha256(encoded.encode()).hexdigest()


def check_result(actual, section):
    expected = read_json(PACKAGE / "RESULT.json")
    expected_json = json.dumps(expected[section], sort_keys=True, separators=(",", ":"))
    actual_json = json.dumps(actual, sort_keys=True, separators=(",", ":"))
    require(expected_json == actual_json, "changed result: " + section)
