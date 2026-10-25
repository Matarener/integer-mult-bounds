#!/usr/bin/env python3
"""Independent check of #4377's uniform CRT evaluator bound E(p, ell) <= 2^(4 ell) (p+2)^16.

Part A  #4377's tariff lemmas and closing inequality, re-derived with exact integers: schoolbook 8ab,
        restoring division 8ab, Euclid 64 b^3, the six cost terms, the q = 4 maximum, the ell-step factors
        and the guard amortization, on p = 2..200 and ell = 1..40.
Part B  an instrumented copy of #4100's retained decode_group / balanced offset (check_batched_crt.py,
        pinned) that charges every multiplication, division, inverse and addition with its ACTUAL operand bit
        lengths under #4377's tariffs, on random CRT groups at the caller's sizes, compared with #4377's
        per-axis bill 128 m W^2 + 128 m ell^3 + 16 m W.
Part C  the per-wire table step: #4377 states 9(ell+2)^2, but its own add + division tariffs give
        4(ell+2) + 8(ell+2)^2, which exceeds 9(ell+2)^2 exactly at ell = 1 (84 > 81). The per-network bound
        25(ell+2)^2 2^ell + 64 ell 2^(2 ell) still holds with the corrected step, so the slip is not
        load-bearing.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/unconditional-batched-crt/check_batched_crt.py"
RETAINED = [
    "        complement = product // modulus\n        residue = value * prefix % modulus\n"
    "        answer += residue * complement * pow(complement, -1, modulus)\n        prefix *= modulus\n",
    "                offset = lower * pow(prefix, -1, moduli[i]) % moduli[i]\n",
]
rng = random.Random(4377)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def bits(x):
    return max(1, abs(x).bit_length())


# ---- #4377 tariffs ---------------------------------------------------------------------------
def t_mul(a, b):
    return 8 * bits(a) * bits(b)


def t_div(n, d):
    """restoring division, quotient length = bit length of the quotient"""
    return 8 * bits(n // d) * bits(d)


def t_inv(x, m):
    """reduce x mod m (a division) then Euclid at 64 b^3, b = bits(m)"""
    return t_div(x, m) + 64 * bits(m) ** 3


def t_add(a, b):
    return 4 * max(bits(a), bits(b))


def charged_axis(residues, moduli, target, right_prefix):
    """decode_group of the left group, then lower * (left product * right prefix)^-1 mod target"""
    cost = 0
    product = 1
    for m in moduli:
        if product != 1:
            cost += t_mul(product, m)
        product *= m
    answer, prefix = 0, 1
    for value, m in zip(residues, moduli):
        cost += t_div(product, m)
        complement = product // m
        cost += t_mul(value, prefix) + t_div(value * prefix, m)
        residue = value * prefix % m
        cost += t_inv(complement, m)
        inv = pow(complement, -1, m)
        cost += t_mul(residue, complement) + t_mul(residue * complement, inv)
        term = residue * complement * inv
        cost += t_add(answer, term)
        answer += term
        cost += t_mul(prefix, m)
        prefix *= m
    cost += t_div(answer, product)
    lower = answer % product
    full = product * right_prefix
    cost += t_mul(product, right_prefix) + t_inv(full, target)
    inv = pow(full, -1, target)
    cost += t_mul(lower, inv) + t_div(lower * inv, target)
    return cost, lower * inv % target


def odd_primes(lo, hi):
    out = []
    for n in range(max(3, lo), hi):
        if n % 2 and all(n % d for d in range(3, int(n ** 0.5) + 1, 2)):
            out.append(n)
    return out


def is_prime(n):
    """deterministic Miller-Rabin for n < 3.3e24"""
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
    if n in small:
        return True
    if any(n % a == 0 for a in small):
        return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d, r = d // 2, r + 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(ell):
    while True:
        n = rng.randrange(2 ** (ell - 1) + 1, 2 ** ell) | 1
        if is_prime(n):
            return n


def main():
    raw = SRC.read_text(encoding="utf-8")
    import importlib.util
    spec = importlib.util.spec_from_file_location("retained_crt", SRC)
    retained = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(retained)
    for snippet in RETAINED:
        need(snippet in raw, "retained decode_group / balanced lines")

    # Part A: lemmas on a grid, then the master inequality exactly
    for a in range(1, 65):
        for b in range(1, 65):
            need(3 * a * b + 3 * a + b <= 8 * a * b, "schoolbook 8ab")
            need(3 * a * b + 4 * a <= 8 * a * b, "division 8ab")
        need(2 * a * (8 * a * a + 16 * a * a + 4 * a) <= 64 * a ** 3, "Euclid 64 b^3")
    worst = 0.0
    for p in range(2, 201):
        q = p + 2
        for ell in range(1, 41):
            terms = [256 * q * q, 524288 * q ** 4, 8192 * q ** 3, 8192 * q * q * ell ** 3,
                     800 * q * (ell + 2) ** 2 * 2 ** ell, 2048 * q * ell * 4 ** ell]
            big = 2 ** (4 * ell) * q ** 16
            need(7 * max(terms) <= big and sum(terms) <= big, f"master inequality p={p} ell={ell}")
            worst = max(worst, sum(terms) / big)
            G = 64 * (ell + (q - 1).bit_length())
            need(sum(terms) * q ** 48 * 2 ** (60 * ell) <= 2 ** G, "guard amortization")

    # Part C: the per-wire step
    slips = [ell for ell in range(1, 41) if 4 * (ell + 2) + 8 * (ell + 2) ** 2 > 9 * (ell + 2) ** 2]
    need(slips == [1], "per-wire 9(ell+2)^2 fails exactly at ell = 1")
    for ell in range(1, 41):
        corrected = (4 * (ell + 2) + 8 * (ell + 2) ** 2) * 2 ** ell + 64 * ell * 4 ** ell + 8 * ell * 2 ** ell
        need(corrected <= 25 * (ell + 2) ** 2 * 2 ** ell + 64 * ell * 4 ** ell, "per-network bound absorbs it")

    # Part B: instrumented CRT bill at the caller's sizes
    samples = 0
    max_ratio = 0.0
    for ell in range(3, 13):
        primes = odd_primes(2 ** (ell - 1), 2 ** ell)
        for p in range(ell, min(8 * ell, 64) + 1, max(1, ell // 2)):
            for _ in range(6):
                m = rng.randint(1, max(1, p // ell))
                pool = rng.sample(primes, min(len(primes), 2 * m + 1))
                moduli, right, target = pool[:m], pool[m:2 * m], pool[-1]
                if target in moduli or target in right:
                    continue
                W = sum(bits(x) for x in moduli)
                need(W <= p, "group bit length at most p")
                residues = [rng.randrange(x) for x in moduli]
                rp = 1
                for x in right[:rng.randint(0, len(right))]:
                    rp *= x
                cost, off = charged_axis(residues, moduli, target, rp)
                prod = 1
                for x in moduli:
                    prod *= x
                ref = retained.decode_group(tuple(residues), tuple(moduli)) * pow(prod * rp, -1, target) % target
                need(off == ref, "instrumented offset equals the retained decode_group offset")
                bill = 128 * m * W * W + 128 * m * ell ** 3 + 16 * m * W
                need(cost <= bill, f"instrumented cost within the per-axis bill at p={p} ell={ell} m={m}")
                max_ratio = max(max_ratio, cost / bill)
                samples += 1
    # long moduli: the inverse term 128 m ell^3 saturates as ell grows at m = 1
    tight = []
    for ell in range(14, 33):
        for m in (1, 2, 4):
            moduli = [random_prime(ell) for _ in range(m)]
            right = [random_prime(ell) for _ in range(m)]
            target = random_prime(ell)
            if len(set(moduli + right + [target])) < 2 * m + 1:
                continue
            W = sum(bits(x) for x in moduli)
            residues = [rng.randrange(x) for x in moduli]
            rp = 1
            for x in right:
                rp *= x
            cost, off = charged_axis(residues, moduli, target, rp)
            prod = 1
            for x in moduli:
                prod *= x
            need(off == retained.decode_group(tuple(residues), tuple(moduli)) * pow(prod * rp, -1, target) % target,
                 "long-moduli offset")
            bill = 128 * m * W * W + 128 * m * ell ** 3 + 16 * m * W
            need(cost <= bill, f"long moduli ell={ell} m={m}: within the per-axis bill")
            max_ratio = max(max_ratio, cost / bill)
            if m == 1:
                tight.append(round(cost / bill, 4))
            samples += 1
    need(tight == sorted(tight) or max(tight) > 0.95, "m = 1 ratio approaches 1")
    need(samples > 300, "enough samples")
    print(json.dumps({
        "status": "PASS_CRT_EVALUATOR_INDEPENDENT_CHECK",
        "master_inequality_grid": "p = 2..200, ell = 1..40",
        "max_sum_terms_over_bound": f"{worst:.3e}",
        "per_wire_slip_at": slips,
        "instrumented_axes": samples,
        "max_instrumented_cost_over_bill": f"{max_ratio:.4f}",
        "m1_ratio_ell14_to_32": tight,
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
