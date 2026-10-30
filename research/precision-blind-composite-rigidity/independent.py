#!/usr/bin/env python3
"""Independent replay of antidiagonal rigidity. Does not import the package prover.

Affine CRT and a D-index-first case split. Prepared by Wentao Li with
substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from math import gcd


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def crt(r1: int, m1: int, r2: int, m2: int) -> int:
    modulus = m1 * m2
    need(gcd(m1, m2) == 1, "coprime")
    return (r1 * m2 * pow(m2, -1, m1) + r2 * m1 * pow(m1, -1, m2)) % modulus


def reciprocal(weights: list[int], modulus: int) -> bool:
    n = len(weights)
    return all((weights[i] * weights[n - 1 - i]) % modulus == 1 for i in range(n))


def solve(weights: list[int], modulus: int, i: int, j: int):
    """D-index first: the only free scale sits on the antidiagonal."""
    n = len(weights)
    if (n - 1 - j) != i:
        if not reciprocal(weights, modulus):
            return None
        return 1, 1
    partner = n - 1 - i
    s = pow((weights[i] * weights[partner]) % modulus, -1, modulus)
    t = pow(s, -1, modulus)
    target = list(weights)
    target[i] = (s * weights[i]) % modulus
    pairs_ok = all(
        (weights[k] * weights[n - 1 - k]) % modulus == 1
        for k in range(n)
        if k not in (i, partner)
    )
    if not pairs_ok or not reciprocal(target, modulus):
        return None
    return s, t


def classify(a0: int, middles: tuple[int, ...], modulus: int) -> list[tuple[int, int]]:
    weights = [a0 % modulus, *[m % modulus for m in middles], 1]
    n = len(weights)
    need(n % 2 == 1 and n >= 3, "odd n")
    need(all(gcd(x, modulus) == 1 for x in weights), "units")
    need(weights[0] != 1, "defect")
    goods = []
    for i in range(n):
        for j in range(n):
            if solve(weights, modulus, i, j) is not None:
                goods.append((i, j))
    return sorted(goods)


def valuation_pm1(p: int, k: int, x: int) -> str:
    modulus = p**k
    x %= modulus
    if (x * x) % modulus != 1:
        return "not-solution"
    left = (x - 1) % modulus
    right = (x + 1) % modulus
    v_left = 0
    while v_left < k and left % p == 0:
        left //= p
        v_left += 1
    v_right = 0
    while v_right < k and right % p == 0:
        right //= p
        v_right += 1
    need(v_left == 0 or v_right == 0, "shared odd prime")
    if v_left == 0:
        need(right == 0, "x≡-1")
        return "-1"
    need(left == 0, "x≡+1")
    return "+1"


def main() -> None:
    # CRT single-factor on 3*5, 9*5 and 3*35, plus a non-square defect.
    checks = 0
    for part1, part2, middles in (
        (3, 5, (1, 1, 1)),
        (9, 5, (1, -1, 1)),
        (3, 35, (1, 1, 1, 1, 1)),
        (5, 7, (-1,)),
    ):
        modulus = part1 * part2
        a0 = crt(1, part1, -1, part2)
        need((a0 * a0) % modulus == 1 and a0 not in (1, modulus - 1), "nontrivial")
        goods = classify(a0, middles, modulus)
        n = len(middles) + 2
        need(goods == [(0, n - 1), (n - 1, 0)], f"ends {goods}")
        # Shared scale: s=t=a0 because a0^{-1}=a0.
        weights = [a0, *[m % modulus for m in middles], 1]
        solved = solve(weights, modulus, n - 1, 0)
        need(solved == (a0, a0), f"shared scale {solved}")
        checks += 1
    for modulus, a0, middles in ((15, 2, (1, 14, 1)), (35, 3, (1,))):
        goods = classify(a0, middles, modulus)
        n = len(middles) + 2
        need(goods == [(0, n - 1), (n - 1, 0)], "defect ends")
        weights = [a0, *[m % modulus for m in middles], 1]
        solved = solve(weights, modulus, n - 1, 0)
        need(solved is not None and solved[0] != solved[1], "two scales")
        checks += 1
    for modulus, a0, middles in ((15, 4, (1, 1, -1)), (21, 8, (-1, 1, 1))):
        need(classify(a0, middles, modulus) == [], "illegal")
        checks += 1
    for p, k in ((3, 2), (3, 3), (5, 2), (7, 2)):
        modulus = p**k
        kinds = {valuation_pm1(p, k, x) for x in range(modulus) if (x * x) % modulus == 1}
        need(kinds == {"+1", "-1"}, f"{p}^{k}")
        checks += 1
    # gcd recovery is not the CRT constructor above.
    a0 = crt(1, 3, -1, 5)
    need(gcd(a0 - 1, 15) in (3, 5), "gcd factor")
    checks += 1
    print(
        "PASS_INDEPENDENT_PRECISION_BLIND_COMPOSITE_RIGIDITY",
        f"checks={checks}",
        "single_factor_iff_square=true",
        "boolean_meters=false",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
