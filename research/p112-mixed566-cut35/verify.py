"""Conditional mixed566 common-cut35 proof checks. Apache-2.0."""

import argparse
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from common import (
    HERE,
    ROOT,
    basis,
    coordinates,
    digest,
    geometry,
    read_json,
    require,
    same,
)


def echelon_spaces(n, codimension):
    require(n == 8 and codimension in (2, 3), "bounded Grassmannian")
    for pivots in combinations(range(n), codimension):
        choices = []
        for pivot in pivots:
            free = tuple(i for i in range(pivot) if i not in pivots)
            choices.append(
                tuple(
                    (1 << pivot)
                    | sum(((code >> j) & 1) << i for j, i in enumerate(free))
                    for code in range(1 << len(free))
                )
            )
        yield from product(*choices)


def closures(labels, axis, rank):
    mapping = coordinates(tuple(labels[i] for i in axis))
    require(len(mapping) == 256 and len(axis) == 33, "axis spans eight bits")
    kernels = tuple(
        sum(
            1 << i
            for i, x in enumerate(labels)
            if x in mapping and not (mapping[x] & normal).bit_count() % 2
        )
        for normal in range(256)
    )
    masks, count = set(), 0
    for rows in echelon_spaces(8, 8 - rank):
        mask = (1 << 120) - 1
        for normal in rows:
            mask &= kernels[normal]
        masks.add(mask)
        count += 1
    require(count == {5: 97155, 6: 10795}[rank], "complete subspace count")
    return masks


def model(g, roots):
    pair = (0, next(j for j, r in enumerate(roots) if not g.dot(roots[0], r)))
    a, b = (roots[i] for i in pair)
    axes = tuple(
        tuple(
            i for i, r in enumerate(roots) if g.dot(first, r) and not g.dot(second, r)
        )
        for first, second in ((a, b), (b, a))
    )
    masks = tuple(sum(1 << i for i in axis) for axis in axes)
    union = sum(1 << i for i, r in enumerate(roots) if g.dot(a, r) or g.dot(b, r))
    require(union.bit_count() == 90 and not masks[0] & masks[1], "D6 plane fibers")
    return pair, axes, masks, union


def near_axis(labels, axes, masks, union):
    five = closures(labels, axes[0], 5)
    near = {m for m in five if (m & masks[0]).bit_count() >= 9 and m & ~masks[0]}
    require(len(near) == 60, "all nonconcentrated near-axis closures")
    require(
        {((m & masks[0]).bit_count(), m.bit_count()) for m in near} == {(9, 12)},
        "nine axis labels and twelve total labels",
    )
    high = []
    for axis, mask in zip(axes, masks, strict=True):
        sections = {m & mask for m in closures(labels, axis, 6)}
        large = {m for m in sections if m.bit_count() > 16}
        require(
            len(large) == 16 and {m.bit_count() for m in large} == {20},
            "all high rank-six sections",
        )
        high.append(large)
    maxima = Counter(
        max(((a | b | c) & union).bit_count() for b in high[0] for c in high[1])
        for a in near
    )
    require(maxima == {45: 60}, "near-axis full-plane coverage")
    witness = min(near)
    return {
        "near_five_closures": len(near),
        "near_sha256": digest(near),
        "high_six_closures": [len(h) for h in high],
        "high_sha256": [digest(h) for h in high],
        "comparisons": len(near) * len(high[0]) * len(high[1]),
        "maximum_coverage": 45,
        "maximum_histogram": dict(maxima),
        "witness_root_indices": [i for i in range(120) if witness >> i & 1],
    }


def transport(g, roots, labels, pair):
    index = {r: i for i, r in enumerate(roots)}
    permutations = []
    for simple in g.SIMPLE:
        permutation = tuple(
            index[
                g.canonical(
                    tuple(
                        x - g.dot(r, simple) // 4 * y
                        for x, y in zip(r, simple, strict=True)
                    )
                )
            ]
            for r in roots
        )
        require(len(set(permutation)) == 120, "root permutation")
        graph = tuple(labels[i] | labels[permutation[i]] << 9 for i in range(120))
        require(
            len(basis(graph, 18)) == len(basis(labels)) == 9,
            "invertible linear label transport",
        )
        permutations.append(permutation)
    expected = {
        (i, j) for i in range(120) for j in range(120) if not g.dot(roots[i], roots[j])
    }
    require(len(expected) == 7560, "ordered orthogonal pair inventory")
    queue, visited = [pair], {pair}
    for cursor in range(7560):
        require(cursor < len(queue), "orbit exhausted early")
        a, b = queue[cursor]
        for permutation in permutations:
            image = permutation[a], permutation[b]
            if image not in visited:
                visited.add(image)
                queue.append(image)
    require(visited == expected, "complete ordered-axis orbit")
    return len(visited)


