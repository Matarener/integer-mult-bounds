#!/usr/bin/env python3
"""Exact finite corroboration of the sunflower inertia construction.

Produced by Nick Petalas. Apache-2.0.
The all-size theorem is the written proof in README.md.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from pathlib import Path
import platform


MAX_GROUND = 7
MAX_ORDER = 64
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def labels_and_ground(sizes, core):
    require(isinstance(core, int) and 0 <= core <= MAX_GROUND, "invalid core")
    require(3 <= len(sizes) <= MAX_GROUND, "at least three petals required")
    require(all(isinstance(a, int) and a >= 1 for a in sizes), "invalid petal")
    require(tuple(sorted(sizes, reverse=True)) == sizes, "petals must be sorted")
    require(sum(sizes) + core <= MAX_GROUND, "ground capacity exceeded")
    base = [(0, s) for s in range(1 << sizes[0])]
    for i, a in enumerate(sizes[1:], 1):
        base.extend((i, s) for s in range(1, 1 << a))
    offsets = [core + sum(sizes[:i]) for i in range(len(sizes))]
    labels = [(r, i, s) for r in range(1 << core) for i, s in base]
    ground = [r | (s << offsets[i]) for r, i, s in labels]
    require(len(labels) <= MAX_ORDER, "matrix capacity exceeded")
    require(len(set(ground)) == len(ground), "ground labels must be distinct")
    return labels, ground


def entry(x, y, leaf_mode="cancel", coefficient=2):
    r, i, s = x
    t, j, u = y
    if r & t:
        return 0
    if i == j:
        return int(s & u == 0)
    k = (s & u).bit_count()
    even = 0 if k == 0 else (1 << (k - 1)) - 1
    if i == 0 or j == 0:
        return 1 + coefficient * even
    if leaf_mode == "cancel":
        return 1 + coefficient**2 * even
    if leaf_mode == "pairwise":
        return 1 + coefficient * even
    require(leaf_mode == "unweighted", "unknown leaf mode")
    return 1


def literal_matrix(labels, leaf_mode="cancel", coefficient=2):
    return [[entry(x, y, leaf_mode, coefficient) for y in labels] for x in labels]


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left, right):
    require(len(left[0]) == len(right), "matrix product shape mismatch")
    require(max(len(left), len(right), len(right[0])) <= MAX_ORDER, "product capacity")
    out = [[0] * len(right[0]) for _ in left]
    for i, row in enumerate(left):
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(right[k]):
                    out[i][j] += value * other
    return out


def permute_first(matrix, position):
    matrix[0], matrix[position] = matrix[position], matrix[0]
    for row in matrix:
        row[0], row[position] = row[position], row[0]


def inertia_determinant(matrix):
    """Symmetric elimination, including zero-diagonal 2-by-2 pivots."""
    n = len(matrix)
    require(1 <= n <= MAX_ORDER, "invalid matrix order")
    require(all(len(row) == n for row in matrix), "matrix must be square")
    require(matrix == transpose(matrix), "matrix must be symmetric")
    work = [[Fraction(x) for x in row] for row in matrix]
    positive = negative = zero = 0
    determinant = Fraction(1)
    for _ in range(n):
        if not work:
            break
        diagonal = next((i for i in range(len(work)) if work[i][i]), None)
        if diagonal is not None:
            permute_first(work, diagonal)
            pivot = work[0][0]
            positive += pivot > 0
            negative += pivot < 0
            determinant *= pivot
            work = [[work[i][j] - work[i][0] * work[0][j] / pivot
                     for j in range(1, len(work))] for i in range(1, len(work))]
            continue
        pair = next(((i, j) for i in range(len(work))
                     for j in range(i + 1, len(work)) if work[i][j]), None)
        if pair is None:
            zero += len(work)
            determinant = Fraction(0)
            work = []
            break
        i, j = pair
        permute_first(work, i)
        # j>i, so the first swap leaves the second pivot index j unchanged.
        work[1], work[j] = work[j], work[1]
        for row in work:
            row[1], row[j] = row[j], row[1]
        pivot = work[0][1]
        positive += 1
        negative += 1
        determinant *= -pivot**2
        work = [[work[i][j] - (work[i][0] * work[1][j]
                 + work[i][1] * work[0][j]) / pivot
                 for j in range(2, len(work))] for i in range(2, len(work))]
    require(not work and positive + negative + zero == n, "elimination incomplete")
    return (positive, negative, zero), determinant


def expected(sizes, core):
    base_order = 1 + sum((1 << a) - 1 for a in sizes)
    n = (1 << core) * base_order
    star = n // 2 if core else 1 << (sizes[0] - 1)
    exponent = (1 << core) * sum((1 << (a - 1)) - 1 for a in sizes[1:])
    return (star, n - star, 0), (-1)**(n - star) * 3**exponent


def transformed_blocks(sizes):
    """Build B independently in the zeta basis, before Schur elimination."""
    labels, _ = labels_and_ground(sizes, 0)
    n = len(labels)
    zeta = [[int(i == j and t & s == t)
             for _, j, t in labels] for _, i, s in labels]
    reduced = [[0] * n for _ in range(n)]
    for x, (_, i, s) in enumerate(labels):
        for y, (_, j, t) in enumerate(labels):
            if i == j == 0:
                reduced[x][y] = (-1)**s.bit_count() if s == t else 0
            elif i == j:
                reduced[x][y] = ((-1)**s.bit_count() if s == t else 0)
                reduced[x][y] += (-1)**(s.bit_count() + t.bit_count())
            elif i == 0:
                reduced[x][y] = ((-1)**(t.bit_count() + 1) if s == 0 else 0)
                reduced[x][y] += 2 * int(s == t and t.bit_count() % 2 == 0)
            elif j == 0:
                reduced[x][y] = ((-1)**(s.bit_count() + 1) if t == 0 else 0)
                reduced[x][y] += 2 * int(s == t and s.bit_count() % 2 == 0)
            else:
                reduced[x][y] = (-1)**(s.bit_count() + t.bit_count())
                reduced[x][y] += 4 * int(s == t and s.bit_count() % 2 == 0)
    return zeta, reduced


def check_schur(sizes, reduced):
    a = sizes[0]
    cut = 1 << a
    labels, _ = labels_and_ground(sizes, 0)
    count = 0
    for i in range(cut, len(reduced)):
        for j in range(cut, len(reduced)):
            correction = sum(reduced[i][k] * (-1)**k.bit_count() * reduced[k][j]
                             for k in range(cut))
            target = (-1 if labels[i][2].bit_count() % 2 else -3) if i == j else 0
            require(reduced[i][j] - correction == target, "Schur cancellation")
            count += 1
    return count


def check_case(sizes, core):
    labels, ground = labels_and_ground(sizes, core)
    matrix = literal_matrix(labels)
    support = 0
    for i, x in enumerate(ground):
        for j, y in enumerate(ground):
            require(type(matrix[i][j]) is int and matrix[i][j] >= 0, "integer positivity")
            require(not (x & y) or matrix[i][j] == 0, "disjointness support")
            support += 1
    stars = [sum(bool(mask & (1 << bit)) for mask in ground)
             for bit in range(sum(sizes) + core)]
    wanted, determinant = expected(sizes, core)
    require(max(stars) == wanted[0], "literal largest star")
    actual, det = inertia_determinant(matrix)
    require((actual, det) == (wanted, determinant), "literal inertia or determinant")
    zeta, reduced = transformed_blocks(sizes)
    base_labels, _ = labels_and_ground(sizes, 0)
    base = literal_matrix(base_labels)
    require(multiply(multiply(zeta, reduced), transpose(zeta)) == base, "zeta congruence")
    schur = check_schur(sizes, reduced)
    return {"petals": list(sizes), "core": core, "order": len(labels),
            "inertia": list(actual), "determinant": str(det),
            "support_entries": support, "schur_entries": schur}


def rejected(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def controls():
    labels, _ = labels_and_ground((2, 2, 2), 0)
    target = ((2, 8, 0), Fraction(9))
    require(inertia_determinant(literal_matrix(labels)) == target, "first new fixture")
    passed = ["first_new_fixture"]
    failures = {}
    for mode in ("pairwise", "unweighted"):
        result = inertia_determinant(literal_matrix(labels, mode))
        require(result != target, "missing cancellation must change the certificate")
        failures[mode] = {"inertia": list(result[0]), "determinant": str(result[1])}
        passed.append(mode)
    weak = inertia_determinant(literal_matrix(labels, coefficient=1))
    require(weak[0][2] > 0, "weak coupling must leave null directions")
    failures["weak_coupling"] = {"inertia": list(weak[0]), "determinant": str(weak[1])}
    passed.append("weak_coupling")
    require(inertia_determinant([[0, 2], [2, 0]]) == ((1, 1, 0), -4), "2x2 pivot")
    passed.append("zero_diagonal_pivot")
    require(inertia_determinant([[0, 0], [0, 0]]) == ((0, 0, 2), 0), "zeros count")
    passed.append("zero_eigenvalues")
    rejected(lambda: inertia_determinant([[1, 2], [0, 1]]), "asymmetry")
    passed.append("asymmetry")
    rejected(lambda: labels_and_ground((2, 2), 0), "previous two-facet domain")
    passed.append("previous_domain_excluded")
    rejected(lambda: labels_and_ground((1, 2, 1), 0), "unsorted petals")
    passed.append("unsorted_petals")
    rejected(lambda: labels_and_ground((2, 1, 0), 0), "empty petal")
    passed.append("empty_petal")
    rejected(lambda: labels_and_ground((3, 3, 2), 0), "capacity")
    passed.append("ground_capacity")
    rejected(lambda: labels_and_ground((1, 1, 1), -1), "negative core")
    passed.append("negative_core")
    require(expected((2, 2, 2), 0)[0][0] < 4, "sum of petal stars is not largest star")
    passed.append("largest_star_not_star_sum")
    return {"count": len(passed), "passed": passed, "distinguishing_fixtures": failures}


def parameter_cases():
    cases = []
    for petals in range(3, MAX_GROUND + 1):
        for ascending in combinations_with_replacement(range(1, MAX_GROUND + 1), petals):
            sizes = tuple(reversed(ascending))
            total = sum(sizes)
            if total <= MAX_GROUND:
                for core in range(MAX_GROUND - total + 1):
                    cases.append((sizes, core))
    require(len(cases) <= 256, "parameter inventory capacity")
    return cases


def main():
    cases = [check_case(sizes, core) for sizes, core in parameter_cases()]
    result = {"status": "PASS_SUNFLOWER_DOWNSET_INERTIA",
              "claim_type": "scoped proof with exact finite corroboration",
              "no_new_kappa": True, "python": platform.python_version(),
              "cases": cases, "case_count": len(cases), "controls": controls()}
    folder = Path(__file__).resolve().parent
    result["sha256"] = {name: sha256((folder / name).read_bytes()).hexdigest()
                        for name in PACKAGE_FILES}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
