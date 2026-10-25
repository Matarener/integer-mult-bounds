"""Exact kernel census and complete four-piece cover exclusion. Apache-2.0."""

import argparse
import hashlib
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path

import common

COUNTS = {5: 3309747, 6: 788035}
CAPACITIES = {5: 12, 6: 20}


def flat_masks(labels, dimension):
    common.require(dimension in (5, 6) and len(labels) == 120, "flat domain")
    kernels = tuple(
        sum(1 << i for i, label in enumerate(labels) if not (label & h).bit_count() % 2)
        for h in range(512)
    )
    for pivots in combinations(range(9), 9 - dimension):
        choices = []
        for pivot in pivots:
            free = tuple(c for c in range(pivot) if c not in pivots)
            choices.append(
                tuple(
                    kernels[
                        (1 << pivot)
                        | sum(((v >> j) & 1) << c for j, c in enumerate(free))
                    ]
                    for v in range(1 << len(free))
                )
            )
        for chosen in product(*choices):
            mask = kernels[0]
            for row in chosen:
                mask &= row
            yield mask


def section_census(labels, support, dimension):
    threshold = CAPACITIES[dimension] - (56 - support.bit_count())
    histogram, sections = Counter(), set()
    total, maximum = 0, 0
    for mask in flat_masks(labels, dimension):
        live = mask & support
        size = live.bit_count()
        histogram[size] += 1
        total += 1
        maximum = max(maximum, mask.bit_count())
        if size >= threshold:
            sections.add(live)
    common.require(total == COUNTS[dimension], "unique complete flat census")
    common.require(maximum == CAPACITIES[dimension], "full-root capacity")
    common.require(len(sections) <= 12000, "eligible section storage")
    return sorted(sections), {
        "dimension": dimension,
        "subspaces": total,
        "full_root_capacity": maximum,
        "threshold": threshold,
        "support_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "sections": len(sections),
        "section_sha256": common.mask_digest(sections),
    }


def cover_check(support, fives, sixes, excluded_small_limit=4):
    common.require(excluded_small_limit in (4, 5), "small-support control domain")
    histogram, profiles, pairs = Counter(), [], []
    for left, right in combinations(sixes, 2):
        union = left | right
        histogram[union.bit_count()] += 1
        if (support & ~union).bit_count() <= 16:
            pairs.append((left, right))
    maximum, witness = 0, None
    for left, right in pairs:
        union = left | right
        remaining = support & ~union
        minimum = 120
        for five in fives:
            small = remaining & ~five
            minimum = min(minimum, small.bit_count())
            covered = (union | five).bit_count()
            if covered > maximum:
                maximum = covered
                witness = [
                    f"{m:030x}" for m in (small, five & ~union, left, right & ~left)
                ]
        profiles.append((union, minimum))
        common.require(minimum > excluded_small_limit, "small-piece cover exists")
    profile_text = "".join(f"{mask:030x}:{size}\n" for mask, size in sorted(profiles))
    return {
        "pair_union_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "eligible_pairs": len(pairs),
        "tested_pair_five_combinations": len(pairs) * len(fives),
        "pair_minimum_remainder_histogram": {
            str(key): value
            for key, value in sorted(Counter(size for _, size in profiles).items())
        },
        "pair_minimum_remainder_sha256": hashlib.sha256(
            profile_text.encode()
        ).hexdigest(),
        "maximum_candidate_large_union": maximum if pairs else None,
        "maximum_candidate_partition_witness": witness,
        "other_pairs_union_bound": support.bit_count() - 17 + 12,
        "four_site_covers": 0,
    }


