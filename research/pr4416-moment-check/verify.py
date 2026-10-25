#!/usr/bin/env python3
"""Independent certified check of #4416's moment and paid-tail inequalities (kappa = 0.00268647).

#4416 (TENSOR.md section 3-4) needs, at saving C and tau = 1 - C, with raw target invoice T, paid invoice
P, B productive fields and completion bases c < b:
    alpha = P_tau / T_tau,  gamma = P_1 / (c^C T_tau),  delta = B b / (c^C T_tau),
    alpha^v + 2 gamma^v + 2 delta^v < 1,
where X_tau = sum_r n_r r^tau. This recomputes alpha, gamma and delta with exact rational enclosures
(ln by atanh after reducing by powers of two, exp by Taylor with a remainder), the closing integer
comparisons at v = 6240, the gap, and the limit saving C* where alpha = 1. TENSOR.md and RESULT.json
are vendored byte-identically. No code from #4416.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
VENDORED = {
    "vendor/TENSOR.md": "b2eba86cb979b4dc2a045f2e74bbd29e4d9e5ec87d6a2bc23ba7b54f1f58e3e3",
    "vendor/RESULT.json": "9b814be97e3b45fcc28eafa8a65694897a7387f71a14d44796c6aadf303d7fab",
}
PHRASES = [
    "T = {5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224},",
    "P = {1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}.",
    "alpha^v + 2*gamma^v + 2*delta^v,",
    "alpha < 1-1/10^8,",
    "gamma < 4991/5000       with c=10,",
    "delta < 2/3            with b=11.",
    "Take v=6240. The exact integer comparison",
    "`(4991/5000)^390<1/2` gives gamma^v<2^-16. Also `(2/3)^2<1/2`,",
    "Bernoulli's inequality bounds alpha^v by 1/(1+v/10^8), so",
    "The exact sufficient gap is greater than 0.00000136095023295546.",
]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def atanh_ln(x, terms=60):
    z = (x - 1) / (x + 1)
    s = 2 * sum(z ** (2 * k + 1) / (2 * k + 1) for k in range(terms + 1))
    return s, s + 2 * z ** (2 * terms + 3) / ((2 * terms + 3) * (1 - z * z))


LN2 = atanh_ln(Q(2))


def ln_bounds(x):
    """x >= 1 rational"""
    k = (x.numerator // x.denominator).bit_length() - 1
    c, d = atanh_ln(x / 2 ** k)
    return k * LN2[0] + c, k * LN2[1] + d


def exp_bounds(y, terms=40):
    """0 <= y <= 1"""
    s, term = Q(0), Q(1)
    for k in range(terms + 1):
        s += term
        term = term * y / (k + 1)
    return s, s + 3 * term


def power_moment(inv, C):
    """sum n r^(1-C) = sum n r exp(-C ln r), enclosed"""
    lo = hi = Q(0)
    for r, n in inv.items():
        if r == 1:
            lo, hi = lo + n, hi + n
            continue
        l_lo, l_hi = ln_bounds(Q(r))
        lo += n * r / exp_bounds(C * l_hi)[1]
        hi += n * r / exp_bounds(C * l_lo)[0]
    return lo, hi


def ratios(T, P, C, B, b, c):
    t_lo, t_hi = power_moment(T, C)
    p_lo, p_hi = power_moment(P, C)
    l_lo, l_hi = ln_bounds(Q(c))
    cc_lo, cc_hi = exp_bounds(C * l_lo)[0], exp_bounds(C * l_hi)[1]
    P1 = sum(r * n for r, n in P.items())
    return {"alpha": (p_lo / t_hi, p_hi / t_lo),
            "gamma": (P1 / (cc_hi * t_hi), P1 / (cc_lo * t_lo)),
            "delta": (B * b / (cc_hi * t_hi), B * b / (cc_lo * t_lo))}


def main():
    for rel, digest in VENDORED.items():
        need(hashlib.sha256((HERE / rel).read_bytes()).hexdigest() == digest, f"vendored {rel}")
    text = (HERE / "vendor/TENSOR.md").read_text()
    for p in PHRASES:
        need(p in text, f"TENSOR.md: {p[:40]}")
    res = json.loads((HERE / "vendor/RESULT.json").read_text())["strictification"]
    T = {int(k): v for k, v in res["targets"].items()}
    P = {int(k): v for k, v in res["paid"].items()}
    ni = res["native_inventory"]
    need({int(k): v for k, v in ni["targets"].items()} == T and {int(k): v for k, v in ni["paid"].items()} == P,
         "the strictification invoice is the native inventory's")
    need(T == {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
         and P == {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}, "the TENSOR.md invoice")
    B = sum(T.values())
    need(B == 7688 == ni["productive_fields"] and sum(P.values()) == 55998 == ni["paid_calls"], "counts")
    T1, P1 = sum(r * n for r, n in T.items()), sum(r * n for r, n in P.items())
    need((T1, P1) == (131723, 131115) and T1 - P1 == ni["rank_margin"] == 608, "rank-one moments and surplus")
    need(max(T) == 121 == ni["dimension"], "ambient 121")

    # the three ratios at the tested saving
    C = Q(res["tested_saving"])
    need(C == Q(33581, 12500000) and str(C.numerator * 10**8 // C.denominator) == "268648", "tested saving 0.00268648")
    R = ratios(T, P, C, B, 11, 10)
    need(R["alpha"][1] < 1 - Q(1, 10**8), "alpha < 1 - 1e-8")
    need(R["gamma"][1] < Q(4991, 5000), "gamma < 4991/5000 (c = 10)")
    need(R["delta"][1] < Q(2, 3), "delta < 2/3 (b = 11)")
    for k in ("alpha", "gamma", "delta"):
        lo, hi = R[k]
        claimed = (Q(res[f"{k}_interval"]["lower"]), Q(res[f"{k}_interval"]["upper"]))
        need(hi - lo < Q(1, 10**30) and not (hi < claimed[0] or lo > claimed[1]), f"{k} enclosure overlaps #4416's")

    # the closing argument at v = 6240
    v = 6240
    need(v == 16 * 390 and Q(4991, 5000) ** 390 < Q(1, 2) and Q(2, 3) ** 2 < Q(1, 2), "integer comparisons")
    need((1 - Q(1, 10**8)) ** 16 * (1 + 16 * Q(1, 10**8)) <= 1, "Bernoulli step, checked on a small power")
    bound = 1 / (1 + v * Q(1, 10**8)) + 4 * Q(1, 2**16)
    need(bound == Q(res["normalized_moment_upper_rational"]) and 1 - bound == Q(res["strictification_gap_rational"]), "normalized bound and gap")
    need(1 - bound > Q("0.00000136095023295546"), "gap as stated")

    # headroom: the limit saving C* with alpha = 1 (gamma, delta stay below 1 there)
    lo, hi = C, Q(3, 1000)
    need(ratios(T, P, hi, B, 11, 10)["alpha"][0] > 1, "alpha > 1 at 0.003")
    for _ in range(30):
        mid = (lo + hi) / 2
        if ratios(T, P, mid, B, 11, 10)["alpha"][1] < 1:
            lo = mid
        else:
            hi = mid
    Rs = ratios(T, P, hi, B, 11, 10)
    need(Rs["gamma"][1] < 1 and Rs["delta"][1] < 1, "gamma, delta < 1 at C*")

    # control: completing every target to the full ambient (b = 121) breaks the completion tail
    need(ratios(T, P, C, B, 121, 10)["delta"][0] > 1, "control: b = 121 gives delta > 1")
    need(Q(P1, 1) / power_moment(T, C)[1] > 1, "control: an undamped rank-one tail P_1/T_tau exceeds one")

    print(json.dumps({
        "status": "PASS_PR4416_MOMENT_CHECK",
        "alpha": f"{float(R['alpha'][1]):.15f}", "one_minus_alpha": f"{float(1 - R['alpha'][1]):.4e}",
        "gamma": f"{float(R['gamma'][1]):.12f}", "delta": f"{float(R['delta'][1]):.12f}",
        "gap": str(1 - bound),
        "limit_saving_C_star": [f"{float(lo):.12f}", f"{float(hi):.12f}"],
        "headroom_over_tested": f"{float(lo - C):.4e}",
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
