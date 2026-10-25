# SPDX-License-Identifier: Apache-2.0
"""Second, independent method (floating point): HiGHS LP + root bisection.

Patterns are generated as integer partitions (descending part lists), not by the
count-vector recursion of verify.py. Reduction columns move one helper-call from
width w to any width v < w at zero cost ("free") or, for the move w -> w-1, at
h(2) - h(1) ("stage"). The "stage" mode is the superseded task-card model, which
adds local rank; it is NOT the staging accounting of README/PROOF and is kept only
as recorded output. Prints JSON with roots and the positive (basic) patterns.
Requires numpy 2.5.4 and scipy 1.18.1 (as used for evidence/HIGHS.json); not part
of the registered replay, see README.
"""
import json
import math
import sys

import numpy as np
import scipy.optimize as so
import scipy.sparse as sp

BINS = {8: 672, 16: 448, 32: 448, 48: 448}
INV544 = {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}
INV3682 = {4: 26, 5: 2, 6: 18, 7: 52, 8: 97, 9: 213}
LOC544 = {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}
LOC3682 = {1: 2437, 2: 724, 3: 226, 4: 102, 5: 20, 8: 8}


def partitions(n, maxpart):
    """All partitions of n with parts <= maxpart, as descending lists."""
    if n == 0:
        yield []
        return
    for first in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - first, first):
            yield [first] + rest


def bin_patterns(wmin):
    out = []
    for cap in BINS:
        for used in range(cap + 1):
            for part in partitions(used, 9):
                if all(x >= wmin for x in part):
                    out.append((cap, tuple(part)))
    return out


def h(l, a):
    return l ** (1.0 - a) if l > 0 else 0.0


def build(pats, widths, moves):
    """Equality rows: one per width, one per bin rank. Columns: patterns, then moves."""
    row = {w: i for i, w in enumerate(widths)}
    caps = list(BINS)
    rows, cols, vals = [], [], []
    for j, (cap, part) in enumerate(pats):
        for x in part:
            rows.append(row[x]); cols.append(j); vals.append(1.0)
        rows.append(len(widths) + caps.index(cap)); cols.append(j); vals.append(1.0)
    n = len(pats)
    for t, (w, v, _) in enumerate(moves):
        rows += [row[w], row[v]]; cols += [n + t, n + t]; vals += [1.0, -1.0]
    A = sp.csc_matrix((vals, (rows, cols)), shape=(len(widths) + len(caps), n + len(moves)))
    return A


def make(inv, loc, wmin, mode):
    widths = list(range(wmin, 10))
    pats = bin_patterns(wmin)
    if mode == "fixed":
        moves = []
    elif mode == "free":
        moves = [(w, v, "free") for w in widths for v in widths if v < w]
    elif mode == "stage":
        moves = [(w, w - 1, "stage") for w in widths if w - 1 >= wmin]
    A = build(pats, widths, moves)
    b = np.array([9.0 * inv.get(w, 0) for w in widths] + [float(BINS[c]) for c in BINS])
    used = lambda p: sum(p[1])  # noqa: E731

    def F(a):
        cost = [h(cap - used(p), a) for p in pats for cap in [p[0]]]
        mc = [0.0 if m[2] == "free" else h(2, a) - h(1, a) for m in moves]
        r = so.linprog(np.array(cost + mc), A_eq=A, b_eq=b, bounds=(0, None), method="highs")
        assert r.status == 0, r.message
        local = 9.0 * sum(n * h(rk, a) for rk, n in loc.items())
        return r.fun + local - 896.0 * h(73, a), r
    return pats, moves, F


def root(F, lo=0.0005, hi=0.005, it=56):
    assert F(lo)[0] < 0 < F(hi)[0]
    for _ in range(it):
        mid = (lo + hi) / 2
        if F(mid)[0] > 0:
            hi = mid
        else:
            lo = mid
    return lo, hi


SCEN = {
    "s544_fixed_w4": (INV544, LOC544, 4, "fixed"),
    "s544_free_w1": (INV544, LOC544, 1, "free"),
    "s544_stage_w1": (INV544, LOC544, 1, "stage"),
    "pr3682_fixed": (INV3682, LOC3682, 4, "fixed"),
    "width_only": (INV544, LOC3682, 4, "fixed"),
    "local_only": (INV3682, LOC544, 4, "fixed"),
}
A_STAR = 0.001730578437266246818741
# one helper-call moved (per replica RHS +-1): F differences at A_STAR give unit prices
UNIT = {"unit_8to7": (8, 7), "unit_5to4": (5, 4), "unit_4to3": (4, 3)}

def unit_prices():
    base = make(INV544, LOC544, 1, "fixed")[2](A_STAR)[0]
    out = {}
    for name, (w, v) in UNIT.items():
        inv = dict(INV544)
        inv[w] = inv[w] - 1 / 9
        inv[v] = inv.get(v, 0) + 1 / 9
        out[name] = make(inv, LOC544, 1, "fixed")[2](A_STAR)[0] - base
    return base, out


if __name__ == "__main__":
    names = sys.argv[1:] or list(SCEN)
    res = {}
    base, up = unit_prices()
    res["unit_prices_at_a_star"] = dict(F_base=base, **up)
    print("unit", base, up, file=sys.stderr, flush=True)
    for name in names:
        inv, loc, wmin, mode = SCEN[name]
        pats, moves, F = make(inv, loc, wmin, mode)
        lo, hi = root(F)
        val, r = F(hi)
        basis = [[pats[j][0], list(pats[j][1])] for j in range(len(pats)) if r.x[j] > 1e-7]
        mv = {f"{m[0]}->{m[1]}": float(r.x[len(pats) + t]) for t, m in enumerate(moves) if r.x[len(pats) + t] > 1e-9}
        res[name] = dict(patterns=len(pats), moves=len(moves), root_lo=repr(lo), root_hi=repr(hi),
                         F_at_a_star=F(A_STAR)[0],
                         positive_patterns=basis, positive_moves=mv,
                         eq_marginals=[float(x) for x in r.eqlin.marginals])
        print(name, len(pats), repr(lo), repr(hi), len(basis), mv, file=sys.stderr, flush=True)
    print(json.dumps(res, indent=1))
