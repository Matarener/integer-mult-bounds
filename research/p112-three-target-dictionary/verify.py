"""Exact three-target dictionary tariff. Nick Petalas. Apache-2.0."""

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
DIRECTIONS = tuple(tuple((s >> j) & 1 for j in range(3)) for s in range(1, 8))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read(path, limit=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "file capacity")
    return raw


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique)


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256")
    header = b"blob " + str(len(raw)).encode() + b"\0"
    need(
        sha1(header + raw, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "source blob",
    )


def load():
    meta = parse(read(HERE / "SOURCES.json", 32768))
    pins = [r for r in meta["files"] if r["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == INPUT, "input inventory")
    raw = read(ROOT / INPUT)
    authenticate(raw, pins[0])
    rows = parse(raw)["recipes"]
    need(type(rows) is list and len(rows) == 112, "112 recipes")
    need(all(type(r["port"]) is int for r in rows), "integer port")
    need(sorted(r["port"] for r in rows) == list(range(112)), "port IDs")
    labels = [r["q"] for r in sorted(rows, key=lambda r: r["port"])]
    need(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    need(len(set(labels)) == 112, "distinct labels")
    raw = read(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    groups = parse(raw)["orthonormal_groups"]
    validate_geometry(labels, groups)
    return labels, groups


def dot(a, b):
    return (a & b).bit_count() % 2


def validate_geometry(labels, groups):
    need(type(groups) is list and len(groups) == 16, "sixteen groups")
    need(all(type(g) is list and len(g) in (4, 6, 8) for g in groups), "sizes")
    need(all(type(p) is int for g in groups for p in g), "integer group port")
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for group in groups:
        need(
            all(dot(labels[p], labels[q]) == int(p == q) for p in group for q in group),
            "orthonormal group",
        )


def rank(rows, width):
    need(0 <= width <= 24 and len(rows) <= 24, "rank capacity")
    pivots = [0] * width
    for value in rows:
        need(type(value) is int and 0 <= value < 1 << width, "binary row")
        for bit in range(width - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(p) for p in pivots)


def cost(labels, source, reader):
    rows = [
        sum(dot(labels[p], labels[q]) << j for j, q in enumerate(reader))
        for p in source
    ]
    return rank(rows, len(reader))


def solve(ids, target):
    need(1 <= len(ids) <= 3 and len(set(ids)) == len(ids), "basis size")
    need(all(type(i) is int and 0 <= i < 7 for i in ids), "direction ID")
    need(type(target) is int and 0 <= target < 3, "target axis")
    matrix = [
        [Fraction(DIRECTIONS[i][j]) for i in ids] + [Fraction(j == target)]
        for j in range(3)
    ]
    for column in range(len(ids)):
        pivot = next((r for r in range(column, 3) if matrix[r][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        value = matrix[column][column]
        matrix[column] = [x / value for x in matrix[column]]
        for row in range(3):
            if row != column:
                value = matrix[row][column]
                matrix[row] = [
                    x - value * y
                    for x, y in zip(matrix[row], matrix[column], strict=True)
                ]
    if any(all(x == 0 for x in row[:-1]) and row[-1] != 0 for row in matrix):
        return None
    return tuple(matrix[i][-1] for i in range(len(ids)))


def bases():
    result = []
    for target in range(3):
        candidates = []
        for size in range(1, 4):
            for ids in itertools.combinations(range(7), size):
                coefficients = solve(ids, target)
                if coefficients is not None and all(coefficients):
                    candidates.append((ids, coefficients))
        need(len(candidates) == 9, "nine minimal representations per axis")
        result.append(candidates)
    return result


def patterns(axis_bases):
    result = []
    for choice in itertools.product(*axis_bases):
        readers = [0] * 7
        operator = [[Fraction(0) for _ in range(3)] for _ in range(3)]
        for target, (ids, coefficients) in enumerate(choice):
            for index, coefficient in zip(ids, coefficients, strict=True):
                readers[index] |= 1 << target
                for coordinate in range(3):
                    operator[target][coordinate] += (
                        coefficient * DIRECTIONS[index][coordinate]
                    )
        need(
            operator == [[int(i == j) for j in range(3)] for i in range(3)],
            "literal three-target operator",
        )
        result.append(tuple(readers))
    need(len(result) == 729 and len(set(result)) == 729, "729 support patterns")
    return sorted(result)


def table(labels, groups, group_ids):
    supports = [[]] + [
        sorted({p for j, g in enumerate(group_ids) if s >> j & 1 for p in groups[g]})
        for s in range(1, 8)
    ]
    return [
        [cost(labels, supports[s], supports[t]) for t in range(8)] for s in range(1, 8)
    ]


def literal_identity(labels, groups):
    owners, planes = {}, {}
    for group in groups:
        for offset in range(0, len(group), 2):
            for port in group[offset : offset + 2]:
                planes[port] = group[offset : offset + 2]
        for half in range(2):
            for port in group[half::2]:
                owners[port] = (tuple(group), half)
    for p, q in itertools.product(range(112), repeat=2):
        for a, b in itertools.product(range(2), repeat=2):
            value = int(owners[p] == owners[q]) * dot(
                labels[planes[p][a]], labels[planes[q][b]]
            )
            need(value == int(p == q and a == b), "expanded I224")
    return 50176


def compute(labels, groups):
    identity_entries = literal_identity(labels, groups)
    candidates = patterns(bases())
    types = Counter(
        tuple(i // 2 for i in ids) for ids in itertools.combinations(range(32), 3)
    )
    need(len(types) == 800 and sum(types.values()) == 4960, "triple coverage")
    records, all_bills = [], sha256()
    for group_ids, multiplicity in sorted(types.items()):
        costs = table(labels, groups, group_ids)
        bills = [sum(costs[i][r] for i, r in enumerate(rs)) for rs in candidates]
        baseline = sum(len(groups[g]) for g in group_ids)
        need(min(bills) == baseline, "three-target minimum")
        digest = sha256(bytes(bills)).hexdigest()
        all_bills.update(bytes(bills))
        records.append(
            [*group_ids, multiplicity, baseline, bills.count(baseline), digest]
        )
    return {
        "status": "PASS_THREE_TARGET_DICTIONARY",
        "indicator_triples": 4960,
        "group_types": 800,
        "axis_representations": [9, 9, 9],
        "patterns_per_type": 729,
        "exact_bills": len(records) * len(candidates),
        "all_bills_sha256": all_bills.hexdigest(),
        "expanded_identity_entries": identity_entries,
        "whole_K_tariff": 224,
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    labels, groups = load()
    result = compute(labels, groups)
    text = json.dumps(result, sort_keys=True, separators=(",", ":"))
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        expected = parse(read(HERE / "RESULT.json"))
        need(
            text == json.dumps(expected, sort_keys=True, separators=(",", ":")),
            "result receipt",
        )
        print(result["status"], result["exact_bills"], result["all_bills_sha256"])


if __name__ == "__main__":
    main()
