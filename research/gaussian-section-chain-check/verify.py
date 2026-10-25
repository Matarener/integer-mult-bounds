#!/usr/bin/env python3
"""One independent check of jwr404's p = 19 normalized-section chain (#4354, #4355, #4361, #4362, #4364 and the
two-power PRs #4366-#4401), plus the sharp two-power threshold.

The section (as in #4319 and my #4336): p = 19, beta0 = -1/2, bandwidth 2, t_i = i on 0..9, interiors 3..6
eliminated, survivors 0,1,2,7,8,9, rows divided by their diagonals: H. Its inverse is the survivor block of
A^-1 times diag(S) (quotient identity); H is the exact inverse of that, with one perturbation bound. HALO's
polynomial inverse P = p^-20 sum_{j<J} Q^j H*, Q = I - p^-20 H*H, J = ceil(p^42), has P - H^-1 = -Q^J H^-1.
Exact rationals throughout; entries from GAUGEFREE-INTERIORS.md's original form. Standard library only.
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



PINS["HALO.md"] = "a2adcf18614983e9255def6d3f5e59be0018a392e418d65e94323722838289cc"
PHRASES["HALO.md"] = ["Put Q_i=I-p^-20 H_i^* H_i and J=ceil(p^42)."]


def main():
    for name, sha in PINS.items():
        raw = (SRC / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == sha, f"pinned {name}")
        for phrase in PHRASES[name]:
            need(phrase in raw.decode(), f"{name}: {phrase}")
    pi_lo, pi_hi = pi_bounds()
    need(exp_pos(pi_hi)[1] < 304 <= exp_pos(Q(9, 4) * pi_lo)[0], "alpha = 3 at p = 19")
    ent = entries(pi_lo, pi_hi)
    mid = [[(ent[i, j][0] + ent[i, j][1]) / 2 if (i, j) in ent else Q(0) for j in range(SIZE)] for i in range(SIZE)]
    rad = max(e[1] - e[0] for e in ent.values()) / 2
    x_hat, eta = perturbed(mid, 4 * rad)
    y_hat = [[x_hat[i][j] for j in KEEP] for i in KEEP]
    s_hat, eta_s = perturbed(y_hat, 6 * eta)
    d_hat = [s_hat[k][k] for k in range(6)]
    err = [[eta * (d_hat[j] + eta_s) + abs(y_hat[i][j]) * eta_s for j in range(6)] for i in range(6)]
    ninv = [[y_hat[i][j] * d_hat[j] for j in range(6)] for i in range(6)]
    e_inv = max(max(sum(err[i]) for i in range(6)), max(sum(err[i][j] for i in range(6)) for j in range(6)))
    need(e_inv < Q(1, 10**40), "inverse error below 1e-40")
    inv_inf = max(sum(abs(x) for x in r) for r in ninv)
    inv_one = max(sum(abs(ninv[i][j]) for i in range(6)) for j in range(6))
    # H itself: exact inverse of the midpoint inverse, with the same perturbation lemma
    h_hat, eta_h = perturbed(ninv, 6 * e_inv)
    need(eta_h < Q(1, 10**35), "H error below 1e-35")
    h_rows = [sum(abs(x) for x in r) + 6 * eta_h for r in h_hat]
    h_cols = [sum(abs(h_hat[i][j]) for i in range(6)) + 6 * eta_h for j in range(6)]
    need(all(abs(h_hat[k][k] - 1) < Q(1, 10**30) for k in range(6)), "H has unit diagonal")

    out = {}
    # #4354: inverse 1-norm in (281/100, 282/100)
    need(Q(281, 100) < inv_one - e_inv and inv_one + e_inv < Q(282, 100), "#4354 inverse 1-norm in (2.81, 2.82)")
    # #4361: every absolute row and column sum of H below 1226/625, so ||H||_2 < 1226/625
    need(max(h_rows + h_cols) < Q(1226, 625), "#4361 row and column sums of H below 1226/625")
    h2_sq = max(h_rows) * max(h_cols)
    need(h2_sq < Q(1226, 625) ** 2 and Q(1226, 625) < 2 < 19 ** 10, "#4361 ||H||_2 < 1226/625 < 2 < 19^10")
    # #4355: ||H^-1||_2^2 <= ||.||_1 ||.||_inf < (319/100)^2; the round ceilings 2.82 * 3.61 would not suffice
    inv2_sq = (inv_one + e_inv) * (inv_inf + e_inv)
    need(inv2_sq < Q(319, 100) ** 2 and 319 ** 2 < 101802 < 320 ** 2, "#4355 ||H^-1||_2 < 319/100")
    # #4362: eigenvalues of Q in (0, 1 - p^-40)
    p = 19
    need(Q(1, p ** 20) * Q(1226, 625) ** 2 < 1 and Q(1, p ** 20) * Q(100, 319) ** 2 > Q(1, p ** 40), "#4362 spectrum of Q inside (0, 1 - p^-40)")
    # #4364: (1 - 19^-40)^(19^42) < exp(-361), since x N = 361 for x = 19^-40, N = 19^42, and ln(1 - x) < -x
    need(Q(1, p ** 40) * p ** 42 == 361, "#4364 x N = 361")
    # the two-power chain: (319/100) e^-361 < 2^-k exactly when e^361 > (319/100) 2^k
    e_lo, e_hi = exp_pos(Q(361))
    need(e_hi / e_lo - 1 < Q(1, 10**60), "e^361 enclosed to 60 digits")
    below = lambda k: e_lo > Q(319, 100) * 2 ** k        # proves (319/100) e^-361 < 2^-k
    not_below = lambda k: e_hi < Q(319, 100) * 2 ** k     # proves it is not
    chain = {4366 + i: 19 * (i + 1) for i in range(4)}
    chain[4374] = 95
    chain.update({4379 + i: 19 * (6 + i) for i in range(22)})
    need(sorted(chain.values()) == [19 * c for c in range(1, 28)] and len(chain) == 27, "27 two-power PRs, C = 1..27")
    need(all(below(k) for k in chain.values()), "every #4366-#4400 claim (319/100) e^-361 < 2^-19C holds")
    need(not_below(532), "#4401: not below 2^-532")
    need(below(519) and not_below(520), "sharp threshold: below 2^-519, not below 2^-520")
    out = {"inverse_one_norm": f"{float(inv_one):.10f}", "inverse_inf_norm": f"{float(inv_inf):.10f}",
           "inverse_two_norm_upper": f"{float(inv2_sq) ** 0.5:.6f}", "H_max_row_col_sum": f"{float(max(h_rows + h_cols)):.10f}",
           "H_two_norm_upper": f"{float(h2_sq) ** 0.5:.6f}", "two_power_claims_checked": len(chain) + 1,
           "sharp_two_power_exponent": 519}
    print(json.dumps({"status": "PASS_GAUSSIAN_SECTION_CHAIN_CHECK", **out, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
