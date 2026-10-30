#!/usr/bin/env python3
"""Exact finite corroboration of the matrix-algebra determinant theorem."""

import hashlib
import itertools
import json
import math
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """The seven fixed small fields used by this verifier."""

    def __init__(self, q):
        configs = {2: (2, (0, 1)), 3: (3, (0, 1)),
                   4: (2, (1, 1, 1)), 5: (5, (0, 1)),
                   7: (7, (0, 1)), 8: (2, (1, 1, 0, 1)),
                   9: (3, (1, 0, 1))}
        require(q in configs, "unsupported field")
        self.q = q
        self.p, self.modulus = configs[q]
        self.e = len(self.modulus) - 1
        self.add = tuple(tuple(self.add_raw(a, b) for b in range(q))
                         for a in range(q))
        self.mul = tuple(tuple(self.mul_raw(a, b) for b in range(q))
                         for a in range(q))
        self.neg = tuple(next(b for b in range(q) if self.add[a][b] == 0)
                         for a in range(q))
        self.inv = (0,) + tuple(next(b for b in range(1, q)
                                    if self.mul[a][b] == 1)
                                for a in range(1, q))

    def digits(self, a):
        return [(a // self.p**i) % self.p for i in range(self.e)]

    def add_raw(self, a, b):
        x, y = self.digits(a), self.digits(b)
        return sum(((x[i] + y[i]) % self.p) * self.p**i
                   for i in range(self.e))

    def mul_raw(self, a, b):
        x, y = self.digits(a), self.digits(b)
        c = [0] * (2 * self.e - 1)
        for i, j in itertools.product(range(self.e), repeat=2):
            c[i + j] = (c[i + j] + x[i] * y[j]) % self.p
        for k in range(2 * self.e - 2, self.e - 1, -1):
            for j in range(self.e):
                c[k - self.e + j] = (c[k - self.e + j]
                                     - c[k] * self.modulus[j]) % self.p
        return sum(c[i] * self.p**i for i in range(self.e))

    def power(self, a, exponent):
        require(0 <= exponent <= 128, "unsupported exponent")
        value = 1
        for _ in range(exponent):
            value = self.mul[value][a]
        return value


def identity(n):
    require(1 <= n <= 9, "unsupported matrix size")
    return tuple(int(i == j) for i in range(n) for j in range(n))


def product(a, b, n, f):
    out = [0] * (n * n)
    for i, j, k in itertools.product(range(n), repeat=3):
        out[i * n + j] = f.add[out[i * n + j]][
            f.mul[a[i * n + k]][b[k * n + j]]]
    return tuple(out)


def inverse_det(a, n, f):
    require(len(a) == n * n and 1 <= n <= 9, "invalid square matrix")
    rows = [list(a[i * n:(i + 1) * n]) + list(identity(n)[i * n:(i + 1) * n])
            for i in range(n)]
    determinant = 1
    for col in range(n):
        pivot = next((r for r in range(col, n) if rows[r][col]), None)
        if pivot is None:
            return None, 0
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            determinant = f.neg[determinant]
        scale = rows[col][col]
        determinant = f.mul[determinant][scale]
        rows[col] = [f.mul[x][f.inv[scale]] for x in rows[col]]
        for r in range(n):
            if r != col:
                coefficient = rows[r][col]
                rows[r] = [f.add[x][f.neg[f.mul[coefficient][y]]]
                           for x, y in zip(rows[r], rows[col])]
    return tuple(x for row in rows for x in row[n:]), determinant


def matrix_basis(n):
    return tuple(tuple(int(j == i) for j in range(n * n))
                 for i in range(n * n))


def linear_map(columns):
    d = len(columns)
    return tuple(columns[j][i] for i in range(d) for j in range(d))


def apply_map(a, x, f):
    d = len(x)
    out = [0] * d
    for i, j in itertools.product(range(d), repeat=2):
        out[i] = f.add[out[i]][f.mul[a[i * d + j]][x[j]]]
    return tuple(out)


def transpose(a, d):
    return tuple(a[j * d + i] for i in range(d) for j in range(d))


def autotopy(a, b, p, n, f):
    pinv, dp = inverse_det(p, n, f)
    require(dp != 0, "singular conjugator")
    sigma = tuple(product(product(p, x, n, f), pinv, n, f)
                  for x in matrix_basis(n))
    fm = linear_map(tuple(product(a, x, n, f) for x in sigma))
    gm = linear_map(tuple(product(x, b, n, f) for x in sigma))
    hm = linear_map(tuple(product(product(a, x, n, f), b, n, f)
                          for x in sigma))
    return fm, gm, hm


def check_autotopy(maps, n, f):
    fm, gm, hm = maps
    d = n * n
    determinants = tuple(inverse_det(a, d, f)[1] for a in maps)
    require(all(determinants), "singular autotopy")
    for x, y in itertools.product(matrix_basis(n), repeat=2):
        lhs = product(apply_map(fm, x, f), apply_map(gm, y, f), n, f)
        rhs = apply_map(hm, product(x, y, n, f), f)
        require(lhs == rhs, "basis-product failure")
    return tuple(f.inv[determinants[i]] if i < 2 else determinants[i]
                 for i in range(3))


def covariant_maps(maps, n, f):
    d = n * n
    return (transpose(inverse_det(maps[0], d, f)[0], d),
            transpose(inverse_det(maps[1], d, f)[0], d), maps[2])


def literal_tensor_check(maps, n, f):
    """Transform all coefficients of mu in A* tensor A* tensor A."""
    s, t, h = maps
    d = n * n
    for i, j, k in itertools.product(range(d), repeat=3):
        value = 0
        for a, b, c in itertools.product(range(n), repeat=3):
            term = f.mul[f.mul[s[i * d + a * n + b]][
                t[j * d + b * n + c]]][h[k * d + a * n + c]]
            value = f.add[value][term]
        expected = int(i % n == j // n and k == (i // n) * n + j % n)
        require(value == expected, "literal covariant tensor failure")
    return d**3


def predicted_image(n, f):
    powers = {f.power(a, n) for a in range(1, f.q)}
    return {(u, v, f.inv[f.mul[u][v]]) for u in powers for v in powers}


def equation_image(n, f):
    exponent = (f.q - 1) // math.gcd(n, f.q - 1)
    return {(u, v, w) for u, v, w in itertools.product(range(1, f.q), repeat=3)
            if f.power(u, exponent) == f.power(v, exponent) == 1
            and f.mul[f.mul[u][v]][w] == 1}


def diagonal(value, n):
    a = list(identity(n))
    a[0] = value
    return tuple(a)


def attaining_fixtures(f):
    report = []
    for n in range(1, 4):
        images = set()
        coefficients = 0
        for alpha, beta in itertools.product(range(1, f.q), repeat=2):
            p = list(identity(n))
            if n > 1:
                p[0], p[-1] = alpha, beta
                p[1] = f.add[alpha][beta]
            maps = autotopy(diagonal(alpha, n), diagonal(beta, n), tuple(p), n, f)
            triple = check_autotopy(maps, n, f)
            coefficients += literal_tensor_check(covariant_maps(maps, n, f), n, f)
            images.add(triple)
            require(triple == (f.inv[f.power(alpha, n)],
                               f.inv[f.power(beta, n)],
                               f.power(f.mul[alpha][beta], n)), "character")
        expected = predicted_image(n, f)
        require(images == expected == equation_image(n, f), "image mismatch")
        g = math.gcd(n, f.q - 1)
        orbit_count = (f.q - 1)**3 // len(images)
        require(orbit_count == (f.q - 1) * g * g, "SL orbit count")
        report.append({"q": f.q, "n": n, "stabilizers": (f.q - 1)**2,
                       "literal_tensor_coefficients": coefficients,
                       "image": sorted(images), "sl_orbits": orbit_count})
    return report


def is_automorphism(a, n, f):
    if apply_map(a, identity(n), f) != identity(n):
        return False
    for x, y in itertools.product(matrix_basis(n), repeat=2):
        if apply_map(a, product(x, y, n, f), f) != product(
                apply_map(a, x, f), apply_map(a, y, f), n, f):
            return False
    return True


def binary_automorphism_census():
    f = Field(2)
    automorphisms = set()
    invertible = 0
    for entries in itertools.product(range(2), repeat=16):
        _, determinant = inverse_det(entries, 4, f)
        if determinant:
            invertible += 1
            if is_automorphism(entries, 2, f):
                automorphisms.add(entries)
    inner = set()
    for p in itertools.product(range(2), repeat=4):
        pinv, determinant = inverse_det(p, 2, f)
        if determinant:
            inner.add(linear_map(tuple(product(product(p, x, 2, f), pinv, 2, f)
                                       for x in matrix_basis(2))))
    require(automorphisms == inner and len(inner) == 6, "complete automorphism census")
    require(invertible == 20160, "complete GL4 census")
    return {"candidate_maps": 65536, "invertible_maps": invertible,
            "automorphisms": len(automorphisms)}


def correction_fixtures(f):
    counts = {"determinant_triples": 0, "correctable": 0, "rejected": 0}
    n = 2
    image = predicted_image(n, f)
    for d1, d2, d3 in itertools.product(range(1, f.q), repeat=3):
        counts["determinant_triples"] += 1
        roots1 = [x for x in range(1, f.q) if f.power(x, n) == d1]
        roots2 = [x for x in range(1, f.q) if f.power(x, n) == d2]
        condition = bool(roots1 and roots2 and f.mul[f.mul[d1][d2]][d3] == 1)
        require(condition == ((f.inv[d1], f.inv[d2], f.inv[d3]) in image),
                "correction criterion")
        if not condition:
            counts["rejected"] += 1
            continue
        counts["correctable"] += 1
        maps = autotopy(diagonal(roots1[0], n), diagonal(roots2[0], n),
                        identity(n), n, f)
        s = covariant_maps(maps, n, f)
        for factor, target in zip(s, (d1, d2, d3)):
            g = diagonal(target, n * n)
            require(inverse_det(product(g, factor, n * n, f), n * n, f)[1] == 1,
                    "SL correction witness")
    return {"q": f.q, **counts}


def controls():
    f = Field(7)
    maps = autotopy(diagonal(2, 2), identity(2), identity(2), 2, f)
    raw = tuple(inverse_det(a, 4, f)[1] for a in maps)
    correct = check_autotopy(maps, 2, f)
    require(raw == (4, 1, 4) and correct == (2, 1, 4), "inverse convention control")
    require(raw not in predicted_image(2, f), "raw determinants falsely admitted")
    require((3, 1, 5) not in predicted_image(2, f), "nth-power restriction omitted")
    require((2, 1, 2) not in predicted_image(2, f), "product restriction omitted")
    require(len(predicted_image(2, Field(3))) == 1, "even-n restriction")
    require(len(predicted_image(3, Field(4))) == 1, "extension-field restriction")
    require(predicted_image(1, Field(4)) == equation_image(1, Field(4)), "n=1")
    require(predicted_image(3, Field(2)) == {(1, 1, 1)}, "q=2")
    bad = list(covariant_maps(maps, 2, f))
    bad[2] = identity(4)
    rejected = False
    try:
        literal_tensor_check(tuple(bad), 2, f)
    except ValueError:
        rejected = True
    require(rejected, "altered output tensor survived")
    for q, n in ((6, 1), (2, 0), (2, 10)):
        rejected = False
        try:
            identity(n) if q == 2 else Field(q)
        except ValueError:
            rejected = True
        require(rejected, "unsupported domain survived")
    return 12


def main():
    fields = tuple(Field(q) for q in (2, 3, 4, 5, 7, 8, 9))
    for f in fields:
        for a, b, c in itertools.product(range(f.q), repeat=3):
            require(f.mul[a][f.add[b][c]] == f.add[f.mul[a][b]][f.mul[a][c]],
                    "field distributivity")
    report = {"claim_type": "scoped proof with finite corroboration",
              "attainment": [r for f in fields for r in attaining_fixtures(f)],
              "binary_census": binary_automorphism_census(),
              "corrections": [correction_fixtures(f) for f in fields],
              "controls": controls()}
    root = Path(__file__).resolve().parent
    report["package_sha256"] = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                     "VERIFY.json", "verify.py")}
    print(json.dumps(report, sort_keys=True))
    print("PASS_MATRIX_TENSOR_DETERMINANT_IMAGE no_new_kappa")


if __name__ == "__main__":
    main()
