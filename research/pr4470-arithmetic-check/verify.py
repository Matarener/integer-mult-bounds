#!/usr/bin/env python3
"""Independent arithmetic check of #4470 (conditional kappa 0.00302015, joint helper boundaries).

With its own certified interval logarithms (the helpers of research/p17-b480-check, copied here), this checks the
numbers printed in #4470 (head b9a13c16): the p16 invoice totals (64,620 paid jobs, 10,928 productive fields, rank
masses 239,886 / 239,134, surplus 752); the local profile change against #4447 (paid {1:2254,2:514,3:444,4:103,5:40,8:8}
-> {1:2237,2:388,3:494,4:147,5:36,8:8}: 53 fewer jobs; helpers {4:26,5:2,7:29,8:42,9:309} -> {4:28,7:7,8:47,9:326};
both masses +37) and its surplus-gain polynomial (vanishes at t = 1, positive on a grid of (0, 1)); the raw root
bracket (0.0030201659770, 0.0030201659771); and the higher-moment tails alpha, gamma_u, delta at #4470's tested
saving 604031/200000000, u = 1/5, cutoff 20, floor 21, against its limits 1 - 1e-9, 97/100, 97/100.
Invoices are as printed in #4470; nothing is imported from it. Also the logarithmic compiler conditions at ambient 145^1024
(theta 63/64, p = 1000) and the sufficiency of H = 64,215,200,000,000. And the nine outer rows from #4470's printed parameters
(FINE-PRIME row formulas, Strassen constant 3/32): all reproduce, binding row main_transform above kappa. Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
import sys

GRID = Q(1, 10**50)


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


def pow_upper(x, v):
    """certified upper bound of x^v for 0 < x < 1 rational: exp(v ln x) with ln x <= -(1-x) - (1-x)^2/2"""
    y = 1 - x
    lnx_hi = -(y + y * y / 2)
    return lnx_hi * v



# #4440's query-thinned units (strictification only; its compiler uses the older power majorant)
T4440C = {153: 224, 17: 448, 25: 448, 33: 448, 41: 448, 49: 448, 5: 532, 57: 448, 6: 342, 65: 448, 7: 1064, 73: 448, 8: 1767, 9: 4047}
P4440C = {1: 49045, 16: 448, 2: 13547, 24: 448, 3: 4256, 32: 448, 4: 1938, 40: 448, 48: 448, 5: 380, 56: 448, 64: 448, 72: 448, 8: 152}
T4440B = {127: 222, 15: 444, 22: 444, 29: 444, 36: 444, 43: 444, 50: 444, 57: 444, 64: 222, 8: 7902}
P4440B = {1: 25479, 14: 444, 2: 24156, 21: 444, 28: 444, 3: 1422, 35: 444, 4: 792, 42: 444, 49: 444, 5: 1836, 56: 444, 6: 198, 63: 222, 7: 342}
EXPECT4440 = {"complex": ("0.999999952117240859760145478346", "0.967466409565147920980822933860", "0.941649713484853845388929204841"),
              "BIT": ("0.999995735238059506641600561768", "0.957429821066420278606254392111", "0.949707924144871179442776557219")}
def lnq(x):
    a, b = ln(x.numerator), ln(x.denominator)
    return a[0] - b[1], a[1] - b[0]


def powq(base, e):
    """certified base^e for integer base >= 1 and rational exponent e (|e ln base| < 1.2)"""
    l = ln(base)
    lo, hi = (e * l[0], e * l[1]) if e >= 0 else (e * l[1], e * l[0])
    return exp_bounds(lo, hi)


def mom(hist, expo):
    lo = hi = Q(0)
    for k, w in hist.items():
        e = powq(k, expo - 1)
        lo, hi = lo + w * k * e[0], hi + w * k * e[1]
    return lo, hi




def ln_int(n):
    k = n.bit_length() - 1
    y = Q(n, 2 ** k)
    u = (y - 1) / (y + 1)
    s, term, j = Q(0), u, 0
    while True:
        s += term / (2 * j + 1)
        j += 1
        term *= u * u
        tail = term / (2 * j + 1) / (1 - u * u) if u else Q(0)
        if tail < Q(1, 10**40):
            break
    l2 = ln(2)
    return 2 * s + k * l2[0], 2 * (s + tail) + k * l2[1]


P = {"1": 41946, "16": 448, "2": 6984, "24": 448, "3": 8892, "32": 448, "4": 2646, "40": 448, "48": 448, "5": 648, "56": 448, "64": 448, "72": 224, "8": 144}
T = {"145": 224, "17": 448, "25": 448, "33": 448, "4": 504, "41": 448, "49": 448, "57": 448, "65": 448, "7": 126, "73": 224, "8": 846, "9": 5868}


def main():
    Pi = {int(k): w for k, w in P.items()}
    Ti = {int(k): w for k, w in T.items()}
    need(sum(Pi.values()) == 64620 and sum(Ti.values()) == 10928, "invoice counts")
    need(sum(k * w for k, w in Ti.items()) == 239886 and sum(k * w for k, w in Pi.items()) == 239134, "rank masses, surplus 752")
    old_p, new_p = {1: 2254, 2: 514, 3: 444, 4: 103, 5: 40, 8: 8}, {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}
    old_h, new_h = {4: 26, 5: 2, 7: 29, 8: 42, 9: 309}, {4: 28, 7: 7, 8: 47, 9: 326}
    need(sum(old_p.values()) - sum(new_p.values()) == 53, "53 fewer paid jobs per local call")
    mass = lambda h: sum(k * w for k, w in h.items())
    need(mass(new_p) - mass(old_p) == 37 == mass(new_h) - mass(old_h), "both masses rise by 37")
    keys = set(old_p) | set(new_p) | set(old_h) | set(new_h)
    coef = {k: (new_h.get(k, 0) - old_h.get(k, 0)) - (new_p.get(k, 0) - old_p.get(k, 0)) for k in keys}
    coef = {k: c for k, c in coef.items() if c}
    need(coef == {1: 17, 2: 126, 3: -50, 4: -42, 5: 2, 7: -22, 8: 5, 9: 17}, "surplus-gain polynomial")
    need(sum(c * k for k, c in coef.items()) == 0, "gain vanishes at t = 1")
    # rigorous: g(1) = 0 and g'(t) = sum c_k ln k k^t < 0 on [0, 1], certified on 256 subintervals with interval bounds
    pieces = 256
    for i in range(pieces):
        t0, t1 = Q(i, pieces), Q(i + 1, pieces)
        upper = Q(0)
        for k, c in coef.items():
            if k == 1:
                continue
            lk = ln(k)
            lo_pow, hi_pow = powq(k, t0)[0], powq(k, t1)[1]  # k^t on [t0, t1]
            upper += c * (lk[1] * hi_pow if c > 0 else lk[0] * lo_pow)
        need(upper < 0, f"g' < 0 on [{t0}, {t1}]")
    lo, hi = Q(30201659770, 10**13), Q(30201659771, 10**13)
    tl, th = moment(Ti, lo); pl, ph = moment(Pi, lo)
    need(tl > ph, "T_t > P_t at the lower root end")
    tl, th = moment(Ti, hi); pl, ph = moment(Pi, hi)
    need(th < pl, "T_t < P_t at the upper root end")
    tested = Q(604031, 200000000)
    t = 1 - tested
    tl, th = moment(Ti, tested); pl, ph = moment(Pi, tested)
    alpha = ph / tl
    gamma = mom(Pi, t + Q(1, 5))[1] / (powq(20, Q(1, 5))[0] * tl)
    delta = Q(sum(Ti.values()) * 21) / (powq(20, tested)[0] * tl)
    need(alpha < 1 - Q(1, 10**9) and gamma < Q(97, 100) and delta < Q(97, 100), "tails within #4470's limits")
    need(Q(97, 100) ** 1024 < Q(1, 2 ** 32), "both tails at power 1024 below 2^-32")
    need(1 / (1 + Q(1024, 10**9)) + 4 * Q(1, 2 ** 32) == Q(2097152001953127, 2097154147483648) < 1,
         "normalized paid bound 1/(1 + v (1 - limit_alpha)) + 2*2^-32 + 2*2^-32 reproduces and is below one")
    need(abs(float(alpha) - 0.999999988558808354) < 1e-15 and abs(float(gamma) - 0.956176646497545) < 1e-12
         and abs(float(delta) - 0.958284435309221) < 1e-12, "tails match #4470's printed values")
    # logarithmic compiler (polylog majorant) at ambient m = 145^v (largest target rank), v = 1024, c = 20, b = 21
    v, c, b, tb, p = 1024, 20, 21, Q(63, 64), 1000
    A_, Bd = tb.numerator, tb.denominator
    need(max(Ti) == 145 and c ** Bd < b ** A_, "compiler: ambient 145, theta = log c / log b < 63/64")
    need((Bd - A_) + Bd * v * ln(c)[1] / ln(2)[0] <= A_ * v * ln(145)[0] / ln(2)[1], "compiler: 2^(b-a) r^b <= m^a")
    ln_eta_lo = lnq(t)[0] - v * tested * ln(145)[1]
    need(p * lnq(tb)[1] < ln_eta_lo, "compiler: theta_bar^p < eta")
    need(v * tested * ln(145)[1] < p * ln(2)[0], "compiler: m^(1-t) < 2^p")
    uniform = Q(528527, 175000000)
    zt = (1 - uniform) - t
    need(zt == Q(1, 1400000000), "compiler: z - t = 1/1400000000")
    H = 64215200000000
    need(p * ln_int(H + 1)[1] < zt * H * ln(2)[0], "compiler: (1+H)^p < 2^((z-t)H) at the stated H")
    # outer ledger: #4470's printed parameters and margins against the FINE-PRIME row formulas
    OP = {k: Q(x) for k, x in {"epsilon": "1399999999/1400000000", "q": "4228213/1400000000", "a": "2114107/700000000", "beta": "1399999997/1400000000", "cap_xi": "1782169498195771787/1960000000000000000", "kappa": "60403/20000000"}.items()}
    OM = {k: Q(x) for k, x in {"boundary_algebraic_matrix": "5919499595771787/1960000000000000000", "fused_gaussian": "5919499587315361/1960000000000000000", "global_coordinate_router": "2114107/700000000", "group_bit_router": "2959750493657679/980000000000000000", "group_scans": "699999999/700000000", "main_transform": "5919498195771787/1960000000000000000", "microbox_face_corrections": "26950000001/350000000", "polynomial_products": "1399999999/1400000000", "sparse_union_movement": "802169499595771787/1960000000000000000"}.items()}
    e, q_, a_, be, xi, kap = OP["epsilon"], OP["q"], OP["a"], OP["beta"], OP["cap_xi"], OP["kappa"]
    need(kap == Q(60403, 20000000), "kappa 0.00302015")
    rows = {"main_transform": e * q_, "global_coordinate_router": a_, "fused_gaussian": 1 - e + q_ * be,
            "group_bit_router": 1 - e + a_ * be, "group_scans": 1 - e + be, "polynomial_products": e,
            "sparse_union_movement": xi + Q(1, 2) - e, "microbox_face_corrections": 1 - (e + be + 48 - 128 + 2),
            "boundary_algebraic_matrix": Q(3, 32) + xi - e}
    need(rows == OM, "all nine outer rows reproduce from the parameters (Strassen constant c = 3/32)")
    need(min(OM, key=OM.get) == "main_transform" and min(OM.values()) > kap, "binding row main_transform, strictly above kappa")
    print(json.dumps({"status": "PASS_PR4470_ARITHMETIC_CHECK", "outer_min_minus_kappa": str(min(OM.values()) - kap), "compiler_H_sufficient": H, "paid_jobs": 64620, "fields": 10928, "surplus": 752,
                      "root_bracket": ["0.0030201659770", "0.0030201659771"], "alpha_upper": f"{float(alpha):.15f}",
                      "gamma_upper": f"{float(gamma):.12f}", "delta_upper": f"{float(delta):.12f}",
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
