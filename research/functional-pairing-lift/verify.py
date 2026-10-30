"""Exact checks for the functional-pairing signing theorem. Apache-2.0."""

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_ORDER = 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def signing(matrix):
    """Return a same-support TU signing; reject outside the row-functional class."""
    n = len(matrix)
    require(1 <= n <= MAX_ORDER, "order outside 1..256")
    require(all(len(row) == n for row in matrix), "matrix must be square")
    require(all(type(x) is int and x in (0, 1) for row in matrix for x in row),
            "entries must be binary integers")
    require(all(matrix[i][i] == 1 for i in range(n)), "diagonal must be one")
    successor = [-1] * n
    indegree = [0] * n
    for i, row in enumerate(matrix):
        edges = [j for j, value in enumerate(row) if value and j != i]
        require(len(edges) <= 1, "more than one off-diagonal one in a row")
        if edges:
            successor[i] = edges[0]
            indegree[edges[0]] += 1
    queue = [i for i in range(n) if indegree[i] == 0]
    for cursor in range(n):
        if cursor == len(queue):
            break
        j = successor[queue[cursor]]
        if j != -1:
            indegree[j] -= 1
            if indegree[j] == 0:
                queue.append(j)
    signed = [list(row) for row in matrix]
    seen = set()
    cycles = []
    for start in range(n):
        if indegree[start] == 0 or start in seen:
            continue
        cycle = []
        vertex = start
        for _ in range(n):
            require(vertex >= 0 and vertex not in seen, "invalid cycle core")
            cycle.append(vertex)
            seen.add(vertex)
            vertex = successor[vertex]
            if vertex == start:
                break
        require(vertex == start and len(cycle) >= 2, "cycle did not close")
        signed[start][successor[start]] = (-1) ** len(cycle)
        cycles.append(cycle)
    return signed, cycles


