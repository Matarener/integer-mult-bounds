"""Exact finite corroboration of the new complex entropy-defect lemma.

The all-complex result is proved in PROOF.md. No predecessor code is executed.
All logarithm intervals below have rational endpoints and explicit tails.
"""

from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from math import isqrt
from pathlib import Path


Gaussian = tuple[F, F]
Interval = tuple[F, F]
TERMS = 48
ROOT_BITS = 192


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def add(x: Gaussian, y: Gaussian) -> Gaussian:
    return x[0] + y[0], x[1] + y[1]


def mul(x: Gaussian, y: Gaussian) -> Gaussian:
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def conjugate(x: Gaussian) -> Gaussian:
    return x[0], -x[1]


def norm2(x: Gaussian) -> F:
    return x[0] ** 2 + x[1] ** 2


def interval_add(x: Interval, y: Interval) -> Interval:
    return x[0] + y[0], x[1] + y[1]


def interval_scale(c: F, x: Interval) -> Interval:
    a, b = c * x[0], c * x[1]
    return min(a, b), max(a, b)


def log_series(x: F) -> Interval:
    require(1 <= x <= 2, "series argument outside [1,2]")
    z = (x - 1) / (x + 1)
    power, total = z, F(0)
    for j in range(TERMS):
        total += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / ((2 * TERMS + 1) * (1 - z * z))
    return total, total + tail


def log2_interval(x: F) -> Interval:
    require(isinstance(x, F) and x > 0, "log argument must be positive Fraction")
    require(x.numerator.bit_length() <= 256, "log numerator too large")
    require(x.denominator.bit_length() <= 256, "log denominator too large")
    k = x.numerator.bit_length() - x.denominator.bit_length()
    u = x / F(2) ** k
    if u < 1:
        k, u = k - 1, 2 * u
    require(1 <= u < 2, "binary range reduction failed")
    lower, upper = log_series(u)
    base_lower, base_upper = log_series(F(2))
    return k + lower / base_upper, k + upper / base_lower


