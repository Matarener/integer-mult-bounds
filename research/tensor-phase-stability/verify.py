#!/usr/bin/env python3
"""Exact finite corroboration for the written tensor phase theorem."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def cmul(z, w):
    return (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])


def conjugate(z):
    return (z[0], -z[1])


def chord2(z):
    return (z[0] - 1) ** 2 + z[1] ** 2


def phase(t, high=False):
    denominator = 1 + t * t
    x = (1 - t * t) / denominator
    return (-x if high else x, 2 * t / denominator)


def scalar_data(z):
    need(z[0] ** 2 + z[1] ** 2 == 1, "unit-circle input")
    square = cmul(z, z)
    cube = cmul(square, z)
    return chord2(z), chord2(square), chord2(cube)


def low_branch(squared_tolerance):
    # The smaller root of s^2-5s+5 is (5-sqrt(5))/2.
    s = squared_tolerance
    return s < F(5, 2) and s * s - 5 * s + 5 > 0


def residual(t, low):
    return t * (3 - t) ** 2 if low else t * (t - 3) ** 2


def enclosure(squared_tolerance, bits=88):
    need(isinstance(squared_tolerance, F), "exact rational tolerance required")
    need(0 <= squared_tolerance <= 4, "squared tolerance outside [0,4]")
    need(type(bits) is int and 16 <= bits <= 128, "bisection bound")
    low = low_branch(squared_tolerance)
    left, right = (F(0), F(1)) if low else (F(3), F(4))
    for _ in range(bits):
        middle = (left + right) / 2
        if residual(middle, low) <= squared_tolerance:
            left = middle
        else:
            right = middle
    check_enclosure(squared_tolerance, low, left, right, bits)
    return low, left, right


def check_enclosure(s, low, left, right, bits):
    need(low is low_branch(s), "wrong phase branch")
    need((0 <= left <= right <= 1) if low else (3 <= left <= right <= 4),
         "wrong root domain")
    need(right - left <= F(1, 2**bits), "root enclosure too wide")
    need(residual(left, low) <= s <= residual(right, low), "false root bracket")


def near_attainment(s, low):
    if s == 0:
        return (F(1), F(0))
    if s == 4:
        return (F(-1), F(0))
    left, right = F(0), F(1, 2) if low else F(1, 3)
    for _ in range(96):
        middle = (left + right) / 2
        _, _, defect3 = scalar_data(phase(middle, high=not low))
        if (defect3 <= s) is low:
            left = middle
        else:
            right = middle
    return phase(left if low else right, high=not low)


def rational_phases():
    values = {phase(F(a, b)) for a in range(-24, 25) for b in range(1, 25)}
    values.add((F(-1), F(0)))
    return sorted(values)


def circle_checks():
    rows = []
    for z in rational_phases():
        t, defect2, defect3 = scalar_data(z)
        need(defect2 == t * (4 - t), "literal tensor-square polynomial")
        need(defect3 == t * (3 - t) ** 2, "literal tensor-cube polynomial")
        s = max(defect2, defect3)
        low, left, right = enclosure(s)
        need(t <= right, "phase violates the proposed envelope")
        need((t <= 1) if low else (t <= 4), "phase branch separation")
        rows.append([str(z[0]), str(z[1]), str(s), str(left), str(right)])
    return rows


def attainment_checks():
    rows = []
    for numerator in range(33):
        epsilon = F(numerator, 16)
        s = epsilon * epsilon
        low, left, right = enclosure(s)
        z = near_attainment(s, low)
        t, defect2, defect3 = scalar_data(z)
        need(max(defect2, defect3) <= s, "infeasible attaining approximation")
        need(left - F(1, 2**75) <= t <= right, "attainment gap")
        rows.append([str(epsilon), "low" if low else "high", str(t)])
    return rows


def qmul(a, b):
    # Exact Q(sqrt(5)); pairs encode a0+a1*sqrt(5).
    return (a[0] * b[0] + 5 * a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def qadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def qscale(a, coefficient):
    return (a[0] * coefficient, a[1] * coefficient)


def threshold_checks():
    one, zero = (F(1), F(0)), (F(0), F(0))
    x = (F(-1, 4), F(-1, 4))  # cos(4*pi/5)
    x2 = qmul(x, x)
    x3 = qmul(x2, x)
    t = qadd(qscale(one, 2), qscale(x, -2))
    e2 = qadd(qscale(one, 4), qscale(x2, -4))
    e3 = qadd(qadd(qscale(one, 2), qscale(x3, -8)), qscale(x, 6))
    need(e2 == e3 == (F(5, 2), F(-1, 2)), "exact fifth-root threshold")
    need(t == (F(5, 2), F(1, 2)), "exact jump witness")
    polynomial = qadd(qadd(qmul(e2, e2), qscale(e2, -5)), qscale(one, 5))
    need(polynomial == zero, "threshold quadratic")
    x5 = qmul(qmul(x3, x), x)
    need(qadd(qadd(qscale(x5, 16), qscale(x3, -20)), qscale(x, 5)) == one,
         "literal fifth-root phase")
    difference = qadd(t, qscale(one, -3))
    need(qmul(t, qmul(difference, difference)) == e2, "large cubic endpoint")
    return {"epsilon_squared": ["5/2", "-1/2"],
            "error_squared": ["5/2", "1/2"], "field": "Q(sqrt(5))"}


def sum_complex(values):
    result = (F(0), F(0))
    for value in values:
        result = (result[0] + value[0], result[1] + value[1])
    return result


def matrix_product(a, b):
    return [[sum_complex(cmul(x, y) for x, y in zip(row, col))
             for col in zip(*b)] for row in a]


def adjoint(a):
    return [[conjugate(z) for z in col] for col in zip(*a)]


def tensor(a, b):
    return [[cmul(a[i][j], b[k][ell])
             for j in range(len(a[0])) for ell in range(len(b[0]))]
            for i in range(len(a)) for k in range(len(b))]


def tensor_power(a, width):
    need(1 <= width <= 3 and len(a) == len(a[0]) == 2, "bounded tensor fixture")
    result = [[(F(1), F(0))]]
    for _ in range(width):
        result = tensor(result, a)
    return result


def matrix_checks():
    zero = (F(0), F(0))
    b = [[(F(3, 5), F(0)), (F(0), F(4, 5))],
         [(F(0), F(4, 5)), (F(3, 5), F(0))]]
    phases = [(F(1), F(0)), (F(-1), F(0)), phase(F(1, 4)), phase(F(3))]
    cases = 0
    for z, w in product(phases, repeat=2):
        diagonal = [[z, zero], [zero, w]]
        a = matrix_product(b, diagonal)
        defect = F(0)
        for width in (2, 3):
            aw, bw = tensor_power(a, width), tensor_power(b, width)
            dw = tensor_power(diagonal, width)
            need(matrix_product(adjoint(bw), aw) == dw, "dense unitary reduction")
            size = len(dw)
            difference = [[(aw[i][j][0] - bw[i][j][0],
                            aw[i][j][1] - bw[i][j][1])
                           for j in range(size)] for i in range(size)]
            gram = matrix_product(adjoint(difference), difference)
            for i, row in enumerate(gram):
                for j, entry in enumerate(row):
                    need(entry == ((chord2(dw[i][i]), F(0)) if i == j else zero),
                         "literal defect Gram matrix")
            defect = max(defect, *(gram[i][i][0] for i in range(size)))
        _, _, upper = enclosure(defect)
        need(max(chord2(z), chord2(w)) <= upper, "matrix envelope")
        cases += 1
    return cases


def rejection_checks():
    failures = 0
    for value, bits in [(F(-1), 88), (F(5), 88), (F(1), 15),
                        (F(1), 129), (1, 88)]:
        try:
            enclosure(value, bits)
        except ValueError:
            failures += 1
        else:
            raise ValueError("invalid input accepted")
    low, left, right = enclosure(F(1))
    for values, message in [((not low, left, right), "wrong phase branch"),
                            ((low, left + 1, right + 1), "wrong root domain"),
                            ((low, F(0), F(1)), "root enclosure too wide"),
                            ((low, F(0), F(1, 2**88)), "false root bracket")]:
        try:
            check_enclosure(F(1), *values, 88)
        except ValueError as error:
            need(str(error) == message, "wrong rejection guard exercised")
            failures += 1
        else:
            raise ValueError("forged certificate accepted")
    t, square, cube = scalar_data((F(-1), F(0)))
    need(t == 4 and square == 0 and cube == 4, "width-two-only phase control")
    need(enclosure(F(9, 4))[0] is False, "large-error branch control")
    return failures + 2


def run_checks():
    circles = circle_checks()
    attainments = attainment_checks()
    threshold = threshold_checks()
    matrix_cases = matrix_checks()
    controls = rejection_checks()
    encoded = json.dumps([circles, attainments], separators=(",", ":")).encode()
    return {"rational_phases": len(circles), "near_attainments": len(attainments),
            "dense_unitary_pairs": matrix_cases, "controls": controls,
            "threshold": threshold, "enumeration_sha256": sha256(encoded).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a fresh hash-bound receipt")
    args = parser.parse_args()
    result = run_checks()
    package = Path(__file__).resolve().parent
    names = ["PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"]
    result["files"] = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(json.loads((package / "RESULT.json").read_text()) == result, "receipt differs")
    print("PASS_TENSOR_PHASE_STABILITY", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
