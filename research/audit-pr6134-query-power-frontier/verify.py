#!/usr/bin/env python3
"""Independent exact checks for the PR6134 stochastic rank-power frontier.

Audit by JosieElliston's session 52 (Claude). Apache-2.0. Standard library only.
Written from PR6134's PROOF.md statement, without importing its verify.py.

Checks, all in exact rational arithmetic over real matrices:

1. Inequality (3) of PR6134, k^2 <= E[rank A] * E||A||_F^2, on seeded random
   unbiased finite laws built as A_i = M_i M^{-1} (M = sum p_i M_i), which
   have arbitrary nonsymmetric, oblique and mixed-rank outcomes.  The
   resulting lower bound trace(C)/k >= k/E[rank] - 1 on the error covariance C
   is checked, and every exact equality is tested against the classification
   proved in AUDIT.md (every nonzero outcome is alpha * P with one common
   alpha and P an orthogonal projection; ranks may differ in (3) alone, and
   the strict concave price is what forces one common rank R in (1)).
2. Attaining laws with non-coordinate projections (not covered by PR6134's
   coordinate and Walsh families), in k = 2, 3, with a zero branch.
3. Necessity controls: equal-cost laws that violate one equality condition
   (oblique idempotent, mixed endpoint scale, mixed ranks) are strictly above
   the bound.
4. The auxiliary-offset remark: an affine offset c with E c = 0 can lower the
   error at one input, but the +/- x average never goes below the linear part.
"""
from fractions import Fraction as F
from itertools import product
import json
import random
import sys


def require(cond, msg):
    if not cond:
        raise ValueError(msg)


def mat_mul(a, b):
    n, m, p = len(a), len(b), len(b[0])
    return [[sum(a[i][h] * b[h][j] for h in range(m)) for j in range(p)]
            for i in range(n)]


def transpose(a):
    return [list(r) for r in zip(*a)]


def eye(k):
    return [[F(int(i == j)) for j in range(k)] for i in range(k)]


def rank(a):
    rows = [list(r) for r in a]
    n, m = len(rows), len(rows[0])
    piv = 0
    for col in range(m):
        sel = next((j for j in range(piv, n) if rows[j][col] != 0), None)
        if sel is None:
            continue
        rows[piv], rows[sel] = rows[sel], rows[piv]
        for j in range(n):
            if j != piv and rows[j][col] != 0:
                s = rows[j][col] / rows[piv][col]
                rows[j] = [x - s * y for x, y in zip(rows[j], rows[piv])]
        piv += 1
    return piv


def inverse(a):
    k = len(a)
    aug = [list(a[i]) + eye(k)[i] for i in range(k)]
    for col in range(k):
        sel = next((j for j in range(col, k) if aug[j][col] != 0), None)
        if sel is None:
            return None
        aug[col], aug[sel] = aug[sel], aug[col]
        s = aug[col][col]
        aug[col] = [x / s for x in aug[col]]
        for j in range(k):
            if j != col and aug[j][col] != 0:
                t = aug[j][col]
                aug[j] = [x - t * y for x, y in zip(aug[j], aug[col])]
    return [row[k:] for row in aug]


def stats(law):
    """Return (mean, error covariance C = E (A-I)^T (A-I), E rank, E||A||^2)."""
    k = len(law[0][1])
    mean = [[F(0)] * k for _ in range(k)]
    cov = [[F(0)] * k for _ in range(k)]
    er = F(0)
    efro = F(0)
    for p, a in law:
        d = [[a[i][j] - int(i == j) for j in range(k)] for i in range(k)]
        dd = mat_mul(transpose(d), d)
        for i in range(k):
            for j in range(k):
                mean[i][j] += p * a[i][j]
                cov[i][j] += p * dd[i][j]
        er += p * rank(a)
        efro += p * sum(x * x for r in a for x in r)
    return mean, cov, er, efro


def is_scaled_orth_projection(a):
    """a = alpha * P with P symmetric idempotent; returns (alpha, rank) or None."""
    r = rank(a)
    if r == 0:
        return (F(0), 0)
    if any(a[i][j] != a[j][i] for i in range(len(a)) for j in range(len(a))):
        return None
    alpha = sum(a[i][i] for i in range(len(a))) / r
    if alpha == 0:
        return None
    sq = mat_mul(a, a)
    if any(sq[i][j] != alpha * a[i][j] for i in range(len(a)) for j in range(len(a))):
        return None
    return (alpha, r)


