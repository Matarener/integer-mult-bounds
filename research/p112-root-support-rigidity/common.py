"""Bounded exact inputs for the P112 root-support lemma. Apache-2.0."""

import hashlib
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
PINS = {
    GEOMETRY: "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021",
    "research/p112-root-simplex-exclusion/PROOF.md": "2b5d70570e3a13d2ccc71c1fc7eef113f0d049993cb9bb24007166223ac7b734",
    "research/p112-six-piece-concentration/README.md": "39ed60e8088e7c21dfe17cc93c600cf398d26676ab38da79601988668cddfa62",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    require(len(pairs) == len({key for key, _ in pairs}), "duplicate JSON key")
    return dict(pairs)


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "regular JSON input")
    raw = path.read_bytes()
    require(len(raw) <= 200_000, "JSON byte bound")
    return json.loads(raw, object_pairs_hook=unique_object)


def same_json(left, right):
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def model(root=ROOT):
    raw_geometry = None
    manifest = read_json(HERE / "SOURCES.json")
    inputs = {row["path"]: row for row in manifest["files"] if row["usage"] == "input"}
    require(set(inputs) == set(PINS), "exact source inventory")
    for name, digest in PINS.items():
        source = root / name
        require(source.is_file() and not source.is_symlink(), "regular source input")
        raw = source.read_bytes()
        require(len(raw) <= 100_000, "source byte bound")
        require(hashlib.sha256(raw).hexdigest() == digest, "source SHA256")
        require(inputs[name]["sha256"] == digest, "source manifest SHA256")
        if name == GEOMETRY:
            raw_geometry = raw
    require(raw_geometry is not None, "geometry input present")
    module = ModuleType("authenticated_geometry")
    exec(compile(raw_geometry, GEOMETRY, "exec"), module.__dict__)  # noqa: S102
    roots, live, _, coordinates = module.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    require(len(roots) == len(set(labels)) == 120, "root-label bijection")
    require(len(live) == 112 and all(x & 1 for x in labels), "leading-one P112")
    return module, roots, live, labels


def reflect(roots, normal, dot, canonical):
    require(len(roots) == 120 and dot(normal, normal) == 8, "reflection dimensions")
    result = []
    lookup = {root: i for i, root in enumerate(roots)}
    for root in roots:
        pairing = dot(root, normal)
        require(pairing % 4 == 0, "integral reflection")
        image = canonical(
            tuple(x - pairing // 4 * y for x, y in zip(root, normal, strict=True))
        )
        require(image in lookup, "reflection preserves roots")
        result.append(lookup[image])
    require(len(set(result)) == 120, "reflection permutation")
    return tuple(result)


def section_check(mask, off, permutation, capacity):
    require(type(mask) is int and 0 <= mask < 1 << 120, "120-bit root section")
    require(
        mask.bit_count() == capacity and mask & ~off == 0,
        "whole section lies off the normal root",
    )
    require(mask & 1 == 0, "canonical normal root excluded")
    image = sum(1 << permutation[i] for i in range(120) if mask >> i & 1)
    require(image == mask, "reflection-closed section")


def mask_digest(masks):
    require(len(masks) <= 4096, "critical section count bound")
    return hashlib.sha256(
        b"".join(x.to_bytes(15, "big") for x in sorted(masks))
    ).hexdigest()
