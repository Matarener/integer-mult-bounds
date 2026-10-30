#!/usr/bin/env python3
"""Independent arithmetic check of the tensor-and-split endpoints of #4412 (kappa 0.00247755) and #4414 (0.00267987).

Both tensor a native mixed unit v times and split paid jobs at a cutoff c^v (#4412: c = 4; #4414:
floor((19/4)^v), which costs a factor 2 in the split tail). With alpha = P_tau/T_tau and
gamma = P_1/(c^C T_tau), the normalized paid moment is below alpha^v + 2 gamma^v (or + 4 gamma^v with the floor).
For each PR this verifier certifies alpha and gamma at the tested saving with its own interval logs, brackets the
raw mixed root, checks the stated v, finds the least v under the same certified bound, and reproduces the stated
compiler ranks H0, H1 from their rational formulas. Inputs are the printed invoices; nothing is imported.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
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



CASES = {
    "4412": {"targets": {5: 196, 6: 126, 7: 392, 8: 651, 9: 1491, 25: 448, 57: 224},
             "paid": {1: 17409, 2: 4991, 3: 1568, 4: 714, 5: 140, 8: 504, 16: 448},
             "C_test": Q("0.00247756"), "kappa": Q("0.00247755"), "v": 15000, "cut": Q(4), "floor": False,
             "alpha_bound": 1 - Q(1, 10**9), "gamma_bound": Q(999, 1000),
             "h": Q(1, 8), "theta_cmp": (4 ** 8, 5 ** 7), "B": lambda v, h: (2 + 6 * h) * v, "log2m": 6,
             "H0": 2508580090000, "H1": 8701218254312470001},
    "4414": {"targets": {5: 364, 6: 234, 7: 728, 8: 1209, 9: 2769, 25: 448, 41: 448, 57: 224, 105: 224},
             "paid": {1: 32331, 2: 9269, 3: 2912, 4: 1326, 5: 260, 8: 1224, 16: 448, 32: 448, 48: 224},
             "C_test": Q("0.00267988"), "kappa": Q("0.00267987"), "v": 150000, "cut": Q(19, 4), "floor": True,
             "alpha_bound": 1 - Q(1, 10**8), "gamma_bound": Q(9999, 10000),
             "h": Q(1, 32), "theta_cmp": (19 ** 32, 4 ** 32 * 5 ** 31), "B": lambda v, h: Q(79, 32) * v, "log2m": 7,
             "H0": 126106333450000, "H1": 473129651134046950001},
}


def ln_q(x):
    """certified ln of a positive rational p/q"""
    a, b = ln(x.numerator), ln(x.denominator)
    return a[0] - b[1], a[1] - b[0]


def analyse(name, cs):
    T_hist, P_hist, C = cs["targets"], cs["paid"], cs["C_test"]
    T1, P1 = sum(k * w for k, w in T_hist.items()), sum(k * w for k, w in P_hist.items())
    need(T1 > P1, f"{name}: positive rank-one surplus")
    def ratios(Cx):
        T = moment(T_hist, Cx)
        Pm = moment(P_hist, Cx)
        lc = ln_q(cs["cut"])
        cC = exp_bounds(Cx * lc[0], Cx * lc[1])
        return (Pm[0] / T[1], Pm[1] / T[0]), (P1 / (cC[1] * T[1]), P1 / (cC[0] * T[0]))
    alpha, gamma = ratios(C)
    need(alpha[1] <= cs["alpha_bound"] and gamma[1] < cs["gamma_bound"], f"{name}: alpha and gamma bounds")
    lo, hi = C, C + Q(1, 10**5)
    need(ratios(hi)[0][0] > 1, f"{name}: root bracket")
    while hi - lo > Q(1, 10**12):
        mid = (lo + hi) / 2
        a = ratios(mid)[0]
        if a[1] < 1:
            lo = mid
        elif a[0] > 1:
            hi = mid
        else:
            break
    tail = 4 if cs["floor"] else 2              # floor(c^v) >= c^v / 2 doubles the split tail
    def total_upper(v):
        ea = 1 / (1 - pow_upper(alpha[1], v))
        lg = pow_upper(gamma[1], v)
        k = int(-lg / ln(2)[1])
        return ea + tail * (Q(1, 2 ** k) if k > 0 else Q(1))
    v = cs["v"]
    need(total_upper(v) < 1, f"{name}: tensor inequality at v = {v}")
    least_v = None
    lo_v, hi_v = 1, v
    while lo_v < hi_v:                          # total_upper is decreasing in v once both decays bite
        mid = (lo_v + hi_v) // 2
        if total_upper(mid) < 1:
            hi_v = mid
        else:
            lo_v = mid + 1
    least_v = lo_v
    need(total_upper(least_v) < 1 and not total_upper(least_v - 1) < 1, f"{name}: least v")
    # ranks
    t = 1 - C
    d = (C - cs["kappa"]) / 7
    z = 1 - (cs["kappa"] + 6 * d)
    z0 = (t + z) / 2
    dl = z0 - t
    a_cmp, b_cmp = cs["theta_cmp"]
    need(a_cmp < b_cmp, f"{name}: theta bound")
    h = cs["h"]
    B = cs["B"](v, h)
    H0 = -((-(B * dl + 1 + cs["log2m"] * v * (1 - z0))) // (h * dl))
    r = H0 * (1 - z0) / (z - z0)
    H1 = r.numerator // r.denominator + 1
    need(H0 == cs["H0"] and H1 == cs["H1"] and H0 >= cs["log2m"] * v, f"{name}: stated ranks reproduced")
    return {"alpha_upper": f"{float(alpha[1]):.12f}", "gamma_upper": f"{float(gamma[1]):.8f}",
            "gamma_stated_bound": str(cs["gamma_bound"]),
            "mixed_root": [f"{float(lo):.13f}", f"{float(hi):.13f}"],
            "C_test_gap_to_root": f"{float(lo - C):.2e}", "v_used": v, "least_v": least_v,
            "H0": H0, "H1": H1}


def main():
    out = {"status": "PASS_PR4412_PR4414_TENSOR_ARITHMETIC", "new_kappa_claimed": False}
    for name, cs in CASES.items():
        out[name] = analyse(name, cs)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
