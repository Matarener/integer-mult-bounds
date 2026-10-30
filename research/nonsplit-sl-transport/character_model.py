#!/usr/bin/env python3
"""Explicit nonsplit Frobenius-product determinant witnesses.

Input fields and residue polynomials are supplied, not recognized. The base is
the retained Field implementation. Extension elements use base-q digits, and
model basis index is offset + monomial_index * residue_degree + coefficient
exponent. Matrices use row-major storage and columns are basis images.
Certificates use tensor(Ua,Vb) = W * model(a,b). All input coordinates must be
canonical field integers. Components must already be in canonical type order.

Finite field-table construction, primitive-element search and discrete-log
enumeration are bounded-fixture algorithms, not polynomial bit-complexity
claims. No arbitrary tensor recognition or cross-presentation field matching
is implemented. Prepared by apoursh with substantial OpenAI Codex assistance.
New work is Apache-2.0; the unchanged vendor retains its own notice.
"""

import hashlib
from itertools import product
from math import gcd
from pathlib import Path
from types import ModuleType


VENDOR_SHA256 = "6daa160346d04691c6ca3c9c820b3df8982de4320ec01e5db10e3cb932f42c00"
_vendor_path = Path(__file__).with_name("vendor") / "local.py"
_vendor_bytes = _vendor_path.read_bytes()
if hashlib.sha256(_vendor_bytes).hexdigest() != VENDOR_SHA256:
    raise ValueError("retained finite-field source hash mismatch")
local = ModuleType("nonsplit_retained_local")
exec(compile(_vendor_bytes, str(_vendor_path), "exec"), local.__dict__)
Field = local.Field


def _integer(value):
    return type(value) is int


def _base_signature(base):
    if not isinstance(base, Field):
        raise ValueError("base must be the retained explicit Field")
    return base.p, base.modulus


def _element(value, field, name="element", nonzero=False):
    if not _integer(value) or not (int(nonzero) <= value < field.q):
        raise ValueError(name + " must be a canonical field integer" + (" and nonzero" if nonzero else ""))


