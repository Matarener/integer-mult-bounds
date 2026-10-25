"""Shared F2[D_{2p}] three-register inverse-rotation model for odd primes p."""
from __future__ import annotations

from itertools import product

NREG = 3
MASK = (1 << NREG) - 1
IDENTITY_MATRIX = sum(1 << (i * NREG + i) for i in range(NREG))

# Odd primes through 31, including D10's p=5 as cross-check.
CERTIFIED_PRIMES = (5, 7, 11, 13, 17, 19, 23, 29, 31)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def group_mul(p: int, a: int, b: int) -> int:
    """Encode D_{2p} elements r^k s^e by 2*k+e; r=st, s^2=t^2=1, (st)^p=1."""
    ka, ea = divmod(a, 2)
    kb, eb = divmod(b, 2)
    k = (ka + (-kb if ea else kb)) % p
    return 2 * k + (ea ^ eb)


def labels_for(p: int) -> tuple[int, int, int, int, int]:
    """Return (E, S, T, R, R_INV) in the 2k+e encoding."""
    e = 0
    s = 1
    t = 2 * (p - 1) + 1
    r = 2
    r_inv = 2 * (p - 1)
    return e, s, t, r, r_inv


def mat_mul(a: int, b: int) -> int:
    out = 0
    for i in range(NREG):
        row = (a >> (i * NREG)) & MASK
        for j in range(NREG):
            col = sum(((b >> (k * NREG + j)) & 1) << k for k in range(NREG))
            if (row & col).bit_count() & 1:
                out |= 1 << (i * NREG + j)
    return out


# 3x3 matrices over F2 pack into 9 bits; table is shared across all primes.
MATMUL = [[mat_mul(a, b) for b in range(1 << 9)] for a in range(1 << 9)]


def mat_rank(a: int) -> int:
    rows = [(a >> (i * NREG)) & MASK for i in range(NREG)]
    rank = 0
    for col in range(NREG):
        pivot = next((i for i in range(rank, NREG) if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(NREG):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def rank_one_idempotents() -> list[int]:
    vals = set()
    for x in range(1, 1 << NREG):
        for y in range(1, 1 << NREG):
            if (x & y).bit_count() & 1:
                n = sum(
                    (((x >> i) & 1) * ((y >> j) & 1)) << (i * NREG + j)
                    for i in range(NREG)
                    for j in range(NREG)
                )
                vals.add(n)
    result = sorted(vals)
    need(len(result) == 28, f"expected 28 projectors, got {len(result)}")
    need(all(MATMUL[n][n] == n and mat_rank(n) == 1 for n in result),
         "projector idempotent/rank failure")
    return result


PROJECTORS = rank_one_idempotents()


def build_group(p: int):
    need(type(p) is int and p >= 3 and p % 2 == 1 and is_prime(p),
         f"odd prime required, got {p}")
    ngroup = 2 * p
    table = [[group_mul(p, a, b) for b in range(ngroup)] for a in range(ngroup)]
    e, s, t, r, r_inv = labels_for(p)
    need(all(table[e][g] == g and table[g][e] == g for g in range(ngroup)),
         f"p={p}: identity")
    need(table[s][s] == e and table[t][t] == e, f"p={p}: reflections involutions")
    need(table[s][t] == r and table[t][s] == r_inv, f"p={p}: st/ts")
    # (st)^p = e
    acc = e
    for _ in range(p):
        acc = table[acc][r]
    need(acc == e, f"p={p}: r^p != e")
    need(table[r][r_inv] == e and table[r_inv][r] == e, f"p={p}: r inverse")
    # associativity sample: full check for small p, random-style full for all certified
    need(all(table[table[a][b]][c] == table[a][table[b][c]]
             for a, b, c in product(range(ngroup), repeat=3)),
         f"p={p}: associativity")
    return {
        "p": p,
        "ngroup": ngroup,
        "table": table,
        "e": e,
        "s": s,
        "t": t,
        "r": r,
        "r_inv": r_inv,
    }


def unit_state(ngroup: int, e: int) -> tuple[int, ...]:
    return tuple(IDENTITY_MATRIX if g == e else 0 for g in range(ngroup))


def target_state(ngroup: int, e: int, r: int, r_inv: int) -> tuple[int, ...]:
    coeffs = [0] * ngroup
    coeffs[r] = 1 << 0
    coeffs[r_inv] = 1 << (1 * NREG + 1)
    coeffs[e] = 1 << (2 * NREG + 2)
    return tuple(coeffs)


def right_multiply_call(table, state: tuple[int, ...], label: int, n: int) -> tuple[int, ...]:
    id_part = IDENTITY_MATRIX ^ n
    out = [0] * len(state)
    for g, coeff in enumerate(state):
        if coeff:
            out[g] ^= MATMUL[coeff][id_part]
            out[table[g][label]] ^= MATMUL[coeff][n]
    return tuple(out)


def word_state(group, labels: tuple[int, ...], projectors: tuple[int, ...]) -> tuple[int, ...]:
    state = unit_state(group["ngroup"], group["e"])
    for label, n in zip(labels, projectors):
        state = right_multiply_call(group["table"], state, label, n)
    return state


def direct_four_call(group):
    e00 = 1 << 0
    e11 = 1 << 4
    labels = (group["s"], group["t"], group["t"], group["s"])
    projectors = (e00, e00, e11, e11)
    need(all(n in PROJECTORS for n in projectors), "direct projectors not rank-one")
    return labels, projectors


EXPECTED_COUNTS = {0: 1, 1: 56, 2: 3136, 3: 175616}
TOTAL_CANDIDATES = 178809
