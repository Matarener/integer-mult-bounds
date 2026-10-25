#!/usr/bin/env python3
"""Independent check of #4436's partially matched direct flow for overlapping ranks.

flow(N, W, P) is a separate implementation of #4436 section 2: units at (rho, a) with m rho c(a) <= N in the
multinomial lockstep classes; a parent round's issued jobs at point b are matched to the child demand
D(b) = sum of W_k u(b - e_k) over present child points, the remaining u(b) - D(b) are paid (boundary) exits;
child target slots without a parent point are new sources; depth-G rounds all exit.
The verifier (1) reproduces all nine finite flows recorded by #4436 exactly (VECTORS.json, copied with its
source SHA256); (2) on the raw p7 invoice checks, at every rank 121 <= N <= 1000, sources in (N/m, N], exits
< N and the exact rank-one potential identity sum S s - sum X e = 608 * (column mass); (3) computes the exact
rational leaf recurrence L(N) and checks L(1000) lies in #4436's printed interval.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

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


def main():
    vec = json.loads((HERE / "VECTORS.json").read_text(encoding="utf-8"))
    for f in vec["finite_flows"]:
        W = {int(k): v for k, v in f["targets"].items()}
        P = {int(k): v for k, v in f["paid"].items()}
        fl = f["flow"]
        r = flow(fl["n"], W, P)
        need(r["S"] == {int(k): v for k, v in fl["sources"].items()}, f"{f['rule']} n={fl['n']}: sources")
        need(r["X"] == {int(k): v for k, v in fl["exits"].items()}, "exits")
        need(r["BX"] == {int(k): v for k, v in fl["boundary_exits"].items()}, "boundary exits")
        need((r["col"], r["units"], r["matched"]) == (fl["column_mass"], fl["units"], fl["matched_jobs"]), "mass, units, matched")
    W = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
    P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
    m = 121
    surplus = sum(k * w for k, w in W.items()) - sum(r * p for r, p in P.items())
    need(surplus == 608, "p7 rank-one surplus")
    L = [Q(0), Q(1)]
    for N in range(2, 1001):
        if N < m:
            L.append(Q(N))
            continue
        r = flow(N, W, P)
        need(all(m * s > N and s <= N for s in r["S"]) and all(e < N for e in r["X"]), f"N={N}: ranks")
        need(sum(s * v for s, v in r["S"].items()) - sum(e * v for e, v in r["X"].items()) == surplus * r["col"],
             f"N={N}: potential identity")
        tot = sum(r["S"].values())
        L.append((sum(v * L[N - s] for s, v in r["S"].items()) + sum(v * L[e] for e, v in r["X"].items())) / tot)
    lo, hi = (Q(vec["p7_leaves_per_array_n1000"][k]) for k in ("lower", "upper"))
    need(lo <= L[1000] <= hi, "L(1000) inside #4436's printed interval")
    print(json.dumps({"status": "PASS_PR4436_DIRECT_FLOW_CHECK", "recorded_flows_reproduced": len(vec["finite_flows"]),
                      "p7_ranks_checked": "121..1000", "L_1000": f"{float(L[1000]):.13f}",
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
