"""Exact arithmetic corroboration of the new coefficient valuation theorem."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb, lcm
from pathlib import Path
from typing import TypeVar


N = TypeVar("N", int, Fraction)
GI = tuple[int, int]
PI = (2, 1)
BAR = (2, -1)
MAX_WIDTH = 32


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def add(x: tuple[N, N], y: tuple[N, N]) -> tuple[N, N]:
    return x[0] + y[0], x[1] + y[1]


def mul(x: tuple[N, N], y: tuple[N, N]) -> tuple[N, N]:
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def power(x: GI, exponent: int) -> GI:
    require(0 <= exponent <= 1024, "power capacity")
    result = (1, 0)
    for _ in range(exponent):
        result = mul(result, x)
    return result


def valuation(x: GI, prime: GI) -> int:
    require(x != (0, 0), "valuation of zero")
    require(prime in (PI, BAR), "unsupported prime")
    bound = (x[0] * x[0] + x[1] * x[1]).bit_length() + 1
    for count in range(bound):
        numerator = mul(x, (prime[0], -prime[1]))
        if numerator[0] % 5 or numerator[1] % 5:
            return count
        x = numerator[0] // 5, numerator[1] // 5
    raise ValueError("valuation capacity exhausted")


def integer_polynomial(f: int) -> list[GI]:
    require(1 <= f <= MAX_WIDTH, "width capacity")
    result = [(1, 0)]
    for k in range(f + 1):
        constant = power(PI, k)
        leading = power(BAR, k)
        nxt = [(0, 0)] * (len(result) + 1)
        for j, coefficient in enumerate(result):
            nxt[j] = add(nxt[j], mul(coefficient, (-constant[0], -constant[1])))
            nxt[j + 1] = add(nxt[j + 1], mul(coefficient, leading))
        result = nxt
    return result


def rational_polynomial(f: int) -> list[tuple[Fraction, Fraction]]:
    require(1 <= f <= MAX_WIDTH, "width capacity")
    result = [(Fraction(1), Fraction(0))]
    root = (Fraction(1), Fraction(0))
    alpha = (Fraction(3, 5), Fraction(4, 5))
    for _ in range(f + 1):
        nxt = [(Fraction(0), Fraction(0))] * (len(result) + 1)
        for j, coefficient in enumerate(result):
            nxt[j] = add(nxt[j], mul(coefficient, (-root[0], -root[1])))
            nxt[j + 1] = add(nxt[j + 1], coefficient)
        result = nxt
        root = mul(root, alpha)
    return result


def validate_profile(coefficients: list[GI], f: int) -> int:
    require(1 <= f <= MAX_WIDTH, "width capacity")
    require(len(coefficients) == f + 2, "wrong coefficient count")
    total = 0
    for j, coefficient in enumerate(coefficients):
        a, b = comb(f + 1 - j, 2), comb(j, 2)
        require(valuation(coefficient, PI) == a, "wrong pi valuation")
        require(valuation(coefficient, BAR) == b, "wrong conjugate valuation")
        norm = coefficient[0] ** 2 + coefficient[1] ** 2
        require(norm >= 5 ** (a + b), "coefficient height lower bound")
        total += a + b
    require(total == f * (f + 1) * (f + 2) // 3, "wrong total valuation")
    return total


def check_coefficients(f: int) -> dict[str, int]:
    integer = integer_polynomial(f)
    rational = rational_polynomial(f)
    s = f * (f + 1) // 2
    scale = power(BAR, s)
    total = validate_profile(integer, f)
    denominators = 0
    for j, (d, c) in enumerate(zip(integer, rational, strict=True)):
        require(mul(c, scale) == d, "independent polynomial mismatch")
        e = s - comb(j, 2)
        denominator = lcm(c[0].denominator, c[1].denominator)
        require(denominator == 5**e, "integer denominator mismatch")
        scaled = mul(c, power(BAR, e))
        require(all(x.denominator == 1 for x in scaled), "Gaussian denominator")
        integral = int(scaled[0]), int(scaled[1])
        require(valuation(integral, BAR) == 0, "denominator is not minimal")
        norm = d[0] ** 2 + d[1] ** 2
        require(norm <= comb(f + 1, j) ** 2 * 5**s, "height upper bound")
        denominators += e
    require(denominators == total, "denominator sum mismatch")
    require(integer[-1] == scale, "leading coefficient mismatch")
    sign = (-1) ** (f + 1)
    constant = power(PI, s)
    require(integer[0] == (sign * constant[0], sign * constant[1]), "constant mismatch")
    return {"coefficients": len(integer), "valuation_sum": total}


def check_subset_oracle() -> int:
    checked = 0
    for f in range(1, 9):
        coefficients = rational_polynomial(f)
        roots = [(Fraction(1), Fraction(0))]
        for _ in range(f):
            roots.append(mul(roots[-1], (Fraction(3, 5), Fraction(4, 5))))
        for size in range(f + 2):
            value = (Fraction(0), Fraction(0))
            for subset in combinations(range(f + 1), size):
                product = (Fraction((-1) ** size), Fraction(0))
                for index in subset:
                    product = mul(product, roots[index])
                value = add(value, product)
                checked += 1
            require(value == coefficients[f + 1 - size], "subset oracle mismatch")
    return checked


def expect_rejection(coefficients: list[GI], f: int) -> None:
    try:
        validate_profile(coefficients, f)
    except ValueError:
        return
    raise ValueError("corrupted coefficient profile accepted")


def check_controls() -> int:
    count = 0
    for f in range(1, 9):
        good = integer_polynomial(f)
        bad = list(good)
        bad[0] = add(bad[0], (1, 0))
        expect_rejection(bad, f)
        expect_rejection([mul(c, PI) for c in good], f)
        expect_rejection([(c[0], -c[1]) for c in good], f)
        expect_rejection(good[:-1], f)
        bad = list(good)
        bad[f // 2] = (0, 0)
        expect_rejection(bad, f)
        count += 5
    for f in (0, MAX_WIDTH + 1):
        expect_rejection([], f)
        count += 1
    return count


def check_sources(package: Path) -> dict[str, str]:
    manifest = json.loads((package / "SOURCES.json").read_text())
    rows = manifest["files"]
    require(isinstance(rows, list) and len(rows) == 4, "source manifest capacity")
    hashes = {}
    root = package.parent.parent
    for row in rows:
        if row["usage"] == "input":
            digest = sha256((root / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source drift: " + row["path"])
            hashes[row["path"]] = digest
    require(len(hashes) == 2, "source manifest coverage")
    return hashes


def main() -> None:
    package = Path(__file__).resolve().parent
    sources = check_sources(package)
    counts = {"widths": MAX_WIDTH, "coefficients": 0, "valuation_sum": 0}
    for f in range(1, MAX_WIDTH + 1):
        for key, value in check_coefficients(f).items():
            counts[key] += value
    counts["subset_terms"] = check_subset_oracle()
    counts["rejection_controls"] = check_controls()
    files = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    receipt = {
        "status": "PASS_TENSOR_ANNIHILATOR_HEIGHT",
        "counts": counts,
        "sources": sources,
        "package_sha256": {name: sha256((package / name).read_bytes()).hexdigest()
                           for name in files},
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
