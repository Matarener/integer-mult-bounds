#!/usr/bin/env python3
"""Across-cell transfer of the delta halo exponents 11, 24, 26, 26, 6 (#4452), and robustness to the rounded reading.

Setting (#4442/#4452): banded reference H, diagonal exactly one, bandwidth W <= p-1, ideal Gaussian matrix N with
row and column off-sums T <= 1 - g, g = 1/(8p^2). Within-cell entries obey |H| <= N/(1-delta), delta = 2^(2-32760p).
  (A) Downward reading (LOG-A, #4449: 0 <= H <= n across cells). Split T = T_in + T_out:
        off(H) <= T_in/(1-delta) + T_out <= T/(1-delta) <= (1-g)/(1-delta),
      because (1-delta)[T_in/(1-delta) + T_out] - T = -delta T_out. So the global Neumann ceiling is #4452's
      U = 8p^2(D-4)/(D-32p^2) and the five exponents transfer verbatim.
  (B) Any reading with excess rho: if every row and column off-sum of |H| is at most (1-g) + rho with
      rho <= 1/(32p^3), then 1 - off >= (4p-1)/(32p^3) >= 7/(64p^2) > 1/(10p^2), so ||H^-1||_2 < 10p^2 with 100p^4 < p^11
      and B < p^6: endpoint 11, length 24, bandwidth/agreement 26 and normalizer 6 hold. Per entry, an absolute
      error e <= 1/(64p^4) on the <= 2W band entries suffices. The downward reading has rho <= 2 delta.
Exact rational checks for p = 2..64; the split identity is a polynomial identity of degree <= 2 per variable, checked
on a 3x3x3 grid (hence identically). The tolerance is near-tight at p = 2 on this route.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PMAX = 64


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def pins():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    loga = (ROOT / "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md").read_text(encoding="utf-8")
    fine = (ROOT / "research/capped-fusion-t74-k554/vendor/pr1786/FINE-PRIME-PADDING.md").read_text(encoding="utf-8")
    down = (ROOT / "references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md").read_text(encoding="utf-8")
    need("across cells, use the retained downward Gaussian entries; set H_jj=1." in loga, "LOG-A downward phrase")
    need("across cells use rounded\nGaussian entries, with diagonal exactly one." in fine, "FINE-PRIME rounded phrase")
    need("poly(p) 2^(-(C-o(1))p)` in row and column norm" in fine, "FINE-PRIME perturbation phrase")
    need("Set P=32768p and eta=2^(-P)." in down, "downstream precision")


def split_identity():
    # (1-d)[a/(1-d) + (t-a)] - t + d(t-a) == 0 as a polynomial in (a, t, d), degree <= 2 in each variable
    vals = [F(1, 7), F(2, 5), F(3, 4)]
    for a, t, d in itertools.product(vals, repeat=3):
        need((1 - d) * (a / (1 - d) + (t - a)) - t + d * (t - a) == 0, "split identity")


def downward(p):
    D = 2 ** (32760 * p)
    delta, g = F(4, D), F(1, 8 * p * p)
    U = F(8 * p * p * (D - 4), D - 32 * p * p)
    for t_in_share in (F(0), F(1, 3), F(1)):
        T = 1 - g
        off = t_in_share * T / (1 - delta) + (1 - t_in_share) * T
        need(off <= T / (1 - delta) and 1 / (1 - off) <= U, "A: global ceiling is U")
    need(U * U < p ** 11 and U < p ** 6 and T / (1 - delta) < 1, "A: exponents 11 and 6")
    need(T / (1 - delta) - T <= 2 * delta <= F(1, 32 * p ** 3), "downward excess within the robust budget")
    return U


def robust(p):
    g, rho = F(1, 8 * p * p), F(1, 32 * p ** 3)
    off = 1 - g + rho
    need(off < 1 and 1 - off == F(4 * p - 1, 32 * p ** 3) >= F(7, 64 * p * p) > F(1, 10 * p * p), "B: gap")
    B = 1 / (1 - off)
    need(B * B < p ** 11 and B < p ** 6 and B < 10 * p * p and 100 * p ** 4 < p ** 11 and 10 * p * p < p ** 6, "B: endpoint 11, normalizer 6")
    need(2 * (p - 1) * F(1, 64 * p ** 4) <= rho, "B: per-entry error 1/(64p^4)")
    # the raw exponential oracle (|z - n| < 2 eta, eta = 2^-32768p, no downward repair) on <= 2W = 2(p-1) entries
    need(2 * (p - 1) * 2 * F(1, 2 ** (32768 * p)) <= rho, "B: raw oracle output fits the budget")
    L = p ** 24
    need((2 * L - 1) * (p - 1) < p ** 26 and (2 * L + 1) * (p - 1) < p ** 26, "bandwidth/agreement 26")


def main():
    pins()
    split_identity()
    for p in range(2, PMAX + 1):
        U = downward(p)
        robust(p)
        if p == 2:
            U2 = U
    # all p >= 2: (4p-1)/p >= 7/2; 70 > 64; 100 < p^7 and 10 < p^4 for p >= 2
    need(2 * (4 * 2 - 1) >= 7 * 2 and 70 > 64 and 100 < 2 ** 7 and 10 < 2 ** 4, "B for all p >= 2")
    # near-tightness at p = 2: the exponent-11 route needs (1 - off)^2 * 2^11 > 1 with off = 31/32 + rho
    ok = lambda rho: (1 - (F(31, 32) + rho)) ** 2 * 2 ** 11 > 1
    need(ok(F(91, 10000)) and not ok(F(92, 10000)), "p = 2 tolerance lies in (0.0091, 0.0092)")
    need(F(1, 256) < F(91, 10000), "the budget 1/(32p^3) = 1/256 at p = 2 is within it")
    print(json.dumps({"status": "PASS_DELTA_CROSS_CELL_TRANSFER", "exact_p_range": [2, PMAX],
                      "downward_global_ceiling_U_p2": f"{float(U2):.12f}", "robust_excess_budget": "1/(32p^3)",
                      "per_entry_budget": "1/(64p^4)", "p2_tolerance_interval": [0.0091, 0.0092],
                      "exponents": [11, 24, 26, 26, 6], "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
