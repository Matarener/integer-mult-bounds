"""Exact finite corroboration of the new shear construction. Apache-2.0."""

import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def label(parameter, side):
    require(type(parameter) in (int, Q), "parameter must be rational")
    require(side in (0, 1), "side must be zero or one")
    x = Q(parameter)
    if side == 0:
        return ((x, x * x), (Q(1), x))
    return ((x, x * x), (Q(0), -x))


def family(parameters, side):
    require(1 <= len(parameters) <= 64, "family size outside 1..64")
    require(len(set(parameters)) == len(parameters), "repeated parameter")
    return tuple(label(x, side) for x in parameters)


def difference(a, b):
    size = len(a)
    return tuple(tuple(a[i][j] - b[i][j] for j in range(size))
                 for i in range(size))


def determinant2(a):
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]


def rank(a):
    """Independent rational row elimination, on matrices of order at most four."""
    size = len(a)
    require(1 <= size <= 4 and all(len(row) == size for row in a),
            "rank expects a square matrix of order at most four")
    work = [[Q(x) for x in row] for row in a]
    pivot = 0
    for column in range(size):
        selected = next((i for i in range(pivot, size) if work[i][column]), None)
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        for i in range(pivot + 1, size):
            factor = work[i][column] / work[pivot][column]
            for j in range(column, size):
                work[i][j] -= factor * work[pivot][j]
        pivot += 1
    return pivot


def shear(a):
    return tuple(tuple(Q(i == j) if j < 2 or i >= 2 else a[i][j - 2]
                       for j in range(4)) for i in range(4))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(4))
                       for j in range(4)) for i in range(4))


def check_family(left, right):
    matrices = left + right
    sides = (0,) * len(left) + (1,) * len(right)
    pairs = 0
    for i, a in enumerate(matrices):
        for j, b in enumerate(matrices):
            delta = difference(a, b)
            expected = 0 if i == j else 1 if sides[i] != sides[j] else 2
            by_determinant = 2 if determinant2(delta) else int(any(map(any, delta)))
            require(by_determinant == expected, "wrong label distance")
            require(rank(delta) == expected, "elimination disagrees")
            require(rank(difference(shear(a), shear(b))) == expected,
                    "wrong operator distance")
            pairs += 1
    return pairs


def check_factors(left_parameters, right_parameters):
    checks = 0
    for t in left_parameters:
        for a in right_parameters:
            factor = ((t - a, (t - a) * (t + a)), (Q(1), t + a))
            require(difference(label(t, 0), label(a, 1)) == factor,
                    "cross rank-one factorization failed")
            checks += 1
    for side, parameters in enumerate((left_parameters, right_parameters)):
        for x in parameters:
            for y in parameters:
                det = determinant2(difference(label(x, side), label(y, side)))
                require(det == (1 if side == 0 else -1) * (x - y) ** 2,
                        "within-family determinant identity failed")
                checks += 1
    return checks


def check_group(matrices):
    identity = shear(((Q(0), Q(0)), (Q(0), Q(0))))
    pairs = 0
    for a in matrices:
        inverse = shear(tuple(tuple(-x for x in row) for row in a))
        require(multiply(shear(a), inverse) == identity, "wrong inverse")
        for b in matrices:
            total = tuple(tuple(a[i][j] + b[i][j] for j in range(2))
                          for i in range(2))
            expected = shear(total)
            require(multiply(shear(a), shear(b)) == expected, "wrong product")
            require(multiply(shear(b), shear(a)) == expected, "not commuting")
            pairs += 1
    return pairs


def rejects(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def check_controls():
    left, right = family((0, 1), 0), family((0, 1), 1)
    wrong_square = (((Q(0), Q(1)), (Q(1), Q(0))), left[1])
    missing_unit = (((Q(0), Q(0)), (Q(0), Q(0))), left[1])
    wrong_sign = (right[0], ((Q(1), Q(1)), (Q(0), Q(1))))
    rejects(lambda: check_family(wrong_square, right), "changed square")
    rejects(lambda: check_family(missing_unit, right), "omitted unit")
    rejects(lambda: check_family(left, wrong_sign), "wrong diagonal sign")
    rejects(lambda: family((0, 0), 0), "duplicate parameter")
    rejects(lambda: family((), 0), "empty family")
    rejects(lambda: family(tuple(range(65)), 0), "oversized finite fixture")
    rejects(lambda: label(0.5, 0), "inexact parameter")
    rejects(lambda: label(True, 0), "boolean parameter")
    rejects(lambda: label(0, 2), "invalid family")
    rejects(lambda: rank(((1, 2),)), "malformed matrix")
    return 10


def run():
    pairs = 0
    sizes = tuple(range(2, 13)) + (16, 32)
    for n in sizes:
        left = family(tuple(range(n)), 0)
        right = family(tuple(range(n)), 1)
        pairs += check_family(left, right)
        bound = max(1, (n - 1) ** 2)
        require(max(abs(x) for m in left + right for row in m for x in row)
                <= bound, "coefficient-height bound failed")
    left_parameters = tuple(Q(i, 3) for i in range(-4, 5))
    right_parameters = tuple(Q(i, 5) for i in range(-5, 6))
    left, right = family(left_parameters, 0), family(right_parameters, 1)
    pairs += check_family(left, right)
    factors = check_factors(left_parameters, right_parameters)
    group_pairs = check_group(left + right)
    controls = check_controls()
    require(pairs == 8116 and factors == 301 and group_pairs == 400,
            "finite coverage count changed")
    return {"status": "PASS_UNBOUNDED_SHEAR_BICLIQUES",
            "claim_type": "scoped written proof with finite corroboration",
            "balanced_fixture_sizes": list(sizes),
            "rational_fixture_parts": [len(left), len(right)],
            "ordered_label_and_operator_pairs": pairs,
            "factorization_and_determinant_checks": factors,
            "ordered_group_product_pairs": group_pairs,
            "rejection_controls": controls,
            "largest_fixture_distortion_by_PR907": str(Q(2 * (32 - 1), 32)),
            "new_kappa": False}


def main():
    require(len(sys.argv) == 1, "this verifier takes no arguments")
    result = run()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    result["package_sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in names}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
