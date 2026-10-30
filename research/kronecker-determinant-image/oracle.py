#!/usr/bin/env python3
"""Independent literal stabilizer enumeration on eight bounded prime-field cases.

No determinant-image formula or symmetric-power construction is used. For each
P and R, Gaussian elimination solves both stabilizer equations for Q transpose.
The right Kronecker block convention is A=[I_e 0], B=[0 I_e], tensored with I_r.
New material: apoursh, with substantial OpenAI Codex assistance; Apache-2.0.
"""

from itertools import product


DOMAINS = (
    (1, 1, 2), (1, 1, 3), (1, 1, 5),
    (2, 1, 2), (2, 1, 3),
    (1, 2, 2), (1, 2, 3), (3, 1, 2),
)
MAX_MATRIX_CANDIDATES = 625
MAX_GROUP_SIZE = 480
MAX_PR_PAIRS = 2304


def _determinant(matrix, prime):
    """Determinant by row elimination, including permutation signs."""
    rows = [list(row) for row in matrix]
    size = len(rows)
    value = 1
    for col in range(size):
        pivot = next((i for i in range(col, size) if rows[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            value = -value
        diagonal = rows[col][col]
        value = value * diagonal % prime
        inverse = pow(diagonal, -1, prime)
        for i in range(col + 1, size):
            scale = rows[i][col] * inverse % prime
            for j in range(col, size):
                rows[i][j] = (rows[i][j] - scale * rows[col][j]) % prime
    return value % prime


def _general_linear(size, prime):
    """Enumerate all matrices first; retain precisely nonzero determinants."""
    candidate_count = prime ** (size * size)
    if candidate_count > MAX_MATRIX_CANDIDATES:
        raise ValueError("matrix enumeration exceeds the fixed oracle cap")
    group = []
    for entries in product(range(prime), repeat=size * size):
        matrix = tuple(entries[i * size:(i + 1) * size] for i in range(size))
        determinant = _determinant(matrix, prime)
        if determinant:
            if len(group) >= MAX_GROUP_SIZE:
                raise ValueError("group enumeration exceeds the fixed oracle cap")
            group.append((matrix, determinant))
    return tuple(group)


def _multiply(left, right, prime):
    return tuple(
        tuple(sum(a * b for a, b in zip(row, col)) % prime
              for col in zip(*right))
        for row in left
    )


def _mix(first, second, a, b, prime):
    return tuple(tuple((a * x + b * y) % prime for x, y in zip(row, other))
                 for row, other in zip(first, second))


def _right_slices(index, multiplicity):
    row_count = index * multiplicity
    col_count = (index + 1) * multiplicity
    first = tuple(tuple(int(j == i) for j in range(col_count))
                  for i in range(row_count))
    second = tuple(tuple(int(j == i + multiplicity) for j in range(col_count))
                   for i in range(row_count))
    return first, second


def _solve_unique(coefficients, targets, prime):
    """Solve C X=D by full-column-rank elimination; reject inconsistency."""
    row_count = len(coefficients)
    col_count = len(coefficients[0])
    target_count = len(targets[0])
    width = col_count + target_count
    rows = [list(left + right) for left, right in zip(coefficients, targets)]
    for col in range(col_count):
        pivot = next((i for i in range(col, row_count) if rows[i][col]), None)
        if pivot is None:
            raise RuntimeError("right-pencil stack unexpectedly lacks full rank")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        inverse = pow(rows[col][col], -1, prime)
        rows[col] = [(entry * inverse) % prime for entry in rows[col]]
        for i in range(row_count):
            if i == col:
                continue
            scale = rows[i][col]
            for j in range(width):
                rows[i][j] = (rows[i][j] - scale * rows[col][j]) % prime
    if any(any(row[col_count:]) for row in rows[col_count:]):
        return None
    return tuple(tuple(row[col_count:]) for row in rows[:col_count])


def _candidate(first, second, left, action, prime):
    """Return Q transpose if this P,R pair is a literal tensor stabilizer."""
    (a, b), (c, d) = action
    mixed_first = _mix(first, second, a, b, prime)
    mixed_second = _mix(first, second, c, d, prime)
    top = _multiply(left, mixed_first, prime)
    bottom = _multiply(left, mixed_second, prime)
    right_transpose = _solve_unique(top + bottom, first + second, prime)
    if right_transpose is None:
        return None
    if _determinant(right_transpose, prime) == 0:
        return None
    if (_multiply(_multiply(left, mixed_first, prime), right_transpose, prime)
            != first):
        raise RuntimeError("first literal stabilizer equation failed")
    if (_multiply(_multiply(left, mixed_second, prime), right_transpose, prime)
            != second):
        raise RuntimeError("second literal stabilizer equation failed")
    return right_transpose


def enumerate_image(index, multiplicity, prime):
    """Return the exact determinant image and stabilizer count on a fixed case.

    Full-column-rank stacking makes Q unique for every pair P,R. Thus exhaustive
    P,R enumeration with equation solving counts every stabilizer exactly once.
    This function deliberately rejects every input outside DOMAINS.
    """
    values = (index, multiplicity, prime)
    if any(type(value) is not int for value in values) or values not in DOMAINS:
        raise ValueError("unsupported oracle case; use one of the eight DOMAINS")
    first, second = _right_slices(index, multiplicity)
    left_group = _general_linear(index * multiplicity, prime)
    slice_group = _general_linear(2, prime)
    tested_pairs = len(left_group) * len(slice_group)
    if tested_pairs > MAX_PR_PAIRS:
        raise ValueError("P,R pair enumeration exceeds the fixed oracle cap")
    image = set()
    stabilizer_count = 0
    for left, left_det in left_group:
        for action, action_det in slice_group:
            right_transpose = _candidate(first, second, left, action, prime)
            if right_transpose is not None:
                stabilizer_count += 1
                right_det = _determinant(right_transpose, prime)
                image.add((left_det, right_det, action_det))
    return {
        "index": index,
        "multiplicity": multiplicity,
        "prime": prime,
        "image": tuple(sorted(image)),
        "stabilizer_count": stabilizer_count,
        "tested_pr_pairs": tested_pairs,
        "left_group_size": len(left_group),
        "slice_group_size": len(slice_group),
    }


def report():
    """Replay all eight independent fixed domains without writing any files."""
    return tuple(enumerate_image(*case) for case in DOMAINS)


if __name__ == "__main__":
    import json

    print(json.dumps(report(), sort_keys=True))
