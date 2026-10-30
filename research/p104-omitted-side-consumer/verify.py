#!/usr/bin/env python3
"""Straight-line unit-addition bill for one bank of (N-P) tensor M.

The canonical P104 fixture determines B2. PR #3996 states
N-P = U^{-t}(I-A)U^{-1} and M = UU^t, and the two-pair uncorrected Gram
saving of 110592 unit additions. This checker builds the shear program for
one application of (N-P) tensor M and counts its B2 coefficient additions.
It does not replay the 763392 literal events and does not claim a minimum.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json"
FIXTURE_SHA256 = "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"
B2_SHA256 = "88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535"
N = 104
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)
ENTRY_ADDS = 319488
CODED_PAIR_ADDS = 26240
REFERENCE_PAIR_ADDS = 241280
MARGINAL_ADDS = REFERENCE_PAIR_ADDS - CODED_PAIR_ADDS  # 215040


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def load_b2():
    raw = FIXTURE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256, "canonical P104 fixture")
    section = json.loads(raw)["section4_explicit_P104"]
    roots = set()
    for coords in itertools.product((-2, 0, 2), repeat=8):
        support = [value for value in coords if value]
        if len(support) == 2 and support[0] > 0:
            roots.add(coords)
    for coords in itertools.product((-1, 1), repeat=8):
        if coords[0] == 1 and coords.count(-1) % 2 == 0:
            roots.add(coords)
    removed = {tuple(row) for row in section["F0"] + section["C"]}
    require(len(roots) == 120 and len(removed) == 16 and removed <= roots, "E8 root domain")
    original = sorted(roots - removed)
    order = list(PIVOTS) + [index for index in range(N) if index not in PIVOTS]
    ports = [original[index] for index in order]
    gram = [[sum(left * right for left, right in zip(row, other)) for other in ports] for row in ports]
    b2 = [[gram[i][8 + j] // 4 for j in range(96)] for i in range(8)]
    digest = hashlib.sha256(json.dumps(b2, separators=(",", ":")).encode("ascii")).hexdigest()
    require(digest == B2_SHA256, "ordered B2 digest")
    return b2


def check_b2(b2):
    values = {entry for row in b2 for entry in row}
    require(values <= {0, 1, -1}, "B2 entries are not in {0, ±1}")
    nonzero = sum(entry != 0 for row in b2 for entry in row)
    require(nonzero == 384, "B2 nonzero count")
    require(all(sum(entry != 0 for entry in row) == 48 for row in b2), "B2 row weight")
    require(all(sum(b2[i][j] != 0 for i in range(8)) == 4 for j in range(96)), "B2 column weight")
    for i in range(8):
        for j in range(8):
            product = sum(b2[i][k] * b2[j][k] for k in range(96))
            require(product == 48 * int(i == j), "B2 B2^t = 48 I")
    return nonzero


def scaled_operators(b2):
    """side = 4(N-P) and moment = 4M, with M = UU^t and B = B2/2."""
    upper = [[2 if i == j else 0 for j in range(N)] for i in range(N)]
    inverse = [[2 if i == j else 0 for j in range(N)] for i in range(N)]
    for i in range(8):
        for j in range(96):
            upper[i][8 + j] = b2[i][j]
            inverse[i][8 + j] = -b2[i][j]
    pivot = [[1 if i == j < 8 else 0 for j in range(N)] for i in range(N)]

    def matmul(left, right):
        columns = list(zip(*right))
        return [[sum(x * y for x, y in zip(row, column)) for column in columns] for row in left]

    def transpose(matrix):
        return [list(row) for row in zip(*matrix)]

    gram_scale = matmul(matmul(transpose(upper), pivot), upper)  # 4A
    squared = matmul(gram_scale, gram_scale)
    require(squared == [[52 * entry for entry in row] for row in gram_scale], "A^2 = 13A")
    left = [[4 * int(i == j) - gram_scale[i][j] for j in range(N)] for i in range(N)]
    sixteen = matmul(matmul(transpose(inverse), left), inverse)  # 16(N-P)
    require(all(entry % 4 == 0 for row in sixteen for entry in row), "N-P scale")
    side = [[entry // 4 for entry in row] for row in sixteen]
    moment = matmul(upper, transpose(upper))  # 4M
    return side, moment


def b2_times(b2, vector, counter):
    output = [0] * 8
    for i in range(8):
        total = 0
        for j in range(96):
            coefficient = b2[i][j]
            if coefficient:
                total += coefficient * vector[j]
                counter[0] += 1
        output[i] = total
    return output


def b2_transpose_times(b2, vector, counter):
    output = [0] * 96
    for j in range(96):
        total = 0
        for i in range(8):
            coefficient = b2[i][j]
            if coefficient:
                total += coefficient * vector[i]
                counter[0] += 1
        output[j] = total
    return output


def apply_m_to_row(b2, row, counter):
    """Right-multiply one row by M = UU^t. Two shears, 768 B2 additions."""
    pivot = [Fraction(entry) for entry in row[:8]]
    rest = [Fraction(entry) for entry in row[8:]]
    mixed = b2_transpose_times(b2, pivot, counter)
    sheared = [rest[j] + Fraction(mixed[j], 2) for j in range(96)]
    back = b2_times(b2, sheared, counter)
    return [pivot[i] + Fraction(back[i], 2) for i in range(8)] + sheared


def apply_np_to_column(b2, column, counter, omit_btb=False):
    """Left-multiply one column by N-P. Three B2 matvecs, 1152 additions."""
    pivot = [Fraction(entry) for entry in column[:8]]
    rest = [Fraction(entry) for entry in column[8:]]
    image = b2_times(b2, rest, counter)  # B2 rest = 2 B rest
    composed = [0] * 96 if omit_btb else b2_transpose_times(b2, image, counter)
    cross = b2_transpose_times(b2, pivot, counter)
    out_pivot = [Fraction(-image[i], 2) for i in range(8)]
    out_rest = [rest[j] - Fraction(cross[j], 2) + Fraction(composed[j], 4) for j in range(96)]
    return out_pivot + out_rest


def consume_bank(b2, matrix, omit_btb=False):
    """Apply (N-P) X M and return (matrix, B2-addition count)."""
    counter = [0]
    right = [apply_m_to_row(b2, row, counter) for row in matrix]
    columns = []
    for j in range(N):
        columns.append(apply_np_to_column(
            b2, [right[i][j] for i in range(N)], counter, omit_btb=omit_btb))
    output = [[columns[j][i] for j in range(N)] for i in range(N)]
    return output, counter[0]


def reference_bank(side, moment, matrix):
    """(N-P) X M = side (X moment) / 16."""
    width = len(matrix)
    moment_columns = list(zip(*moment))
    scaled = []
    for row in matrix:
        scaled.append([sum(entry * moment_columns[column][k]
                           for k, entry in enumerate(row))
                       for column in range(width)])
    product = []
    for i in range(width):
        product.append([sum(side[i][k] * scaled[k][j] for k in range(width))
                        for j in range(width)])
    return [[Fraction(entry, 16) for entry in row] for row in product]


def gram_add_saving(pairs):
    """PR #3996 unit-ADD gap: reference pairs minus entry/exit minus coded pairs."""
    require(type(pairs) is int and pairs >= 0, "pair count")
    return REFERENCE_PAIR_ADDS * pairs - ENTRY_ADDS - CODED_PAIR_ADDS * pairs


