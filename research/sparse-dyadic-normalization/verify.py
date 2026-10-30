#!/usr/bin/env python3
"""Exact new-domain corroboration; no predecessor code is imported."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import gcd, prod
from pathlib import Path


PRIMES = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
MAX_ROWS = 16
MAX_BITS = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def is_dyadic(value):
    denominator = Fraction(value).denominator
    return denominator & (denominator - 1) == 0


def bezout_pair(left, right):
    """Bounded extended Euclid, including zero and signed right operands."""
    old_r, r = abs(left), abs(right)
    old_s, s, old_t, t = 1, 0, 0, 1
    limit = 2 * max(abs(left).bit_length(), abs(right).bit_length()) + 2
    for _ in range(limit):
        if r == 0:
            u = old_s if left >= 0 else -old_s
            v = old_t if right >= 0 else -old_t
            require(u * left + v * right == old_r, "Bezout invariant")
            return old_r, u, v
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    raise ValueError("Euclid iteration bound exhausted")


def decoder(base, rows):
    require(type(base) is int and 0 < base < 1 << MAX_BITS, "invalid base")
    require(len(rows) <= MAX_ROWS, "too many rows")
    require(all(type(v) is int and abs(v) < 1 << MAX_BITS for v in rows),
            "invalid row")
    coefficients = [1]
    common = base
    for row in rows:
        common, u, v = bezout_pair(common, row)
        coefficients = [u * coefficient for coefficient in coefficients] + [v]
    if common & (common - 1):
        return None
    answer = tuple(Fraction(coefficient, common) for coefficient in coefficients)
    check_decoder(base, rows, answer)
    return answer


def check_decoder(base, rows, coefficients):
    require(len(coefficients) == len(rows) + 1, "wrong coefficient count")
    require(all(is_dyadic(c) for c in coefficients), "non-dyadic coefficient")
    require(sum(c * value for c, value in zip(coefficients, (base, *rows))) == 1,
            "decoder identity failed")


def encode(universe_size, masks):
    require(type(universe_size) is int and 0 <= universe_size <= len(PRIMES),
            "invalid universe")
    require(len(masks) <= MAX_ROWS, "too many masks")
    require(all(type(m) is int and 0 <= m < 1 << universe_size for m in masks),
            "invalid mask")
    primes = PRIMES[:universe_size]
    base = prod(primes)
    rows = tuple(prod(p for j, p in enumerate(primes) if not (mask >> j & 1))
                 for mask in masks)
    return base, rows


def selected_indices(size, mask):
    return tuple(index for index in range(size) if mask >> index & 1)


def check_menu(universe_size, masks, counts):
    base, rows = encode(universe_size, masks)
    feasible = []
    for selection in range(1 << len(masks)):
        indices = selected_indices(len(masks), selection)
        union = 0
        for index in indices:
            union |= masks[index]
        chosen = tuple(rows[index] for index in indices)
        common = gcd(base, *chosen)
        expected_gcd = prod(PRIMES[j] for j in range(universe_size)
                            if not (union >> j & 1))
        require(common == expected_gcd, "uncovered-prime product")
        coefficients = decoder(base, chosen)
        covered = union == (1 << universe_size) - 1
        require((coefficients is not None) == covered, "cover equivalence")
        if coefficients is not None:
            for scalar in (Fraction(-3, 2), Fraction(0), Fraction(7, 3)):
                output = sum(c * value * scalar for c, value in
                             zip(coefficients, (base, *chosen)))
                require(output == scalar, "literal scalar decoding")
                counts["literal_decodings"] += 1
        feasible.append((indices, covered, common == 1))
        counts["menu_selections"] += 1
    for costs in product((1, 2, 3), repeat=len(masks)):
        cover_costs = [sum(costs[i] for i in ix) for ix, cover, _ in feasible if cover]
        gcd_costs = [sum(costs[i] for i in ix) for ix, _, unit in feasible if unit]
        require(min(cover_costs, default=None) == min(gcd_costs, default=None),
                "weighted optimum")
        counts["weighted_menus"] += 1
    counts["menus"] += 1


def check_unbounded_family(counts):
    for size in range(1, len(PRIMES) + 1):
        base, rows = encode(size, tuple(1 << j for j in range(size)))
        require(decoder(base, rows) is not None, "full family must decode")
        for selection in range(1 << size):
            indices = selected_indices(size, selection)
            common = gcd(base, *(rows[j] for j in indices))
            require((common == 1) == (len(indices) == size), "sharp acquisition floor")
            if len(indices) < size:
                missing = next(j for j in range(size) if not (selection >> j & 1))
                require(all(value % PRIMES[missing] == 0 for value in
                            (base, *(rows[j] for j in indices))), "modular obstruction")
            counts["sharp_family_selections"] += 1
        counts["sharp_family_sizes"] += 1


def must_reject(function, *arguments):
    try:
        function(*arguments)
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def check_controls(counts):
    for base, rows in ((0, ()), (-1, ()), (True, ()), (1 << MAX_BITS, ()),
                       (1, (True,)), (1, (Fraction(1, 2),)),
                       (1, (0,) * (MAX_ROWS + 1)), (1, (1 << MAX_BITS,))):
        must_reject(decoder, base, rows)
        counts["rejection_controls"] += 1
    for size, masks in ((-1, ()), (13, ()), (1, (2,)), (1, (-1,))):
        must_reject(encode, size, masks)
        counts["rejection_controls"] += 1
    for base, rows, coefficients in ((3, (), (Fraction(1, 3),)),
                                      (3, (5,), (1, 0)),
                                      (3, (5,), (1,))):
        must_reject(check_decoder, base, rows, coefficients)
        counts["rejection_controls"] += 1
    for base, rows in ((8, ()), (12, (-20, 0)), (12, (18, 0)), (45, (0, -14))):
        result = decoder(base, rows)
        common = gcd(base, *rows)
        require((result is not None) == (common & (common - 1) == 0),
                "signed/non-squarefree boundary")
        counts["boundary_controls"] += 1
    base, rows = encode(3, (1, 2, 4))
    require((base, rows) == (105, (35, 21, 15)), "complement convention")
    require(all(decoder(base, (row,)) is None for row in rows), "rational rank mutant")
    require(all(decoder(base, rows[:j] + rows[j + 1:]) is None for j in range(3)),
            "two-observation mutant")
    counts["semantic_controls"] = 3


def main():
    counts = dict.fromkeys(("menus", "menu_selections", "weighted_menus",
                           "literal_decodings", "sharp_family_sizes",
                           "sharp_family_selections", "rejection_controls",
                           "boundary_controls", "semantic_controls"), 0)
    for size in range(4):
        for length in range(4):
            for masks in product(range(1 << size), repeat=length):
                check_menu(size, masks, counts)
    check_unbounded_family(counts)
    check_controls(counts)
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_SPARSE_DYADIC_NORMALIZATION", "counts": counts,
                      "source_sha256": hashes}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
