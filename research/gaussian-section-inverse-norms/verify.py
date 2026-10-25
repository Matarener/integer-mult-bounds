#!/usr/bin/env python3
"""Certified induced 1-norm and infinity norm of one normalized Gaussian Schur-section inverse.

The section is #4319's: p = 19, beta0 = -1/2, bandwidth 2, t_i = i on the path 0..9, interiors
3..6 eliminated, survivors 0,1,2,7,8,9, each Schur row divided by its diagonal. Entries are built
from GAUGEFREE-INTERIORS.md's original form N_{i,i+h} = exp(-a[(rho h + beta_i)^2 - beta_{i+h}^2]),
not the gauge form, and no Schur complement is formed: the quotient identity S^-1 = (A^-1)_KK gives
the inverse directly. Exact rationals throughout; one rigorous perturbation bound covers the entry
radii. Standard library only; no code from #4319.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/unconditional-batched-crt"
PINS = {
    "vendor/GAUGEFREE-INTERIORS.md": "d1423ac0ea0003521797209f4396e6981a66994bbee4f8b48026e5b95f8c5116",
    "INVERSE-CONDITIONING.md": "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a",
    "GAUSSIAN.md": "2f63c91c58f2d1cf31294812c75970ea390c61866a8da7ed700d4316a033a242",
}
PHRASES = {
    "vendor/GAUGEFREE-INTERIORS.md": ["N_{i,i+h} = exp(-a[(rho h + beta_i)^2 - beta_{i+h}^2]), a = pi alpha^2, beta_i = beta0 + theta t_i"],
    "INVERSE-CONDITIONING.md": ["||H^-1||_1 <= 1/delta + 2 b rho/delta^2,", "||M||_2^2 <= ||M||_1 ||M||_infinity"],
    "GAUSSIAN.md": ["theta=t/s-1 in [1/(4p^2),1/p^2], rho=1+theta", "alpha=ceil(sqrt((4/pi)log(16p)))"],
}
P, WIDTH, SIZE = 19, 2, 10
INTERIOR, KEEP = (3, 4, 5, 6), (0, 1, 2, 7, 8, 9)
GRID = Q(1, 10**90)           # entries are snapped outward to this grid


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def atan_inv(n, terms):
    """bounds of atan(1/n) from the alternating series"""
    s, x = Q(0), Q(1, n)
    for k in range(terms):
        s += (-1) ** k * x ** (2 * k + 1) / (2 * k + 1)
    tail = x ** (2 * terms + 1) / (2 * terms + 1)
    return (s, s + tail) if terms % 2 == 0 else (s - tail, s)


def pi_bounds():
    a, b = atan_inv(5, 70)
    c, d = atan_inv(239, 25)
    return 16 * a - 4 * d, 16 * b - 4 * c


def exp_pos(y):
    """bounds of exp(y), y >= 0: Taylor on y/2^k <= 1/2 with Lagrange remainder, then squaring"""
    k = 0
    while y / 2 ** k > Q(1, 2):
        k += 1
    z, s, term = y / 2 ** k, Q(0), Q(1)
    for i in range(60):
        s += term
        term = term * z / (i + 1)
    lo, hi = s, s + 2 * term
    for _ in range(k):
        lo, hi = lo * lo, hi * hi
        lo, hi = Q(lo.numerator * 10**95 // lo.denominator, 10**95), Q(-(-hi.numerator * 10**95 // hi.denominator), 10**95)
    return lo, hi


def snap(lo, hi):
    return (lo / GRID).__floor__() * GRID, (hi / GRID).__ceil__() * GRID


def entries(pi_lo, pi_hi, alpha=3):
    """dict (i, j) -> (lo, hi) for the 10x10 banded matrix"""
    theta = Q(1, 4 * P * P)
    rho, beta0 = 1 + theta, Q(-1, 2)
    out = {}
    for i in range(SIZE):
        for j in range(SIZE):
            h = j - i
            if abs(h) > WIDTH:
                continue
            if h == 0:
                out[i, j] = (Q(1), Q(1))
                continue
            bi, bj = beta0 + theta * i, beta0 + theta * j
            c = (rho * h + bi) ** 2 - bj ** 2
            need(c > 0, "every off-diagonal exponent is negative")
            # cross-check against the gauge form: log N = (a/1444)(-1445 h^2 + 1444 h + i^2 - j^2)
            need(c * 1444 == 1445 * h * h - 1444 * h - i * i + j * j, "original form equals gauge form")
            e_lo = exp_pos(alpha ** 2 * pi_lo * c)[0]
            e_hi = exp_pos(alpha ** 2 * pi_hi * c)[1]
            out[i, j] = snap(1 / e_hi, 1 / e_lo)
    return out


def inverse(m):
    n = len(m)
    w = [row[:] + [Q(int(r == c)) for c in range(n)] for r, row in enumerate(m)]
    for c in range(n):
        p = next(r for r in range(c, n) if w[r][c] != 0)
        w[c], w[p] = w[p], w[c]
        w[c] = [x / w[c][c] for x in w[c]]
        for r in range(n):
            if r != c and w[r][c] != 0:
                f = w[r][c]
                w[r] = [x - f * y for x, y in zip(w[r], w[c])]
    return [row[n:] for row in w]


def inf_norm(m):
    return max(sum(abs(x) for x in row) for row in m)


def perturbed(m_hat, radius_norm):
    """inverse of the midpoint and a bound on ||M^-1 - inverse||_inf for ||M - midpoint||_inf <= radius_norm"""
    x = inverse(m_hat)
    nx = inf_norm(x)
    need(nx * radius_norm < Q(1, 2), "perturbation is small")
    return x, nx * nx * radius_norm / (1 - nx * radius_norm)


def main():
    for name, sha in PINS.items():
        raw = (SRC / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == sha, f"pinned {name}")
        for phrase in PHRASES[name]:
            need(phrase in raw.decode(), f"{name}: {phrase}")

    pi_lo, pi_hi = pi_bounds()
    need(0 < pi_hi - pi_lo < Q(1, 10**95) and Q(314159, 10**5) < pi_lo < pi_hi < Q(314160, 10**5), "pi enclosure")
    # alpha = ceil(sqrt((4/pi) log(16p))) = 3  <=>  4 < (4/pi) log 304 <= 9  <=>  pi < log 304 <= 9 pi/4
    e_pi = exp_pos(pi_hi)[1]
    e_9pi4 = exp_pos(Q(9, 4) * pi_lo)[0]
    need(e_pi < 304 <= e_9pi4, "alpha = 3 at p = 19")

    ent = entries(pi_lo, pi_hi)
    mid = [[(ent[i, j][0] + ent[i, j][1]) / 2 if (i, j) in ent else Q(0) for j in range(SIZE)] for i in range(SIZE)]
    rad = max(e[1] - e[0] for e in ent.values()) / 2
    need(rad <= GRID, "entry radius within one grid step")
    # every row has at most 4 uncertain entries (the diagonal is exact)
    x_hat, eta = perturbed(mid, 4 * rad)

    # quotient identity: inverse of the Schur section onto KEEP is the KEEP block of A^-1
    y_hat = [[x_hat[i][j] for j in KEEP] for i in KEEP]
    s_hat, eta_s = perturbed(y_hat, 6 * eta)
    d_hat = [s_hat[k][k] for k in range(6)]
    need(all(d > Q(9, 10) for d in d_hat), "Schur diagonals near 1")
    # the true N^-1 = Y D with |Y - y_hat| <= eta and |D - d_hat| <= eta_s entrywise
    err = [[eta * (d_hat[j] + eta_s) + abs(y_hat[i][j]) * eta_s for j in range(6)] for i in range(6)]
    ninv = [[y_hat[i][j] * d_hat[j] for j in range(6)] for i in range(6)]
    rows = [sum(abs(x) for x in ninv[i]) for i in range(6)]
    cols = [sum(abs(ninv[i][j]) for i in range(6)) for j in range(6)]
    row_err = [sum(err[i]) for i in range(6)]
    col_err = [sum(err[i][j] for i in range(6)) for j in range(6)]
    tol = max(row_err + col_err)
    need(tol < Q(1, 10**40), "rigorous error below 1e-40")
    inf_lo, inf_hi = max(rows) - tol, max(rows) + tol
    one_lo, one_hi = max(cols) - tol, max(cols) + tol

    # #4319's claim
    need(Q(18, 5) < inf_lo and inf_hi < Q(361, 100), "#4319: 18/5 < ||N^-1||_inf < 361/100")
    # #4317's Neumann ceilings at the displayed-expression gap: 27, 3938, and 2-norm below 321
    need(inf_hi < 27 and one_hi < 3938, "true norms below #4317's ceilings")
    two_sq_hi = inf_hi * one_hi
    need(two_sq_hi < 321 ** 2, "sqrt(||.||_1 ||.||_inf) below 321")
    # lower bound for the 2-norm: the largest column Euclidean norm
    col2 = max(sum(ninv[i][j] ** 2 for i in range(6)) for j in range(6))
    two_sq_lo = col2 - Q(1, 10**30)

    # Control: the principal restriction A_KK (no interior elimination, so no 2 -> 7 fill) misses
    # #4319's bracket, so the bracket does see the Schur complement.
    restricted = inf_norm(inverse([[mid[i][j] for j in KEEP] for i in KEEP]))
    need(restricted < Q(3), "control: principal restriction has infinity norm below 3")

    # the unsectioned 10-vertex path (diagonal 1 already): its 1-norm is also below its infinity norm
    full_inf = inf_norm(x_hat)
    full_one = max(sum(abs(x_hat[i][j]) for i in range(SIZE)) for j in range(SIZE))
    need(full_one + 2 * SIZE * eta < full_inf - 2 * SIZE * eta, "full path: ||A^-1||_1 < ||A^-1||_inf")

    argmax_col = KEEP[max(range(6), key=lambda j: cols[j])]
    argmax_row = KEEP[max(range(6), key=lambda i: rows[i])]
    print(json.dumps({
        "status": "PASS_GAUSSIAN_SECTION_INVERSE_NORMS",
        "inf_norm": [f"{float(inf_lo):.12f}", f"{float(inf_hi):.12f}"],
        "inf_argmax_row": argmax_row,
        "one_norm": [f"{float(one_lo):.12f}", f"{float(one_hi):.12f}"],
        "one_argmax_column": argmax_col,
        "two_norm": [f"{float(two_sq_lo) ** 0.5:.6f}", f"{float(two_sq_hi) ** 0.5:.6f}"],
        "neumann_ceilings_4317": {"inf": 27, "one": 3938, "two": 321},
        "full_path_inf_one": [f"{float(full_inf):.6f}", f"{float(full_one):.6f}"],
        "rigorous_error": f"{float(tol):.1e}",
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