def classify_equality(law, common_rank=False):
    """Equality in (3): nonzero outcomes are alpha * P with one common alpha.

    Ranks may differ in (3) alone; common_rank=True adds the endpoint-rank
    condition that the strict concave price r <= R^(1-t) r^t forces in (1).
    """
    shapes = set()
    for p, a in law:
        if p == 0:
            continue
        s = is_scaled_orth_projection(a)
        if s is None:
            return False
        if s[1]:
            shapes.add(s if common_rank else s[0])
    return len(shapes) == 1


def bound_gap(law):
    """Return (k^2 vs E r * E||A||^2 slack, trace(C)/k - (k/E r - 1))."""
    k = len(law[0][1])
    mean, cov, er, efro = stats(law)
    require(mean == eye(k), "unbiased")
    tr = sum(cov[i][i] for i in range(k))
    require(tr == efro - k, "E||A-I||^2 = E||A||^2 - k")
    return er * efro - k * k, tr / k - (F(k) / er - 1), cov


def check_random(seed=6134, trials=4000):
    rng = random.Random(seed)
    tested = equalities = mixed_rank_equalities = nontrivial = 0
    for _ in range(trials):
        k = rng.choice((1, 2, 3))
        m = rng.choice((1, 2, 3))
        ms = [[[F(rng.choice((-1, 0, 0, 1, 2))) for _ in range(k)] for _ in range(k)]
              for _ in range(m)]
        ws = [rng.randint(0, 3) for _ in range(m)]
        if sum(ws) == 0:
            continue
        ps = [F(w, sum(ws)) for w in ws]
        mean = [[sum(p * x[i][j] for p, x in zip(ps, ms)) for j in range(k)]
                for i in range(k)]
        inv = inverse(mean)
        if inv is None:
            continue
        law = [(p, mat_mul(x, inv)) for p, x in zip(ps, ms)]
        slack, gap, cov = bound_gap(law)
        require(slack >= 0, "inequality (3)")
        require(gap >= 0, "trace(C)/k >= k/E r - 1")
        # A literal input e_i realizes error C_ii, so omega >= max_i C_ii.
        er = stats(law)[2]
        require(max(cov[i][i] for i in range(k)) >= F(k) / er - 1,
                "an actual basis input meets the bound")
        if slack == 0:
            require(gap == 0, "equality propagates")
            require(classify_equality(law), "equality classification")
            equalities += 1
            mixed_rank_equalities += not classify_equality(law, True)
            nonzero = {tuple(map(tuple, a)) for p, a in law if p and rank(a)}
            nontrivial += k >= 2 and len(nonzero) >= 2
        tested += 1
    return {"laws": tested, "exact_equalities": equalities,
            "mixed_rank_equalities_in_3": mixed_rank_equalities,
            "equalities_k2plus_two_distinct_nonzero_outcomes": nontrivial}


def proj(u):
    n = sum(x * x for x in u)
    return [[F(x * y, n) for y in u] for x in u]


def scaled(a, s):
    return [[s * x for x in r] for r in a]


def zero(k):
    return [[F(0)] * k for _ in range(k)]


def frame_law(vectors, beta):
    """Rank-one frame with E P = I/k on the nonzero branch, scaled k/beta."""
    k = len(vectors[0])
    w = beta / len(vectors)
    law = [(1 - beta, zero(k))]
    law += [(w, scaled(proj(u), F(k) / beta)) for u in vectors]
    return law


