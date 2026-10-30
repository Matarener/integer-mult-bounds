#!/usr/bin/env python3
"""Exact finite corroboration of the optional-diagonal inverse envelope."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

MAX_DIMENSION = 6


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(graph: tuple[tuple[int, ...], ...], budgets: tuple[F, ...]) -> int:
    n = len(graph)
    if not 1 <= n <= MAX_DIMENSION or len(budgets) != n:
        raise ValueError("dimension must be between one and six")
    if any(type(r) is not F or not 0 < r < 1 for r in budgets):
        raise ValueError("budgets must be rational and strictly between zero and one")
    for row in graph:
        if tuple(sorted(set(row))) != row:
            raise ValueError("neighbors must be sorted and distinct")
        if any(type(k) is not int or not 0 <= k < n for k in row):
            raise ValueError("neighbor outside the graph")
    return n


def column_bound(graph: tuple[tuple[int, ...], ...], budgets: tuple[F, ...],
                 root: int) -> tuple[tuple[F, ...], tuple[F, ...], F]:
    n = validate(graph, budgets)
    if type(root) is not int or not 0 <= root < n:
        raise ValueError("invalid root")
    weights = tuple(F(i == root) for i in range(n))
    # Walks of length at most n-1 suffice: deleting a cycle raises its weight.
    for _ in range(n - 1):
        weights = tuple(
            F(1) if i == root else max(
                [weights[i]] + [budgets[i] * weights[k] for k in graph[i]])
            for i in range(n))
    cycle = max([F(0)] + [budgets[root] * weights[k] for k in graph[root]])
    check(0 <= cycle < 1 and weights[root] == 1, "invalid return factor")
    bound = tuple(w / (1 - cycle) for w in weights)
    return bound, weights, cycle


def attaining_matrix(graph: tuple[tuple[int, ...], ...], budgets: tuple[F, ...],
                     root: int) -> list[list[F]]:
    bound, weights, cycle = column_bound(graph, budgets, root)
    n = len(graph)
    matrix = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        target = cycle if i == root else weights[i]
        if target == 0:
            continue
        options = [k for k in graph[i] if budgets[i] * weights[k] == target]
        check(bool(options), "missing maximizing successor")
        matrix[i][options[0]] = budgets[i]
    validate_matrix(matrix, graph, budgets)
    for i in range(n):
        check(bound[i] - sum(matrix[i][k] * bound[k] for k in range(n))
              == F(i == root), "attaining Bellman residual")
    return matrix


def validate_matrix(matrix: list[list[F]], graph: tuple[tuple[int, ...], ...],
                    budgets: tuple[F, ...]) -> None:
    n = validate(graph, budgets)
    check(len(matrix) == n and all(len(row) == n for row in matrix), "matrix shape")
    for i, row in enumerate(matrix):
        check(all(type(x) is F for x in row), "nonrational matrix")
        check(sum(abs(x) for x in row) <= budgets[i], "row budget exceeded")
        check(all(x == 0 or k in graph[i] for k, x in enumerate(row)),
              "forbidden nonzero entry")


def inverse(matrix: list[list[F]]) -> list[list[F]]:
    """Literal Gauss-Jordan inverse of I-E, independent of graph formulas."""
    n = len(matrix)
    check(1 <= n <= MAX_DIMENSION, "inverse dimension")
    work = [[F(i == j) - matrix[i][j] for j in range(n)]
            + [F(i == j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivots = [i for i in range(j, n) if work[i][j] != 0]
        check(bool(pivots), "singular inverse fixture")
        pivot = pivots[0]
        work[j], work[pivot] = work[pivot], work[j]
        scale = work[j][j]
        work[j] = [x / scale for x in work[j]]
        for i in range(n):
            if i != j:
                scale = work[i][j]
                work[i] = [a - scale * b for a, b in zip(work[i], work[j])]
    return [row[n:] for row in work]


def policy_maxima(graph: tuple[tuple[int, ...], ...], budgets: tuple[F, ...]
                  ) -> tuple[list[list[F]], int]:
    """Enumerate every zero-or-saturated single-successor row policy."""
    n = validate(graph, budgets)
    check(n <= 4, "policy oracle limited to four vertices")
    best = [[F(0) for _ in range(n)] for _ in range(n)]
    count = 0
    for choices in itertools.product(*(tuple([-1]) + row for row in graph)):
        matrix = [[F(0) for _ in range(n)] for _ in range(n)]
        for i, k in enumerate(choices):
            if k >= 0:
                matrix[i][k] = budgets[i]
        actual = inverse(matrix)
        for i in range(n):
            for j in range(n):
                best[i][j] = max(best[i][j], actual[i][j])
        count += 1
    check(count <= (n + 1) ** n, "policy capacity")
    return best, count


def support_graph(n: int, mask: int) -> tuple[tuple[int, ...], ...]:
    check(1 <= n <= 3 and 0 <= mask < 2 ** (n * n), "support domain")
    return tuple(tuple(k for k in range(n) if mask & (1 << (i * n + k)))
                 for i in range(n))


def diffuse_checks(graph: tuple[tuple[int, ...], ...], budgets: tuple[F, ...],
                   bounds: list[tuple[F, ...]]) -> int:
    n = len(graph)
    for pattern in range(3):
        matrix = [[F(0) for _ in range(n)] for _ in range(n)]
        for i, row in enumerate(graph):
            for k in row:
                sign = -1 if pattern and (i + (pattern + 1) * k) % 3 else 1
                matrix[i][k] = sign * budgets[i] / len(row)
        validate_matrix(matrix, graph, budgets)
        actual = inverse(matrix)
        for j in range(n):
            check(all(abs(actual[i][j]) <= bounds[j][i] for i in range(n)),
                  "diffuse entry exceeded envelope")
    return 3


def exhaustive_checks() -> dict[str, int]:
    counts = dict(support_budget_cases=0, policy_matrices=0,
                  attaining_columns=0, diffuse_matrices=0)
    for n in range(1, 4):
        for mask in range(2 ** (n * n)):
            graph = support_graph(n, mask)
            # Only changed-hypothesis cases: at least one diagonal is forbidden.
            if all(i in graph[i] for i in range(n)):
                continue
            for budgets in itertools.product((F(1, 3), F(2, 3)), repeat=n):
                best, policies = policy_maxima(graph, budgets)
                bounds = [column_bound(graph, budgets, j)[0] for j in range(n)]
                for j in range(n):
                    check(tuple(best[i][j] for i in range(n)) == bounds[j],
                          "complete policy oracle disagrees")
                    actual = inverse(attaining_matrix(graph, budgets, j))
                    check(tuple(actual[i][j] for i in range(n)) == bounds[j],
                          "literal attaining inverse disagrees")
                    counts['attaining_columns'] += 1
                counts['support_budget_cases'] += 1
                counts['policy_matrices'] += policies
                counts['diffuse_matrices'] += diffuse_checks(graph, budgets, bounds)
    return counts


def reject(call, label: str) -> None:
    try:
        call()
    except (AssertionError, ValueError):
        return
    raise AssertionError("control accepted: " + label)


def fixture_checks() -> dict[str, str]:
    graph = ((1,), (0,))
    budgets = (F(1, 2), F(3, 4))
    bound0, _, q0 = column_bound(graph, budgets, 0)
    bound1, _, q1 = column_bound(graph, budgets, 1)
    check(q0 == q1 == F(3, 8), "two-cycle return product")
    check(sum(bound0) == F(14, 5) and sum(bound1) == F(12, 5), "two-cycle columns")
    check(max(map(sum, (bound0, bound1))) == F(14, 5), "two-cycle norm")
    completed = ((0, 1), (0, 1))
    old = max(sum(column_bound(completed, budgets, j)[0]) for j in range(2))
    check(old == 6, "diagonal-completion comparison")
    check(sum(bound0) != F(7, 2), "root-loop denominator mutant escaped")
    dag = ((1,), (2,), ())
    dag_r = (F(1, 2), F(3, 4), F(1, 4))
    check(max(sum(column_bound(dag, dag_r, j)[0]) for j in range(3)) == F(17, 8),
          "acyclic exact norm")
    check(all(column_bound(dag, dag_r, j)[2] == 0 for j in range(3)), "acyclic return")
    figure8 = ((1, 2), (0,), (3,), (0,))
    r8 = (F(1, 2), F(1, 10), F(9, 10), F(9, 10))
    bound8, _, q8 = column_bound(figure8, r8, 0)
    check(q8 == F(81, 200) and sum(bound8) == F(562, 119), "weighted return cycle")
    best8, count8 = policy_maxima(figure8, r8)
    check(tuple(best8[i][0] for i in range(4)) == bound8, "figure-eight oracle")
    check(count8 == 24 and q8 != r8[0] * r8[1], "shortest-cycle mutant escaped")
    # A cycle elsewhere cannot be used as this root's return factor.
    disconnected = ((1,), (), (2,))
    check(column_bound(disconnected, (F(1, 2),) * 3, 0)[2] == 0,
          "unrelated cycle contaminated root")
    return dict(two_cycle_norm="14/5", diagonal_completion_norm="6",
                acyclic_norm="17/8", longer_return_column="562/119")


def failure_controls() -> int:
    graph, budgets = ((1,), (0,)), (F(1, 2), F(3, 4))
    invalid = [lambda: column_bound((), (), 0),
               lambda: column_bound(graph, (F(1), F(1, 2)), 0),
               lambda: column_bound(graph, (F(0), F(1, 2)), 0),
               lambda: column_bound(graph, (F(-1, 2), F(1, 2)), 0),
               lambda: column_bound(graph, (0.5, F(1, 2)), 0),
               lambda: column_bound(((1, 1), (0,)), budgets, 0),
               lambda: column_bound(((2,), (0,)), budgets, 0),
               lambda: column_bound(graph, budgets, 2)]
    for call in invalid:
        reject(call, "invalid graph/budget/root")
    matrix = attaining_matrix(graph, budgets, 0)
    matrix[0][0] = F(1, 10)
    matrix[0][1] = F(0)
    reject(lambda: validate_matrix(matrix, graph, budgets), "forbidden diagonal")
    matrix[0][0], matrix[0][1] = F(0), F(3, 4)
    reject(lambda: validate_matrix(matrix, graph, budgets), "overspent row")
    return len(invalid) + 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    counts = exhaustive_checks()
    fixtures = fixture_checks()
    counts['rejection_controls'] = failure_controls()
    package = Path(__file__).resolve().parent
    names = ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    receipt = dict(status='PASS_SUPPORT_CYCLE_RESOLVENT', counts=counts,
                   fixtures=fixtures, source_sha256=hashes,
                   scope='Exact finite corroboration; the universal result is the written proof.')
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.receipt is not None:
        target = args.receipt.resolve()
        if target.is_relative_to(package.parents[1]):
            raise ValueError('receipt must be outside the checkout or export')
        with target.open('x', encoding='utf-8') as stream:
            check(stream.write(rendered) == len(rendered), 'partial receipt write')
    print(rendered, end='')


if __name__ == '__main__':
    main()
