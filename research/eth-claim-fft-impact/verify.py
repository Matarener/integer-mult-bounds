"""Re-check the computed figures of research/eth-claim-fft-impact.

Standard library only; runs in well under a second.

Section 5 of README.md quotes the size of the claimed speed-up with every hidden constant set to 1:
  - the factor ln ln n / sqrt(ln n) in the exponent at n = 10^4, 10^6 and 10^30;
  - the n beyond which the sharper exponent n * ln ln n / sqrt(ln n) beats 3-SAT's 1.307^n;
  - the n beyond which the Lean exponent n * (ln ln n)^2 / sqrt(ln n) beats brute force 2^n.

This script recomputes each figure from its formula, checks that README.md prints it as computed,
and checks that four false figures are rejected by the same tests (failure controls).
Prints PASS_ETH_CLAIM_FFT_IMPACT on success; exits with status 1 otherwise.
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LN10 = math.log(10.0)


def factor(log10_n):
    """ln ln n / sqrt(ln n) at n = 10^log10_n."""
    big_l = log10_n * LN10
    return math.log(big_l) / math.sqrt(big_l)


def lean_factor(big_l):
    """(ln ln n)^2 / sqrt(ln n) as a function of L = ln n."""
    return math.log(big_l) ** 2 / math.sqrt(big_l)


def crossing(g, target, lo, hi):
    """The L in [lo, hi] with g(L) = target, for g decreasing on [lo, hi]."""
    if not (g(lo) > target > g(hi)):
        raise AssertionError("no single crossing in the bracket")
    for _ in range(200):
        mid = (lo + hi) / 2
        if g(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def sharp_threshold_log10():
    """log10 of the n beyond which 2^(n ln ln n / sqrt(ln n)) < 1.307^n."""
    rate = math.log2(1.307)
    # ln L / sqrt L decreases for L > e^2; its maximum 2/e is above the rate.
    return crossing(lambda big_l: math.log(big_l) / math.sqrt(big_l), rate, math.e ** 2, 1e5) / LN10


def lean_threshold_log10():
    """log10 of the n beyond which 2^(n (ln ln n)^2 / sqrt(ln n)) < 2^n."""
    # (ln L)^2 / sqrt L decreases for L > e^4.
    return crossing(lean_factor, 1.0, math.e ** 4, 1e6) / LN10


def check_factor(log10_n, claimed):
    return round(factor(log10_n), 2) == claimed


def check_threshold(kind, claimed_exponent):
    value = sharp_threshold_log10() if kind == "sharp" else lean_threshold_log10()
    return round(value) == claimed_exponent


# (test, the phrase README.md must contain)
CLAIMS = [
    (lambda: check_factor(4, 0.73), "0.73 at n = 10^4"),
    (lambda: check_factor(6, 0.71), "0.71 at n = 10^6"),
    (lambda: check_factor(30, 0.51), "0.51 at n = 10^30"),
    (lambda: check_threshold("sharp", 79), "1.307^n, only beyond about n = 10^79"),
    (lambda: check_threshold("lean", 2390), "2^n, only beyond about n = 10^2390"),
]

# false figures that the same tests must reject
CONTROLS = [
    (lambda: check_factor(4, 0.80), "factor 0.80 at n = 10^4"),
    (lambda: check_factor(30, 0.61), "factor 0.61 at n = 10^30"),
    (lambda: check_threshold("sharp", 50), "sharp exponent beats 1.307^n beyond 10^50"),
    (lambda: check_threshold("lean", 239), "Lean exponent beats 2^n beyond 10^239"),
]


def main():
    readme = " ".join((HERE / "README.md").read_text(encoding="utf-8").split())
    failures = []
    for test, phrase in CLAIMS:
        if not test():
            failures.append("figure does not match its formula: " + phrase)
        if phrase not in readme:
            failures.append("README.md does not print: " + phrase)
    for test, label in CONTROLS:
        if test():
            failures.append("false figure accepted: " + label)
    print("factor at 10^4, 10^6, 10^30: %.4f %.4f %.4f" % (factor(4), factor(6), factor(30)))
    print("sharp exponent beats 1.307^n beyond n = 10^%.1f" % sharp_threshold_log10())
    print("Lean exponent beats 2^n beyond n = 10^%.1f" % lean_threshold_log10())
    print("claims checked: %d; controls rejected: %d of %d"
          % (len(CLAIMS), sum(1 for t, _ in CONTROLS if not t()), len(CONTROLS)))
    if failures:
        for line in failures:
            print("FAIL " + line)
        return 1
    print("PASS_ETH_CLAIM_FFT_IMPACT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
