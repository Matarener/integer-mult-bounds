#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite corroboration of the transported-coframe hardness reduction.

Produced by Nick Petalas. The universal reduction is proved in PROOF.md.
No predecessor verifier, optimizer, numerical solver or external module is used.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
I = (Fraction(0), Fraction(1))
HALF_PI = (Fraction(1, 2), Fraction(-1, 2))
IDENTITY = ((ONE, ZERO), (ZERO, ONE))
FOURIER = ((HALF_PI, HALF_PI),
           (HALF_PI, (-HALF_PI[0], -HALF_PI[1])))
MAX_VERTICES = 5


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def multiply(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def scale(a, matrix):
    return tuple(tuple(multiply(a, x) for x in row) for row in matrix)


def matrix_product(a, b):
    return tuple(tuple(add(multiply(a[r][0], b[0][c]),
                           multiply(a[r][1], b[1][c]))
                       for c in range(2)) for r in range(2))


def apply(matrix, vector):
    return tuple(add(multiply(row[0], vector[0]),
                     multiply(row[1], vector[1])) for row in matrix)


def gaussian_rank(matrix):
    """One-axis Clifford rank, classified by its computational support."""
    support = tuple(tuple(x != ZERO for x in row) for row in matrix)
    rows = tuple(sum(row) for row in support)
    cols = tuple(sum(support[r][c] for r in range(2)) for c in range(2))
    if rows == cols == (1, 1):
        return 0
    require(rows == cols == (2, 2), "Not an admitted one-axis support")
    return 1


def transitions():
    inverse = scale(I, FOURIER)
    require(matrix_product(FOURIER, inverse) == IDENTITY, "Wrong inverse")
    require(matrix_product(FOURIER, FOURIER) == scale((0, -1), IDENTITY),
            "The Fourier square must retain its scalar phase")
    charts, inverses = (IDENTITY, FOURIER), (IDENTITY, inverse)
    tables = tuple(tuple(matrix_product(matrix_product(charts[b], FOURIER),
                                         inverses[a])
                         for b in range(2)) for a in range(2))
    ranks = tuple(tuple(gaussian_rank(tables[a][b]) for b in range(2))
                  for a in range(2))
    require(ranks == ((1, 0), (0, 1)), "Incorrect twisted rank table")
    boundary = tuple(gaussian_rank(charts[a]) + gaussian_rank(inverses[a])
                     for a in range(2))
    require(boundary == (0, 2), "Both boundary adapters must be charged")
    return tables, ranks, boundary


def validate_graph(n, edges):
    require(type(n) is int and 1 <= n <= MAX_VERTICES, "Vertex capacity")
    require(type(edges) is tuple and len(edges) <= n * (n - 1) // 2,
            "Edge capacity")
    for edge in edges:
        require(type(edge) is tuple and len(edge) == 2, "Edge shape")
        u, v = edge
        require(type(u) is type(v) is int and 0 <= u < v < n,
                "Use distinct in-range vertices in increasing order")
    require(len(set(edges)) == len(edges), "Duplicate edge")


def rank_bill(n, edges, bits, ranks, boundary, repetitions=None):
    validate_graph(n, edges)
    require(type(bits) is tuple and len(bits) == n
            and all(type(b) is int and b in (0, 1) for b in bits),
            "Invalid coframe choices")
    repeats = 2 * n + 1 if repetitions is None else repetitions
    require(type(repeats) is int and 1 <= repeats <= 2 * n + 1,
            "Repetition capacity")
    return repeats * sum(ranks[bits[u]][bits[v]] for u, v in edges) + sum(
        boundary[b] for b in bits)


def small_graph_census(ranks, boundary):
    counts = {"graphs": 0, "assignments": 0, "decision_thresholds": 0}
    examples = {}
    for n in range(1, MAX_VERTICES + 1):
        possible = tuple(combinations(range(n), 2))
        assignments = tuple(product(range(2), repeat=n))
        for graph_mask in range(1 << len(possible)):
            edges = tuple(edge for j, edge in enumerate(possible)
                          if graph_mask & (1 << j))
            best, largest_cut = None, 0
            max_cut_small_side = n
            for bits in assignments:
                crossing = sum(bits[u] != bits[v] for u, v in edges)
                bill = rank_bill(n, edges, bits, ranks, boundary)
                require(bill == (2 * n + 1) * (len(edges) - crossing)
                        + 2 * sum(bits), "Literal rank invoice disagrees")
                best = bill if best is None else min(best, bill)
                if crossing > largest_cut:
                    largest_cut, max_cut_small_side = crossing, sum(bits)
                elif crossing == largest_cut:
                    max_cut_small_side = min(max_cut_small_side, sum(bits))
                counts["assignments"] += 1
            require(best // (2 * n + 1) == len(edges) - largest_cut,
                    "The rank optimum does not recover the maximum cut")
            require(best % (2 * n + 1) == 2 * max_cut_small_side,
                    "Boundary-charge remainder disagrees")
            for threshold in range(len(edges) + 2):
                bound = (2 * n + 1) * (len(edges) - threshold) + 2 * n
                require((best <= bound) == (largest_cut >= threshold),
                        "Decision reduction disagrees")
                counts["decision_thresholds"] += 1
            counts["graphs"] += 1
            if len(edges) == len(possible):
                examples[f"K{n}"] = {"maximum_cut": largest_cut,
                                      "minimum_rank_bill": best}
    return counts, examples


def run_word(n, edges, bits, column, physical, bad_inverse=False,
             discard_scalar=False):
    """Literal Gaussian-rational action on one arbitrary-input basis column."""
    state = [[ZERO, ZERO] for _ in range(n)]
    state[column // 2][column % 2] = ONE
    inverse = FOURIER if bad_inverse else scale(I, FOURIER)
    if physical:
        for v in range(n):
            if bits[v]:
                state[v] = list(apply(FOURIER, state[v]))
    for u, v in edges:
        for _ in range(2 * n + 1):
            response = tuple(state[u])
            if physical and bits[u]:
                response = apply(scale(I, FOURIER), response)
            response = apply(FOURIER, response)
            if physical and bits[v]:
                response = apply(FOURIER, response)
            if discard_scalar and physical and bits[v] and not bits[u]:
                response = tuple(state[u])
            state[v] = [add(state[v][j], response[j]) for j in range(2)]
    if physical:
        for v in range(n):
            if bits[v]:
                state[v] = list(apply(inverse, state[v]))
    return state


def endpoint_census():
    counts = {"complete_word_columns": 0, "scalar_output_equalities": 0}
    for n in range(1, 4):
        possible = tuple(combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            edges = tuple(e for j, e in enumerate(possible) if mask & (1 << j))
            reference = tuple(run_word(n, edges, (0,) * n, j, False)
                              for j in range(2 * n))
            for bits in product(range(2), repeat=n):
                for j in range(2 * n):
                    require(run_word(n, edges, bits, j, True) == reference[j],
                            "The complete phase-exact endpoint changed")
                    counts["complete_word_columns"] += 1
                    counts["scalar_output_equalities"] += 2 * n
    return counts


def rejection_controls(ranks, boundary):
    invalid = ((True, ()), (0, ()), (6, ()), (2, ((0, 0),)),
               (2, ((1, 0),)), (2, ((0, 2),)),
               (3, ((0, 1), (0, 1))))
    for n, edges in invalid:
        try:
            validate_graph(n, edges)
        except ValueError:
            continue
        raise ValueError("An invalid graph was accepted")
    triangle = ((0, 1), (0, 2), (1, 2))
    choices = tuple(product(range(2), repeat=3))
    correct = min(rank_bill(3, triangle, b, ranks, boundary) for b in choices)
    require(correct == 9, "Triangle optimum")
    for altered in ((0, 0), (0, 1)):
        require(min(rank_bill(3, triangle, b, ranks, altered) for b in choices)
                != correct, "Missing adapter was invisible")
    untwisted = ((0, 1), (1, 0))
    require(min(rank_bill(3, triangle, b, untwisted, boundary)
                for b in choices) != correct, "Missing logical transport")
    too_small = min(rank_bill(3, triangle, b, ranks, boundary, 1) for b in choices)
    require(too_small // 1 != 1, "Insufficient replication was invisible")
    require(run_word(1, (), (1,), 0, True, bad_inverse=True)
            != run_word(1, (), (0,), 0, False), "Wrong inverse was invisible")
    require(run_word(2, ((0, 1),), (0, 1), 0, True, discard_scalar=True)
            != run_word(2, ((0, 1),), (0, 0), 0, False),
            "Discarded scalar phase was invisible")
    for b in choices:
        require(sum(b[u] == b[v] for u, v in triangle) % 2 == 1,
                "A frustrated triangle became switchable")
    return {"invalid_graphs_rejected": len(invalid),
            "hypothesis_mutants_detected": 6, "triangle_complements": 8}


def main():
    _, ranks, boundary = transitions()
    counts, examples = small_graph_census(ranks, boundary)
    counts.update(endpoint_census())
    counts.update(rejection_controls(ranks, boundary))
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    print(json.dumps({"status": "PASS_TRANSPORTED_COFRAME_HARDNESS",
                      "counts": counts, "complete_graphs": examples,
                      "rank_table": ranks, "boundary_table": boundary,
                      "package_sha256": hashes}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
