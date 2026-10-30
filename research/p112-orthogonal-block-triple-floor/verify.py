"""Orthogonal-block triple reader floor. Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[1]
PATTERNS = {
    "MMM": ((3, 12), (5, 10), (6, 9)),
    "VVV": ((7, 12, 11), (7, 10, 13), (7, 9, 14)),
}
QUERY_GROUPS = {"MMM": (7, 7, 7, 7), "VVV": (3, 5, 6, 7)}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    need(path.absolute() == path.resolve() and path.is_file(), "regular input")
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    need(len(raw) <= 1048576, "input capacity")
    return raw


def load(path):
    return json.loads(read(path))


def authenticate():
    manifest = load(HERE / "SOURCES.json")
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    need(1 <= len(rows) <= 12, "source inventory capacity")
    for row in rows:
        path = ROOT / row["path"]
        need(path.is_relative_to(ROOT), "source containment")
        need(hashlib.sha256(read(path)).hexdigest() == row["sha256"], "source drift")
    need(len(manifest["retained_sources"]) == 2, "retained source inventory")
    for row in manifest["retained_sources"]:
        path = HERE / row["local_path"]
        need(path.parent == HERE, "retained path")
        need(hashlib.sha256(read(path)).hexdigest() == row["sha256"], "retained drift")


def rank(columns, width):
    need(0 <= width <= 32 and len(columns) <= 32, "rank capacity")
    pivots = [0] * width
    for original in columns:
        value = original
        need(type(value) is int and 0 <= value < 1 << width, "rank domain")
        for bit in range(width - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(x) for x in pivots)


def dot(a, b):
    return (a & b).bit_count() & 1


def orthonormal(basis):
    return all(
        dot(a, b) == (i == j) for i, a in enumerate(basis) for j, b in enumerate(basis)
    )


def geometry(row):
    atoms, groups = row["atoms"], row["groups"]
    need(type(row["aligned_bases"]) is bool, "aligned declaration domain")
    need(1 <= len(atoms) <= 4 and len(groups) == 3, "fixture capacity")
    frames = [a["frame"] for a in atoms]
    flat = [x for frame in frames for x in frame]
    need(
        len(flat) <= 12 and all(type(x) is int and 0 < x < 4096 for x in flat),
        "frame domain",
    )
    need(
        all(len(f) in (2, 4, 6) for f in frames) and orthonormal(flat),
        "orthogonal atoms",
    )
    labels, planes, parts, memberships = [], [], [], [[], [], []]
    for part, group in enumerate(groups):
        basis, ids, pairs = group["basis"], group["atom_ids"], group["planes"]
        need(
            0 < len(basis) <= 12 and len(basis) == len(ids) and orthonormal(basis),
            "group Gram-I",
        )
        need(all(type(x) is int and 0 < x < 4096 for x in basis), "group domain")
        need(all(type(a) is int and 0 <= a < len(atoms) for a in ids), "atom ids")
        need(
            len(pairs) * 2 == len(basis)
            and sorted(i for p in pairs for i in p) == list(range(len(basis))),
            "complete plane partition",
        )
        for a, frame in enumerate(frames):
            block = [x for x, atom in zip(basis, ids, strict=True) if atom == a]
            need(
                not block or len(block) == len(frame) == rank(frame + block, 12),
                "complete block basis",
            )
            memberships[part].append(bool(block))
            if row["aligned_bases"] and block:
                need(sorted(block) == sorted(frame), "aligned basis declaration")
        offset = len(labels)
        for pair in pairs:
            need(len(pair) == 2 and ids[pair[0]] == ids[pair[1]], "plane crosses block")
            planes.append(tuple(offset + x for x in pair))
            parts.append(part)
        labels.extend(basis)
    need(len(planes) <= 9 and len(labels) <= 18, "enumeration capacity")
    counts = [0, 0, 0]
    for a, frame in enumerate(frames):
        k = sum(memberships[j][a] for j in range(3))
        need(1 <= k <= 3, "unused block")
        counts[k - 1] += len(frame)
    return labels, planes, parts, counts


def tariffs(labels, planes, parts, family):
    answer = []
    for request in QUERY_GROUPS[family]:
        source = [
            labels[x]
            for p, part in zip(planes, parts, strict=True)
            if request >> part & 1
            for x in p
        ]
        projected = [
            tuple(sum(dot(v, labels[x]) << j for j, v in enumerate(source)) for x in p)
            for p in planes
        ]
        table = []
        for mask in range(1 << len(planes)):
            columns = [x for j, p in enumerate(projected) if mask >> j & 1 for x in p]
            table.append(rank(columns, len(source)))
        answer.append(table)
    return answer


def census(row, family):
    labels, planes, parts, counts = geometry(row)
    tables = tariffs(labels, planes, parts, family)
    stream, histogram = hashlib.sha256(), Counter()
    floor = (2 if family == "MMM" else 1) * counts[0] + 3 * sum(counts[1:])
    total = 0
    for choices in itertools.product(
        range(len(PATTERNS[family][0])), repeat=len(planes)
    ):
        masks = [0] * 4
        for j, (part, choice) in enumerate(zip(parts, choices, strict=True)):
            active = PATTERNS[family][part][choice]
            for term in range(4):
                if active >> term & 1:
                    masks[term] |= 1 << j
        charges = [tables[j][masks[j]] for j in range(4)]
        bill = sum(charges)
        need(bill >= floor, "atomic floor")
        stream.update(bytes(charges))
        histogram[bill] += 1
        total += 1
    if row["aligned_bases"]:
        need(min(histogram) == floor, "aligned sharpness")
    return {
        "name": row["name"],
        "family": family,
        "dimensions": counts,
        "original": sum((i + 1) * x for i, x in enumerate(counts)),
        "floor": floor,
        "minimum": min(histogram),
        "assignments": total,
        "histogram": {str(k): v for k, v in sorted(histogram.items())},
        "charge_sha256": stream.hexdigest(),
    }


def local_tables():
    answer = []
    for family in ("MMM", "VVV"):
        for membership in range(1, 8):
            parts = [j for j in range(3) if membership >> j & 1]
            histogram = Counter()
            for choices in itertools.product(
                range(len(PATTERNS[family][0])), repeat=len(parts)
            ):
                active = 0
                for part, choice in zip(parts, choices, strict=True):
                    active |= PATTERNS[family][part][choice]
                bill = sum(
                    bool(active >> j & 1 and request & membership)
                    for j, request in enumerate(QUERY_GROUPS[family])
                )
                histogram[bill] += 1
            floor = (2 if family == "MMM" else 1) if len(parts) == 1 else 3
            need(min(histogram) == floor, "local table")
            answer.append(
                {
                    "family": family,
                    "membership": membership,
                    "minimum": floor,
                    "histogram": {str(k): v for k, v in sorted(histogram.items())},
                }
            )
    return answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    authenticate()
    fixtures = load(HERE / "FIXTURES.json")
    need(1 <= len(fixtures) <= 8, "fixture inventory")
    result = {
        "schema_version": 1,
        "local_tables": local_tables(),
        "fixtures": [
            census(row, family) for row in fixtures for family in ("MMM", "VVV")
        ],
    }
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        need(result == load(HERE / "RESULT.json"), "result drift")
        print(
            "PASS_ORTHOGONAL_BLOCK_TRIPLE",
            len(result["fixtures"]),
            "censuses",
            sum(r["assignments"] for r in result["fixtures"]),
            "assignments",
        )


if __name__ == "__main__":
    main()
