#!/usr/bin/env python3
"""Exact finite corroboration of the laminar full-guard composition law."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """Prime fields and F4 = F2[x]/(x^2+x+1); all domains are fixed below."""

    def __init__(self, q):
        require(q in (2, 3, 4, 5), "unsupported field")
        self.q = q

    def add(self, a, b):
        return a ^ b if self.q == 4 else (a + b) % self.q

    def neg(self, a):
        return a if self.q == 4 else (-a) % self.q

    def mul(self, a, b):
        if self.q != 4:
            return a * b % self.q
        value = (a if b & 1 else 0) ^ (a << 1 if b & 2 else 0)
        return value ^ 7 if value & 4 else value

    def inv(self, a):
        require(a != 0, "inverse of zero")
        return next(b for b in range(1, self.q) if self.mul(a, b) == 1)


def dot(a, b, f):
    value = 0
    for x, y in zip(a, b, strict=True):
        value = f.add(value, f.mul(x, y))
    return value


def inverse(a, f):
    n = len(a)
    rows = [list(row) + [int(i == j) for j in range(n)]
            for i, row in enumerate(a)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = f.inv(rows[j][j])
        rows[j] = [f.mul(scale, x) for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                scale = rows[i][j]
                rows[i] = [f.add(x, f.neg(f.mul(scale, y)))
                           for x, y in zip(rows[i], rows[j], strict=True)]
    return tuple(tuple(row[n:]) for row in rows)


def matrix_product(a, b, f):
    return tuple(tuple(dot(row, col, f) for col in zip(*b, strict=True))
                 for row in a)


def projector(g, h, mask, f):
    n = len(g)
    return tuple(tuple(dot([g[i][k] for k in range(n) if mask >> k & 1],
                           [h[k][j] for k in range(n) if mask >> k & 1], f)
                       for j in range(n)) for i in range(n))


def passes(a, rank, f):
    # Direct principal-minor nonsingularity, independent of Schur recursion.
    return all(inverse(tuple(row[:k] for row in a[:k]), f) is not None
               for k in range(1, rank + 1))


def schur(a, f):
    scale = f.inv(a[0][0])
    return tuple(tuple(f.add(a[i][j], f.neg(f.mul(a[i][0],
                        f.mul(scale, a[0][j]))))
                       for j in range(1, len(a)))
                 for i in range(1, len(a)))


def orthogonal_law(q, n, ranks):
    value = Fraction(1)
    for t in range(max(ranks, default=0)):
        active = [r - t for r in ranks if r > t]
        free = n - t - sum(active)
        require(free >= 0, "negative free dimension")
        numerator = (q - 1) ** len(active) * q ** free - (-1) ** len(active)
        for r in active:
            numerator *= q ** r - 1
        value *= Fraction(numerator, q ** len(active) * (q ** (n - t) - 1))
    return value


def laminar(a, b):
    return a & b in (0, a, b)


def families(n):
    masks = tuple(range(1, 1 << n))
    result = []
    for code in range(1 << len(masks)):
        selected = [s for s in masks if code >> (s - 1) & 1]
        if all(laminar(a, b) for i, a in enumerate(selected) for b in selected[:i]):
            result.append((code, tuple(selected)))
    return result


def hierarchy(n, selected):
    # Node zero is an unguarded virtual ambient node, even for a full-rank request.
    nodes = (0,) + selected
    children = {node: [] for node in nodes}
    for s in selected:
        strict = [p for p in selected if s != p and s & p == s]
        parent = min(strict, key=int.bit_count) if strict else 0
        children[parent].append(s)
    return [(n if node == 0 else node.bit_count(),
             tuple(child.bit_count() for child in children[node])) for node in nodes]


def law(q, n, selected):
    value = Fraction(1)
    for dimension, ranks in hierarchy(n, selected):
        value *= orthogonal_law(q, dimension, ranks)
    return value


def check_schur(matrices, f):
    count = 0
    # New nontrivial containment step uses two positive-rank Schur complements.
    for p_mask, q_mask in ((3, 7), (3, 15), (7, 15)):
        if q_mask not in matrices:
            continue
        p, q = matrices[p_mask], matrices[q_mask]
        if p[0][0] and q[0][0]:
            s, t = schur(p, f), schur(q, f)
            require(matrix_product(s, t, f) == s, "Schur ST != S")
            require(matrix_product(t, s, f) == s, "Schur TS != S")
            count += 1
    return count


def census(q, n):
    f = Field(q)
    require(2 <= n <= 4 and q ** (n * n) <= 262144, "census capacity exceeded")
    mask_count = (1 << n) - 1
    counts = [0] * (1 << mask_count)
    headers = schur_checks = 0
    for entries in product(range(q), repeat=n * n):
        g = tuple(tuple(entries[i * n:(i + 1) * n]) for i in range(n))
        h = inverse(g, f)
        if h is None:
            continue
        matrices = {s: projector(g, h, s, f) for s in range(1, 1 << n)}
        code = sum(1 << (s - 1) for s, a in matrices.items()
                   if passes(a, s.bit_count(), f))
        counts[code] += 1
        headers += 1
        schur_checks += check_schur(matrices, f)
    expected = 1
    for j in range(n):
        expected *= q ** n - q ** j
    require(headers == expected, "incomplete GL census")
    # Superset zeta transform counts every all-pass event, including empty family.
    for bit in range(mask_count):
        for code in range(1 << mask_count):
            if not code >> bit & 1:
                counts[code] += counts[code | 1 << bit]
    checked = 0
    for code, selected in families(n):
        predicted = law(q, n, selected)
        require(Fraction(counts[code], headers) == predicted,
                f"law failed q={q}, n={n}, masks={selected}")
        zero = q == 2 and any(sum(rs) == d and len(rs) > 0 and len(rs) % 2 == 0
                             for d, rs in hierarchy(n, selected))
        require((counts[code] == 0) == zero, "zero criterion failed")
        checked += 1
    return {"q": q, "m": n, "headers": headers,
            "families": checked, "schur_containments": schur_checks}


def controls():
    # Incorrect independence is numerically different on an actual nested pair.
    nested = law(3, 3, (1, 3))
    independent = orthogonal_law(3, 3, (1,)) * orthogonal_law(3, 3, (2,))
    require(nested != independent, "independence control did not separate")
    require(nested != law(3, 3, (1, 6)), "orthogonal control did not separate")
    # A saturated even branch fails inside Q despite unused ambient coordinates.
    require(law(2, 3, (1, 2, 3)) == 0, "internal parity obstruction missing")
    require(law(3, 3, (1, 2, 3)) > 0, "odd-field positive control failed")
    # Nonlaminar commuting projectors can cease commuting under Schur deletion.
    f = Field(3)
    witness = None
    for entries in product(range(3), repeat=9):
        g = tuple(tuple(entries[i * 3:(i + 1) * 3]) for i in range(3))
        h = inverse(g, f)
        if h is None:
            continue
        p, q = projector(g, h, 3, f), projector(g, h, 6, f)
        if p[0][0] and q[0][0]:
            s, t = schur(p, f), schur(q, f)
            if matrix_product(s, t, f) != matrix_product(t, s, f):
                witness = g
                break
    require(witness is not None, "nonlaminar commuting control did not separate")
    require(Field(4).mul(2, 2) == 3, "F4 arithmetic control failed")
    return {"count": 6, "nonlaminar_witness": witness,
            "nested_example": str(nested), "independence": str(independent)}


def main():
    domains = ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (4, 2), (4, 3), (5, 2))
    results = [census(q, n) for q, n in domains]
    checks = controls()
    package = Path(__file__).resolve().parent
    # Generated hash-bound stdout receipt; no files are written by this verifier.
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    print("PASS_LAMINAR_HEADER_LAW " + json.dumps({"domains": results,
          "controls": checks, "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