def coordinate_generators():
    generators = []
    for pair in range(4):
        permutation = list(range(8))
        permutation[2 * pair], permutation[2 * pair + 1] = 2 * pair + 1, 2 * pair
        generators.append((tuple(permutation), (1,) * 8))
    for pair in range(3):
        permutation = list(range(8))
        for side in range(2):
            permutation[2 * pair + side], permutation[2 * pair + side + 2] = (
                2 * pair + side + 2,
                2 * pair + side,
            )
        generators.append((tuple(permutation), (1,) * 8))
    for other in range(1, 8):
        generators.append(
            (tuple(range(8)), tuple(-1 if i in (0, other) else 1 for i in range(8)))
        )
    return generators


def coordinate_image(row, permutation, signs):
    return tuple(signs[i] * row[permutation[i]] for i in range(8))


def orbit_transport(g, roots, live, labels, representatives):
    index, permutations = {root: i for i, root in enumerate(roots)}, []
    matrix = tuple(zip(*g.SIMPLE, strict=True))
    for permutation, signs in coordinate_generators():
        images = [
            index[g.canonical(coordinate_image(root, permutation, signs))]
            for root in roots
        ]
        common.require({roots[i] for i in images} == set(roots), "root automorphism")
        common.require(
            {roots[images[index[r]]] for r in live} == set(live), "live automorphism"
        )
        columns = [
            g.solve(matrix, coordinate_image(simple, permutation, signs))
            for simple in g.SIMPLE
        ]
        common.require(
            all(x.denominator == 1 for col in columns for x in col), "lattice action"
        )
        for i, label in enumerate(labels):
            image = 1 | sum(
                (
                    sum(int(columns[j][k]) * ((label >> (j + 1)) & 1) for j in range(8))
                    % 2
                )
                << (k + 1)
                for k in range(8)
            )
            common.require(labels[images[i]] == image, "linear label transport")
        permutations.append(images)
    orbits = []
    for normal in representatives:
        reached, queue = {index[normal]}, [index[normal]]
        for position in range(120):
            if position >= len(queue):
                break
            for permutation in permutations:
                image = permutation[queue[position]]
                if image not in reached:
                    reached.add(image)
                    queue.append(image)
        orbits.append(reached)
    common.require([len(o) for o in orbits] == [48, 64, 8], "three root-normal orbits")
    common.require(len(set.union(*orbits)) == 120, "normal orbit coverage")
    return {
        "coordinate_generators": 14,
        "linear_label_checks": 1680,
        "normal_orbits": [48, 64, 8],
        "normal_coverage": 120,
    }


def result():
    g, roots, live, labels, coordinates = common.model()
    normals = common.representatives(roots, live)
    rows = []
    for normal in normals:
        support = sum(
            1 << i
            for i, root in enumerate(roots)
            if root in live and g.dot(root, normal)
        )
        fives, five_receipt = section_census(labels, support, 5)
        sixes, six_receipt = section_census(labels, support, 6)
        rows.append(
            {
                "normal": normal,
                "support": support.bit_count(),
                "five_sections": five_receipt,
                "six_sections": six_receipt,
                "cover": cover_check(support, fives, sixes),
            }
        )
    return {
        "schema_version": 1,
        "piece_ranks": [3, 5, 6, 6],
        "capacities": [4, 12, 20, 20],
        "support_budget": 56,
        "transport": orbit_transport(g, roots, live, labels, normals),
        "chamber": g.chamber_receipt(roots, live, coordinates),
        "normal_cases": rows,
        "code_intersection_dimension": 0,
        "standard_weyl_chamber_premise": True,
        "new_kappa": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=common.HERE / "RESULT.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    observed = result()
    if args.output:
        output = args.output.expanduser().resolve()
        common.require(
            not output.is_relative_to(common.ROOT), "external receipt output required"
        )
        with output.open("x") as stream:
            stream.write(json.dumps(observed, indent=2) + "\n")
    else:
        common.require(
            common.same_json(observed, common.read_json(args.receipt)),
            "exact typed receipt",
        )
    print(
        "PASS_P112_FOUR_PIECE_RANK3 normals=120 ranks=3,5,6,6 "
        "intersection=0 conditional_no_new_kappa"
    )


if __name__ == "__main__":
    main()
