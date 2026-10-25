#!/usr/bin/env python3
"""Exact recognition of prime-field Frobenius-truncated algebras.

The input structure constants have convention table[i][j][k] = coefficient
of basis vector k in basis_i * basis_j. The basis need not contain the unit.
Integer coefficients are reduced modulo p. Malformed input raises ValueError;
a well-formed table outside the target class returns status="rejected".

An accepted result includes an explicit change of basis, with transporter
stored as a list of columns and inverse stored as matrix rows. Exponent tuples
are in lexicographic order, with their last coordinate varying fastest.
validate_witness checks that certificate without running the recognition flag.

Only Python's standard library is used. Primality uses trial division: the
fixed-prime recognition algorithm is polynomial in the algebra dimension,
but this primality check is not polynomial in the bit length of a variable p.
"""

from itertools import product
from math import isqrt


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _input(p, table):
    if not _integer(p) or p < 2:
        raise ValueError("p must be a prime integer")
    if p != 2 and (p % 2 == 0 or any(p % d == 0 for d in range(3, isqrt(p) + 1, 2))):
        raise ValueError("p must be prime")
    if not isinstance(table, (list, tuple)) or not table:
        raise ValueError("table must have positive dimension")
    n = len(table)
    normalized = []
    for plane in table:
        if not isinstance(plane, (list, tuple)) or len(plane) != n:
            raise ValueError("table must have shape n by n by n")
        result_plane = []
        for row in plane:
            if not isinstance(row, (list, tuple)) or len(row) != n:
                raise ValueError("table must have shape n by n by n")
            if any(not _integer(value) for value in row):
                raise ValueError("structure constants must be integers")
            result_plane.append([value % p for value in row])
        normalized.append(result_plane)
    return normalized


def _basis(n):
    return [[int(i == j) for i in range(n)] for j in range(n)]


def _multiply(left, right, table, p):
    result = [0] * len(table)
    for i, a in enumerate(left):
        if a:
            for j, b in enumerate(right):
                if b:
                    scale = a * b
                    for k, value in enumerate(table[i][j]):
                        result[k] = (result[k] + scale * value) % p
    return result


def _power(value, exponent, unit, table, p):
    result = list(unit)
    base = list(value)
    while exponent:
        if exponent & 1:
            result = _multiply(result, base, table, p)
        exponent //= 2
        if exponent:
            base = _multiply(base, base, table, p)
    return result


