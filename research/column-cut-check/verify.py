#!/usr/bin/env python3
"""Independent numerical check of #4437: the ideal column majorant survives g = 2 steps.

Builds the ideal narrow matrix directly from LOG-A's entry law n_(i,h) = exp(-a[(rho h + beta_i)^2 - beta_(i+h)^2]),
rho = 1 + theta, beta_i = rho i - q_i in [-1/2, 1/2) (so q_i = floor(rho i + beta_0 + 1/2) and every step is 1 or 2),
and checks every interior column off-sum against
    M(a, theta) = exp(-2 a theta) + exp(-2 a (1-theta)) + 2 exp(-2a) / (1 - exp(-4a))
over 4 primes-sized p, 5 values of a (both GAUSSIAN ends and three outside), 4 values of theta and 20 phases beta_0.
It also checks #4437's landing-interval table (incoming/outgoing g against beta_j), that the majorant is attained
(sharp), and the gap 1 - M > 1/(8p^2) at the corners of a in [4 log 16p, 5 log 16p], theta in [1/(4p^2), 1/p^2] for
p = 2..10^4 (M is monotone in a; both theta ends are checked), plus the 2p eps <= 1/(16p^2) perturbation step.
Floating point with explicit tolerances. Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def majorant(a, th):
    return math.exp(-2 * a * th) + math.exp(-2 * a * (1 - th)) + 2 * math.exp(-2 * a) / (1 - math.exp(-4 * a))


def columns(a, th, b0, n=200, H=40):
    rho = 1 + th
    q = [math.floor(rho * i + b0 + 0.5) for i in range(n)]
    beta = [rho * i + b0 - q[i] for i in range(n)]
    need(all(-0.5 <= b < 0.5 for b in beta) and all(q[i] - q[i - 1] in (1, 2) for i in range(1, n)), "entry law")
    out = []
    for j in range(H, n - H):
        s = sum(math.exp(-a * ((rho * (j - i) + beta[i]) ** 2 - beta[j] ** 2)) for i in range(j - H, j + H + 1) if i != j)
        gin, gout = q[j] - q[j - 1], q[j + 1] - q[j]
        b = beta[j]
        if gin == 2:
            need(gout == 1 and -0.5 <= b < -0.5 + th + 1e-12, "landing: incoming g = 2")
        elif gout == 2:
            need(0.5 - th - 1e-12 <= b < 0.5, "landing: outgoing g = 2")
        else:
            need(-0.5 + th - 1e-12 <= b < 0.5 - th + 1e-12, "landing: both steps 1")
        out.append((s, gin == 2 or gout == 2))
    return out


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    loga = (ROOT / "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md").read_text(encoding="utf-8")
    need("`n_i,h=exp(-a[(rho*h+beta_i)^2-beta_(i+h)^2])`" in loga and "`beta_i=rho*i-q_i`" in loga, "LOG-A entry law")
    total = with_g2 = 0
    worst = 0.0
    for p in (2, 3, 5, 10):
        L = math.log(16 * p)
        for a in (4 * L, 5 * L, 1.0, 0.5, 0.25):
            for th in (1 / (4 * p * p), 1 / (p * p), 0.2, 0.25):
                M = majorant(a, th)
                for k in range(20):
                    for s, g2 in columns(a, th, -0.5 + k / 20):
                        need(s <= M * (1 + 1e-11), f"column majorant p={p} a={a} theta={th}")
                        worst = max(worst, s / M)
                        total += 1
                        with_g2 += g2
    need(worst > 1 - 1e-9, "the majorant is attained (sharp)")
    need(with_g2 > 0.2 * total, "a substantial share of columns meet a g = 2 step")
    min_ratio = math.inf
    for p in range(2, 10001):
        L = math.log(16 * p)
        for th in (1 / (4 * p * p), 1 / (p * p)):
            gap = 1 - majorant(4 * L, th)
            min_ratio = min(min_ratio, gap * 8 * p * p)
            need(gap > 1 / (8 * p * p), f"gap > 1/(8p^2) at p={p}")
            need(gap - (2 * p - 1) / (2 * p) / (16 * p * p) > 1 / (16 * p * p), "perturbed gap > 1/(16p^2)")
    print(json.dumps({"status": "PASS_COLUMN_CUT_CHECK", "columns": total, "columns_meeting_g2": with_g2,
                      "max_offsum_over_majorant": round(worst, 12), "min_gap_times_8p2_p_to_1e4": round(min_ratio, 4),
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
