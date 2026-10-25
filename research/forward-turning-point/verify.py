#!/usr/bin/env python3
"""Turning-point asymptotics of the broad forward phase-cell inverse.

Prediction (README): for K_(k,i) = alpha^-1 exp(-b0 (i - lambda k - c)^2) on a phase cell starting at beta' = -1/2,

    ||K^-1||_2 * sqrt(theta)  ->  e^(a/4) / (2 alpha sqrt(pi)),   a = pi alpha^2,  as theta -> 0.

The verifier builds the banded block (entries farther than 20 from the centre are below e^-78 and dropped; the dropped
part is bounded and reported), computes ||K^-1||_2 by inverse power iteration on K^T K with sparse LU, and checks
  * the ratio to the prediction tends to 1: within 1% at theta = 1/102400 for alpha = 3 and 4, monotone over the
    last three theta values, with 1 - ratio shrinking by a factor near 2 per factor 4 in theta (O(theta^1/2));
  * agreement with a dense SVD on the full cell at theta = 1/400 (band truncation control);
  * localisation: halving the block length (still >= 30 theta^-1/2) changes the value by < 1e-6 relative.
Numerical evidence for a formal derivation; not a proof. Pinned: FORWARD-SMALL-A-AUDIT.md phrase.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
import math
from pathlib import Path
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

ROOT = Path(__file__).resolve().parents[2]
PHRASE = "`||K^-1|| <= alpha exp(3b/4) c_b^-4/(1-exp(-b rho theta))^2`"
BAND = 20


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def kmat(alpha, theta, n):
    rho = 1 + theta
    lam, b0, c = 1 / rho, math.pi / alpha ** 2, 0.5 / rho      # beta'_0 = -rho c = -1/2
    rows, cols, vals = [], [], []
    for k in range(n):
        centre = int(lam * k + c)
        i = np.arange(max(0, centre - BAND), min(n, centre + BAND + 2))
        rows.extend([k] * len(i))
        cols.extend(i.tolist())
        vals.extend((np.exp(-b0 * (i - lam * k - c) ** 2) / alpha).tolist())
    return sp.csc_matrix((vals, (rows, cols)), shape=(n, n))


def inv_norm2(K):
    lu, luT = spl.splu(K), spl.splu(K.T.tocsc())
    x = np.random.default_rng(0).standard_normal(K.shape[0])
    x /= np.linalg.norm(x)
    s = 0.0
    for _ in range(500):
        z = luT.solve(lu.solve(x))
        s_new = math.sqrt(np.linalg.norm(z))
        x = z / np.linalg.norm(z)
        if abs(s_new - s) < 1e-12 * s_new:
            break
        s = s_new
    return s_new


def main():
    text = (ROOT / "research/capped-phase-fusion/FORWARD-SMALL-A-AUDIT.md").read_text(encoding="utf-8")
    need(PHRASE in text, "pinned bound")
    out = {"status": "PASS_FORWARD_TURNING_POINT", "new_kappa_claimed": False, "alphas": {}}
    for alpha in (3, 4):
        pred = math.exp(math.pi * alpha ** 2 / 4) / (2 * alpha * math.sqrt(math.pi))
        b0 = math.pi / alpha ** 2
        need(math.exp(-b0 * BAND ** 2) < 1e-20, "dropped band entries negligible")
        rows = []
        for inv_th in (400, 1600, 6400, 25600, 102400):
            th = 1 / inv_th
            n = int(min(inv_th, 60 * math.sqrt(inv_th)))
            s = inv_norm2(kmat(alpha, th, n))
            rows.append((inv_th, n, s, s * math.sqrt(th) / pred))
        # dense control on the whole cell
        Kd = kmat(alpha, 1 / 400, 400).toarray()
        dense = 1 / np.linalg.svd(Kd, compute_uv=False)[-1]
        need(abs(dense - rows[0][2]) < 1e-6 * dense, "sparse power iteration matches dense SVD")
        # localisation control
        half = inv_norm2(kmat(alpha, 1 / 102400, 30 * 320))
        need(abs(half - rows[-1][2]) < 1e-6 * half, "the norm is localised at the turning point")
        ratios = [r[3] for r in rows]
        need(abs(1 - ratios[-1]) < 0.01, f"alpha={alpha}: within 1% at theta=1/102400")
        gaps = [1 - r for r in ratios[-3:]]
        need(gaps[0] > gaps[1] > gaps[2] > 0 and all(1.5 < gaps[i] / gaps[i + 1] < 2.6 for i in range(2)),
             f"alpha={alpha}: O(theta^1/2) convergence")
        out["alphas"][alpha] = {"predicted_constant": f"{pred:.4f}",
                                "rows": [{"inv_theta": a, "n": b, "inv_norm2": f"{c:.3f}", "ratio": f"{d:.6f}"}
                                         for a, b, c, d in rows]}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
