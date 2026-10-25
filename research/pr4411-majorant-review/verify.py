#!/usr/bin/env python3
"""Independent review of #4411's logarithmic majorant L(n) <= F(n) = n^t (1 + log2 n)^(1/q).

Part A  certified arithmetic for both families: theta = log r_max / log k_min < theta_bar (exact integers),
        condition (2) 2^(b-a) r_max^b <= m^a, condition (3) theta_bar < eta^q with eta = t m^(t-1), condition (4)
        m^(q(1-t)) < 2, and the four integer rank comparisons (1 + H)^den < 2^(num H) with H - 1 controls.
Part B  the separate aggregated lockstep-flow simulator of #4404 (FINITE-PRECOMPILATION.md section 3), with exact
        rational L(N) for every N <= NMAX, checked against F(N) (float comparison with 1e-9 relative margin) and
        against the exact recurrence identities.
Separately written; imports nothing from #4411.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from math import factorial, log
import json
import sys

NMAX = 6000
GRID = Q(1, 10**45)
CASES = {
    "complex": {"targets": {6: 192, 7: 56, 8: 93, 9: 1229, 25: 448, 57: 224},
                "paid": {1: 17623, 2: 5065, 3: 1738, 4: 714, 5: 254},
                "t": Q("0.997695"), "theta_bar": Q(9, 10), "q": 9,
                "ranks": [(Q("0.997696"), 2352000), (Q("0.9976995"), 465000)]},
    "BIT": {"targets": {8: 3073, 22: 444, 50: 222},
            "paid": {1: 9261, 2: 9394, 3: 553, 4: 308, 5: 714, 6: 77, 7: 1465},
            "t": Q("0.997231"), "theta_bar": Q(15, 16), "q": 4,
            "ranks": [(Q("0.997240"), 529000), (Q("0.997682"), 7100)]},
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


def ln_big(n):
    """certified bounds of ln n for an integer n >= 1, by reduction to [1, 2)"""
    k = n.bit_length() - 1
    y = Q(n, 2 ** k)
    u = (y - 1) / (y + 1)
    s, term, j = Q(0), u, 0
    while True:
        s += term / (2 * j + 1)
        j += 1
        term *= u * u
        tail = term / (2 * j + 1) / (1 - u * u) if u else Q(0)
        if tail < GRID:
            break
    l2 = LN2
    return down(2 * s + k * l2[0]), up(2 * (s + tail) + k * l2[1])


def passes(H, g, certain):
    """(1 + H) < 2^(g H) decided by certified logs; certain=True requires the inequality to be proven"""
    lo, hi = ln_big(1 + H)
    if certain:
        return hi < g * H * LN2[0]
    return lo < g * H * LN2[1]


def exp_bounds(lo, hi):
    def series(x):
        s, term = Q(0), Q(1)
        for i in range(60):
            s += term
            term = term * x / (i + 1)
        return s, abs(term) * 2
    a, ea = series(lo)
    b, eb = series(hi)
    return down(a - ea), up(b + eb)


def multis(n_types, size):
    if n_types == 0:
        if size == 0:
            yield ()
        return
    for x in range(size + 1):
        for rest in multis(n_types - 1, size - x):
            yield (x,) + rest


def flow(N, W, P):
    ks = sorted(W)
    m = ks[-1]
    def c(a):
        v = 1
        for k, x in zip(ks, a):
            v *= k ** x
        return v
    def u(a):
        v = factorial(sum(a))
        for k, x in zip(ks, a):
            v = v // factorial(x) * W[k] ** x
        return v
    G = 0
    while any(m * c(a) <= N for a in multis(len(ks), G + 1)):
        G += 1
    F = [{1: 1}]                          # F[d][rho]: number of length-d paid sequences with dilation rho
    for d in range(1, G + 1):
        nxt = {}
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                if m * rho * r <= N:
                    nxt[rho * r] = nxt.get(rho * r, 0) + cnt * pr
        F.append(nxt)
    surplus = sum(k * w for k, w in W.items()) - sum(r * p for r, p in P.items())
    S, X, col_mass = {}, {}, 0
    for d in range(G + 1):
        for rho, cnt in F[d].items():
            for a in multis(len(ks), G - d):
                col = rho * c(a)
                if m * col > N:
                    continue
                col_mass += cnt * u(a) * col
                if d == G:
                    for r, pr in P.items():
                        X[r * col] = X.get(r * col, 0) + cnt * u(a) * pr
    for a in multis(len(ks), G):          # top class: every target is a source
        if m * c(a) <= N:
            for k in ks:
                S[k * c(a)] = S.get(k * c(a), 0) + W[k] * u(a)
    for d in range(1, G + 1):             # child targets whose parent unit is absent
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                for a in multis(len(ks), G - d):
                    if m * rho * r * c(a) > N:
                        continue
                    for i, k in enumerate(ks):
                        b = list(a)
                        b[i] += 1
                        if m * rho * c(b) > N:
                            S[rho * r * c(b)] = S.get(rho * r * c(b), 0) + cnt * pr * u(a) * W[k]
    return G, S, X, col_mass * surplus




def simulate(case):
    W, P = case["targets"], case["paid"]
    m = max(W)
    t, qq = float(case["t"]), case["q"]
    L = [Q(0), Q(1)]
    worst = 0.0
    for N in range(2, NMAX + 1):
        if N < m:
            val = Q(N)
        else:
            G, S, X, pot = flow(N, W, P)
            need(all(m * s > N and s <= N for s in S) and all(e < N for e in X), f"N={N}: ranks")
            need(sum(s * v for s, v in S.items()) - sum(e * v for e, v in X.items()) == pot, f"N={N}: potential")
            tot = sum(S.values())
            val = (sum(v * L[N - s] for s, v in S.items()) + sum(v * L[e] for e, v in X.items())) / tot
        F = N ** t * (1 + log(N, 2)) ** (1 / qq)
        need(float(val) <= F * (1 - 1e-9), f"N={N}: L(N) <= F(N)")
        worst = max(worst, float(val) / F)
        L.append(val)
    return worst


def main():
    global LN2
    LN2 = ln_bounds(2)
    out = {"status": "PASS_PR4411_MAJORANT_REVIEW", "new_kappa_claimed": False, "cases": {}}
    for name, case in CASES.items():
        W, P = case["targets"], case["paid"]
        m, kmin, rmax = max(W), min(W), max(P)
        t, tb, qq = case["t"], case["theta_bar"], case["q"]
        a, b = tb.numerator, tb.denominator
        need(rmax ** b < kmin ** a, "theta < theta_bar")
        need(2 ** (b - a) * rmax ** b <= m ** a, "condition (2)")
        lnm = ln_bounds(m)
        # eta^q = t^q exp(q (t-1) ln m); lower bound uses the upper bound of ln m
        eta_q_lo = t ** qq * exp_bounds(qq * (t - 1) * lnm[1], qq * (t - 1) * lnm[1])[0]
        need(eta_q_lo > tb, "condition (3): theta_bar < eta^q")
        eta_q_hi = t ** qq * exp_bounds(qq * (t - 1) * lnm[0], qq * (t - 1) * lnm[0])[1]
        need(exp_bounds(qq * (1 - t) * lnm[1], qq * (1 - t) * lnm[1])[1] < 2, "condition (4)")
        ranks = []
        for z, H in case["ranks"]:
            g = qq * (z - t)                   # need 1 + H < 2^(g H)
            num, den = g.numerator, g.denominator
            need(passes(H, g, True), f"rank H={H} certified")
            lo_h, hi_h = 1, H                  # least certified H, by bisection on the monotone test
            while lo_h < hi_h:
                mid = (lo_h + hi_h) // 2
                if passes(mid, g, True):
                    hi_h = mid
                else:
                    lo_h = mid + 1
            need(not passes(lo_h - 1, g, False) or lo_h == 1, "one less is certified to fail")
            ranks.append({"stated_H": H, "least_H": lo_h})
        worst = simulate(case)
        out["cases"][name] = {"eta_q_minus_theta_bar": [f"{float(eta_q_lo - tb):.12f}", f"{float(eta_q_hi - tb):.12f}"],
                              "ranks_H": ranks, "flows_to": NMAX, "max_L_over_F": f"{worst:.4f}"}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
