"""Bounded exact model and source binding. Apache-2.0."""

import hashlib
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "6f100d4bb5083f8c35d96fd95a539811c62f245c"
INPUTS = {
    "research/p112-root-simplex-exclusion/geometry.py": (
        "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021"
    ),
    "research/p112-mixed566-cut32/PROOF.md": (
        "fd34597aa7e0e358cf2cb20ac71d597f24dbf7a1b90570f025f8b79950dcd43d"
    ),
    "research/p112-mixed566-cut33/PROOF.md": (
        "09050050da60676b68454047f13813ea3294a759626ce60bfeed8c24d76e455a"
    ),
    "research/d6-axis-concentration14/PROOF.md": (
        "ccff2c13d4ac590646002f198a4d729a6b5f9b48fba17493a63c8fa461f7ba55"
    ),
    "research/e8-a2-joint-incidence20/PROOF.md": (
        "c994ec3b6833f05f460880503a7c314ef331d5714711303a4e0cf459ea7c251b"
    ),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "regular JSON file")
    raw = path.read_bytes()
    require(len(raw) <= 200_000, "JSON size bound")
    return json.loads(raw)


def authenticate(root=ROOT, package=HERE):
    manifest = read_json(package / "SOURCES.json")
    require(manifest["base_commit"] == BASE, "scientific baseline")
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(rows) == len(INPUTS), "complete input inventory")
    require(
        {row["path"]: row["sha256"] for row in rows} == INPUTS,
        "fixed input paths, hashes and usage",
    )
    payloads = {}
    for path, digest in INPUTS.items():
        source = root / path
        require(source.is_file() and not source.is_symlink(), "regular source")
        raw = source.read_bytes()
        require(len(raw) <= 200_000, "source size bound")
        require(hashlib.sha256(raw).hexdigest() == digest, "source SHA256: " + path)
        payloads[path] = raw
    return payloads


def geometry():
    payloads = authenticate()
    path = "research/p112-root-simplex-exclusion/geometry.py"
    module = ModuleType("authenticated_geometry")
    exec(compile(payloads[path], path, "exec"), module.__dict__)
    roots, points, _, coordinates = module.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    require(len(roots) == len(set(labels)) == 120, "distinct full-root labels")
    return module, roots, points, labels, coordinates


def basis(values, bits=9):
    require(len(values) <= 120 and bits in (9, 18), "basis dimensions")
    pivots = [0] * bits
    for value in values:
        require(type(value) is int and 0 <= value < 1 << bits, "binary label")
        for bit in range(bits - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return tuple(x for x in pivots if x)


def coordinates(values):
    generators = basis(values)
    require(len(generators) <= 8, "coordinate capacity")
    mapping = {0: 0}
    for j, value in enumerate(generators):
        mapping.update({x ^ value: y ^ (1 << j) for x, y in list(mapping.items())})
    return mapping


def digest(masks):
    return hashlib.sha256(json.dumps(sorted(masks)).encode()).hexdigest()


def same(actual, expected):
    require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "exact result receipt including JSON types",
    )
