#!/usr/bin/env python3
"""Independent check of #4416's paid-completion tensor bound and arithmetic (kappa = 0.00268647).

Inputs are #4416's printed p7 invoice and parameters; nothing is imported from #4416.
Part A  invoice totals; certified raw moments T_tau, P_tau at C_test = 0.00268648 and the three ratios
        alpha = P_tau/T_tau, gamma = P_1/(c^C T_tau) (c = 10), delta = B b/(c^C T_tau) (b = 11); the p7 mixed
        root bracketed to 1e-12.
Part B  alpha^v + 2 gamma^v + 2 delta^v < 1 at v = 6240, both by #4416's Bernoulli route and by direct certified
        powers; the least v for these (b, c) by the direct bound.
Part C  #4416's rational H0, H1 reproduced exactly; the same compiler induction with certified -log2(eta),
        the exact exit constant log2(r_max m^h) and the best h = 1 - theta_bar admissible with an integer
        comparison gives a smaller sufficient rank.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
import sys

GRID = Q(1, 10**50)
TARGETS = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
PAID = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
C_TEST, KAPPA, V, B_FLOOR, C_CUT = Q("0.00268648"), Q("0.00268647"), 6240, 11, 10


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def down(x):
    return (x / GRID).__floor__() * GRID


def up(x):
    return (x / GRID).__ceil__() * GRID


def ln_bounds(n):
    """certified ln n for integer n >= 1 (reduction to [1, 2) and the atanh series)"""
    if n == 1:
        return Q(0), Q(0)
    k = n.bit_length() - 1
    y = Q(n, 2 ** k)
    out = [Q(0), Q(0)]
    for part, scale in ((y, 1), (Q(2), k)):
        if part == 1 or scale == 0:
            continue
        u = (part - 1) / (part + 1)
        s, term, j = Q(0), u, 0
        while True:
            s += term / (2 * j + 1)
            j += 1
            term *= u * u
            tail = term / (2 * j + 1) / (1 - u * u)
            if tail < GRID:
                break
        out[0] += scale * down(2 * s)
        out[1] += scale * up(2 * (s + tail))
    return out[0], out[1]


def exp_bounds(x_lo, x_hi):
    """certified exp on a small interval (|x| < 1)"""
    def series(x):
        s, term = Q(0), Q(1)
        for i in range(70):
            s += term
            term = term * x / (i + 1)
        return s, abs(term) * 2
    a, ea = series(x_lo)
    b, eb = series(x_hi)
    return down(a - ea), up(b + eb)


LN = {}


def ln(n):
    if n not in LN:
        LN[n] = ln_bounds(n)
    return LN[n]


def moment(hist, C):
    """bounds of sum count * k^(1-C)"""
    lo = hi = Q(0)
    for k, w in hist.items():
        e = exp_bounds(-C * ln(k)[1], -C * ln(k)[0])
        lo, hi = lo + w * k * e[0], hi + w * k * e[1]
    return lo, hi


def ratios(C):
    T = moment(TARGETS, C)
    Pm = moment(PAID, C)
    cC = exp_bounds(C * ln(C_CUT)[0], C * ln(C_CUT)[1])
    B = sum(TARGETS.values())
    P1 = sum(k * w for k, w in PAID.items())
    alpha = (Pm[0] / T[1], Pm[1] / T[0])
    gamma = (P1 / (cC[1] * T[1]), P1 / (cC[0] * T[0]))
    delta = (B * B_FLOOR / (cC[1] * T[1]), B * B_FLOOR / (cC[0] * T[0]))
    return alpha, gamma, delta


def pow_upper(x, v):
    """certified upper bound of x^v for 0 < x < 1 rational: exp(v ln x) with ln x <= -(1-x) - (1-x)^2/2"""
    y = 1 - x
    lnx_hi = -(y + y * y / 2)
    return lnx_hi * v


def main():
    need(sum(TARGETS.values()) == 7688 and sum(PAID.values()) == 55998, "field and call counts")
    T1, P1 = sum(k * w for k, w in TARGETS.items()), sum(k * w for k, w in PAID.items())
    need((T1, P1) == (131723, 131115), "rank-one masses")
    need(max(PAID) < 121 and max(TARGETS) == 121, "ambient 121")

    alpha, gamma, delta = ratios(C_TEST)
    need(alpha[1] < 1 - Q(1, 10**8), "alpha < 1 - 1e-8")
    need(gamma[1] < Q(4991, 5000), "gamma < 4991/5000")
    need(delta[1] < Q(2, 3), "delta < 2/3")
    # p7 mixed root: alpha(C) = 1, alpha increasing in C
    lo, hi = Q("0.00268"), Q("0.00269")
    need(ratios(lo)[0][1] < 1 < ratios(hi)[0][0], "root bracket start")
    while hi - lo > Q(1, 10**12):
        mid = (lo + hi) / 2
        a = ratios(mid)[0]
        if a[1] < 1:
            lo = mid
        elif a[0] > 1:
            hi = mid
        else:
            break
    root = (lo, hi)
    need(root[0] > C_TEST, "C_test below the p7 mixed root")

    # Part B: #4416's sufficient route
    need((Q(4991, 5000)) ** 390 < Q(1, 2) and Q(2, 3) ** 2 < Q(1, 2), "decay blocks")
    need(1 / (1 + Q(V, 10**8)) + Q(4, 2 ** 16) < 1, "Bernoulli route at v = 6240")
    # direct certified powers: ln(x^v) upper bounds, then compare via exp of a negative number
    def total_upper(v):
        la, lg, ld = pow_upper(alpha[1], v), pow_upper(gamma[1], v), pow_upper(delta[1], v)
        # exp(x) <= 1/(1 - x) is false for x<0; use exp(x) <= 1/(1 + |x|) for the alpha term (Bernoulli-type)
        ea = 1 / (1 - la)
        def small(lx):                         # exp(lx) <= 2^-k when lx <= -k ln 2
            k = int(-lx / ln(2)[1])
            return Q(1, 2 ** k) if k > 0 else Q(1)
        return ea + 2 * small(lg) + 2 * small(ld)
    need(total_upper(V) < 1, "direct certified route at v = 6240")
    least_v = next(v for v in range(1, V + 1) if total_upper(v) < 1)

    # Part C: compiler ranks
    t = 1 - C_TEST
    d = (C_TEST - KAPPA) / 7
    z = 1 - (KAPPA + 6 * d)
    z0 = (t + z) / 2
    dl = z0 - t
    need(d == Q(1, 700000000) and dl == Q(1, 1400000000), "slack family")
    need(10 ** 26 < 11 ** 25, "theta < 25/26")
    Bc, h = Q(111, 26) * V, Q(1, 26)
    H0 = -((-(Bc * dl + 1 + 7 * V * (1 - z0))) // (h * dl))
    r = H0 * (1 - z0) / (z - z0)
    H1 = r.numerator // r.denominator + 1
    need(H0 == 4307773805920 and H1 == 16201843136005340321 and H0 >= 7 * V, "#4416 ranks reproduced")
    # tighter: certified log2 values, h from the best theta_bar = a/b with 10^b < 11^a
    ln2 = ln(2)
    log2_121_hi, log2_10_hi = ln(121)[1] / ln2[0], ln(10)[1] / ln2[0]
    x = 1 - z0
    s, term = Q(0), x
    for j in range(1, 30):
        s += term / j
        term *= x
    neg_log2_z0_hi = (s + term / (1 - x)) / ln2[0]
    neg_log2_eta = neg_log2_z0_hi + (1 - z0) * V * log2_121_hi
    best = None
    for den in range(26, 400):
        # smallest a with 10^den < 11^a, i.e. theta = log 10 / log 11 < a/den
        a = int(den * 0.9602) - 2
        while not 10 ** den < 11 ** a:
            a += 1
        hh = 1 - Q(a, den)
        B2 = V * (log2_10_hi + hh * log2_121_hi)
        H0b = -((-(B2 * dl + neg_log2_eta)) // (hh * dl))
        if H0b < 7 * V:
            continue
        rb = H0b * (1 - z0) / (z - z0)
        H1b = rb.numerator // rb.denominator + 1
        if best is None or H1b < best[0]:
            best = (H1b, H0b, f"{a}/{den}")
    print(json.dumps({
        "status": "PASS_PR4416_PADDING_ARITHMETIC",
        "invoice": {"fields": 7688, "paid_calls": 55998, "rank_one": [131723, 131115]},
        "alpha_upper": f"{float(alpha[1]):.12f}", "gamma_upper": f"{float(gamma[1]):.8f}",
        "delta_upper": f"{float(delta[1]):.8f}",
        "p7_mixed_root": [f"{float(root[0]):.15f}", f"{float(root[1]):.15f}"],
        "least_v_direct_route": least_v,
        "ranks_4416": {"H0": H0, "H1": H1},
        "tighter_sufficient_rank": {"H1": best[0], "H0": best[1], "theta_bar": best[2],
                                    "factor": f"{H1 / best[0]:.4f}"},
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
