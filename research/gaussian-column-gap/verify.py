#!/usr/bin/env python3
"""Column gap of the narrow Gaussian kernel, and certified inverse norms on longer paths.

Part A checks the exact column identity behind the README lemma: inside one constant-phase run,
(rho h + beta_j - theta h)^2 - beta_j^2 = h^2 + 2 beta_j h, so column j of N depends only on
beta_j. Part B certifies the resulting column-gap bound at p = 19 (alpha = 3, theta = 1/(4p^2)).
Part C certifies ||A^-1||_1 and ||A^-1||_inf, and the same norms for the normalized 3+3 Schur
section, for every path length 10..40 (plus 100) at both ends of the phase run, against
1/delta_col.

Exact rationals throughout. Approximate inverses come from float64 and are certified by an exact
rational residual. Standard library only; no code imported from other packages.
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
    "vendor/GAUGEFREE-INTERIORS.md": [
        "N_{i,i+h} = exp(-a[(rho h + beta_i)^2 - beta_{i+h}^2]), a = pi alpha^2, beta_i = beta0 + theta t_i",
        "With beta_{i+h} = beta_i + theta h, rho = 1+theta:",
        "Phase cell: beta_i = theta i - c in [-1/2,1/2)",
    ],
    "INVERSE-CONDITIONING.md": ["||H^-1||_1 <= 1/delta + 2 b rho/delta^2,", "||M||_2^2 <= ||M||_1 ||M||_infinity"],
    "GAUSSIAN.md": [
        "theta=t/s-1 in [1/(4p^2),1/p^2], rho=1+theta",
        "||N-I||_infinity <= exp(-2a theta)+5exp(-2a).",
        "does not assume that a row norm bounds a column norm",
    ],
}
P, WIDTH = 19, 2
THETA = Q(1, 4 * P * P)
RHO = 1 + THETA
LENGTHS = list(range(10, 41)) + [100]
GRID = Q(1, 10**40)          # entries are snapped outward to this grid


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
    a, b = atan_inv(5, 40)
    c, d = atan_inv(239, 15)
    return 16 * a - 4 * d, 16 * b - 4 * c


def floor_grid(x, g):
    return (x / g).__floor__() * g


def ceil_grid(x, g):
    return (x / g).__ceil__() * g


def exp_pos(y):
    """bounds of exp(y), y >= 0: Taylor on y/2^k <= 1/2 with remainder, then outward squaring"""
    k = 0
    while y / 2 ** k > Q(1, 2):
        k += 1
    z, s, term = y / 2 ** k, Q(0), Q(1)
    for i in range(40):
        s += term
        term = term * z / (i + 1)
    lo, hi = s, s + 2 * term
    g = Q(1, 10**60)
    for _ in range(k):
        lo, hi = floor_grid(lo * lo, g), ceil_grid(hi * hi, g)
    return lo, hi


def exp_neg(x_lo, x_hi):
    """bounds of exp(-x) for 0 <= x_lo <= x <= x_hi"""
    return 1 / exp_pos(x_hi)[1], 1 / exp_pos(x_lo)[0]


def gaussian_matrix(n, beta0, a_lo, a_hi):
    """interval entries {(i, j): (lo, hi)} of the banded normalized narrow matrix, beta_i = beta0 + theta i"""
    out = {}
    for i in range(n):
        for h in range(-WIDTH, WIDTH + 1):
            j = i + h
            if not 0 <= j < n:
                continue
            if h == 0:
                out[i, j] = (Q(1), Q(1))
                continue
            bi, bj = beta0 + THETA * i, beta0 + THETA * j
            need(-Q(1, 2) <= bi < Q(1, 2) and -Q(1, 2) <= bj < Q(1, 2), "inside one phase run")
            c = (RHO * h + bi) ** 2 - bj ** 2                       # original form
            need(c == (1 + 2 * THETA) * h * h + 2 * bi * h, "row form")
            need(c == h * h + 2 * bj * h, "column form: depends on beta_j only")
            need(c > 0, "off-diagonal exponent is negative")
            lo, hi = exp_neg(a_lo * c, a_hi * c)
            out[i, j] = (floor_grid(lo, GRID), ceil_grid(hi, GRID))
    return out


def dense(n, ent, pick):
    m = [[Q(0)] * n for _ in range(n)]
    for (i, j), e in ent.items():
        m[i][j] = pick(e)
    return m


def float_inverse(m):
    """float64 Gauss-Jordan with partial pivoting; only an approximation, certified afterwards"""
    n = len(m)
    w = [[float(x) for x in row] + [float(r == c) for c in range(n)] for r, row in enumerate(m)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(w[r][c]))
        w[c], w[p] = w[p], w[c]
        piv = w[c][c]
        w[c] = [x / piv for x in w[c]]
        for r in range(n):
            if r != c and w[r][c] != 0.0:
                f = w[r][c]
                w[r] = [x - f * y for x, y in zip(w[r], w[c])]
    return [[Q(x) for x in row[n:]] for row in w]


def exact_inverse(m):
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


def one_norm(m):
    return max(sum(abs(m[i][j]) for i in range(len(m))) for j in range(len(m[0])))


def certified_inverse(n, ent):
    """approximate inverse X of the midpoint and a bound eps >= max |A^-1 - X| entrywise, with norm errors"""
    mid = dense(n, ent, lambda e: (e[0] + e[1]) / 2)
    rad = max(e[1] - e[0] for e in ent.values()) / 2
    x = float_inverse(mid)
    band = {i: [(j, mid[i][j]) for j in range(max(0, i - WIDTH), min(n, i + WIDTH + 1))] for i in range(n)}
    # R = I - X M (left residual, for the infinity norm) and R' = I - M X (right residual, for the 1-norm)
    left = [[int(i == k) - sum(x[i][j] * v for (j, v) in [(j, mid[j][k]) for j in range(max(0, k - WIDTH), min(n, k + WIDTH + 1))])
             for k in range(n)] for i in range(n)]
    right = [[int(i == k) - sum(v * x[j][k] for (j, v) in band[i]) for k in range(n)] for i in range(n)]
    dm = (2 * WIDTH) * rad                  # ||A - mid|| in both norms (diagonal exact)
    nx_inf, nx_one = inf_norm(x), one_norm(x)
    r_inf = inf_norm(left) + nx_inf * dm
    r_one = one_norm(right) + nx_one * dm
    need(r_inf < Q(1, 2) and r_one < Q(1, 2), "residuals small")
    # A^-1 = (I - R)^-1 X with ||R|| <= r  =>  ||A^-1 - X|| <= r ||X|| / (1 - r)
    e_inf = r_inf * nx_inf / (1 - r_inf)
    e_one = r_one * nx_one / (1 - r_one)
    return x, min(e_inf, e_one), e_inf, e_one


def perturbed(m_hat, radius_norm):
    x = exact_inverse(m_hat)
    nx = inf_norm(x)
    need(nx * radius_norm < Q(1, 2), "perturbation is small")
    return x, nx * nx * radius_norm / (1 - nx * radius_norm)


def section_norms(x, eps, keep):
    """normalized Schur section onto keep: N^-1 = Y D, Y = (A^-1)_KK, D = diag(Y^-1)"""
    k = len(keep)
    y = [[x[i][j] for j in keep] for i in keep]
    s_hat, eta_s = perturbed(y, k * eps)
    d = [s_hat[j][j] for j in range(k)]
    need(all(v > Q(9, 10) for v in d), "Schur diagonals near 1")
    err = [[eps * (d[j] + eta_s) + abs(y[i][j]) * eta_s for j in range(k)] for i in range(k)]
    ninv = [[y[i][j] * d[j] for j in range(k)] for i in range(k)]
    tol = max([sum(r) for r in err] + [sum(err[i][j] for i in range(k)) for j in range(k)])
    unnorm_one = one_norm(y) + k * eps
    return inf_norm(ninv), one_norm(ninv), tol, unnorm_one


def column_gap_bound(a_lo, a_hi):
    """certified lower bound for 1 - [e^{-2a theta} + e^{-2a(1-theta)} + 2e^{-2a}/(1-e^{-4a})]"""
    t1 = exp_neg(2 * THETA * a_lo, 2 * THETA * a_hi)[1]
    t2 = exp_neg(2 * (1 - THETA) * a_lo, 2 * (1 - THETA) * a_hi)[1]
    t3 = exp_neg(2 * a_lo, 2 * a_hi)[1]
    t4 = exp_neg(4 * a_lo, 4 * a_hi)[1]
    return 1 - t1 - t2 - 2 * t3 / (1 - t4), t1


def main():
    for name, sha in PINS.items():
        raw = (SRC / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == sha, f"pinned {name}")
        for phrase in PHRASES[name]:
            need(phrase in raw.decode(), f"{name}: {phrase}")

    # Part A: the column identity is a polynomial identity in (beta_j, theta, h); check it on a rational grid
    for bj in [Q(k, 37) for k in range(-18, 19)]:
        for th in [Q(1, 1444), Q(1, 361), Q(2, 7)]:
            for h in range(-6, 7):
                rho, bi = 1 + th, bj - th * h
                need((rho * h + bi) ** 2 - bj ** 2 == h * h + 2 * bj * h, "column identity")
                need((rho * h + bi) ** 2 - (bi + th * h) ** 2 == (1 + 2 * th) * h * h + 2 * bi * h, "row identity")

    pi_lo, pi_hi = pi_bounds()
    need(0 < pi_hi - pi_lo < Q(1, 10**50) and Q(314159, 10**5) < pi_lo, "pi enclosure")
    e_pi, e_9pi4 = exp_pos(pi_hi)[1], exp_pos(Q(9, 4) * pi_lo)[0]
    need(e_pi < 304 <= e_9pi4, "alpha = 3 at p = 19")
    a_lo, a_hi = 9 * pi_lo, 9 * pi_hi

    # Part B: the column-gap bound at p = 19 and the INVERSE-CONDITIONING ceilings it replaces
    dcol, first = column_gap_bound(a_lo, a_hi)
    need(Q(38, 1000) < dcol < Q(39, 1000), "delta_col in (0.038, 0.039)")
    need(dcol > Q(1, 16 * P * P), "delta_col above GAUSSIAN.md's 1/(16p^2)")
    lemma_one = 1 / dcol + 2 * WIDTH * (1 - dcol) / dcol ** 2

    rows = []
    worst_ratio = Q(0)
    for n in LENGTHS:
        for label, beta0 in (("start", -Q(1, 2)), ("end", Q(1, 2) - THETA * n)):
            ent = gaussian_matrix(n, beta0, a_lo, a_hi)
            # actual column and row gaps of this banded matrix (upper bounds of |entries|)
            col = max(sum(ent[i, j][1] for i in range(n) if (i, j) in ent and i != j) for j in range(n))
            row = max(sum(ent[i, j][1] for j in range(n) if (i, j) in ent and i != j) for i in range(n))
            need(col <= 1 - dcol, "column sums obey the column-gap bound")
            x, eps, e_inf, e_one = certified_inverse(n, ent)
            need(e_inf < Q(1, 10**9) and e_one < Q(1, 10**9), "certified inverse error below 1e-9")
            f_inf, f_one = inf_norm(x), one_norm(x)
            f_inf_lo, f_one_hi = f_inf - e_inf, f_one + e_one
            need(f_one_hi <= 1 / dcol, "full path: ||A^-1||_1 <= 1/delta_col")
            need(f_one_hi < f_inf_lo, "full path: ||A^-1||_1 < ||A^-1||_inf")
            keep = (0, 1, 2, n - 3, n - 2, n - 1)
            s_inf, s_one, tol, s_unnorm = section_norms(x, eps, keep)
            need(tol < Q(1, 10**8), "section error below 1e-8")
            need(s_unnorm <= 1 / dcol, "unnormalized Schur inverse: ||S^-1||_1 <= 1/delta_col")
            need(s_one + tol < s_inf - tol, "3+3 section: ||N^-1||_1 < ||N^-1||_inf")
            worst_ratio = max(worst_ratio, f_one_hi * dcol)
            rows.append({
                "n": n, "end": label,
                "full_inf": f"{float(f_inf):.6f}", "full_one": f"{float(f_one):.6f}",
                "section_inf": f"{float(s_inf):.6f}", "section_one": f"{float(s_one):.6f}",
                "row_gap": f"{float(1 - row):.6f}", "col_gap": f"{float(1 - col):.6f}",
            })

    # control: without the phase-run premise the column form fails (a cut row reads beta_{i+h} - 1)
    bi, h = Q(1, 2) - THETA, 1
    bj_cut = bi + THETA * h - 1
    need((RHO * h + bi) ** 2 - bj_cut ** 2 != h * h + 2 * bj_cut * h, "control: identity needs one phase run")

    table = {(r["n"], r["end"]): r for r in rows}
    print(json.dumps({
        "status": "PASS_GAUSSIAN_COLUMN_GAP",
        "delta_col_lower": f"{float(dcol):.10f}",
        "one_over_delta_col": f"{float(1 / dcol):.6f}",
        "first_neighbour_term": f"{float(first):.10f}",
        "inverse_conditioning_one_norm_ceiling_at_delta_col": f"{float(lemma_one):.2f}",
        "lengths": [LENGTHS[0], LENGTHS[-3], LENGTHS[-2], LENGTHS[-1]],
        "placements": 2 * len(LENGTHS),
        "max_full_one_norm_times_delta_col": f"{float(worst_ratio):.6f}",
        "sample": [table[10, "start"], table[40, "start"], table[100, "start"], table[40, "end"], table[100, "end"]],
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
