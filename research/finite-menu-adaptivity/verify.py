#!/usr/bin/env python3
"""Exact finite corroboration and rational witnesses for the written theorem."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from math import prod
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows):
    require(isinstance(rows, (list, tuple)) and 1 <= len(rows) <= 8,
            "expected one to eight rows")
    require(all(isinstance(row, (list, tuple)) for row in rows), "invalid row")
    width = len(rows[0])
    require(1 <= width <= 8 and all(len(row) == width for row in rows),
            "expected a rectangular matrix of width at most eight")
    require(all(type(x) is int or isinstance(x, Fraction) for row in rows for x in row),
            "expected exact rational coefficients")
    result = tuple(tuple(Fraction(x) for x in row) for row in rows)
    require(all(x.numerator.bit_length() <= 64 and x.denominator.bit_length() <= 64
                for row in result for x in row), "coefficient limit")
    return result


def difference(left, right):
    require(len(left) == len(right) and len(left[0]) == len(right[0]),
            "shape mismatch")
    return tuple(tuple(a - b for a, b in zip(x, y)) for x, y in zip(left, right))


def image(operator, vector):
    require(len(operator[0]) == len(vector), "vector shape mismatch")
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in operator)


def rank(rows):
    if not rows or not rows[0]:
        return 0
    work = [list(map(Fraction, row)) for row in rows]
    pivot = 0
    for column in range(len(work[0])):
        candidates = [i for i in range(pivot, len(work)) if work[i][column]]
        if not candidates:
            continue
        selected = candidates[0]
        work[pivot], work[selected] = work[selected], work[pivot]
        scale = work[pivot][column]
        work[pivot] = [x / scale for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            scale = work[i][column]
            work[i] = [x - scale * y for x, y in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def escape(target_rows, menu_rows):
    """Return an input missed by every entry, or reject a menu containing target."""
    target = matrix(target_rows)
    require(isinstance(menu_rows, (list, tuple)) and 1 <= len(menu_rows) <= 32,
            "expected one to 32 menu entries")
    defects = [difference(matrix(entry), target) for entry in menu_rows]
    require(all(any(x for row in defect for x in row) for defect in defects),
            "menu already contains target")
    dimension = len(target[0])
    limit = len(defects) * (dimension - 1) + 1
    for t in range(limit):
        vector = tuple(Fraction(t**j) for j in range(dimension))
        if all(any(image(defect, vector)) for defect in defects):
            return vector, t, limit
    raise ValueError("moment-curve theorem violated")


def weighted_basis(defect, sizes):
    require(len(sizes) == len(defect[0]) and
            all(type(s) is int and 1 <= s <= 32 for s in sizes), "grid size limit")
    selected = []
    for column in sorted(range(len(sizes)), key=lambda j: (-sizes[j], j)):
        trial = selected + [column]
        submatrix = [[row[j] for j in trial] for row in defect]
        if rank(submatrix) == len(trial):
            selected.append(column)
    require(len(selected) == rank(defect), "incomplete column basis")
    return tuple(selected), prod(sizes[j] for j in selected)


def coverage_bound(target_rows, menu_rows, sizes):
    target = matrix(target_rows)
    require(isinstance(menu_rows, (list, tuple)) and 1 <= len(menu_rows) <= 32,
            "expected one to 32 menu entries")
    defects = [difference(matrix(entry), target) for entry in menu_rows]
    return sum((Fraction(1, weighted_basis(defect, sizes)[1]) for defect in defects),
               Fraction(0))


def minor_rank(rows):
    """Independent determinant/permutation oracle, limited to four by four."""
    height, width = len(rows), len(rows[0])
    require(max(height, width) <= 4, "minor oracle limit")
    answer = 0
    for size in range(1, min(height, width) + 1):
        for rr in combinations(range(height), size):
            for cc in combinations(range(width), size):
                value = Fraction(0)
                for order in permutations(range(size)):
                    inversions = sum(order[i] > order[j]
                                     for i in range(size) for j in range(i + 1, size))
                    value += (-1)**inversions * prod(rows[rr[i]][cc[order[i]]]
                                                    for i in range(size))
                if value:
                    answer = size
    return answer


def check_grids():
    matrices = [matrix([bits[:3], bits[3:]])
                for bits in product((-1, 0, 1), repeat=6)]
    sizes_cases = ((1, 2, 3), (3, 2, 1), (2, 2, 2))
    fibers = 0
    for operator in matrices:
        expected_rank = minor_rank(operator)
        require(rank(operator) == expected_rank, "rank oracle disagreement")
        for sizes in sizes_cases:
            basis, weight = weighted_basis(operator, sizes)
            weights = []
            for columns in combinations(range(3), expected_rank):
                sub = [[row[j] for j in columns] for row in operator]
                if not columns or minor_rank(sub) == expected_rank:
                    weights.append(prod(sizes[j] for j in columns))
            require(weight == max(weights), "weighted-basis optimum failed")
            require(len(basis) == expected_rank, "basis rank changed")
            points = list(product(*(range(s) for s in sizes)))
            outcomes = {}
            for point in points:
                value = image(operator, point)
                outcomes[value] = outcomes.get(value, 0) + 1
            require(all(count * weight <= prod(sizes) for count in outcomes.values()),
                    "Cartesian fiber bound failed")
            fibers += len(outcomes)
    return {"matrices": len(matrices), "weighted_grids": len(matrices) * 3,
            "enumerated_fibers": fibers}


def check_witnesses():
    rows = [row for row in product((-1, 0, 1), repeat=3) if any(row)]
    target = [[0, 0, 0]]
    grid = tuple(product(range(4), repeat=3))
    witnesses = 0
    for family in combinations(rows, 3):
        vector, t, limit = escape(target, [[row] for row in family])
        require(t < limit == 7, "wrong witness budget")
        require(all(image([row], vector) != (0,) for row in family),
                "returned vector is not a simultaneous witness")
        bound = coverage_bound(target, [[row] for row in family], (4, 4, 4))
        covered = sum(any(image([row], point) == (0,) for row in family)
                      for point in grid)
        require(bound == Fraction(3, 4) and covered <= bound * len(grid),
                "menu coverage exceeds strict grid bound")
        witnesses += 1
    family = [[[2*j*(2*j + 1), -(4*j + 1), 1]] for j in range(4)]
    vector, t, limit = escape(target, family)
    require((vector, t, limit) == ((1, 8, 64), 8, 9), "sharp curve fixture")
    require(escape([[0]], [[[1]], [[-1]]]) == ((1,), 0, 1), "dimension one")
    rational = [[[Fraction(1, 3), 0]], [[0, Fraction(2, 5)]]]
    require(escape([[0, 0]], rational)[0] == (1, 1), "rational coefficients")
    return {"three_entry_menus": witnesses, "sharp_curve_tests": 9,
            "menu_grid_points": witnesses * len(grid),
            "rational_and_dimension_one_controls": 2}


def check_scope():
    identity = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    menus = [matrix([[1, 0, 0], [0, 1, 0], [1, sign, 1]]) for sign in (-1, 1)]
    grid = list(product((-1, 1), repeat=3))
    require(all(any(image(entry, x) == x for entry in menus) for x in grid),
            "strict-inequality boundary fixture")
    require(coverage_bound(identity, menus, (2, 2, 2)) == 1,
            "strictness boundary has incorrect weight")
    vector, _, _ = escape(identity, menus)
    require(all(image(entry, vector) != vector for entry in menus), "full dirty endpoint")
    require(all(entry[:2] == identity[:2] for entry in menus), "projection control")
    finite_points = 0
    for p in (2, 3, 5, 7):
        normals = [(1, -a) for a in range(p)] + [(0, 1)]
        for x, y, z in product(range(p), repeat=3):
            require(any((a*x + b*y) % p == 0 for a, b in normals), "finite field cover")
            finite_points += 1
        require(all(any((a*x + b*y) % p for x, y in product(range(p), repeat=2))
                    for a, b in normals), "finite leaf unexpectedly equals identity")
    rational_points = 0
    for x, y in product(range(-4, 5), repeat=2):
        normal = (y, -x) if (x or y) else (1, 0)
        require(any(normal) and normal[0]*x + normal[1]*y == 0, "infinite menu")
        rational_points += 1
    return {"sharp_restricted_grid_points": len(grid),
            "finite_field_points": finite_points, "infinite_menu_controls": rational_points,
            "dirty_projection_control": 1}


def check_rejections():
    cases = (
        lambda: escape([[0]], []),
        lambda: escape([[0]], [[[0]]]),
        lambda: escape([[0]], [[[1, 0]]]),
        lambda: escape([[0]], [[[1]]] * 33),
        lambda: matrix([[0.0]]),
        lambda: matrix([[True]]),
        lambda: matrix([[2**65]]),
        lambda: matrix([[1], [1, 2]]),
        lambda: weighted_basis(matrix([[1]]), (0,)),
        lambda: weighted_basis(matrix([[1]]), (True,)),
    )
    for case in cases:
        try:
            case()
        except ValueError:
            continue
        raise ValueError("invalid domain was accepted")
    return len(cases)


def main():
    results = {"grid_checks": check_grids(), "witness_checks": check_witnesses(),
               "scope_checks": check_scope(), "domain_rejections": check_rejections()}
    package = Path(__file__).resolve().parent
    results["source_sha256"] = {
        name: sha256((package / name).read_bytes()).hexdigest()
        for name in ("README.md", "PROOF.md", "verify.py", "TASK.json",
                     "SOURCES.json", "VERIFY.json")}
    results["status"] = "PASS_FINITE_MENU_ADAPTIVITY"
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
