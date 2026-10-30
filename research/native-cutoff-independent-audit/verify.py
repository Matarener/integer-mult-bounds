#!/usr/bin/env python3
"""Independent finite checks for the scoped PR5369 proof audit.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable or arithmetic module is imported. All arithmetic is exact.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = "research/native-tensor-cutoff/PROOF.md"
SOURCE_SHA = "b2d31ea52b652f43cc8576affde6092a884d2832820221a43933e7e27dc07041"
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_check():
    require(sha256((ROOT / SOURCE).read_bytes()).hexdigest() == SOURCE_SHA,
            "source proof hash mismatch")


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def spanning(points, n):
    return bool(points) and binary_rank([x ^ points[0] for x in points]) == n


def phase(x, c, linear, pairs):
    answer = c
    for j, a in enumerate(linear):
        answer += a * ((x >> j) & 1)
    for j, k, b in pairs:
        answer += 2 * b * ((x >> j) & 1) * ((x >> k) & 1)
    return answer % 4


def literal_character(points, n):
    # Evaluate actual phase generators point by point, without the count formula.
    generators = [(1, [0] * n, [])]
    for j in range(n):
        linear = [0] * n
        linear[j] = 1
        generators.append((0, linear, []))
    for j in range(n):
        for k in range(j + 1, n):
            generators.append((0, [0] * n, [(j, k, 1)]))
    values = [sum(phase(x, *g) for x in points) % 4 for g in generators]
    require(all(v % 2 == 0 for v in values[n + 1:]), "pair phase parity")
    return tuple(values[:n + 1] + [v // 2 for v in values[n + 1:]])


def count_character(counts, n):
    r = sum(counts) % 4
    u = [sum(counts[x] for x in range(1 << n) if x & (1 << j)) % 4
         for j in range(n)]
    v = [sum(counts[x] for x in range(1 << n)
             if x & (1 << j) and x & (1 << k)) % 2
         for j in range(n) for k in range(j + 1, n)]
    return (r, *u, *v)


def affine_maps(n):
    result = []
    for rows in product(range(1 << n), repeat=n):
        if binary_rank(rows) != n:
            continue
        for offset in range(1 << n):
            result.append(tuple(offset ^ sum(((row & x).bit_count() % 2) << j
                                             for j, row in enumerate(rows))
                                for x in range(1 << n)))
    return result


def character_census():
    reports = []
    for n in (1, 2, 3):
        size = 1 << n
        support_points = {mask: tuple(x for x in range(size) if mask & (1 << x))
                          for mask in range(1 << size)}
        full = {mask for mask, points in support_points.items() if spanning(points, n)}
        minima, witnesses = {}, {}
        visited = 0
        # Reducing each positive multiplicity to 1+((m-1) mod 4) preserves
        # character and support and cannot increase length. This finite domain
        # therefore contains a shortest spanning tuple for EACH character.
        for counts in product(range(5), repeat=size):
            visited += 1
            mask = sum(1 << x for x, count in enumerate(counts) if count)
            if mask not in full:
                continue
            key = count_character(counts, n)
            length = sum(counts)
            if key not in minima or length < minima[key]:
                minima[key], witnesses[key] = length, counts
        expected_keys = set(product(*([range(4)] * (n + 1)
                                     + [range(2)] * (n * (n - 1) // 2))))
        require(set(minima) == expected_keys, "missing phase character")
        literal_probes = 0
        for key, counts in witnesses.items():
            points = tuple(x for x, count in enumerate(counts) for _ in range(count))
            require(literal_character(points, n) == key, "literal phase mismatch")
            F = 2 * n + 4
            f = F + (key[0] - F) % 4
            require(len(points) <= f, "published four-width bound failed")
            padded = points + (0,) * (f - len(points))
            require(spanning(padded, n) and literal_character(padded, n) == key,
                    "padding changed character or span")
            literal_probes += 2 * (1 + n + n * (n - 1) // 2)
        maps = affine_maps(n)
        require(len(maps) == {1: 2, 2: 24, 3: 1344}[n], "affine group inventory")
        # Test isolation on every full-span support, not only a canonical basis.
        for mask in full:
            points = support_points[mask]
            require(len({tuple(mapping[x] for x in points) for mapping in maps}) == len(maps),
                    "affine maps collide on a spanning support")
        table = [[list(key), minima[key]] for key in sorted(minima)]
        reports.append({
            "axes": n, "multisets": visited, "characters": len(minima),
            "full_span_supports": len(full), "affine_maps": len(maps),
            "affine_restrictions": len(full) * len(maps),
            "literal_generator_probes": literal_probes,
            "largest_minimum_by_residue": [max(length for key, length in minima.items()
                                               if key[0] == r) for r in range(4)],
            "minimum_length_histogram": dict(sorted(Counter(minima.values()).items())),
            "minima_sha256": sha256(json.dumps(table, separators=(",", ":")).encode()).hexdigest(),
        })
    return reports


def add(z, w):
    return (z[0] + w[0], z[1] + w[1])


def mul(z, w):
    return (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])


def divide(z, w):
    den = w[0] * w[0] + w[1] * w[1]
    return (Fraction(z[0] * w[0] + z[1] * w[1], den),
            Fraction(z[1] * w[0] - z[0] * w[1], den))


def gaussian_rank(rows):
    pivots = {}
    for raw in rows:
        row = list(raw)
        for col in range(len(row)):
            if row[col] == (0, 0):
                continue
            if col not in pivots:
                pivot = row[col]
                pivots[col] = [divide(value, pivot) for value in row]
                break
            factor = row[col]
            row = [add(value, mul((-factor[0], -factor[1]), old))
                   for value, old in zip(row, pivots[col])]
    return len(pivots)


ONE_AXIS_GROUP = tuple(product(range(2), range(4), range(4)))  # t,c,a


def operator_rows(f):
    require(f >= 1, "positive width required")
    rows = []
    # Literal entries of all operators; only identically zero rows are omitted.
    # No Hamming-weight or theoretical rank formula is used here.
    for bits in product(range(2), repeat=f):
        outputs = {}
        for index, (t, c, a) in enumerate(ONE_AXIS_GROUP):
            y = tuple(x ^ t for x in bits)
            exponent = sum(phase(x, c, [a], []) for x in bits) % 4
            outputs.setdefault(y, [(0, 0)] * len(ONE_AXIS_GROUP))[index] = UNITS[exponent]
        rows.extend(tuple(row) for row in outputs.values())
    return rows


def dot(row, coefficients):
    answer = (0, 0)
    for x, y in zip(row, coefficients):
        answer = add(answer, mul(x, y))
    return answer


def one_axis():
    ranks, raw_counts, distinct = [], [], {}
    for f in range(1, 10):
        rows = operator_rows(f)
        raw_counts.append(len(rows))
        distinct[f] = sorted(set(rows))
        rank = gaussian_rank(distinct[f])
        require(rank == 2 * min(f + 1, 4), "one-axis rank formula failed")
        ranks.append(rank)
    windows = {}
    for first, expected in ((1, 26), (2, 30), (3, 32), (6, 32)):
        rows = [row for f in range(first, first + 4) for row in distinct[f]]
        windows[str(first)] = gaussian_rank(rows)
        require(windows[str(first)] == expected, "one-axis window rank failed")
    # C_2 times the weight-three projector (unnormalized): missed by widths 2..5.
    trap = [UNITS[(-2 * c - 3 * a) % 4] if t == 0 else (0, 0)
            for t, c, a in ONE_AXIS_GROUP]
    require(all(dot(row, trap) == (0, 0) for f in range(1, 6) for row in distinct[f]),
            "sharpness trap did not vanish")
    require(any(dot(row, trap) == (16, 0) for row in distinct[6]),
            "sharpness trap missing width-six witness")
    # Each central residue is necessary, even at large widths.
    for r in range(4):
        projector = [UNITS[(-r * c) % 4] if t == 0 and a == 0 else (0, 0)
                     for t, c, a in ONE_AXIS_GROUP]
        for f in range(3, 7):
            values = {dot(row, projector) for row in distinct[f]}
            require(((4, 0) in values) == (f % 4 == r), "central residue control failed")
            if f % 4 != r:
                require(values == {(0, 0)}, "central projector leaked into another residue")
    # A DIFFERENT residual at each f can vanish despite nonzero coefficients.
    for f in range(3, 7):
        residual = [(0, 0)] * 32
        residual[ONE_AXIS_GROUP.index((0, 1, 0))] = (1, 0)
        residual[ONE_AXIS_GROUP.index((0, 0, 0))] = tuple(-x for x in UNITS[f % 4])
        require(any(z != (0, 0) for z in residual)
                and all(dot(row, residual) == (0, 0) for row in distinct[f]),
                "width-dependent-program control failed")
    return {"group_order": 32, "widths": list(range(1, 10)), "ranks": ranks,
            "literal_matrix_entry_rows": sum(raw_counts), "window_ranks_by_first_width": windows,
            "earliest_complete_consecutive_window": [3, 4, 5, 6],
            "width_2_to_5_trap_width_6_entry": [16, 0],
            "least_uniform_stabilization_threshold": 3}


def hypothesis_controls():
    require(literal_character((1, 1), 1) == (2, 2), "mod-four repair control")
    X, Y = (0, 3, 0, 1, 2), (1, 2, 0, 1, 2)
    left, right = literal_character(X, 2), literal_character(Y, 2)
    require(spanning(X, 2) and spanning(Y, 2), "pair control span")
    require(left[:3] == right[:3] and left[3] != right[3], "pair statistic control")
    identity, shear = (0, 1, 2, 3), (0, 1, 3, 2)
    require(identity[:2] == shear[:2] and identity != shear, "affine span control")
    require(literal_character((0, 1), 1) != literal_character((0, 1, 0), 1),
            "constant phase control")
    require(sum(phase(x, 1, [0], []) for x in (0, 1)) % 4 == 2,
            "tensor constant must be multiplied by width")
    return {"mod_four_not_parity": True, "pair_statistic_not_marginals": True,
            "nonspanning_affine_collision": True, "constant_character_required": True,
            "tensor_constant_scaled_by_width": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--section", choices=("all", "characters", "one-axis", "controls"), default="all")
    args = parser.parse_args()
    source_check()
    status = ("PASS_NATIVE_CUTOFF_INDEPENDENT_AUDIT" if args.section == "all"
              else "PASS_NATIVE_CUTOFF_AUDIT_SECTION")
    report = {"status": status, "section": args.section,
              "proof_sha256": SOURCE_SHA, "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}
    if args.section in ("all", "characters"):
        report["character_census"] = character_census()
    if args.section in ("all", "one-axis"):
        report["one_axis"] = one_axis()
    if args.section in ("all", "controls"):
        report["hypothesis_controls"] = hypothesis_controls()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
