#!/usr/bin/env python3
"""Log-gap ceiling of #4405's refined-induction test on #4436's direct p7 flow.

At the unit root t* (sum_k W_k k^t = sum_r P_r r^t) exits and sources carry equal t-potential. With the t*-weighted log
gap g(N) = E_S[ln s] - E_X[ln e], first order gives kappa(N, z0) ~ exp(-(z0 - t*) g) while eta(z0) =
z0 m^(z0 - 1) ~ exp(-(1 - z0)(1 + ln m)), so the test certifies savings up to about s* g / (g + 1 + ln m).
On a 5% grid 1000 <= N <= 5e5 this checks: the potential balance at t*, the first-order formula, that the per-level
(sawtooth) minima of g increase with the lockstep depth G, that this growth comes from the leaf exits alone (boundary
exits and sources keep fixed log-depth), and the pass/fail savings 0.0008 / 0.001.
Floating-point finite evidence. Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
import math
import sys

from math import factorial
def multis(n_types, size):
    if n_types == 0:
        if size == 0: yield ()
        return
    for x in range(size + 1):
        for rest in multis(n_types - 1, size - x): yield (x,) + rest
def flow(N, W, P):
    ks = sorted(W); m = ks[-1]; kmin = ks[0]
    def c(a):
        v = 1
        for k, x in zip(ks, a): v *= k ** x
        return v
    def u(a):
        v = factorial(sum(a))
        for k, x in zip(ks, a): v = v // factorial(x) * W[k] ** x
        return v
    G = 0
    while kmin ** (G + 1) <= N // m: G += 1
    F = [{1: 1}]
    for d in range(1, G + 1):
        nxt = {}
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                if m * rho * r <= N: nxt[rho * r] = nxt.get(rho * r, 0) + cnt * pr
        F.append(nxt)
    S, X, BX = {}, {}, {}
    col = units = matched = 0
    add = lambda D, k, v: D.__setitem__(k, D.get(k, 0) + v)
    present = lambda rho, a: m * rho * c(a) <= N
    for d in range(G + 1):
        for rho, cnt in F[d].items():
            for b in multis(len(ks), G - d):
                if not present(rho, b): continue
                units += cnt * u(b); col += cnt * u(b) * rho * c(b)
                for r, pr in P.items():
                    issued = cnt * pr * u(b); rank = r * rho * c(b)
                    if d == G:
                        add(X, rank, issued); continue
                    D = sum(W[k] * u(tuple(x - (i == j) for j, x in enumerate(b)))
                            for i, k in enumerate(ks) if b[i] > 0 and present(rho * r, tuple(x - (i == j) for j, x in enumerate(b))))
                    matched += cnt * pr * D
                    if issued - cnt * pr * D:
                        add(X, rank, issued - cnt * pr * D); add(BX, rank, issued - cnt * pr * D)
    for a in multis(len(ks), G):
        if present(1, a):
            for k in ks: add(S, k * c(a), W[k] * u(a))
    for d in range(1, G + 1):
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                for a in multis(len(ks), G - d):
                    if not present(rho * r, a): continue
                    for i, k in enumerate(ks):
                        b = list(a); b[i] += 1
                        if not present(rho, tuple(b)):
                            add(S, rho * r * c(tuple(b)), cnt * pr * u(a) * W[k])
    return dict(G=G, S=S, X=X, BX=BX, col=col, units=units, matched=matched)


W = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
M = 121


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def root():
    f = lambda t: sum(W[k] * k ** t for k in W) - sum(P[r] * r ** t for r in P)
    lo, hi = 0.99, 1.0
    need(f(lo) < 0 < f(hi), "root bracket")
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if f(mid) > 0 else (mid, hi)
    return (lo + hi) / 2


def main():
    ts = root()
    sstar = 1 - ts
    need(abs(sstar - 0.0026865) < 1e-6, "t* matches the p7 root")
    rows = []
    for N in [int(1000 * 1.05 ** i) for i in range(0, 130) if 1000 * 1.05 ** i <= 5e5]:
        R = flow(N, W, P)
        S, X = R["S"], R["X"]
        st = sum(v * s ** ts for s, v in S.items())
        xt = sum(v * e ** ts for e, v in X.items())
        need(abs(xt / st - 1) < 1e-9, f"N={N}: exit and source t*-potentials balance")
        g = (sum(v * s ** ts * math.log(s) for s, v in S.items()) / st
             - sum(v * e ** ts * math.log(e) for e, v in X.items()) / xt)
        kap = {sv: sum(v * e ** (1 - sv) for e, v in X.items()) / sum(v * s ** (1 - sv) for s, v in S.items())
               for sv in (0.0008, 0.001)}
        need(abs(kap[0.001] - math.exp(-(sstar - 0.001) * g)) < 3e-5, f"N={N}: first-order kappa")
        BX = R["BX"]
        leaf = {e: v - BX.get(e, 0) for e, v in X.items() if v != BX.get(e, 0)}
        bd = {e: v for e, v in BX.items() if v}
        depth = lambda D: sum(v * e ** ts * math.log(N / e) for e, v in D.items()) / sum(v * e ** ts for e, v in D.items())
        comp = (depth(leaf), depth(bd) if bd else None, depth(S))
        rows.append((N, R["G"], g, kap, comp))
    mins = {}
    for N, G, g, _, _ in rows:
        if G not in mins or g < mins[G][1]:
            mins[G] = (N, g)
    levels = [mins[G][1] for G in range(2, 6)]
    need(all(a < b for a, b in zip(levels, levels[1:])), "per-level minima of g increase with G")
    need((levels[-1] - levels[0]) / 3 > 0.15, "average growth per level above 0.15")
    eta = lambda sv: (1 - sv) * M ** (-sv)
    need(all(k[0.0008] < eta(0.0008) for N, G, g, k, _ in rows if N >= 3e5), "saving 0.0008 passes for N >= 3e5")
    need(any(k[0.001] > eta(0.001) for N, G, g, k, _ in rows if N >= 3e5), "saving 0.001 still fails somewhere N >= 3e5")
    # decomposition at the per-level minima: only the leaf exits sink; boundary exits and sources stay put
    at = {N: c for N, G, g, k, c in rows}
    comps = {G: at[mins[G][0]] for G in range(2, 6)}
    need(all(abs(comps[G][1] - comps[2][1]) < 0.1 and abs(comps[G][2] - comps[2][2]) < 0.1 for G in comps),
         "boundary-exit and source log-depths are stable across levels")
    need(all(comps[a][0] < comps[b][0] for a, b in zip(range(2, 5), range(3, 6))), "leaf log-depth increases with G")
    tilt = lambda D: sum(D[x] * x ** ts * math.log(x) for x in D) / sum(D[x] * x ** ts for x in D)
    need(tilt(P) - math.log(5) > 0, "tilted P-step mean exceeds the barrier slope ln 5 (positive relative drift)")
    cap = lambda g: sstar * g / (g + 1 + math.log(M))
    print(json.dumps({"status": "PASS_DIRECT_FLOW_LOG_GAP", "t_star": f"{ts:.12f}", "ranks": len(rows),
                      "per_level_min_g": {G: [mins[G][0], round(mins[G][1], 4)] for G in sorted(mins)},
                      "log_depth_at_level_minima_leaf_bd_src": {G: [round(x, 4) for x in comps[G]] for G in comps},
                      "tilted_P_step_mean_minus_ln5": round(tilt(P) - math.log(5), 6),
                      "first_order_cap_at_level_minima": {G: round(cap(mins[G][1]), 6) for G in sorted(mins)},
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