def _rref(matrix, p, coefficient_columns):
    rows = [[value % p for value in row] for row in matrix]
    pivots = []
    for column in range(coefficient_columns):
        pivot = next((r for r in range(len(pivots), len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        row_index = len(pivots)
        rows[row_index], rows[pivot] = rows[pivot], rows[row_index]
        scale = pow(rows[row_index][column], -1, p)
        rows[row_index] = [(scale * value) % p for value in rows[row_index]]
        for r, row in enumerate(rows):
            if r != row_index and row[column]:
                scale = row[column]
                rows[r] = [(a - scale * b) % p for a, b in zip(row, rows[row_index])]
        pivots.append(column)
        if len(pivots) == len(rows):
            break
    return rows, pivots


def _kernel(columns, p):
    n = len(columns)
    rows, pivots = _rref(list(map(list, zip(*columns))), p, n)
    result = []
    for free in range(n):
        if free not in pivots:
            vector = [0] * n
            vector[free] = 1
            for r, pivot in enumerate(pivots):
                vector[pivot] = -rows[r][free] % p
            result.append(vector)
    return result


def _add_column(echelon, vector, p):
    """Extend a column span in place; report whether its dimension increased."""
    reduced = [value % p for value in vector]
    for pivot in sorted(echelon):
        if reduced[pivot]:
            scale = reduced[pivot]
            reduced = [(a - scale * b) % p for a, b in zip(reduced, echelon[pivot])]
    pivot = next((i for i, value in enumerate(reduced) if value), None)
    if pivot is None:
        return False
    scale = pow(reduced[pivot], -1, p)
    echelon[pivot] = [(scale * value) % p for value in reduced]
    return True


def _apply(columns, vector, p):
    return [sum(columns[j][i] * vector[j] for j in range(len(columns))) % p
            for i in range(len(columns))]


def _inverse(columns, p):
    n = len(columns)
    rows = [[columns[j][i] for j in range(n)] + [int(i == j) for j in range(n)]
            for i in range(n)]
    reduced, pivots = _rref(rows, p, n)
    if len(pivots) != n:
        return None
    return [row[n:] for row in reduced]


def _algebra_error(table, p):
    n = len(table)
    for i in range(n):
        for j in range(i):
            if table[i][j] != table[j][i]:
                return "table is not commutative"
    for i in range(n):
        for j in range(n):
            for k in range(n):
                left = [sum(table[i][j][r] * table[r][k][s] for r in range(n)) % p
                        for s in range(n)]
                right = [sum(table[j][k][r] * table[i][r][s] for r in range(n)) % p
                         for s in range(n)]
                if left != right:
                    return "table is not associative"
    return None


def _recover_unit(table, p):
    n = len(table)
    equations = [[table[i][j][k] for i in range(n)] + [int(j == k)]
                 for j in range(n) for k in range(n)]
    reduced, pivots = _rref(equations, p, n)
    if any(not any(row[:n]) and row[n] for row in reduced):
        return None
    unit = [0] * n
    for r, pivot in enumerate(pivots):
        unit[pivot] = reduced[r][n]
    for vector in _basis(n):
        if _multiply(unit, vector, table, p) != vector:
            return None
        if _multiply(vector, unit, table, p) != vector:
            return None
    return unit


def recognize(p, table):
    """Recognize a tensor product of F_p[x]/(x**(p**h)), and return its witness."""
    table = _input(p, table)
    n = len(table)
    result = {"status": "rejected", "reason": "", "n": n}
    error = _algebra_error(table, p)
    if error is not None:
        result["reason"] = error
        return result
    unit = _recover_unit(table, p)
    if unit is None:
        result["reason"] = "table has no two-sided unit"
        return result

    levels, bound = 0, 1
    while bound < n:
        levels += 1
        bound *= p
    result["frobenius_levels"] = levels
    identity = _basis(n)
    kernels = []
    current = identity
    if levels:
        frobenius = [_power(vector, p, unit, table, p) for vector in identity]
        for _ in range(levels):
            current = [_apply(frobenius, column, p) for column in current]
            kernels.append(_kernel(current, p))
    radical = kernels[-1] if kernels else []
    result["radical_dimension"] = len(radical)
    if len(radical) != n - 1:
        result["reason"] = "Frobenius radical does not have codimension one"
        return result

    quotient_span = {}
    for i, left in enumerate(radical):
        for right in radical[i:]:
            _add_column(quotient_span, _multiply(left, right, table, p), p)
    square_dimension = len(quotient_span)
    result["radical_square_dimension"] = square_dimension
    result["tangent_dimension"] = len(radical) - square_dimension
    heights, generators, flag_dimensions = [], [], [0]
    for e, kernel in enumerate(kernels, 1):
        for vector in kernel:
            if _add_column(quotient_span, vector, p):
                heights.append(e)
                generators.append(list(vector))
        flag_dimensions.append(len(quotient_span) - square_dimension)
    result["flag_dimensions"] = flag_dimensions
    result["heights"] = heights
    predicted_dimension = p ** sum(heights)
    result["predicted_dimension"] = predicted_dimension
    if predicted_dimension != n:
        result["reason"] = "adapted Frobenius heights predict a different dimension"
        return result

    sizes = [p ** height for height in heights]
    exponents = [list(exponent) for exponent in product(*(range(size) for size in sizes))]
    powers = [[_power(generator, exponent, unit, table, p) for exponent in range(size)]
              for generator, size in zip(generators, sizes)]
    columns = []
    for exponent in exponents:
        column = list(unit)
        for i, value in enumerate(exponent):
            column = _multiply(column, powers[i][value], table, p)
        columns.append(column)
    inverse = _inverse(columns, p)
    if inverse is None:
        raise RuntimeError("recognition criterion passed but monomial columns are singular")
    result.update({
        "status": "accepted",
        "reason": "verified monomial basis for the recovered Frobenius heights",
        "generators": generators,
        "unit": unit,
        "monomial_exponents": exponents,
        "transporter": columns,
        "inverse": inverse,
    })
    validate_witness(p, table, result)
    return result


def _witness_vectors(value, count, n, p, name):
    if not isinstance(value, list) or len(value) != count:
        raise ValueError(name + " has the wrong number of vectors")
    for vector in value:
        if not isinstance(vector, list) or len(vector) != n:
            raise ValueError(name + " has a vector of the wrong dimension")
        if any(not _integer(a) or not 0 <= a < p for a in vector):
            raise ValueError(name + " must use canonical prime-field coordinates")
    return value


def validate_witness(p, table, witness):
    """Independently check a monomial transporter; return True or raise ValueError.

    The checker does not use Frobenius kernels, radical dimensions, flag
    dimensions or the recognition decision. It verifies the declared model's
    relations, all monomial columns, both inverse identities, and every basis
    product in the source and target. Diagnostic fields are not certificate
    premises and are deliberately ignored.
    """
    table = _input(p, table)
    n = len(table)
    if not isinstance(witness, dict) or witness.get("status") != "accepted":
        raise ValueError("witness must declare an accepted certificate")
    if not _integer(witness.get("n")) or witness["n"] != n:
        raise ValueError("witness dimension does not match table")
    error = _algebra_error(table, p)
    if error is not None:
        raise ValueError(error)
    unit = _witness_vectors([witness.get("unit")], 1, n, p, "unit")[0]
    for vector in _basis(n):
        if _multiply(unit, vector, table, p) != vector or _multiply(vector, unit, table, p) != vector:
            raise ValueError("witness unit does not satisfy both identity laws")
    heights = witness.get("heights")
    if not isinstance(heights, list) or any(not _integer(h) or h < 1 for h in heights):
        raise ValueError("heights must be positive integers")
    # This bound also avoids constructing a maliciously large p**h value.
    maximum_height, bound = 0, 1
    while bound < n:
        maximum_height += 1
        bound *= p
    if any(h > maximum_height for h in heights) or len(heights) > n:
        raise ValueError("heights exceed the model dimension")
    if p ** sum(heights) != n:
        raise ValueError("model dimension does not match table")
    generators = _witness_vectors(witness.get("generators"), len(heights), n, p, "generators")
    columns = _witness_vectors(witness.get("transporter"), n, n, p, "transporter")
    inverse = _witness_vectors(witness.get("inverse"), n, n, p, "inverse")
    sizes = [p ** height for height in heights]
    exponents = [list(exponent) for exponent in product(*(range(size) for size in sizes))]
    supplied_exponents = witness.get("monomial_exponents")
    if not isinstance(supplied_exponents, list) or len(supplied_exponents) != n:
        raise ValueError("monomial exponents have the wrong length")
    for actual, expected in zip(supplied_exponents, exponents):
        if not isinstance(actual, list) or any(not _integer(a) for a in actual) or actual != expected:
            raise ValueError("monomial exponents are not the declared lexicographic order")
    zero = [0] * n
    powers = []
    for generator, height, size in zip(generators, heights, sizes):
        if _power(generator, size, unit, table, p) != zero:
            raise ValueError("generator violates its truncation relation")
        if _power(generator, p ** (height - 1), unit, table, p) == zero:
            raise ValueError("generator has a smaller Frobenius height")
        powers.append([_power(generator, a, unit, table, p) for a in range(size)])
    for column, exponent in zip(columns, exponents):
        expected = list(unit)
        for i, a in enumerate(exponent):
            expected = _multiply(expected, powers[i][a], table, p)
        if column != expected:
            raise ValueError("transporter column does not equal its generator monomial")
    for i in range(n):
        for j in range(n):
            if sum(columns[k][i] * inverse[k][j] for k in range(n)) % p != int(i == j):
                raise ValueError("transporter times inverse is not the identity")
            if sum(inverse[i][k] * columns[j][k] for k in range(n)) % p != int(i == j):
                raise ValueError("inverse times transporter is not the identity")
    monomial_index = {tuple(exponent): i for i, exponent in enumerate(exponents)}
    for i, a in enumerate(exponents):
        for j, b in enumerate(exponents):
            combined = tuple(x + y for x, y in zip(a, b))
            expected = zero if any(x >= size for x, size in zip(combined, sizes)) else columns[monomial_index[combined]]
            if _multiply(columns[i], columns[j], table, p) != expected:
                raise ValueError("transporter fails a model basis-product identity")
    return True
