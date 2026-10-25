#!/usr/bin/env python3
"""Separate lattice/RREF/pair-join corroboration; imports no primary routines.

Same-session computational corroboration, not independent human review.
Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
"""

import ast
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_MANIFEST_SHA = "9312885bb9c46b31a199283937b4cf0aec74252f6cd6877f6ef6e27f84f979fb"


def check(ok, message):
    if not ok:
        raise ValueError(message)


def authenticated_inputs():
    raw = (HERE / "SOURCES.json").read_bytes()
    check(hashlib.sha256(raw).hexdigest() == SOURCE_MANIFEST_SHA, "manifest pin")
    result = {}
    for row in json.loads(raw)["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        check(not path.is_symlink() and path.resolve().is_relative_to(ROOT), "input path")
        data = path.read_bytes()
        check(len(data) <= 2_000_000, "input byte bound")
        check(hashlib.sha256(data).hexdigest() == row["sha256"], "input digest")
        result[row["path"]] = data
    return result


def inverse(matrix):
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(8)]
            for i, row in enumerate(matrix)]
    for j in range(8):
        k = next(i for i in range(j, 8) if rows[i][j])
        rows[j], rows[k] = rows[k], rows[j]
        scalar = rows[j][j]
        rows[j] = [x / scalar for x in rows[j]]
        for i in range(8):
            if i != j:
                factor = rows[i][j]
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[j])]
    return [row[8:] for row in rows]


def reconstruct(inputs):
    prefix = "research/p112-common-deletion-slice/"
    parsed = ast.parse(inputs[prefix + "geometry.py"])
    simple = next(ast.literal_eval(n.value) for n in parsed.body
                  if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "SIMPLE" for t in n.targets))
    # Enumerate the doubled E8 lattice shell, independently of the source generator.
    roots = []
    for row in product(range(-2, 3), repeat=8):
        if sum(x * x for x in row) != 8 or sum(row) % 4:
            continue
        if len({x % 2 for x in row}) != 1:
            continue
        if next(x for x in row if x) > 0:
            roots.append(row)
    roots.sort()
    check(len(roots) == 120, "lattice root shell")
    inv = inverse([[simple[j][i] for j in range(8)] for i in range(8)])
    coords = [tuple(sum(inv[i][j] * r[j] for j in range(8)) for i in range(8)) for r in roots]
    check(all(x.denominator == 1 for c in coords for x in c), "integral coordinates")
    check(all(min(c) >= 0 or max(c) <= 0 for c in coords), "simple-root signs")
    frame = {tuple(r) for r in json.loads(inputs[prefix + "FIXTURE.json"])["omitted_frame"]}
    live = [r for r in roots if r not in frame]
    labels = [256 + sum((int(x) % 2) * 2 ** i for i, x in enumerate(c))
              for r, c in zip(roots, coords) if r not in frame]
    check(len(live) == 112 and len(set(labels)) == 112, "live model")
    table = inputs["research/one-sided-six-multisets/data/data.txt"].decode().splitlines()
    check([tuple(map(int, row.split())) for row in table[2:114]] == live,
          "canonical caller root rows")
    check(list(map(int, table[0].split())) == [1 + 2 * (label - 256) for label in labels],
          "canonical caller label bits")
    return roots, live, labels, coords


def rref_annihilators():
    rows = []
    for p, q in combinations(range(9), 2):
        free = [(0, j) for j in range(p + 1, 9) if j != q]
        free += [(1, j) for j in range(q + 1, 9)]
        for bits in product((0, 1), repeat=len(free)):
            pair = [1 << p, 1 << q]
            for (row, j), bit in zip(free, bits):
                pair[row] += bit << j
            rows.append(tuple(pair))
    check(len(rows) == len(set(rows)) == 43_435, "RREF domain")
    return rows


