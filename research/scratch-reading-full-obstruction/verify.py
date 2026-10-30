#!/usr/bin/env python3
"""Finite corroboration in F2[S3^3], with no predecessor imports or writes.

The written proof is universal. Live allocation is bounded by the fixed
216-element algebra, four owners, and 736 explicitly enumerated cases.
"""
from itertools import permutations, product
from hashlib import sha256
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def algebra():
    perms = tuple(permutations(range(3)))
    mul6 = tuple(tuple(perms.index(tuple(a[b[i]] for i in range(3)))
                       for b in perms) for a in perms)
    words = tuple(product(range(6), repeat=3))
    index = {word: i for i, word in enumerate(words)}
    table = tuple(tuple(index[tuple(mul6[a[k]][b[k]] for k in range(3))]
                        for b in words) for a in words)
    # permutations[2] is (1,0,2); these two elements form a subgroup.
    h = tuple(i for i, w in enumerate(words) if all(x in (0, 2) for x in w))
    grades = tuple(sum(x not in (0, 2) for x in w) for w in words)
    keep = sum(1 << i for i, grade in enumerate(grades) if grade <= 2)
    need(len(words) == 216 and len(h) == 8, "wrong algebra dimensions")
    return words, table, h, grades, keep


def support(value):
    need(type(value) is int and 0 <= value < (1 << 216), "invalid algebra element")
    return tuple(i for i in range(value.bit_length()) if value >> i & 1)


def mul(a, b, table):
    answer = 0
    for i in support(a):
        for j in support(b):
            answer ^= 1 << table[i][j]
    return answer


def shear(vector, dst, src, coefficient, table):
    need(0 <= dst < len(vector) and 0 <= src < len(vector) and dst != src,
         "invalid shear endpoints")
    out = list(vector)
    out[dst] ^= mul(coefficient, vector[src], table)
    return tuple(out)


def diagonal(vector, units, table):
    need(len(vector) == len(units), "wrong diagonal size")
    return tuple(mul(1 << unit, entry, table) for unit, entry in zip(units, vector))


def free(vector, variant, h, table):
    n = len(vector)
    out = vector
    for k in range(2 * n):
        src = (k + variant) % n
        dst = (src + 1 + k % (n - 1)) % n
        # Elementary controls stay invertible with zero-divisor coefficients.
        coefficient = (1 << h[(k + variant) % 8]) ^ (1 << h[(k + 3) % 8])
        out = shear(out, dst, src, coefficient, table)
    return out[variant % n:] + out[:variant % n]


def packed(vector, keep):
    return sum((entry & keep) << (216 * i) for i, entry in enumerate(vector))


def binary_rank(columns):
    need(len(columns) <= 32, "rank capacity exceeded")
    basis = {}
    for original in columns:
        value = original
        for _ in range(32):
            if not value:
                break
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
        else:
            need(not value, "elimination capacity exhausted")
    return len(basis)


def fixture(n, first, second, variant, context):
    words, table, h, grades, keep = context
    low = tuple(i for i, g in enumerate(grades) if g == 1)
    high = tuple(i for i, g in enumerate(grades) if g == 3)
    d1 = tuple(low[(7 * i + variant) % 48] if i < 2 or variant & 1 else 0
               for i in range(n))
    d2 = tuple(low[(11 * i + 5 + variant) % 48] if i < 2 or variant & 1 else 0
               for i in range(n))
    q1 = 1 << high[variant]
    q2 = (1 << high[variant + 2]) ^ (1 << low[variant + 9])
    if variant & 2:
        q1 ^= 1 << low[variant + 1]
    columns, restricted, outer = [], [], []
    for owner, b in product(range(n), h):
        vector = tuple((1 << b) if i == owner else 0 for i in range(n))
        mid = shear(vector, *first, q1, table)
        mid = free(diagonal(mid, d1, table), variant, h, table)
        out = diagonal(shear(mid, *second, q2, table), d2, table)
        columns.append(packed(out, keep))
        if owner != first[1]:
            restricted.append(packed(out, keep))
        # A separately executed whole map includes outer B-controls.
        mid = free(vector, variant + 1, h, table)
        mid = diagonal(shear(mid, *first, q1, table), d1, table)
        mid = free(mid, variant, h, table)
        mid = diagonal(shear(mid, *second, q2, table), d2, table)
        outer.append(packed(free(mid, variant + 2, h, table), keep))
    floor = (n - 1) * len(h)
    need(binary_rank(restricted) == floor, "restriction is not injective")
    rank = binary_rank(columns)
    need(rank >= floor, "projected rank below theorem bound")
    need(binary_rank(outer) == rank, "outer B-control changed projected rank")
    target = []
    for owner, b in product(range(n), h):
        entry = mul(1 << high[0], 1 << b, table) if owner < 2 else 1 << b
        target.append(packed(tuple(entry if i == owner else 0 for i in range(n)), keep))
    need(binary_rank(target) == (n - 2) * len(h), "wrong target image")
    return rank


