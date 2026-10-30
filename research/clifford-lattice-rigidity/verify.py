"""Exact matrix-unit and invariant-lattice rigidity corroboration.

Produced by Nick Petalas. Apache-2.0.
"""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


Z = (0, 0)
O = (1, 0)
I = (0, 1)
PI = (1, 1)
FILES = ("README.md", "PROOF.md", "verify.py", "TASK.json", "SOURCES.json", "VERIFY.json")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def neg(a):
    return (-a[0], -a[1])


def mul(a, b):
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])


def scale(matrix, value):
    return tuple(mul(value, x) for x in matrix)


def matrix_add(a, b):
    return tuple(add(x, y) for x, y in zip(a, b))


def matrix_mul(a, b):
    need(len(a) == len(b) == 4, "fixed two-by-two matrices")
    return tuple(add(mul(a[2*r], b[c]), mul(a[2*r+1], b[2+c]))
                 for r in range(2) for c in range(2))


def units():
    identity = (O, Z, Z, O)
    butterfly = (O, O, Z, I)
    phase = (O, Z, I, I)
    minus_i = scale(identity, neg(I))
    e00 = scale(matrix_mul(matrix_add(butterfly, minus_i),
                           matrix_add(phase, minus_i)), I)
    e01 = matrix_add(matrix_mul(e00, butterfly), scale(e00, (-1, 0)))
    e10 = scale(matrix_add(matrix_mul(phase, e00), scale(e00, (-1, 0))), neg(I))
    e11 = matrix_add(identity, scale(e00, (-1, 0)))
    result = (e00, e01, e10, e11)
    for index, matrix in enumerate(result):
        need(matrix == tuple(O if j == index else Z for j in range(4)), "generated matrix unit")
    for a, b in product(range(4), repeat=2):
        expected = result[2*(a//2)+b%2] if a%2 == b//2 else (Z,)*4
        need(matrix_mul(result[a], result[b]) == expected, "matrix-unit multiplication law")
    return result, butterfly, phase


def rank_of(values):
    size = len(values)
    need(2 <= size <= 128 and size & (size-1) == 0, "rank 1..7 only")
    return size.bit_length()-1


def apply_local(values, bit, matrix):
    rank = rank_of(values)
    need(0 <= bit < rank and len(matrix) == 4, "local matrix domain")
    out = list(values)
    for address in range(len(values)):
        if not address & (1 << bit):
            other = address | (1 << bit)
            a, b = values[address], values[other]
            out[address] = add(mul(matrix[0], a), mul(matrix[1], b))
            out[other] = add(mul(matrix[2], a), mul(matrix[3], b))
    return out


def tensor_unit_checks(local_units):
    records = []
    for rank in range(1, 8):
        size = 1 << rank
        values = [(j+1, 2*j+3) for j in range(size)]
        for row, column in product(range(size), repeat=2):
            actual = list(values)
            for bit in range(rank):
                unit = local_units[2*((row >> bit)&1)+((column >> bit)&1)]
                actual = apply_local(actual, bit, unit)
            expected = [values[column] if j == row else Z for j in range(size)]
            need(actual == expected, "tensor product gives the requested global matrix unit")
        records.append({"rank": rank, "global_units": size*size})
    return records


def divide_pi(value):
    a, b = value
    need((a-b) % 2 == 0, "nonintegral Gaussian division")
    return ((a+b)//2, (b-a)//2)


def power_pi(exponent):
    need(0 <= exponent <= 7, "fixed Gaussian power bound")
    value = O
    for _ in range(exponent):
        value = mul(value, PI)
    return value


def encode(values):
    rank = rank_of(values)
    out = [mul(value, power_pi(mask.bit_count())) for mask, value in enumerate(values)]
    for bit in range(rank):
        for mask in range(len(out)):
            if mask & (1 << bit):
                out[mask] = add(out[mask], out[mask ^ (1 << bit)])
    return out


def member(values):
    rank = rank_of(values)
    out = list(values)
    for bit in range(rank):
        for mask in range(len(out)):
            if mask & (1 << bit):
                out[mask] = add(out[mask], neg(out[mask ^ (1 << bit)]))
    for mask, value in enumerate(out):
        for _ in range(mask.bit_count()):
            if (value[0]-value[1]) % 2:
                return False
            value = divide_pi(value)
    return True


def gaussian_divides(divisor, value):
    norm = divisor[0]**2 + divisor[1]**2
    need(norm > 0, "nonzero ideal generator")
    numerator = mul(value, (divisor[0], -divisor[1]))
    return numerator[0] % norm == numerator[1] % norm == 0


def quotient(value, divisor):
    need(gaussian_divides(divisor, value), "exact Gaussian quotient")
    norm = divisor[0]**2 + divisor[1]**2
    a, b = mul(value, (divisor[0], -divisor[1]))
    return (a//norm, b//norm)


def scalar_lattice_member(values, scalar):
    if not all(gaussian_divides(scalar, value) for value in values):
        return False
    return member([quotient(value, scalar) for value in values])


def quarter_controls():
    scalars = (O, I, PI, (2, 0), (2, 1), (3, -1), (-7, 4))
    cases = 0
    for rank in range(1, 8):
        size = 1 << rank
        basis = [Z]*(size-1) + [power_pi(max(rank, 4))]
        for scalar in scalars:
            values = [mul(scalar, value) for value in basis]
            need(scalar_lattice_member(values, scalar), "scaled lattice quarter entrance")
            need(all(x % 4 == 0 for z in values for x in z), "quarter has integral coordinates")
            divided = [tuple(x//4 for x in z) for z in values]
            need(not scalar_lattice_member(divided, scalar), "every scalar lattice fails quarter closure")
            cases += 1
    return cases


def residue_action(value, matrix):
    vector = [((value >> (2*j))&1, (value >> (2*j+1))&1) for j in range(2)]
    image = apply_local(vector, 0, matrix)
    return sum(((a % 2)+2*(b % 2)) << (2*j) for j, (a, b) in enumerate(image))


def finite_module_census(butterfly, phase):
    """All 67 additive subgroups of (Z[i]/2)^2, then impose i,C,S."""
    spaces = {frozenset({0})}
    for _ in range(4):
        next_spaces = set(spaces)
        for space in spaces:
            for value in range(16):
                next_spaces.add(frozenset(space | {x ^ value for x in space}))
        need(len(next_spaces) <= 67, "bounded complete subgroup census")
        spaces = next_spaces
    need(len(spaces) == 67, "all binary dimension-four subspaces")
    scalar_i = (I, Z, Z, I)
    stable = []
    for _, ordered in sorted((len(s), tuple(sorted(s))) for s in spaces):
        space = frozenset(ordered)
        if all(residue_action(v, m) in space for v in space for m in (scalar_i, butterfly, phase)):
            stable.append(sorted(space))
    need(stable == [[0], [0, 3, 12, 15], list(range(16))], "only the three scalar ideals survive")
    for vector in ([O, Z], [Z, PI]):
        need(gaussian_divides(PI, apply_local(vector, 0, butterfly)[1]), "C-only skew lattice is invariant")
    need(not gaussian_divides(PI, apply_local([O, Z], 0, phase)[1]), "phase premise is necessary")
    return {"additive_subgroups": 67, "invariant": stable, "C_only_skew_counterexample": True}


def ideal_preservation(butterfly, phase):
    count = 0
    for rank in range(1, 8):
        size = 1 << rank
        for scalar in (O, PI, (2, 1)):
            coefficients = [mul(scalar, (j-17, 3*j+2)) for j in range(size)]
            physical = encode(coefficients)
            need(scalar_lattice_member(physical, scalar), "independent coefficient fixture")
            for bit in range(rank):
                for matrix in (butterfly, phase):
                    image = apply_local(coefficients, bit, matrix)
                    need(scalar_lattice_member(encode(image), scalar), "scalar ideal invariant")
                    count += 1
    return count


def hashes():
    root = Path(__file__).resolve().parent
    result = {}
    for name in FILES:
        content = (root/name).read_bytes()
        need(len(content) <= 200_000, "bounded receipt source")
        result[name] = sha256(content).hexdigest()
    return result


def main():
    local_units, butterfly, phase = units()
    result = {"local_units": 4, "local_unit_products": 16,
              "tensor_units": tensor_unit_checks(local_units),
              "finite_module": finite_module_census(butterfly, phase),
              "ideal_generator_checks": ideal_preservation(butterfly, phase),
              "integral_quarter_counterexamples": quarter_controls(),
              "sha256": hashes()}
    print(json.dumps(result, sort_keys=True))
    print("PASS_CLIFFORD_LATTICE_RIGIDITY ranks=1..7 scalar_classes_only quarter_closure=excluded no_new_kappa")


if __name__ == "__main__":
    main()
