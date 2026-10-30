"""Construct a complete paired-lattice certificate in the anchored class.

Produced by Nick Petalas. Apache-2.0.
"""

from linear import (block_at, identity, inverse, matrix, multiply, paired,
                    require, valuation, zero)

MAX_ADDRESS_DIM = 8
MAX_APPLIED = 64


def validate(anchors, applied):
    require(isinstance(anchors, (list, tuple)), "anchor sequence required")
    size = len(anchors)
    require(1 <= size <= MAX_ADDRESS_DIM, "unsupported anchor count")
    require(isinstance(applied, (list, tuple)) and 1 <= len(applied) <= MAX_APPLIED,
            "unsupported applied-matrix count")
    anchors = tuple(matrix(value, size) for value in anchors)
    applied = tuple(matrix(value, 2 * size) for value in applied)
    for i, projector in enumerate(anchors):
        require(multiply(projector, projector) == projector, "anchor not idempotent")
        require(sum(projector[j][j] for j in range(size)) == 1, "anchor not rank one")
        for j, other in enumerate(anchors):
            if i != j:
                require(multiply(projector, other) == zero(size), "anchors not orthogonal")
    total = tuple(tuple(sum(p[i][j] for p in anchors) for j in range(size))
                  for i in range(size))
    require(total == identity(size), "anchors not complete")
    blocks = tuple(block_at(g, r, c, size) for g in applied for r in range(2)
                   for c in range(2))
    require(all(p in blocks for p in anchors), "anchor absent from applied blocks")
    return anchors, applied


def anchor_basis(anchors):
    size = len(anchors)
    columns = []
    for projector in anchors:
        column = next(j for j in range(size) if any(projector[i][j] for i in range(size)))
        columns.append(tuple(projector[i][column] for i in range(size)))
    basis = tuple(tuple(columns[j][i] for j in range(size)) for i in range(size))
    inverse(basis)  # Check the full eigenbasis before graph construction.
    return basis


def edges_for(basis, applied):
    size = len(basis)
    change = paired(basis)
    undo = inverse(change)
    edges = []
    for index, value in enumerate(applied):
        changed = multiply(multiply(undo, value), change)
        for i in range(2 * size):
            for j in range(2 * size):
                if changed[i][j]:
                    edges.append((j % size, i % size, valuation(changed[i][j]), index, i, j))
    return tuple(edges)


def solve_edges(size, edges):
    distances, predecessor = [0] * size, [None] * size
    changed = None
    for _ in range(size):
        changed = None
        for index, (source, target, weight, *_) in enumerate(edges):
            if distances[target] > distances[source] + weight:
                distances[target] = distances[source] + weight
                predecessor[target] = index
                changed = target
        if changed is None:
            return {"kind": "potential", "exponents": [x - distances[0] for x in distances]}
    vertex = changed
    for _ in range(size):
        require(predecessor[vertex] is not None, "broken negative-cycle predecessor")
        vertex = edges[predecessor[vertex]][0]
    start, reverse_cycle = vertex, []
    for _ in range(size):
        index = predecessor[vertex]
        require(index is not None, "broken cycle")
        reverse_cycle.append(index)
        vertex = edges[index][0]
        if vertex == start:
            cycle = list(reversed(reverse_cycle))
            require(sum(edges[index][2] for index in cycle) < 0, "cycle not negative")
            return {"kind": "cycle", "entries": [list(edges[index][3:]) for index in cycle]}
    raise ValueError("negative-cycle extraction exceeded dimension")


def solve(anchors, applied):
    anchors, applied = validate(anchors, applied)
    basis = anchor_basis(anchors)
    certificate = solve_edges(len(anchors), edges_for(basis, applied))
    certificate["basis"] = basis
    return certificate
