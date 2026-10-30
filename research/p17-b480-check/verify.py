#!/usr/bin/env python3
"""Independent arithmetic check of #4447 (kappa 0.00300123) and #4453 (kappa 0.00300120).

Both report the same B/480 contact patch on #4441's p17 invoice. This verifier checks, with its own certified
interval logarithms: the invoice is #4441's plus exactly 19 per-call swaps [2,2,1,3] -> [1,1,2,4]; the raw root
bracket; for each PR the higher-moment strictification (main's research/higher-moment-strictification theorem:
alpha = P_t/T_t, gamma_u = P_(t+u)/(c^u T_t), delta = B b/(c^C T_t), bound alpha^v + 2 gamma_u^v + 2 delta^v < 1)
at the PR's own (C, v, c, b, u) and stated rational limits; the polylog compiler conditions (theta, the shifted
exit condition, theta_bar^p < eta, m^(1-t) < 2^p) at ambient 153^v; and the least H with (1+H)^p < 2^((z-t)H).
Invoices and parameters are as printed in the PRs; nothing is imported from them.
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



# #4440's query-thinned units (strictification only; its compiler uses the older power majorant)
T4440C = {153: 224, 17: 448, 25: 448, 33: 448, 41: 448, 49: 448, 5: 532, 57: 448, 6: 342, 65: 448, 7: 1064, 73: 448, 8: 1767, 9: 4047}
P4440C = {1: 49045, 16: 448, 2: 13547, 24: 448, 3: 4256, 32: 448, 4: 1938, 40: 448, 48: 448, 5: 380, 56: 448, 64: 448, 72: 448, 8: 152}
T4440B = {127: 222, 15: 444, 22: 444, 29: 444, 36: 444, 43: 444, 50: 444, 57: 444, 64: 222, 8: 7902}
P4440B = {1: 25479, 14: 444, 2: 24156, 21: 444, 28: 444, 3: 1422, 35: 444, 4: 792, 42: 444, 49: 444, 5: 1836, 56: 444, 6: 198, 63: 222, 7: 342}
EXPECT4440 = {"complex": ("0.999999952117240859760145478346", "0.967466409565147920980822933860", "0.941649713484853845388929204841"),
              "BIT": ("0.999995735238059506641600561768", "0.957429821066420278606254392111", "0.949707924144871179442776557219")}
T = {153: 224, 17: 448, 25: 448, 33: 448, 4: 494, 41: 448, 49: 448, 5: 38, 57: 448, 65: 448, 7: 551, 73: 448, 8: 798, 9: 5871}
P = {1: 44618, 16: 448, 2: 9766, 24: 448, 3: 8436, 32: 448, 4: 1957, 40: 448, 48: 448, 5: 760, 56: 448, 64: 448, 72: 448, 8: 152}
P4441 = {1: 44599, 16: 448, 2: 9785, 24: 448, 3: 8455, 32: 448, 4: 1938, 40: 448, 48: 448, 5: 760, 56: 448, 64: 448, 72: 448, 8: 152}
CASES = {
    "4447": {"kappa": Q("0.00300123"), "C": Q(600247, 200000000), "v": 1024, "c": 20, "b": 21, "u": Q(1, 5),
             "limits": (1 - Q(1, 10**9), Q(97, 100), Q(19, 20)), "theta_bar": Q(63, 64), "p": 1000, "H": 64215200000000},
    "4441": {"kappa": Q("0.00300105"), "C": Q(750263, 250000000), "v": 1024, "c": 20, "b": 21, "u": Q(1, 5),
             "limits": (1 - Q(1, 10**9), Q(97, 100), Q(19, 20)), "theta_bar": Q(63, 64), "p": 1000, "H": 165315500000000,
             "invoice": "P4441"},
    "4453": {"kappa": Q(7503, 2500000), "C": Q(150061, 50000000), "v": 675, "c": 18, "b": 22, "u": Q(3, 25),
             "limits": (Q(999999981, 10**9), Q(491, 500), Q(391, 400)), "theta_bar": Q(15, 16), "p": 160, "H": 2299850000000},
}


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


def log2_upper_of_H1(H):
    """certified upper bound of log2(1+H)"""
    n = H + 1
    l = ln(n) if n < 2**60 else None
    return l


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


def main():
    from collections import Counter
    d = Counter(P4441)
    d.update({1: 19, 4: 19})
    d.subtract({2: 19, 3: 19})
    need(+d == Counter(P), "invoice = #4441 + 19 swaps [2,2,1,3] -> [1,1,2,4]")
    need(sum(T.values()) == 11560 and sum(P.values()) == 69273, "fields and calls")
    need((sum(k * w for k, w in T.items()), sum(k * w for k, w in P.items())) == (260798, 259998), "rank surplus 800")
    need(all((1 + 4 ** x) < 2 ** x + 3 ** x for x in (0.1, 0.5, 0.9)), "concavity spot checks")
    # raw root bracket
    def alpha(C):
        tl, th = mom(T, 1 - C)
        pl, ph = mom(P, 1 - C)
        return pl / th, ph / tl
    lo, hi = Q("0.0030012390168"), Q("0.0030012390174")
    need(alpha(lo)[1] < 1 < alpha(hi)[0], "root bracket (0.0030012390168, 0.0030012390174)")
    out = {"status": "PASS_PR4447_PR4453_ARITHMETIC", "new_kappa_claimed": False,
           "invoice": {"fields": 11560, "paid_calls": 69273, "rank_surplus": 800}, "root_bracket": [str(lo), str(hi)]}
    B = sum(T.values())
    for name, cs in CASES.items():
        C, v, c, b, u = cs["C"], cs["v"], cs["c"], cs["b"], cs["u"]
        Pinv = P4441 if cs.get("invoice") == "P4441" else P
        t = 1 - C
        need(u >= C and t + u >= 1 and 1 < c < b < 153, f"{name}: theorem hypotheses")
        tl, th = mom(T, t)
        pl, ph = mom(Pinv, t)
        a_hi = ph / tl
        g_num = mom(Pinv, t + u)[1]
        cu = powq(c, u)[0]
        g_hi = g_num / (cu * tl)
        cC = powq(c, C)[0]
        d_hi = B * b / (cC * tl)
        la, lg, ld = cs["limits"]
        need(a_hi < la and g_hi < lg and d_hi < ld, f"{name}: alpha, gamma_u, delta below the stated limits")
        total = 1 / (1 + v * (1 - la)) + 2 * lg ** v + 2 * ld ** v
        need(total < 1, f"{name}: alpha^v + 2 gamma^v + 2 delta^v < 1")
        # compiler (polylog majorant): m = 153^v, r_max = c^v, k_min = b^v
        tb, p = cs["theta_bar"], cs["p"]
        A_, Bd = tb.numerator, tb.denominator
        need(c ** Bd < b ** A_, f"{name}: theta = log c / log b < theta_bar")
        need((Bd - A_) + Bd * v * ln(c)[1] / ln(2)[0] <= A_ * v * ln(153)[0] / ln(2)[1], f"{name}: 2^(b-a) r^b <= m^a")
        # eta = t * 153^(v (t-1)); need theta_bar^p < eta and m^(1-t) < 2^p (logs)
        ln_eta_lo = lnq(t)[0] - v * C * ln(153)[1]
        need(p * lnq(tb)[1] < ln_eta_lo, f"{name}: theta_bar^p < eta")
        need(v * C * ln(153)[1] < p * ln(2)[0], f"{name}: m^(1-t) < 2^p")
        dgap = (C - cs["kappa"]) / 7
        z = 1 - (cs["kappa"] + 6 * dgap)
        zt = z - t
        need(zt == dgap, f"{name}: z - t = d")
        H = cs["H"]
        def ok(Hx):
            l = ln_int(Hx + 1)
            return p * l[1] < zt * Hx * ln(2)[0]
        need(ok(H), f"{name}: (1+H)^p < 2^((z-t)H) at stated H")
        lo_h, hi_h = 1, H
        while lo_h < hi_h:
            mid = (lo_h + hi_h) // 2
            if ok(mid):
                hi_h = mid
            else:
                lo_h = mid + 1
        out[name] = {"alpha_upper": f"{float(a_hi):.15f}", "gamma_u_upper": f"{float(g_hi):.12f}",
                     "delta_upper": f"{float(d_hi):.12f}", "stated_limits": [str(x) for x in cs["limits"]],
                     "tensor_bound": f"{float(total):.10f}", "stated_H": H, "least_certified_H": lo_h}
    # #4440: strictification ratios against the printed upper ends
    for name, (Tx, Px, C, c, b) in {"4440-complex": (T4440C, P4440C, Q(29603, 10000000), 20, 21),
                                    "4440-BIT": (T4440B, P4440B, Q(173, 50000), 17, 18)}.items():
        u, v, t = Q(1, 5), 1024, 1 - C
        need(sum(k * w for k, w in Tx.items()) > sum(k * w for k, w in Px.items()), f"{name}: rank surplus")
        tl, th = mom(Tx, t)
        a_hi = mom(Px, t)[1] / tl
        g_hi = mom(Px, t + u)[1] / (powq(c, u)[0] * tl)
        d_hi = sum(Tx.values()) * b / (powq(c, C)[0] * tl)
        ea, eg, ed = (Q(x) for x in EXPECT4440[name.split("-")[1]])
        need(abs(a_hi - ea) < Q(1, 10**28) and abs(g_hi - eg) < Q(1, 10**28) and abs(d_hi - ed) < Q(1, 10**28),
             f"{name}: ratios match the printed intervals")
        lnb = lambda x: -(1 - x) - (1 - x) ** 2 / 2
        bound = 1 / (1 - v * lnb(a_hi)) + 2 * Q(1, 2 ** int(-v * lnb(g_hi) / ln(2)[1])) + 2 * Q(1, 2 ** int(-v * lnb(d_hi) / ln(2)[1]))
        need(bound < 1, f"{name}: tensor bound at v = 1024")
        out[name] = {"alpha_upper": f"{float(a_hi):.15f}", "gamma_u_upper": f"{float(g_hi):.12f}",
                     "delta_upper": f"{float(d_hi):.12f}", "tensor_bound_upper": f"{float(bound):.10f}"}
    # #4446: rank-one tail (gamma = P_1/(c^C T)), v = 17160, c = 18, b = 19, ambient 281^v; power-majorant compiler
    C, v, c, b, kap = Q(1500527, 500000000), 17160, 18, 19, Q(3001053, 10**9)
    t = 1 - C
    tl, th = mom(T, t)
    a_hi = mom(P4441, t)[1] / tl
    P1 = sum(k * w for k, w in P4441.items())
    g_hi = P1 / (powq(c, C)[0] * tl)
    d_hi = sum(T.values()) * b / (powq(c, C)[0] * tl)
    for got, want in ((a_hi, "0.99999999981197332875426410809243317"), (g_hi, "0.99907124299228386730839393376721824"),
                      (d_hi, "0.84399113766577138522456189514008498")):
        need(abs(got - Q(want)) < Q(1, 10**30), "#4446: ratio matches its printed interval")
    la, lg, ld = 1 - Q(1, 10**10), Q(9991, 10000), Q(6, 7)
    need(a_hi < la and g_hi < lg and d_hi < ld, "#4446: below stated limits")
    need(lg ** 780 < Q(1, 2) and ld ** 5 < Q(1, 2), "#4446: decay blocks")
    bound = 1 / (1 + v * (1 - la)) + 2 * Q(1, 2 ** 22) + 2 * Q(1, 2 ** (v // 5))
    need(bound < 1, "#4446: alpha^v + 2 gamma^v + 2 delta^v < 1")
    need(18 ** 55 < 19 ** 54, "#4446: theta = log 18 / log 19 < 54/55")
    h, d = Q(1, 55), (C - kap) / 7
    z = 1 - (kap + 6 * d)
    z0 = (t + z) / 2
    dl = z0 - t
    need(dl == Q(1, 14000000000), "#4446: delta gap")
    Bexit, negl2eta = Q(88608), Q(32513793811, 70000000)
    l2 = ln(2)
    true_B = v * (ln(18)[1] + h * ln(281)[1]) / l2[0]
    need(true_B < Bexit, "#4446: exit constant dominates log2(r_max m^h) at ambient 281^v")
    s_, term = Q(0), 1 - z0
    for j in range(1, 30):
        s_ += term / j
        term *= (1 - z0)
    true_negl2eta = (s_ + term / z0) / l2[0] + (1 - z0) * v * ln(281)[1] / l2[0]
    need(true_negl2eta < negl2eta, "#4446: -log2(eta) upper bound dominates")
    H0 = -((-(Bexit * dl + negl2eta)) // (h * dl))
    r = H0 * (1 - z0) / (z - z0)
    H1 = r.numerator // r.denominator + 1
    need(H0 == 357651736794440 and H1 == 15026650096742881962201, "#4446: H0, H1 reproduced")
    out["4446"] = {"alpha_upper": f"{float(a_hi):.15f}", "gamma_upper": f"{float(g_hi):.12f}",
                   "delta_upper": f"{float(d_hi):.12f}", "tensor_bound": f"{float(bound):.10f}",
                   "exit_constant": [f"{float(true_B):.1f}", 88608], "neg_log2_eta": [f"{float(true_negl2eta):.3f}", f"{float(negl2eta):.3f}"],
                   "H0": H0, "H1": H1}
    # #4440's power-majorant compiler (PROOF.md section 3): h = 1/64, v = 1024, z0 = (t + z)/2
    def compiler4440(tested, uniform):
        hh, vv = Q(1, 64), 1024
        t_, z_ = 1 - tested, 1 - uniform
        z0_ = (t_ + z_) / 2
        gap = z0_ - t_
        x = (gap * (5 + 8 * hh) * vv + 1 + 8 * vv * (1 - z0_)) / (hh * gap)
        h0 = -((-x.numerator) // x.denominator)
        x = h0 * (1 - z0_) / (z_ - z0_)
        return h0, x.numerator // x.denominator + 1
    k4440, tc = Q(37, 12500), Q(29603, 10000000)
    uc = k4440 + 6 * (tc - k4440) / 7
    need(uc == Q(103609, 35000000), "#4440: complex uniform saving kappa + 6d")
    need(compiler4440(tc, uc) == (75415467350, 10418370291022217), "#4440: complex H0, H1")
    need(compiler4440(Q(173, 50000), Q(3459, 1000000)) == (3755884544, 25986965159937), "#4440: BIT H0, H1")
    for g_, s_ in ((Q(1, 30000000), Q(8589700209, 251666829934592)), (Q(1, 250000), Q(68719461047, 16845935476736))):
        need(1 - 1 / (1 + 1024 * g_) - Q(4, 2 ** 32) == s_ > 0, "#4440: Bernoulli surplus")
    need(20 ** 64 < 21 ** 63 and 17 ** 64 < 18 ** 63 and Q(31, 32) ** 128 < Q(1, 16) and Q(19, 20) ** 128 < Q(1, 16),
         "#4440: exit exponent h = 1/64 and tail decay blocks")
    # #4446's separate p6 BIT supplier (ordinary BIT premise): invoice, raw root and alpha at the tested saving
    Pb = {1: 17199, 2: 17446, 3: 1027, 4: 572, 5: 1326, 6: 143, 7: 1357, 14: 444, 28: 444, 42: 222}
    Tb = {8: 5707, 22: 444, 36: 444, 50: 222, 92: 222}
    need(sum(k * w for k, w in Pb.items()) == 102419 and sum(k * w for k, w in Tb.items()) == 102932, "#4446 BIT: rank masses")
    tl, _ = moment(Tb, Q(157, 50000))
    _, ph = moment(Pb, Q(157, 50000))
    need(ph / tl < Q(99999, 100000), "#4446 BIT: alpha < 99999/100000 at the tested saving 157/50000")
    lo_t, _ = moment(Tb, Q(314, 100000)); _, hi_p = moment(Pb, Q(314, 100000))
    _, hi_t = moment(Tb, Q(315, 100000)); lo_p, _ = moment(Pb, Q(315, 100000))
    need(lo_t > hi_p and hi_t < lo_p, "#4446 BIT: raw root in (0.00314, 0.00315), above the admitted 0.00312")
    out["4446_BIT_supplier"] = {"rank_masses": [102419, 102932], "surplus": 513, "alpha_upper": f"{float(ph / tl):.9f}",
                                "raw_root_bracket": ["0.00314", "0.00315"]}
    # gamma (rank-one tail at cutoff 7), the finite paid moment at power 6000, the compiler and the delayed cover
    Cb, Ub, Cov, POW = Q(157, 50000), Q(627, 200000), Q(313, 100000), 6000
    e7 = exp_bounds(-Cb * ln(7)[1], -Cb * ln(7)[0])  # 7^(-C) bounds
    gamma_hi = Q(102419) * e7[1] / tl  # P1 / (7^C T_t), upper bound via 7^(-C) upper and T_t lower
    need(gamma_hi < Q(999, 1000) and Q(999, 1000) ** 1000 < Q(1, 2), "#4446 BIT: gamma < 999/1000 and decay block")
    need(Q(1, 1) / (1 + Q(POW, 100000)) + 2 * Q(1, 2) ** (POW // 1000) == Q(1653, 1696), "#4446 BIT: finite paid moment 1653/1696")
    need(7 ** 16 < 8 ** 15 and 92 < 2 ** 7, "#4446 BIT: separation and ambient")
    tb, zb = 1 - Cb, 1 - Ub
    z0b = (tb + zb) / 2
    db, hb = z0b - tb, Q(1, 16)
    x = ((3 + 7 * hb) * POW * db + 1 + 7 * POW * (1 - z0b)) / (hb * db)
    H0b = -((-x.numerator) // x.denominator)
    x = H0b * (1 - z0b) / (zb - z0b)
    need((H0b, x.numerator // x.denominator + 1) == (850090000, 1066862950001), "#4446 BIT: compiler H0, H1")
    need(Ub - Cov == Q(1, 200000) and (1 + (Ub - Cov) / 4) / (1 + (Ub - Cov) / 2) < 1, "#4446 BIT: delayed cover gap")
    out["4446_BIT_supplier"].update({"gamma_upper": f"{float(gamma_hi):.6f}", "H0_H1": [850090000, 1066862950001]})
    # outer ledgers of all five kappa PRs: printed parameters and margins against the FINE-PRIME row formulas
    OUTER = {"4441": {"parameters": {"epsilon": "3499999999/3500000000", "q": "5251839/1750000000", "a": "10503679/3500000000", "beta": "3499999997/3500000000", "cap_xi": "5569162686494748161/6125000000000000000", "kappa": "60021/20000000"}, "margins": {"boundary_algebraic_matrix": "18381438244748161/6125000000000000000", "fused_gaussian": "18381438234244483/6125000000000000000", "global_coordinate_router": "10503679/3500000000", "group_bit_router": "36762879968488963/12250000000000000000", "group_scans": "1749999999/1750000000", "main_transform": "18381436494748161/6125000000000000000", "microbox_face_corrections": "67375000001/875000000", "polynomial_products": "3499999999/3500000000", "sparse_union_movement": "2506662688244748161/6125000000000000000"}}, "4447": {"parameters": {"epsilon": "1399999999/1400000000", "q": "168069/56000000", "a": "2100863/700000000", "beta": "1399999997/1400000000", "cap_xi": "71285296599831931/78400000000000000", "kappa": "300123/100000000"}, "margins": {"boundary_algebraic_matrix": "235296655831931/78400000000000000", "fused_gaussian": "235296655495793/78400000000000000", "global_coordinate_router": "2100863/700000000", "group_bit_router": "2941208893697411/980000000000000000", "group_scans": "699999999/700000000", "main_transform": "235296599831931/78400000000000000", "microbox_face_corrections": "26950000001/350000000", "polynomial_products": "1399999999/1400000000", "sparse_union_movement": "32085296655831931/78400000000000000"}}, "4453": {"parameters": {"epsilon": "349999999/350000000", "q": "1050423/350000000", "a": "131303/43750000", "beta": "349999997/350000000", "cap_xi": "111383273048949577/122500000000000000", "kappa": "7503/2500000"}, "margins": {"boundary_algebraic_matrix": "367648398949577/122500000000000000", "fused_gaussian": "367648396848731/122500000000000000", "global_coordinate_router": "131303/43750000", "group_bit_router": "45956093356091/15312500000000000", "group_scans": "174999999/175000000", "main_transform": "367648048949577/122500000000000000", "microbox_face_corrections": "6737500001/87500000", "polynomial_products": "349999999/350000000", "sparse_union_movement": "50133273398949577/122500000000000000"}}, "4440": {"parameters": {"epsilon": "69999997/70000000", "q": "207209/70000000", "a": "51803/17500000", "beta": "69999991/70000000", "cap_xi": "4455129629378373/4900000000000000", "kappa": "37/12500"}, "margins": {"boundary_algebraic_matrix": "14504839378373/4900000000000000", "fused_gaussian": "14504838135119/4900000000000000", "global_coordinate_router": "51803/17500000", "group_bit_router": "3626262033773/1225000000000000", "group_scans": "34999997/35000000", "main_transform": "14504629378373/4900000000000000", "microbox_face_corrections": "1347500003/17500000", "polynomial_products": "69999997/70000000", "sparse_union_movement": "2005129839378373/4900000000000000"}}, "4446": {"parameters": {"epsilon": "6999999999/7000000000", "q": "10503687/3500000000", "a": "168059/56000000", "beta": "6999999997/7000000000", "cap_xi": "22276650808989496313/24500000000000000000", "kappa": "3001053/1000000000"}, "margins": {"boundary_algebraic_matrix": "73525812489496313/24500000000000000000", "fused_gaussian": "73525812468488939/24500000000000000000", "global_coordinate_router": "168059/56000000", "group_bit_router": "1176413055495823/392000000000000000", "group_scans": "3499999999/3500000000", "main_transform": "73525808989496313/24500000000000000000", "microbox_face_corrections": "134750000001/1750000000", "polynomial_products": "6999999999/7000000000", "sparse_union_movement": "10026650812489496313/24500000000000000000"}}}
    outer_min = {}
    for n, rec in OUTER.items():
        P_ = {k: Q(x) for k, x in rec["parameters"].items()}
        M_ = {k: Q(x) for k, x in rec["margins"].items()}
        e, q_, a_, be, xi, kap = P_["epsilon"], P_["q"], P_["a"], P_["beta"], P_["cap_xi"], P_["kappa"]
        rows = {"main_transform": e * q_, "global_coordinate_router": a_, "fused_gaussian": 1 - e + q_ * be,
                "group_bit_router": 1 - e + a_ * be, "group_scans": 1 - e + be, "polynomial_products": e,
                "sparse_union_movement": xi + Q(1, 2) - e, "microbox_face_corrections": 1 - (e + be + 48 - 128 + 2),
                "boundary_algebraic_matrix": Q(3, 32) + xi - e}
        need(rows == M_, f"#{n}: all nine outer rows reproduce")
        need(min(M_, key=M_.get) == "main_transform" and min(M_.values()) > kap, f"#{n}: binding row above kappa")
        outer_min[n] = f"{float(min(M_.values()) - kap):.3e}"
    out["outer_ledgers_min_minus_kappa"] = outer_min
    out["4440_compiler"] = {"complex": [75415467350, 10418370291022217], "BIT": [3755884544, 25986965159937]}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
