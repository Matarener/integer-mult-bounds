#!/usr/bin/env python3
"""Broad forward phase-cell blocks at the fine-prime theta: rigorous inverse-norm bounds vs FORWARD-SMALL-A-AUDIT.

FINE-PRIME.md reuses FORWARD-SMALL-A-AUDIT.md sections 1-2,
    ||K^-1|| <= alpha exp(3b/4) c_b^-4 / (1 - exp(-b rho theta))^2 = O(alpha^5 rho^2 theta^-2 exp(a rho/3)),
at theta = 1/(4p^2). For p in PRIMES, alpha = ceil(sqrt((4/pi) log(16p))), it builds the actual blocks
K_(k,i) = alpha^-1 exp(-b0 (i - lambda k - c)^2) on contiguous intervals inside one phase cell
(beta'_k = theta k - rho c in [-1/2, 1/2)), inverts them in float64 and bounds ||K^-1||_inf and ||K^-1||_1
rigorously from float residuals with the standard gamma_n rounding bound. It checks every bound against
the audit's ceiling and records how the true norm scales with theta.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "research/capped-phase-fusion/FORWARD-SMALL-A-AUDIT.md":
        ("`||K^-1|| <= alpha exp(3b/4) c_b^-4/(1-exp(-b rho theta))^2`",
         "`c_b^-4 <= exp(pi alpha^2 rho/3)=exp(a rho/3)`"),
    "research/unconditional-batched-crt/vendor/FINE-PRIME.md":
        ("||K^-1|| <= O(alpha^5 rho^2 theta^-2 exp(a rho/3)).",),
}
PRIMES = (5, 7, 11, 13, 19)
STARTS = (-0.5, -0.25, 0.0)
U = 2.0 ** -53


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def ceiling(alpha, theta):
    rho = 1 + theta
    b = math.pi / (alpha ** 2 * rho ** 2)
    log_cb = sum(math.log1p(-math.exp(-2 * b * rho * m)) for m in range(1, 20000))
    return alpha * math.exp(3 * b / 4) * math.exp(-4 * log_cb) / (-math.expm1(-b * rho * theta)) ** 2


def block(alpha, theta, n, beta_start):
    rho = 1 + theta
    lam, b0 = 1 / rho, math.pi / alpha ** 2
    c = -beta_start / rho                       # beta'_0 = theta*0 - rho c = beta_start
    k = np.arange(n, dtype=float)
    arg = b0 * (k[None, :] - lam * k[:, None] - c) ** 2
    kmat = np.exp(-arg) / alpha
    # relative entry error: exponent argument error <= arg * 8u, exp and division <= 3u
    rel = arg.max() * 8 * U + 3 * U
    return kmat, rel


def rigorous_norms(kmat, rel):
    """upper bounds of ||K^-1||_inf and ||K^-1||_1 for the true K with |K - kmat| <= rel |kmat|"""
    n = kmat.shape[0]
    x = np.linalg.inv(kmat)
    g = (n + 2) * U / (1 - (n + 2) * U)
    ax, ak = np.abs(x), np.abs(kmat)
    out = []
    for left in (True, False):
        r = np.eye(n) - (x @ kmat if left else kmat @ x)
        prod = ax @ ak if left else ak @ ax
        rmat = np.abs(r) + g * (prod + np.eye(n)) + rel * prod * (1 + g)
        norm = (lambda m: m.sum(1).max()) if left else (lambda m: m.sum(0).max())
        rr = norm(rmat)
        need(rr < 0.5, "residual small")
        nx = norm(ax) * (1 + g)
        out.append(nx / (1 - rr))
    return out[0], out[1], float(np.linalg.norm(x, 2))


def main():
    for path, phrases in PINS.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for phrase in phrases:
            need(phrase in text, f"{path}: {phrase}")
    rows, scaling = [], []
    for p in PRIMES:
        theta = 1 / (4 * p * p)
        alpha = math.ceil(math.sqrt((4 / math.pi) * math.log(16 * p)))
        ceil_val = ceiling(alpha, theta)
        need(ceil_val < 16 * p ** 4 * alpha ** 5 * math.exp(math.pi * alpha ** 2 * (1 + theta) / 3) * 10,
             "ceiling has the stated alpha^5 theta^-2 exp(a rho/3) shape")
        worst = [0.0, 0.0, 0.0]
        cell = int(round(1 / theta))
        for beta_start in STARTS:
            span = int(math.floor((0.5 - beta_start) / theta))   # beta' stays below 1/2
            lengths = sorted({min(span, 2 ** j) for j in range(1, 12)} | {span})
            for n in lengths:
                kmat, rel = block(alpha, theta, n, beta_start)
                inf_hi, one_hi, two = rigorous_norms(kmat, rel)
                need(max(inf_hi, one_hi) < ceil_val, f"p={p}, n={n}: below the audit ceiling")
                worst = [max(worst[0], inf_hi), max(worst[1], one_hi), max(worst[2], two)]
        rows.append({"p": p, "alpha": alpha, "theta": f"1/{cell}", "ceiling": f"{ceil_val:.4g}",
                     "inf_upper": f"{worst[0]:.2f}", "one_upper": f"{worst[1]:.2f}", "two": f"{worst[2]:.2f}",
                     "ratio_to_ceiling": f"{max(worst[:2]) / ceil_val:.2e}"})
    # theta-scaling at fixed alpha = 3, full cell from beta' = -1/2
    for inv_theta in (100, 200, 400, 800, 1600, 3200):
        theta = 1 / inv_theta
        kmat, rel = block(3, theta, inv_theta, -0.5)
        _, _, two = rigorous_norms(kmat, rel)
        scaling.append({"inv_theta": inv_theta, "two": f"{two:.2f}", "two_times_sqrt_theta": f"{two * theta ** 0.5:.3f}"})
    s = [float(r["two_times_sqrt_theta"]) for r in scaling]
    need(max(s) / min(s) < 1.05, "||K^-1||_2 sqrt(theta) constant within 5% over theta = 1/100 .. 1/3200")
    print(json.dumps({"status": "PASS_FORWARD_FINE_THETA_CONDITIONING", "primes": rows,
                      "theta_scaling_alpha3": scaling, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
