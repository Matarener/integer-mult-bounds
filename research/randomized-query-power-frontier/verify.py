#!/usr/bin/env python3
"""Exact finite controls for the stochastic rank-power query frontier.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
from math import comb
from pathlib import Path
import json
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(k):
    return tuple(tuple(F(i == j) for j in range(k)) for i in range(k))


def zero(k):
    return tuple(tuple(F(0) for _ in range(k)) for _ in range(k))


def rank(matrix):
    """Bounded exact elimination; every caller supplies at most eight rows."""
    n = len(matrix)
    require(1 <= n <= 8 and all(len(row) == n for row in matrix), "matrix size")
    rows = [list(map(F, row)) for row in matrix]
    pivot = 0
    for col in range(n):
        chosen = next((j for j in range(pivot, n) if rows[j][col]), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        scale = rows[pivot][col]
        rows[pivot] = [x / scale for x in rows[pivot]]
        for j in range(pivot + 1, n):
            scale = rows[j][col]
            rows[j] = [x - scale * y for x, y in zip(rows[j], rows[pivot])]
        pivot += 1
    return pivot


def multiply(a, b):
    k = len(a)
    return tuple(tuple(sum(a[i][h] * b[h][j] for h in range(k))
                       for j in range(k)) for i in range(k))


def inspect_law(k, cap, law):
    """Compute every entry of the mean and error covariance, not sampled x."""
    require(1 <= cap <= k <= 8, "law dimensions")
    require(1 <= len(law) <= 71, "law capacity")
    require(all(isinstance(p, F) and p >= 0 for p, _ in law), "probability")
    require(sum(p for p, _ in law) == 1, "probability sum")
    mean = [[F(0) for _ in range(k)] for _ in range(k)]
    error = [[F(0) for _ in range(k)] for _ in range(k)]
    mean_rank = F(0)
    for probability, matrix in law:
        r = rank(matrix)
        require(r <= cap, "rank cap")
        mean_rank += probability * r
        for i in range(k):
            for j in range(k):
                mean[i][j] += probability * matrix[i][j]
                error[i][j] += probability * sum(
                    (matrix[h][i] - (h == i)) * (matrix[h][j] - (h == j))
                    for h in range(k))
    require(tuple(map(tuple, mean)) == identity(k), "unbiased operator")
    return tuple(map(tuple, error)), mean_rank


def projection_law(k, cap, beta, walsh=False):
    """Uniform coordinate projectors, optionally in a rational Walsh basis."""
    require(1 <= cap <= k <= 8 and 0 < beta <= 1, "projection parameters")
    require(not walsh or k & (k - 1) == 0, "Walsh width")
    law = [(1 - beta, zero(k))]
    weight = beta / comb(k, cap)
    scale = F(k, cap) / beta
    for subset in combinations(range(k), cap):
        if walsh:
            matrix = tuple(tuple(scale * sum(
                (-1) ** ((i & h).bit_count() + (j & h).bit_count())
                for h in subset) / k for j in range(k)) for i in range(k))
        else:
            matrix = tuple(tuple(scale * (i == j and i in subset)
                                 for j in range(k)) for i in range(k))
        law.append((weight, matrix))
    return law


def check_attainers():
    cases = outcomes = 0
    examples = []
    for k in range(1, 9):
        for cap in range(1, k + 1):
            for beta in (F(1), F(1, 2), F(2, 3), F(1, 4)):
                for walsh in ((False, True) if k & (k - 1) == 0 else (False,)):
                    law = projection_law(k, cap, beta, walsh)
                    covariance, mean_rank = inspect_law(k, cap, law)
                    variance = F(k, cap) / beta - 1
                    expected = tuple(tuple(variance * (i == j) for j in range(k))
                                     for i in range(k))
                    require(covariance == expected, "sharp worst-input covariance")
                    require(mean_rank == beta * cap, "rank charge")
                    require(all(p == 0 or rank(a) in (0, cap) for p, a in law),
                            "only endpoint ranks attain the power relaxation")
                    cases += 1
                    outcomes += len(law)
                    if (k, cap, beta, walsh) in ((8, 4, F(1, 2), False),
                                                 (8, 8, F(2, 3), True)):
                        examples.append({"k": k, "cap": cap, "beta": str(beta),
                                         "variance": str(variance)})
    return {"laws": cases, "outcomes": outcomes, "examples": examples}


def check_trace_rank():
    matrices = equalities = 0
    for k in range(1, 4):
        for entries in product((-1, 0, 1), repeat=k * k):
            a = tuple(tuple(F(entries[i * k + j]) for j in range(k))
                      for i in range(k))
            r = rank(a)
            trace = sum(a[i][i] for i in range(k))
            norm2 = sum(x * x for row in a for x in row)
            require(trace * trace <= r * norm2, "trace-rank inequality")
            if r and trace * trace == r * norm2:
                scale = trace / r
                square = multiply(a, a)
                require(all(a[i][j] == a[j][i] and square[i][j] == scale * a[i][j]
                            for i in range(k) for j in range(k)),
                        "equality is a scalar orthogonal projector")
                equalities += 1
            matrices += 1
    return {"matrices": matrices, "nonzero_equalities": equalities}


def check_power_and_precision():
    inequalities = strict = 0
    for cap in range(1, 65):
        for r in range(1, cap + 1):
            for numerator, denominator in ((1, 2), (2, 3), (9, 10), (499, 500)):
                # ((r/cap)^t >= r/cap)^denominator, exactly over integers.
                left = r ** numerator * cap ** denominator
                right = r ** denominator * cap ** numerator
                require(left >= right and (left == right) == (r == cap),
                        "strict concave rank-price comparison")
                inequalities += 1
                strict += left > right
    rows = []
    for guard in range(17):
        epsilon2 = F(1, 4 ** guard)
        beta = 1 / (1 + epsilon2)
        require(1 / beta - 1 == epsilon2, "variance-budget inverse")
        require(1 - beta == F(1, 4 ** guard + 1), "precision saving fraction")
        rows.append({"g": guard, "maximum_fractional_saving": str(1 - beta)})
    return {"power_comparisons": inequalities, "strict": strict,
            "normalized_tolerances": rows}


def expect_rejection(k, cap, law, message):
    try:
        inspect_law(k, cap, law)
    except ValueError as error:
        require(str(error) == message, "wrong failure reason")
        return 1
    raise ValueError("invalid law was accepted: " + message)


def check_controls():
    controls = 0
    controls += expect_rejection(2, 0, [(F(1), identity(2))], "law dimensions")
    controls += expect_rejection(9, 1, [(F(1), identity(9))], "law dimensions")
    controls += expect_rejection(2, 2, [(F(-1), zero(2)), (F(2), identity(2))],
                                 "probability")
    controls += expect_rejection(2, 2, [(F(1, 2), identity(2))], "probability sum")
    controls += expect_rejection(2, 1, [(F(1), identity(2))], "rank cap")
    controls += expect_rejection(2, 2, [(F(1), zero(2))], "unbiased operator")
    law = projection_law(2, 1, F(1, 2))
    damaged = [(p, tuple(tuple(x / 2 for x in row) for row in a)) for p, a in law]
    controls += expect_rejection(2, 1, damaged, "unbiased operator")
    biased = [(F(1), ((F(1), F(0)), (F(0), F(0))))]
    controls += expect_rejection(2, 1, biased, "unbiased operator")
    covariance, _ = inspect_law(2, 1, law)
    require(covariance != ((F(1), F(0)), (F(0), F(1))), "omitted thinning noise")
    controls += 1
    coordinate = projection_law(2, 1, F(1))
    lottery = projection_law(2, 2, F(1, 2))
    covariance1, rank1 = inspect_law(2, 1, coordinate)
    covariance2, rank2 = inspect_law(2, 2, lottery)
    require(covariance1 == covariance2 and rank1 == rank2 == 1,
            "equal mean rank and noise do not fix the power price")
    # At t=1/2 the normalized prices are sqrt(1/2) and 1/2.
    require(F(1, 2) ** 2 < F(1, 2), "strict price advantage for the full-rank lottery")
    controls += 1
    for copies in range(1, 9):
        repeated = [(F(comb(copies, j), 2 ** copies),
                     tuple(tuple(F(2 * j, copies) * (a == b) for b in range(2))
                           for a in range(2))) for j in range(copies + 1)]
        covariance, _ = inspect_law(2, 2, repeated)
        require(covariance == ((F(1, copies), F(0)), (F(0), F(1, copies))),
                "independent averaging covariance")
        require(F(copies, 2) >= 1 / (1 + covariance[0][0]), "repeats pay")
        controls += 1
    return controls


def package_hashes(root):
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (root / name).open("rb") as stream:
            data = stream.read(262145)
        require(len(data) <= 262144, "package file capacity")
        hashes[name] = sha256(data).hexdigest()
    return hashes


def main():
    require(len(sys.argv) == 1, "no command-line arguments")
    root = Path(__file__).resolve().parent
    result = {"status": "PASS_RANDOMIZED_QUERY_POWER_FRONTIER",
              "attainers": check_attainers(), "trace_rank": check_trace_rank(),
              "power_and_precision": check_power_and_precision(),
              "controls": check_controls(), "python": sys.version.split()[0]}
    result["sha256"] = package_hashes(root)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
