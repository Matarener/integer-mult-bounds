"""Exact finite corroboration; the universal analytic proof is in PROOF.md."""

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def numerator(r: int, h: int) -> list[int]:
    require(2 <= r <= 96 and 1 <= h < r, "kernel domain")
    result = [0] * r
    for a in range(h - 1, r - 1):
        result[a] += 1
    for a in range(r - h - 1, r - 1):
        result[a] += 1
    return result


def check_kernel(r: int, h: int, values: list[int]) -> None:
    require(len(values) == r, "kernel length")
    actual = [0] * (r + 1)
    for a, value in enumerate(values):
        actual[a] += value
        actual[a + 1] -= value
    expected = [0] * (r + 1)
    expected[h - 1] += 1
    expected[r - h - 1] += 1
    expected[r - 1] -= 2
    require(actual == expected, "divided kernel identity")
    require(all(v >= 0 for v in values) and any(values), "positive kernel")


def kernel_checks() -> int:
    count = 0
    for r in range(2, 97):
        total = [0] * r
        for h in range(1, r):
            values = numerator(r, h)
            check_kernel(r, h, values)
            require(values == numerator(r, r - h), "reflection")
            total = [a + b for a, b in zip(total, values, strict=True)]
            count += 1
        require(total == [2 * (a + 1) for a in range(r - 1)] + [0],
                "sum of kernels equals twice S derivative")
    return count


def log_unit(value: F) -> tuple[F, F]:
    require(1 <= value <= 2, "log interval domain")
    z = (value - 1) / (value + 1)
    total, power = F(0), z
    for j in range(48):
        total += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / (97 * (1 - z * z))
    return total, total + tail


def log_integer(r: int) -> tuple[F, F]:
    require(2 <= r <= 4096, "integer log domain")
    k = r.bit_length() - 1
    a, b = log_unit(F(r, 1 << k))
    c, d = log_unit(F(2))
    return a + k * c, b + k * d


def series_checks() -> int:
    count = 0
    for r in range(2, 41):
        lo, hi = log_integer(r)
        for m in (8, 32):
            total = F(0)
            for h in range(1, r):
                for q in range(m):
                    term = (F(1, q * r + h) + F(1, q * r + r - h)
                            - F(2, q * r + r)) / 2
                    require(term > 0, "positive Abel series term")
                    total += term
            harmonic = sum((F(1, j) for j in range(m + 1, m * r + 1)), F(0))
            require(total == harmonic, "harmonic telescoping")
            require(total < lo <= hi < total + F(1, m), "log limit enclosure")
            count += 1
    return count


def fourier_fixture(r: int, diagonal: tuple[F, F]) -> list[tuple[F, F]]:
    """Formal log(2),log(3) coefficients; all cosines are rational here."""
    require(r in (3, 4, 6), "fixture radix")
    zero = (F(0), F(0))
    logs = {
        3: [zero, (F(0), F(1, 2)), (F(0), F(1, 2))],
        4: [zero, (F(1, 2), F(0)), (F(1), F(0)), (F(1, 2), F(0))],
        6: [zero, zero, (F(0), F(1, 2)), (F(1), F(0)),
            (F(0), F(1, 2)), zero],
    }[r]
    cosines = {
        3: [F(1), F(-1, 2), F(-1, 2)],
        4: [F(1), F(0), F(-1), F(0)],
        6: [F(1), F(1, 2), F(-1, 2), F(-1), F(-1, 2), F(1, 2)],
    }[r]
    logs[0] = diagonal
    result = []
    for h in range(r):
        row = tuple(sum((logs[s][a] * cosines[(h * s) % r]
                         for s in range(r)), F(0)) / r for a in range(2))
        result.append(row)
    return result


def check_fixture(r: int, diagonal: tuple[F, F]) -> None:
    rows = fourier_fixture(r, diagonal)
    require(rows[0] == (F(0), F(0)), "zero Fourier mean")
    for a, b in rows[1:]:
        require(a <= 0 and b <= 0 and (a < 0 or b < 0), "negative Fourier mode")
    mass = tuple(-sum((row[a] for row in rows[1:]), F(0)) for a in range(2))
    require(mass == tuple(-v for v in diagonal), "Fourier mass")


def is_prime(n: int) -> bool:
    require(2 <= n <= 512, "prime test domain")
    return all(n % d for d in range(2, n))


def budget(r: int, degree: int) -> tuple[int, int]:
    require(r >= 3 and 1 <= degree < r, "budget domain")
    ell = (r - 1).bit_length()
    old = 1 + 2 * ell + (r - 1) * degree * min(r, 8 * ell * ell)
    new = 1 + 2 * ell + (r - 1) * degree * min(r, 3 * ell * ell)
    return old, new


def budget_checks() -> tuple[int, int]:
    c, d = log_unit(F(2))
    require(F(2, 3) < c <= d < F(3, 4), "log two constants")
    for ell in range(2, 1025):
        require(2 * d * ell * ell + 3 * ell <= 3 * ell * ell,
                "dyadic polynomial envelope")
    cases = set()
    for p in range(2, 513):
        if is_prime(p):
            r = p
            for _ in range(9):
                if r > 512:
                    break
                if r >= 3:
                    cases.add((r, r - r // p))
                r *= p
    cases.update((1 << a, 1 << (a - 1)) for a in range(2, 129))
    improved = 0
    for r, degree in sorted(cases):
        old, new = budget(r, degree)
        require(new <= old, "budget monotonicity")
        improved += new < old
    require(budget(4096, 2048) == (9661317145, 3622993945), "4096 budget")
    return len(cases), improved


def expect_rejection(function, *args) -> None:
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError("control unexpectedly passed")


def controls() -> int:
    count = 0
    for r, h in ((3, 1), (4, 2), (17, 7), (96, 95)):
        wrong = numerator(r, h)
        wrong[h - 1] += 1
        expect_rejection(check_kernel, r, h, wrong)
        count += 1
    for r in (3, 4, 6):
        expect_rejection(check_fixture, r, (F(0), F(0)))
        count += 1
    expect_rejection(numerator, 97, 1)
    expect_rejection(numerator, 4, 0)
    expect_rejection(log_unit, F(3))
    expect_rejection(budget, 3, 3)
    return count + 4


def main() -> None:
    require(len(sys.argv) == 1, "no command-line arguments are accepted")
    kernels = kernel_checks()
    series = series_checks()
    for r, diagonal in ((3, (F(0), F(-1))), (4, (F(-2), F(0))),
                        (6, (F(-1), F(-1)))):
        check_fixture(r, diagonal)
    cases, improved = budget_checks()
    rejected = controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(path.is_file() and path.stat().st_size <= 1_048_576, "package file bound")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print("PASS_ZERO_MEAN_CYCLOTOMIC_HEIGHT", json.dumps({
        "kernel_identities": kernels, "harmonic_checks": series,
        "exact_fourier_fixtures": 3, "budget_cases": cases,
        "strict_budget_improvements": improved, "rejected_controls": rejected,
        "radix4096_old_d": 9661317145, "radix4096_new_d": 3622993945,
        "package_sha256": hashes,
        "scope": "finite exact corroboration; universal proof is PROOF.md",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
