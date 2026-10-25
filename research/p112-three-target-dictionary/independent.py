"""Minor and coordinate-matrix replay. Nick Petalas. Apache-2.0."""

import itertools
import json
from collections import Counter
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bounded_json(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "JSON size")
    return json.loads(raw)


def source(path, pin, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "source size")
    require(sha256(raw).hexdigest() == pin["sha256"], "independent source hash")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    require(
        sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "independent source blob",
    )
    return json.loads(raw)


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dimension(vectors):
    require(len(vectors) <= 8 and all(len(v) == 3 for v in vectors), "minor capacity")
    for a, b, c in itertools.combinations(vectors, 3):
        if sum(x * y for x, y in zip(cross(a, b), c, strict=True)):
            return 3
    if any(any(cross(a, b)) for a, b in itertools.combinations(vectors, 2)):
        return 2
    return int(any(any(v) for v in vectors))


def minimal_supports():
    dictionary = [tuple(int(x) for x in f"{s:03b}"[::-1]) for s in range(1, 8)]
    determinants = [
        abs(sum(x * y for x, y in zip(cross(a, b), c, strict=True)))
        for a, b, c in itertools.combinations(dictionary, 3)
    ]
    require(Counter(determinants) == {0: 6, 1: 28, 2: 1}, "all 35 minors")
    supports = []
    for target in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        admitted = []
        for mask in range(1, 128):
            vectors = [d for i, d in enumerate(dictionary) if mask & (1 << i)]
            if dimension(vectors) == dimension([*vectors, target]):
                admitted.append(mask)
        minimal = [
            s for s in admitted if not any(t != s and t & s == t for t in admitted)
        ]
        require(len(minimal) == 9, "independent nine minimal supports")
        require(all(s.bit_count() <= 3 for s in minimal), "three-vector basis")
        supports.append(minimal)
    patterns = [
        tuple(
            sum(1 << t for t, s in enumerate(triple) if s & (1 << i)) for i in range(7)
        )
        for triple in itertools.product(*supports)
    ]
    require(len(set(patterns)) == 729, "independent pattern coverage")
    return sorted(patterns)


def binary_rank(matrix):
    require(len(matrix) <= 24, "matrix row capacity")
    width = len(matrix[0]) if matrix else 0
    require(width <= 24 and all(len(r) == width for r in matrix), "column capacity")
    rows = [r[:] for r in matrix]
    used = 0
    for column in range(width):
        hit = next((i for i in range(used, len(rows)) if rows[i][column]), None)
        if hit is not None:
            rows[used], rows[hit] = rows[hit], rows[used]
            for row in range(used + 1, len(rows)):
                if rows[row][column]:
                    rows[row] = [
                        a ^ b for a, b in zip(rows[row], rows[used], strict=True)
                    ]
            used += 1
    return used


def costs(labels, groups, ids):
    sets = [
        sorted({p for t in range(3) if s & (1 << t) for p in groups[ids[t]]})
        for s in range(8)
    ]
    bits = [tuple(int(x) for x in f"{q:09b}") for q in labels]
    result = []
    for left in sets[1:]:
        row = []
        for right in sets:
            gram = [
                [
                    sum(a * b for a, b in zip(bits[p], bits[q], strict=True)) % 2
                    for q in right
                ]
                for p in left
            ]
            row.append(binary_rank(gram))
        result.append(row)
    return result


def geometry():
    meta = bounded_json(HERE / "SOURCES.json", 32768)
    pins = [r for r in meta["files"] if r["usage"] == "input"]
    require(len(pins) == 1 and pins[0]["path"] == INPUT, "independent input inventory")
    data = source(HERE.parents[1] / INPUT, pins[0], 1_048_576)
    labels = [r["q"] for r in sorted(data["recipes"], key=lambda r: r["port"])]
    retained = source(HERE / "RETAINED-RANK32.json", meta["retained_rank32"], 32768)
    groups = retained["orthonormal_groups"]
    require(len(labels) == 112 and len(groups) == 16, "independent geometry size")
    require(
        sorted(p for g in groups for p in g) == list(range(112)),
        "independent partition",
    )
    for group in groups:
        require(
            binary_rank(
                [
                    [(labels[a] & labels[b]).bit_count() % 2 for b in group]
                    for a in group
                ]
            )
            == len(group),
            "independent group rank",
        )
        require(
            all(
                (labels[a] & labels[b]).bit_count() % 2 == int(a == b)
                for a in group
                for b in group
            ),
            "independent Gram identity",
        )
    return labels, groups


def replay():
    labels, groups = geometry()
    patterns = minimal_supports()
    # Enumerate the original indicators, rather than deriving a type count formula.
    names = [(g, h) for g in range(16) for h in range(2)]
    occurrences = Counter(
        tuple(g for g, _ in triple) for triple in itertools.combinations(names, 3)
    )
    require(
        len(occurrences) == 800 and sum(occurrences.values()) == 4960,
        "independent original triple count",
    )
    records, digest = [], sha256()
    for ids, count in sorted(occurrences.items()):
        matrix = costs(labels, groups, ids)
        bills = [
            sum(matrix[i][support] for i, support in enumerate(pattern))
            for pattern in patterns
        ]
        bound = sum(map(len, (groups[g] for g in ids)))
        require(min(bills) == bound, "independent exact minimum")
        digest.update(bytes(bills))
        records.append(
            [*ids, count, bound, bills.count(bound), sha256(bytes(bills)).hexdigest()]
        )
    expected = bounded_json(HERE / "RESULT.json", 1_048_576)
    require(records == expected["records"], "independent records")
    require(digest.hexdigest() == expected["all_bills_sha256"], "independent digest")
    require(
        dimension([(1, 1, 0), (1, 0, 1), (0, 1, 1)]) == 3,
        "characteristic-zero determinant-two branch",
    )
    print(
        "PASS_INDEPENDENT_THREE_TARGET",
        len(records) * len(patterns),
        digest.hexdigest(),
    )


if __name__ == "__main__":
    replay()