def controls(context):
    words, table, h, grades, keep = context
    g = words.index((1, 1, 1))
    inverse = next(i for i in range(216) if table[g][i] == table[i][g] == 0)
    a, b = words.index((1, 0, 0)), words.index((0, 1, 0))
    lowkeep = sum(1 << i for i, grade in enumerate(grades) if grade <= 1)
    checked = []
    for n in (2, 3, 4):
        columns, below, nonfree, nonunit, three = [], [], [], [], []
        for owner, x in product(range(n), h):
            v = tuple((1 << x) if i == owner else 0 for i in range(n))
            z = shear(shear(v, 1, 0, 1 << g, table), 0, 1, 1 << inverse, table)
            columns.append(packed(z, keep))
            z = diagonal(diagonal(v, (a,) * n, table), (b,) * n, table)
            below.append(packed(z, lowkeep))
            nonfree.append(packed(diagonal(v, (g,) * n, table), keep))
            nonunit.append(packed(tuple(0 for _ in v), keep))
            # A third query and a scalar owner swap attain two high targets.
            z = shear(shear(shear(v, 0, 1, 1 << g, table),
                            1, 0, 1 << inverse, table), 0, 1, 1 << g, table)
            z = (z[1], z[0]) + z[2:]
            three.append(packed(z, keep))
        need(binary_rank(columns) == (n - 1) * 8, "sharpness fixture failed")
        need(binary_rank(below) == 0, "cutoff control failed")
        need(binary_rank(nonfree) == 0, "non-B control failed")
        need(binary_rank(nonunit) == 0, "nonunit control failed")
        need(binary_rank(three) == (n - 2) * 8, "third-query control failed")
        checked.extend(f"n{n}:{name}" for name in
                       ("sharpness", "cutoff", "nonfree", "nonunit", "third_query"))
    nilpotent = 1 ^ (1 << h[1])
    need(nilpotent != 0 and mul(nilpotent, nilpotent, table) == 0,
         "zero-divisor control failed")
    p, q = words.index((1, 0, 0)), words.index((2, 0, 0))
    need(table[p][q] != table[q][p], "noncommutative control failed")
    checked.extend(("nilpotent_free_coefficient", "noncommutativity"))
    try:
        shear((1, 1), 0, 0, 1, table)
    except ValueError:
        checked.append("same_owner_rejected")
        return checked
    raise ValueError("diagonal shear was accepted")


def arithmetic_checks(context):
    _, table, h, grades, _ = context
    products_checked = 0
    for a, b in product(range(216), repeat=2):
        need(grades[table[a][b]] <= grades[a] + grades[b], "grade is not subadditive")
        if a in h:
            need(grades[table[a][b]] == grades[b], "left B-invariance failed")
        if b in h:
            need(grades[table[a][b]] == grades[a], "right B-invariance failed")
        products_checked += 1
    matrices_checked = 0
    for rows, cols in product(range(4), repeat=2):
        for bits in range(1 << (rows * cols)):
            columns = tuple((bits >> (rows * i)) & ((1 << rows) - 1)
                            for i in range(cols))
            span = {0}
            for column in columns:
                span = span | {x ^ column for x in span}
            need(len(span) == 1 << binary_rank(columns), "rank/span oracle disagrees")
            matrices_checked += 1
    return {"grade_products": products_checked, "rank_oracle_matrices": matrices_checked}


def verify():
    context = algebra()
    counts = {"cases": 0, "scratch_read": 0, "scratch_write": 0,
              "scratch_to_scratch": 0, "original_transverse_placement": 0}
    histogram = {}
    for n in (2, 3, 4):
        pairs = tuple((i, j) for i, j in product(range(n), repeat=2) if i != j)
        for first, second, variant in product(pairs, pairs, range(4)):
            rank = fixture(n, first, second, variant, context)
            counts["cases"] += 1
            counts["scratch_read"] += first[1] >= 2 or second[1] >= 2
            counts["scratch_write"] += first[0] >= 2 or second[0] >= 2
            counts["scratch_to_scratch"] += min(first) >= 2 or min(second) >= 2
            counts["original_transverse_placement"] += not variant & 1
            key = f"n{n}:rank{rank}"
            histogram[key] = histogram.get(key, 0) + 1
    need(counts["cases"] == 736, "incomplete owner-pair enumeration")
    checked = controls(context)
    result = {"status": "PASS_SCRATCH_READING_FULL_OBSTRUCTION", **counts,
              "algebra_dimension": 216, "subgroup_dimension": 8,
              "controls": len(checked), "control_names": checked,
              "rank_histogram": histogram, **arithmetic_checks(context),
              "source_sha256": {name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                for name in ("verify.py", "PROOF.md")}}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    verify()