def flat_check(roots, live, labels):
    chars = [sum((1 << i) for i, label in enumerate(labels)
                 if bin(a & label).count("1") % 2) for a in range(512)]
    flats = [((1 << 112) - 1) - (chars[a] | chars[b]) for a, b in rref_annihilators()]
    off = [sum(1 << i for i, r in enumerate(live) if sum(a * b for a, b in zip(r, h)))
           for h in roots]
    counts = Counter(mask.bit_count() for mask in flats)
    maxima = [max((mask & support).bit_count() for mask in flats) for support in off]
    check(set(maxima) == {32} and max(counts) == 36, "independent flat capacities")
    cuts = Counter((mask.bit_count(), m, mask.bit_count() - m) for mask, m in zip(off, maxima))
    return off, {"seven_flats": len(flats), "global_seven_flat_cap": max(counts),
                 "flat_size_histogram": {str(k): counts[k] for k in sorted(counts)},
                 "root_flat_tests": len(roots) * len(flats),
                 "root_cut_minima": {",".join(map(str, k)): cuts[k] for k in sorted(cuts)}}


def pair_join_check(off):
    # Unique ordered split a<b<c<d, grouped by the second index instead of 4-subsets.
    histogram = Counter()
    for b in range(1, 118):
        left = [off[a] & off[b] for a in range(b)]
        right = [off[c] & off[d] for c in range(b + 1, 119) for d in range(c + 1, 120)]
        for first in left:
            for second in right:
                histogram[(first & second).bit_count()] += 1
    check(sum(histogram.values()) == 8_214_570 and max(histogram) == 14, "pair-join coverage")
    return {str(k): histogram[k] for k in sorted(histogram)}


def rank2(values):
    rows = list(values)
    pivot = 0
    for j in range(9):
        choice = next((i for i in range(pivot, len(rows)) if rows[i] & (1 << j)), None)
        if choice is None:
            continue
        rows[pivot], rows[choice] = rows[choice], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i] & (1 << j):
                rows[i] ^= rows[pivot]
        pivot += 1
    return pivot


def main():
    inputs = authenticated_inputs()
    roots, live, labels, coords = reconstruct(inputs)
    receipt = json.loads((HERE / "RESULT.json").read_bytes())
    sizes = []
    for removed in range(8):
        sizes.append(sum(c[removed] == 0 for c in coords))
    check(sizes == receipt["chamber"]["seven_face_counts"], "independent chamber faces")
    lower = max(sum(all(c[j] == 0 for j in range(8) if not (mask >> j & 1)) for c in coords)
                for mask in range(256) if mask.bit_count() <= 6)
    check(lower == 36, "independent lower-dimensional chamber cap")
    off, flat_summary = flat_check(roots, live, labels)
    check(flat_summary == receipt["flat_facts"], "independent flat summary")
    check(pair_join_check(off) == receipt["fourfold"]["histogram"], "independent fourfold histogram")
    fixture = receipt["positive_fixture"]
    common = set(fixture["common_cut_indices"])
    check(len(common) == 22, "fixture common budget")
    for h in fixture["directions"]:
        residual = [label for i, (r, label) in enumerate(zip(live, labels))
                    if i not in common and sum(a * b for a, b in zip(r, h))]
        check(rank2(residual) == 7, "independent positive residual")
    check(4 * 21 - 3 * 23 == 15 > 14 and 2 + 4 + 8 + 8 == 22 < 53, "proof arithmetic")
    prior = json.loads(inputs["research/p112-b6-t4-original-covers/RESULT.json"])
    rows = [tuple(r["weights"]) for r in prior["rows"] if not r["covered"]]
    used = {tuple([2, 2, 2] + [7] * 7), tuple([2, 5] + [6] * 8), tuple([2, 3, 4, 4] + [7] * 6)}
    check(set(rows) - used == {tuple([4, 5, 5, 5] + [6] * 6)}, "independent caller partition")
    check(sum(r["covered"] for r in prior["rows"]) + len(used) == 68, "conditional inventory")
    print("PASS_COMMON_CUT23_INDEPENDENT lattice/RREF/pair-join; 8214570 quadruples; conditional68/69")


if __name__ == "__main__":
    main()
