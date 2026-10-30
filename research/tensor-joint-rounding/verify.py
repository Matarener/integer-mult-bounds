#!/usr/bin/env python3
"""Exact finite corroboration for correlated Tensor tail truncations."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import gcd, trunc
from pathlib import Path
import json


PACKAGE = Path(__file__).resolve().parent
SOURCE = PACKAGE.parent / "tensor-expansion-accuracy" / "PROOF.md"
SOURCE_HASH = "659fe79662c5cfab5fd22cc937e88b849c1491bf4a66e79ee1a7558aeb090e0d"
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def file_hash(path):
    require(path.is_file() and path.stat().st_size <= 65536, "missing or oversized input")
    return sha256(path.read_bytes()).hexdigest()


def toward_zero(value, shift):
    require(type(value) is int, "integer numerator required")
    require(type(shift) is int and 0 <= shift <= 32, "shift outside finite replay")
    magnitude = abs(value) >> shift
    return -magnitude if value < 0 else magnitude


def tail_radius(coefficient, shift):
    require(type(coefficient) is int and coefficient > 0, "positive coefficient required")
    require(type(shift) is int and 0 <= shift <= 32, "invalid tail shift")
    denominator = 1 << shift
    return Fraction(denominator - gcd(coefficient, denominator), denominator)


def check_composition():
    count = 0
    for first, second, value in product(range(8), range(8), range(-2048, 2049)):
        actual = toward_zero(toward_zero(value, first), second)
        reference = trunc(Fraction(value, 1 << (first + second)))
        require(actual == reference, "signed truncation composition")
        count += 1
    return count


def check_tail_sharpness():
    systems = cases = 0
    for precision in range(2, 8):
        quantum = 1 << precision
        for extraction in range(min(4, precision - 1) + 1):
            denominator = 1 << (precision + extraction)
            for coefficient in range(1, quantum // 4 + 1):
                radius = tail_radius(coefficient, precision + extraction)
                period = denominator // gcd(coefficient, denominator)
                maximum = Fraction(0)
                for value in range(-period, period + 1):
                    output = toward_zero(toward_zero(coefficient * value, precision), extraction)
                    residual = abs(output - Fraction(coefficient * value, denominator))
                    require(residual <= radius, "joint tail radius")
                    maximum = max(maximum, residual)
                    cases += 1
                require(maximum == radius, "sharp tail maximum not attained")
                systems += 1
    return systems, cases


def execute_row(p, precision, scale, a, k, b, c, values):
    quantum = 1 << precision
    extraction = precision - p - 2 * scale
    weighted = tuple(toward_zero(x * (1 << (precision - p)) * v, precision)
                     for x, v in zip(a, values, strict=True))
    summed = sum(x * w for x, w in zip(k, weighted, strict=True))
    convolved = toward_zero(summed, precision)
    post_b = toward_zero(b * convolved, precision)
    normalized = toward_zero(c * post_b, precision)
    output = toward_zero(normalized, extraction)
    rho1 = tuple(w - Fraction(x * v, 1 << p)
                 for w, x, v in zip(weighted, a, values, strict=True))
    rho2 = convolved - Fraction(summed, quantum)
    rho3 = post_b - Fraction(b * convolved, quantum)
    tail = output - Fraction(c * post_b, 1 << (precision + extraction))
    return output, rho1, rho2, rho3, tail


def check_row(p, precision, scale, a, k, b, c, values):
    quantum = 1 << precision
    h = Fraction(1, 1 << p)
    multiplier = 1 << (2 * scale)
    work_unit = Fraction(multiplier, quantum)
    ca = Fraction(c, quantum)
    ba = Fraction(b, quantum)
    ka = tuple(Fraction(x, quantum) for x in k)
    output, rho1, rho2, rho3, tail = execute_row(p, precision, scale, a, k, b, c, values)
    ideal = Fraction(multiplier * c * b, quantum ** 4) * sum(
        Fraction(x * y * v, 1 << p) for x, y, v in zip(a, k, values, strict=True))
    terms = (work_unit * ca * ba * sum(x * r for x, r in zip(ka, rho1, strict=True)),
             work_unit * ca * ba * rho2, work_unit * ca * rho3, h * tail)
    defect = output * h - ideal
    require(defect == sum(terms), "joint four-residual identity")
    extraction = precision - p - 2 * scale
    radius = tail_radius(c, precision + extraction)
    coefficient_bound = h * radius + work_unit * (ca * ba * sum(ka) + ca * ba + ca)
    uniform_bound = h + work_unit * Fraction(len(a) + 2, 4)
    require(abs(defect) < coefficient_bound, "coefficient-sensitive scalar bound")
    require(coefficient_bound < uniform_bound, "strict improvement to uniform bound")
    reference = tuple(trunc(Fraction(x * v, 1 << p)) for x, v in zip(a, values, strict=True))
    reference_y = trunc(sum(Fraction(x * w, quantum) for x, w in zip(k, reference, strict=True)))
    reference_z = trunc(Fraction(b * reference_y, quantum))
    reference_o = trunc(Fraction(c * reference_z, 1 << (precision + extraction)))
    require(output == reference_o, "independent Fraction row arithmetic")
    return tuple(term != 0 for term in terms), defect


def check_rows():
    cases = cancellations = zero_shifts = 0
    transported = [False] * 4
    configurations = ((1, 2, 0), (1, 3, 1), (2, 3, 0), (1, 4, 1), (2, 4, 1))
    for p, precision, scale in configurations:
        quantum = 1 << precision
        factors = (0, 1, quantum // 2, quantum - 1, quantum)
        normalizers = tuple(sorted({1, quantum // 4}))
        inputs = tuple(sorted({-(1 << p), -1, 0, 1, 1 << p}))
        for width in (1, 2):
            a_rows = tuple(product((1, quantum // 2, quantum), repeat=width))
            k_rows = tuple(product((0, 1, quantum - 1, quantum), repeat=width))
            value_rows = tuple(product(inputs, repeat=width))
            for a, k, b, c, values in product(a_rows, k_rows, factors, normalizers, value_rows):
                flags, defect = check_row(p, precision, scale, a, k, b, c, values)
                transported = [old or new for old, new in zip(transported, flags, strict=True)]
                if sum(values) == 0 and any(values):
                    cancellations += 1
                zero_shifts += precision == p + 2 * scale
                require(isinstance(defect, Fraction), "exact arithmetic required")
                cases += 1
    require(all(transported), "missing omission control for a transported residual")
    require(cancellations > 0 and zero_shifts > 0, "missing boundary cases")
    return cases, cancellations, zero_shifts


def check_complex_rows():
    cases = 0
    p, precision, scale = 2, 4, 1
    quantum = 1 << precision
    components = tuple(product(range(-4, 5), repeat=2))
    disk = tuple(z for z in components if z[0] ** 2 + z[1] ** 2 <= 16)
    for left, right, b, c in product(disk, disk, (1, 7, 16), (1, 4)):
        a, k = (7, 15), (13, 16)
        _, real = check_row(p, precision, scale, a, k, b, c, (left[0], right[0]))
        _, imag = check_row(p, precision, scale, a, k, b, c, (left[1], right[1]))
        scalar_bound = Fraction(1, 1 << p) + Fraction(1 << (2 * scale), quantum)
        require(real * real + imag * imag < 2 * scalar_bound ** 2, "complex squared bound")
        cases += 1
    return cases


def check_controls():
    rejected = 0
    for value, shift in ((True, 1), (1.5, 1), (1, -1), (1, 33), (1, True)):
        try:
            toward_zero(value, shift)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid truncation input accepted")
    for coefficient, shift in ((0, 1), (-1, 1), (True, 1), (1, -1), (1, 33)):
        try:
            tail_radius(coefficient, shift)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid tail input accepted")
    require(toward_zero(-1, 2) == 0 and (-1 // 4) == -1, "signed floor control")
    require(toward_zero(4, 2) - toward_zero(3, 2) > Fraction(1, 4), "nonexpansive control")
    require(toward_zero(toward_zero(1, 2), 0) - Fraction(1, 4) == -Fraction(1, 4),
            "zero extraction shift does not remove normalization residual")
    require(tail_radius(4, 4) == Fraction(3, 4), "coefficient gcd control")
    return rejected + 8  # Four arithmetic controls and four transported-term omissions.


def check_guard_example():
    epsilon = Fraction(1, 2)
    new_guards = tuple(g for g in range(6) if Fraction(3, 4 * (1 << g)) <= epsilon)
    old_guards = tuple(g for g in range(6) if Fraction(7, 4 * (1 << g)) <= epsilon)
    require(min(new_guards) == 1 and min(old_guards) == 2, "one-bit sufficient-guard improvement")
    return {"n": 1, "epsilon": "1/2", "new_sufficient_guard": 1, "old_sufficient_guard": 2}


def main():
    require(file_hash(SOURCE) == SOURCE_HASH, "predecessor proof drift")
    composition = check_composition()
    systems, tails = check_tail_sharpness()
    rows, cancellations, zero_shifts = check_rows()
    complex_rows = check_complex_rows()
    controls = check_controls()
    result = {"composition_cases": composition, "tail_systems": systems, "tail_cases": tails,
              "scalar_rows": rows, "cancellation_rows": cancellations, "zero_extraction_rows": zero_shifts,
              "complex_rows": complex_rows, "controls": controls, "guard_example": check_guard_example()}
    hashes = {name: file_hash(PACKAGE / name) for name in PACKAGE_FILES}
    print("PASS_TENSOR_JOINT_ROUNDING")
    print(json.dumps({"result": result, "package_sha256": hashes, "source_sha256": SOURCE_HASH}, sort_keys=True))


if __name__ == "__main__":
    main()
