#!/usr/bin/env python3
"""Independent check of #4451 and #4452: within-cell halo exponents under delta = 2^(2-32760p).

Separate route from the PRs' polynomial certificates. Write D = 2^(32760p), delta = 4/D, g = 1/(8p^2).
  (R) a - 4eta < ahat <= a, a > 2^-8p, eta = 2^-32768p  =>  a/ahat < 1/(1-delta).
  (N) Neumann ceiling (1-delta)/(g-delta) equals U = 8p^2(D-4)/(D-32p^2) (exact identity).
  (B) For all p >= 2, p < 2^p gives 512 p^4 < 2^(4p+9) <= D, so r = 32p^2/D < 1/(16p^2), and with
      V = 8p^2/(1-r):  8p^2 < U < V < 8p^2 + 1 <= 16p^2 - 1 < p^6, and V^2 < (8p^2+1)^2 < p^11.
  (S) Neumann polynomial P = p^-11 sum_{j<L} Q^j A*: P - A^-1 = -Q^L A^-1, |Q| < 1 - p^-22,
      so the error is < U (1-p^-22)^L <= U exp(-p^-22 L) < p^6 exp(-p^2) at L = p^24.
Every comparison is also checked by exact rational arithmetic for p = 2..64, and each "fails" entry at
p = 2 (or p = 3) is checked with certified bounds. Ryanson Jonathan with Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import json
import math
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
    down = (ROOT / "references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md").read_text(encoding="utf-8")
    for phrase in ("Set P=32768p and eta=2^(-P).", "2^(-8p)<a_j<=1.", "absolute error below four eta"):
        need(phrase in down, f"pinned phrase {phrase!r}")


def exact(p):
    D = 2 ** (32760 * p)
    delta, g = F(4, D), F(1, 8 * p * p)
    eta, floor_a = F(1, 2 ** (32768 * p)), F(1, 2 ** (8 * p))
    # (R): worst case a -> 2^-8p, ahat -> a - 4 eta
    need(4 * eta / floor_a == delta and delta < 1, "R: 4 eta / 2^-8p = delta")
    need(delta < F(1, 16 * p * p), "#4451: delta < 1/(16p^2)")
    U = F(8 * p * p * (D - 4), D - 32 * p * p)
    V = F(8 * p * p * D, D - 32 * p * p)
    need((1 - delta) / (g - delta) == U, "N: Neumann ceiling identity")
    need((1 - g) / (1 - delta) < 1, "rounded off-sum < 1, absolute sums < 2")
    need(8 * p * p < U < V < 8 * p * p + 1 <= 16 * p * p - 1 < p ** 6, "B: U chain")
    need(V * V < p ** 11, "B: V^2 < p^11")
    need(U * U < p ** 11 and 4 < p ** 11, "spectrum of A*A inside (p^-11, p^11)")
    L = p ** 24
    need((2 * L - 1) * (p - 1) < p ** 26 and (2 * L + 1) * (p - 1) < p ** 26, "bandwidth/agreement < p^26")
    return U


def series_error_ok(p, length_exp):
    """certified: U*(1-x)^L < p^6 exp(-p^2) with x = p^-22, L = p^length_exp; uses (1-x)^L <= exp(-xL)"""
    xL = F(p ** length_exp, p ** 22)
    U_upper = 8 * p * p + 1
    # need log(U_upper) - xL < 6 log p - p^2, i.e. xL - p^2 > log(U_upper / p^6) (negative RHS)
    return xL - p * p > math.log(U_upper / p ** 6) + 1e-9


def series_error_fails(p, length_exp):
    """certified failure of the bound route: U*(1-x)^L >= p^6 exp(-p^2), using (1-x)^L >= exp(-xL - x^2 L)"""
    x = F(1, p ** 22)
    L = p ** length_exp
    lower_exp = x * L + x * x * L
    U_lower = 8 * p * p
    return math.log(U_lower / p ** 6) - float(lower_exp) > -p * p + 1e-9


def main():
    pins()
    for p in range(2, PMAX + 1):
        U = exact(p)
        if p == 2:
            U2 = U
    # general p >= 2 by p < 2^p (B): 512 p^4 < 2^(4p+9) <= 2^(32760p) = D
    need(all(p < 2 ** p for p in range(2, 200)), "p < 2^p sample")  # induction: 2^(p+1) = 2*2^p > 2p >= p+1
    need(4 * 2 + 9 <= 32760 * 2 and 32760 - 4 > 0, "4p+9 <= 32760p for p >= 2")
    # with r < 1/(16p^2): V = 8p^2/(1-r) < 8p^2 (1 + 2r) < 8p^2 + 1; 8p^2 + 1 <= 16p^2 - 1 iff p^2 >= 1/4;
    # 16p^2 - 1 < p^6 iff p^4 >= 16; (8p^2+1)^2 < p^11: p = 2 gives 1089 < 2048, p >= 3 gives <= 81 p^4 <= p^8.
    need(33 ** 2 < 2 ** 11 and 64 + 16 + 1 <= 81 <= 3 ** 4, "V^2 < p^11 for all p")
    # Neumann series error at L = p^24 holds; lengths and endpoints one lower fail on this route at p = 2
    need(all(series_error_ok(p, 24) for p in range(2, PMAX + 1)), "S: error < p^6 exp(-p^2) at L = p^24")
    need(series_error_fails(2, 23), "series length 23 fails at p = 2")
    need(U2 > 2 ** 5 and U2 * U2 > 2 ** 10, "endpoint 10 and normalizer 5 fail at p = 2")
    need((2 * 2 ** 24 + 1) * 1 > 2 ** 25, "loose radius exceeds p^25 at p = 2")
    need(all((2 * p ** 24 - 1) * (p - 1) > p ** 25 for p in range(3, PMAX + 1)), "sharp radius exceeds p^25, p >= 3")
    need((2 * 2 ** 24 - 1) * 1 < 2 ** 25, "sharp radius stays below p^25 at p = 2 (only the loose count fails)")
    print(json.dumps({"status": "PASS_DELTA_HALO_EXPONENT_CHECK", "exact_p_range": [2, PMAX],
                      "exponents": {"spectral_endpoint": 11, "series_length": 24, "bandwidth": 26,
                                    "agreement_distance": 26, "normalizer": 6},
                      "U_at_p2": f"{float(U2):.12f}", "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
