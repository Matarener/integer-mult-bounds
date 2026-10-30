#!/usr/bin/env python3
"""Boundary-exit potential share in #4436's direct p7 flow: mirror identity, a rigorous uniform bound, and the
correction that leaf exits (not boundary exits) dominate the exit coefficient.

Using an independent implementation of #4436's partially matched flow (the same as research/pr4436-direct-flow-check),
for every rank 121 <= N <= 3000 and a 1%-geometric grid up to 5*10^5 this computes
    beta(N) = sum over boundary exits x_e e^t / sum over sources w_s s^t,     t = 1 - 0.0026865,
and checks: every exit is at most r_max N / m (r_max = 48, m = 121), the exact rank-one potential identity, and
max beta < 0.16 (observed 0.1545). It also checks EXACTLY, at four ranks, the mirror identity: boundary exits and inner
sources are one base measure seen through windows (1/r, 1/k] and (1/k, 1/r]; this gives the uniform bound
beta <= max_J E_J / S_J ~ 0.3208 over elementary windows J. CORRECTION (README): leaf exits reach ~0.384 N and carry
~85-92% of the t-potential, so the earlier "leaf term vanishes" hypothesis is false; the exit coefficient
kappa(N, z0) is recorded against eta(z0) instead.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
import sys

from fractions import Fraction as Q
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


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def mirror_bound(W, P, t):
    """max over elementary windows J of E_J / S_J (floats; margins are large)"""
    pts = sorted({Q(1, x) for x in list(P) + list(W)})
    best = 0.0
    for lo, hi in zip(pts, pts[1:]):
        mid = (lo + hi) / 2
        E = sum(P[r] * W[k] * (r * k) ** t for r in P for k in W if r > k and Q(1, r) < mid <= Q(1, k))
        S = sum(P[r] * W[k] * (r * k) ** t for r in P for k in W if k > r and Q(1, k) < mid <= Q(1, r))
        if E > 0:
            need(S > 0, "every exit window is covered by source windows")
            best = max(best, E / S)
    return best


def mirror_identity(N, W, P, m, r):
    """exact: BX and S equal the mirrored windows of the base measure mu(z), z = rho c(a)"""
    ks = sorted(W)
    G = r["G"]
    F = [{1: 1}]
    for d in range(1, G + 1):
        nxt = {}
        for rho, cnt in F[d - 1].items():
            for rr, pr in P.items():
                if m * rho * rr <= N:
                    nxt[rho * rr] = nxt.get(rho * rr, 0) + cnt * pr
        F.append(nxt)
    mu = {}
    for d in range(G):
        for rho, cnt in F[d].items():
            for a in multis(len(ks), G - d - 1):
                c, u = 1, factorial(sum(a))
                for k, x in zip(ks, a):
                    c *= k ** x
                    u = u // factorial(x) * W[k] ** x
                mu[rho * c] = mu.get(rho * c, 0) + cnt * u
    bx, src = {}, {}
    for z, w in mu.items():
        for rr in P:
            for k in W:
                if rr > k and N < m * z * rr and m * z * k <= N:
                    bx[rr * k * z] = bx.get(rr * k * z, 0) + P[rr] * W[k] * w
                if k > rr and N < m * z * k and m * z * rr <= N:
                    src[rr * k * z] = src.get(rr * k * z, 0) + P[rr] * W[k] * w
    for a in multis(len(ks), G):
        c, u = 1, factorial(G)
        for k, x in zip(ks, a):
            c *= k ** x
            u = u // factorial(x) * W[k] ** x
        if m * c <= N:
            for k in ks:
                src[k * c] = src.get(k * c, 0) + W[k] * u
    need(bx == {e: v for e, v in r["BX"].items() if v}, f"N={N}: boundary exits are the mirrored windows")
    need(src == r["S"], f"N={N}: sources are the mirrored windows plus the top layer")


def main():
    W = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
    P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
    m, rmax, surplus = 121, 48, 608
    t = 1 - 0.0026865
    savings = (0.002, 0.001, 0.0008)
    Ns = sorted(set(list(range(121, 3001)) + [int(121 * 1.01 ** k) for k in range(0, 850)]))
    Ns = [n for n in Ns if n <= 500000]
    best, at, leaf_min, leaf_rank = 0.0, None, 1.0, 0.0
    kap = {s: {} for s in savings}
    for N in Ns:
        r = flow(N, W, P)
        need(all(e * m <= rmax * N for e in r["X"]), f"N={N}: exits <= r_max N/m")
        need(sum(s * v for s, v in r["S"].items()) - sum(e * v for e, v in r["X"].items()) == surplus * r["col"],
             f"N={N}: potential identity")
        if N in (1089, 3000, 20000, 100000):
            mirror_identity(N, W, P, m, r)
        st = sum(v * s ** t for s, v in r["S"].items())
        bt = sum(v * e ** t for e, v in r["BX"].items())
        if bt / st > best:
            best, at = bt / st, N
        if r["G"] >= 1:
            leaf = {e: v - r["BX"].get(e, 0) for e, v in r["X"].items() if v != r["BX"].get(e, 0)}
            leaf_min = min(leaf_min, sum(v * e ** t for e, v in leaf.items()) / st)
            leaf_rank = max(leaf_rank, max(leaf) / N)
        if N >= 1000:
            for s in savings:
                z = 1 - s
                kap[s][N] = sum(v * e ** z for e, v in r["X"].items()) / sum(v * x ** z for x, v in r["S"].items())
    bound = mirror_bound(W, P, t)
    need(best < 0.16 and best <= bound < 0.33, "boundary share below the rigorous mirror bound")
    need(leaf_min > 0.8 and leaf_rank > 0.38, "leaf exits dominate and reach Theta(N): the leaf hypothesis fails")
    table = {}
    for s in savings:
        eta = (1 - s) * m ** (-s)
        table[str(s)] = {"eta": round(eta, 6), **{f"sup_kappa_N>={th:g}": round(max(v for N, v in kap[s].items()
                         if N >= th), 6) for th in (1e3, 1e4, 1e5, 3e5)}}
    need(max(v for N, v in kap[0.0008].items() if N >= 3e5) < table["0.0008"]["eta"], "saving 0.0008 passes at N>=3e5")
    need(max(v for N, v in kap[0.001].items() if N >= 3e5) > table["0.001"]["eta"], "saving 0.001 still fails at N>=3e5")
    print(json.dumps({"status": "PASS_DIRECT_FLOW_BOUNDARY_SHARE", "ranks_scanned": len(Ns), "max_N": Ns[-1],
                      "max_boundary_share": round(best, 6), "at_N": at, "rigorous_mirror_bound": round(bound, 6),
                      "min_leaf_share": round(leaf_min, 6), "max_leaf_rank_over_N": round(leaf_rank, 6),
                      "exit_coefficient_vs_eta": table, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
