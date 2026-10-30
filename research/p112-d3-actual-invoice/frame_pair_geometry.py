"""Independent, bounded frame-pair checks for the actual 8771 proof.

Research by conorholds with OpenAI Codex assistance. Apache-2.0.
Retains the E8/P112 geometry lineage credited by PR3689's SOURCES.json.
Written proof and exact computational coverage are distinguished in VERIFY.md.

No source module is imported or executed. Roots are reconstructed directly;
labels use a new polar basis, bound by an invertible leading-coordinate-
preserving transfer to the source's literal SIMPLE declaration.
"""

from __future__ import annotations

import argparse
import ast
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    require(len(left) == len(right), "dot dimensions")
    return sum(a * b for a, b in zip(left, right))


def binary_rank(values):
    pivots = {}
    for original in values:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def binary_span(values):
    result = {0}
    for value in values:
        if value not in result:
            result |= {old ^ value for old in tuple(result)}
    return result


def inverse(matrix):
    size = len(matrix)
    require(size and all(len(row) == size for row in matrix), "inverse shape")
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        require(pivot is not None, "singular simple system")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for i in range(size):
            if i != column and rows[i][column]:
                factor = rows[i][column]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[column])]
    return [row[size:] for row in rows]


def roots_and_frame():
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.append(tuple(root))
    for signs in range(128):
        if signs.bit_count() % 2 == 0:
            roots.append((1,) + tuple(-1 if signs >> i & 1 else 1 for i in range(7)))
    roots.sort()
    frame = []
    for i in (0, 2, 4, 6):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[i + 1] = 2, 2 * sign
            frame.append(tuple(root))
    frame.sort()
    require(len(roots) == len(set(roots)) == 120, "120 distinct root lines")
    require(len(frame) == len(set(frame)) == 8 and set(frame) <= set(roots), "eight frame roots")
    require(all(dot(root, root) == 8 for root in roots), "root norm")
    require(all(dot(a, b) == 0 for a, b in combinations(frame, 2)), "orthogonal frame")
    return tuple(roots), tuple(frame)


def declared_labels(path, roots):
    tree = ast.parse(path.read_bytes(), filename=str(path))
    declarations = [node.value for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "SIMPLE"
                            for target in node.targets)]
    require(len(declarations) == 1, "unique literal SIMPLE declaration")
    simple = ast.literal_eval(declarations[0])
    require(len(simple) == 8 and all(len(row) == 8 for row in simple), "SIMPLE shape")
    transform = inverse(tuple(zip(*simple)))
    labels = []
    for root in roots:
        coordinates = [dot(row, root) for row in transform]
        require(all(x.denominator == 1 for x in coordinates), "integral simple coordinates")
        labels.append(1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(coordinates)))
    return tuple(labels)


