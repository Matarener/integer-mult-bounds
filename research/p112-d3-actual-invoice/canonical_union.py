#!/usr/bin/env python3
"""Independent canonical-coordinate union verifier, prepared by conorholds.

Prepared independently from the written canonical quadratic model, with
substantial OpenAI Codex assistance. Apache-2.0.
Uses only the standard library, imports no candidate modules, and writes no files.
Coordinates are little endian: q(x)=x0*x1+x2*x3+x4*x5+x6*x7.
Only 5,440 maximal section masks are retained; pairs are counted in a stream.
"""

import argparse
import json
import sys


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def q(x):
    return (x & (x >> 1) & 0x55).bit_count() & 1


def bilinear(u, v):
    # B(u,v)=sum_i (u[2i]*v[2i+1]+u[2i+1]*v[2i]).
    swapped_u = ((u & 0x55) << 1) | ((u & 0xAA) >> 1)
    return (swapped_u & v).bit_count() & 1


def affine_root_mask(roots, normals, values):
    mask = 0
    for index, x in enumerate(roots):
        if all(bilinear(v, x) == value for v, value in zip(normals, values)):
            mask |= 1 << index
    return mask


def label_rank(points):
    basis = [0] * 9
    rank = 0
    for x in points:
        label = (x << 1) | 1  # Coordinates for the label (1,x).
        while label:
            pivot = label.bit_length() - 1
            if basis[pivot]:
                label ^= basis[pivot]
            else:
                basis[pivot] = label
                rank += 1
                break
    return rank


def points_in_mask(roots, mask):
    return [x for index, x in enumerate(roots) if (mask >> index) & 1]


def validate_maximal_section(roots, a, b, syndrome, mask):
    require(bilinear(a, b) == 1, "36-root normal plane is degenerate")
    expected = (q(a) ^ 1) | ((q(b) ^ 1) << 1)
    require(syndrome == expected, "36-root section has the wrong affine coset")
    require(mask.bit_count() == 36, "maximal section does not have 36 roots")
    values = (syndrome & 1, syndrome >> 1)
    require(
        mask == affine_root_mask(roots, (a, b), values),
        "maximal mask disagrees with its explicit normal equations",
    )


def validate_sharp_fixture(roots, first, second):
    first_points = points_in_mask(roots, first)
    second_points = points_in_mask(roots, second)
    counts = (len(first_points), len(second_points))
    ranks = (label_rank(first_points), label_rank(second_points))
    overlap = (first & second).bit_count()
    union = (first | second).bit_count()
    require(counts == (36, 32), f"mixed fixture counts are {counts}")
    require(ranks == (7, 7), f"mixed fixture label ranks are {ranks}")
    require(overlap == 0, f"mixed fixture sections overlap in {overlap} roots")
    require(union == 68, f"mixed fixture union has {union} roots")
    return {
        "root_counts": list(counts),
        "label_ranks": list(ranks),
        "intersection": overlap,
        "union": union,
        "root_masks_hex": [f"{first:030x}", f"{second:030x}"],
        "root_points": [first_points, second_points],
    }


def sharp_fixture(roots, mutation):
    a, b, c = 1, 2, 4
    require((q(a), q(b), q(c)) == (0, 0, 0), "fixture normals not isotropic")
    require(bilinear(a, b) == 1, "fixture hyperbolic pair is wrong")
    require(bilinear(a, c) == bilinear(b, c) == 0, "fixture c is not orthogonal")
    first = affine_root_mask(roots, (a, b), (1, 1))
    # The mutation preserves the second count 32 and its rank seven, but
    # changes its intersection with the first section from zero to sixteen.
    second_values = (1 if mutation == "wrong-mixed-coset" else 0, 1)
    second = affine_root_mask(roots, (a, c), second_values)
    result = validate_sharp_fixture(roots, first, second)
    result["normal_equations"] = [
        {"normals": [a, b], "values": [1, 1]},
        {"normals": [a, c], "values": list(second_values)},
    ]
    return result


