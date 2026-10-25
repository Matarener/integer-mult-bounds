#!/usr/bin/env python3
"""Dimension exponent of #4100's 2^{-4p} sentence, and the product-reading gap.

The checker uses only the standard library. It binds two source sentences,
proves the size-section exponent for every admissible b, and checks the
conditional one-factor precision coefficient by exact integer comparison.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "research/unconditional-batched-crt/PROOF.md"
GAUSSIAN = ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"

AMPLIFICATION = (
    "There are polynomially many\n"
    "levels/groups per coefficient. Allowing even the full array dimension in\n"
    "all norm changes costs at most2^O(p), since T=2^Theta(p)."
)


def ceil_log2(n):
    if n < 1:
        raise ValueError(n)
    return (n - 1).bit_length()


def floor_log2(n):
    if n < 1:
        raise ValueError(n)
    return n.bit_length() - 1


def exponent_k(n):
    """Unique k with T=2^k in [4n/b, 8n/b), b=ceil(log2 n)."""
    b = ceil_log2(n)
    if b < 2:
        raise ValueError(n)
    k = 0
    while (b << k) < 4 * n:
        k += 1
        if k > b + 4:
            raise AssertionError((n, b, k))
    if (b << k) >= 8 * n:
        raise AssertionError(("interval missed", n, b, k))
    if k and (b << (k - 1)) >= 4 * n:
        raise AssertionError(("not minimal", n, b, k))
    return b, 6 * b, k


def bucket_bounds(b):
    """Proved bounds on k for every n with ceil(log2 n)=b and n>=4."""
    t = floor_log2(b)
    if not ((1 << t) <= b < (1 << (t + 1))):
        raise AssertionError(b)
    # Upper. Admissible n satisfy n<=2^b, so b*2^k < 8n <= 2^{b+3}.
    # Thus b*2^k <= 2^{b+3}-1. Since b>=2^t,
    # b*2^{b+3-t} >= 2^{b+3} > 2^{b+3}-1, so 2^k < 2^{b+3-t} and k<=b+2-t.
    if (b << (b + 3 - t)) < (1 << (b + 3)):
        raise AssertionError(("upper comparison", b))
    # Lower. The smallest admissible n is 2^{b-1}+1, so 4n > 2^{b+1}.
    # b<2^{t+1} makes 2^{b+1}/b > 2^{b-t}, hence 2^k > 2^{b-t} and k>=b-t+1.
    if 4 * ((1 << (b - 1)) + 1) <= (1 << (b + 1)):
        raise AssertionError(("lower comparison", b))
    return b - t + 1, b + 2 - t


def sum_holds(b, factors, degree, coefficient, constant):
    """constant * (6b)^degree * T^factors * 2^{-coefficient * p} < 2^{-4p}.

    Uses the proved upper bound on log2 T, so a pass covers every n in the bucket.
    """
    _, high = bucket_bounds(b)
    room = (coefficient - 4) * 6 * b - factors * high
    if room <= 0:
        return False
    return constant * pow(6 * b, degree) < (1 << room)


def first_b0(factors, degree, coefficient, constant, limit=400):
    for start in range(2, limit):
        if all(sum_holds(b, factors, degree, coefficient, constant)
               for b in range(start, limit)):
            return start
    return None


def require_source_sentences():
    proof = PROOF.read_text(encoding="utf-8")
    gaussian = GAUSSIAN.read_text(encoding="utf-8")
    required = (
        (proof, "nominal p=6b"),
        (proof, "power of two in [4n/b,8n/b)"),
        (proof, AMPLIFICATION),
        (proof, "absolute coefficient error less than 2^-4p"),
        (gaussian, "row gap delta>=1/(16p^2)"),
        (gaussian, "||H^-1||_infinity<=delta^-1"),
        (gaussian, "||H^-1||_1<=delta^-1+2w(1-delta)delta^-2"),
        (gaussian, "2^{-(C-O(1))p}"),
    )
    for text, snippet in required:
        if snippet not in text:
            raise AssertionError("missing source sentence: " + snippet[:80])
    # Control: the gap is this sentence, not a nearby cost row.
    if "costs at most 2^{p/6}" in proof:
        raise AssertionError("source unexpectedly contains the explicit exponent")


def check_dimension(exhaustive_n=200000, bucket_limit=4096):
    sharp_upper = sharp_lower = None
    previous = None
    for n in range(4, exhaustive_n + 1):
        b, p, k = exponent_k(n)
        low, high = bucket_bounds(b)
        if not (low <= k <= high and p == 6 * b):
            raise AssertionError((n, b, p, k, low, high))
        if previous is not None and b == previous[0] and k < previous[1]:
            raise AssertionError(("k decreased", n, k, previous))
        previous = (b, k)
        if k == high and sharp_upper is None:
            sharp_upper = (n, b, k)
        if k == low and sharp_lower is None:
            sharp_lower = (n, b, k)
    if sharp_upper != (4, 2, 3):
        raise AssertionError(sharp_upper)
    if sharp_lower != (5, 3, 3):
        raise AssertionError(sharp_lower)
    for b in range(2, bucket_limit + 1):
        low, high = bucket_bounds(b)
        _, _, k_min = exponent_k((1 << (b - 1)) + 1)
        _, _, k_max = exponent_k(1 << b)
        if k_min < low or k_max > high or k_min > k_max:
            raise AssertionError((b, k_min, k_max, low, high))
    # Control: shaving one bit off the upper bound is false.
    if exponent_k(4)[2] <= bucket_bounds(2)[1] - 1:
        raise AssertionError("upper bound was not sharp")
    return sharp_upper, sharp_lower


def check_product_reading():
    """m(p)=p factors of T are not a 2^{O(p)} amplification."""
    ratios = []
    expected = (3, 4, 14, 60, 250, 1016, 4086)
    for b in (2, 4, 16, 64, 256, 1024, 4096):
        low, _ = bucket_bounds(b)
        _, p, k = exponent_k(1 << b)
        if k < low:
            raise AssertionError((b, k, low))
        ratios.append(k)
        if p * k <= 10 * p and b >= 64:
            raise AssertionError((b, p, k))
    if tuple(ratios) != expected or ratios != sorted(ratios):
        raise AssertionError(ratios)
    # Control: a uniform linear claim with coefficient 10 fails at b=64.
    if ratios[3] <= 10:
        raise AssertionError("product reading unexpectedly became O(p) with constant 10")
    return ratios


def check_conditional_constants():
    claims = (
        # one factor T, no extra polynomial: C=5 for every b>=2
        (1, 0, 5, 1, 2),
        # one T and p^10: C=5 from b=13; C=8 from b=2
        (1, 10, 5, 1, 13),
        (1, 10, 8, 1, 2),
        # infinity-norm inverse 16 p^2 times one T
        (1, 2, 5, 16, 3),
        (1, 2, 6, 16, 2),
        # one-norm majorant 512 p^5 times one T
        (1, 5, 5, 512, 8),
        (1, 5, 7, 512, 2),
        # six T factors need a linear coefficient past 4+6/6=5
        (6, 0, 6, 1, 2),
        (6, 10, 6, 1, 9),
    )
    found = []
    for factors, degree, coefficient, constant, expected in claims:
        got = first_b0(factors, degree, coefficient, constant)
        if got != expected:
            raise AssertionError((factors, degree, coefficient, constant, got, expected))
        found.append(got)
    # Control: six T factors leave no room at C=5, at every checked bucket.
    if first_b0(6, 10, 5, 1) is not None:
        raise AssertionError("C=5 unexpectedly absorbed six dimension factors")
    if any(sum_holds(b, 6, 10, 5, 1) for b in range(2, 80)):
        raise AssertionError("C=5 passed a six-factor bucket")
    return found


def inverse_majorant(p):
    """Displayed dominance bounds at delta>=1/(16p^2) and bandwidth <= p-1.

    The infinity norm is at most 16 p^2. The one-norm is at most
    512 p^5 - 512 p^4 - 32 p^3 + 48 p^2, which is < 512 p^5.
    """
    if p < 1:
        raise ValueError(p)
    infinity = 16 * p * p
    # 32*(p-1)*p^2*(16*p^2-1) is the expanded one-norm majorant before +16p^2.
    expanded = 32 * (p - 1) * p * p * (16 * p * p - 1) + 16 * p * p
    one = 512 * p**5 - 512 * p**4 - 32 * p**3 + 48 * p * p
    if expanded != one or one >= 512 * p**5 or infinity != 16 * p * p:
        raise AssertionError((p, infinity, one, expanded))
    return infinity, one


def main():
    require_source_sentences()
    sharp_upper, sharp_lower = check_dimension()
    ratios = check_product_reading()
    thresholds = check_conditional_constants()
    for p in range(1, 41):
        inverse_majorant(p)
    print("sharp_upper_witness", sharp_upper)
    print("sharp_lower_witness", sharp_lower)
    print("product_exponent_over_p", ratios)
    print("conditional_b0", thresholds)
    print("infinity_norm_p4", inverse_majorant(4)[0])
    print("one_norm_p4", inverse_majorant(4)[1])
    print("PASS_EXPLICIT_4P_DIMENSION")


if __name__ == "__main__":
    main()
