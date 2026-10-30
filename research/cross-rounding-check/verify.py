#!/usr/bin/env python3
"""Independent check of #4449: downward rounding of the across-cell Gaussian coefficient.

With positive integers s < t, u (u = alpha^2), rho = t/s, q_i = floor(t i/s + 1/2), b_i = t i - s q_i, beta_i = b_i/s:
  (1) exact rationals: (rho h + beta_i)^2 - beta_(i+h)^2 = j / (u k) with j = u((t h + b_i)^2 - b_(i+h)^2), k = s^2,
      so n_(i,h) = exp(-pi u (...)) = exp(-pi j / k);
  (2) -s/2 <= b_i < s/2 and j > 0 for every h != 0 (j = 0 at h = 0);
  (3) the second form j/k = u d (d + 2 b_(i+h)/s), d = q_(i+h) - q_i;
  (4) period cut: q_(i+s) = q_i + t and b_(i+s) = b_i;
  (5) repair H = max(0, z - 2 eta) for any oracle |z - n| < 2 eta on the P-grid: 0 <= H <= n, n - H < 4 eta
      (adversarial grid of n and admissible z, exact rationals); one ulp is not enough (n = 3eta/2, z = 3eta);
      the constant 4 is a sharp supremum (z = 2 eta, n -> 4 eta);
  (6) 2W entries give an absolute across-cell rounding sum below 8 W eta.
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
    need("`n_i,h=exp(-a[(rho*h+beta_i)^2-beta_(i+h)^2])`" in loga and "`beta_i=rho*i-q_i`" in loga, "LOG-A entry law")
    rng = random.Random(4449)
    cases = 0
    for _ in range(3000):
        s = rng.randint(1, 60)
        t = rng.randint(s + 1, 3 * s)  # any t > s, as in #4449 (rho up to 3)
        u = rng.randint(1, 50)
        rho = F(t, s)
        q = lambda i: math.floor(F(t * i, s) + F(1, 2))
        b = lambda i: t * i - s * q(i)
        for _ in range(8):
            i = rng.randint(-500, 500)
            h = rng.randint(-40, 40)
            bi, bh = b(i), b(i + h)
            need(F(-s, 2) <= bi < F(s, 2), "(2) b range")
            beta_i, beta_h = F(bi, s), F(bh, s)
            need(beta_i == rho * i - q(i), "beta definition")
            j = u * ((t * h + bi) ** 2 - bh ** 2)
            k = s * s
            need(u * ((rho * h + beta_i) ** 2 - beta_h ** 2) == F(j, k), "(1) exact exponent")
            need((j > 0) if h else (j == 0), "(2) j > 0 off the diagonal")
            d = q(i + h) - q(i)
            need(F(j, k) == u * d * (d + F(2 * bh, s)), "(3) second form")
            need(q(i + s) == q(i) + t and b(i + s) == b(i), "(4) period cut")
            cases += 1
    # (5) repair lemma on an adversarial exact grid
    P = 12
    eta = F(1, 2 ** P)
    reps = 0
    for num in range(0, 200):
        n = F(num, 37) * eta  # true value, arbitrary rational
        lo = math.floor((n - 2 * eta) / eta) + 1
        hi = math.ceil((n + 2 * eta) / eta) - 1
        for zz in range(lo, hi + 1):
            z = zz * eta
            if not abs(z - n) < 2 * eta:
                continue
            H = max(F(0), z - 2 * eta)
            need(0 <= H <= n and n - H < 4 * eta and (H / eta).denominator == 1, "(5) repair")
            reps += 1
    n, z = F(3, 2) * eta, 3 * eta
    need(abs(z - n) < 2 * eta and z - eta > n, "(5) one ulp is not enough")
    for dl in (F(1, 2), F(1, 10), F(1, 1000)):
        n, z = (4 - dl) * eta, 2 * eta
        need(abs(z - n) < 2 * eta and max(F(0), z - 2 * eta) == 0 and n - 0 == (4 - dl) * eta, "(5) 4 is sharp")
    for W in range(1, 50):
        need(2 * W * 4 * eta == 8 * W * eta, "(6) 2W entries below 8 W eta")
    print(json.dumps({"status": "PASS_CROSS_ROUNDING_CHECK", "exponent_cases": cases, "repair_cases": reps,
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