def banks():
    ones = [[1 for _ in range(N)] for _ in range(N)]
    spike = [[0 for _ in range(N)] for _ in range(N)]
    spike[0][0] = 1
    modular = [[(3 * i + 5 * j + 1) % 7 - 3 for j in range(N)] for i in range(N)]
    return ones, spike, modular


def main():
    b2 = load_b2()
    nonzero = check_b2(b2)
    side, moment = scaled_operators(b2)
    counts = []
    for matrix in banks():
        output, adds = consume_bank(b2, matrix)
        require(output == reference_bank(side, moment, matrix), "consumer differs from (N-P)XM")
        counts.append(adds)
    require(counts == [199680, 199680, 199680], "addition count depends on the bank")
    one_side = counts[0]
    require(one_side == N * (2 * nonzero + 3 * nonzero), "5 matvecs times 104 times nnz")
    require(gram_add_saving(1) == -104448, "one-pair ADD gap")
    require(gram_add_saving(2) == 110592, "two-pair ADD saving")
    require(MARGINAL_ADDS == 215040, "marginal ADD saving")
    net_two = gram_add_saving(2) - one_side
    net_three = gram_add_saving(3) - one_side
    require(net_two == -89088 and net_three == 125952, "net after one side")
    both_sides = 2 * one_side
    require(CODED_PAIR_ADDS + both_sides > REFERENCE_PAIR_ADDS, "both sides versus one reference pair")
    broken, broken_adds = consume_bank(b2, banks()[0], omit_btb=True)
    require(broken != reference_bank(side, moment, banks()[0]), "dropped B^t B term still matched")
    require(broken_adds == one_side - N * nonzero, "dropped term was not one matvec per column")
    receipt = {
        "adds_one_side": one_side,
        "adds_m_right_multiply": N * 2 * nonzero,
        "adds_np_left_multiply": N * 3 * nonzero,
        "b2_nonzero": nonzero,
        "banks_checked": 3,
        "both_sides_adds": both_sides,
        "both_sides_exceed_one_reference_pair": True,
        "k2_gram_add_saving": gram_add_saving(2),
        "k2_net_after_one_side": net_two,
        "k3_net_after_one_side": net_three,
        "minimum_claimed": False,
        "new_kappa": False,
    }
    print("PASS_P104_OMITTED_SIDE_CONSUMER " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
