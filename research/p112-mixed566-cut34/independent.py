"""Separate root inventory and occupancy checks, without predecessor imports."""

import hashlib
import json
from itertools import combinations, product
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


def reconstruct():
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for tail in product((-1, 1), repeat=7):
        row = (1,) + tail
        if sum(x < 0 for x in row) % 2 == 0:
            roots.add(row)
    frame = set()
    for i in (0, 2, 4, 6):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            frame.add(tuple(row))
    check(len(roots) == 120 and len(frame) == 8 and frame <= roots, "root/frame model")
    return tuple(sorted(roots)), frame


def geometry_check(expected):
    roots, frame = reconstruct()
    check(hashlib.sha256(json.dumps(roots).encode()).hexdigest()
          == expected["full_roots_sha256"], "independent full root order")
    # Bitmasks encode nonzero real pairings, not the F2 label pairing.
    masks = []
    for a in roots:
        mask = 0
        for j, b in enumerate(roots):
            if sum(a[k] * b[k] for k in range(8)):
                mask |= 1 << j
        masks.append(mask)
    live = sum(1 << j for j, r in enumerate(roots) if r not in frame)
    removed = ((1 << 120) - 1) ^ live
    histogram, axes = {}, 0
    for i, j in combinations(range(120), 2):
        if masks[i] >> j & 1:
            continue
        size = ((masks[i] | masks[j]) & live).bit_count()
        histogram[str(size)] = histogram.get(str(size), 0) + 1
        if size == 82:
            for a, b in ((i, j), (j, i)):
                axis = masks[a] & ~masks[b]
                punctures = axis & removed
                check(axis.bit_count() == 33 and punctures.bit_count() == 4,
                      "union82 full/punctured axis sizes")
                ids = tuple(k for k in range(120) if punctures >> k & 1)
                check(all(not (masks[x] >> y & 1) for x, y in combinations(ids, 2)),
                      "orthogonal four-puncture geometry")
                axes += 1
    check(histogram == expected["plane_union_counts"] and axes == 896, "entire plane inventory")
    return histogram


def occupancy_check(expected):
    # An arbitrary retained union needs at least N total piece incidences.
    # Exhaust every feasible support-size triple after the rank6 refinement.
    triples = tuple(m for m in product(range(13), range(19), range(19)) if sum(m) >= 48)
    check(triples == ((12, 18, 18),), "only capacity-equality triple survives")
    # At equality, any repeated incidence or any support outside R loses coverage.
    for size in (2, 3):
        check(48 - (size - 1) < 48, "overlap must lose coverage")
    bounds = []
    for small_axis, first_axis, second_axis in product((0, 1), repeat=3):
        if first_axis == second_axis == small_axis:
            upper = 29
        elif first_axis == second_axis:
            upper = 12 + 29
        else:
            upper = 18 + 28
        bounds.append(upper)
    row = expected["D6"]["82"]
    check(bounds == row["eight_axis_assignment_bounds"] and max(bounds) == 46,
          "independent equality-case axis split")
    check(expected["E6"] == {"incidence_upper": 86, "required_twice": 88}, "strict E6 gap")
    for union, minimum in ((84, 50), (85, 51), (86, 52)):
        row = expected["D6"][str(union)]
        check(row["required"] == minimum and row["coverage_upper"] == 48 < minimum,
              "other strict D6 gaps")
    return {"support_size_triples": 13 * 19 * 19, "surviving_triples": [list(m) for m in triples],
            "equality_axis_bounds": bounds}


def main():
    path = Path(__file__).with_name("RESULT.json")
    check(path.stat().st_size <= 200_000, "receipt capacity")
    result = json.loads(path.read_text(encoding="utf-8"))
    histogram = geometry_check(result["geometry"])
    occupancy = occupancy_check(result["arithmetic"])
    print(json.dumps({"status": "PASS_SEPARATE_CUT34_RECONSTRUCTION",
                      "plane_union_counts": histogram, "occupancy": occupancy}, sort_keys=True))


if __name__ == "__main__":
    main()