FRAMES = {
    "k2_hadamard_axis": [(1, 1), (1, -1)],
    "k2_axis_plus_diagonal": [(1, 0), (0, 1), (1, 1), (1, -1)],
    "k3_tetrahedral": [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
    "k3_pythagorean": [(3, 4, 0), (4, -3, 0), (0, 0, 5)],
}


def check_attainers():
    rows = []
    for name, vecs in FRAMES.items():
        for beta in (F(1), F(1, 2), F(3, 7)):
            law = frame_law(vecs, beta)
            k = len(vecs[0])
            slack, gap, cov = bound_gap(law)
            target = F(k) / beta - 1
            require(slack == 0 and gap == 0, "attains (3)")
            require(cov == scaled(eye(k), target), "isotropic covariance: omega = trace/k")
            require(classify_equality(law, True), "attainer has the classified shape")
            rows.append(name + "@" + str(beta))
    # Rank-two complement projections in k = 3 (R = 2): I - u u^T / |u|^2.
    vecs = FRAMES["k3_tetrahedral"]
    beta = F(2, 3)
    law = [(1 - beta, zero(3))]
    law += [(beta / 4, scaled([[int(i == j) - x for j, x in enumerate(r)]
                               for i, r in enumerate(proj(u))], F(3, 2) / beta))
            for u in vecs]
    slack, gap, cov = bound_gap(law)
    require(slack == 0 and gap == 0 and classify_equality(law, True), "rank-two attainer")
    require(cov == scaled(eye(3), F(3) / (beta * 2) - 1), "rank-two covariance")
    rows.append("k3_R2_tetrahedral_complement@2/3")
    return rows


def check_necessity_controls():
    out = {}
    # Oblique idempotent of rank one in k = 2 with E A = I and E rank = 1:
    # E = [[1, 1], [0, 0]] and F = [[0, -1], [0, 1]] (both idempotent, E + F = I).
    e = [[F(1), F(1)], [F(0), F(0)]]
    f = [[F(0), F(-1)], [F(0), F(1)]]
    law = [(F(1, 2), scaled(e, 2)), (F(1, 2), scaled(f, 2))]
    slack, gap, _ = bound_gap(law)
    require(slack > 0 and gap > 0 and not classify_equality(law), "oblique is strict")
    out["oblique_rank1_k2_trace_gap"] = str(gap)
    # Unequal scales on two orthogonal rank-one branches (still unbiased).
    p1, p2 = proj((1, 0)), proj((0, 1))
    law = [(F(1, 3), scaled(p1, 3)), (F(2, 3), scaled(p2, F(3, 2)))]
    slack, gap, _ = bound_gap(law)
    require(slack > 0 and not classify_equality(law), "unequal scale is strict")
    out["unequal_scale_k2_slack"] = str(slack)
    # Mixed ranks (rank 2 at scale 1, rank 1 at scale 2): strict in (3).
    law2 = [(F(1, 2), eye(2)), (F(1, 4), scaled(p1, 2)), (F(1, 4), scaled(p2, 2))]
    slack, gap, _ = bound_gap(law2)
    require(slack > 0, "mixed ranks with different scales are strict in (3)")
    out["mixed_rank_k2_slack"] = str(slack)
    # Mixed ranks with one common alpha attain (3) exactly (k = 3, ranks 1, 2):
    # (3) alone does not force a common rank.  For 0 < t < 1, R = 2 this law has
    # E r^t = (1 + 2^t)/2 and (1) gives 3 * 2^t/(1 + 2^t) - 1 < 1 = omega,
    # strict because 2^t < 2; at t = 1 it would attain.
    d1 = [[F(0)] * 3 for _ in range(3)]
    d1[1][1] = F(2)
    d2 = [[F(0)] * 3 for _ in range(3)]
    d2[0][0] = d2[2][2] = F(2)
    law = [(F(1, 2), d1), (F(1, 2), d2)]
    slack, gap, cov = bound_gap(law)
    require(slack == 0 and gap == 0 and cov == eye(3), "mixed-rank equality in (3)")
    require(classify_equality(law) and not classify_equality(law, True),
            "common alpha, two ranks")
    out["mixed_rank_common_alpha_k3_attains_3"] = True
    return out


def check_aux_offset():
    """Output A x + c, E A = I, E c = 0.  Cross terms can help at one x only."""
    # k = 1: A in {0, 2} each w.p. 1/2; c = +1 when A = 2, -1 when A = 0.
    law = [(F(1, 2), F(2), F(1)), (F(1, 2), F(0), F(-1))]
    require(sum(p * a for p, a, _ in law) == 1 and sum(p * c for p, _, c in law) == 0,
            "unbiased affine response")

    def err(x):
        return sum(p * ((a - 1) * x + c) ** 2 for p, a, c in law)

    lin = sum(p * (a - 1) ** 2 for p, a, _ in law)
    require(err(F(-1)) < lin, "offset lowers error at x = -1")
    require(max(err(F(1)), err(F(-1))) >= lin, "worst of +/- x is not lowered")
    require((err(F(1)) + err(F(-1))) / 2 == lin + sum(p * c * c for p, _, c in law),
            "+/- x average = linear error + E|c|^2")
    return {"err_minus1": str(err(F(-1))), "err_plus1": str(err(F(1))),
            "linear": str(lin)}


def main():
    result = {
        "random_unbiased_laws": check_random(),
        "non_coordinate_attainers": check_attainers(),
        "necessity_controls": check_necessity_controls(),
        "aux_offset": check_aux_offset(),
        "status": "PASS_AUDIT_PR6134",
    }
    json.dump(result, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
