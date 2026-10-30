"""Corroborate the commuting-repair obstruction; no predecessor replay.

The unbounded result is proved in PROOF.md. All executable domains below
are fixed and finite. This program writes only deterministic stdout.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import isqrt
from pathlib import Path
import json


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dyadic(value: Fraction) -> bool:
    denominator = value.denominator
    return denominator & (denominator - 1) == 0


def unit(value: int | Fraction) -> bool:
    value = Fraction(value)
    numerator = abs(value.numerator)
    return dyadic(value) and numerator > 0 and numerator & (numerator - 1) == 0


def square(value: Fraction) -> bool:
    return value >= 0 and (
        isqrt(value.numerator) ** 2 == value.numerator
        and isqrt(value.denominator) ** 2 == value.denominator
    )


def obstruction(factors: tuple) -> tuple[int, int]:
    """Return total degree and bad-factor degree for a factored polynomial.

    Coefficients are in increasing order. Only irreducible monic degree-one
    and degree-two factors are accepted. This is a degree certificate, not
    a routine to recognize a matrix or establish its characteristic factors.
    """
    need(1 <= len(factors) <= 8, "factor count")
    total = bad = 0
    seen = set()
    for coefficients, multiplicity in factors:
        need(2 <= len(coefficients) <= 3, "factor degree")
        need(type(multiplicity) is int and 1 <= multiplicity <= 40000,
             "multiplicity")
        coefficients = tuple(Fraction(x) for x in coefficients)
        need(all(dyadic(x) for x in coefficients), "dyadic coefficients")
        need(all(x.numerator.bit_length() <= 128
                 and x.denominator.bit_length() <= 128 for x in coefficients),
             "coefficient size")
        need(coefficients[-1] == 1, "monic factor")
        need(coefficients not in seen, "distinct factors")
        seen.add(coefficients)
        if len(coefficients) == 3:
            constant, linear, _ = coefficients
            need(not square(linear * linear - 4 * constant),
                 "irreducible quadratic required")
        degree = len(coefficients) - 1
        total += degree * multiplicity
        if not unit(coefficients[0]):
            bad += degree * multiplicity
    need(total <= 100000, "total dimension")
    return total, bad


def det2(matrix: tuple) -> int | Fraction:
    a, b, c, d = matrix
    return a * d - b * c


def rank2(matrix: tuple) -> int:
    return 2 if det2(matrix) else int(any(matrix))


def mul2(left: tuple, right: tuple) -> tuple:
    a, b, c, d = left
    e, f, g, h = right
    return (a * e + b * g, a * f + b * h,
            c * e + d * g, c * f + d * h)


def add2(left: tuple, right: tuple) -> tuple:
    return tuple(a + b for a, b in zip(left, right, strict=True))


def good_degree2(matrix: tuple) -> int:
    """Classify its monic quadratic over Q using trace and determinant."""
    trace = matrix[0] + matrix[3]
    determinant = det2(matrix)
    discriminant = trace * trace - 4 * determinant
    if discriminant < 0 or isqrt(discriminant) ** 2 != discriminant:
        return 2 if unit(determinant) else 0
    root = isqrt(discriminant)
    need((trace + root) % 2 == 0, "integral rational root")
    return int(unit((trace + root) // 2)) + int(unit((trace - root) // 2))


def exhaustive_pairs() -> dict:
    matrices = tuple(product(range(-2, 3), repeat=4))
    need(len(matrices) == 625, "complete matrix box")
    commuting = accepted = sharp = 0
    ranks = [0, 0, 0]
    for original in matrices:
        floor = 2 - good_degree2(original)
        for repair in matrices:
            if mul2(original, repair) != mul2(repair, original):
                continue
            commuting += 1
            if not unit(det2(add2(original, repair))):
                continue
            accepted += 1
            observed = rank2(repair)
            need(observed >= floor, "commuting rank obstruction")
            ranks[observed] += 1
            sharp += int(observed == floor)
    need(accepted > 0 and sharp > 0, "nonempty positive domain")
    return {"pairs": len(matrices) ** 2, "commuting": commuting,
            "accepted": accepted, "sharp": sharp, "accepted_ranks": ranks}


def changed_basis_cases() -> int:
    """Literal dyadic conjugations of independent small repaired matrices."""
    values = tuple(Fraction(x, 2) for x in range(-4, 5))
    originals = ((1, 0, 0, -38), (-44, 0, 0, 1),
                 (0, 5888, 1, 188), (3, 0, 0, 5))
    checked = 0
    identity = (1, 0, 0, 1)
    for original in originals:
        expected = 2 - good_degree2(original)
        repair = tuple(a - b for a, b in zip(identity, original, strict=True))
        need(rank2(repair) == expected, "attaining algebraic correction")
        for value in values:
            basis = (1, value, 0, 1)
            inverse = (1, -value, 0, 1)
            c = mul2(mul2(basis, original), inverse)
            b = mul2(mul2(basis, repair), inverse)
            need(all(dyadic(Fraction(x)) for x in c + b), "dyadic conjugate")
            need(mul2(c, b) == mul2(b, c), "conjugated commutation")
            need(add2(c, b) == identity and rank2(b) == expected,
                 "literal attaining endpoint and rank")
            checked += 1
    return checked


def hypothesis_controls() -> dict:
    original = (3, 0, 0, 5)
    repair = (2, 4, -4, -8)
    need(rank2(repair) == 1 and det2(add2(original, repair)) == 1,
         "rank-one unrestricted unit repair")
    need(mul2(original, repair) != mul2(repair, original),
         "unrestricted witness must break commutation")
    rational = (Fraction(-14, 5), 0, 0, 0)
    need(rank2(rational) == 1 and det2(add2(original, rational)) == 1,
         "rational determinant-one control")
    need(not dyadic(rational[0]), "odd denominator must be excluded")
    need(mul2(original, rational) == mul2(rational, original),
         "rational control really commutes")
    need(det2(original) != 0 and not unit(det2(original)),
         "rational invertibility is insufficient")
    need(det2((3, 1, -1, 0)) == 1,
         "an auxiliary direction changes the interface")
    factors = (((-1, 1), 30144), ((38, 1), 224),
               ((44, 1), 560), ((-5888, -188, 1), 16))
    need(obstruction(factors) == (30960, 816), "new H6 application")
    need(816 - 560 == 256, "gap from cited unrestricted rank")
    mutants = (
        (((-1, 1), 30144), ((38, 1), 224), ((44, 1), 560)),
        (((-1, 1), 30144), ((2, 1), 224), ((44, 1), 560),
         ((-5888, -188, 1), 16)),
        (((-1, 1), 30144), ((38, 1), 224), ((4, 1), 560),
         ((-5888, -188, 1), 16)),
    )
    for mutant in mutants:
        need(obstruction(mutant) != (30960, 816), "damaged factor control")
    return {"noncommuting_rank_one": list(repair),
            "repaired_determinant": 1, "factor_mutations": len(mutants),
            "hypothesis_controls": 4}


def rejection_controls() -> int:
    invalid = ((), (((1, 2), 1),), (((1, 0, 1), 0),),
               (((Fraction(1, 3), 1), 1),), (((1, 1), 40001),),
               (((0, 1, 1), 1),), (((1, 1), 1), ((1, 1), 1)),
               (((1 << 128, 1), 1),),
               tuple(((x, 1), 1) for x in range(9)),
               (((0, 1), 40000), ((3, 1), 40000), ((5, 1), 40000)))
    for factors in invalid:
        try:
            obstruction(factors)
        except ValueError:
            continue
        raise ValueError("invalid factor certificate accepted")
    need(obstruction((((1, 0, 1), 40000), ((-1, 1), 20000)))
         == (100000, 0), "dimension boundary")
    need(obstruction((((1 << 127, 1), 1),)) == (1, 0),
         "coefficient-size boundary")
    return len(invalid)


def main() -> None:
    result = {"claim_type": "scoped written proof with finite corroboration",
              "h6_commuting_rank": 816, "cited_unrestricted_rank": 560,
              "pairs": exhaustive_pairs(),
              "dyadic_basis_cases": changed_basis_cases(),
              "controls": hypothesis_controls(),
              "invalid_certificates_rejected": rejection_controls()}
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    result["sha256"] = {name: sha256((root / name).read_bytes()).hexdigest()
                        for name in names}
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_H6_COMMUTING_REPAIR rank=816 no_new_kappa")


if __name__ == "__main__":
    main()
