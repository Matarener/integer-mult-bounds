# SPDX-License-Identifier: Apache-2.0
"""Exact dual certificate on the owner-fill root for a given staged544-type inventory.

Adapted from research/staged544-clock-ceiling/ceiling_certificate.py (PR3815, ChaloupeMusic,
Apache-2.0): the same idle-bin model, the same ten-pattern basis and the same weak-duality
argument, with the per-call helper supply and local paid profile as parameters. For a dual
(pi, mu) with pi . p + mu_c <= h(l_p) for every pattern p of every rank c, every packing,
integer or not, with or without time windows, has F(a) >= local + dual - live per owner
replica. F has the sign of a strictly increasing function, so a positive lower bound at
a_hi proves that every owner fill (any clock, any replica count) has its root below a_hi.
Outward rational enclosures of r^(1-a) come from PR3734 rational_price.py. Standard library.
"""
from fractions import Fraction as Q

W = (4, 5, 6, 7, 8, 9)
BINS = {8: 672, 16: 448, 32: 448, 48: 448}         # idle bins per owner replica (PR3734)
CAPS = (8, 16, 32, 48)
BASIS = [(8, (0, 0, 0, 0, 1, 0)), (16, (0, 0, 0, 1, 0, 1)), (32, (1, 0, 0, 0, 0, 3)),
         (32, (0, 0, 1, 0, 1, 2)), (32, (0, 1, 0, 0, 0, 3)), (32, (0, 0, 0, 1, 2, 1)),
         (32, (0, 0, 0, 0, 0, 3)), (32, (0, 0, 0, 2, 0, 2)), (48, (0, 0, 0, 0, 0, 0)),
         (48, (0, 0, 0, 0, 0, 5))]


def patterns(cap):
    out = []

    def rec(i, rest, cur):
        if i == len(W):
            out.append(tuple(cur))
            return
        for k in range(rest // W[i] + 1):
            rec(i + 1, rest - k * W[i], cur + [k])
    rec(0, cap, [])
    return out


def left(cap, p):
    return cap - sum(k * w for k, w in zip(p, W))


def solve(A, b):
    n = len(A)
    M = [[Q(x) for x in row] + [Q(y)] for row, y in zip(A, b)]
    for c in range(n):
        piv = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def certify(R, a, supply, local, perturb=Q(0)):
    """supply: helpers per call for widths 4..9; local: per-call paid profile {rank: count}."""
    a = Q(a)
    supply = tuple(supply[w] for w in W) if isinstance(supply, dict) else tuple(supply)
    h = {l: R.h_bounds(l, a)[0] for l in range(1, 49)}
    cost = lambda cap, p: h[left(cap, p)] if left(cap, p) else Q(0)  # noqa: E731
    rows, rhs = [], []
    for cap, p in BASIS:
        rows.append(list(p) + [1 if cap == c else 0 for c in CAPS])
        rhs.append(cost(cap, p))
    sol = solve(rows, rhs)
    pi, mu = sol[:6], dict(zip(CAPS, sol[6:]))
    pi[5] += perturb
    worst = None
    for cap in CAPS:
        for p in patterns(cap):
            rc = cost(cap, p) - sum(x * k for x, k in zip(pi, p)) - mu[cap]
            if worst is None or rc < worst[0]:
                worst = (rc, cap, p)
    dual = sum(mu[c] * BINS[c] for c in CAPS) + sum(x * 9 * s for x, s in zip(pi, supply))
    loc = sum(9 * n * R.h_bounds(r, a)[0] for r, n in local.items())
    live = 896 * R.h_bounds(73, a)[1]
    return dict(min_reduced_cost=worst[0], dual_feasible=worst[0] >= 0,
                lower_bound=loc + dual - live, patterns=sum(len(patterns(c)) for c in CAPS))
