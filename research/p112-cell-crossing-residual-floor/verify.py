"""Exact residual tariffs for closure cells crossing orthogonal blocks.

Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VVV_Q = ((1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
MMM_Q = ((1, 1, -1), (1, -1, 1), (-1, 1, 1), (1, 1, 1))
VVV_U = ((1, 1, -1, -1), (1, -1, 1, -1), (-1, 1, 1, -1), (0, 0, 0, 2))
MMM_U = ((1, 1, 0, -1), (1, 0, 1, -1), (0, 1, 1, -1), (0, 0, 0, 1))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name):
    path = HERE / name
    need(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 262144,
        "regular package input",
    )
    return json.loads(path.read_bytes())


def rank(columns):
    pivots = {}
    for original_column in columns:
        column = original_column
        for bit in range(column.bit_length() - 1, -1, -1):
            if not (column >> bit) & 1:
                continue
            if bit in pivots:
                column ^= pivots[bit]
            else:
                pivots[bit] = column
                break
    return len(pivots)


def dot(a, b):
    return (a & b).bit_count() % 2


def gram_i(basis):
    return all(
        dot(x, y) == int(i == j)
        for i, x in enumerate(basis)
        for j, y in enumerate(basis)
    )


def geometry(row):
    width = row["ambient_dimension"]
    need(type(width) is int and 1 <= width <= 16, "ambient dimension capacity")
    blocks = row["blocks"]
    need(1 <= len(blocks) <= 8, "block capacity")
    flat = [x for block in blocks for x in block]
    need(
        len(flat) <= width and all(1 <= len(b) <= 8 for b in blocks), "block dimensions"
    )
    need(all(type(x) is int and 0 < x < 1 << width for x in flat), "binary labels")
    need(gram_i(flat), "orthogonal Gram-I block decomposition")
    need(len(row["groups"]) == 3, "three target groups")
    labels, cells, memberships = [], [], [0] * len(blocks)
    for g, group in enumerate(row["groups"]):
        group_labels, seen = [], set()
        for part in group["parts"]:
            k, basis = part["block"], part["basis"]
            need(
                type(k) is int and 0 <= k < len(blocks) and k not in seen,
                "distinct group blocks",
            )
            need(
                len(basis) == len(blocks[k]) and gram_i(basis),
                "complete group block basis",
            )
            need(
                all(type(x) is int and 0 < x < 1 << width for x in basis),
                "group labels",
            )
            need(rank(blocks[k] + basis) == len(blocks[k]), "group block span")
            memberships[k] |= 1 << g
            seen.add(k)
            group_labels.extend(basis)
        need(group_labels and len(group_labels) <= 16, "positive bounded target group")
        parts = group["cells"]
        need(
            1 <= len(parts) <= 8 and all(part for part in parts),
            "nonempty closure cells",
        )
        indices = [x for part in parts for x in part]
        need(all(type(x) is int for x in indices), "integer cell indices")
        need(
            sorted(indices) == list(range(len(group_labels))),
            "cells partition target group",
        )
        offset = len(labels)
        labels.extend(group_labels)
        cells.extend((g, tuple(offset + x for x in part)) for part in parts)
    need(len(cells) <= 9 and all(memberships), "cell capacity and block coverage")
    n = [
        sum(
            len(b)
            for b, m in zip(blocks, memberships, strict=True)
            if m.bit_count() == k
        )
        for k in (1, 2, 3)
    ]
    return labels, cells, n


def symbolic_identity(queries, readers):
    for i in range(4):
        for j in range(3):
            value = sum(readers[t][i] * queries[t][j] for t in range(4))
            need(value == 2 * int(i == j), "exact integer residual operator")


def table(labels, cells, family):
    queries, readers = (VVV_Q, VVV_U) if family == "VVV" else (MMM_Q, MMM_U)
    symbolic_identity(queries, readers)
    cached = []
    for term in range(4):
        source = [labels[x] for g, c in cells if queries[term][g] for x in c]
        values = []
        for mask in range(1 << len(cells)):
            columns = [
                sum(dot(q, labels[x]) << j for j, q in enumerate(source))
                for c, (_, indices) in enumerate(cells)
                if mask >> c & 1
                for x in indices
            ]
            values.append(rank(columns))
        cached.append(values)
    patterns = []
    for g, _ in cells:
        patterns.append(
            [
                tuple(int(readers[t][g] + readers[t][3] * v != 0) for t in range(4))
                for v in ((0, 1, -1) if family == "VVV" else (0, 1))
            ]
        )
    return cached, patterns


def census(row, family):
    labels, cells, n = geometry(row)
    costs, patterns = table(labels, cells, family)
    choices = 3 if family == "VVV" else 2
    bound = (
        n[0] + 3 * n[1] + 3 * n[2]
        if family == "VVV"
        else 2 * n[0] + 3 * n[1] + 3 * n[2]
    )
    stream, histogram, minimum = hashlib.sha256(), {}, None
    minimizing = None
    for assignment in itertools.product(range(choices), repeat=len(cells)):
        charge = []
        for t in range(4):
            mask = sum(patterns[j][v][t] << j for j, v in enumerate(assignment))
            charge.append(costs[t][mask])
        total = sum(charge)
        need(total >= bound, "residual tariff below theorem")
        histogram[str(total)] = histogram.get(str(total), 0) + 1
        stream.update((",".join(map(str, charge)) + "\n").encode())
        if minimum is None or total < minimum:
            minimum, minimizing = total, list(assignment)
    return {
        "assignments": choices ** len(cells),
        "n": n,
        "original": n[0] + 2 * n[1] + 3 * n[2],
        "bound": bound,
        "minimum": minimum,
        "minimizer": minimizing,
        "histogram": histogram,
        "charge_stream_sha256": stream.hexdigest(),
    }


def result():
    fixtures = load("FIXTURES.json")["fixtures"]
    need(1 <= len(fixtures) <= 12, "fixture capacity")
    need(len({r["name"] for r in fixtures}) == len(fixtures), "distinct fixture names")
    return {
        "schema": 1,
        "fixtures_sha256": hashlib.sha256(
            (HERE / "FIXTURES.json").read_bytes()
        ).hexdigest(),
        "results": {
            r["name"]: {f: census(r, f) for f in ("VVV", "MMM")} for r in fixtures
        },
    }


def main():
    need(sys.argv[1:] in ([], ["--write"]), "usage: verify.py [--write]")
    actual = result()
    if sys.argv[1:]:
        (HERE / "RESULT.json").write_text(
            json.dumps(actual, indent=2, sort_keys=True) + "\n"
        )
    else:
        need(actual == load("RESULT.json"), "recorded exact result mismatch")
    total = sum(
        f["assignments"] for r in actual["results"].values() for f in r.values()
    )
    print(
        f"PASS_CELL_CROSSING_RESIDUAL fixtures={len(actual['results'])} "
        f"assignments={total}"
    )


if __name__ == "__main__":
    main()
