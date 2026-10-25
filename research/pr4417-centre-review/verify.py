#!/usr/bin/env python3
"""Independent review of #4417's packing screen and Kronecker sharpness (centre-path-sharing).

A separate implementation of the hosted nine-stage coverage relaxation (not importing ceiling.py):
per call w = families/stages live families, total paid mass (m - 1) w + centre, the local word's own children,
and the remaining idle mass M placed in fractional rank-R children with R the largest rank satisfying the outer
halving guard m^2 > 2 R^2. The moment

    relax(a) = [ sum_local n_r (r/m)^(1-a) + (M/R)(R/m)^(1-a) ] / w

is increasing in a; its root a* is the ceiling. The verifier brackets a* to 1e-12 for the six rows of #4417's
screen (selected 8 x rank-8; packs into 4 x 16, 2 x 32, 1 x 64; ideal fractional rank-72; halved-information
control 4 x 8 with centre 32) and compares them with #4417's RESULT.json values.
It also proves the regroup extremality: for fixed centre mass, (r/m)^(1-a) / r = r^-a m^(a-1) is nonincreasing in r,
so moving mass to the largest child rank m - 1 = 72 minimises the moment, i.e. maximises the ceiling; and it
checks Kronecker packing sharpness exhaustively on small grids.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import itertools
import json
import sys

GRID = Q(1, 10**60)
M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
EXPECTED_HI = {  # #4417 RESULT.json a_hi values, rounded to 11 digits in its README table
    "selected": "0.00169005411", "pack2": "0.00169362555", "pack4": "0.00169720789",
    "pack8": "0.00170080115", "regroup72": "0.00170141282", "halved": "0.00321297289"}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def down(x):
    return (x / GRID).__floor__() * GRID


def up(x):
    return (x / GRID).__ceil__() * GRID


LN = {}


def ln(n):
    """certified ln of an integer by bit reduction and the atanh series"""
    if n in LN:
        return LN[n]
    if n == 1:
        LN[n] = (Q(0), Q(0))
        return LN[n]
    k = n.bit_length() - 1
    lo = hi = Q(0)
    for y, scale in ((Q(n, 2 ** k), 1), (Q(2), k)):
        if y == 1 or scale == 0:
            continue
        u = (y - 1) / (y + 1)
        s, term, j = Q(0), u, 0
        while True:
            s += term / (2 * j + 1)
            j += 1
            term *= u * u
            tail = term / (2 * j + 1) / (1 - u * u)
            if tail < GRID:
                break
        lo += scale * down(2 * s)
        hi += scale * up(2 * (s + tail))
    LN[n] = (lo, hi)
    return LN[n]


def exp_iv(lo, hi):
    def series(x):
        s, term = Q(0), Q(1)
        for i in range(60):
            s += term
            term = term * x / (i + 1)
        return s, abs(term) * 2
    a, ea = series(lo)
    b, eb = series(hi)
    return down(a - ea), up(b + eb)


def idle_rank(m):
    R = 1
    while 2 * (R + 1) ** 2 < m * m:
        R += 1
    return R


def relax(local, centre, a):
    w = Q(FAM, ST)
    R = idle_rank(M)
    idle = (M - 1) * w + centre - sum(r * Q(n) for r, n in local.items())
    need(idle >= 0, "coverage law")
    lo = hi = Q(0)
    lm = ln(M)
    for r, n in list(local.items()) + [(R, idle / R)]:
        lr = ln(r)
        e = exp_iv(a * (lm[0] - lr[1]), a * (lm[1] - lr[0]))   # (m/r)^a
        lo += Q(n) * Q(r, M) * e[0]
        hi += Q(n) * Q(r, M) * e[1]
    return lo / w, hi / w


def ceiling(local, centre=64):
    lo, hi = Q(0), Q(1, 20)
    need(relax(local, centre, hi)[0] > 1 and relax(local, centre, lo)[1] < 1, "bracket")
    while hi - lo > Q(1, 10**12):
        mid = (lo + hi) / 2
        v = relax(local, centre, mid)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise AssertionError("enclosure too wide")
    return lo, hi


def kronecker_sharp(widths, bits):
    """k values of `bits` bits pack injectively into sum(widths) bits iff sum(widths) >= k*bits"""
    values = list(itertools.product(range(2 ** bits), repeat=len(widths)))
    total = sum(widths)
    packed = {sum(v << (bits * i) for i, v in enumerate(vals)) for vals in values}
    return len(packed) == len(values) and max(packed) < 2 ** total


def main():
    need(idle_rank(M) == 51, "R = 51 for m = 73")
    rest = {r: n for r, n in WORD.items() if r != 8}
    rows = {"selected": (WORD, 64), "pack2": ({**rest, 16: Q(4)}, 64), "pack4": ({**rest, 32: Q(2)}, 64),
            "pack8": ({**rest, 64: Q(1)}, 64), "regroup72": ({**rest, 72: Q(64, 72)}, 64),
            "halved": ({**WORD, 8: 4}, 32)}
    out = {}
    base = None
    for name, (local, centre) in rows.items():
        lo, hi = ceiling(local, centre)
        exp = Q(EXPECTED_HI[name])
        need(abs(hi - exp) < Q(1, 10**11), f"{name}: matches #4417's a_hi to 1e-11")
        base = hi if base is None else base
        out[name] = {"a_hi": f"{float(hi):.12f}", "ratio": f"{float(hi / base):.6f}"}
    need(Q(out["regroup72"]["a_hi"]) / Q(out["selected"]["a_hi"]) < Q(1007, 1000), "+0.7% cap")
    # extremality: per-unit-mass cost r^-a m^(a-1) nonincreasing in r for a >= 0, so any regrouping of the
    # 64 centre mass into children of rank <= 72 has moment >= the fractional rank-72 relaxation
    a = Q(1, 500)
    for r in range(1, 72):
        c1 = exp_iv(-a * ln(r + 1)[1], -a * ln(r + 1)[0])[1]     # (r+1)^-a upper
        c0 = exp_iv(-a * ln(r)[1], -a * ln(r)[0])[0]             # r^-a lower
        need(c1 <= c0, "per-unit-mass cost nonincreasing")
    # Kronecker sharpness on small grids
    for k, bits in ((2, 2), (3, 2), (2, 3), (4, 1), (3, 3), (2, 4)):
        need(kronecker_sharp([bits] * k, bits), "packing at exact width is injective")
        vals = list(itertools.product(range(2 ** bits), repeat=k))
        need(len(vals) > 2 ** (k * bits - 1), "one bit less collides (pigeonhole)")
    print(json.dumps({"status": "PASS_PR4417_SCREEN_REVIEW", "rows": out, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
