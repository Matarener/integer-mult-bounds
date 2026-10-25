"""Separate four-root-basis reconstruction of the near-axis bound. Apache-2.0."""

from itertools import combinations

from common import HERE, basis, coordinates, digest, geometry, read_json, require, same


def span(generators):
    values = {0}
    require(len(generators) <= 6, "small support span")
    for generator in generators:
        values |= {x ^ generator for x in values}
    return values


def independent_near(roots, labels, g, a, b):
    axis = tuple(
        i for i, r in enumerate(roots) if g.dot(roots[a], r) and not g.dot(roots[b], r)
    )
    bulk = tuple(i for i in axis if i != a)
    masks, seen = set(), set()
    for chosen in combinations(bulk, 4):
        values = span(tuple(labels[i] for i in chosen))
        if len(values) != 16:
            continue
        key = frozenset(values)
        if key in seen:
            continue
        seen.add(key)
        section = tuple(i for i in bulk if labels[i] in values)
        if len(section) != 8:
            continue
        ambient = values | {x ^ labels[a] for x in values}
        require(len(ambient) == 32, "exception adds one binary dimension")
        mask = sum(1 << i for i, x in enumerate(labels) if x in ambient)
        require(
            (mask & sum(1 << i for i in axis)).bit_count() == 9,
            "exactly nine axis roots",
        )
        require(mask.bit_count() == 12, "whole-root near-axis closure")
        masks.add(mask)
    require(len(masks) == 60, "complete near-axis basis reconstruction")
    return masks


def high_sections(roots, labels, g, a, b):
    bulk = tuple(
        i
        for i, r in enumerate(roots)
        if i != a and g.dot(roots[a], r) and not g.dot(roots[b], r)
    )
    # Rank-six concentration14 confines every >16 section to this bulk seven-space.
    mapping = coordinates(tuple(labels[i] for i in bulk))
    require(len(mapping) == 128, "bulk seven-space")
    sections = {
        sum(1 << i for i in bulk if not (mapping[labels[i]] & normal).bit_count() % 2)
        for normal in range(1, 128)
    }
    high = {m for m in sections if m.bit_count() > 16}
    require(
        len(high) == 16 and {m.bit_count() for m in high} == {20},
        "all large bulk hyperplanes",
    )
    return high


def main():
    g, roots, _, labels, _ = geometry()
    a = 0
    b = next(i for i, r in enumerate(roots) if not g.dot(roots[a], r))
    near = independent_near(roots, labels, g, a, b)
    high = [
        high_sections(roots, labels, g, a, b),
        high_sections(roots, labels, g, b, a),
    ]
    union = sum(
        1 << i for i, r in enumerate(roots) if g.dot(roots[a], r) or g.dot(roots[b], r)
    )
    maximum = max(
        ((x | y | z) & union).bit_count()
        for x in near
        for y in high[0]
        for z in high[1]
    )
    require(maximum == 45, "separate full-plane union bound")
    expected = read_json(HERE / "RESULT.json")["near_axis"]
    same(digest(near), expected["near_sha256"])
    same([digest(h) for h in high], expected["high_sha256"])
    # Nine leading-one labels cannot have rank at most four.
    witness = expected["witness_root_indices"]
    require(len(basis(tuple(labels[i] for i in witness))) == 5, "literal witness rank")
    print("PASS_SEPARATE_NEAR_AXIS bases=35960 near=60 high=16,16 coverage=45")


if __name__ == "__main__":
    main()
