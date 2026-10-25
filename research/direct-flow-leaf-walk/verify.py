#!/usr/bin/env python3
"""The leaf-exit walk of #4436's direct p7 flow: sqrt(G) regime now, predicted saturation later.

A leaf exit of the direct flow at rank N is r*rho, rho a product of G = floor(log5(N/m)) letters of P with
m*rho*r <= N at each step; its t*-potential weight is cnt(rho) P_r (r rho)^t*. Since every step ln r >= 0, only the
final constraint binds: S_G = ln rho <= B = ln(N/m). This verifier computes the leaf log-depth
    D(G) = E[ln(N / (r rho))]   (t*-potential weights)   at N = 121 * 5^G, exactly from F[G], for G = 2..40,
and checks: D fits a + b sqrt(G) (max residual < 0.08, b close to sigma sqrt(2/pi)) far better than a linear or a
logarithmic law; increments are decreasing. It also computes the tilted step law: mean mu > ln 5, sigma, the Esscher
parameter lambda* with tilted mean ln 5, and the crossover G_x = sigma^2 / (mu - ln 5)^2. For G >> G_x the conditioned
overshoot B - S_G tends to Exp(lambda*), so D saturates near ln m - E[ln r] + 1/lambda*: the log-gap g of #4465 then
stays bounded and the refined-induction cap stays strictly below s*. Floating point; the saturation is an asymptotic
heuristic, not a proof. Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
import math
import sys

P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
W = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
M = 121


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def root():
    f = lambda t: sum(W[k] * k ** t for k in W) - sum(P[r] * r ** t for r in P)
    lo, hi = 0.99, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if f(mid) > 0 else (mid, hi)
    return (lo + hi) / 2


def leaf_depth(N, ts):
    G = 0
    while 5 ** (G + 1) <= N // M:
        G += 1
    F = {1: 1.0}
    for _ in range(G):
        nxt = {}
        for rho, c in F.items():
            for r, pr in P.items():
                if M * rho * r <= N:
                    nxt[rho * r] = nxt.get(rho * r, 0.0) + c * pr
        s = sum(nxt.values())
        F = {k: v / s for k, v in nxt.items()}
    num = den = 0.0
    for rho, c in F.items():
        for r, pr in P.items():
            w = c * pr * (r * rho) ** ts
            num += w * math.log(N / (r * rho))
            den += w
    return G, num / den


def fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    return a, b, max(abs(y - a - b * x) for x, y in zip(xs, ys))


def tilted(s):
    w = {r: P[r] * r ** s for r in P}
    z = sum(w.values())
    m1 = sum(w[r] * math.log(r) for r in P) / z
    return m1, sum(w[r] * math.log(r) ** 2 for r in P) / z - m1 * m1


def main():
    ts = root()
    D = {}
    for G in range(2, 41):
        g, d = leaf_depth(M * 5 ** G, ts)
        need(g == G, "level")
        D[G] = d
    sel = [G for G in D if G >= 7]
    a, b, res = fit([math.sqrt(G) for G in sel], [D[G] for G in sel])
    _, _, res_lin = fit(sel, [D[G] for G in sel])
    _, _, res_log = fit([math.log(G) for G in sel], [D[G] for G in sel])
    mu, var = tilted(ts)
    sigma = math.sqrt(var)
    need(res < 0.08 and res_lin > 0.25 and res_log > 0.25, "sqrt(G) law fits far better than linear or logarithmic")
    need(abs(b - sigma * math.sqrt(2 / math.pi)) < 0.15, "slope close to the CLT value sigma sqrt(2/pi)")
    inc = [D[G + 10] - D[G] for G in range(10, 31, 10)]
    need(all(x > y for x, y in zip(inc, inc[1:])), "increments decrease (concave growth)")
    need(mu > math.log(5), "tilted mean exceeds the barrier slope ln 5")
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tilted(ts - mid)[0] > math.log(5) else (lo, mid)
    lam = (lo + hi) / 2
    offset = math.log(M) - mu
    need(abs(offset - a) < 0.3, "fitted intercept matches ln m - E[ln r]")
    print(json.dumps({"status": "PASS_DIRECT_FLOW_LEAF_WALK", "t_star": f"{ts:.12f}",
                      "leaf_depth": {G: round(D[G], 4) for G in (2, 5, 10, 20, 30, 40)},
                      "sqrt_fit": {"a": round(a, 4), "b": round(b, 4), "max_residual": round(res, 4)},
                      "linear_fit_max_residual": round(res_lin, 4), "log_fit_max_residual": round(res_log, 4),
                      "tilted_step": {"mu": round(mu, 6), "sigma": round(sigma, 6), "mu_minus_ln5": round(mu - math.log(5), 6)},
                      "esscher_lambda": round(lam, 6), "saturation_depth_estimate": round(offset + 1 / lam, 2),
                      "crossover_G": round(var / (mu - math.log(5)) ** 2), "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
