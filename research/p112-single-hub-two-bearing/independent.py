"""Second implementation of the single-hub row minimum.

No import from verify.py. Span tests use maximal minors. Linear systems use
Cramer's rule on one nonzero maximal minor, with free variables set to zero.
GF4 is the integer field {0,1,2,3}, not the bit-pair encoding.
"""

import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZERO = Fraction(0)
NAMES = "gdthxy"
QUERIES = [
    (0, 0, 1, 0),
    (1, 1, 0, 0),
    (1, 1, 1, 0),
    (0, 0, 0, 1),
    (1, 0, 1, -1),
    (0, 1, 1, -1),
]
QUERIES = [tuple(Fraction(a) for a in row) for row in QUERIES]
MARKS = [(Fraction(1), ZERO, ZERO, ZERO), (ZERO, Fraction(1), ZERO, ZERO)]
INDEX = {name: i for i, name in enumerate(NAMES)}
READERS = {
    0: ["ghx", "dthx", "gdhy", "thy", "dxy", "gtxy"],
    1: ["gdhx", "thx", "ghy", "dthy", "dxy", "gtxy"],
}
SOURCES = {0: ["gx", "thx", "ty", "ghy"], 1: ["tx", "ghx", "gy", "thy"]}
FORCED = {("reader", 0, "dxy"), ("reader", 0, "gtxy"), ("reader", 1, "dxy"), ("reader", 1, "gtxy")}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def det(matrix):
    size = len(matrix)
    if size == 1:
        return matrix[0][0]
    total = ZERO
    for column in range(size):
        minor = [
            [matrix[row][other] for other in range(size) if other != column]
            for row in range(1, size)
        ]
        sign = Fraction(1) if column % 2 == 0 else Fraction(-1)
        total += sign * matrix[0][column] * det(minor)
    return total


def rank(columns):
    count = len(columns)
    for size in range(min(4, count), 0, -1):
        for chosen_columns in combinations(range(count), size):
            for chosen_rows in combinations(range(4), size):
                matrix = [
                    [columns[column][row] for column in chosen_columns]
                    for row in chosen_rows
                ]
                if det(matrix) != 0:
                    return size
    return 0


def contained(columns, target):
    return rank(columns) == rank(list(columns) + [tuple(target)])


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def solve(equations, targets, variables):
    """One particular solution, or None when inconsistent."""
    count = len(equations)
    chosen = None
    for size in range(min(variables, count), -1, -1):
        found = False
        row_sets = list(combinations(range(count), size)) if size else [()]
        column_sets = list(combinations(range(variables), size)) if size else [()]
        for rows in row_sets:
            for columns in column_sets:
                minor = [[equations[row][column] for column in columns] for row in rows]
                if size == 0 or det(minor) != 0:
                    chosen = (rows, columns)
                    found = True
                    break
            if found:
                break
        if found:
            break
    rows, columns = chosen
    square = [[equations[row][column] for column in columns] for row in rows]
    rhs = [targets[row] for row in rows]
    pivot = []
    if rows:
        base = det(square)
        for column_index in range(len(columns)):
            replaced = [list(row) for row in square]
            for row_index in range(len(rows)):
                replaced[row_index][column_index] = rhs[row_index]
            pivot.append(det(replaced) / base)
    solution = [ZERO] * variables
    for value, column in zip(pivot, columns):
        solution[column] = value
    if any(dot(equation, solution) != target for equation, target in zip(equations, targets)):
        return None
    return solution


def coefficients(support, mark):
    equations = [[QUERIES[i][coordinate] for i in support] for coordinate in range(4)]
    return solve(equations, list(MARKS[mark]), len(support))


def evaluator(mark, killed):
    equations = [list(MARKS[mark]), list(MARKS[1 - mark])]
    targets = [Fraction(1), ZERO]
    for index in killed:
        equations.append(list(QUERIES[index]))
        targets.append(ZERO)
    return solve(equations, targets, 4)


def minimum(kind, mark, spec):
    pools = [spec] if kind == "reader" else READERS[mark]
    extra = () if kind == "reader" else tuple(INDEX[name] for name in spec)
    best = None
    for pool in pools:
        indices = [INDEX[name] for name in pool]
        for size in range(1, len(indices) + 1):
            for pick in combinations(indices, size):
                solution = coefficients(pick, mark)
                if solution is None:
                    continue
                support = tuple(i for i, coeff in zip(pick, solution) if coeff != 0)
                for killed_count in range(len(support), -1, -1):
                    hit = False
                    for extra_killed in combinations(support, killed_count):
                        phi = evaluator(mark, tuple(sorted(set(extra) | set(extra_killed))))
                        if phi is None:
                            continue
                        cost = sum(1 for i in support if dot(phi, QUERIES[i]) != 0)
                        best = cost if best is None else min(best, cost)
                        hit = True
                        break
                    if hit:
                        break
    require(best is not None, "missing row")
    return best


