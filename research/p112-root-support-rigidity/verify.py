"""Full annihilator census and literal frame transport. Apache-2.0."""

import argparse
from itertools import combinations, product
from pathlib import Path

import common


def flat_masks(labels, dimension):
    common.require(dimension in (5, 6) and len(labels) == 120, "census domain")
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


def census(labels, off, permutation, dimension):
    capacity, threshold, count = {5: (12, 11, 3309747), 6: (20, 17, 788035)}[dimension]
    histogram = [0] * 121
    critical, boundary = set(), None
    total, maximum = 0, 0
    for mask in flat_masks(labels, dimension):
        n = (mask & off).bit_count()
        histogram[n] += 1
        total += 1
        maximum = max(maximum, mask.bit_count())
        if n >= threshold:
            common.section_check(mask, off, permutation, capacity)
            critical.add(mask)
            common.require(len(critical) <= 4096, "critical section storage bound")
        elif n == threshold - 1:
            image = sum(1 << permutation[i] for i in range(120) if mask >> i & 1)
            if image != mask and (boundary is None or mask < boundary):
                boundary = mask
    common.require(total == count and maximum == capacity, "complete capacity census")
    common.require(boundary is not None, "strict threshold boundary witness")
    return {
        "dimension": dimension,
        "subspaces": total,
        "capacity": maximum,
        "threshold": threshold,
        "off_histogram": {str(i): n for i, n in enumerate(histogram) if n},
        "critical_count": len(critical),
        "critical_sha256": common.mask_digest(critical),
        "boundary_mask": f"{boundary:030x}",
    }


def transport(g, roots, live, labels):
    generators = [common.reflect(roots, s, g.dot, g.canonical) for s in g.SIMPLE]
    for j, permutation in enumerate(generators):
        cartan = [g.dot(s, g.SIMPLE[j]) // 4 for s in g.SIMPLE]
        for i, label in enumerate(labels):
            parity = sum(c * ((label >> (k + 1)) & 1) for k, c in enumerate(cartan)) % 2
            common.require(
                labels[permutation[i]] == label ^ (parity << (j + 1)),
                "linear simple-reflection label action",
            )
    reached, queue = {0}, [0]
    for position in range(120):
        common.require(position < len(queue), "root orbit terminated early")
        for permutation in generators:
            image = permutation[queue[position]]
            if image not in reached:
                reached.add(image)
                queue.append(image)
    common.require(len(reached) == 120, "transitive root orbit")
    frame = set(roots) - set(live)
    for normal in live:
        permutation = common.reflect(roots, normal, g.dot, g.canonical)
        active = [f for f in frame if g.dot(f, normal)]
        partners = {roots[permutation[roots.index(f)]] for f in active}
        common.require(len(active) == len(partners) == 4, "four frame partners")
        common.require(partners <= set(live) - {normal}, "distinct live partners")
        common.require(all(g.dot(p, normal) for p in partners), "partners in support")
    return {
        "linear_label_checks": 960,
        "normal_orbit": 120,
        "live_normals": 112,
        "missing_frame_partners_each": 4,
    }


def result():
    g, roots, live, labels = common.model()
    off = sum(1 << i for i, r in enumerate(roots) if g.dot(r, roots[0]))
    permutation = common.reflect(roots, roots[0], g.dot, g.canonical)
    capacities = [2, 12, 20, 20]
    slack = sum(capacities) - 53
    forced_partners = 4 - (capacities[0] - 1)
    common.require(
        slack == 1 and forced_partners > slack, "frame-partner contradiction"
    )
    common.require(
        capacities[1] - slack >= 11 and capacities[2] - slack >= 17,
        "singleton thresholds reached",
    )
    return {
        "schema_version": 1,
        "sections": [census(labels, off, permutation, d) for d in (5, 6)],
        "transport": transport(g, roots, live, labels),
        "chamber": g.chamber_receipt(roots, live, g.root_data()[3]),
        "support_budget": {
            "piece_ranks": [2, 5, 6, 6],
            "capacities": capacities,
            "sum": sum(capacities),
            "root_support": 53,
            "slack": slack,
            "forced_large_piece_partners": forced_partners,
            "intersection_dimension": 0,
        },
        "caller": {
            "profile": [2, 5] + [6] * 8,
            "quotient_dimension": 4,
            "distinct_projective_endpoints": 8,
            "full_exclusion": False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=common.HERE / "RESULT.json")
    args = parser.parse_args()
    observed = result()
    common.require(
        common.same_json(observed, common.read_json(args.receipt)),
        "exact typed result receipt",
    )
    print(
        "PASS_P112_ROOT_SUPPORT_RIGIDITY flats=4097782 thresholds=11,17 span2566=0 no_new_kappa"
    )


if __name__ == "__main__":
    main()
