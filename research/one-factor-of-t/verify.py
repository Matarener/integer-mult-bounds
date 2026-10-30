#!/usr/bin/env python3
"""Factors of T on one coefficient's error path: fixed-point simulation of #4100's normalized synthetic convolution.

PROOF.md computes (f*g)/(rM) as M F_plus((F_minus f)(F_minus g)/r) with normalized butterflies
H0 = [[1,1],[1,-1]]/2, truncation toward zero after each round, and an exact final multiplication by M = T/r.
The README's ledger says one coefficient's error is at most about M * (c ell) * 2^-P: the factor M multiplies
only rounding made inside the synthetic convolution, and errors already present in the inputs pass through a
contraction (a cyclic average of bounded data). This verifier simulates the scalar case r = 1 (so M = T) with
P-bit truncation for T = 2^4 .. 2^14 and checks:
  * max error <= 4 * M * ell * 2^-P on every size (one factor of M, with a logarithmic level count);
  * max error / (M * 2^-P) stays bounded while max error / (M^2 * 2^-P) -> 0 (no second factor of T);
  * an exact-arithmetic input perturbation of sup size eta changes the output by at most eta (no M).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "research/unconditional-batched-crt/PROOF.md"
PHRASES = (
    "Use the normalized simultaneous butterfly H0=[[1,1],[1,-1]]/2 from",
    "    M F_plus((F_minus f)(F_minus g)/r)=(f*g)/(rM)",
    "It can amplify numerical error by M<2^p, already allowed in the error",
    "all norm changes costs at most2^O(p), since T=2^Theta(p).",
)
P = 40
rng = np.random.default_rng(4371)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def trunc(z):
    """truncate real and imaginary parts toward zero on the 2^-P grid"""
    s = 2.0 ** P
    return np.trunc(z.real * s) / s + 1j * np.trunc(z.imag * s) / s


def normalized_fft(x, sign):
    """radix-2 decimation in time with H0 butterflies; every level divides by 2 and truncates"""
    n = len(x)
    ell = n.bit_length() - 1
    rev = np.array([int(format(i, f"0{ell}b")[::-1], 2) for i in range(n)])
    a = x[rev].astype(complex)
    size = 2
    while size <= n:
        half = size // 2
        w = trunc(np.exp(sign * 2j * np.pi * np.arange(half) / size))
        a = a.reshape(-1, size)
        top, bot = a[:, :half], a[:, half:] * w
        a = trunc(np.concatenate([(top + bot) / 2, (top - bot) / 2], axis=1)).reshape(-1)
        size *= 2
    return a


def synthetic(f, g):
    T = len(f)
    uf, ug = normalized_fft(f, -1), normalized_fft(g, -1)
    prod = trunc(uf * ug)                     # r = 1
    back = normalized_fft(prod, +1)
    return back * T                           # exact multiplication by M = T


def exact(f, g):
    T = len(f)
    return np.fft.ifft(np.fft.fft(f) * np.fft.fft(g)) / T     # (f*g)/T


def main():
    text = PROOF.read_text(encoding="utf-8")
    for phrase in PHRASES:
        need(phrase in text, f"PROOF.md phrase: {phrase}")
    rows = []
    unit = 2.0 ** -P
    for ell in range(4, 15):
        T = 2 ** ell
        worst = 0.0
        for _ in range(3):
            f = (rng.uniform(-1, 1, T) + 1j * rng.uniform(-1, 1, T)) / 4
            g = (rng.uniform(-1, 1, T) + 1j * rng.uniform(-1, 1, T)) / 4
            err = np.abs(synthetic(f, g) - exact(f, g)).max()
            worst = max(worst, err)
            # input perturbation through the exact map: no factor of M
            eta = 1e-6
            e = eta * np.exp(2j * np.pi * rng.uniform(0, 1, T))
            change = np.abs(exact(f + e, g) - exact(f, g)).max()
            need(change <= eta * (1 + 1e-9), "input error is not amplified by M")
        need(worst <= 4 * T * ell * unit, f"T=2^{ell}: error <= 4 M ell 2^-P")
        rows.append({"T": T, "ell": ell, "err_over_unit": f"{worst / unit:.1f}",
                     "over_M_ell": f"{worst / (T * ell * unit):.4f}",
                     "over_M2": f"{worst / (T * T * unit):.2e}"})
    m_ratio = [float(r["over_M_ell"]) for r in rows]
    m2_ratio = [float(r["over_M2"]) for r in rows]
    need(max(m_ratio) < 4 and m2_ratio[-1] < m2_ratio[0] / 100, "one factor of M, not two")
    print(json.dumps({"status": "PASS_ONE_FACTOR_OF_T", "precision_bits": P, "rows": rows,
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
