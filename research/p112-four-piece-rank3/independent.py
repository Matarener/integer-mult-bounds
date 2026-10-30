"""Separate affine-flat enumeration and residual-intersection check. Apache-2.0.

The forward-basis affine-coset method follows the attributed PR3397 replay.
It shares authenticated geometry and digest serialization with the primary.
"""

import hashlib
from collections import Counter
from itertools import combinations, product

import common


def affine_sections(labels, dimension):
    common.require(dimension in (4, 5), "affine dimension")
    at_point = [0] * 256
    for index, label in enumerate(labels):
        at_point[label >> 1] = 1 << index
    for pivots in combinations(range(8), dimension):
        complement = tuple(c for c in range(8) if c not in pivots)
        row_options = []
        for pivot in pivots:
            free = tuple(c for c in complement if c > pivot)
            row_options.append(
                tuple(
                    (1 << pivot) | sum(((v >> j) & 1) << c for j, c in enumerate(free))
                    for v in range(1 << len(free))
                )
            )
        offsets = tuple(
            sum(((v >> j) & 1) << c for j, c in enumerate(complement))
            for v in range(1 << len(complement))
        )
        for basis in product(*row_options):
            vectors = [0]
            for row in basis:
                vectors += [value ^ row for value in vectors]
            for offset in offsets:
                yield sum(at_point[value ^ offset] for value in vectors)


def reconstruct_sections(labels, support, expected):
    dimension = expected["dimension"]
    histogram, found = Counter(), set()
    total, maximum = 0, 0
    for mask in affine_sections(labels, dimension - 1):
        size = (mask & support).bit_count()
        histogram[size] += 1
        total += 1
        maximum = max(maximum, mask.bit_count())
        if size >= expected["threshold"]:
            found.add(mask & support)
    common.require(total == {5: 3212592, 6: 777240}[dimension], "affine census count")
    leading_zero_spaces = {5: 97155, 6: 10795}[dimension]
    histogram[0] += leading_zero_spaces
    observed = {
        "dimension": dimension,
        "subspaces": total + leading_zero_spaces,
        "full_root_capacity": maximum,
        "threshold": expected["threshold"],
        "support_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "sections": len(found),
        "section_sha256": common.mask_digest(found),
    }
    common.require(common.same_json(observed, expected), "independent section census")
    return found


def intersect_check(support, fives, sixes, expected):
    histogram, profiles = Counter(), []
    maximum = 0
    for left, right in combinations(sorted(sixes), 2):
        joined = left | right
        histogram[joined.bit_count()] += 1
        residual = support ^ joined
        if residual.bit_count() <= 16:
            covered = max((five & residual).bit_count() for five in fives)
            minimum = residual.bit_count() - covered
            common.require(minimum >= 5, "independent four-site cover")
            maximum = max(maximum, support.bit_count() - minimum)
            profiles.append((joined, minimum))
    text = "".join(f"{mask:030x}:{size}\n" for mask, size in sorted(profiles))
    checks = {
        "pair_union_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "eligible_pairs": len(profiles),
        "tested_pair_five_combinations": len(profiles) * len(fives),
        "pair_minimum_remainder_histogram": {
            str(key): value
            for key, value in sorted(Counter(n for _, n in profiles).items())
        },
        "pair_minimum_remainder_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "maximum_candidate_large_union": maximum if profiles else None,
        "other_pairs_union_bound": support.bit_count() - 17 + 12,
        "four_site_covers": 0,
    }
    for key, observed in checks.items():
        common.require(
            common.same_json(observed, expected[key]), "independent cover " + key
        )


def check_partition(row, roots, labels, live):
    masks = [
        int(value, 16) for value in row["cover"]["maximum_candidate_partition_witness"]
    ]
    normal = row["normal"]
    live = set(live)
    support = {
        i
        for i, root in enumerate(roots)
        if root in live and sum(x * y for x, y in zip(root, normal, strict=True))
    }
    pieces = [{i for i in range(120) if mask >> i & 1} for mask in masks]
    common.require(
        set.union(*pieces) == support and sum(map(len, pieces)) == len(support),
        "boundary partition coverage",
    )
    ranks = [common.rank_labels([labels[i] for i in piece]) for piece in pieces]
    common.require(
        len(pieces[0]) == 5 and ranks == [5, 5, 6, 6], "five-site boundary ranks"
    )
    for index, root in enumerate(roots):
        value = (
            sum(x * y for x, y in zip(root, normal, strict=True))
            if index in support
            else 0
        )
        piece_values = [value if index in piece else 0 for piece in pieces]
        common.require(sum(piece_values) == value, "literal coefficient identity")


def main():
    g, roots, live, labels, _ = common.model()
    receipt = common.read_json(common.HERE / "RESULT.json")
    common.require(receipt["piece_ranks"] == [3, 5, 6, 6], "declared rank domain")
    common.require(len(receipt["normal_cases"]) == 3, "normal case count")
    for normal, row in zip(
        common.representatives(roots, live), receipt["normal_cases"], strict=True
    ):
        common.require(list(normal) == row["normal"], "representative identity")
        support = sum(
            1 << i
            for i, root in enumerate(roots)
            if root in live and g.dot(root, normal)
        )
        fives = reconstruct_sections(labels, support, row["five_sections"])
        sixes = reconstruct_sections(labels, support, row["six_sections"])
        intersect_check(support, fives, sixes, row["cover"])
        if row["support"] == 53:
            check_partition(row, roots, labels, live)
    print(
        "PASS_P112_RANK3_AFFINE normal_cases=3 affine_sections=11969496 "
        "five_site_boundary=yes"
    )


if __name__ == "__main__":
    main()
