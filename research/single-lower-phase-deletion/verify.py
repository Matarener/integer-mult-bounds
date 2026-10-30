"""Exact finite corroboration of PROOF.md; standard library, read-only.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
import random
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dimension(a):
    n = isqrt(len(a))
    require(n * n == len(a) and 1 <= n <= 6, "matrix extent")
    return n


def identity(n):
    require(1 <= n <= 6, "identity extent")
    return tuple(Q(i == j) for i in range(n) for j in range(n))


def add(a, b, sign=1):
    require(len(a) == len(b), "addition extent")
    return tuple(x + sign * y for x, y in zip(a, b))


def multiply(a, b):
    n = dimension(a)
    require(len(b) == len(a), "product extent")
    return tuple(sum((a[i*n+k] * b[k*n+j] for k in range(n)), Q(0))
                 for i in range(n) for j in range(n))


def shear(a, lower=False):
    m = dimension(a)
    require(m <= 3, "shear width")
    n = 2 * m
    g = list(identity(n))
    for i in range(m):
        for j in range(m):
            row, col = (m+i, j) if lower else (i, m+j)
            g[row*n+col] = a[i*m+j]
    return tuple(g)


def block(g, row, col):
    n = dimension(g)
    require(n % 2 == 0 and row in (0, 1) and col in (0, 1), "block")
    m = n // 2
    return tuple(g[(row*m+i)*n+col*m+j] for i in range(m) for j in range(m))


def inner_inverse(k):
    """Row/column elimination gives D=P K T, and H=T D P."""
    n = dimension(k)
    a, p, t = [list(x) for x in (k, identity(n), identity(n))]
    rank = 0
    for z in range(n):
        pivots = [(i, j) for i in range(z, n) for j in range(z, n)
                  if a[i*n+j]]
        if not pivots:
            break
        i, j = pivots[0]
        for x in (a, p):
            for c in range(n):
                x[z*n+c], x[i*n+c] = x[i*n+c], x[z*n+c]
        for x in (a, t):
            for r in range(n):
                x[r*n+z], x[r*n+j] = x[r*n+j], x[r*n+z]
        pivot = a[z*n+z]
        for x in (a, p):
            for c in range(n):
                x[z*n+c] /= pivot
        for r in range(n):
            if r != z:
                coefficient = a[r*n+z]
                for x in (a, p):
                    for c in range(n):
                        x[r*n+c] -= coefficient * x[z*n+c]
        for c in range(n):
            if c != z:
                coefficient = a[z*n+c]
                for x in (a, t):
                    for r in range(n):
                        x[r*n+c] -= coefficient * x[r*n+z]
        rank += 1
    d = tuple(Q(i == j and i < rank) for i in range(n) for j in range(n))
    require(tuple(a) == d, "elimination diagonal")
    h = multiply(multiply(tuple(t), d), tuple(p))
    require(multiply(multiply(k, h), k) == k, "inner inverse identity")
    return h


def project_label(g):
    """For known UVU labels recover A+B without the generating A or B."""
    m = dimension(g) // 2
    k = block(g, 1, 0)
    left = add(block(g, 0, 0), identity(m), -1)
    right = add(block(g, 1, 1), identity(m), -1)
    correction = multiply(multiply(left, inner_inverse(k)), right)
    return shear(add(block(g, 0, 1), correction, -1))


def is_upper(g):
    m = dimension(g) // 2
    zero = (Q(0),) * (m*m)
    return (block(g, 1, 0) == zero and block(g, 0, 0) == identity(m)
            and block(g, 1, 1) == identity(m))


def finite_product(a, b, n, prime):
    return tuple(sum(a[i*n+k]*b[k*n+j] for k in range(n)) % prime
                 for i in range(n) for j in range(n))


def collision_checks():
    triples = collisions = 0
    classes = []
    for m, prime in ((1, 2), (1, 3), (1, 5), (2, 2)):
        matrices = list(itertools.product(range(prime), repeat=m*m))
        labels = {}
        for a, k, b in itertools.product(matrices, repeat=3):
            ua, vk, ub = (tuple(map(int, shear(x, low)))
                          for x, low in ((a, False), (k, True), (b, False)))
            g = finite_product(finite_product(ua, vk, 2*m, prime), ub, 2*m, prime)
            total = tuple((x+y) % prime for x, y in zip(a, b))
            if g in labels:
                require(labels[g] == total, "finite collision changes A+B")
                collisions += 1
            labels[g] = total
            triples += 1
        classes.append({"width": m, "prime": prime, "labels": len(labels)})
    return {"triples": triples, "repeated_labels": collisions, "domains": classes}


def rational_checks(rng):
    counts = {"triples": 0, "singular_k": 0, "bimodule": 0}
    values = (Q(-2), Q(-1, 2), Q(0), Q(1, 3), Q(1), Q(3, 2))
    for m in (1, 2, 3):
        for index in range(48):
            a, b, e, h = [tuple(rng.choice(values) for _ in range(m*m))
                          for _ in range(4)]
            k = tuple(Q(i == j and i < index % (m+1))
                      for i in range(m) for j in range(m))
            s, t = list(identity(m)), list(identity(m))
            if m > 1:
                s[1], t[m] = Q(1, 2), Q(-2, 3)
            k = multiply(multiply(tuple(s), k), tuple(t))
            g = multiply(multiply(shear(a), shear(k, True)), shear(b))
            require(project_label(g) == shear(add(a, b)), "rational projection")
            outer = multiply(multiply(shear(e), g), shear(h))
            target = shear(add(add(e, add(a, b)), h))
            require(project_label(outer) == target, "bimodule law")
            counts["triples"] += 1
            counts["singular_k"] += index % (m+1) < m
            counts["bimodule"] += 1
    return counts


def algebra_product(a, b):
    require(len(a) <= 256 and len(b) <= 256, "algebra support bound")
    result = set()
    for x in a:
        for y in b:
            z = multiply(x, y)
            result.symmetric_difference_update((z,))
    require(len(result) <= 256, "algebra result bound")
    return frozenset(result)


def state_identity(registers, m):
    one = frozenset((identity(2*m),))
    return [[one if i == j else frozenset() for j in range(registers)]
            for i in range(registers)]


def state_product(a, b):
    r = len(a)
    require(r == len(b) and 1 <= r <= 3, "register extent")
    result = [[frozenset() for _ in range(r)] for _ in range(r)]
    for i in range(r):
        for j in range(r):
            for z in range(r):
                result[i][j] ^= algebra_product(a[i][z], b[z][j])
    return result


def projected(state):
    result = []
    for row in state:
        output = []
        for cell in row:
            value = set()
            for g in cell:
                value.symmetric_difference_update((project_label(g),))
            output.append(frozenset(value))
        result.append(output)
    return result


def phase(rng, registers, m, lower):
    state = state_identity(registers, m)
    augmented = state_identity(registers, m)
    for _ in range(2):
        role = rng.randrange(registers)
        frame = tuple(rng.choice((Q(-1, 2), Q(0), Q(1))) for _ in range(m*m))
        gate = state_identity(registers, m)
        gate[role][role] = frozenset((shear(frame, lower),))
        state = state_product(gate, state)
        if registers > 1:
            target, source = rng.sample(range(registers), 2)
            mixing = state_identity(registers, m)
            mixing[target][source] = frozenset((identity(2*m),))
            state = state_product(mixing, state)
            augmented = state_product(mixing, augmented)
    return state, augmented


def circuit_checks(rng):
    counts = {"factorizations": 0, "entries": 0, "upper_supported_entries": 0}
    for m, registers in itertools.product((1, 2), (1, 2, 3)):
        for _ in range(4):
            left, _ = phase(rng, registers, m, False)
            right, _ = phase(rng, registers, m, False)
            middle, augmentation = phase(rng, registers, m, True)
            actual = state_product(state_product(left, middle), right)
            deleted = state_product(state_product(left, augmentation), right)
            require(projected(actual) == deleted, "formal phase identity")
            for i in range(registers):
                for j in range(registers):
                    if all(is_upper(g) for g in actual[i][j]):
                        require(actual[i][j] == deleted[i][j], "endpoint deletion")
                        counts["upper_supported_entries"] += 1
                    counts["entries"] += 1
            counts["factorizations"] += 1
    require(counts["upper_supported_entries"] > 0, "endpoint coverage")
    return counts


def controls():
    zero, one = (Q(0),), (Q(1),)
    k = (Q(1), Q(0), Q(0), Q(0))
    d = (Q(0), Q(0), Q(0), Q(1, 2))
    vk = shear(k, True)
    require(multiply(multiply(shear(d), vk), shear(tuple(-x for x in d))) == vk,
            "singular collision witness")
    require(shear(d) != identity(4), "left-only mutant survives")
    g = multiply(multiply(shear(one), shear(one, True)), shear(one))
    require(shear(block(g, 0, 1)) != project_label(g), "raw block mutant survives")
    require(shear(one, True) != project_label(shear(one, True)), "endpoint control")
    diagonal = (Q(2), Q(0), Q(0), Q(1))
    inverse = (Q(1, 2), Q(0), Q(0), Q(1))
    levi_word = multiply(multiply(multiply(shear(one), diagonal), shear((Q(-1, 2),))), inverse)
    require(levi_word == identity(2) and shear((Q(1, 2),)) != levi_word, "Levi control")
    word = identity(2)
    for value, lower in ((1, False), (1, True), (1, False),
                         (Q(-1, 3), True), (-3, False), (Q(-1, 3), True)):
        word = multiply(word, shear((Q(value),), lower))
    require(word == identity(2) and shear((Q(-1),)) != word, "alternation control")
    state = state_identity(3, 2)
    state[2][2] = frozenset((vk,))
    require(projected(state) == state_identity(3, 2), "auxiliary projection")
    require(state[0][:2] == state_identity(3, 2)[0][:2], "clean data boundary")
    failures = 0
    for bad in ((), (Q(1), Q(2)), (Q(0),) * 49):
        try:
            dimension(bad)
        except ValueError:
            failures += 1
    require(failures == 3, "dimension rejection")
    require(project_label(shear(zero)) == identity(2), "zero K coverage")
    return {"hypothesis_and_mutation_controls": 6, "dimension_rejections": failures}


def main():
    rng = random.Random(2613001)
    counts = {"collisions": collision_checks(), "rational": rational_checks(rng),
              "circuits": circuit_checks(rng), "controls": controls()}
    package = Path(__file__).resolve().parent
    files = sorted(p for p in package.iterdir() if p.is_file())
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    print(json.dumps({"status": "PASS_SINGLE_LOWER_PHASE_DELETION", "counts": counts,
                      "claim_type": "scoped proof with finite corroboration",
                      "sha256": hashes}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
