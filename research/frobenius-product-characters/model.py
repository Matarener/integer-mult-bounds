#!/usr/bin/env python3
"""Exact split Frobenius-product character witnesses over prime fields.

Matrices use row-major storage; columns are basis images. Input coordinates
must be canonical integers from 0 through p-1. A table uses table[i][j][k]
for the kth coefficient of e_i*e_j. Certificates use T(Ua,Vb)=W*mu(a,b), from a literal model to a
supplied tensor. Heights are sorted within factors; supplied factor order
is preserved. Labels explicitly normalize that order to lexicographic order.

This executable handles prime fields only. Trial division, primitive-root
search and a direct discrete-log loop are finite fixture algorithms, not a
polynomial bit-complexity claim for variable characteristic. No recognition
of an arbitrary supplied tensor is attempted.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""

from itertools import product
from math import gcd, isqrt


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _prime(p):
    if not _integer(p) or p < 2:
        raise ValueError("p must be a prime integer")
    if p != 2 and (p % 2 == 0 or any(p % d == 0 for d in range(3, isqrt(p) + 1, 2))):
        raise ValueError("p must be prime")


def _components(components):
    if not isinstance(components, (list, tuple)) or not components:
        raise ValueError("a product must have at least one component")
    result = []
    for heights in components:
        if not isinstance(heights, (list, tuple)):
            raise ValueError("each component must be a height list")
        if any(not _integer(h) or h < 1 for h in heights):
            raise ValueError("heights must be positive integers")
        result.append(sorted(heights))
    return result


def _nonzero(value, p, name):
    if not _integer(value) or not 1 <= value < p:
        raise ValueError(name + " must be a nonzero canonical field element")


def identity(n):
    if not _integer(n) or n < 1:
        raise ValueError("matrix dimension must be a positive integer")
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(matrix):
    if not isinstance(matrix, (list, tuple)) or not matrix:
        raise ValueError("transpose requires a nonempty square matrix")
    if any(not isinstance(row, (list, tuple)) or len(row) != len(matrix) for row in matrix):
        raise ValueError("transpose requires a square matrix")
    if any(not _integer(x) or x < 0 for row in matrix for x in row):
        raise ValueError("matrix entries must be nonnegative field integers")
    return [list(row) for row in zip(*matrix)]


def _matrix(matrix, n, p, name):
    if not isinstance(matrix, (list, tuple)) or len(matrix) != n:
        raise ValueError(name + " must be an n by n matrix")
    result = []
    for row in matrix:
        if not isinstance(row, (list, tuple)) or len(row) != n:
            raise ValueError(name + " must be an n by n matrix")
        if any(not _integer(x) or not 0 <= x < p for x in row):
            raise ValueError(name + " entries must be canonical field integers")
        result.append(list(row))
    return result


def matmul(left, right, p):
    _prime(p)
    if not isinstance(left, (list, tuple)) or not left:
        raise ValueError("multiplication requires nonempty square matrices")
    n = len(left)
    left, right = _matrix(left, n, p, "left matrix"), _matrix(right, n, p, "right matrix")
    return [[sum(left[i][k] * right[k][j] for k in range(n)) % p
             for j in range(n)] for i in range(n)]


def _apply(matrix, vector, p):
    return [sum(a * b for a, b in zip(row, vector)) % p for row in matrix]


def determinant(matrix, p):
    _prime(p)
    if not isinstance(matrix, (list, tuple)) or not matrix:
        raise ValueError("determinant requires a nonempty square matrix")
    rows = _matrix(matrix, len(matrix), p, "matrix")
    answer = 1
    for column in range(len(rows)):
        pivot = next((i for i in range(column, len(rows)) if rows[i][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            answer = -answer % p
        value = rows[column][column]
        answer = answer * value % p
        scale = pow(value, -1, p)
        for i in range(column + 1, len(rows)):
            multiplier = rows[i][column] * scale % p
            rows[i] = [(a - multiplier * b) % p for a, b in zip(rows[i], rows[column])]
    return answer


def inverse(matrix, p):
    _prime(p)
    if not isinstance(matrix, (list, tuple)) or not matrix:
        raise ValueError("inverse requires a nonempty square matrix")
    n = len(matrix)
    rows = [row + eye for row, eye in zip(_matrix(matrix, n, p, "matrix"), identity(n))]
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        if pivot is None:
            raise ValueError("matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = pow(rows[column][column], -1, p)
        rows[column] = [x * scale % p for x in rows[column]]
        for i in range(n):
            if i != column:
                multiplier = rows[i][column]
                rows[i] = [(a - multiplier * b) % p for a, b in zip(rows[i], rows[column])]
    return [row[n:] for row in rows]


def _table(table, n, p):
    if not isinstance(table, (list, tuple)) or len(table) != n:
        raise ValueError("tensor table must have shape n by n by n")
    return [_matrix(plane, n, p, "tensor plane") for plane in table]


def _multiply(table, left, right, p):
    result = [0] * len(table)
    for i, a in enumerate(left):
        if a:
            for j, b in enumerate(right):
                if b:
                    for k, value in enumerate(table[i][j]):
                        result[k] = (result[k] + a * b * value) % p
    return result


def make_model(p, components):
    """Return the literal product table, retaining the supplied factor order."""
    _prime(p)
    components = _components(components)
    dimensions = [p ** sum(heights) for heights in components]
    offsets, offset = [], 0
    exponents = []
    for heights, size in zip(components, dimensions):
        offsets.append(offset)
        offset += size
        exponents.append([list(a) for a in product(*(range(p ** h) for h in heights))])
    n = sum(dimensions)
    table = [[[0] * n for _ in range(n)] for _ in range(n)]
    unit = [0] * n
    for heights, start, basis in zip(components, offsets, exponents):
        index = {tuple(a): i for i, a in enumerate(basis)}
        sizes = [p ** h for h in heights]
        unit[start] = 1
        for i, a in enumerate(basis):
            for j, b in enumerate(basis):
                combined = tuple(x + y for x, y in zip(a, b))
                if all(x < size for x, size in zip(combined, sizes)):
                    table[start + i][start + j][start + index[combined]] = 1
    return {"p": p, "components": components, "n": n, "dimensions": dimensions,
            "offsets": offsets, "exponents": exponents, "table": table, "unit": unit}


def model_isomorphism(p, source_components, target_components):
    """Map source model columns into a reordered target with identical types."""
    source = make_model(p, source_components)
    target = make_model(p, target_components)
    if sorted(source["components"]) != sorted(target["components"]):
        raise ValueError("component height multisets are not isomorphic")
    matrix = [[0] * source["n"] for _ in range(source["n"])]
    available = list(range(len(target["components"])))
    for i, kind in enumerate(source["components"]):
        j = next(j for j in available if target["components"][j] == kind)
        available.remove(j)
        for k in range(source["dimensions"][i]):
            matrix[target["offsets"][j] + k][source["offsets"][i] + k] = 1
    return matrix


def determinant_character(p, components):
    """Return the exact index g of the algebra-automorphism determinant image."""
    _prime(p)
    components = _components(components)
    dimensions = [p ** sum(heights) for heights in components]
    local = [[size * (p ** h - 1) // 2 for h in heights]
             for size, heights in zip(dimensions, components)]
    pairs = []
    seen = {}
    for i, kind in enumerate(components):
        key = tuple(kind)
        if key in seen:
            pairs.append([seen[key], i])
        else:
            seen[key] = i
    g = p - 1
    for exponents in local:
        for exponent in exponents:
            g = gcd(g, exponent)
    if p % 2 and pairs:
        g = gcd(g, (p - 1) // 2)
    return {"p": p, "n": sum(dimensions), "components": components,
            "local_exponents": local, "swap_pairs": pairs, "index": g,
            "label_exponent": (p - 1) // g}


def _primitive_root(p):
    if p == 2:
        return 1
    remainder, divisor, factors = p - 1, 2, []
    while divisor * divisor <= remainder:
        if remainder % divisor == 0:
            factors.append(divisor)
            while remainder % divisor == 0:
                remainder //= divisor
        divisor += 1
    if remainder > 1:
        factors.append(remainder)
    return next(a for a in range(2, p) if all(pow(a, (p - 1) // q, p) != 1 for q in factors))


def _extended_gcd(a, b):
    old_r, r, old_s, s, old_t, t = a, b, 1, 0, 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def _exponent_word(p, exponents, desired):
    """Solve a product of power generators by Bezout coefficients and one log."""
    root = _primitive_root(p)
    value, logarithm = 1, 0
    while value != desired:
        value = value * root % p
        logarithm += 1
        if logarithm >= p - 1:
            raise ValueError("requested determinant is not a nonzero field element")
    divisor, coefficients = p - 1, []
    for exponent in exponents:
        divisor, left, right = _extended_gcd(divisor, exponent)
        coefficients = [left * c for c in coefficients] + [right]
    if logarithm % divisor:
        raise ValueError("requested determinant is outside the automorphism image")
    return root, [c * (logarithm // divisor) for c in coefficients]


def _check_map(p, source, target, U, V, W):
    n = len(source)
    u_columns, v_columns = transpose(U), transpose(V)
    for i in range(n):
        for j in range(n):
            if _multiply(target, u_columns[i], v_columns[j], p) != _apply(W, source[i][j], p):
                raise ValueError("three-factor certificate fails a basis-product identity")


def automorphism(p, components, desired_det):
    """Construct any attainable determinant using variable scales and swaps."""
    model = make_model(p, components)
    _nonzero(desired_det, p, "desired determinant")
    character = determinant_character(p, components)
    instructions, exponents = [], []
    for j, values in enumerate(character["local_exponents"]):
        for i, exponent in enumerate(values):
            instructions.append(("scale", j, i))
            exponents.append(exponent)
    if p % 2:
        for first, second in character["swap_pairs"]:
            instructions.append(("swap", first, second))
            exponents.append((p - 1) // 2)
    root, coefficients = _exponent_word(p, exponents, desired_det)
    matrix = identity(model["n"])
    scalings, swaps = [], []
    for instruction, coefficient in zip(instructions, coefficients):
        kind, first, second = instruction
        if kind == "scale":
            scalar = pow(root, coefficient % (p - 1), p)
            if scalar != 1:
                start = model["offsets"][first]
                for k, exponent in enumerate(model["exponents"][first]):
                    factor = pow(scalar, exponent[second], p)
                    matrix[start + k] = [factor * x % p for x in matrix[start + k]]
                scalings.append({"component": first, "variable": second, "scalar": scalar})
        elif coefficient % 2:
            first_start, second_start = model["offsets"][first], model["offsets"][second]
            for k in range(model["dimensions"][first]):
                matrix[first_start + k], matrix[second_start + k] = matrix[second_start + k], matrix[first_start + k]
            swaps.append([first, second])
    if determinant(matrix, p) != desired_det:
        raise RuntimeError("constructed automorphism has the wrong determinant")
    if _apply(matrix, model["unit"], p) != model["unit"]:
        raise RuntimeError("constructed automorphism does not preserve the unit")
    _check_map(p, model["table"], model["table"], matrix, matrix, matrix)
    return {"matrix": matrix, "determinant": desired_det, "scalings": scalings,
            "swaps": swaps, "index": character["index"]}


def _unit_multiplier(model, desired_det):
    p, n = model["p"], model["n"]
    # One local dimension is a p-power, hence invertible modulo p-1. The
    # total product dimension need not be: a global scalar is insufficient.
    scalar = 1 if p == 2 else pow(desired_det, pow(model["dimensions"][0], -1, p - 1), p)
    unit = list(model["unit"])
    unit[model["offsets"][0]] = scalar
    matrix = identity(n)
    for i in range(model["dimensions"][0]):
        matrix[i][i] = scalar
    if determinant(matrix, p) != desired_det:
        raise RuntimeError("component unit multiplier has the wrong determinant")
    return matrix, unit


def autotopism(p, components, a, b, c):
    """Construct U,V,W with dets a,b,c and mu(Ux,Vy)=W mu(x,y)."""
    model = make_model(p, components)
    for value, name in [(a, "a"), (b, "b"), (c, "c")]:
        _nonzero(value, p, name)
    delta = a * b * pow(c, -1, p) % p
    phi = automorphism(p, components, delta)
    left, left_unit = _unit_multiplier(model, a * pow(delta, -1, p) % p)
    right, right_unit = _unit_multiplier(model, b * pow(delta, -1, p) % p)
    U = matmul(left, phi["matrix"], p)
    V = matmul(right, phi["matrix"], p)
    W = matmul(matmul(left, right, p), phi["matrix"], p)
    actual = [determinant(matrix, p) for matrix in [U, V, W]]
    if actual != [a, b, c]:
        raise RuntimeError("autotopism determinant mismatch")
    _check_map(p, model["table"], model["table"], U, V, W)
    return {"U": U, "V": V, "W": W, "determinants": actual,
            "left_unit": left_unit, "right_unit": right_unit, "automorphism": phi}


def covariant_stabilizer(p, components, a, b, c):
    """Construct the covariant tensor stabilizer (U^-T,V^-T,W)."""
    _prime(p)
    for value, name in [(a, "a"), (b, "b"), (c, "c")]:
        _nonzero(value, p, name)
    witness = autotopism(p, components, pow(a, -1, p), pow(b, -1, p), c)
    A, B, C = transpose(inverse(witness["U"], p)), transpose(inverse(witness["V"], p)), witness["W"]
    if [determinant(matrix, p) for matrix in [A, B, C]] != [a, b, c]:
        raise RuntimeError("covariant determinant mismatch")
    return {"A": A, "B": B, "C": C, "determinants": [a, b, c], "autotopism": witness}


def validate_certificate(p, components, table, U, V, W):
    """Check every model-to-tensor product and return its canonical SL label.

    If R maps the canonical factor order into the supplied model order, the
    normalized certificate is (UR,VR,WR); its ratio is raw_d/det(R).
    This sign matters when unequal component types are reordered.
    """
    model = make_model(p, components)
    n = model["n"]
    table = _table(table, n, p)
    U, V, W = [_matrix(matrix, n, p, name) for matrix, name in [(U, "U"), (V, "V"), (W, "W")]]
    determinants = [determinant(matrix, p) for matrix in [U, V, W]]
    if not all(determinants):
        raise ValueError("certificate factor maps must be invertible")
    _check_map(p, model["table"], table, U, V, W)
    canonical = sorted(model["components"])
    R = model_isomorphism(p, canonical, model["components"])
    normalization_det = determinant(R, p)
    raw_d = determinants[2] * pow(determinants[0] * determinants[1] % p, -1, p) % p
    d = raw_d * pow(normalization_det, -1, p) % p
    character = determinant_character(p, canonical)
    return {"n": n, "components": canonical, "determinants": determinants,
            "normalization_det": normalization_det, "raw_d": raw_d, "d": d,
            "label": pow(d, character["label_exponent"], p), "index": character["index"],
            "basis_products_checked": n * n,
            "normalized_certificate": {"U": matmul(U, R, p), "V": matmul(V, R, p), "W": matmul(W, R, p)}}


def sl_transporter(p, left_components, left_table, left_certificate,
                   right_components, right_table, right_certificate):
    """Construct right(Ax,By)=C left(x,y), with all three determinants one."""
    certificates = []
    for components, table, certificate in [(left_components, left_table, left_certificate),
                                            (right_components, right_table, right_certificate)]:
        if not isinstance(certificate, dict) or any(key not in certificate for key in ("U", "V", "W")):
            raise ValueError("a certificate must supply U, V and W")
        certificates.append(validate_certificate(p, components, table, certificate["U"], certificate["V"], certificate["W"]))
    left, right = certificates
    if left["components"] != right["components"]:
        raise ValueError("component height multisets are not isomorphic")
    if left["label"] != right["label"]:
        raise ValueError("tensors have different special-linear orbit labels")
    L, R = left["normalized_certificate"], right["normalized_certificate"]
    desired = [determinant(L[key], p) * pow(determinant(R[key], p), -1, p) % p for key in ("U", "V", "W")]
    correction = autotopism(p, left["components"], *desired)
    maps = [matmul(matmul(R[key], correction[key], p), inverse(L[key], p), p) for key in ("U", "V", "W")]
    if [determinant(matrix, p) for matrix in maps] != [1, 1, 1]:
        raise RuntimeError("special-linear transporter determinant mismatch")
    n = left["n"]
    _check_map(p, _table(left_table, n, p), _table(right_table, n, p), *maps)
    return {"A": maps[0], "B": maps[1], "C": maps[2], "determinants": [1, 1, 1],
            "label": left["label"], "basis_products_checked": n * n}