def binary_rank(matrix):
    basis = {}
    for row in matrix:
        value = sum((int(x) & 1) << j for j, x in enumerate(row))
        for _ in range(len(row)):
            if value == 0:
                break
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def rational_rank(matrix):
    if not matrix:
        return 0
    work = [[Fraction(x) for x in row] for row in matrix]
    pivot_row = 0
    for col in range(len(work[0])):
        pivot = next((i for i in range(pivot_row, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][col]
        work[pivot_row] = [x / divisor for x in work[pivot_row]]
        for i in range(pivot_row + 1, len(work)):
            multiplier = work[i][col]
            if multiplier:
                work[i] = [x - multiplier * y
                           for x, y in zip(work[i], work[pivot_row])]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def determinant(matrix):
    """Independent Leibniz oracle, used only at orders zero through four."""
    n = len(matrix)
    require(n <= 4 and all(len(row) == n for row in matrix), "minor too large")
    total = 0
    for permutation in itertools.permutations(range(n)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(n) for j in range(i + 1, n))
        term = (-1) ** inversions
        for i, j in enumerate(permutation):
            term *= matrix[i][j]
        total += term
    return total


def restrict(matrix, rows, columns):
    return [[matrix[i][j] for j in columns] for i in rows]


def functional_matrices(n):
    choices = [[-1] + [j for j in range(n) if j != i] for i in range(n)]
    for successors in itertools.product(*choices):
        matrix = [[int(i == j) for j in range(n)] for i in range(n)]
        for i, j in enumerate(successors):
            if j != -1:
                matrix[i][j] = 1
        yield matrix


def exhaustive_checks():
    totals = {"matrices": 0, "rectangular_ranks": 0, "square_minors": 0,
              "identity_decoder_attainments": 0, "cycles": 0}
    for n in range(1, 5):
        subsets = [tuple(i for i in range(n) if mask >> i & 1)
                   for mask in range(1 << n)]
        for matrix in functional_matrices(n):
            signed, cycles = signing(matrix)
            totals["matrices"] += 1
            totals["cycles"] += len(cycles)
            require(all(bool(x) == bool(y) for a, b in zip(matrix, signed)
                        for x, y in zip(a, b)), "support changed")
            for rows in subsets:
                for columns in subsets:
                    old = restrict(matrix, rows, columns)
                    new = restrict(signed, rows, columns)
                    require(binary_rank(old) == rational_rank(new), "rank mismatch")
                    totals["rectangular_ranks"] += 1
                    if len(rows) == len(columns):
                        require(determinant(new) in (-1, 0, 1), "non-TU minor")
                        totals["square_minors"] += 1
            cost = sum(binary_rank([[matrix[i][i]]]) for i in range(n))
            require(cost == n, "identity decoder must attain v")
            totals["identity_decoder_attainments"] += 1
    return totals


def cycle_fixture(n):
    return [[int(j == i or j == (i + 1) % n) for j in range(n)]
            for i in range(n)]


def larger_checks():
    result = {"matrices": 0, "rectangular_ranks": 0, "two_total_decoders": 0}
    for n in range(5, 17):
        cycle = cycle_fixture(n)
        path = [[int(j == i or j == i + 1) for j in range(n)] for i in range(n)]
        star = [[int(j == i or (i != 0 and j == 0)) for j in range(n)]
                for i in range(n)]
        pairs = [[int(j == i or j == (i ^ 1)) for j in range(n)]
                 for i in range(n)]
        for matrix in (cycle, path, star, pairs):
            signed, _ = signing(matrix)
            result["matrices"] += 1
            choices = [tuple(range(k)) for k in range(n + 1)]
            choices += [tuple(range(k, n)) for k in range(n + 1)]
            for rows, columns in itertools.product(choices, repeat=2):
                require(binary_rank(restrict(matrix, rows, columns)) ==
                        rational_rank(restrict(signed, rows, columns)),
                        "larger rectangular rank mismatch")
                result["rectangular_ranks"] += 1
        points = [(1, i + 1) for i in range(n)]
        lines = [(((i - 1) % n) + 1, -1) for i in range(n)]
        for i, j in itertools.product(range(n), repeat=2):
            value = sum(a * b for a, b in zip(points[i], lines[j]))
            require(value != 0 if i == j else not cycle[i][j] or value == 0,
                    "two-total fixture violates exactness")
        cost = 2 * binary_rank(cycle)
        require(cost == 2 * n - 2 and cost >= n, "two-total cycle cost")
        result["two_total_decoders"] += 1
    return result


def rejection_checks():
    bad = [[], [[0]], [[True]], [[1, 1]], [[1, 1, 1], [0, 1, 0], [0, 0, 1]]]
    count = 0
    for matrix in bad:
        try:
            signing(matrix)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid matrix was accepted")
    unsigned = cycle_fixture(3)
    signed, _ = signing(unsigned)
    require(determinant(unsigned) == 2 and determinant(signed) == 0,
            "odd-cycle sign control must discriminate")
    require(binary_rank(unsigned) == 2 and rational_rank(unsigned) == 3,
            "unsigned lift must fail rank agreement")
    require(signing([[int(i == j) for j in range(MAX_ORDER)]
                     for i in range(MAX_ORDER)])[1] == [], "capacity endpoint")
    try:
        signing([[1]] * (MAX_ORDER + 1))
    except ValueError:
        count += 1
    else:
        raise ValueError("oversize input was accepted")
    return count + 3


def receipt():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    source_rows = [row for row in sources["files"] if row["usage"] == "input"]
    root = HERE.parents[1]
    for row in source_rows:
        require(hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() ==
                row["sha256"], "cited source bytes changed")
    files = ("verify.py", "README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json")
    return {"schema": "functional-pairing-lift/v1", "claim_type": "scoped-proof",
            "exhaustive": exhaustive_checks(), "larger": larger_checks(),
            "controls": rejection_checks(),
            "sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                       for name in files},
            "source_sha256": {row["path"]: row["sha256"] for row in source_rows}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="create a new receipt outside the package")
    args = parser.parse_args()
    result = receipt()
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.emit:
        require(not args.emit.resolve().is_relative_to(HERE.parents[1]),
                "receipt output must be outside the checkout")
        with args.emit.open("x", encoding="utf-8") as stream:
            require(stream.write(payload) == len(payload), "incomplete receipt write")
    else:
        require((HERE / "RESULT.json").read_text() == payload, "receipt differs")
    print("PASS_FUNCTIONAL_PAIRING_LIFT " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
