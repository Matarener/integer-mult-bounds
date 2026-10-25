#!/usr/bin/env python3
"""One odd root pair climbs by copy rank 7, and the ideal screen clears 5%.

The checker rebuilds the 120 lines, prices this one pair, and screens the
eight-child profile. It does not census frames.
"""

import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ODD_PAIR_BLOCK_RANK punctured_rank=7 above_five_percent=true no_new_kappa"
ALPHA = (2, 2, 0, 0, 0, 0, 0, 0)
BETA = (1, 1, 1, 1, 1, 1, 1, 1)
SELECTED = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
from ceiling import ceiling  # noqa: E402


def fail(message):
    raise SystemExit("FAIL_ODD_PAIR_BLOCK_RANK " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/complex-frame-pair-decoders/README.md",
        "research/complex-local-word-ceiling/ceiling.py",
        "research/complex-local-word-ceiling/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def lines():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for left in (1, -1):
            for right in (1, -1):
                vector = [0] * 8
                vector[i], vector[j] = 2 * left, 2 * right
                roots.append(tuple(vector))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(signs)
    found = []
    seen = set()
    for root in roots:
        key = root if root > tuple(-part for part in root) else tuple(-part for part in root)
        if key not in seen:
            seen.add(key)
            found.append(root)
    require(len(found) == 120, "the line count moved")
    return found


def inner(left, right):
    value = sum(a * b for a, b in zip(left, right))
    require(value % 4 == 0, "an inner product left the doubled lattice")
    return value // 4


def rank(rows):
    basis = {}
    found = 0
    for row in rows:
        while row:
            head = row.bit_length() - 1
            if head in basis:
                row ^= basis[head]
            else:
                basis[head] = row
                found += 1
                break
    return found


def pair_rank(labels, rows, cols):
    mask = 0
    for index in cols:
        mask |= 1 << index
    return rank(labels[index] & mask for index in rows)


def copy_rank(table, labels, live, left, right):
    rows = [index for index in live if table[left][index]]
    cols = [index for index in live if table[right][index]]
    return pair_rank(labels, rows, cols)


def evaluate():
    authenticate()
    note = (ROOT / "research/complex-frame-pair-decoders/README.md").read_text(encoding="utf-8")
    require(
        "If both lines are punctured, it costs exactly 7 (for p ≤ 24). If either line is live, or if\n"
        "   α = β (the coordinate decoder), it costs 8." in note,
        "the cost sentence moved",
    )
    ceiling_note = (ROOT / "research/complex-local-word-ceiling/README.md").read_text(encoding="utf-8")
    require(
        "Centre path free (no rank-8 copies, no 64-per-call charge)" in ceiling_note,
        "the centre lever moved",
    )
    found = lines()
    alpha = found.index(ALPHA)
    beta = found.index(BETA)
    table = [[inner(found[i], found[j]) for j in range(120)] for i in range(120)]
    require(table[alpha][beta] == 1, "the pair is not odd")
    labels = [
        sum(((table[i][j] + 1) & 1) << j for j in range(120))
        for i in range(120)
    ]
    punctured = [index for index in range(120) if index not in (alpha, beta)]
    punctured_rank = copy_rank(table, labels, punctured, alpha, beta)
    alpha_live = copy_rank(table, labels, punctured + [alpha], alpha, beta)
    beta_live = copy_rank(table, labels, punctured + [beta], alpha, beta)
    self_rank = copy_rank(table, labels, [index for index in range(120) if index != alpha], alpha, alpha)
    require(punctured_rank == 7 and alpha_live == 8 and beta_live == 8 and self_rank == 8, "the copy ranks moved")
    block = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 7: 8}
    require(sum(rank * count for rank, count in block.items()) == 5578, "the block mass moved")
    selected = ceiling(SELECTED, 73, 896, 9, 64, grid=Fraction(1, 10**12))
    screened = ceiling(block, 73, 896, 9, 56, grid=Fraction(1, 10**12))
    require(selected[1] == Fraction(169005411, 100000000000), "the selected ceiling moved")
    require(screened[1] == Fraction(2069881607, 1000000000000), "the block ceiling moved")
    ratio = screened[1] / selected[1]
    require(ratio == Fraction(26201033, 21393090) and ratio > Fraction(21, 20), "the five-percent gap moved")
    return {
        "pair_ip": 1,
        "punctured_rank": 7,
        "live_rank": 8,
        "copy_mass": 56,
        "ceiling_hi": "2069881607/1000000000000",
        "selected_ceiling_hi": "169005411/100000000000",
        "ratio_above_five_percent": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