def inventory(g, roots, points, coordinates_):
    counts = Counter()
    for a, b in combinations(roots, 2):
        if g.dot(a, b):
            continue
        size = sum(bool(g.dot(a, r) or g.dot(b, r)) for r in points)
        counts[size] += 1
        if size == 82:
            for first, second in ((a, b), (b, a)):
                punctures = tuple(
                    r
                    for r in roots
                    if g.dot(first, r) and not g.dot(second, r) and r not in points
                )
                require(len(punctures) == 4, "union82 four punctures")
                require(
                    all(not g.dot(x, y) for x, y in combinations(punctures, 2)),
                    "orthogonal frame punctures",
                )
    require(counts == {82: 448, 84: 2688, 85: 448, 86: 168, 88: 28}, "all D6 unions")
    five = [
        sum(all(c[i] == 0 for i in omitted) for c in coordinates_)
        for omitted in combinations(range(8), 3)
    ]
    six = [
        sum(all(c[i] == 0 for i in omitted) for c in coordinates_)
        for omitted in combinations(range(8), 2)
    ]
    require(
        max(five) == 20 and {n for n in six if n >= 25} == {30, 36},
        "normalization at twenty-five zeros",
    )
    require(max(n for n in six if n < 25) == 21, "other parabolics")
    return dict(counts)


def axis_upper(assignment, capacities, size):
    require(len(assignment) == 3 and set(assignment) <= {0, 1}, "axis assignment")
    total = 0
    for axis in range(2):
        group = [i for i in range(3) if assignment[i] == axis]
        bound = min(size, sum(capacities[i] for i in group))
        if len(group) == 2 and 0 in group:
            bound = min(bound, 28)
        total += bound
    return total


def arithmetic(cut=35):
    require(type(cut) is int and 0 <= cut <= 36, "common-cut bound")
    require(2 * (78 - cut) > 20 + 32 + 32, "strict E6 gap")
    # Union82: two concentrated rank-six pieces have capacities eighteen.
    retained = 82 - cut
    require(retained - 36 >= 10, "refined rank-five concentration")
    bounds82 = [axis_upper(a, (12, 18, 18), 29) for a in product((0, 1), repeat=3)]
    require(max(bounds82) < retained, "union82 strict two-axis bound")
    # Union84: a nonconcentrated rank-five piece has nine singleton axis sites.
    require(84 - cut >= 49 and (84 - cut) - 32 >= 14, "union84 six concentration")
    require(max(48, 45) < 84 - cut, "union84 concentrated or near-axis bound")
    larger = {}
    for union in (85, 86):
        n = union - cut
        require(n - 40 >= 10 and n - 32 >= 14, "all-piece concentration")
        bounds = [axis_upper(a, (12, 20, 20), 33) for a in product((0, 1), repeat=3)]
        require(max(bounds) < n, "larger-union strictness")
        larger[str(union)] = {"required": n, "upper": max(bounds)}
    return {
        "cut": cut,
        "E6": {"required_twice": 2 * (78 - cut), "upper": 84},
        "D6_82": {"required": retained, "upper": max(bounds82)},
        "D6_84": {
            "required": 84 - cut,
            "concentrated_upper": 48,
            "near_upper": 45,
            "low_six_upper": 48,
        },
        "D6_larger": larger,
    }


def compute():
    g, roots, points, labels, coordinates_ = geometry()
    pair, axes, masks, union = model(g, roots)
    return {
        "status": "PASS_CONDITIONAL_MIXED566_CUT35",
        "arithmetic": arithmetic(),
        "near_axis": near_axis(labels, axes, masks, union),
        "ordered_axis_orbit": transport(g, roots, labels, pair),
        "plane_union_counts": inventory(g, roots, points, coordinates_),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.output is None:
        same(result, read_json(HERE / "RESULT.json"))
    else:
        require(not args.output.resolve().is_relative_to(ROOT), "external output only")
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
