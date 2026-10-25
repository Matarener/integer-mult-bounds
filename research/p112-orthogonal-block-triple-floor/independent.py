"""Separate raw-Gram and integer coefficient replay. Apache-2.0."""

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).absolute().parent
QUERIES = {
    "MMM": ((1, 1, -1), (1, -1, 1), (-1, 1, 1), (1, 1, 1)),
    "VVV": ((1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(name):
    path = HERE / name
    require(
        path.is_file() and path.absolute() == path.resolve(), "independent regular path"
    )
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    require(len(raw) <= 1048576, "independent file capacity")
    return json.loads(raw)


def gram_rank(rows, cols):
    require(len(rows) <= 24 and len(cols) <= 24, "raw matrix capacity")
    matrix = [[(r & c).bit_count() % 2 for c in cols] for r in rows]
    pivot = 0
    for col in range(len(cols)):
        found = next((r for r in range(pivot, len(rows)) if matrix[r][col]), None)
        if found is None:
            continue
        matrix[pivot], matrix[found] = matrix[found], matrix[pivot]
        for r in range(pivot + 1, len(rows)):
            if matrix[r][col]:
                matrix[r] = [
                    x ^ y for x, y in zip(matrix[r], matrix[pivot], strict=True)
                ]
        pivot += 1
    return pivot


def coefficients(family, part, choice):
    a, b, c = [int(j == part) for j in range(3)]
    if family == "MMM":
        v = choice
        return (a + b - v, a + c - v, b + c - v, v)
    w = (0, 1, -1)[choice]
    return (a + b - c - w, a - b + c - w, -a + b + c - w, 2 * w)


def local_checks():
    tables, entries = [], 0
    for family, queries in QUERIES.items():
        alphabet = range(2 if family == "MMM" else 3)
        for part in range(3):
            for choice in alphabet:
                readers = coefficients(family, part, choice)
                for source in range(3):
                    value = sum(
                        u * q[source] for u, q in zip(readers, queries, strict=True)
                    )
                    require(value == 2 * (source == part), "integer target identity")
                    for prime in (3, 5, 7):
                        scales = (1, 2, 4)
                        scaled = value * scales[source] * pow(scales[part], -1, prime)
                        require(
                            scaled % prime == (2 * (source == part)) % prime,
                            "gauged field identity",
                        )
                        entries += 1
        for membership in range(1, 8):
            parts = [j for j in range(3) if membership & (1 << j)]
            hist = Counter()
            for choices in itertools.product(alphabet, repeat=len(parts)):
                vectors = [
                    coefficients(family, p, c)
                    for p, c in zip(parts, choices, strict=True)
                ]
                bill = sum(
                    any(q[p] for p in parts) and any(u[i] for u in vectors)
                    for i, q in enumerate(queries)
                )
                hist[bill] += 1
            tables.append(
                {
                    "family": family,
                    "membership": membership,
                    "minimum": min(hist),
                    "histogram": {str(k): v for k, v in sorted(hist.items())},
                }
            )
    return tables, entries


def check_block(frame, group, atom):
    block = [
        x
        for x, tag in zip(group["basis"], group["atom_ids"], strict=True)
        if tag == atom
    ]
    if not block:
        return False
    require(
        len(block) == len(frame) == gram_rank(frame, block), "independent full block"
    )
    for x in block:
        projected = 0
        for v in frame:
            if (x & v).bit_count() % 2:
                projected ^= v
        require(projected == x, "independent block containment")
    require(
        all(
            (x & y).bit_count() % 2 == (i == j)
            for i, x in enumerate(block)
            for j, y in enumerate(block)
        ),
        "independent block basis",
    )
    return True


def fixture_data(row):
    labels, planes, parts = [], [], []
    require(
        1 <= len(row["atoms"]) <= 4 and len(row["groups"]) == 3,
        "independent geometry capacity",
    )
    frames = [a["frame"] for a in row["atoms"]]
    all_frame = [x for f in frames for x in f]
    require(
        len(all_frame) <= 12 and gram_rank(all_frame, all_frame) == len(all_frame),
        "independent frame rank",
    )
    require(
        all(
            (a & b).bit_count() % 2 == (i == j)
            for i, a in enumerate(all_frame)
            for j, b in enumerate(all_frame)
        ),
        "independent orthogonal blocks",
    )
    counts = [0, 0, 0]
    for a, frame in enumerate(frames):
        members = 0
        for group in row["groups"]:
            members += check_block(frame, group, a)
        require(1 <= members <= 3, "independent membership")
        counts[members - 1] += len(frame)
    for part, group in enumerate(row["groups"]):
        offset = len(labels)
        labels.extend(group["basis"])
        for pair in group["planes"]:
            require(
                group["atom_ids"][pair[0]] == group["atom_ids"][pair[1]],
                "independent complete-plane compatibility",
            )
            planes.append(tuple(offset + i for i in pair))
            parts.append(part)
    require(
        1 <= len(planes) <= 9 and len(labels) <= 18, "independent enumeration capacity"
    )
    return labels, planes, parts, counts


def replay(row, family):
    labels, planes, parts, counts = fixture_data(row)
    queries = QUERIES[family]
    tables = []
    for q in queries:
        source = [
            labels[i]
            for pair, part in zip(planes, parts, strict=True)
            if q[part]
            for i in pair
        ]
        table = []
        for mask in range(1 << len(planes)):
            reader = [
                labels[i]
                for j, pair in enumerate(planes)
                if mask & (1 << j)
                for i in pair
            ]
            table.append(gram_rank(reader, source))
        tables.append(table)
    histogram, digest, total = Counter(), hashlib.sha256(), 0
    for choices in itertools.product(
        range(2 if family == "MMM" else 3), repeat=len(planes)
    ):
        masks = [0] * 4
        for j, (part, choice) in enumerate(zip(parts, choices, strict=True)):
            for i, coefficient in enumerate(coefficients(family, part, choice)):
                if coefficient:
                    masks[i] += 1 << j
        charges = [tables[i][mask] for i, mask in enumerate(masks)]
        histogram[sum(charges)] += 1
        digest.update(bytes(charges))
        total += 1
    return {
        "name": row["name"],
        "family": family,
        "dimensions": counts,
        "original": sum((i + 1) * n for i, n in enumerate(counts)),
        "floor": (2 if family == "MMM" else 1) * counts[0] + 3 * sum(counts[1:]),
        "minimum": min(histogram),
        "assignments": total,
        "histogram": {str(k): v for k, v in sorted(histogram.items())},
        "charge_sha256": digest.hexdigest(),
    }


def main():
    fixtures = load("FIXTURES.json")
    require(1 <= len(fixtures) <= 8, "independent fixture count")
    tables, entries = local_checks()
    result = {
        "schema_version": 1,
        "local_tables": tables,
        "fixtures": [
            replay(row, family) for row in fixtures for family in ("MMM", "VVV")
        ],
    }
    require(result == load("RESULT.json"), "independent complete result drift")
    print(
        "PASS_INDEPENDENT_ORTHOGONAL_BLOCK",
        sum(x["assignments"] for x in result["fixtures"]),
        "assignments",
        entries,
        "gauged field entries",
    )


if __name__ == "__main__":
    main()