def model(source_geometry):
    roots, frame = roots_and_frame()
    pairings = [[dot(a, b) for b in roots] for a in roots]
    require(all(value % 4 == 0 for row in pairings for value in row), "polar divisibility")
    polar_rows = [sum(((value // 4) % 2) << j for j, value in enumerate(row))
                  for row in pairings]
    basis_ids = []
    for i in range(120):
        if binary_rank([polar_rows[j] for j in basis_ids] + [polar_rows[i]]) > len(basis_ids):
            basis_ids.append(i)
    require(len(basis_ids) == 8, "polar quotient rank eight")
    labels = tuple(1 | sum(((pairings[i][j] // 4) % 2) << (k + 1)
                          for k, j in enumerate(basis_ids)) for i in range(120))
    require(len(set(labels)) == 120 and binary_rank(labels) == 9, "independent label embedding")
    source_labels = declared_labels(source_geometry, roots)
    require(binary_rank(source_labels) == 9, "declared label rank")
    require(binary_rank([old | (new << 9) for old, new in zip(source_labels, labels)]) == 9,
            "label embeddings fail invertible linear transfer")
    # Both embeddings have literal leading bit one on every root. The full
    # rank-nine transfer therefore preserves the leading coordinate.
    frame_ids = tuple(roots.index(root) for root in frame)
    live_ids = tuple(i for i in range(120) if i not in frame_ids)
    return roots, frame, frame_ids, live_ids, labels, pairings


def checks(source_geometry, mutation=None):
    roots, frame, frame_ids, live_ids, labels, pairings = model(source_geometry)
    if mutation == "omit-live-root":
        live_ids = live_ids[:-1]
    neighbors = [set(i for i in live_ids if pairings[fi][i]) for fi in frame_ids]
    require(all(len(sites) == 56 for sites in neighbors), "56 live frame neighbors")
    matched_cuts = 0
    minimum_matched_missing = 56
    for axis, sites in enumerate(neighbors):
        target_span = binary_span(labels[i] for i in sites)
        require(len(target_span) == 256, "frame neighborhood spans its rank-eight hyperplane")
        require(all(labels[fi] not in target_span for fi in frame_ids),
                "frame-neighborhood hyperplane contains an excluded frame label")
        for normal in range(1, 512):
            if (normal & labels[frame_ids[axis]]).bit_count() % 2:
                continue
            missing = sum((normal & labels[i]).bit_count() % 2 for i in sites)
            require(missing >= 24, "matched rank-eight G2 cut misses fewer than 24 target sites")
            minimum_matched_missing = min(minimum_matched_missing, missing)
            matched_cuts += 1
    require(matched_cuts == 2040 and minimum_matched_missing == 24,
            "incomplete or unsharp matched-cut G2 domain")
    pair_records = []
    deletion_checks = 0
    stratum_checks = 0
    for a in range(8):
        for b in range(8):
            if a == b:
                continue
            first_pair = (a, b) == (0, 1)
            na, nb = neighbors[a], neighbors[b]
            x, y, common = nb - na, na - nb, na & nb
            require((len(x), len(y), len(common)) == (32, 32, 24), "orthogonal frame region sizes")
            span_x = binary_span(labels[i] for i in x)
            require(len(span_x) == 128, "completion rank seven")
            for deleted in x:
                require(binary_rank(labels[i] for i in x if i != deleted) == 7,
                        "completion loses rank on one-site deletion")
                deletion_checks += 1
            matched_label = labels[frame_ids[b]]
            if mutation == "matched-live-label" and first_pair:
                matched_label = labels[min(na)]
            hyperplane = binary_span(tuple(span_x) + (matched_label,))
            require(len(hyperplane) == 256, "completion plus matched label has rank eight")
            require(all((labels[i] in hyperplane) == (pairings[frame_ids[a]][i] % 8 == 0)
                        for i in range(120)), "matched hyperplane is ker b_a")
            require(not any(labels[i] in hyperplane for i in na), "matched hyperplane meets N_a")
            span_y = binary_span(labels[i] for i in y)
            require(len(span_y) == 128, "opposite completion rank")
            require(all(labels[i] not in span_y for i in common),
                    "common neighbor fails to raise completion rank")
            ratios = {}
            for i in sorted(common):
                ratio = Fraction(pairings[frame_ids[b]][i], pairings[frame_ids[a]][i])
                if mutation == "common-ratio-sign" and first_pair and i == min(common):
                    ratio = -ratio
                ratios[ratio] = ratios.get(ratio, 0) + 1
            require(ratios == {Fraction(-1): 12, Fraction(1): 12}, "common-neighbor ratio split")
            ranks = {}
            # Every characteristic-zero coefficient ratio belongs to one of
            # c=0,+1,-1 or c not in {0,+1,-1}. c=2 represents the last support
            # stratum: only the pairings 0,+/-4 occur on N_a.
            for coefficient in (0, 1, -1, 2):
                used_coefficient = coefficient
                if mutation == "generic-coefficient" and first_pair and coefficient == 2:
                    used_coefficient = 1
                support = [i for i in na if pairings[frame_ids[a]][i]
                           + used_coefficient * pairings[frame_ids[b]][i]]
                require(len(support) == (44 if coefficient in (-1, 1) else 56),
                        "wrong characteristic-zero support stratum")
                ranks[str(coefficient)] = binary_rank(labels[i] for i in support)
                require(ranks[str(coefficient)] == 8, "restricted two-frame combination has rank below eight")
                stratum_checks += 1
            pair_records.append({"a": a, "b": b, "completion_size": len(x),
                                 "completion_rank": 7, "matched_hyperplane_rank": 8,
                                 "ratio_multiplicities": {"-1": 12, "1": 12},
                                 "restricted_plane_stratum_ranks": ranks})
    require(len(pair_records) == 56 and deletion_checks == 1792 and stratum_checks == 224,
            "incomplete ordered frame-pair domain")
    return {"status": "pass", "scope": "frame-pair geometry only; no actual invoice enumeration",
            "source_geometry_sha256": sha256(source_geometry.read_bytes()).hexdigest(),
            "ordered_frame_pairs": len(pair_records), "one_site_deletions": deletion_checks,
            "matched_G2_cuts": matched_cuts,
            "minimum_matched_G2_missing": minimum_matched_missing,
            "characteristic_zero_support_strata": stratum_checks,
            "records_sha256": sha256(json.dumps(pair_records, sort_keys=True,
                                                separators=(",", ":")).encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-geometry", type=Path, required=True)
    parser.add_argument("--mutation", choices=("matched-live-label", "common-ratio-sign",
                                              "omit-live-root", "generic-coefficient"))
    args = parser.parse_args()
    print(json.dumps(checks(args.source_geometry, args.mutation), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
