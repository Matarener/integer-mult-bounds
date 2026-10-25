#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Sharp F2 pairing-rank cap of the PR717 E8 label alphabet, screened on the selected template.

Standard library only. Rejection controls raise through require(); they stay active under -O.
"""
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CEILING_PATH = ROOT / "research/complex-local-word-ceiling/ceiling.py"
RESULT_PATH = ROOT / "research/complex-local-word-ceiling/RESULT.json"


def require(ok, why):
    if not ok:
        raise SystemExit("FAIL: " + why)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def inner(x, y):
    value = dot(x, y)
    require(value % 4 == 0, "doubled E8 inner product is not divisible by 4")
    return value // 4


def neg(v):
    return tuple(-a for a in v)


def e8_roots():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                vector = [0] * 8
                vector[i], vector[j] = 2 * si, 2 * sj
                roots.append(tuple(vector))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    return roots


def f2_rank(rows):
    basis = {}
    rank = 0
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def row_basis(rows):
    basis = {}
    order = []
    for index, value in enumerate(rows):
        reduced = value
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot in basis:
                reduced ^= basis[pivot]
            else:
                basis[pivot] = reduced
                order.append(index)
                break
    return order


def load_ceiling():
    spec = importlib.util.spec_from_file_location("pinned_ceiling", CEILING_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    roots = e8_roots()
    require(len(roots) == 240, "E8 root count")
    lines = []
    seen = set()
    for root in roots:
        key = root if root > neg(root) else neg(root)
        if key not in seen:
            seen.add(key)
            lines.append(root)
    count = len(lines)
    require(count == 120, "E8 line count")
    products = [[inner(lines[i], lines[j]) for j in range(count)] for i in range(count)]
    require(all(products[i][i] == 2 for i in range(count)), "root-line norm")
    off = {products[i][j] for i in range(count) for j in range(count) if i != j}
    require(off == {-1, 0, 1}, "off-diagonal inner products")
    rows = [
        sum(((products[i][j] + 1) & 1) << j for j in range(count))
        for i in range(count)
    ]
    require(len(set(rows)) == 120, "pairing rows are not distinct")
    basis = row_basis(rows)
    require(len(basis) == 9, "label pairing rank is not 9")
    pivots = {}
    for index in basis:
        reduced = rows[index]
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot in pivots:
                reduced ^= pivots[pivot]
            else:
                pivots[pivot] = reduced
                break
    for row in rows:
        reduced = row
        while reduced:
            pivot = reduced.bit_length() - 1
            require(pivot in pivots, "a pairing row escapes the 9-dimensional row space")
            reduced ^= pivots[pivot]
        require(reduced == 0, "row reduction did not close")
    full_columns = (1 << count) - 1
    witness = [rows[index] & full_columns for index in basis]
    require(f2_rank(witness) == 9, "basis supports do not attain pairing rank 9")

    # The rank routine can see rank 10. The real pairing cannot.
    extended = list(witness)
    extended.append(1 << count)
    require(f2_rank(extended) == 10, "rank routine missed an extended independent row")
    require(f2_rank(rows) == 9, "full pairing rank drifted from the basis count")

    frame = []
    for axis in range(4):
        for sign in (1, -1):
            vector = [0] * 8
            vector[2 * axis], vector[2 * axis + 1] = 2, 2 * sign
            frame.append(lines.index(tuple(vector)))
    require(len(frame) == 8, "coordinate frame size")
    require(
        all(products[a][b] == 0 for a in frame for b in frame if a != b),
        "coordinate frame is not an orthogonal 8-line set",
    )

    record = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    model = record["model"]
    selected = record["selected"]
    require(model["m"] == 73 and model["stages"] == 9, "template width or stage count")
    require(model["ports"] == 112 and model["pairs"] == 4, "port template")
    require(model["centre_per_call"] == 64 and model["idle_rank_cap"] == 51, "centre or idle cap")
    profile = {int(rank): int(count_) for rank, count_ in selected["local_profile_per_call"].items()}
    require(profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "selected local profile")
    mass = sum(rank * count_ for rank, count_ in profile.items())
    require(mass == 5586 and str(selected["local_mass_per_call"]) == "5586", "local mass")
    require(str(selected["idle_mass_per_call"]) == "1646", "idle mass")
    families = 2 * model["pairs"] * model["ports"]
    require(families == 896, "family count")

    ceiling = load_ceiling()
    target = Fraction(1, 99)
    fractional = {9: Fraction(mass, 9)}
    quantities = ceiling.model(fractional, 73, families, 9, 64)
    require(quantities["local_mass"] == mass, "fractional profile changed the local mass")
    require(quantities["idle_mass"] == 1646, "fractional profile changed the idle mass")
    require(quantities["R"] == 51, "idle cap")
    low, high = ceiling.relax(fractional, 73, families, 9, 64, target)
    require(low > 1, "rank-9 relaxation at 1/99 is not strictly above one")
    integer = {9: 620, 6: 1}
    require(sum(rank * count_ for rank, count_ in integer.items()) == mass, "integer histogram mass")
    integer_low, _integer_high = ceiling.relax(integer, 73, families, 9, 64, target)
    require(integer_low > 1, "integer rank-9 histogram passes 1/99")
    for rank in range(1, 9):
        smaller = ceiling.child_cost(rank, 73, target)
        larger = ceiling.child_cost(9, 73, target)
        require(larger[1] / 9 < smaller[0] / rank, "rank 9 is not strictly cheaper per unit than rank %d" % rank)
    cap_low, cap_high = ceiling.ceiling(fractional, 73, families, 9, 64, grid=Fraction(1, 10**15))
    require(cap_high < target, "rank-9 ceiling reaches 1/99")
    require(cap_low < cap_high, "ceiling bracket is empty")
    # A larger alphabet cap is visible to the same screen, so the failure is not a stuck comparator.
    wide_low, wide_high = ceiling.relax({44: Fraction(mass, 44)}, 73, families, 9, 64, target)
    require(wide_high < 1, "rank-44 control did not fall below one at 1/99")
    require(wide_low < 1, "rank-44 control enclosure straddles one")

    print(
        "PASS_E8_LABEL_PAIRING_RANK_CAP"
        " lines=120 pairing_rank=9 attained=9"
        " witness_lines=%s"
        " local_mass=5586 idle_mass=1646"
        " relax_1/99_low=%s"
        " ceiling=(%s,%s)"
        " below_1/99=yes integer_histogram_fails=yes rank44_control_passes=yes"
        % (
            ",".join(str(index) for index in basis),
            low,
            cap_low,
            cap_high,
        )
    )


if __name__ == "__main__":
    main()
