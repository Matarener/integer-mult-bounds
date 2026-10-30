#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact local-to-global kernel certificates for a routed observation block.

Clear1nsight, with substantial OpenAI assistance. Classical sheaf/coset and
integer-fibre methods are credited in PROOF.md. This is not a native program.
"""
from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return sha256(canonical(value)).hexdigest()


def apply(columns: tuple[int, ...], vector: int) -> int:
    out = 0
    while vector:
        low = vector & -vector
        out ^= columns[low.bit_length() - 1]
        vector ^= low
    return out


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    """The product left*right, represented by columns over F2."""
    return tuple(apply(left, column) for column in right)


def closure(generators: list[tuple[int, ...]], cap: int = 10000) -> list[tuple[int, ...]]:
    need(bool(generators), "nonempty generating set")
    identity = tuple(1 << i for i in range(len(generators[0])))
    found = {identity}
    queue = deque([identity])
    while queue:
        element = queue.popleft()
        for generator in generators:
            other = compose(element, generator)
            if other not in found:
                need(len(found) < cap, "group closure exceeds declared cap")
                found.add(other)
                queue.append(other)
    return sorted(found)


def rref(matrix: list[list[Q]]) -> tuple[list[list[Q]], list[int]]:
    if not matrix:
        return [], []
    width = len(matrix[0])
    need(all(len(row) == width for row in matrix), "rectangular matrix")
    work = [[Q(x) for x in row] for row in matrix]
    pivots: list[int] = []
    for column in range(width):
        pivot = next((i for i in range(len(pivots), len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        at = len(pivots)
        work[at], work[pivot] = work[pivot], work[at]
        divisor = work[at][column]
        work[at] = [x / divisor for x in work[at]]
        for i in range(len(work)):
            if i != at and work[i][column]:
                scalar = work[i][column]
                work[i] = [x - scalar * y for x, y in zip(work[i], work[at])]
        pivots.append(column)
        if len(pivots) == len(work):
            break
    return work, pivots


def rank(matrix: list[list[Q]]) -> int:
    return len(rref(matrix)[1])


def coset_classes(routes: list[tuple[int, ...]], subgroup: set[tuple[int, ...]]) -> list[list[int]]:
    """Partition involutory ports by H*rho_p = H*rho_q.

    This is equivalent to rho_p*rho_q in H. Test every pair, including both
    directions and diagonal, rather than treating a union-find guess as proof.
    """
    width = len(routes[0])
    identity = tuple(1 << i for i in range(width))
    need(all(compose(route, route) == identity for route in routes), "routes must be involutions")
    classes: list[list[int]] = []
    assignment = []
    for p, route in enumerate(routes):
        found = next((j for j, block in enumerate(classes)
                      if compose(route, routes[block[0]]) in subgroup), None)
        if found is None:
            found = len(classes)
            classes.append([])
        classes[found].append(p)
        assignment.append(found)
    for p in range(len(routes)):
        for q in range(len(routes)):
            need((compose(routes[p], routes[q]) in subgroup) == (assignment[p] == assignment[q]),
                 "right-coset equivalence failed")
    return classes


def analyse(rows: list[list[Q]], routes: list[tuple[int, ...]], triple=(0, 6, 85), cap=10000) -> dict:
    """Compute a finite certificate; fails unless full kernel reduces to triple.

    The proof in PROOF.md, not floating-point rank or toy sampling, lifts these
    exact premises to the full routed kernel over Q and its integer fibre.
    """
    ports = len(routes)
    need(len(rows) == 8 and all(len(row) == ports for row in rows), "eight query rows")
    need(len(set(routes)) == ports, "distinct routes")
    need(rank(rows) == 8, "full old-query rank")
    a, b, c = triple
    need(len(set(triple)) == 3 and all(0 <= p < ports for p in triple), "triple range")
    need(all(row[a] - row[b] - row[c] == 0 for row in rows), "triple relation is (1,-1,-1)")
    need(rank([[row[p] for p in triple] for row in rows]) == 2, "triple rank two")
    generators = [compose(routes[a], routes[b]), compose(routes[a], routes[c])]
    elements = closure(generators, cap)
    subgroup = set(elements)
    classes = coset_classes(routes, subgroup)
    table = []
    for block in classes:
        matrix = [[row[p] for p in block] for row in rows]
        table.append({"ports": block, "rank": rank(matrix)})
    deficient = [entry for entry in table if entry["rank"] != len(entry["ports"])]
    need(deficient == [{"ports": sorted(triple), "rank": 2}],
         "full-block reduction has additional dependent coset classes: " + str(deficient))
    # Build an undirected compatibility graph independently of group closure.
    # Edges say alpha(h)=alpha(h*rho_a*rho_b/c). Keep both directions, with
    # separate endpoint and spanning-tree checks.
    index = {g: i for i, g in enumerate(elements)}
    adjacency = [set() for _ in elements]
    for i, element in enumerate(elements):
        for generator in generators:
            j = index[compose(element, generator)]
            adjacency[i].add(j)
            adjacency[j].add(i)
    start = index[tuple(1 << i for i in range(len(routes[0])))]
    parent = {start: None}
    queue = deque([start])
    tree = []
    while queue:
        i = queue.popleft()
        for j in sorted(adjacency[i]):
            if j not in parent:
                parent[j] = i
                tree.append([i, j])
                queue.append(j)
    need(len(parent) == len(elements) and len(tree) + 1 == len(elements), "compatibility graph connected")
    variables = ports * len(elements)
    old_rank = 8 * len(elements)
    ambient_old_kernel = variables - old_rank
    return {
        "schema_version": 1,
        "status": "PASS_CENTRE_SHEAF_FIBRE",
        "ports": ports,
        "active_dimension": len(routes[0]),
        "owners": len(elements),
        "right_coset_classes": table,
        "class_size_histogram": {str(k): v for k, v in sorted(Counter(map(len, classes)).items())},
        "deficient_coset_classes": deficient,
        "compatibility_vertices": len(elements),
        "compatibility_edges": sum(map(len, adjacency)) // 2,
        "spanning_tree_edges": len(tree),
        "spanning_tree_sha256": digest(tree),
        "subgroup_sha256": digest(elements),
        "geometry_sha256": digest({"rows": [[str(x) for x in row] for row in rows], "routes": routes}),
        "full_variables": variables,
        "old_rank": old_rank,
        "old_kernel_dimension": ambient_old_kernel,
        "full_joint_kernel_dimension": 1,
        "additional_linear_observations_required": ambient_old_kernel - 1,
        "primitive_move_positive_entries": len(elements),
        "primitive_move_negative_entries": 2 * len(elements),
        "primitive_move_support": 3 * len(elements),
        "constant_count_constraint_kills_kernel": True,
        "scope": "Fixed H block and all declared ports, exact scalar observations only; no native tariff or physical caller.",
    }
