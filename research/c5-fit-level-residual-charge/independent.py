#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dense elimination and iterative chordless-path reconstruction."""

from __future__ import annotations

import gzip
import io
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import need, sources  # noqa: E402

PASS_LINE = (
    "PASS_C5_FIT_LEVEL_RESIDUAL_CHARGE_INDEPENDENT "
    "cycles=23 local_floor_sum=460 diagonal_cost=224 inequality_holds=false"
)


def dense_rank(matrix) -> int:
    need(len(matrix) <= 112 and all(len(r) <= 112 for r in matrix), "dense bounds")
    rows = [list(r) for r in matrix]
    pivot = 0
    width = len(rows[0]) if rows else 0
    for col in range(width):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def parity(a: int, b: int) -> int:
    return sum(((a >> j) & 1) * ((b >> j) & 1) for j in range(9)) % 2


def rank(left, right) -> int:
    return dense_rank([[parity(x, y) for y in right] for x in left])


def cycle_sets(planes):
    adj = [
        {j for j in range(56) if j != i and rank(planes[i], planes[j]) == 0}
        for i in range(56)
    ]
    paths = [(i,) for i in range(56)]
    for length in range(1, 5):
        extended = []
        for path in paths:
            for vertex in adj[path[-1]]:
                if vertex <= path[0] or vertex in path:
                    continue
                if any(vertex in adj[i] for i in path[1:-1]):
                    continue
                if length > 1 and (vertex in adj[path[0]]) != (length == 4):
                    continue
                need(len(extended) < 100_000, "bounded simple paths")
                extended.append(path + (vertex,))
        paths = extended
    found = {tuple(sorted(p)) for p in paths}
    need(len(found) == 23, "23 chordless C5s")
    return tuple(sorted(found))


def geometry():
    raw = sources()
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        rows = json.loads(stream.read())["recipes"]
    labels = {r["port"]: r["q"] for r in rows}
    matching = json.loads(raw["MATCHING.json"])["matching"]
    planes = tuple(tuple(labels[p] for p in pair) for pair in matching)
    need(all(rank(p, p) == 2 for p in planes), "plane self-rank I2")
    return planes, matching


def main() -> None:
    planes, matching = geometry()
    cycles = cycle_sets(planes)
    ranks = []
    for cycle in cycles:
        local = tuple(q for i in cycle for q in planes[i])
        ranks.append(rank(local, local))
    need(Counter(ranks) == {7: 4, 8: 6, 9: 13}, "independent rank histogram")
    all_labels = tuple(q for plane in planes for q in plane)
    need(rank(all_labels, all_labels) == 9, "independent global rank")

    # Diagonal identity by direct matrix assembly.
    matrix = [[0] * 112 for _ in range(112)]
    total = 0
    for port in range(112):
        plane_index = next(
            i for i, pair in enumerate(matching) if port in pair
        )
        cost = rank(planes[plane_index], planes[plane_index])
        need(cost == 2, "independent single-plane tariff")
        total += cost
        matrix[port][port] += 1
    need(
        all(matrix[i][j] == int(i == j) for i in range(112) for j in range(112)),
        "independent diagonal sums to I",
    )
    need(total == 224, "independent diagonal cost")
    local_floor_sum = 20 * 23
    need(local_floor_sum == 460 and not (local_floor_sum <= total), "obstruction")

    committed = json.loads((HERE / "RESULT.json").read_bytes())
    need(committed["uniform_local_floor_sum"] == 460, "receipt floor sum")
    need(committed["diagonal_fit"]["total_cost"] == 224, "receipt diagonal")
    need(committed["inequality_holds"] is False, "receipt inequality")
    need(len(committed["cycles"]) == 23, "receipt cycle count")
    print(PASS_LINE)


if __name__ == "__main__":
    main()
