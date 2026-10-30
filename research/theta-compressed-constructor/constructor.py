"""Exact compressed coordinate sharing on theta(2,3,3), Apache-2.0."""

from fractions import Fraction
from itertools import combinations, product


EDGES = ((0, 2), (2, 1), (0, 3), (3, 4), (4, 1), (0, 5), (5, 6), (6, 1))
ODD_CYCLES = ((0, 1, 4, 3, 2), (0, 1, 7, 6, 5))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integers(values: tuple, size: int) -> None:
    need(isinstance(values, tuple) and len(values) == size, "wrong tuple shape")
    need(all(type(x) is int and x >= 0 for x in values), "invalid nonnegative integer")


def doubled_inverse(matrix: tuple) -> tuple | None:
    """Return 2*A^-1, or None for a singular incidence submatrix."""
    n = len(matrix)
    need(1 <= n <= 7, "inverse dimension")
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for i in range(n):
            if i != column:
                scale = rows[i][column]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[column])]
    result = tuple(tuple(2 * x for x in row[n:]) for row in rows)
    need(all(x.denominator == 1 for row in result for x in row), "non-half-integral basis")
    return tuple(tuple(int(x) for x in row) for row in result)


def compile_templates() -> tuple:
    """A fixed graph-only enumeration; never loops over payload coordinates."""
    templates = []
    for size in range(1, 8):
        for edge_ids in combinations(range(8), size):
            for vertex_ids in combinations(range(7), size):
                matrix = tuple(tuple(int(v in EDGES[e]) for e in edge_ids)
                               for v in vertex_ids)
                inverse = doubled_inverse(matrix)
                if inverse is not None:
                    templates.append((edge_ids, vertex_ids, inverse))
    need(len(templates) <= 6435, "template enumeration bound")
    return tuple(templates)


def covers() -> tuple:
    return tuple(y for y in product(range(3), repeat=7)
                 if all(y[u] + y[v] >= 2 for u, v in EDGES))


def fractional_optimum(widths: tuple, templates: tuple) -> tuple:
    integers(widths, 7)
    best = (0,) * 8
    for edge_ids, vertex_ids, inverse in templates:
        values = tuple(sum(c * widths[v] for c, v in zip(row, vertex_ids))
                       for row in inverse)
        if min(values) < 0:
            continue
        candidate = [0] * 8
        for edge, value in zip(edge_ids, values):
            candidate[edge] = value
        if any(sum(candidate[e] for e in range(8) if v in EDGES[e]) > 2 * widths[v]
               for v in range(7)):
            continue
        if sum(candidate) > sum(best):
            best = tuple(candidate)
    dual = min(covers(), key=lambda y: sum(a * b for a, b in zip(widths, y)))
    need(sum(best) == sum(a * b for a, b in zip(widths, dual)), "primal/dual gap")
    return best, dual


def round_cycle(doubled: tuple) -> tuple:
    integers(doubled, 8)
    odd = {e for e in range(8) if doubled[e] % 2}
    result = [x // 2 for x in doubled]
    if odd:
        cycle = next((cycle for cycle in ODD_CYCLES if set(cycle) == odd), None)
        need(cycle is not None, "fractional edges are not one odd cycle")
        for position in (1, 3):
            result[cycle[position]] += 1
    return tuple(result)


def validate(widths: tuple, certificate: dict) -> None:
    """Check an integer matching against a half-integral cover upper bound."""
    integers(widths, 7)
    need(type(certificate) is dict and set(certificate) ==
         {"shared", "private", "dual", "rank"}, "certificate fields")
    shared, private, dual = (certificate[key] for key in ("shared", "private", "dual"))
    integers(shared, 8)
    integers(private, 7)
    integers(dual, 7)
    need(all(x <= 2 for x in dual), "dual alphabet")
    need(all(dual[u] + dual[v] >= 2 for u, v in EDGES), "uncovered edge")
    need(all(private[v] + sum(shared[e] for e in range(8) if v in EDGES[e]) == widths[v]
             for v in range(7)), "coordinate capacity equation")
    bound = sum(a * b for a, b in zip(widths, dual)) // 2
    need(sum(shared) == bound, "nonoptimal matching certificate")
    need(type(certificate["rank"]) is int and
         certificate["rank"] == sum(widths) - sum(shared), "wrong fitting rank")


def construct(widths: tuple, templates: tuple) -> dict:
    doubled, dual = fractional_optimum(widths, templates)
    shared = round_cycle(doubled)
    private = tuple(widths[v] - sum(shared[e] for e in range(8) if v in EDGES[e])
                    for v in range(7))
    result = {"shared": shared, "private": private, "dual": dual,
              "rank": sum(widths) - sum(shared)}
    validate(widths, result)
    return result
