# SPDX-License-Identifier: Apache-2.0
"""Exact dual certificate: no owner fill of the staged544 inventory beats the ideal root.

Inventory per owner replica (PR3734 template and native supplier, any clock, any replica
count T): nine calls of 408 helpers with widths {4:26, 5:2, 6:18, 7:53, 8:96, 9:213}; idle
bins 672 of rank 8, 448 of rank 16, 448 of rank 32, 448 of rank 48; local paid profile
{1:2440, 2:725, 3:224, 4:102, 5:20, 8:8} per call; 896 live families of rank 73. Every
helper occupies its width in one idle bin and each bin's remainder l > 0 is paid as one
rank-l child (owner_audit.py).

The root is unique: F(a) = sum n_r r^(1-a) - 896 T 73^(1-a) has the sign of
G(a) = sum n_r r (73/r)^a - 65408 T, strictly increasing because every paid rank is < 73.
So "root < a_hi" is "F(a_hi) > 0". F(a_hi) is linear in the bin pattern counts y, so for
any dual (pi, mu) with pi . p + mu_c <= h(l_p) for every pattern p of every rank c, weak
duality gives sum y h(l) >= sum_c mu_c B_c + sum_w pi_w 9 s_w for every packing, integer or
not, with or without time windows or the one-helper-per-call-per-bin rule. The dual is the
exact solution on the ten patterns of the fixed-inventory ideal, with outward rational
enclosures of r^(1-a) from PR3734 rational_price.py. Standard library only.
"""
from fractions import Fraction as Q

W = (4, 5, 6, 7, 8, 9)
SUPPLY = (26, 2, 18, 53, 96, 213)                  # helpers per call
BINS = {8: 672, 16: 448, 32: 448, 48: 448}         # idle bins per owner replica
LOCAL = {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}
CAPS = (8, 16, 32, 48)
# the ten patterns of the fixed-inventory ideal (counts of widths 4..9)
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
    """Exact Gaussian elimination over the rationals."""
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


def certify(R, a, perturb=Q(0)):
    """Lower bound on min over all packings of F(a) per owner replica, with its dual.

    R is PR3734 rational_price module; lower enclosures of h keep the bound valid.
    perturb shifts the width-9 dual after solving (a control: feasibility must then fail)."""
    a = Q(a)
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
    dual = sum(mu[c] * BINS[c] for c in CAPS) + sum(x * 9 * s for x, s in zip(pi, SUPPLY))
    local = sum(9 * n * R.h_bounds(r, a)[0] for r, n in LOCAL.items())
    live = 896 * R.h_bounds(73, a)[1]
    return dict(min_reduced_cost=worst[0], worst_pattern=(worst[1], worst[2]), dual_feasible=worst[0] >= 0,
                lower_bound=local + dual - live, patterns=sum(len(patterns(c)) for c in CAPS))
