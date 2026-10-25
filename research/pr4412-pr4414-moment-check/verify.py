#!/usr/bin/env python3
"""Independent certified check of the strictification inequalities in #4412 and #4414.

Both build a tensor power of a native mixed unit with target invoice T and paid invoice P, split paid jobs
at a cutoff J, and need, at saving C (tau = 1 - C), alpha = P_tau/T_tau < 1 and gamma = P_1/(b^C T_tau) < 1:
  #4412: J = 4^n,             alpha < 1 - 1e-9, gamma < 999/1000,   n = 15000,  1/(1+n/1e9) + 2 (999/1000)^n < 1;
  #4414: J = floor((19/4)^v), alpha < 1 - 1e-8, gamma < 9999/10000, v = 150000, 1/(1+v/1e8) + 4/2^15 < 1.
X_tau = sum_r n_r r^tau. Exact rational enclosures: ln by atanh after reducing by powers of two, exp by
Taylor with a remainder. Each invoice's limit saving C* (alpha = 1) is also computed. The four inputs are
vendored byte-identically. No code from #4412 or #4414.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
VENDORED = {
    "vendor/4412-TENSOR.md": "d65a39979a0d44ba85123f9e323614caf8efe5585f3b5ea2cb6091c11ce1acc5",
    "vendor/4412-RESULT.json": "4b0bbf35d51e25c167327ceba9f969eba2a80bd359d5a92964e1c47ba5bce15d",
    "vendor/4414-TENSOR.md": "96e4593ff213a51defba0bcd394deffaa2b9c69292da895cf02d8e33469c27eb",
    "vendor/4414-RESULT.json": "d9a04cbbc4235a187c863a463dc2105c71a6b3bffd2129ca082759d9257845cf",
}
PHRASES = {
    "4412": ["targets = {5:196, 6:126, 7:392, 8:651, 9:1491, 25:448, 57:224},",
             "paid    = {1:17409, 2:4991, 3:1568, 4:714, 5:140, 8:504, 16:448}.",
             "alpha < 999999999/1000000000,", "gamma = P_1/(4^C*T_tau) < 999/1000.",
             "Use `n=15000`, `J=4^15000`.", "1/(1+15000/10^9) + 2*(999/1000)^15000 < 1.",
             "The certified surplus is greater than `0.00001439`."],
    "4414": ["T = {5:364,6:234,7:728,8:1209,9:2769,25:448,41:448,57:224,105:224},",
             "P = {1:32331,2:9269,3:2912,4:1326,5:260,8:1224,16:448,32:448,48:224}.",
             "gamma < 9999/10000.", "Take v=150000. The exact finite inequality",
             "`(9999/10000)^10000<1/2` gives gamma^v<2^-15.", "1/(1+150000/10^8) + 4/2^15 < 1.",
             "<= alpha^v+2^(1+C)*gamma^v < alpha^v+4*gamma^v."],
}


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



def ratios(T, P, C, b):
    t_lo, t_hi = power_moment(T, C)
    p_lo, p_hi = power_moment(P, C)
    l_lo, l_hi = ln_bounds(Q(b))
    bc_lo, bc_hi = exp_bounds(C * l_lo)[0], exp_bounds(C * l_hi)[1]
    P1 = sum(r * n for r, n in P.items())
    return {"alpha": (p_lo / t_hi, p_hi / t_lo), "gamma": (P1 / (bc_hi * t_hi), P1 / (bc_lo * t_lo))}


def limit_saving(T, P, lo, hi):
    for _ in range(30):
        mid = (lo + hi) / 2
        if ratios(T, P, mid, 4)["alpha"][1] < 1:
            lo = mid
        else:
            hi = mid
    return lo, hi


def load(tag):
    text = (HERE / f"vendor/{tag}-TENSOR.md").read_text()
    for p in PHRASES[tag]:
        need(p in text, f"#{tag} TENSOR.md: {p[:40]}")
    s = json.loads((HERE / f"vendor/{tag}-RESULT.json").read_text())["strictification"]
    T = {int(k): v for k, v in s["targets"].items()}
    P = {int(k): v for k, v in s["paid"].items()}
    ni = s["native_inventory"]
    need({int(k): v for k, v in ni["targets"].items()} == T and {int(k): v for k, v in ni["paid"].items()} == P,
         f"#{tag}: strictification invoice is the native inventory's")
    return s, T, P


def check_interval(tag, s, R):
    for k in ("alpha", "gamma"):
        lo, hi = R[k]
        cl = (Q(s[f"{k}_interval"]["lower"]), Q(s[f"{k}_interval"]["upper"]))
        need(hi - lo < Q(1, 10**30) and not (hi < cl[0] or lo > cl[1]), f"#{tag} {k} overlaps the recorded interval")


def main():
    for rel, digest in VENDORED.items():
        need(hashlib.sha256((HERE / rel).read_bytes()).hexdigest() == digest, f"vendored {rel}")
    out = {}

    # #4412
    s, T, P = load("4412")
    need((sum(T.values()), sum(r * n for r, n in T.items()), sum(r * n for r, n in P.items()), sum(P.values())) == (3528, 47075, 46851, 25774), "#4412 invoice aggregates")
    C = Q(s["tested_saving"])
    need(C == Q(61939, 25000000), "#4412 tested saving 0.00247756")
    R = ratios(T, P, C, 4)
    need(R["alpha"][1] < Q(999999999, 10**9) and R["gamma"][1] < Q(999, 1000), "#4412 alpha < 1 - 1e-9, gamma < 999/1000")
    check_interval("4412", s, R)
    n = 15000
    bound = 1 / (1 + n * Q(1, 10**9)) + 2 * Q(999, 1000) ** n
    need(bound < 1 and 1 - bound > Q(1439, 10**8), "#4412 closing bound and surplus > 0.00001439")
    g = s["strictification_gap"]
    need(Q(g["lower"]) <= 1 - bound <= Q(g["upper"]), "#4412 gap inside the recorded interval")
    need(max(P) == 16 and min(T) == 5, "#4412 cutoff base 4 lies below the minimum target 5")
    Cs = limit_saving(T, P, C, Q(3, 1000))
    need(ratios(T, P, Cs[1], 4)["gamma"][1] < 1, "#4412 gamma < 1 at the limit saving")
    out["4412"] = {"alpha": f"{float(R['alpha'][1]):.12f}", "one_minus_alpha": f"{float(1 - R['alpha'][1]):.4e}",
                   "gamma": f"{float(R['gamma'][1]):.10f}", "gap": f"{float(1 - bound):.10e}",
                   "limit_saving": f"{float(Cs[0]):.12f}", "headroom": f"{float(Cs[0] - C):.4e}"}

    # #4414
    s, T, P = load("4414")
    need((sum(T.values()), sum(r * n for r, n in T.items()), sum(r * n for r, n in P.items()), sum(P.values())) == (6648, 108769, 108257, 48442), "#4414 invoice aggregates")
    C = Q(s["tested_saving"])
    need(C == Q(66997, 25000000), "#4414 tested saving 0.00267988")
    R = ratios(T, P, C, Q(19, 4))
    need(R["alpha"][1] < 1 - Q(1, 10**8) and R["gamma"][1] < Q(9999, 10000), "#4414 alpha < 1 - 1e-8, gamma < 9999/10000")
    check_interval("4414", s, R)
    v = 150000
    need(v == 15 * 10000 and Q(9999, 10000) ** 10000 < Q(1, 2), "#4414 (9999/10000)^10000 < 1/2")
    need(Q(19, 4) < 5 and Q(2) ** 2 == 4, "#4414 floor cutoff below the minimum target 5^v; 2^(1+C) < 4")
    bound = 1 / (1 + v * Q(1, 10**8)) + 4 * Q(1, 2**15)
    need(bound == Q(s["normalized_moment_upper_rational"]) == Q(16386003, 16408576) and 1 - bound == Q(s["strictification_gap_rational"]), "#4414 normalized bound and gap")
    need(ratios(T, P, C, 4)["gamma"][0] > 1, "#4414 control: integer cutoff base 4 fails the tail (gamma > 1)")
    Cs = limit_saving(T, P, C, Q(3, 1000))
    need(ratios(T, P, Cs[1], Q(19, 4))["gamma"][1] < 1, "#4414 gamma < 1 at the limit saving")
    out["4414"] = {"alpha": f"{float(R['alpha'][1]):.12f}", "one_minus_alpha": f"{float(1 - R['alpha'][1]):.4e}",
                   "gamma": f"{float(R['gamma'][1]):.10f}", "gap": str(1 - bound),
                   "limit_saving": f"{float(Cs[0]):.12f}", "headroom": f"{float(Cs[0] - C):.4e}"}

    print(json.dumps({"status": "PASS_PR4412_PR4414_MOMENT_CHECK", **out, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