def pairing_holds():
    samples = (ZERO, Fraction(1), Fraction(-1))
    specs = ((0, "dxy"), (1, "dxy"), (0, "gtxy"), (1, "gtxy"))
    for mark, spec in specs:
        support = [INDEX[name] for name in spec]
        require(coefficients(support, mark) is not None, spec)
        for dropped in combinations(support, len(support) - 1):
            require(coefficients(dropped, mark) is None, "proper subset of " + spec)
        for alpha in samples:
            for beta in samples:
                phi = (Fraction(1), ZERO, alpha, beta) if mark == 0 else (ZERO, Fraction(1), alpha, beta)
                values = [dot(phi, QUERIES[i]) for i in support]
                gap = 1 if mark == 0 else -1
                if spec == "dxy":
                    require(values[0] == 1 and values[1] - values[2] == gap, spec)
                else:
                    require(values[1] - values[0] == 1 and values[2] - values[3] == gap, spec)
                require(sum(value != 0 for value in values) >= 2, spec)


def gf4_ok():
    mul = [
        [0, 0, 0, 0],
        [0, 1, 2, 3],
        [0, 2, 3, 1],
        [0, 3, 1, 2],
    ]

    def add(left, right):
        return [a ^ b for a, b in zip(left, right)]

    def scale(scalar, vector):
        return [mul[scalar][entry] for entry in vector]

    e, f, g, h = [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]
    images = [
        g,
        add(add(e, f), scale(2, add(g, h))),
        add(add(add(e, f), g), scale(2, h)),
        h,
        add(add(e, g), h),
        add(add(f, g), h),
    ]
    marks = (e, f)

    def inside(columns, target):
        rows = [[columns[col][row] for col in range(len(columns))] + [target[row]] for row in range(4)]
        pivot = 0
        for col in range(len(columns)):
            chosen = next((i for i in range(pivot, 4) if rows[i][col] != 0), None)
            if chosen is None:
                continue
            rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
            inverse = next(cand for cand in range(1, 4) if mul[rows[pivot][col]][cand] == 1)
            rows[pivot] = [mul[inverse][entry] for entry in rows[pivot]]
            for i in range(4):
                if i != pivot and rows[i][col] != 0:
                    factor = rows[i][col]
                    rows[i] = [a ^ mul[factor][b] for a, b in zip(rows[i], rows[pivot])]
            pivot += 1
        return all(row[-1] == 0 for row in rows if all(entry == 0 for entry in row[:-1]))

    for mask in range(64):
        chosen = [i for i in range(6) if mask >> i & 1]
        for mark in (0, 1):
            old_reader = contained([QUERIES[i] for i in chosen], MARKS[mark])
            old_outside = not contained([MARKS[1 - mark]] + [QUERIES[i] for i in chosen], MARKS[mark])
            new = [images[i] for i in chosen]
            if old_reader and not inside(new, marks[mark]):
                return False
            if old_outside and inside([marks[1 - mark]] + new, marks[mark]):
                return False
    return True


def check_witness(payload):
    require(len(payload["rows"]) == 20, "row count")
    for record in payload["rows"]:
        mark = record["mark"]
        support = [INDEX[name] for name in record["support"]]
        coeffs = [Fraction(value) for value in record["u"]]
        phi = [Fraction(value) for value in record["phi"]]
        total = [ZERO] * 4
        for coeff, index in zip(coeffs, support):
            total = [a + coeff * b for a, b in zip(total, QUERIES[index])]
        require(tuple(total) == MARKS[mark], record["premise"])
        require(dot(phi, MARKS[mark]) == 1 and dot(phi, MARKS[1 - mark]) == 0, "phi")
        lower = 2 if (record["kind"], mark, record["premise"]) in FORCED else 1
        require(record["cost"] == lower, "stored cost")
        require(minimum(record["kind"], mark, record["premise"]) == record["cost"], "searched cost")
    require(payload["query_charges"] == [0, 20, 4, 8, 6, 10], "charges")
    require(sum(payload["query_charges"]) == 48, "total")


def main():
    require(gf4_ok(), "GF4 transfer")
    pairing_holds()
    check_witness(json.loads((ROOT / "WITNESS.json").read_text(encoding="utf-8")))
    print("PASS_SINGLE_HUB_TWO_BEARING_INDEPENDENT")


if __name__ == "__main__":
    main()
