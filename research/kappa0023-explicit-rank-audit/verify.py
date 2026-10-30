#!/usr/bin/env python3
"""Independent check of #4359's explicit-rank chain (EXPLICIT-TEMPLATE-BOUNDS.md, FINITE-PRECOMPILATION.md 3-5).

Separately written; imports nothing from #4359. Inputs are the two p3 invoices as printed in
#4359's PR body and EXPLICIT-TEMPLATE-BOUNDS.json.

Part A  certified logarithm/exponential enclosures: the superpotential sum_paid r^t < sum_targets W_k k^t
        at the tested t, the mixed-balance root bracket, and eta = z0 m^(z0-1) > 1/4.
Part B  the exact rational chain: theta < theta_bar, m^h < 2, 2 r_max <= 16, H0 and H1 from their formulas,
        the exit coefficient (16 n0^-h)^delta <= 1/8 and A N^z0 < N^z, with +-1 controls.
Part C  an aggregated simulation of the section 3 integer lockstep flow (classes grouped by dilation)
        at every top rank N <= NMAX: sources lie in (N/m, N], exits are at most r_max^(G+1) <= E(N),
        and the rank-one potential identity sum_s S_s s - sum_e X_e e = surplus * sum_units col holds
        exactly; the leaf recurrence L(N) obeys L(N) <= N.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from math import factorial, log
import json
import sys

CASES = {
    "complex": {
        "targets": {6: 192, 7: 56, 8: 93, 9: 1229, 25: 448, 57: 224},
        "paid": {1: 17623, 2: 5065, 3: 1738, 4: 714, 5: 254},
        "t": Q(199539, 200000), "z0": Q(1995391, 2000000), "z": Q(15589, 15625), "theta_bar": Q(9, 10),
        "H0": 60000040, "H1": 276540184361, "surplus": 224,
        "root": (Q("0.002305090194876170622919094755"), Q("0.002305090194876170622919094756")),
    },
    "BIT": {
        "targets": {8: 3073, 22: 444, 50: 222},
        "paid": {1: 9261, 2: 9394, 3: 553, 4: 308, 5: 714, 6: 77, 7: 1465},
        "t": Q(997231, 1000000), "z0": Q(1994471, 2000000), "z": Q(24931, 25000), "theta_bar": Q(15, 16),
        "H0": 10666731, "H1": 6552928412, "surplus": 225,
        "root": (Q("0.002769830250"), Q("0.002769830251")),
    },
}
NMAX = 10000
GRID = Q(1, 10**45)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def down(x):
    return (x / GRID).__floor__() * GRID


def up(x):
    return (x / GRID).__ceil__() * GRID


def ln_bounds(k):
    """ln k = 2 atanh(y), y = (k-1)/(k+1); positive series with geometric tail bound"""
    y = Q(k - 1, k + 1)
    s, term, n = Q(0), y, 0
    while True:
        s += term / (2 * n + 1)
        n += 1
        term *= y * y
        tail = term / (2 * n + 1) / (1 - y * y)
        if tail < GRID:
            return down(2 * s), up(2 * (s + tail))


def exp_bounds(lo, hi):
    """bounds of exp(x) for x in [lo, hi], |x| small enough for direct Taylor with remainder"""
    def series(x):
        s, term = Q(0), Q(1)
        for i in range(80):
            s += term
            term = term * x / (i + 1)
        rem = abs(term) * 2
        return s - rem, s + rem
    need(abs(lo) < 1 and abs(hi) < 1, "small exponent")
    return down(series(lo)[0]), up(series(hi)[1])


def power_bounds(k, t, lnk):
    """k^t = k * exp(-(1-t) ln k) for t close to 1"""
    e_lo, e_hi = exp_bounds(-(1 - t) * lnk[1], -(1 - t) * lnk[0])
    return k * e_lo, k * e_hi


def balance(case, t, logs):
    """bounds of sum_targets W k^t - sum_paid p r^t"""
    lo = hi = Q(0)
    for k, w in case["targets"].items():
        a, b = power_bounds(k, t, logs[k])
        lo, hi = lo + w * a, hi + w * b
    for r, p in case["paid"].items():
        a, b = power_bounds(r, t, logs[r])
        lo, hi = lo - p * b, hi - p * a
    return lo, hi


def ceil_q(x):
    return -((-x.numerator) // x.denominator)


# ---- Part C: aggregated lockstep flow --------------------------------------------------------

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
    m, kmin, rmax = max(W), min(W), max(P)
    a, b = case["theta_bar"].numerator, case["theta_bar"].denominator
    L = [Q(0), Q(1)]
    flows = 0
    for N in range(2, NMAX + 1):
        if N < m:
            L.append(Q(N))                 # ordinary sequential base program
            continue
        G, S, X, pot = flow(N, W, P)
        flows += 1
        need(all(m * s > N and s <= N for s in S), f"N={N}: sources in (N/m, N]")
        e_cap = rmax ** (G + 1)
        need(all(e <= e_cap and e < N for e in X), f"N={N}: exits at most r_max^(G+1)")
        # r_max^(G+1) <= r_max (N/m)^theta_bar, via k_min^G <= N/m and r_max^b < k_min^a
        need(kmin ** G * m <= N and (rmax ** G) ** b <= (Q(N, m)) ** a, f"N={N}: exit rank exponent")
        lhs = sum(s * v for s, v in S.items()) - sum(e * v for e, v in X.items())
        need(lhs == pot, f"N={N}: exact rank-one potential identity")
        tot = sum(S.values())
        val = (sum(v * L[N - s] for s, v in S.items()) + sum(v * L[e] for e, v in X.items())) / tot
        need(val <= N, f"N={N}: L(N) <= N")
        L.append(val)
    return flows, L


def main():
    out = {"status": "PASS_KAPPA0023_EXPLICIT_RANK_AUDIT", "new_kappa_claimed": False, "cases": {}}
    for name, case in CASES.items():
        W, P = case["targets"], case["paid"]
        m, kmin, rmax = max(W), min(W), max(P)
        t, z0, z, tb = case["t"], case["z0"], case["z"], case["theta_bar"]
        need(sum(W.values()) in (2242, 3739) and sum(P.values()) in (25394, 21772), "invoice totals")
        logs = {k: ln_bounds(k) for k in set(W) | set(P) | {2}}

        # Part A
        sp = balance(case, t, logs)
        need(sp[0] > 0, "strict superpotential at t")
        r_lo, r_hi = case["root"]
        at_lo = balance(case, 1 - r_lo, logs)     # exponent 1 - C below the root's C: targets lose
        at_hi = balance(case, 1 - r_hi, logs)
        need(at_lo[1] < 0 < at_hi[0] or at_hi[1] < 0 < at_lo[0], "author's root bracket straddles the balance")
        surplus = sum(k * w for k, w in W.items()) - sum(r * p for r, p in P.items())
        need(surplus == case["surplus"] > 0, "rank-one surplus")
        need(z0 > Q(1, 2) and (1 - z0) * logs[m][1] < logs[2][0], "eta = z0 m^(z0-1) > 1/4")

        # Part B
        delta, h = z0 - t, 1 - tb
        need(0 < t < z0 < z < 1, "exponent order")
        need(rmax ** tb.denominator < kmin ** tb.numerator, "theta = log r_max / log k_min < theta_bar")
        need(m ** h.numerator < 2 ** h.denominator and 2 * rmax <= 16, "m^h < 2 and 2 r_max <= 16")
        H0 = ceil_q((3 + 4 * delta) / (h * delta))
        need(H0 == case["H0"], "H0 formula")
        # (16 * 2^(-H0 h))^delta <= 1/8  <=>  H0 h delta >= 3 + 4 delta (base-2 exponents)
        need(H0 * h * delta >= 3 + 4 * delta and (H0 - 1) * h * delta < 3 + 4 * delta, "H0 minimal for 1/8")
        ratio = H0 * (1 - z0) / (z - z0)
        H1 = ratio.numerator // ratio.denominator + 1
        need(H1 == case["H1"], "H1 formula")
        # A N^z0 < N^z  <=>  H0 (1 - z0) < H1 (z - z0)
        need(H0 * (1 - z0) < H1 * (z - z0) and not H0 * (1 - z0) < (H1 - 1) * (z - z0), "H1 minimal")
        need(2 ** 6 > m and H0 > 6, "n0 = 2^H0 exceeds m")

        # Part C
        flows, L = simulate(case)
        out["cases"][name] = {
            "superpotential_at_t": f"{float(sp[0]):.12f}",
            "rank_one_surplus": surplus,
            "H0": H0, "H1": H1,
            "flows_checked": flows, "ranks": f"{m}..{NMAX}",
            "L_at_NMAX": f"{float(L[NMAX]):.6f}",
            "effective_saving_at_NMAX": f"{1 - log(float(L[NMAX])) / log(NMAX):.6f}",
        }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
