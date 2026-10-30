#!/usr/bin/env python3
"""Independent exact symplectic-frame census and rational-bound controls.

For CrocSwap/integer-mult-bounds PR #5694 at
  aa01976e51aa1731433a9e65443303a7c2f869ca.
This file does not import the PR's source, generators, or residual-form code.
Substantial OpenAI assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from itertools import product
from math import prod
import json
import platform
import time


def omega(u: int, v: int, n: int) -> int:
    mask = (1 << n) - 1
    return (
        ((u & mask) & (v >> n)).bit_count()
        + ((v & mask) & (u >> n)).bit_count()
    ) & 1


def rank(vectors) -> int:
    pivots: dict[int, int] = {}
    for v in vectors:
        while v:
            bit = v.bit_length() - 1
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit] = v
                break
    return len(pivots)


def frame_census(n: int) -> list[int]:
    """Enumerate every ordered symplectic basis of F_2^(2n)."""
    hist = Counter()

    def recurse(pairs: tuple[tuple[int, int], ...], complement: tuple[int, ...]):
        if len(pairs) == n:
            columns = [a for a, _ in pairs] + [b for _, b in pairs]
            displacement = [columns[j] ^ (1 << j) for j in range(2 * n)]
            hist[rank(displacement)] += 1
            return
        for e in complement:
            if e == 0:
                continue
            for f in complement:
                if omega(e, f, n) != 1:
                    continue
                next_complement = tuple(
                    v for v in complement
                    if omega(v, e, n) == 0 and omega(v, f, n) == 0
                )
                recurse(pairs + ((e, f),), next_complement)

    recurse((), tuple(range(1 << (2 * n))))
    result = [hist[k] for k in range(2 * n + 1)]
    group_order = (1 << (n * n)) * prod((1 << (2*j)) - 1 for j in range(1, n + 1))
    if sum(result) != group_order:
        raise ValueError(f"symplectic group order mismatch for n={n}")
    if result[1] != (1 << (2 * n)) - 1:
        raise ValueError(f"rank-one transvection count mismatch for n={n}")
    return result


def brute_force_sp4():
    """Unrelated literal matrix oracle: scan all 2^16 binary 4x4 matrices."""
    hist = Counter()
    for columns in product(range(16), repeat=4):
        if all(omega(columns[i], columns[j], 2) == omega(1 << i, 1 << j, 2)
               for i in range(4) for j in range(i+1, 4)):
            hist[rank([columns[i] ^ (1 << i) for i in range(4)])] += 1
    return [hist[k] for k in range(5)]


def exact_row(n: int, counts: list[int]) -> Fraction:
    N = 2 * n
    return sum((Fraction((1 << k) * c, 1 << (k * (N + 2)))
                for k, c in enumerate(counts) if k), Fraction())


def check():
    expected = {
        1: ([1, 3, 2], Fraction(13, 32)),
        2: ([1, 15, 100, 300, 304], Fraction(37739, 65536)),
        3: ([1, 63, 1932, 28980, 202944, 608832, 608768],
            Fraction(5366132533, 8589934592)),
    }
    evidence = {}
    for n, (want_hist, want_row) in expected.items():
        counts = frame_census(n)
        row = exact_row(n, counts)
        if counts != want_hist or row != want_row:
            raise ValueError(f"symplectic-frame count mismatch at n={n}")
        N = 2*n
        for k in range(1, N+1):
            upper = 1 << (N*k - k*(k-1)//2)
            if counts[k] > upper:
                raise ValueError(f"upper count bound violation at n={n} k={k}")
            if N >= 2*k:
                lower = prod((1 << (N-i)) - (1 << i) for i in range(k))
                if counts[k] < lower:
                    raise ValueError(f"lower count bound violation at n={n} k={k}")
        evidence[str(n)] = {"rank_histogram": counts, "row": str(row)}
    if brute_force_sp4() != expected[2][0]:
        raise ValueError("independent all-matrix Sp4 oracle mismatch")

    partial5 = sum((Fraction(1, 1 << (k*(k+1)//2)) for k in range(1, 6)), Fraction())
    tail_first = Fraction(1, 1 << 21)
    upper_tail = partial5 + tail_first / (1 - Fraction(1, 1 << 7))
    alpha = 1 - upper_tail
    if alpha != Fraction(1491359, 4161536):
        raise ValueError("submitted rational alpha not reproduced")
    partial8 = sum((Fraction(1, 1 << (k*(k+1)//2)) for k in range(1, 9)), Fraction())
    gap_upper = upper_tail - partial8
    if gap_upper != Fraction(129, 8727373545472) or gap_upper >= Fraction(148, 10**13):
        raise ValueError("limit gap certificate not reproduced")
    # Deliberately incorrect tail ratio 2^-8 (instead of 2^-7) must fail
    # even the finite k<=8 lower control.
    wrong_upper_tail = partial5 + tail_first / (1 - Fraction(1, 1 << 8))
    if not wrong_upper_tail < partial8:
        raise ValueError("invalid-fast-tail negative control unexpectedly accepted")

    return {
        "status": "PASS_INDEPENDENT_ROW_SHARPNESS",
        "scope": "finite n<=3 corroboration; all-n lower-bound/limit proof in README.md",
        "python": platform.python_version(),
        "histograms": evidence,
        "rational_alpha": str(alpha),
        "exact_series_gap_upper": str(gap_upper),
        "controls": ["Sp group orders", "rank-1 transvections", "Sp4 brute matrix sweep",
                     "all finite upper/lower inequalities", "rational tail", "invalid faster ratio"],
    }


if __name__ == '__main__':
    start = time.monotonic()
    receipt = check()
    receipt["elapsed_seconds"] = round(time.monotonic() - start, 3)
    print(json.dumps(receipt, sort_keys=True, indent=2))