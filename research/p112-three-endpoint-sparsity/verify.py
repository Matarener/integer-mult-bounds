"""Weyl orbit and exact line-pencil proof for the literal P112 caller."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import combinations

import common

PAIRS = tuple(combinations(range(8), 2))


def add(a, b, coefficient=1):
    return tuple(x + coefficient * y for x, y in zip(a, b, strict=True))


def plane(a, b):
    return common.primitive(a[i] * b[j] - a[j] * b[i] for i, j in PAIRS)


def coefficients(a, b, v):
    for i, j in PAIRS:
        determinant = a[i] * b[j] - a[j] * b[i]
        if determinant:
            x = F(v[i] * b[j] - v[j] * b[i], determinant)
            y = F(a[i] * v[j] - a[j] * v[i], determinant)
            return (x, y) if add(tuple(x * z for z in a), b, y) == v else None
    return None


def shell(g):
    roots = g.root_lines()
    reached, queue = {(4, 0, 0, 0, 0, 0, 0, 0)}, [(4, 0, 0, 0, 0, 0, 0, 0)]
    for position in range(1080):
        common.require(position < len(queue), "short D7 orbit")
        for simple in g.SIMPLE:
            vector = g.canonical(
                add(queue[position], simple, -F(g.dot(queue[position], simple), 4))
            )
            common.require(all(x.denominator == 1 for x in vector), "nonintegral shell")
            if vector not in reached:
                reached.add(vector)
                queue.append(vector)
                common.require(len(queue) <= 1080, "D7 orbit bound")
    common.require(len(reached) == 1080, "D7 orbit count")
    lines = {common.primitive(v) for v in roots + tuple(queue)}
    common.require(len(lines) == 1200, "normal-line inventory")
    return roots, tuple(queue), lines


def ordered_pair_orbit(g, roots, a, b):
    signed = tuple(roots) + tuple(tuple(-x for x in r) for r in roots)
    lookup = {r: i for i, r in enumerate(signed)}
    permutations = []
    for simple in g.SIMPLE:
        permutations.append(
            tuple(lookup[add(r, simple, -g.dot(r, simple) // 4)] for r in signed)
        )
    start = (lookup[a], lookup[b])
    reached, queue = {start}, [start]
    for position in range(30240):
        common.require(position < len(queue), "short ordered orthogonal-pair orbit")
        i, j = queue[position]
        for permutation in permutations:
            image = permutation[i], permutation[j]
            if image not in reached:
                reached.add(image)
                queue.append(image)
                common.require(len(queue) <= 30240, "pair orbit bound")
    common.require(len(reached) == 30240, "pair transitivity")
    return len(reached)


def root_pencils(g, roots, lines, a):
    pencils = defaultdict(list)
    for v in sorted(lines):
        if v != common.primitive(a):
            pencils[plane(a, v)].append(v)
    root_lines = {common.primitive(v) for v in roots}
    for b in roots:
        if common.primitive(b) == common.primitive(a):
            continue
        members = set(pencils[plane(a, b)]) | {common.primitive(a)}
        if g.dot(a, b):
            common.require(len(members) == 3 and members <= root_lines, "A2 pencil")
        else:
            expected = {common.primitive(v) for v in (a, b, add(a, b), add(a, b, -1))}
            common.require(members == expected, "B2 pencil")
    return pencils


def affine_candidates(pencils, lines, a, b):
    candidates = set()
    for members in pencils.values():
        common.require(len(members) <= 3, "root pencil capacity")
        for v, w in combinations(members, 2):
            x, y = coefficients(v, w, a)
            for u in (tuple(x * z for z in v), tuple(y * z for z in w)):
                if (
                    coefficients(a, b, u) is None
                    and common.primitive(add(u, b, -1)) in lines
                ):
                    candidates.add(u)
    common.require(len(candidates) == 360, "affine candidate inventory")
    return candidates


def fifth_endpoint(candidates, lines, a, b):
    first, second, complete = set(), set(), set()
    for u in candidates:
        for v in lines:
            xy = coefficients(u, a, v)
            if xy is None or xy[0] == 0:
                continue
            t = -xy[1] / xy[0]
            if t in (0, 1, -1):
                continue
            first.add(u + (t,))
            if common.primitive(add(u, b, t)) not in lines:
                continue
            second.add(u + (t,))
            final = add(add(u, a, -(t + 1) / 2), b, (t - 1) / 2)
            if common.primitive(final) in lines:
                complete.add(u + (t,))
    common.require(
        len(first) == 32 and not second and not complete, "fifth endpoint exclusion"
    )
    return {
        "first_pencil": len(first),
        "first_parameters": sorted({str(v[-1]) for v in first}),
        "second_pencil": len(second),
        "complete": len(complete),
        "first_sha256": common.digest_rows(first),
    }


def incidence_receipt():
    # For k nonzero values among eight endpoints, at most 56-C(8-k,3)
    # triple determinants are nonzero. Its marginal cost never exceeds 21,
    # and after the first incidence never exceeds 15.
    from math import comb

    maximums = [56 - (comb(8 - k, 3) if 8 - k >= 3 else 0) for k in range(9)]
    common.require(all(maximums[k] <= 15 * k + 6 for k in range(9)), "concave charge")
    bounds = [56 * s + 15 * 160 + 6 * (112 - s) for s in range(15)]
    upper = max(bounds)
    roots_needed = (56 * 70 - upper + 16) // 17
    common.require(upper == 3772 and roots_needed == 9, "root-triple quota")
    common.require(
        8 * (7 // 2) // 3 == 8 < roots_needed, "linear packing contradiction"
    )
    return {
        "triples": 56,
        "small_union_cap": 14,
        "large_incidence_cap": 160,
        "triple_incidence_cap": upper,
        "nonroot_distance": 70,
        "root_distance": 53,
        "root_triples_needed": roots_needed,
        "pair_linear_triples_cap": 8,
        "full_caller_excluded_conditionally": True,
    }


def result():
    g = common.geometry()
    roots, d7, lines = shell(g)
    full_roots, live, _, coordinates = g.root_data()
    chamber = g.chamber_receipt(full_roots, live, coordinates)
    ray = common.primitive(g.solve(g.SIMPLE, [1] + [0] * 7))
    common.require(
        ray in lines and ray not in {common.primitive(r) for r in roots},
        "D7 chamber ray",
    )
    a = roots[0]
    b = next(r for r in roots if g.dot(a, r) == 0)
    pencils = root_pencils(g, roots, lines, a)
    candidates = affine_candidates(pencils, lines, a, b)
    return {
        "shell": {
            "root_lines": 120,
            "d7_lines": len(d7),
            "all_lines": len(lines),
            "line_sha256": common.digest_rows(lines),
            "d7_supports": dict(
                sorted(
                    Counter(
                        str(sum(bool(g.dot(v, r)) for r in live)) for v in d7
                    ).items()
                )
            ),
            "chamber_ray_zeros": chamber["ray_zero_counts"],
            "rank_six_cap": 36,
        },
        "geometry": {
            "ordered_orthogonal_pairs": ordered_pair_orbit(g, roots, a, b),
            "root_pencil_histogram": dict(
                sorted(Counter(str(len(v)) for v in pencils.values()).items())
            ),
            "affine_candidates": len(candidates),
            "candidate_sha256": common.digest_rows(candidates),
            "fifth_endpoint": fifth_endpoint(candidates, lines, a, b),
        },
        "incidence": incidence_receipt(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    actual = result()
    if args.write:
        import json

        (common.PACKAGE / "RESULT.json").write_text(json.dumps(actual, indent=2) + "\n")
    else:
        for key, value in actual.items():
            common.check_result(value, key)
    print(
        "PASS_P112_THREE_ENDPOINTS lines=1200 candidates=360 fifth=0 root_triples>=9 conditional_caller_exclusion"
    )


if __name__ == "__main__":
    main()
