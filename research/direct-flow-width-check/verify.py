#!/usr/bin/env python3
"""Independent check of #4436 section 3 on raw p7: width, routing-slot and growth bounds.

Uses an independent implementation of #4436's direct overlapping flow (the same as research/pr4436-direct-flow-check).
For every rank 121 <= n <= 2000, with W = sum_k W_k = 7688 and P = sum_r P_r = 55998 (the unit's target and paid
multiplicities) and h = G(n), it checks:
  * S_n = total source weight <= C = W (W+P+1)^(h+1)    (#4436's width factor bound);
  * the exact slot identity S + X + 2 * matched = U (W + P), so the routing count
    sources + exits + U (W + P) = 2 (W+P) U - 2 matched <= 2 (W+P) U   (sharpens #4436's bound);
  * log B_N = sum_n log S_n grows like N log N: the ratio log B_N / (N log N) stays below 2.1 through N = 2000.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
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


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    Wt, Pt = sum(W.values()), sum(P.values())
    need((Wt, Pt) == (7688, 55998), "unit multiplicities")
    worst, logB, ratios = 0.0, 0.0, {}
    for n in range(121, 2001):
        R = flow(n, W, P)
        S, X, U, M = sum(R["S"].values()), sum(R["X"].values()), R["units"], R["matched"]
        C = Wt * (Wt + Pt + 1) ** (R["G"] + 1)
        need(S <= C, f"n={n}: width factor bound")
        worst = max(worst, S / C)
        need(S + X + 2 * M == U * (Wt + Pt), f"n={n}: exact slot identity")
        need(S + X + U * (Wt + Pt) <= 2 * (Wt + Pt) * U, f"n={n}: routing bound")
        logB += math.log(S)
        if n in (500, 1000, 1500, 2000):
            ratios[n] = round(logB / (n * math.log(n)), 4)
    need(max(ratios.values()) < 2.1, "log B_N / (N log N) below 2.1")
    print(json.dumps({"status": "PASS_DIRECT_FLOW_WIDTH_CHECK", "ranks": "121..2000", "max_S_over_C": f"{worst:.3e}",
                      "logB_over_NlogN": ratios, "slot_identity": "S + X + 2*matched = U*(W+P)",
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
