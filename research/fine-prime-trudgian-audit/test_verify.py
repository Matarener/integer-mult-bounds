#!/usr/bin/env python3
"""Rejecting controls for the fine-prime interval audit."""
import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify  # noqa: E402


def main():
    # 1. If log t were only Theta(log p) (ell = 3 log2 p), the dominance test
    #    never passes: the p^2 factor beats exp(-sqrt(log t / R)).
    for e in [2, 10, 100, 300]:
        log_p = e * math.log(10)
        assert not verify.dominance(log_p, 3 * log_p)

    # 2. #4029's prime supply needs d <= ell^334. At epsilon = 1 - 1e-30,
    #    log d / log ell = epsilon / (1 - epsilon) ~ 1e30, far outside it.
    eps = Fraction(1) - Fraction(1, 10**30)
    assert eps / (1 - eps) > 334

    # 3. Without the -2eta shift the interval collapses: eta = 0 gives no theta >= 1/(4p^2).
    p = 5
    assert 1 / (1 - Fraction(0)) - 1 < Fraction(1, 4 * p * p)

    # 4. Sieve sanity against a direct count.
    assert verify.count_primes(100, 200) == sum(
        1 for n in range(101, 201) if all(n % q for q in range(2, math.isqrt(n) + 1)))

    # 5. The small-count rows are below the Trudgian threshold: they are sanity
    #    checks only, not evidence for the asymptotic step.
    assert not verify.dominance(math.log(12), 28 * math.log(2))
    print("PASS_FINE_PRIME_AUDIT_CONTROLS")


if __name__ == "__main__":
    main()