class Extension:
    """Finite residue field over an explicit base Field, with constant-first modulus."""

    def __init__(self, base, modulus):
        _base_signature(base)
        if (not isinstance(modulus, (list, tuple)) or len(modulus) < 2
                or any(not _integer(c) or not 0 <= c < base.q for c in modulus)
                or modulus[-1] != 1):
            raise ValueError("residue modulus must be monic with canonical base-field coefficients")
        self.base, self.modulus = base, tuple(modulus)
        self.degree, self.p = len(modulus) - 1, base.p
        self.q = base.q ** self.degree
        self.digits = [[(a // base.q ** i) % base.q for i in range(self.degree)] for a in range(self.q)]
        self.add = [[sum(base.add[x][y] * base.q ** i for i, (x, y) in enumerate(zip(a, b)))
                     for b in self.digits] for a in self.digits]
        self.neg = [sum(base.neg[x] * base.q ** i for i, x in enumerate(a)) for a in self.digits]
        self.mul = []
        for a in self.digits:
            row = []
            for b in self.digits:
                coefficients = [0] * (2 * self.degree - 1)
                for i, x in enumerate(a):
                    for j, y in enumerate(b):
                        coefficients[i + j] = base.add[coefficients[i + j]][base.mul[x][y]]
                for k in range(len(coefficients) - 1, self.degree - 1, -1):
                    for j in range(self.degree):
                        correction = base.neg[base.mul[coefficients[k]][modulus[j]]]
                        coefficients[k - self.degree + j] = base.add[coefficients[k - self.degree + j]][correction]
                row.append(sum(coefficients[i] * base.q ** i for i in range(self.degree)))
            self.mul.append(row)
        self.inv = [0] + [self.power(a, self.q - 2) for a in range(1, self.q)]
        if any(self.mul[a][self.inv[a]] != 1 for a in range(1, self.q)):
            raise ValueError("residue modulus is reducible over the supplied base field")

    def power(self, a, exponent):
        _element(a, self)
        if not _integer(exponent) or exponent < 0:
            raise ValueError("power exponent must be a nonnegative integer")
        result = 1
        while exponent:
            if exponent & 1:
                result = self.mul[result][a]
            a = self.mul[a][a]
            exponent //= 2
        return result

    def norm(self, a):
        value = self.power(a, (self.q - 1) // (self.base.q - 1))
        if any(self.digits[value][1:]):
            raise RuntimeError("norm did not land in the supplied base field")
        return self.digits[value][0]

    def frobenius(self, a):
        return self.power(a, self.base.q)


def _components(components):
    if not isinstance(components, (list, tuple)) or not components:
        raise ValueError("a product must have at least one component")
    result = []
    for component in components:
        if not isinstance(component, (list, tuple)) or len(component) != 2:
            raise ValueError("a component must be (residue degree, heights)")
        degree, heights = component
        if not _integer(degree) or degree < 1:
            raise ValueError("residue degree must be a positive integer")
        if not isinstance(heights, (list, tuple)) or any(not _integer(h) or h < 1 for h in heights):
            raise ValueError("heights must be positive integers")
        if list(heights) != sorted(heights):
            raise ValueError("heights must be sorted")
        result.append((degree, tuple(heights)))
    if result != sorted(result):
        raise ValueError("components must be in canonical degree-and-height order")
    return result


def make_model(base, components, residues=None):
    """Construct the ground-field table, using one residue presentation per degree."""
    signature = _base_signature(base)
    types = _components(components)
    degrees = {degree for degree, _ in types}
    if residues is None:
        residues = {}
    if not isinstance(residues, dict):
        raise ValueError("residues must map degrees to explicit Extension objects")
    supplied = dict(residues)
    if 1 in degrees and 1 not in supplied:
        supplied[1] = Extension(base, [0, 1])
    if any(not _integer(d) or d not in degrees for d in supplied):
        raise ValueError("residue dictionary has an invalid or unused degree")
    if set(supplied) != degrees:
        raise ValueError("one explicit residue field is required for each degree")
    for degree, residue in supplied.items():
        if not isinstance(residue, Extension) or residue.degree != degree:
            raise ValueError("residue field degree does not match its key")
        if _base_signature(residue.base) != signature:
            raise ValueError("residue field uses a different base presentation")
    local_dimensions = [base.p ** sum(heights) for _, heights in types]
    dimensions = [degree * size for (degree, _), size in zip(types, local_dimensions)]
    offsets, offset = [], 0
    exponents = []
    for (_, heights), size in zip(types, dimensions):
        offsets.append(offset)
        offset += size
        exponents.append([list(a) for a in product(*(range(base.p ** h) for h in heights))])
    n = sum(dimensions)
    table = [[[0] * n for _ in range(n)] for _ in range(n)]
    unit = [0] * n
    for (degree, heights), start, monomials in zip(types, offsets, exponents):
        residue = supplied[degree]
        monomial_index = {tuple(a): i for i, a in enumerate(monomials)}
        bounds = [base.p ** h for h in heights]
        unit[start] = 1
        for i, a in enumerate(monomials):
            for j, b in enumerate(monomials):
                combined = tuple(x + y for x, y in zip(a, b))
                if any(x >= bound for x, bound in zip(combined, bounds)):
                    continue
                target = start + degree * monomial_index[combined]
                for r in range(degree):
                    for s in range(degree):
                        coefficients = residue.digits[residue.mul[base.q ** r][base.q ** s]]
                        for k, value in enumerate(coefficients):
                            table[start + degree * i + r][start + degree * j + s][target + k] = value
    return {"base": base, "components": [[d, list(h)] for d, h in types],
            "residues": supplied, "local_dimensions": local_dimensions,
            "dimensions": dimensions, "offsets": offsets, "exponents": exponents,
            "n": n, "table": table, "unit": unit}


def model_isomorphism(first, second):
    """Match identical supplied presentations; alternative field isomorphisms are not provided."""
    if _base_signature(first["base"]) != _base_signature(second["base"]):
        raise ValueError("base-field presentations differ")
    if first["components"] != second["components"]:
        raise ValueError("component degree-and-height types differ")
    if any(first["residues"][d].modulus != second["residues"][d].modulus for d in first["residues"]):
        raise ValueError("residue presentations differ; supply a separate checked field isomorphism")
    return local.identity(first["n"])


def determinant_character(base, components):
    _base_signature(base)
    types = _components(components)
    exponents = [[base.p ** sum(heights) * (base.p ** h - 1) // 2 for h in heights]
                 for _, heights in types]
    g = base.q - 1
    for row in exponents:
        for exponent in row:
            g = gcd(g, exponent)
    signs = []
    if base.q % 2:
        signs.extend({"kind": "frobenius", "component": i} for i, (d, _) in enumerate(types) if d % 2 == 0)
        seen = {}
        for i, kind in enumerate(types):
            if kind in seen and kind[0] % 2:
                signs.append({"kind": "swap", "components": [seen[kind], i]})
            seen.setdefault(kind, i)
        if signs:
            g = gcd(g, (base.q - 1) // 2)
    return {"index": g, "label_exponent": (base.q - 1) // g,
            "local_exponents": exponents, "sign_generators": signs}


def _component(model, component):
    if not _integer(component) or not 0 <= component < len(model["components"]):
        raise ValueError("invalid component index")
    degree, heights = model["components"][component]
    return degree, heights, model["residues"][degree]


def _coefficient_matrix(model, component, images):
    degree, _, residue = _component(model, component)
    matrix = local.identity(model["n"])
    start = model["offsets"][component]
    for monomial in range(model["local_dimensions"][component]):
        block = start + degree * monomial
        for column in range(degree):
            image = images(monomial, residue.base.q ** column)
            for row, value in enumerate(residue.digits[image]):
                matrix[block + row][block + column] = value
    return matrix


def variable_scaling(model, component, variable, scalar):
    _, heights, residue = _component(model, component)
    if not _integer(variable) or not 0 <= variable < len(heights):
        raise ValueError("invalid variable index")
    _element(scalar, residue, "scaling coefficient", True)
    return _coefficient_matrix(model, component, lambda m, a: residue.mul[a][
        residue.power(scalar, model["exponents"][component][m][variable])])


def coefficient_frobenius(model, component):
    _, _, residue = _component(model, component)
    return _coefficient_matrix(model, component, lambda m, a: residue.frobenius(a))


def component_swap(model, first, second):
    _component(model, first)
    _component(model, second)
    if first == second or model["components"][first] != model["components"][second]:
        raise ValueError("swap requires two distinct components of identical type")
    matrix = local.identity(model["n"])
    for k in range(model["dimensions"][first]):
        a, b = model["offsets"][first] + k, model["offsets"][second] + k
        matrix[a], matrix[b] = matrix[b], matrix[a]
    return matrix


def unit_multiplication(model, component, scalar):
    _, _, residue = _component(model, component)
    _element(scalar, residue, "unit coefficient", True)
    return _coefficient_matrix(model, component, lambda m, a: residue.mul[scalar][a])


def _primitive_element(field):
    for candidate in range(1, field.q):
        value, seen = 1, set()
        while value not in seen:
            seen.add(value)
            value = field.mul[value][candidate]
        if len(seen) == field.q - 1:
            return candidate
    raise RuntimeError("no primitive element in checked field")


def _norm_preimage(residue, desired):
    _element(desired, residue.base, "desired norm", True)
    for candidate in range(1, residue.q):
        if residue.norm(candidate) == desired:
            return candidate
    raise RuntimeError("checked finite-field norm was not surjective")


def _exponent_word(base, exponents, desired):
    root = _primitive_element(base)
    value, logarithm = 1, 0
    while value != desired:
        value = base.mul[value][root]
        logarithm += 1
        if logarithm >= base.q - 1:
            raise ValueError("desired determinant is not a nonzero base-field element")
    divisor, coefficients = base.q - 1, []
    for exponent in exponents:
        divisor, left, right = local.bezout(divisor, exponent)
        coefficients = [left * c for c in coefficients] + [right]
    if logarithm % divisor:
        raise ValueError("desired determinant lies outside the automorphism image")
    return root, [c * (logarithm // divisor) for c in coefficients]


def _check_products(model, target, U, V, W):
    f, n = model["base"], model["n"]
    for i in range(n):
        for j in range(n):
            if local.tensor_value(target, local.column(U, i), local.column(V, j), f) != local.mv(W, model["table"][i][j], f):
                raise ValueError("three-factor certificate fails a basis-product identity")


def automorphism(model, desired_det):
    base = model["base"]
    _element(desired_det, base, "desired determinant", True)
    character = determinant_character(base, model["components"])
    instructions, exponents = [], []
    for component, row in enumerate(character["local_exponents"]):
        for variable, exponent in enumerate(row):
            instructions.append({"kind": "scale", "component": component, "variable": variable})
            exponents.append(exponent)
    for sign in character["sign_generators"]:
        instructions.append(sign)
        exponents.append((base.q - 1) // 2)
    root, coefficients = _exponent_word(base, exponents, desired_det)
    matrix, operations = local.identity(model["n"]), []
    for instruction, coefficient in zip(instructions, coefficients):
        kind = instruction["kind"]
        if kind == "scale":
            component = instruction["component"]
            residue = model["residues"][model["components"][component][0]]
            scalar = _norm_preimage(residue, base.power(root, coefficient % (base.q - 1)))
            operation = variable_scaling(model, component, instruction["variable"], scalar)
            operations.append({**instruction, "scalar": scalar})
        elif coefficient % 2:
            operation = coefficient_frobenius(model, instruction["component"]) if kind == "frobenius" else component_swap(model, *instruction["components"])
            operations.append(dict(instruction))
        else:
            continue
        matrix = local.mm(operation, matrix, base)
    if local.determinant(matrix, base) != desired_det:
        raise RuntimeError("automorphism determinant mismatch")
    if local.mv(matrix, model["unit"], base) != model["unit"]:
        raise RuntimeError("automorphism does not preserve the unit")
    _check_products(model, model["table"], matrix, matrix, matrix)
    return {"matrix": matrix, "determinant": desired_det, "operations": operations, "index": character["index"]}


def _unit_with_determinant(model, desired):
    base = model["base"]
    degree = model["components"][0][0]
    exponent = 0 if base.q == 2 else pow(model["local_dimensions"][0], -1, base.q - 1)
    scalar = _norm_preimage(model["residues"][degree], base.power(desired, exponent))
    matrix = unit_multiplication(model, 0, scalar)
    if local.determinant(matrix, base) != desired:
        raise RuntimeError("unit determinant mismatch")
    return matrix, scalar


def autotopism(model, a, b, c):
    base = model["base"]
    for value in (a, b, c):
        _element(value, base, "requested determinant", True)
    delta = base.mul[base.mul[a][b]][base.inv[c]]
    phi = automorphism(model, delta)
    left, left_scalar = _unit_with_determinant(model, base.mul[a][base.inv[delta]])
    right, right_scalar = _unit_with_determinant(model, base.mul[b][base.inv[delta]])
    U, V = local.mm(left, phi["matrix"], base), local.mm(right, phi["matrix"], base)
    W = local.mm(local.mm(left, right, base), phi["matrix"], base)
    determinants = [local.determinant(matrix, base) for matrix in (U, V, W)]
    if determinants != [a, b, c]:
        raise RuntimeError("autotopism determinant mismatch")
    _check_products(model, model["table"], U, V, W)
    return {"U": U, "V": V, "W": W, "determinants": determinants,
            "left_unit_scalar": left_scalar, "right_unit_scalar": right_scalar, "automorphism": phi}


def covariant_stabilizer(model, a, b, c):
    base = model["base"]
    for value in (a, b, c):
        _element(value, base, "requested determinant", True)
    witness = autotopism(model, base.inv[a], base.inv[b], c)
    A = list(map(list, zip(*local.inverse(witness["U"], base))))
    B = list(map(list, zip(*local.inverse(witness["V"], base))))
    C = witness["W"]
    if [local.determinant(matrix, base) for matrix in (A, B, C)] != [a, b, c]:
        raise RuntimeError("covariant determinant mismatch")
    return {"A": A, "B": B, "C": C, "determinants": [a, b, c], "autotopism": witness}


def _matrix(matrix, n, base, name):
    if not isinstance(matrix, (list, tuple)) or len(matrix) != n:
        raise ValueError(name + " must be an n by n matrix")
    result = []
    for row in matrix:
        if not isinstance(row, (list, tuple)) or len(row) != n:
            raise ValueError(name + " must be an n by n matrix")
        for value in row:
            _element(value, base, name + " entry")
        result.append(list(row))
    return result


def validate_certificate(model, table, U, V, W):
    """Validate a supplied three-factor decomposition and compute its canonical orbit label."""
    base, n = model["base"], model["n"]
    if not isinstance(table, (list, tuple)) or len(table) != n:
        raise ValueError("tensor must have shape n by n by n")
    table = [_matrix(plane, n, base, "tensor plane") for plane in table]
    U, V, W = [_matrix(matrix, n, base, name) for matrix, name in ((U, "U"), (V, "V"), (W, "W"))]
    determinants = [local.determinant(matrix, base) for matrix in (U, V, W)]
    if not all(determinants):
        raise ValueError("certificate factor maps must be invertible")
    _check_products(model, table, U, V, W)
    d = base.mul[determinants[2]][base.inv[base.mul[determinants[0]][determinants[1]]]]
    character = determinant_character(base, model["components"])
    return {"n": n, "components": model["components"], "determinants": determinants,
            "d": d, "label": base.power(d, character["label_exponent"]),
            "index": character["index"], "basis_products_checked": n * n}