def root_interval(x: F) -> Interval:
    require(isinstance(x, F) and x >= 0, "root argument must be nonnegative Fraction")
    scale = 1 << ROOT_BITS
    k = isqrt((x.numerator * scale * scale) // x.denominator)
    lower, upper = F(k, scale), F(k + 1, scale)
    require(lower * lower <= x < upper * upper, "root enclosure failed")
    return lower, upper


def entropy(x: Gaussian, cache: dict[F, Interval]) -> tuple[Interval, Interval]:
    n = norm2(x)
    if n == 0:
        return (F(0), F(0)), (F(0), F(0))
    if n not in cache:
        require(len(cache) < 4096, "log cache capacity exceeded")
        cache[n] = log2_interval(n)
    return interval_scale(-x[0] / 2, cache[n]), interval_scale(-x[1] / 2, cache[n])


def defect(p: Gaussian, q: Gaussian, cache: dict[F, Interval]) -> tuple[Interval, Interval]:
    hp, hq, hs = entropy(p, cache), entropy(q, cache), entropy(add(p, q), cache)
    return tuple(
        interval_add(interval_add(hp[j], hq[j]), interval_scale(F(-1), hs[j]))
        for j in range(2)
    )


def squared_upper(z: tuple[Interval, Interval]) -> F:
    return sum(max(abs(a), abs(b)) ** 2 for a, b in z)


def check_scalar(p: Gaussian, q: Gaussian, cache: dict[F, Interval]) -> bool:
    # Equal-input and zero-input cases are exact identities, so interval
    # rounding cannot incorrectly reject equality in the sharp theorem.
    if p == q:
        if norm2(p):
            d = defect(p, q, cache)
            require(all(d[j][0] <= 2 * p[j] <= d[j][1] for j in range(2)), "equality lost")
        return bool(norm2(p))
    if not norm2(p) or not norm2(q):
        d = defect(p, q, cache)
        require(all(a <= 0 <= b for a, b in d), "zero-input identity lost")
        return False
    d = defect(p, q, cache)
    lower = root_interval(norm2(p))[0] + root_interval(norm2(q))[0]
    require(squared_upper(d) < lower * lower, "strict scalar inequality failed")
    return False


def check_mix(case: int, cache: dict[F, Interval]) -> int:
    # Two rows of a forward matrix and its inverse-dual transform.
    # Arbitrary N is allowed: the conservation identity is columnwise.
    c = F(case % 5 - 2), F(case % 7 - 3)
    if not norm2(c):
        c = F(1), F(0)
    checked = 0
    for j in range(3):
        mt = F((case + j) % 5 - 2), F((case + 2 * j) % 3 - 1)
        ms = F((case + 3 * j) % 7 - 3), F((case + j) % 3 - 1)
        nt = F((case + 2 * j) % 5 - 2), F((case + j) % 5 - 2)
        ns = F((case + j) % 7 - 3), F((case + 4 * j) % 3 - 1)
        mt_new = add(mt, mul(c, ms))
        ns_new = add(ns, mul((-c[0], c[1]), nt))
        old = mul(mt, conjugate(nt)), mul(ms, conjugate(ns))
        new = mul(mt_new, conjugate(nt)), mul(ms, conjugate(ns_new))
        require(add(*old) == add(*new), "pair conservation failed")
        for pair in (old, new):
            check_scalar(*pair, cache)
        h = [entropy(z, cache) for z in (*old, *new)]
        delta = tuple(
            interval_add(interval_add(h[2][i], h[3][i]),
                         interval_scale(F(-1), interval_add(h[0][i], h[1][i])))
            for i in range(2)
        )
        limit = sum(root_interval(norm2(z))[0] for z in (*old, *new))
        require(squared_upper(delta) <= limit * limit, "mixing bound failed")
        checked += 1
    return checked


def exact_dyadic(p: Gaussian, q: Gaussian) -> bool:
    # An independent branch uses only exact log2 values of dyadic norms.
    values = []
    for z in (p, q, add(p, q)):
        n = norm2(z)
        require(n.denominator == 1, "dyadic control expects integer inputs")
        k = n.numerator
        if k and k & (k - 1):
            return False
        factor = -F(k.bit_length() - 1, 2) if k else F(0)
        values.append((factor * z[0], factor * z[1]))
    d = add(add(values[0], values[1]), (-values[2][0], -values[2][1]))
    a, b = norm2(p), norm2(q)
    excess = norm2(d) - a - b
    require(excess <= 0 or excess ** 2 <= 4 * a * b, "exact dyadic bound failed")
    equality = excess >= 0 and excess ** 2 == 4 * a * b
    require(equality == (p == q), "exact equality classification failed")
    return True


def controls(cache: dict[F, Interval]) -> int:
    one, zero = (F(1), F(0)), (F(0), F(0))
    d = defect(one, one, cache)
    require(d == ((F(2), F(2)), (F(0), F(0))), "sharp witness not exact")
    require(F(199, 100) ** 2 < squared_upper(d), "subunit-constant control failed")
    require(defect(one, (-one[0], F(0)), cache) == ((F(0), F(0)),) * 2,
            "cancellation control failed")
    require(check_scalar(one, zero, cache) is False, "zero case control failed")
    d = defect(one, (F(0), F(1)), cache)
    require(d[0] == d[1] == (F(1, 2), F(1, 2)), "nonreal defect control failed")
    bad = 0
    for function, argument in ((log2_interval, F(0)), (log2_interval, F(-1)),
                               (log2_interval, 1), (root_interval, F(-1)),
                               (log2_interval, F(1 << 257)), (log_series, F(3))):
        try:
            function(argument)
        except ValueError:
            bad += 1
    require(bad == 6, "invalid input accepted")
    c, ms = (F(0), F(1)), one
    wrong = add(mul(c, ms), mul(ms, conjugate((-c[0], -c[1]))))
    require(norm2(wrong) > 0, "wrong-conjugation control failed")
    return bad + 6


def package_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    result = {}
    for name in names:
        path = root / name
        require(path.is_file() and not path.is_symlink(), "invalid package file")
        require(path.stat().st_size <= 128 * 1024, "package file too large")
        result[name] = sha256(path.read_bytes()).hexdigest()
    return result


def main() -> None:
    cache: dict[F, Interval] = {}
    points = tuple((F(x), F(y)) for x, y in product(range(-3, 4), repeat=2))
    equalities = sum(check_scalar(p, q, cache) for p, q in product(points, repeat=2))
    exact = sum(exact_dyadic(p, q) for p, q in product(points, repeat=2))
    scaled = 0
    for k, phase in product(range(-12, 13), range(4)):
        unit = ((F(1), F(0)), (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1)))[phase]
        a = F(2) ** k
        p, q = mul((a, a / 3), unit), mul((a / 5, -a / 7), unit)
        check_scalar(p, q, cache)
        scaled += 1
    mixed = sum(check_mix(case, cache) for case in range(64))
    rejected = controls(cache)
    require(F(3, 2) / F(8, 3) == F(9, 16) < F(2, 3), "proof constants failed")
    require(log_series(F(2))[0] > F(2, 3), "log lower bound failed")
    print(json.dumps({"scalar_pairs": len(points) ** 2, "nonzero_equalities": equalities,
                      "exact_dyadic_pairs": exact, "scaled_pairs": scaled,
                      "mix_columns": mixed, "controls": rejected,
                      "log_intervals": len(cache), "package_sha256": package_hashes()}, sort_keys=True))
    print("PASS_SHARP_COMPLEX_ENTROPY_DEFECT scalar_constant=1 update_coefficient=4")


if __name__ == "__main__":
    main()
