"""Check certificates directly against original matrices, without the solver.

Produced by Nick Petalas. Apache-2.0.
"""

from linear import (block_at, inverse, matrix, multiply, paired, power_two,
                    require, valuation)


def check_eigenbasis(anchors, basis):
    size = len(anchors)
    basis = matrix(basis, size)
    inverse(basis)
    for i, projector in enumerate(anchors):
        expected = tuple(tuple(basis[r][c] if c == i else 0 for c in range(size))
                         for r in range(size))
        require(multiply(projector, basis) == expected, "basis does not diagonalize anchors")
    return basis


def check_potential(basis, applied, exponents):
    size = len(basis)
    require(isinstance(exponents, (list, tuple)) and len(exponents) == size,
            "potential size")
    require(all(type(x) is int and abs(x) <= 100000 for x in exponents),
            "invalid potential")
    scaled = tuple(tuple(basis[i][j] * power_two(exponents[j]) for j in range(size))
                   for i in range(size))
    change = paired(scaled)
    undo = inverse(change)
    for value in applied:
        changed = multiply(multiply(undo, value), change)
        require(all(not x or valuation(x) >= 0 for row in changed for x in row),
                "nonintegral applied matrix")
    return True


def check_cycle(basis, applied, entries):
    size = len(basis)
    require(isinstance(entries, (list, tuple)) and 1 <= len(entries) <= size,
            "cycle length")
    change = paired(basis)
    undo = inverse(change)
    first, previous, total = None, None, 0
    for entry in entries:
        require(isinstance(entry, (list, tuple)) and len(entry) == 3
                and all(type(x) is int for x in entry), "cycle entry shape")
        index, row, column = entry
        require(0 <= index < len(applied) and 0 <= row < 2 * size
                and 0 <= column < 2 * size, "cycle index")
        changed = multiply(multiply(undo, applied[index]), change)
        value = changed[row][column]
        require(value != 0, "cycle uses zero entry")
        source, target = column % size, row % size
        if first is None:
            first = source
        else:
            require(source == previous, "cycle disconnected")
        previous, total = target, total + valuation(value)
    require(previous == first and total < 0, "cycle not closed and negative")
    return False


def check(anchors, applied, certificate):
    require(isinstance(anchors, (list, tuple)) and 1 <= len(anchors) <= 8,
            "anchor count")
    size = len(anchors)
    require(isinstance(applied, (list, tuple)) and 1 <= len(applied) <= 64,
            "applied count")
    anchors = tuple(matrix(p, size) for p in anchors)
    applied = tuple(matrix(g, 2 * size) for g in applied)
    require(isinstance(certificate, dict), "certificate must be a mapping")
    basis = check_eigenbasis(anchors, certificate.get("basis"))
    blocks = tuple(block_at(g, r, c, size) for g in applied for r in range(2)
                   for c in range(2))
    require(all(p in blocks for p in anchors), "unapplied anchor")
    kind = certificate.get("kind")
    if kind == "potential":
        return check_potential(basis, applied, certificate.get("exponents"))
    require(kind == "cycle", "unknown certificate kind")
    return check_cycle(basis, applied, certificate.get("entries"))
