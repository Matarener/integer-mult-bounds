#!/usr/bin/env python3
"""Exact checks supporting the written caller-obstruction proof.

The universal claim follows from the displayed group relations and ring
argument, not from the finite controls below. No predecessor code is imported.
"""

import ast
import hashlib
import json
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parent
I = (1, 0, 0, 1)
X = (1, 1, 0, 1)
XI = (1, -1, 0, 1)
Y = (1, 0, 1, 1)
YI = (1, 0, -1, 1)
B = (5, 2, 2, 1)
PINS = {
    "source/sl2z-README.md": (
        "b27bf4c72a822b21f483e08cb3241ad9d165b66f",
        "f8c354eeb9cc3b60ed4d0da5a58329517c33cd4d",
        "fb475d7cf4de6df3c258d7a9366ef1b3edc61302370f9081c299353ab59b35b1",
    ),
    "source/sl2z-verify.py": (
        "b27bf4c72a822b21f483e08cb3241ad9d165b66f",
        "db16b86750aa558ade71db2efb3a8c2d38853e20",
        "653acaedf1119e232edb681428c707292e717860be01c25801066b10cfd97364",
    ),
    "source/a5-README.md": (
        "e44c63550d59173d7f5425b97c7fe22764214e0b",
        "5a665e77455339daac0cc5aedebae761c6161d31",
        "ea4708432e3a53db38c22ecb43b5988d86e6cdf9e8f956a45502bd5f6a5a060f",
    ),
    "source/additive-README.md": (
        "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "25e41c370c101a33a6deb978de08b03ed7539b79",
        "c12b33ef388deece0cbf891505a2ce2c0779a0c3a6cf1f0f7f7039bab59cbebd",
    ),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check_sources():
    manifest = json.loads((ROOT / "SOURCE-ORIGINS.json").read_text())
    require(manifest["repository"] == "CrocSwap/integer-mult-bounds", "source repository changed")
    entries = manifest["files"]
    require(len(entries) == len(PINS), "source count changed")
    require({entry["path"] for entry in entries} == set(PINS), "source paths changed")
    for entry in entries:
        pin = PINS[entry["path"]]
        require(tuple(entry[k] for k in ("upstream_commit", "git_blob", "sha256")) == pin,
                "source provenance changed: " + entry["path"])
        raw = (ROOT / entry["path"]).read_bytes()
        blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == pin[1], "source Git blob mismatch: " + entry["path"])
        require(hashlib.sha256(raw).hexdigest() == pin[2], "source SHA256 mismatch: " + entry["path"])
    expected = {"IDENTITY": I, "X": X, "XI": XI, "Y": Y, "YI": YI, "EXPECTED": B}
    constants = {}
    for node in ast.parse((ROOT / "source/sl2z-verify.py").read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in expected:
                require(target.id not in constants, "duplicate predecessor constant")
                constants[target.id] = ast.literal_eval(node.value)
    require(constants == expected, "predecessor constants disagree with the audited model")


def mul(a, b, modulus=None):
    value = tuple(sum(a[2 * i + k] * b[2 * k + j] for k in range(2))
                  for i in range(2) for j in range(2))
    return value if modulus is None else tuple(x % modulus for x in value)


def power(a, n, multiply=mul, identity=I):
    result = identity
    for _ in range(n):
        result = multiply(result, a)
    return result


def check_integer_relations():
    require(mul(X, XI) == mul(XI, X) == I, "bad X inverse")
    require(mul(Y, YI) == mul(YI, Y) == I, "bad Y inverse")
    s = mul(mul(X, YI), X)
    require(s == mul(mul(YI, X), YI) == (0, 1, -1, 0), "braid relation failed")
    require(power(s, 2) == (-1, 0, 0, -1) and power(s, 4) == I, "order-four relation failed")
    require(mul(power(X, 2), power(Y, 2)) == B != I, "target changed or became identity")
    require((B[0] - 1) * (B[3] - 1) - B[1] * B[2] == -4, "target rank changed")
    require(mul(X, Y) != mul(Y, X), "native shear generators unexpectedly commute")


def check_symbolic_implications():
    # Exponents of commuting units U,V. Cancelling units from the braid
    # identity gives U*V=1 in every commutative ring, even with zero divisors.
    left, right = (2, -1), (1, -2)
    relation = tuple(a - b for a, b in zip(left, right))
    require(relation == (1, 1), "wrong Laurent cancellation")
    require((2, 2) == tuple(2 * e for e in relation), "B is not twice the cancelled relation")
    reduce_exponent = lambda e: e[0] - e[1]  # V=U^-1
    require(reduce_exponent((2, 2)) == 0, "target survives commutative quotient")
    require(4 * reduce_exponent(left) == 12, "wrong generator torsion bound")
    # Nonzero same-sign rational labels fail the original braid equality.
    evaluate = lambda e, uv: sum(a * b for a, b in zip(e, uv))
    require(evaluate(left, (1, 1)) != evaluate(right, (1, 1)), "same-sign invalid map accepted")
    require(evaluate(left, (1, -1)) == evaluate(right, (1, -1)), "braid control failed")
    require(4 * evaluate(left, (1, -1)) != 0, "order-four obstruction lost")
    # Exact F2[t] identities used by the domain-plus-augmentation argument.
    # Polynomials are sets of exponents with coefficient one.
    def polynomial_mul(a, b):
        result = set()
        for i in a:
            for j in b:
                if i + j in result:
                    result.remove(i + j)
                else:
                    result.add(i + j)
        return result
    require(power({0, 3}, 4, polynomial_mul, {0}) == {0, 12}, "Frobenius identity failed")
    require(polynomial_mul({0, 1}, {0, 1, 2}) == {0, 3}, "cubic factorization failed")
    require(len({0, 1, 2}) % 2 == 1, "augmentation of the second factor must be one")


def residue_character(modulus, order):
    """Verify an actual finite quotient character, not just two relations."""
    reduce_matrix = lambda a: tuple(x % modulus for x in a)
    generators = ((reduce_matrix(X), 1), (reduce_matrix(Y), -1))
    values, pending = {I: 0}, [I]
    while pending:
        a = pending.pop()
        for generator, weight in generators:
            b = mul(a, generator, modulus)
            value = (values[a] + weight) % order
            if b in values:
                require(values[b] == value, "inconsistent quotient character")
            else:
                values[b] = value
                pending.append(b)
    whole_group = {a for a in product(range(modulus), repeat=4)
                   if (a[0] * a[3] - a[1] * a[2]) % modulus == 1}
    require(set(values) == whole_group, "generators did not produce the declared finite quotient")
    for a, b in product(values, repeat=2):
        require(values[mul(a, b, modulus)] == (values[a] + values[b]) % order,
                "quotient character does not preserve multiplication")
    require(values[reduce_matrix(B)] == 0, "B survived an abelian character")
    return values


def f4_mul(a, b):
    result = 0
    for j in range(2):
        if (b >> j) & 1:
            result ^= a << j
    if result & 4:
        result ^= 7  # omega^2 + omega + 1
    return result


def dual_mul(a, b):
    # a=a0+a1*epsilon, epsilon^2=0.
    return ((a & 1) & (b & 1)) | ((((a & 1) & (b >> 1)) ^ ((a >> 1) & (b & 1))) << 1)


def check_ring_control(values, multiply, generator, order, modulus):
    images = {a: power(generator, exponent, multiply, 1) for a, exponent in values.items()}
    require(power(generator, order, multiply, 1) == 1 and generator != 1, "control unit collapsed")
    for a, b in product(values, repeat=2):
        require(images[mul(a, b, modulus)] == multiply(images[a], images[b]), "ring-valued character failed")
    # Together with linear extension over F2, this is a unital algebra map
    # from the original group algebra via matrix reduction modulo 2 or 3.
    u = images[tuple(x % modulus for x in X)]
    v = images[tuple(y % modulus for y in Y)]
    require(u != 1 and v != 1 and multiply(u, v) == 1, "wrong nontrivial generator control")
    require(multiply(multiply(u, u), multiply(v, v)) == 1, "target should still collapse")


def check_boundary_controls():
    mod3 = residue_character(3, 3)
    mod2 = residue_character(2, 2)
    require((len(mod3), len(mod2)) == (24, 6), "finite quotient size mismatch")
    check_ring_control(mod3, f4_mul, 2, 3, 3)
    require(all(f4_mul(a, b) != 0 for a in range(1, 4) for b in range(1, 4)), "F4 is not a field")
    # F4 is a domain but has no F2-valued augmentation: omega maps to 0 or1,
    # and neither is a root of t^2+t+1. Domain alone cannot force U=1.
    require(all((a * a + a + 1) % 2 == 1 for a in (0, 1)), "unexpected F4 retraction")
    check_ring_control(mod2, dual_mul, 3, 2, 2)
    require(dual_mul(2, 2) == 0 and 2 != 0, "dual-number nilpotent missing")
    require(all((dual_mul(a, b) & 1) == ((a & 1) * (b & 1)) for a, b in product(range(4), repeat=2)),
            "dual-number augmentation failed")

    points = tuple(v for v in product(range(3), repeat=2) if v != (0, 0))
    def permutation(a):
        return tuple(points.index(((a[0] * v[0] + a[1] * v[1]) % 3,
                                   (a[2] * v[0] + a[3] * v[1]) % 3)) for v in points)
    compose = lambda a, b: tuple(a[b[i]] for i in range(8))
    action = {a: permutation(a) for a in mod3}
    require(all(sorted(p) == list(range(8)) for p in action.values()), "invalid native permutation")
    for a, b in product(mod3, repeat=2):
        require(action[mul(a, b, 3)] == compose(action[a], action[b]), "noncommutative action failed")
    px, py, pb = permutation(X), permutation(Y), permutation(B)
    require(compose(px, py) != compose(py, px), "escape carrier became commutative")
    require(compose(compose(px, px), compose(py, py)) == pb, "escape target identity failed")
    require(sum(i != j for i, j in enumerate(pb)) == 8, "escape carrier did not preserve nontrivial B")


def main():
    check_sources()
    check_integer_relations()
    check_symbolic_implications()
    check_boundary_controls()
    print("PASS_SL2Z_COMMUTATIVE_CALLER sources=4 relations=2 target_killed=1 "
          "rational_generators_killed=1 quotient_sizes=24,6 "
          "f4_control=1 dual_number_control=1 noncommutative_moved=8 no_new_kappa")


if __name__ == "__main__":
    main()
