"""Exact basic solutions over the toolkit's Mersenne field.

The first independent columns are the pivots and all free variables are zero.
This is the same convention as the retained Gauss-Jordan solver.
"""

import numpy as np

P = 2147483647
MAX_DIMENSION = 4096


def eliminate(work, variables):
    """Normalize pivots and eliminate below them; return their column indices."""
    rows = work.shape[0]
    pivots = []
    for column in range(variables):
        row = len(pivots)
        if row == rows:
            break
        nonzero = np.flatnonzero(work[row:, column])
        if nonzero.size == 0:
            continue
        selected = row + int(nonzero[0])
        if selected != row:
            work[[row, selected]] = work[[selected, row]]
        inverse = pow(int(work[row, column]), P - 2, P)
        work[row, column:] = work[row, column:] * inverse % P
        if work[row, column] != 1:
            raise ArithmeticError("pivot normalization failed")
        below = row + 1 + np.flatnonzero(work[row + 1:, column])
        factors = work[below, column].copy()
        work[below, column:] = (
            work[below, column:]
            - factors[:, None] * work[row, column:][None, :] % P
        ) % P
        pivots.append(column)
    return pivots


def solve(matrix, rhs):
    """Return the canonical basic solution, or None for an inconsistent system.

    Integer matrices and vectors must have compatible shapes, with each matrix
    dimension at most 4096. Inputs are copied and reduced modulo P.
    """
    matrix = np.asarray(matrix)
    rhs = np.asarray(rhs)
    if matrix.ndim != 2 or rhs.ndim != 1:
        raise ValueError("expected a matrix and a vector")
    rows, variables = matrix.shape
    if rhs.shape != (rows,) or max(rows, variables) > MAX_DIMENSION:
        raise ValueError("incompatible or oversized system")
    if matrix.dtype.kind not in "iu" or rhs.dtype.kind not in "iu":
        raise ValueError("integer arrays required")
    # Widen narrow types first; retain unsigned values until after reduction.
    matrix_type = np.uint64 if matrix.dtype.kind == "u" else np.int64
    rhs_type = np.uint64 if rhs.dtype.kind == "u" else np.int64
    matrix = (matrix.astype(matrix_type, copy=False) % P).astype(np.int64, copy=False)
    rhs = (rhs.astype(rhs_type, copy=False) % P).astype(np.int64, copy=False)
    work = np.column_stack((matrix, rhs))
    pivots = eliminate(work, variables)
    if np.any(work[len(pivots):, variables]):
        return None
    solution = np.zeros(variables, dtype=np.int64)
    for row in range(len(pivots) - 1, -1, -1):
        column = pivots[row]
        terms = work[row, column + 1: variables] * solution[column + 1:] % P
        # At most 4096 reduced summands; their sum fits signed int64.
        solution[column] = (int(work[row, variables]) - int(terms.sum())) % P
    return solution
