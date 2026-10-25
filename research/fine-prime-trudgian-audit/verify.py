#!/usr/bin/env python3
"""Audit the fine-prime interval step of the proposed #4100 construction.

Proposition (vendor/FINE-PRIME.md section 1, used by PROOF.md "Sizes, setup and
elementary fallback" and GAUSSIAN.md lines 13-19): with eta = 1/(4p^2) and a
dyadic target t = 2^ell, ell = Theta(p^(1-epsilon)), epsilon = 1 - 10^-30, the
interval ((1-2eta)t, (1-eta)t] eventually holds at least t/(8 p^2 log t)
primes, more than d = Theta(p^epsilon), and every prime s there gives
theta = t/s - 1 in [1/(4p^2), 1/p^2].

Checks:
1. source binding: the cited theorem, eta, epsilon and theta range are read
   from the pinned #4100 files;
2. exact theta endpoints for p = 2..199;
3. the sufficient Trudgian-dominance test and its explicit threshold at the
   caller's epsilon (floating point, logarithmic domain; reported, not used
   as a proof);
4. exact prime counts (segmented sieve) in small real intervals.
"""
import json
import math
from fractions import Fraction
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
SRC = ROOT / "research" / "unconditional-batched-crt"

# Trudgian, arXiv:1401.2689v2, Theorem 2: for x >= 229,
# |pi(x) - li(x)| <= 0.2795 x (log x)^(-3/4) exp(-sqrt(log x / 6.455)).
A, R, X0 = 0.2795, 6.455, 229


def check_sources():
    fine = (SRC / "vendor" / "FINE-PRIME.md").read_text(encoding="utf-8")
    proof = (SRC / "PROOF.md").read_text(encoding="utf-8")
    gauss = (SRC / "GAUSSIAN.md").read_text(encoding="utf-8")
    for needle in ["eta_p = 1/(4p^2)", "(1-2 eta_p) t_i < s_i <= (1-eta_p) t_i",
                   "|pi(x)-li(x)| <= 0.2795 x (log x)^(-3/4)",
                   "exp(-sqrt(log x/6.455))", "for x>=229",
                   "x/(8p^2 log x)", "1/(4p^2) < theta_i <= 1/(2p^2-1) <= 1/p^2"]:
        assert needle in fine, needle
    assert "d=Theta(p^epsilon), epsilon=1-10^-30" in proof
    assert "ell=Theta(p^(1-epsilon))" in proof
    assert "theta_i in [1/(4p^2),1/p^2]" in proof
    assert "log t=Theta(p^(1-epsilon))" in gauss
    supply = (ROOT / "research" / "many-axis-prime-supply" / "README.md").read_text(encoding="utf-8")
    assert "2≤d≤ell^334" in supply and "(t(1−1/(3d)), t(1−1/(4d))]" in supply


def check_theta():
    for p in range(2, 200):
        eta = Fraction(1, 4 * p * p)
        closed = 1 / (1 - eta) - 1      # s = (1-eta)t, attained
        open_ = 1 / (1 - 2 * eta) - 1   # s -> (1-2eta)t, not attained
        assert Fraction(1, 4 * p * p) < closed < open_
        assert open_ == Fraction(1, 2 * p * p - 1) <= Fraction(1, p * p)
        # capacity: s/t > 1 - 2 eta for each axis, so S/T > 1 - d/(2p^2) > 1/2 for d <= p
        assert 1 - Fraction(p, 2 * p * p) > Fraction(1, 2)


def dominance(log_p, L):
    """True if 2*Trudgian error <= half of the main term eta*t/log t at log t = L.

    Equivalent to log(16) + 2 log p + log L + log(0.2795) - 0.75 log L
    - sqrt(L/R) <= 0.  Both endpoint errors are bounded by the value at t,
    since x (log x)^(-3/4) exp(-sqrt(log x/R)) increases for x >= 229.
    """
    return (math.log(16) + 2 * log_p + 0.25 * math.log(L) + math.log(A)
            - math.sqrt(L / R)) <= 0


def needed_L(log_p):
    lo, hi = math.log(X0), 1e6
    while not dominance(log_p, hi):
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if dominance(log_p, mid) else (mid, hi)
    return hi


def caller_threshold(delta=1e-30, const=6.0):
    """Smallest ln p with ell = p^delta/const >= needed ell, by bisection on ln p."""
    def ok(u):
        return delta * u - math.log(const) >= math.log(needed_L(u) / math.log(2))
    lo, hi = 1.0, 1e36
    assert not ok(lo) and ok(hi)
    for _ in range(400):
        mid = math.sqrt(lo * hi)
        lo, hi = (lo, mid) if ok(mid) else (mid, hi)
    return hi


def small_primes(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


def count_primes(a, b):
    """Number of primes in (a, b]."""
    lo = a + 1
    seg = bytearray([1]) * (b - lo + 1)
    for q in small_primes(math.isqrt(b)):
        start = max(q * q, (lo + q - 1) // q * q)
        seg[start - lo::q] = bytearray(len(seg[start - lo::q]))
    return sum(seg)


def check_counts():
    rows = []
    for p in [2, 3, 4, 6, 8, 12]:
        for ell in [24, 28]:
            t = 2 ** ell
            eta = Fraction(1, 4 * p * p)
            a = math.floor((1 - 2 * eta) * t)
            b = math.floor((1 - eta) * t)
            if b - a > 3_000_000:
                continue
            cnt = count_primes(a, b)
            claim = t / (8 * p * p * math.log(t))
            assert cnt > claim, (p, ell, cnt, claim)
            rows.append({"p": p, "ell": ell, "primes": cnt, "claimed_min": round(claim, 1),
                         "trudgian_test_applies": dominance(math.log(p), math.log(t))})
    assert len(rows) == 9 and not any(r["trudgian_test_applies"] for r in rows)
    return rows


def main():
    check_sources()
    check_theta()
    thresholds = {str(e): round(needed_L(e * math.log(10)) / math.log(2), 1)
                  for e in [1, 2, 3, 10, 100, 10**6, 10**30]}
    # needed ell grows like (2 ln p)^2 * R / ln 2: polynomial in log p
    ratio = needed_L(1e30 * math.log(10)) / (6.455 * (2 * 1e30 * math.log(10)) ** 2)
    assert 0.99 < ratio < 1.01
    ln_p = caller_threshold()
    assert 1e32 < ln_p < 2e32
    rows = check_counts()
    out = {"needed_ell_by_log10_p": thresholds, "caller_threshold_ln_p": ln_p,
           "small_counts": rows}
    print(json.dumps(out, indent=1))
    print("PASS_FINE_PRIME_INTERVAL_STEP_AS_STATED")


if __name__ == "__main__":
    main()
