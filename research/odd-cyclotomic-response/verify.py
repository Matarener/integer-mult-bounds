#!/usr/bin/env python3
"""Exact finite evidence. Produced by Nick Petalas. Apache-2.0."""
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
import hashlib
import json
from math import gcd, lcm
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Matrix:
    n: int
    real: tuple
    imag: tuple
    denominator: int = 1

    def __post_init__(self):
        require(1 <= self.n <= 16, "matrix dimension outside 1..16")
        require(len(self.real) == len(self.imag) == self.n**2, "matrix shape")
        require(1 <= self.denominator <= 2**256, "denominator capacity")
        require(all(type(x) is int and abs(x) <= 2**256
                    for x in self.real + self.imag), "numerator capacity")


def matrix(rows, denominator=1):
    n = len(rows)
    require(1 <= n <= 16 and type(denominator) is int and denominator > 0,
            "matrix input domain")
    require(all(len(row) == n for row in rows), "square rows required")
    real = tuple(z[0] for row in rows for z in row)
    imag = tuple(z[1] for row in rows for z in row)
    common = reduce(gcd, real + imag, denominator)
    return Matrix(n, tuple(x // common for x in real),
                  tuple(x // common for x in imag), denominator // common)


def identity(n):
    require(type(n) is int and 1 <= n <= 16, "identity dimension")
    return matrix([[(int(i == j), 0) for j in range(n)] for i in range(n)])


def multiply(a, b):
    require(a.n == b.n, "matrix multiplication dimension")
    n = a.n
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            real = imag = 0
            for k in range(n):
                ar, ai = a.real[i*n+k], a.imag[i*n+k]
                br, bi = b.real[k*n+j], b.imag[k*n+j]
                real += ar*br - ai*bi
                imag += ar*bi + ai*br
            row.append((real, imag))
        rows.append(row)
    return matrix(rows, a.denominator*b.denominator)


def add(a, b):
    require(a.n == b.n, "matrix addition dimension")
    d = lcm(a.denominator, b.denominator)
    x, y = d // a.denominator, d // b.denominator
    return matrix([[(x*a.real[i*a.n+j] + y*b.real[i*a.n+j],
                     x*a.imag[i*a.n+j] + y*b.imag[i*a.n+j])
                    for j in range(a.n)] for i in range(a.n)], d)


def scale(a, real, imag=0):
    return matrix([[(real*a.real[i*a.n+j] - imag*a.imag[i*a.n+j],
                     real*a.imag[i*a.n+j] + imag*a.real[i*a.n+j])
                    for j in range(a.n)] for i in range(a.n)], a.denominator)


def adjoint(a):
    return matrix([[(a.real[j*a.n+i], -a.imag[j*a.n+i])
                    for j in range(a.n)] for i in range(a.n)], a.denominator)


def tensor(a, b):
    require(a.n*b.n <= 16, "tensor dimension capacity")
    rows = []
    for i in range(a.n*b.n):
        row = []
        for j in range(a.n*b.n):
            u, v = (i//b.n)*a.n+j//b.n, (i%b.n)*b.n+j%b.n
            row.append((a.real[u]*b.real[v] - a.imag[u]*b.imag[v],
                        a.real[u]*b.imag[v] + a.imag[u]*b.real[v]))
        rows.append(row)
    return matrix(rows, a.denominator*b.denominator)


def power(a, k):
    require(type(k) is int and 0 <= k <= 32, "power capacity")
    result = identity(a.n)
    for _ in range(k):
        result = multiply(result, a)
    return result


def trace(a):
    return (Fraction(sum(a.real[i*a.n+i] for i in range(a.n)), a.denominator),
            Fraction(sum(a.imag[i*a.n+i] for i in range(a.n)), a.denominator))


def polynomial(a, coefficients):
    require(1 <= len(coefficients) <= 33, "matrix polynomial capacity")
    require(all(type(c) is int and abs(c) <= 32 for c in coefficients),
            "matrix polynomial coefficient capacity")
    result = scale(identity(a.n), 0)
    for c in reversed(coefficients):
        result = add(multiply(result, a), scale(identity(a.n), c))
    return result


def pauli(qubits, label):
    require(1 <= qubits <= 4 and 0 <= label < 4**qubits, "Pauli capacity")
    n = 2**qubits
    x, z = label % n, label // n
    phase = (x & z).bit_count() % 4
    unit = ((1, 0), (0, 1), (-1, 0), (0, -1))[phase]
    rows = [[(0, 0)]*n for _ in range(n)]
    for j in range(n):
        sign = (-1)**((z & j).bit_count())
        rows[j ^ x][j] = (sign*unit[0], sign*unit[1])
    return matrix(rows)


def binary_rank(columns):
    require(len(columns) <= 8 and all(0 <= x < 256 for x in columns),
            "binary rank capacity")
    basis = [0]*8
    rank = 0
    for column in columns:
        for bit in range(7, -1, -1):
            if column & (1 << bit):
                if basis[bit]:
                    column ^= basis[bit]
                else:
                    basis[bit] = column
                    rank += 1
                    break
    return rank


def clifford_record(u):
    qubits = u.n.bit_length()-1
    require(u.n == 2**qubits and 1 <= qubits <= 4, "qubit dimension")
    require(multiply(u, adjoint(u)) == identity(u.n), "unitarity")
    lookup = {}
    for label in range(4**qubits):
        p = pauli(qubits, label)
        lookup[p] = (label, 1)
        lookup[scale(p, -1)] = (label, -1)
    columns = []
    for bit in range(2*qubits):
        image = multiply(multiply(u, pauli(qubits, 1 << bit)), adjoint(u))
        require(image in lookup, "not Clifford")
        columns.append(lookup[image][0])
    defect = binary_rank([c ^ (1 << j) for j, c in enumerate(columns)])
    native = binary_rank([columns[qubits+j] % u.n for j in range(qubits)])
    fixed = []
    character_sum = 0
    for label in range(4**qubits):
        image_label = 0
        for bit in range(2*qubits):
            if label & (1 << bit):
                image_label ^= columns[bit]
        if image_label == label:
            image = multiply(multiply(u, pauli(qubits, label)), adjoint(u))
            require(image in lookup and lookup[image][0] == label, "fixed label")
            character_sum += lookup[image][1]
            fixed.append(label)
    tr = trace(u)
    require(tr[0]**2 + tr[1]**2 == character_sum, "adjoint trace identity")
    return {"qubits": qubits, "trace": [str(x) for x in tr],
            "symplectic_defect_rank": defect, "native_B_rank": native,
            "fixed_labels": len(fixed), "fixed_character_sum": character_sum}


def fixture_checks():
    # H_g=(1+i)H/sqrt(2); U5=-CNOT_(0->1) S_0 (H_g tensor H_g).
    h = matrix([[(1, 1), (1, 1)], [(1, 1), (-1, -1)]], 2)
    s = matrix([[(1, 0), (0, 0)], [(0, 0), (0, 1)]])
    c = permutation([0, 1, 3, 2])
    u = scale(multiply(multiply(c, tensor(s, identity(2))), tensor(h, h)), -1)
    displayed = matrix([[(0, -1), (0, -1), (0, -1), (0, -1)],
                        [(0, -1), (0, 1), (0, -1), (0, 1)],
                        [(1, 0), (-1, 0), (-1, 0), (1, 0)],
                        [(1, 0), (1, 0), (-1, 0), (-1, 0)]], 2)
    require(u == displayed, "displayed matrix and literal circuit agree")
    zero = scale(identity(4), 0)
    require(power(u, 5) == identity(4), "degree-four order")
    require(polynomial(u, (1, 1, 1, 1, 1)) == zero, "primitive degree four")
    basic = clifford_record(u)
    require(basic["symplectic_defect_rank"] == 4, "degree-four defect")
    # Bell preparation on (0,2),(1,3), with two spectator qubits.
    bell_h = tensor(tensor(h, h), identity(4))
    bell_c = permutation([j ^ (((j >> 3) & 1) << 1) ^ (((j >> 2) & 1))
                          for j in range(16)])
    bell = multiply(bell_c, bell_h)
    sharp_u = multiply(multiply(adjoint(bell), tensor(u, identity(4))), bell)
    require(polynomial(sharp_u, (1, 1, 1, 1, 1)) == scale(identity(16), 0),
            "Bell primitive response")
    sharp = clifford_record(sharp_u)
    require(sharp["native_B_rank"] == sharp["symplectic_defect_rank"] == 4,
            "sharp degree-four native rank")
    mixed = tensor(u, u)
    require(power(mixed, 5) == identity(16), "tensor order control")
    require(polynomial(mixed, (1, 1, 1, 1, 1)) != scale(identity(16), 0),
            "order alone is not primitive response")
    mixed_record = clifford_record(mixed)
    require(mixed_record["symplectic_defect_rank"] == 8, "tensor defect control")
    require(polynomial(scale(u, 0, 1), (1, 1, 1, 1, 1)) != zero,
            "global phase matters")
    require(polynomial(power(u, 2), (1, 1, 1, 1, 1)) == zero,
            "primitive-power positive control")
    return {"degree_four": basic, "sharp_degree_four": sharp,
            "order_only_tensor_control": mixed_record}


def permutation(images):
    n = len(images)
    require(1 <= n <= 16, "permutation dimension")
    require(sorted(images) == list(range(n)), "permutation required")
    return matrix([[(int(i == images[j]), 0) for j in range(n)] for i in range(n)])


def factors(n):
    require(type(n) is int and 1 <= n <= 4095, "factor domain 1..4095")
    result = []
    remaining = n
    for p in range(2, n+1):
        if remaining % p == 0:
            exponent = 0
            for _ in range(n.bit_length()):
                if remaining % p:
                    break
                exponent += 1
                remaining //= p
            result.append((p, exponent))
    require(remaining == 1, "factor exhaustion")
    return result


def number_checks():
    permitted = []
    cases = 0
    for n in range(3, 4096, 2):
        fs = factors(n)
        phi = sum(gcd(k, n) == 1 for k in range(1, n+1))
        product = 1
        for p, exponent in fs:
            product *= p**(exponent-1)*(p-1)
        require(product == phi, "totient independent enumeration")
        power_two = phi & (phi-1) == 0
        squarefree_fermat = all(e == 1 and (p-1) & (p-2) == 0 for p, e in fs)
        require(power_two == squarefree_fermat, "odd degree classification")
        if power_two:
            permitted.append([n, phi, 2*(phi.bit_length()-1)])
        cases += 1
    require(all(n not in (7, 9, 25, 27) for n, _, _ in permitted), "excluded orders")
    return {"odd_orders_checked": cases, "degree_permitted_orders": permitted}


def rejection_checks():
    rejected = 0
    for n in (0, 4096, -1, Fraction(3)):
        try:
            factors(n)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("factor domain accepted invalid value")
    require(rejected == 4, "domain rejection count")
    # Phi5 alone does not imply the Clifford or unitary hypothesis.
    companion = matrix([[(0, 0), (0, 0), (0, 0), (-1, 0)],
                        [(1, 0), (0, 0), (0, 0), (-1, 0)],
                        [(0, 0), (1, 0), (0, 0), (-1, 0)],
                        [(0, 0), (0, 0), (1, 0), (-1, 0)]])
    require(polynomial(companion, (1, 1, 1, 1, 1)) == scale(identity(4), 0),
            "companion primitive positive algebra control")
    try:
        clifford_record(companion)
    except ValueError as error:
        require(str(error) == "unitarity", "companion rejection reason")
        rejected += 1
    else:
        raise ValueError("nonunitary companion accepted")
    return rejected


def main():
    result = {"status": "PASS_ODD_CYCLOTOMIC_RESPONSE", "claim_type": "scoped-proof",
              "number_theory": number_checks(), "matrices": fixture_checks(),
              "invalid_domain_and_unitarity_rejections": rejection_checks()}
    directory = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["package_sha256"] = {
        name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
