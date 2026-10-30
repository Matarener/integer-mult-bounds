#!/usr/bin/env python3
"""Independent check of #4439 and #4442: halo exponents under the relative weight budget eps = 1/(16p^2).

Ceiling. Ideal off-sums T <= 1 - g (g = 1/(8p^2)); within-cell entries <= ideal/(1-eps); across-cell entries in [0, n].
Split T = T_in + T_out: off <= T_in/(1-eps) + T_out <= T/(1-eps) <= (16p^2-2)/(16p^2-1), so the gap is 1/(16p^2-1),
||H^-1||_2 <= B = 16p^2 - 1 and ||H||_2 < 2. Exponents: endpoint 12 (B^2 <= p^12), length 26 (error < B e^-p^2 < p^6 e^-p^2),
bandwidth/agreement 28, normalizer 6 (B < p^6; 7 also works). Fails: 11 (B^2 > p^11 at p = 2), 25 (length p^25 at
p = 2), 27 (loose count at p = 2, sharp count p >= 3), normalizer 5 (63 > 32). Tightness at p = 2: an across-cell
overshoot of 1/64 over the ideal off-sum (S-2)/S exceeds (S-2)/(S-1): 63*63 > 62*64. Bare-kernel example: theta = beta
= 1/4, h = 1, g = 2 gives square gap 2 = 32/16 against rho h^2 = 5/4 = 20/16. Exact rationals p = 2..64, all-p
arguments where stated. Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
from pathlib import Path
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
    # split identity: (1-e)[a/(1-e) + (t-a)] - t = -e (t-a), polynomial of degree <= 2 per variable, 3x3x3 grid
    vals = [F(1, 7), F(2, 5), F(3, 4)]
    for a, t, e in itertools.product(vals, repeat=3):
        need((1 - e) * (a / (1 - e) + (t - a)) - t == -e * (t - a), "split identity")
    for p in range(2, 65):
        S = 16 * p * p
        g, eps = F(1, 8 * p * p), F(1, S)
        off = (1 - g) / (1 - eps)
        need(off == F(S - 2, S - 1) and 1 - off == F(1, S - 1), "ceiling: gap 1/(16p^2-1)")
        need(1 + off < 2, "absolute sums below 2")
        B = S - 1
        need(B * B <= p ** 12 and B < p ** 6, "endpoint 12, normalizer 6")
        need(B < p ** 7, "normalizer 7 also works")
        L = p ** 26
        need((2 * L - 1) * (p - 1) < p ** 28 and (2 * L + 1) * (p - 1) < p ** 28, "bandwidth/agreement 28")
        # error at length p^26: B (1 - p^-24)^(p^26) <= B e^-(p^2) < p^6 e^-(p^2)
        need(B < p ** 6, "series error")
        if p >= 3:
            need((2 * p ** 26 - 1) * (p - 1) > p ** 27, "27 fails (sharp count, p >= 3)")
    need(63 * 63 > 2 ** 11, "endpoint 11 fails at p = 2")
    need(63 > 2 ** 5, "normalizer 5 fails at p = 2")
    need((2 * 2 ** 26 + 1) > 2 ** 27, "27 fails (loose count, p = 2)")
    # length p^25 fails at p = 2 on this route: B (1-x)^L >= B exp(-xL - x^2 L) with x = 2^-24, L = 2^25
    x, L = F(1, 2 ** 24), 2 ** 25
    need(math.log(63) - float(x * L + x * x * L) > math.log(64) - 4, "length 25 fails at p = 2")
    # all p >= 2: (16p^2-1)^2 <= p^12 and 16p^2-1 < p^6 (p^4 >= 16, room 1 at p = 2)
    need(all((16 * p * p - 1) ** 2 <= p ** 12 for p in range(2, 1000)), "endpoint 12 sample")
    need(16 * 16 < 3 ** 8, "p >= 3: (16p^2)^2 < p^12 since p^8 >= 3^8 > 256")
    # tightness at p = 2
    Sx = 64
    need(F(Sx - 2, Sx) + F(1, 64) > F(Sx - 2, Sx - 1) and 63 * 63 == 3969 and 62 * 64 == 3968, "p = 2 tightness")
    # bare-kernel example
    theta, beta, h, gstep = F(1, 4), F(1, 4), 1, 2
    rho = 1 + theta
    beta_next = beta + rho * h - gstep
    gap = (rho * h + beta) ** 2 - beta_next ** 2
    need(beta_next == F(-1, 2) and gap == 2 and rho * h * h == F(5, 4) and gap * 16 == 32 and rho * 16 == 20,
         "bare-kernel example: square gap 32/16 against 20/16")
    print(json.dumps({"status": "PASS_EPS_HALO_EXPONENT_CHECK", "exact_p_range": [2, 64],
                      "exponents": {"spectral_endpoint": 12, "series_length": 26, "bandwidth": 28,
                                    "agreement_distance": 28, "normalizer": 6},
                      "fails_confirmed": ["11 at p=2", "25 at p=2", "27 (loose p=2, sharp p>=3)", "normalizer 5 at p=2"],
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
