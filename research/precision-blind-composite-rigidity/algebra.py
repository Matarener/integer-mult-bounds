"""Antidiagonal rigidity for precision-blind dual scales on odd moduli.

For odd M≥3 and odd length n=2k+1≥3, a unit weight
a=(a0, middles, 1) with a0≢1 admits an involutory dual-scale target on
exactly the far end (H'_{n-1}, D'_0) and the near end (H'_0, D'_{n-1}),
and only when every middle pair is reciprocal. Off the antidiagonal
j=n-1-i a dual scale cannot change any weight. A shared single-factor
scale on those ends exists iff a0²≡1. A unit a0 with a0²≡1 and a0≢±1
exists iff M is not an odd prime power.

No Boolean meters. No reprint of the #4073 n=5/n=7 prime-power grids.
No new kappa.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from math import gcd

KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def is_odd_prime(p: int) -> bool:
    if type(p) is not int or p < 3 or p % 2 == 0:
        return False
    d = 3
    while d * d <= p:
        if p % d == 0:
            return False
        d += 2
    return True


def inv(x: int, modulus: int) -> int:
    need(gcd(x, modulus) == 1, f"{x} not invertible mod {modulus}")
    return pow(x % modulus, -1, modulus)


def fully_reciprocal(weights: list[int], modulus: int) -> bool:
    n = len(weights)
    return all((weights[i] * weights[n - 1 - i]) % modulus == 1 for i in range(n))


def middle_reciprocal(weights: list[int], modulus: int) -> bool:
    n = len(weights)
    return all((weights[i] * weights[n - 1 - i]) % modulus == 1 for i in range(1, n - 1))


def prove_pm1(p: int, k: int, x: int) -> str:
    """If x²≡1 mod p^k for odd prime p, return '+1' or '-1'.

    (x-1) and (x+1) differ by 2, so an odd prime cannot divide both.
    Their p-valuations therefore cannot split, and p^k divides one factor.
    """
    need(is_odd_prime(p) and type(k) is int and k >= 1, "odd prime power")
    modulus = p**k
    x %= modulus
    if (x * x - 1) % modulus != 0:
        return "not-solution"
    v1 = 0
    aa = (x - 1) % modulus
    while v1 < k and aa % p == 0:
        aa //= p
        v1 += 1
    v2 = 0
    bb = (x + 1) % modulus
    while v2 < k and bb % p == 0:
        bb //= p
        v2 += 1
    need(not (v1 > 0 and v2 > 0), "p divides both x-1 and x+1, hence 2")
    if v1 == 0:
        need((x + 1) % modulus == 0, "coprime x-1 did not force x≡-1")
        return "-1"
    need(v2 == 0, "unsplit valuation")
    need((x - 1) % modulus == 0, "coprime x+1 did not force x≡+1")
    return "+1"


def crt(residues: list[int], moduli: list[int]) -> int:
    need(len(residues) == len(moduli) >= 2, "CRT needs at least two moduli")
    modulus = 1
    for m in moduli:
        need(type(m) is int and m > 1 and gcd(modulus, m) == 1, "pairwise coprime CRT")
        modulus *= m
    acc = 0
    for residue, part in zip(residues, moduli):
        rest = modulus // part
        acc += (residue % part) * rest * pow(rest, -1, part)
    return acc % modulus


def nontrivial_from_split(part1: int, part2: int) -> tuple[int, int]:
    """CRT witness a0≡1 mod part1, a0≡-1 mod part2. Then a0²≡1 and a0≢±1."""
    need(part1 > 1 and part2 > 1 and gcd(part1, part2) == 1, "coprime split")
    need(part1 % 2 == 1 and part2 % 2 == 1, "odd split")
    modulus = part1 * part2
    a0 = crt([1, -1], [part1, part2])
    need((a0 * a0) % modulus == 1, "CRT square")
    need(a0 % modulus not in (1, modulus - 1), "CRT nontrivial")
    need(gcd(a0 - 1, modulus) == part1, "gcd recovers the split")
    return modulus, a0


def split_from_nontrivial(modulus: int, a0: int) -> tuple[int, int]:
    """Inverse of the CRT map: gcd(a0-1, M) is a proper coprime factor."""
    need(type(modulus) is int and modulus >= 3 and modulus % 2 == 1, "odd modulus")
    a0 %= modulus
    need((a0 * a0) % modulus == 1, "a0 squares to 1")
    need(a0 not in (1, modulus - 1), "nontrivial")
    part1 = gcd(a0 - 1, modulus)
    need(1 < part1 < modulus, "proper factor")
    part2 = modulus // part1
    need(part1 * part2 == modulus and gcd(part1, part2) == 1, "coprime factor")
    need(crt([1, -1], [part1, part2]) % modulus == a0, "split round-trips")
    return part1, part2


def analyze_support(weights: list[int], modulus: int, i: int, j: int):
    """Solve one dual-scale support by antidiagonal rigidity.

    Returns (s, t, target) or None. Off the antidiagonal j=n-1-i, both
    scales are forced to 1, so the weight list is unchanged.
    """
    n = len(weights)
    need(0 <= i < n and 0 <= j < n, "support index")
    if j != n - 1 - i:
        # D' writes p_i = a_i, H' writes p_i = s a_i, and a_i is a unit.
        # H' writes the D-scaled slot as a_{n-1-j}, D' divides it by t.
        if not fully_reciprocal(weights, modulus):
            return None
        return 1, 1, list(weights)
    partner = n - 1 - i
    prod = (weights[i] * weights[partner]) % modulus
    s = inv(prod, modulus)
    t = inv(s, modulus)
    target = list(weights)
    target[i] = (s * weights[i]) % modulus
    # Consistency of the two writings of p_i: s a_i = a_i / t.
    need((s * weights[i]) % modulus == (weights[i] * inv(t, modulus)) % modulus,
         "scale consistency")
    other_ok = all(
        (weights[k] * weights[n - 1 - k]) % modulus == 1
        for k in range(n)
        if k != i and k != partner
    )
    if not other_ok or not fully_reciprocal(target, modulus):
        return None
    return s, t, target


def prove_supports(weights: list[int], modulus: int) -> dict:
    """Exact support classification for one odd modulus and one odd length."""
    need(type(modulus) is int and modulus >= 3 and modulus % 2 == 1, "odd modulus")
    n = len(weights)
    need(type(n) is int and n >= 3 and n % 2 == 1, "odd length n>=3")
    need(all(type(x) is int for x in weights), "integer weights")
    weights = [x % modulus for x in weights]
    need(all(gcd(x, modulus) == 1 for x in weights), "unit weights")
    need(weights[-1] == 1, "normalized far end")
    a0 = weights[0]
    need(a0 != 1, "precision defect a0≢1")
    goods = []
    for i in range(n):
        for j in range(n):
            solved = analyze_support(weights, modulus, i, j)
            if solved is None:
                continue
            s, t, target = solved
            goods.append({
                "H_index": i,
                "D_index": j,
                "scale_H": s,
                "scale_D": t,
                "target": target,
            })
    legal = middle_reciprocal(weights, modulus)
    inv_a0 = inv(a0, modulus)
    if not legal:
        need(goods == [], "illegal middles admit no dual-scale support")
        return {
            "modulus": modulus,
            "n": n,
            "a0": a0,
            "middle_reciprocal": False,
            "good_supports": [],
            "single_factor": False,
        }
    keys = sorted((g["H_index"], g["D_index"]) for g in goods)
    need(keys == [(0, n - 1), (n - 1, 0)], f"far+near only, got {keys}")
    far = next(g for g in goods if g["H_index"] == n - 1)
    near = next(g for g in goods if g["H_index"] == 0)
    need(far["scale_H"] == inv_a0 and far["scale_D"] == a0 % modulus, "far scales")
    need(near["scale_H"] == inv_a0 and near["scale_D"] == a0 % modulus, "near scales")
    need(far["target"] == weights[:-1] + [inv_a0], "far target")
    need(near["target"] == [1] + weights[1:], "near target")
    single = (a0 * a0) % modulus == 1
    need(single == (far["scale_H"] == far["scale_D"]), "single-factor iff a0^2=1")
    if single:
        need(far["scale_H"] == a0 and (a0 * far["scale_H"]) % modulus == 1,
             "shared scale is a0 itself")
    return {
        "modulus": modulus,
        "n": n,
        "a0": a0,
        "inv_a0": inv_a0,
        "middle_reciprocal": True,
        "a0_square": (a0 * a0) % modulus,
        "single_factor": single,
        "good_supports": [
            [g["H_index"], g["D_index"]] for g in sorted(
                goods, key=lambda g: (g["H_index"], g["D_index"])
            )
        ],
        "far_target": far["target"],
        "near_target": near["target"],
    }


def bank_formulas_match(weights: list[int], modulus: int) -> None:
    """Indexwise identity: far/near Norm equals F_{P'} for the proved targets."""
    proved = prove_supports(weights, modulus)
    need(proved["middle_reciprocal"], "bank identity needs reciprocal middles")
    n = proved["n"]
    a0 = proved["a0"]
    inv_a0 = proved["inv_a0"]
    # Far: scale H'_{n-1} by a0^{-1} and D'_0 by a0.
    # H'_k = a_k D_{n-1-k}; after the scale only k=n-1 changes, to a0^{-1} D_0.
    # F_{P'} with P'=(a0, middles, a0^{-1}) reproduces that coordinate.
    for k in range(n - 1):
        need(weights[k] == proved["far_target"][k], "far unscaled coordinate")
    need(proved["far_target"][n - 1] == inv_a0, "far scaled end")
    # Near: H'_0 is scaled by a0^{-1}, cancelling a0 D_{n-1} down to D_{n-1}.
    need((inv_a0 * a0) % modulus == 1, "near cancellation")
    need(proved["near_target"][0] == 1 and proved["near_target"][-1] == 1, "near units")
    for k in range(1, n - 1):
        need(proved["near_target"][k] == weights[k], "near middles unchanged")


def exhaustive_goods(weights: list[int], modulus: int) -> list[tuple[int, int]]:
    """Brute dual-scale search used only as a control on small witnesses."""
    n = len(weights)
    units = [x for x in range(modulus) if gcd(x, modulus) == 1]
    found = []
    for i in range(n):
        for j in range(n):
            hit = False
            for s in units:
                for t in units:
                    ph = [(s * weights[k] if k == i else weights[k]) % modulus for k in range(n)]
                    pd = [None] * n
                    ok = True
                    t_inv = pow(t, -1, modulus)
                    for k in range(n):
                        idx = n - 1 - k
                        val = (weights[idx] * t_inv if k == j else weights[idx]) % modulus
                        if pd[idx] is None:
                            pd[idx] = val
                        elif pd[idx] != val:
                            ok = False
                            break
                    if not ok or ph != pd:
                        continue
                    if fully_reciprocal(ph, modulus):
                        hit = True
                        break
                if hit:
                    break
            if hit:
                found.append((i, j))
    return sorted(found)


def weight_list(a0: int, middles: tuple[int, ...], modulus: int) -> list[int]:
    return [a0 % modulus, *[m % modulus for m in middles], 1]
