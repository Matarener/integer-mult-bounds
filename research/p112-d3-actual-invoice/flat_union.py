"""Exact finite double-seven union check.

Research by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
Reuses frame_pair_geometry.py's E8/P112 model and predecessor credits;
this file does not execute the pinned source geometry. canonical_union.py
provides the independent canonical-coordinate implementation.

Expected domain: 10,795 binary two-planes, of which 5,440 are nondegenerate.
Their unique 36-root sections give 14,794,080 unordered distinct section pairs.
Optional census: 43,180 affine six-sections, with full-root counts
{24:5355, 28:16320, 32:16065, 36:5440}. The 255 rank-seven spaces contained
in tau=0 have empty leading-one section, bringing the nine-bit total to 43,435.

Only Python's standard library is required. The exhaustive pair
loop retains 5,440 masks, rather than materializing its 14.8 million pairs.
This checker corroborates finite binary geometry, not arbitrary actual bases
or the handwritten characteristic-zero invoice assembly.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from types import ModuleType


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_model(engine_path, source_geometry):
    """Reuse the selected engine's root reconstruction and literal AST binding."""
    engine = ModuleType("flat_union_geometry")
    engine.__file__ = str(engine_path)
    exec(compile(engine_path.read_bytes(), str(engine_path), "exec"), engine.__dict__)
    require(callable(getattr(engine, "model", None)), "geometry engine lacks model()")
    require(callable(getattr(engine, "binary_rank", None)), "geometry engine lacks binary_rank()")
    roots, frame, frame_ids, live_ids, labels, pairings = engine.model(source_geometry)
    require(len(roots) == len(labels) == len(set(labels)) == 120, "120 distinct labeled roots")
    require(len(frame) == len(frame_ids) == 8 and len(live_ids) == 112,
            "frame/live inventory")
    require(set(frame_ids).isdisjoint(live_ids)
            and set(frame_ids) | set(live_ids) == set(range(120)), "frame/live partition")
    require(all(type(label) is int and 0 < label < 512 and label & 1 for label in labels),
            "literal leading-one nine-bit labels")
    residues = tuple(label >> 1 for label in labels)
    require(0 not in residues and len(set(residues)) == 120, "distinct nonzero root residues")

    # Full E8 root residues are exactly q=1; every remaining residue has q=0.
    root_residues = set(residues)
    q = bytes(int(x in root_residues) for x in range(256))
    require(sum(1 - 2 * value for value in q) == 16, "ambient plus-type Gauss sign")
    polar = tuple(sum((q[x ^ y] ^ q[x] ^ q[y]) << y for y in range(256))
                  for x in range(256))
    linear_rows = [0] * 256
    for x in range(1, 256):
        bit = x & -x
        linear_rows[x] = linear_rows[x ^ bit] ^ polar[bit]
        require(polar[x] == linear_rows[x], "polarization is not binary bilinear")
        require(not ((polar[x] >> x) & 1), "polarization is not alternating")
    require(engine.binary_rank(polar[1 << i] for i in range(8)) == 8,
            "degenerate ambient polarity")
    for i, left in enumerate(residues):
        for j, right in enumerate(residues):
            require(pairings[i][j] % 4 == 0, "root polar normalization")
            require(((polar[left] >> right) & 1) == ((pairings[i][j] // 4) & 1),
                    "quadratic/root polar binding")

    frame_residues = {residues[i] for i in frame_ids}
    anchor = min(frame_residues)
    translated = {value ^ anchor for value in frame_residues}
    require(len(translated) == 8 and engine.binary_rank(translated) == 3,
            "frame residues are not an affine three-flat")
    return roots, tuple(frame_ids), residues, q, polar


def planes():
    """Each two-plane once: its three nonzero vectors satisfy a<b<a^b."""
    for a in range(1, 256):
        for b in range(a + 1, 256):
            c = a ^ b
            if b < c:
                yield a, b, c


def enumerate_maximal_sections(residues, q, polar, frame_ids, all_sections, mutation=None):
    universe = (1 << 120) - 1
    ambient = (1 << 256) - 1
    frame_mask = sum(1 << i for i in frame_ids)
    root_points = sum(1 << residue for residue in residues)
    ones = tuple(sum(1 << i for i, residue in enumerate(residues)
                     if (polar[a] >> residue) & 1) for a in range(256))
    section_masks, normal_masks = [], []
    total_planes = 0
    full_histogram = Counter()
    frame_intersection_histogram = Counter()
    maximal_from_census = set()
    max_corrected_live = 0
    digest = sha256()

    for a, b, c in planes():
        total_planes += 1
        nondegenerate = (polar[a] >> b) & 1
        if nondegenerate:
            # Unique maximal affine coset: B(x,v)=q(v)+1 on all nonzero v in E.
            target_a, target_b, target_c = q[a] ^ 1, q[b] ^ 1, q[c] ^ 1
            if mutation == "wrong-normal-coset" and not section_masks:
                target_a ^= 1
            point_mask = (polar[a] if target_a else ambient ^ polar[a])
            point_mask &= polar[b] if target_b else ambient ^ polar[b]
            require(point_mask.bit_count() == 64, "affine six-section point count")
            c_half = polar[c] if target_c else ambient ^ polar[c]
            require(not (point_mask & (ambient ^ c_half)), "third normal equation fails")
            require((point_mask & root_points).bit_count() == 36,
                    "unique normal-plane section does not have 36 roots")
            section = (ones[a] if target_a else universe ^ ones[a])
            section &= ones[b] if target_b else universe ^ ones[b]
            require(section.bit_count() == 36, "120-root mask does not have 36 roots")
            section_masks.append(section)
            normal_masks.append((1 << a) | (1 << b) | (1 << c))
            digest.update(bytes((a, b, c)))
            digest.update(section.to_bytes(15, "little"))

        if all_sections:
            for target_a in (0, 1):
                left = ones[a] if target_a else universe ^ ones[a]
                for target_b in (0, 1):
                    section = left & (ones[b] if target_b else universe ^ ones[b])
                    full_count = section.bit_count()
                    full_histogram[full_count] += 1
                    if full_count == 36:
                        maximal_from_census.add(section)
                    frame_count = (section & frame_mask).bit_count()
                    frame_intersection_histogram[frame_count] += 1
                    require(frame_count in (0, 2, 4, 8), "invalid affine frame intersection")
                    if frame_count:
                        live_count = full_count - frame_count
                        require(live_count <= 34, "corrected seven live capacity exceeds 34")
                        max_corrected_live = max(max_corrected_live, live_count)

    require(total_planes == 10795, "incomplete binary two-plane domain")
    require(len(section_masks) == len(set(section_masks)) == 5440,
            "nondegenerate planes / distinct maximal sections differ from 5440")
    result = {"normal_two_planes": total_planes, "nondegenerate_two_planes": len(section_masks),
              "distinct_36_root_sections": len(set(section_masks)),
              "normal_section_records_sha256": digest.hexdigest()}
    if all_sections:
        expected = {24: 5355, 28: 16320, 32: 16065, 36: 5440}
        require(dict(full_histogram) == expected and sum(full_histogram.values()) == 43180,
                "affine six-section cardinality census differs")
        require(maximal_from_census == set(section_masks), "maximal section census incomplete")
        require(max_corrected_live == 34, "corrected-seven live capacity is not sharp at 34")
        result["all_sections"] = {
            "nonempty_affine_six_sections": 43180,
            "full_root_histogram": {str(k): v for k, v in sorted(full_histogram.items())},
            "tau_zero_rank_seven_spaces": 255,
            "all_nine_bit_rank_seven_spaces": 43180 + 255,
            "frame_intersection_histogram": {
                str(k): v for k, v in sorted(frame_intersection_histogram.items())},
            "maximum_corrected_live_support": max_corrected_live,
        }
    return section_masks, normal_masks, result


def check_pairs(section_masks, normal_masks, by_normal_intersection):
    # Histogram accumulation also counts the executed comparisons, rather than
    # merely reporting the combinatorial number of intended comparisons.
    histogram = [0] * 37
    by_dimension = [[0] * 37 for _ in range(2)] if by_normal_intersection else None
    minimum_intersection = 120
    minimum_witness = None
    for i, left in enumerate(section_masks):
        normal_left = normal_masks[i]
        for j in range(i):
            intersection = (left & section_masks[j]).bit_count()
            if intersection < 4:
                raise ValueError(f"36-root section intersection below four: {i},{j},{intersection}")
            histogram[intersection] += 1
            if intersection < minimum_intersection:
                minimum_intersection = intersection
                minimum_witness = (j, i)
            if by_dimension is not None:
                dimension = int(bool(normal_left & normal_masks[j]))
                if dimension and intersection < 12:
                    raise ValueError(f"shared-normal intersection below twelve: {i},{j},{intersection}")
                by_dimension[dimension][intersection] += 1

    pair_count = sum(histogram)
    require(pair_count == 14794080, "incomplete unordered maximal-section pair domain")
    require({k: count for k, count in enumerate(histogram) if count}
            == {6: 913920, 10: 8225280, 12: 5140800, 20: 514080},
            "maximal-section intersection spectrum differs from the stated finite inventory")
    require(minimum_intersection >= 4 and 72 - minimum_intersection <= 68,
            "intersection / union bounds exceed the written 4 / 68 estimates")
    result = {"unordered_distinct_section_pairs": pair_count,
              "minimum_full_root_intersection": minimum_intersection,
              "maximum_union_of_36_root_sections": 72 - minimum_intersection,
              "minimum_intersection_witness_indices": minimum_witness,
              "intersection_histogram": {str(k): v for k, v in enumerate(histogram) if v}}
    if by_dimension is not None:
        require(sum(map(sum, by_dimension)) == pair_count, "normal-dimension histogram incomplete")
        # Each nonzero vector belongs to 64 nondegenerate two-planes. Thus
        # each such plane meets 3*(64-1)=189 others in a line, with no overlap.
        require([sum(row) for row in by_dimension] == [14280000, 514080],
                "normal-intersection dimension domain differs")
        result["normal_intersection_dimension_histograms"] = {
            str(dimension): {str(k): v for k, v in enumerate(row) if v}
            for dimension, row in enumerate(by_dimension)}
    return result


def mixed_sharp_witness(residues, q, polar, frame_ids):
    """Materialize the analytic disjoint 36/32 construction in this E8 model."""
    a = next(x for x in range(1, 256) if q[x] == 0)
    b = next(x for x in range(1, 256) if q[x] == 0 and (polar[a] >> x) & 1)
    c = next(x for x in range(1, 256) if q[x] == 0
             and not ((polar[a] >> x) & 1) and not ((polar[b] >> x) & 1))
    require(len({0, a, b, a ^ b, c}) == 5, "mixed witness normals are dependent")
    maximal = sum(1 << i for i, x in enumerate(residues)
                  if ((polar[a] >> x) & 1) and ((polar[b] >> x) & 1))
    other = sum(1 << i for i, x in enumerate(residues)
                if not ((polar[a] >> x) & 1) and ((polar[c] >> x) & 1))
    require(maximal.bit_count() == 36 and other.bit_count() == 32,
            "mixed witness does not have the analytic 36/32 cardinalities")
    require(not (maximal & other) and (maximal | other).bit_count() == 68,
            "mixed witness does not attain the full-root union bound")
    frame_mask = sum(1 << i for i in frame_ids)
    return {"normal_vectors": {"a": a, "b": b, "c": c},
            "normal_targets": [[1, 1], [0, 1]],
            "normal_pairs": [[a, b], [a, c]],
            "full_root_counts": [maximal.bit_count(), other.bit_count()],
            "intersection_full_roots": (maximal & other).bit_count(),
            "union_full_roots": (maximal | other).bit_count(),
            "union_excluded_frame_roots": ((maximal | other) & frame_mask).bit_count(),
            "root_masks_hex": [f"{maximal:030x}", f"{other:030x}"]}


def checks(source_geometry, geometry_engine, all_sections=False, by_normal_intersection=False,
           mutation=None):
    roots, frame_ids, residues, q, polar = load_model(geometry_engine, source_geometry)
    sections, normals, census = enumerate_maximal_sections(
        residues, q, polar, frame_ids, all_sections, mutation)
    pairs = check_pairs(sections, normals, by_normal_intersection)
    sharp = mixed_sharp_witness(residues, q, polar, frame_ids)
    universal_bound = None
    inference = None
    if all_sections:
        sizes = sorted(int(count) for count in census["all_sections"]["full_root_histogram"])
        require(len(sizes) >= 2, "section spectrum lacks the mixed-size case")
        mixed_upper = sizes[-1] + sizes[-2]
        maximal_upper = pairs["maximum_union_of_36_root_sections"]
        universal_bound = max(mixed_upper, maximal_upper)
        require(universal_bound == sharp["union_full_roots"],
                "derived universal bound and materialized sharp witness disagree")
        inference = {"largest_section": sizes[-1], "largest_nonmaximal_section": sizes[-2],
                     "mixed_pair_upper_bound": mixed_upper,
                     "maximal_pair_upper_bound": maximal_upper,
                     "derived_upper_bound": universal_bound,
                     "materialized_lower_bound": sharp["union_full_roots"]}
    return {"status": "pass", "scope": "finite E8 binary-flat geometry only",
            "source_geometry_sha256": sha256(source_geometry.read_bytes()).hexdigest(),
            "geometry_engine_sha256": sha256(geometry_engine.read_bytes()).hexdigest(),
            "root_residue_order_sha256": sha256(bytes(residues)).hexdigest(),
            "root_lines": len(roots), "frame_lines": len(frame_ids),
            "quadratic_gauss_sum": 16, "frame_affine_dimension": 3,
            "universal_double_seven_full_union_bound": universal_bound,
            "universal_union_inference": inference,
            "universal_bound_coverage": (
                "all rank-at-most-seven flats via complete section census and all maximal pairs"
                if all_sections else "maximal section pairs only; full census was not requested"),
            "census": census, "pairs": pairs,
            "mixed_36_32_sharp_witness": sharp}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-geometry", type=Path, required=True)
    parser.add_argument("--geometry-engine", type=Path, required=True,
                        help="existing frame_pair_geometry.py root model; canonical_union.py is independent")
    parser.add_argument("--all-sections", action="store_true")
    parser.add_argument("--normal-intersection-histogram", action="store_true")
    args = parser.parse_args()
    print(json.dumps(checks(args.source_geometry, args.geometry_engine, args.all_sections,
                            args.normal_intersection_histogram), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
