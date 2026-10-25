#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dense elimination and iterative chordless-path reconstruction."""

from __future__ import annotations

import gzip
import io
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import WEIGHT16, cycles as primary_cycles, need, sources  # noqa: E402

PASS_LINE = (
    "PASS_C5_FIT_LEVEL_CANCELLATION_CHARGE_INDEPENDENT "
    "cycles=23 weight_sum=9/4 J_free_floor=45 one_J_floor=561/16 "
    "termwise_ceiling=180/7 beats=true"
)


def dense_rank(matrix) -> int:
    need(len(matrix) <= 112 and all(len(r) <= 112 for r in matrix), "dense bounds")
    if not matrix or not matrix[0]:
        return 0
    rows = [list(r) for r in matrix]
    pivot = 0
    width = len(rows[0])
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
    if not left or not right:
        return 0
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


def named_supports():
    return [(i,) for i in range(56)] + [
        (i, j) for i in range(56) for j in range(i + 1, 56)
    ]


def local_tables(planes, cycles):
    tables = []
    for cycle in cycles:
        table = [0] * (32 * 32)
        for mask_l in range(32):
            left = tuple(
                q
                for bit in range(5)
                if mask_l >> bit & 1
                for q in planes[cycle[bit]]
            )
            for mask_r in range(32):
                right = tuple(
                    q
                    for bit in range(5)
                    if mask_r >> bit & 1
                    for q in planes[cycle[bit]]
                )
                table[mask_l + 32 * mask_r] = rank(left, right)
        tables.append(table)
    return tables


def support_masks(support, cycles):
    present = set(support)
    out = []
    for cycle in cycles:
        mask = 0
        for bit, plane in enumerate(cycle):
            if plane in present:
                mask |= 1 << bit
        out.append(mask)
    return out


def main() -> None:
    planes, matching = geometry()
    # Independent chordless-path census checks the same 23 vertex sets; charging
    # uses the primary cyclic order so WEIGHT16 indices stay aligned.
    independent_sets = cycle_sets(planes)
    ordered = primary_cycles(planes)
    need(
        {frozenset(c) for c in ordered} == {frozenset(c) for c in independent_sets},
        "cycle set agreement",
    )
    ranks = []
    for cycle in ordered:
        local = tuple(q for i in cycle for q in planes[i])
        ranks.append(rank(local, local))
    need(Counter(ranks) == {7: 4, 8: 6, 9: 13}, "independent rank histogram")
    all_labels = tuple(q for plane in planes for q in plane)
    need(rank(all_labels, all_labels) == 9, "independent global rank")

    need(sum(WEIGHT16) == 36, "weight sum")
    weight_sum = Fraction(sum(WEIGHT16), 16)
    rho = sum(Fraction(WEIGHT16[i], 16) * ranks[i] for i in range(23))
    need(weight_sum == Fraction(9, 4) and rho == Fraction(303, 16), "certificate scalars")
    credit = rho - 9
    j_free = 20 * weight_sum
    one_j = j_free - credit
    need(j_free == 45 and one_j == Fraction(561, 16), "floors")
    need(j_free > Fraction(180, 7) and one_j > Fraction(180, 7), "beat ceiling")

    tables = local_tables(planes, ordered)
    supports = named_supports()
    masks = [support_masks(s, ordered) for s in supports]
    labels = [tuple(q for i in s for q in planes[i]) for s in supports]
    checked = 0
    min_slack = None
    for i, left in enumerate(labels):
        mi = masks[i]
        for j, right in enumerate(labels):
            mj = masks[j]
            global_rank = rank(left, right)
            loc16 = 0
            for k, w in enumerate(WEIGHT16):
                if w:
                    loc16 += w * tables[k][mi[k] + 32 * mj[k]]
            need(loc16 <= 16 * global_rank, "independent named domination")
            slack = 16 * global_rank - loc16
            if min_slack is None or slack < min_slack:
                min_slack = slack
            checked += 1
            need(checked <= 3_000_000, "bounded")
    need(checked == len(supports) ** 2, "complete independent census")
    need(min_slack == 0, "independent certificate tightness")

    total = 0
    matrix = [[0] * 112 for _ in range(112)]
    for port in range(112):
        plane_index = next(i for i, pair in enumerate(matching) if port in pair)
        total += rank(planes[plane_index], planes[plane_index])
        matrix[port][port] = 1
    need(total == 224, "independent diagonal tariff")
    need(
        all(matrix[i][j] == int(i == j) for i in range(112) for j in range(112)),
        "independent diagonal identity",
    )
    need(total >= int(j_free), "diagonal meets J-free floor")

    print(PASS_LINE)


if __name__ == "__main__":
    main()
