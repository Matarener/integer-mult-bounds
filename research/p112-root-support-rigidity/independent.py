"""Separate forward-basis affine-coset enumeration. Apache-2.0."""

from itertools import combinations, product

import common


def affine_sections(labels, dimension):
    common.require(dimension in (4, 5), "affine dimension")
    root_at = [0] * 256
    for i, label in enumerate(labels):
        root_at[label >> 1] = 1 << i
    for pivots in combinations(range(8), dimension):
        complement = tuple(c for c in range(8) if c not in pivots)
        choices = []
        for pivot in pivots:
            free = tuple(c for c in complement if c > pivot)
            choices.append(
                tuple(
                    (1 << pivot) | sum(((v >> j) & 1) << c for j, c in enumerate(free))
                    for v in range(1 << len(free))
                )
            )
        offsets = tuple(
            sum(((v >> j) & 1) << c for j, c in enumerate(complement))
            for v in range(1 << len(complement))
        )
        for basis in product(*choices):
            span = [0]
            for row in basis:
                span += [x ^ row for x in span]
            for offset in offsets:
                yield sum(root_at[x ^ offset] for x in span)


def census(labels, off, permutation, expected):
    dimension = expected["dimension"]
    histogram, critical = [0] * 121, set()
    boundary, maximum, total = None, 0, 0
    for mask in affine_sections(labels, dimension - 1):
        n = (mask & off).bit_count()
        histogram[n] += 1
        maximum = max(maximum, mask.bit_count())
        total += 1
        if n >= expected["threshold"]:
            indices = {i for i in range(120) if mask >> i & 1}
            common.require(len(indices) == expected["capacity"], "affine closure size")
            common.require(0 not in indices, "affine normal root excluded")
            common.require(
                all(off >> i & 1 for i in indices), "affine closure off normal"
            )
            common.require(
                {permutation[i] for i in indices} == indices,
                "affine reflection invariance",
            )
            critical.add(mask)
            common.require(len(critical) <= 4096, "affine critical storage bound")
        elif n == expected["threshold"] - 1:
            image = sum(1 << permutation[i] for i in range(120) if mask >> i & 1)
            if image != mask and (boundary is None or mask < boundary):
                boundary = mask
    empty_even_spaces = {5: 97155, 6: 10795}[dimension]
    histogram[0] += empty_even_spaces
    observed = {
        "dimension": dimension,
        "subspaces": total + empty_even_spaces,
        "capacity": maximum,
        "threshold": expected["threshold"],
        "off_histogram": {str(i): n for i, n in enumerate(histogram) if n},
        "critical_count": len(critical),
        "critical_sha256": common.mask_digest(critical),
        "boundary_mask": f"{boundary:030x}",
    }
    common.require(
        common.same_json(observed, expected), "separate affine census receipt"
    )
    return total


def main():
    g, roots, _, labels = common.model()
    off = sum(1 << i for i, r in enumerate(roots) if g.dot(r, roots[0]))
    permutation = common.reflect(roots, roots[0], g.dot, g.canonical)
    expected = common.read_json(common.HERE / "RESULT.json")
    counts = [census(labels, off, permutation, row) for row in expected["sections"]]
    common.require(counts == [3212592, 777240], "complete affine-space counts")
    print("PASS_P112_ROOT_SUPPORT_AFFINE affine_sections=3989832 shared_geometry")


if __name__ == "__main__":
    main()
