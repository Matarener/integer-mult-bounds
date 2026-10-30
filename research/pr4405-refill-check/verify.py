#!/usr/bin/env python3
"""Independent check of #4405's refined template ranks and endpoint slack family (refining #4359).

Part A  the refined induction needs only exit coefficient <= eta = z0 m^(z0-1). With certified logarithms,
        H0 = least integer with h delta H0 >= 4 delta - log2(eta), H1 = floor(H0 (1-z0)/(z-z0)) + 1;
        recompute #4405's (335449, 1546084442) complex and (69740, 42843607) BIT, both minimal, and the
        endpoint rank exponent 2099384703303215709.
Part B  levers: (i) the intermediate z0 -- scan a rational grid and compare with the midpoint;
        (ii) the exit constant 16 -- its share of H0; (iii) the uniform saving -- H1 as it varies.
Part C  endpoint family at kappa = 0.00230509: the tested mixed moment is positive at C_test (so
        C_test < C*), and the self-contained gap identities of ENDPOINT.md hold exactly, also on a sweep of
        rational kappa.
Separately written; imports nothing from #4405 or #4359. Invoices embedded as printed in #4359.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
import sys

GRID = Q(1, 10**45)
CASES = {
    "complex": {"targets": {6: 192, 7: 56, 8: 93, 9: 1229, 25: 448, 57: 224},
                "paid": {1: 17623, 2: 5065, 3: 1738, 4: 714, 5: 254},
                "tested": Q(461, 200000), "uniform": Q(36, 15625), "h": Q(1, 10),
                "H0": 335449, "H1": 1546084442, "old_H1": 276540184361},
    "BIT": {"targets": {8: 3073, 22: 444, 50: 222},
            "paid": {1: 9261, 2: 9394, 3: 553, 4: 308, 5: 714, 6: 77, 7: 1465},
            "tested": Q(2769, 1000000), "uniform": Q(69, 25000), "h": Q(1, 16),
            "H0": 69740, "H1": 42843607, "old_H1": 6552928412},
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def down(x):
    return (x / GRID).__floor__() * GRID


def up(x):
    return (x / GRID).__ceil__() * GRID


def ln_bounds(k):
    y = Q(k - 1, k + 1)
    s, term, n = Q(0), y, 0
    while True:
        s += term / (2 * n + 1)
        n += 1
        term *= y * y
        tail = term / (2 * n + 1) / (1 - y * y)
        if tail < GRID:
            return down(2 * s), up(2 * (s + tail))


def exp_small(lo, hi):
    def series(x):
        s, term = Q(0), Q(1)
        for i in range(60):
            s += term
            term = term * x / (i + 1)
        return s, abs(term) * 2
    a, ea = series(lo)
    b, eb = series(hi)
    return down(a - ea), up(b + eb)


def balance(case, saving, logs):
    """bounds of sum W k^(1-C) - sum p r^(1-C)"""
    lo = hi = Q(0)
    for k, w in case["targets"].items():
        e = exp_small(-saving * logs[k][1], -saving * logs[k][0])
        lo, hi = lo + w * k * e[0], hi + w * k * e[1]
    for r, pr in case["paid"].items():
        e = exp_small(-saving * logs[r][1], -saving * logs[r][0])
        lo, hi = lo - pr * r * e[1], hi - pr * r * e[0]
    return lo, hi


def ranks(t, z0, z, h, m, logs):
    """least H0 certified to give (16 2^(-h H0))^delta <= eta, and H1"""
    delta = z0 - t
    ln2 = logs[2]
    # log2 eta = log2 z0 + (z0 - 1) log2 m ; z0 close to 1: log z0 = -sum (1-z0)^j / j
    x = 1 - z0
    s, term = Q(0), x
    for j in range(1, 40):
        s += term / j
        term *= x
    ln_z0 = (-(s + term / (1 - x)), -s)
    l2_lo = ln_z0[0] / ln2[0] + (z0 - 1) * logs[m][1] / ln2[0]
    l2_hi = ln_z0[1] / ln2[1] + (z0 - 1) * logs[m][0] / ln2[1]
    need(l2_lo <= l2_hi < 0, "log2 eta enclosure")
    need_lo = 4 * delta - l2_hi            # smallest possible requirement
    need_hi = 4 * delta - l2_lo            # largest possible requirement
    H0 = -((-need_hi) // (h * delta))      # ceil: certified sufficient
    certain_fail = h * delta * (H0 - 1) < need_lo
    ratio = H0 * (1 - z0) / (z - z0)
    H1 = ratio.numerator // ratio.denominator + 1
    need(H1 * (z - z0) > H0 * (1 - z0) and not (H1 - 1) * (z - z0) > H0 * (1 - z0), "H1 minimal")
    return H0, H1, certain_fail, (4 * delta) / need_hi


def main():
    logs = {k: ln_bounds(k) for k in (2, 3, 4, 5, 6, 7, 8, 9, 22, 25, 50, 57)}
    logs[1] = (Q(0), Q(0))
    out = {"status": "PASS_PR4405_REFILL_INDEPENDENT_CHECK", "new_kappa_claimed": False, "cases": {}}
    for name, case in CASES.items():
        m = max(case["targets"])
        t, z = 1 - case["tested"], 1 - case["uniform"]
        z0 = (t + z) / 2
        H0, H1, minimal, share16 = ranks(t, z0, z, case["h"], m, logs)
        need(H0 == case["H0"] and H1 == case["H1"] and minimal, f"{name}: #4405 H0/H1 reproduced and minimal")
        need(case["old_H1"] // H1 > 150, "factor > 150 over #4359")
        # lever (i): z0 grid
        best = (H1, z0)
        for j in range(1, 200):
            zz = t + (z - t) * j / 200
            _, h1, _, _ = ranks(t, zz, z, case["h"], m, logs)
            if h1 < best[0]:
                best = (h1, zz)
        # lever (iii): uniform saving
        curve = []
        for u in (Q(23, 10000), Q(2302, 1000000), Q(2303, 1000000), case["uniform"]):
            if u >= case["tested"]:
                continue
            zu = 1 - u
            _, h1u, _, _ = ranks(t, (t + zu) / 2, zu, case["h"], m, logs)
            curve.append({"uniform_saving": str(u), "H1": h1u})
        out["cases"][name] = {
            "H0": H0, "H1": H1, "midpoint_H1": H1,
            "best_grid_z0_H1": best[0], "z0_gain": f"{1 - best[0] / H1:.4%}",
            "exit_constant_16_share_of_H0": f"{float(share16):.2e}",
            "H1_vs_uniform_saving": curve,
        }

    # Part C: endpoint
    cx = CASES["complex"]
    kappa, c_test = Q("0.00230509"), Q("0.00230509019")
    bal = balance(cx, c_test, logs)
    need(bal[0] > 0, "mixed moment positive at C_test, so C_test < C*")
    bal_hi = balance(cx, Q("0.002306"), logs)
    need(bal_hi[1] < 0, "C* < 0.002306")
    sweep = [kappa] + [Q(k, 10**7) for k in range(1, 23051, 997)]
    for kap in sweep:
        ct = c_test if kap == kappa else (kap + Q("0.00230509")) / 2 if kap < Q("0.00230509") else None
        if ct is None:
            continue
        d = (ct - kap) / 7
        uniform, b, a, q = kap + 6 * d, kap + 5 * d, kap + 4 * d, kap + 3 * d
        eps, beta, r0, stop, layout = 1 - d, 1 - 3 * d, d / 10, d, d
        xi = eps * (1 + q) - Q(3, 32) + layout
        need(xi == Q(29, 32) + (1 - d) * q, "xi identity")
        need(eps * q == kap + d * (3 - q) and eps * q > kap, "main-transform saving")
        lam, lam_p, tau, sigma = 1 - (q + a) / 2, 1 - q, 1 - a, 1 - b
        need(lam - tau == d / 2 and lam - sigma == 3 * d / 2 and lam_p - lam == d / 2, "stopped-supplier gaps")
        need((1 - stop) * b - a == d * (1 - b) > 0, "stop gap")
        need(eps - xi == Q(3, 32) - d - (1 - d) * q > 0, "epsilon - xi")
        need(1 - (2 * xi - 2) - r0 - beta == Q(3, 16) - 2 * (1 - d) * q + Q(29, 10) * d > 0, "precision guard gap")
        need(0 < d < Q(1, 3000) and 0 < q < a < b < uniform < ct, "parameter order")
        need(Q(1, 2) < xi < eps < 1 and 0 < beta < eps and b < Q(1, 32), "geometric gaps")
    # endpoint rank
    d = (c_test - kappa) / 7
    z = 1 - (kappa + 6 * d)
    t = 1 - c_test
    _, H1e, _, _ = ranks(t, (t + z) / 2, z, cx["h"], 57, logs)
    need(H1e == 2099384703303215709, "#4405 endpoint rank exponent")
    out["endpoint"] = {"kappa": str(kappa), "C_test": str(c_test), "moment_at_C_test": f"{float(bal[0]):.3e}",
                       "H1": H1e, "kappa_sweep_points": len(sweep)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
