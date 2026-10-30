"""Bounded independent corroboration of the new isomorphism classification.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
from pathlib import Path
import random

from algebra import (canonical_chart, determinant, eye, inverse, isomorphism,
                     mm, mv, need, normalize_form, recover_form,
                     transpose, validate)


def symmetric_forms(p, r):
    positions = [(i, j) for i in range(r) for j in range(i, r)]
    for values in itertools.product(range(p), repeat=len(positions)):
        b = [[0] * r for _ in range(r)]
        for (i, j), value in zip(positions, values):
            b[i][j] = b[j][i] = value
        yield b


def literal_determinant(a, p):
    r = len(a)
    total = 0
    for permutation in itertools.permutations(range(r)):
        term = 1
        for i in range(r):
            term *= a[i][permutation[i]]
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(r) for j in range(i + 1, r))
        total += (-1) ** inversions * term
    return total % p


def key(b):
    return tuple(x for row in b for x in row)


def orbit_oracle(p, r):
    nonsquare = next(x for x in range(2, p) if x not in {y * y % p for y in range(p)})
    representatives = [eye(r)]
    if r % 2 == 0:
        other = eye(r)
        other[-1][-1] = nonsquare
        representatives.append(other)
    classes = {}
    matrices = 0
    for entries in itertools.product(range(p), repeat=r * r):
        a = [list(entries[i * r:(i + 1) * r]) for i in range(r)]
        if literal_determinant(a, p) == 0:
            continue
        matrices += 1
        for label, b in enumerate(representatives):
            for c in range(1, p):
                # Direct coefficient formula, independent of normalization.
                image = [[c * sum(a[k][i] * b[k][l] * a[l][j]
                                  for k in range(r) for l in range(r)) % p
                          for j in range(r)] for i in range(r)]
                fingerprint = key(image)
                need(fingerprint not in classes or classes[fingerprint] == label,
                     "predicted classes intersect")
                classes[fingerprint] = label
    checked = 0
    for b in symmetric_forms(p, r):
        if literal_determinant(b, p):
            signature, _, _ = normalize_form(b, p)
            need(key(b) in classes and signature == [r, classes[key(b)]],
                 "complete orbit disagrees with signature")
            checked += 1
    need(len(classes) == checked, "orbit domain coverage")
    return matrices, checked


def model_table(b, p):
    n = len(b) + 2
    t = [[[0] * n for _ in range(n)] for _ in range(n)]
    for i in range(n):
        t[0][i][i] = t[i][0][i] = 1
    for i in range(n - 2):
        for j in range(n - 2):
            t[i + 1][j + 1][-1] = b[i][j]
    return t


def model_product(b, a, c, p):
    r = len(b)
    middle = [(a[0] * c[i + 1] + c[0] * a[i + 1]) % p for i in range(r)]
    last = (a[0] * c[-1] + c[0] * a[-1]
            + sum(a[i + 1] * b[i][j] * c[j + 1]
                  for i in range(r) for j in range(r))) % p
    return [a[0] * c[0] % p] + middle + [last]


def changed_table(b, q, p):
    qi = inverse(q, p)
    columns = transpose(q)
    return [[mv(qi, model_product(b, a, c, p), p)
             for c in columns] for a in columns]


def random_chart(n, p, rng):
    q = eye(n)
    for _ in range(4 * n):
        i, j = rng.sample(range(n), 2)
        c = rng.randrange(1, p)
        q[i] = [(x + c * y) % p for x, y in zip(q[i], q[j])]
    # One scale and a swap also move the unit and socle coordinates.
    scale = rng.randrange(1, p)
    q[0] = [scale * x % p for x in q[0]]
    q[0], q[-1] = q[-1], q[0]
    need(determinant(q, p) != 0, "fixture chart")
    return q


def check_homomorphism(t, other, f, p):
    need(f is not None and determinant(f, p) != 0, "invertible transporter")
    n = len(t)
    columns = transpose(f)
    count = 0
    for i in range(n):
        for j in range(n):
            actual = [sum(columns[i][a] * columns[j][b] * other[a][b][k]
                          for a in range(n) for b in range(n)) % p
                      for k in range(n)]
            need(actual == mv(f, t[i][j], p), "transported basis product")
            count += 1
    return count


def form_checks():
    total = 0
    for p, r in ((3, 1), (3, 2), (3, 3), (3, 4),
                 (5, 1), (5, 2), (5, 3), (7, 1), (7, 2)):
        for b in symmetric_forms(p, r):
            d = literal_determinant(b, p)
            need(d == determinant(b, p), "independent determinant")
            if not d:
                continue
            signature, q, scale = normalize_form(b, p)
            canonical = eye(r)
            if signature[1]:
                canonical[-1][-1] = next(x for x in range(2, p)
                                         if pow(x, (p - 1) // 2, p) == p - 1)
            expected = [[scale * x % p for x in row] for row in canonical]
            need(mm(mm(transpose(q), b, p), q, p) == expected,
                 "literal similarity certificate")
            total += 1
    return total


def algebra_checks():
    rng = random.Random(5540)
    fixtures = products = mutations = 0
    for p in (3, 5, 7):
        nonsquare = next(x for x in range(2, p) if pow(x, (p - 1) // 2, p) == p - 1)
        for r in range(1, 5):
            for last in (1, nonsquare):
                b = eye(r)
                b[-1][-1] = last
                for _ in range(4):
                    t = changed_table(b, random_chart(r + 2, p, rng), p)
                    other = changed_table(b, random_chart(r + 2, p, rng), p)
                    signature, chart = canonical_chart(t, p)
                    canonical = eye(r)
                    canonical[-1][-1] = nonsquare if signature[1] else 1
                    products += check_homomorphism(model_table(canonical, p), t, chart, p)
                    f = isomorphism(t, other, p)
                    products += check_homomorphism(t, other, f, p)
                    corrupt = [row[:] for row in f]
                    unit = validate(t, p)
                    j = next(j for j, coefficient in enumerate(unit) if coefficient)
                    corrupt[0][j] = (corrupt[0][j] + 1) % p
                    try:
                        check_homomorphism(t, other, corrupt, p)
                    except ValueError:
                        mutations += 1
                    else:
                        raise ValueError("changed transporter accepted")
                    fixtures += 1
            a = model_table(eye(r), p)
            b[-1][-1] = nonsquare
            result = isomorphism(a, model_table(b, p), p)
            need((result is None) == (r % 2 == 0), "odd/even class boundary")
    return fixtures, products, mutations


def rejection_checks():
    base = model_table(eye(2), 3)
    zero_square = model_table([[0, 0], [0, 0]], 3)
    extra_socle = model_table([[1, 0], [0, 0]], 3)
    truncated = [[[0] * 4 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4 - i):
            truncated[i][j][i + j] = 1
    product_fields = [[[int(i == j == k) for k in range(3)]
                       for j in range(3)] for i in range(3)]
    noncommutative = json.loads(json.dumps(base))
    noncommutative[1][2][-1] = 1
    nonassociative = json.loads(json.dumps(base))
    nonassociative[1][1][1] = 1
    boolean = json.loads(json.dumps(base))
    boolean[0][0][0] = True
    bad = [(base, 2), (base, 9), (base, 37), (base[:-1], 3),
           (zero_square, 3), (extra_socle, 3), (truncated, 3),
           (product_fields, 3), (noncommutative, 3), (nonassociative, 3),
           (boolean, 3), ([[[0] * 3 for _ in range(3)] for _ in range(3)], 3)]
    for t, p in bad:
        try:
            recover_form(t, p)
        except ValueError:
            continue
        raise ValueError("invalid or out-of-class algebra accepted")
    return len(bad)


def main():
    forms = form_checks()
    orbit_counts = [orbit_oracle(p, r) for p, r in ((3, 2), (5, 2), (7, 2), (3, 3))]
    fixtures, products, mutations = algebra_checks()
    controls = rejection_checks()
    package = Path(__file__).resolve().parent
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(package.iterdir())
              if path.is_file() and path.suffix in (".py", ".md", ".json")}
    print(json.dumps({"status": "PASS_CUBE_ZERO_GORENSTEIN_ISOMORPHISM",
                      "nonsingular_forms": forms, "complete_orbit_domains": orbit_counts,
                      "changed_presentations": fixtures, "basis_products": products,
                      "transporter_mutations": mutations, "rejections": controls,
                      "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