def checks(mutation=None):
    """Return JSON-serializable evidence, or raise VerificationError.

    mutation='wrong-mixed-coset' must be rejected by the ordinary fixture
    validator; it changes a coset without changing either root count or rank.
    """
    require(mutation in (None, "wrong-mixed-coset"), "unknown mutation")
    roots = [x for x in range(256) if q(x) == 1]
    require(len(roots) == 120, "canonical quadric does not have 120 roots")
    require(sum(1 - 2 * q(x) for x in range(256)) == 16, "ambient Gauss sum")
    for u in range(256):
        for v in range(256):
            require(q(u ^ v) == (q(u) ^ q(v) ^ bilinear(u, v)), "polar identity")
        if u:
            require(any(bilinear(u, 1 << i) for i in range(8)), "polar degeneracy")
    fixture = sharp_fixture(roots, mutation)

    plane_count = 0
    section_histogram = [0] * 65
    maximal_masks = []
    for a in range(1, 256):
        for b in range(a + 1, 256):
            # Each two-plane has exactly three nonzero points a,b,a^b;
            # take the increasing first two, so it is enumerated once.
            if b >= (a ^ b):
                continue
            plane_count += 1
            sections = [0, 0, 0, 0]
            for index, x in enumerate(roots):
                syndrome = bilinear(a, x) | (bilinear(b, x) << 1)
                sections[syndrome] |= 1 << index
            counts = [mask.bit_count() for mask in sections]
            expected = [28, 28, 28, 36] if bilinear(a, b) else [24, 32, 32, 32]
            require(sorted(counts) == expected, f"two-plane spectrum at {a},{b}")
            for syndrome, mask in enumerate(sections):
                section_histogram[mask.bit_count()] += 1
                if mask.bit_count() == 36:
                    validate_maximal_section(roots, a, b, syndrome, mask)
                    maximal_masks.append(mask)

    spectrum = {n: count for n, count in enumerate(section_histogram) if count}
    require(plane_count == 10795, f"normal two-plane count {plane_count}")
    require(sum(spectrum.values()) == 43180, "affine six-section count")
    require(spectrum == {24: 5355, 28: 16320, 32: 16065, 36: 5440}, "root spectrum")
    require(len(maximal_masks) == 5440, "maximal section count")
    require(len(set(maximal_masks)) == 5440, "duplicate maximal root masks")

    intersections = [0] * 37
    for i, left in enumerate(maximal_masks):
        for j in range(i + 1, len(maximal_masks)):
            intersections[(left & maximal_masks[j]).bit_count()] += 1
    pair_histogram = {n: count for n, count in enumerate(intersections) if count}
    pair_count = sum(pair_histogram.values())
    require(pair_count == 14794080, f"unordered distinct maximal pair count {pair_count}")
    require(
        pair_histogram == {6: 913920, 10: 8225280, 12: 5140800, 20: 514080},
        f"maximal pair intersection histogram {pair_histogram}",
    )
    maximal_union = 72 - min(pair_histogram)
    require(maximal_union == 66, "maximal pair union bound")
    # Every other pair has a member of size <=32 and the other size <=36.
    universal_union = max(maximal_union, 32 + max(spectrum))
    require(universal_union == fixture["union"] == 68, "sharp universal union bound")
    return {
        "status": "pass",
        "model": "F2^8, q=x0*x1+x2*x3+x4*x5+x6*x7",
        "root_order": roots,
        "normal_two_planes": plane_count,
        "affine_six_sections": sum(spectrum.values()),
        "section_root_histogram": spectrum,
        "maximal_sections": len(maximal_masks),
        "maximal_distinct_pairs": pair_count,
        "maximal_pair_intersection_histogram": pair_histogram,
        "maximal_pair_union_bound": maximal_union,
        "universal_union_bound": universal_union,
        "sharp_fixture": fixture,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutate", choices=["wrong-mixed-coset"])
    args = parser.parse_args()
    try:
        result = checks(mutation=args.mutate)
    except VerificationError as error:
        print(json.dumps({"status": "fail", "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
