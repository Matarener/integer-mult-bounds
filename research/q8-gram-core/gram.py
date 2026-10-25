"""Construct the call core and check the exact negative-target criterion.

Nick Petalas, Apache-2.0.
"""

from linear import column, factor, matrix, multiply, rank, require
from model import Gate, binary_right, endpoint, label_sum, validate


def normal_form(rows, labels):
    n = len(rows)
    matrix(rows, n)
    require(len(labels) == n and all(label in (2, 4) for label in labels), "labels")
    require(all((rows[j] >> j) & 1 for j in range(n)), "Gram diagonal")
    x, y = factor(rows)
    gates = tuple(Gate(label, column(x, j), y[j]) for j, label in enumerate(labels))
    validate(gates, len(x))
    return gates, len(x)


def ambient_gates(rows, labels):
    normal_form(rows, labels)  # Validate the matrix and labels before construction.
    return tuple(Gate(label, column(rows, j), 1 << j) for j, label in enumerate(labels))


def negative_target(rows, labels, i_targets, j_targets):
    """Exact existential criterion; this checks a candidate, not every candidate."""
    gates = ambient_gates(rows, labels)
    n = len(rows)
    require(type(i_targets) is int and type(j_targets) is int, "target type")
    require(0 <= i_targets <= n and 0 <= j_targets <= n, "target count")
    pi, pj = label_sum(gates, n, 2), label_sum(gates, n, 4)
    pim, pjm = multiply(pi, rows), multiply(pj, rows)
    if rank(pim) != i_targets or rank(pjm) != j_targets:
        return False
    zero = (0,) * n
    if multiply(pi, pim) != pim or multiply(pj, pjm) != pjm:
        return False
    if multiply(pi, pjm) != zero or multiply(pj, pim) != zero:
        return False
    actual = binary_right(endpoint(gates, n), rows, n)
    expected = tuple(tuple(
        ((rows[a] >> b) & 1)
        ^ ((1 ^ (1 << 3)) if (pim[a] >> b) & 1 else 0)
        ^ ((1 ^ (1 << 5)) if (pjm[a] >> b) & 1 else 0)
        for b in range(n)) for a in range(n))
    return actual == expected
