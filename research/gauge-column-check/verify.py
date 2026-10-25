#!/usr/bin/env python3
"""Independent check of #4438: the within-cell gauge column transfer.

On a constant-phase run (beta_(i+h) = beta_i + theta h) LOG-A's entry n_(i,h) = exp(-a[(rho h + beta_i)^2 - beta_(i+h)^2])
factors as (a_i / a_(i+h)) exp(-a rho h^2) with a_i = exp(a beta_i^2 / theta), since the exponent is
h^2 (1 + 2 theta) + 2 h beta_i. For a downward kernel 0 <= Ghat <= G and (1-eps) a <= ahat <= a, each within-cell
column off-sum of diag(ahat) Ghat diag(ahat)^-1 is at most the ideal one divided by 1-eps. Checks:
  * the factorization on random runs (relative error < 1e-12);
  * the 1/(1-eps) bound on 2,000 random rounded blocks, eps = 1/(16p^2), p in {2,3,5,10} (and its tightness);
  * exact rationals: ideal off-sum 1-1/(8p^2) with eps = 1/(16p^2) leaves gap 1/(16p^2-1); eps = 1/2 leaves none;
  * C = 3 is the least integer with 2^(-Cp) <= 1/(16p^2) for all p >= 2 (equality at p = 2; C = 2 fails at p = 2),
    checked exactly to p = 10^4 plus 16 p^2 <= 8^p by induction (8 (p+1)^2 <= 8 * 2.25 p^2 < 8 * 8 p^2... ratio);
  * the downstream comparison (2p-1)/(16p) > 1/(8p^2), i.e. p(2p-1) > 2.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    loga = (ROOT / "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md").read_text(encoding="utf-8")
    need("`n_i,h=exp(-a[(rho*h+beta_i)^2-beta_(i+h)^2])`" in loga, "LOG-A entry law")
    rng = random.Random(4438)
    worst_fact = 0.0
    tight = 0.0
    blocks = 0
    for p in (2, 3, 5, 10):
        eps = 1 / (16 * p * p)
        for _ in range(500):
            a = rng.uniform(0.5, 5 * math.log(16 * p))
            theta = rng.uniform(1 / (4 * p * p), 1 / (p * p))
            n = p * 6
            b0 = rng.uniform(-0.5, 0.5 - theta * n)  # a run of n indices stays inside [-1/2, 1/2)
            beta = [b0 + theta * i for i in range(n)]
            rho = 1 + theta
            lw = [a * b * b / theta for b in beta]  # log a_i (kept in log form to avoid overflow)
            W = p - 1
            ideal = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(max(0, i - W), min(n, i + W + 1)):
                    if i == j:
                        continue
                    h = j - i
                    le = -a * ((rho * h + beta[i]) ** 2 - beta[j] ** 2)
                    lf = lw[i] - lw[j] - a * rho * h * h
                    worst_fact = max(worst_fact, abs(le - lf) / max(1.0, abs(le)))
                    ideal[i][j] = math.exp(le)
            u = [1 - eps * rng.random() for _ in range(n)]  # ahat_i = a_i u_i with (1-eps) a <= ahat <= a
            for j in range(n):
                col_ideal = sum(ideal[i][j] for i in range(n))
                # entry ahat_i Ghat_h / ahat_j = ideal * (u_i / u_j) * (Ghat / G), with Ghat / G in [0.9, 1]
                col_hat = sum(ideal[i][j] * u[i] / u[j] * rng.uniform(0.9, 1.0) for i in range(n) if ideal[i][j])
                need(col_hat <= col_ideal / (1 - eps) * (1 + 1e-12), "column bound 1/(1-eps)")
                if col_ideal:
                    tight = max(tight, col_hat / col_ideal * (1 - eps))
            blocks += 1
    need(worst_fact < 1e-12, "factorization")
    for p in range(2, 200):
        g, eps = F(1, 8 * p * p), F(1, 16 * p * p)
        need(1 - (1 - g) / (1 - eps) == F(1, 16 * p * p - 1), "gap 1/(16p^2-1)")
        need((1 - g) / F(1, 2) > 1, "eps = 1/2 leaves no gap")
        need(p * (2 * p - 1) > 2 and F(2 * p - 1, 16 * p) > F(1, 8 * p * p), "downstream comparison")
    need(all(16 * p * p <= 8 ** p for p in range(2, 10001)) and 16 * 4 == 8 ** 2, "C = 3 works, equality at p = 2")
    need(16 * 4 > 4 ** 2, "C = 2 fails at p = 2")
    # induction for p >= 3: 16(p+1)^2 <= 16 * (16/9) p^2 < 8 * 16 p^2 <= 8 * 8^p
    need(F(4, 3) ** 2 < 8, "induction ratio ((p+1)/p)^2 <= 16/9 < 8 for p >= 3")
    print(json.dumps({"status": "PASS_GAUGE_COLUMN_CHECK", "random_blocks": blocks,
                      "factorization_max_log_error": f"{worst_fact:.1e}", "max_column_ratio_over_bound": round(tight, 6),
                      "least_setup_constant": 3, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
