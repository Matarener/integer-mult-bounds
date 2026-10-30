#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite audit of PR5459 over F3[i]/(i^2+1).

Prepared for Charan / theon199 with substantial OpenAI Codex assistance.
No predecessor executable is imported. See README for finite coverage limits.
"""
from collections import Counter
from hashlib import sha1, sha256
from itertools import combinations, product
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SEED = 83


def require(condition, message):
    if not condition:
        raise ValueError(message)


# a+3b encodes a+b*i, i^2=-1, with a,b in F3.
ADD = [[(a % 3 + b % 3) % 3 + 3 * ((a // 3 + b // 3) % 3)
        for b in range(9)] for a in range(9)]
MUL = [[((a % 3) * (b % 3) - (a // 3) * (b // 3)) % 3
        + 3 * (((a % 3) * (b // 3) + (a // 3) * (b % 3)) % 3)
        for b in range(9)] for a in range(9)]
NEG = [(-(a % 3)) % 3 + 3 * (-(a // 3) % 3) for a in range(9)]
INV = [0] + [next(b for b in range(1, 9) if MUL[a][b] == 1) for a in range(1, 9)]


def power(a, n):
    result = 1
    for _ in range(n):
        result = MUL[result][a]
    return result


def determinant(matrix):
    """Eliminate over F9, retaining actual row operations and signs."""
    rows = [list(row) for row in matrix]
    result = 1
    for j in range(len(rows)):
        k = next((k for k in range(j, len(rows)) if rows[k][j]), None)
        if k is None:
            return 0
        if k != j:
            rows[k], rows[j] = rows[j], rows[k]
            result = NEG[result]
        pivot = rows[j][j]
        result = MUL[result][pivot]
        for k in range(j + 1, len(rows)):
            coefficient = MUL[rows[k][j]][INV[pivot]]
            if coefficient:
                rows[k] = [ADD[x][NEG[MUL[coefficient][y]]]
                           for x, y in zip(rows[k], rows[j])]
    return result


def determinant_by_subsets(matrix):
    """Division-free Leibniz sum, sharing partial column subsets (no pivots)."""
    states = {0: 1}
    for row in matrix:
        following = {}
        for mask, value in states.items():
            for j, entry in enumerate(row):
                if entry and not (mask >> j & 1):
                    term = MUL[value][entry]
                    if (mask >> (j + 1)).bit_count() % 2:
                        term = NEG[term]
                    key = mask | (1 << j)
                    following[key] = ADD[following.get(key, 0)][term]
        states = {key: value for key, value in following.items() if value}
    return states.get((1 << len(matrix)) - 1, 0)


def prime_determinant(rows):
    """Independent F3 elimination, with no F9 tables or inverse routine."""
    a = [list(row) for row in rows]
    sign = 1
    for col in range(len(a)):
        pivot = next((r for r in range(col, len(a)) if a[r][col] % 3), None)
        if pivot is None:
            return 0
        if pivot != col:
            a[pivot], a[col] = a[col], a[pivot]
            sign = -sign
        value = a[col][col] % 3
        sign *= value
        for r in range(col + 1, len(a)):
            scale = a[r][col] * value % 3
            if scale:
                for j in range(col, len(a)):
                    a[r][j] = (a[r][j] - scale * a[col][j]) % 3
    return sign % 3


def restrict_scalars(matrix):
    """Replace a+b*i by its multiplication matrix [[a,-b],[b,a]]."""
    result = [[0] * (2 * len(matrix)) for _ in range(2 * len(matrix))]
    for r, row in enumerate(matrix):
        for c, value in enumerate(row):
            a, b = value % 3, value // 3
            result[2*r][2*c:2*c+2] = [a, -b % 3]
            result[2*r+1][2*c:2*c+2] = [b, a]
    return result


class Quotient:
    def __init__(self, cutoffs):
        self.cutoffs = tuple(cutoffs)
        self.basis = list(product(*(range(n) for n in cutoffs)))
        self.index = {m: i for i, m in enumerate(self.basis)}
        self.n = len(self.basis)
        self.one = {(0,) * len(cutoffs): 1}
        self.generators = []
        for j in range(len(cutoffs)):
            m = tuple(int(i == j) for i in range(len(cutoffs)))
            self.generators.append({m: 1})
        # Conjugate by a deterministic permutation to avoid testing only
        # already-triangular matrices. The permutation has determinant square 1.
        self.order = list(range(self.n))
        random.Random(SEED + self.n).shuffle(self.order)

    def multiply(self, left, right):
        result = {}
        for a, x in left.items():
            for b, y in right.items():
                m = tuple(i + j for i, j in zip(a, b))
                if all(e < n for e, n in zip(m, self.cutoffs)):
                    result[m] = ADD[result.get(m, 0)][MUL[x][y]]
        return {m: c for m, c in result.items() if c}

    def pow(self, value, exponent):
        result = self.one
        for _ in range(exponent):
            result = self.multiply(result, value)
        return result

    def columns(self, images):
        powers = [[self.pow(image, e) for e in range(n)]
                  for image, n in zip(images, self.cutoffs)]
        columns = []
        for m in self.basis:
            value = self.one
            for j, e in enumerate(m):
                value = self.multiply(value, powers[j][e])
            columns.append(value)
        return columns

    def matrix(self, columns):
        return [[columns[c].get(self.basis[r], 0) for c in self.order]
                for r in self.order]

    def predicted(self, images):
        # Each height block in these three contexts is one dimensional.
        result = 1
        for image, generator, cutoff in zip(images, self.generators, self.cutoffs):
            c = image.get(next(iter(generator)), 0)
            require(c != 0, "singular tangent")
            result = MUL[result][power(c, self.n * (cutoff - 1) // 2)]
        return result

    def check_relations(self, images):
        for image, cutoff in zip(images, self.cutoffs):
            require(not self.pow(image, cutoff), "defining power relation")

    def check_products(self, images, columns):
        checks = 0
        require(columns[0] == self.one, "unit image")
        # Every generator times every basis monomial, including zero products.
        for image, generator in zip(images, self.generators):
            for j, monomial in enumerate(self.basis):
                source = self.multiply(generator, {monomial: 1})
                expected = columns[self.index[next(iter(source))]] if source else {}
                require(self.multiply(image, columns[j]) == expected, "generator product")
                checks += 1
        return checks


def cases():
    for a, b in product(range(1, 9), range(9)):
        yield "cutoff3_complete", (3,), [{(1,): a, **({(2,): b} if b else {})}], True
    # All supports of size <=2 among nonlinear degrees 2..8; no duplicates.
    for size in range(3):
        for degrees in combinations(range(2, 9), size):
            for coefficients in product(range(1, 9), repeat=size + 1):
                image = {(1,): coefficients[0]}
                image.update({(d,): c for d, c in zip(degrees, coefficients[1:])})
                yield "cutoff9_two_tail", (9,), [image], size == 0
    # All flag-preserving linear substitutions: x->a*x; y->b*x+c*y.
    for a, b, c in product(range(1, 9), range(9), range(1, 9)):
        yield "mixed_linear_complete", (3, 9), [{(1, 0): a},
            {(0, 1): c, **({(1, 0): b} if b else {})}], False
    A = Quotient((3, 9))
    allowed = [[m for m in A.basis if sum(m) >= 2 and
                not A.pow({m: 1}, cutoff)] for cutoff in A.cutoffs]
    for variable, monomials in enumerate(allowed):
        for m, c in product(monomials, range(1, 9)):
            images = [dict(g) for g in A.generators]
            images[variable][m] = c
            yield "mixed_single_tail_complete", (3, 9), images, False
    rng = random.Random(SEED)
    for _ in range(SEED):
        images = [{(1, 0): rng.randrange(1, 9)}, {(0, 1): rng.randrange(1, 9)}]
        cross = rng.randrange(9)
        if cross:
            images[1][(1, 0)] = cross
        for image, monomials in zip(images, allowed):
            for m in monomials:
                c = rng.randrange(9)
                if c:
                    image[m] = c
        yield "mixed_dense_seed83", (3, 9), images, True


def reject(call, diagnostic):
    try:
        call()
    except ValueError as error:
        require(diagnostic in str(error), "wrong failure: " + str(error))
    else:
        raise ValueError("negative control accepted: " + diagnostic)


def source_checks():
    pins = json.loads((HERE / "REFERENCE.json").read_text())
    for row in pins["files"]:
        raw = (HERE / row["local_path"]).read_bytes()
        require(sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                == row["git_blob"], "source Git blob")
    return pins["source_head"]


def audit():
    source_head = source_checks()
    for a, b, c in product(range(9), repeat=3):
        require(MUL[a][ADD[b][c]] == ADD[MUL[a][b]][MUL[a][c]], "distributivity")
        require(MUL[MUL[a][b]][c] == MUL[a][MUL[b][c]], "associativity")
    for a in range(1, 9):
        require(MUL[a][INV[a]] == 1, "field inverse")
    require(power(4, 8) == 1 and power(4, 4) != 1, "primitive extension element")
    contexts = {c: Quotient(c) for c in ((3,), (9,), (3, 9))}
    counts, spectra = Counter(), {}
    products_checked = subset_checks = norm_checks = 0
    transcript = sha256()
    for label, cutoffs, images, norm_check in cases():
        A = contexts[cutoffs]
        A.check_relations(images)
        columns = A.columns(images)
        products_checked += A.check_products(images, columns)
        matrix = A.matrix(columns)
        actual, expected = determinant(matrix), A.predicted(images)
        require(actual == expected, "automorphism determinant character")
        if A.n <= 9:
            require(determinant_by_subsets(matrix) == actual, "Leibniz determinant")
            subset_checks += 1
        if norm_check:
            a, b = actual % 3, actual // 3
            require(prime_determinant(restrict_scalars(matrix)) == (a*a + b*b) % 3,
                    "restriction-of-scalars norm")
            norm_checks += 1
        counts[label] += 1
        spectra.setdefault(label, Counter())[str(actual)] += 1
        transcript.update(json.dumps([label, [sorted(image.items()) for image in images],
                                      actual], separators=(",", ":")).encode() + b"\n")
    require(dict(counts) == {"cutoff3_complete": 72, "cutoff9_two_tail": 11208,
                            "mixed_linear_complete": 576,
                            "mixed_single_tail_complete": 376, "mixed_dense_seed83": 83},
            "domain coverage")
    require(set(spectra["cutoff3_complete"]) == set(map(str, range(1, 9))), "cutoff3 image")
    require(set(spectra["cutoff9_two_tail"]) == {"1", "2"}, "cutoff9 image")
    require(set(spectra["mixed_linear_complete"]) == set(map(str, range(1, 9))), "mixed image")
    A = contexts[(3, 9)]
    controls = []
    for name, images in [
        ("forbidden_linear_height", [{(1, 0): 1, (0, 1): 1}, {(0, 1): 1}]),
        ("invalid_nonlinear_tail", [{(1, 0): 1, (0, 2): 1}, {(0, 1): 1}]),
    ]:
        reject(lambda: A.check_relations(images), "defining power relation")
        controls.append(name)
    reject(lambda: A.predicted([{}, {(0, 1): 1}]), "singular tangent")
    controls.append("singular_tangent")
    columns = A.columns(A.generators)
    columns[A.index[(1, 1)]] = {(1, 1): 2}
    reject(lambda: A.check_products(A.generators, columns), "generator product")
    controls.append("corrupted_substitution_column")
    require(power(4, 3) != MUL[4][power(1, 3)], "p-Frobenius must fail K-linearity")
    controls.append("semilinear_p_frobenius")
    require(power(4, 3) != power(4, 12), "using q instead of p must change character")
    controls.append("wrong_characteristic_exponent")
    identity9 = contexts[(9,)].matrix(contexts[(9,)].columns(contexts[(9,)].generators))
    require(prime_determinant(restrict_scalars(identity9)) == 1
            and prime_determinant(restrict_scalars([[3]])) == 1,
            "norm-only control must admit the counterfeit i")
    reject(lambda: require(determinant(identity9) == 3, "counterfeit F9 determinant"),
           "counterfeit F9 determinant")
    controls.append("norm_only_false_positive")
    require(all((3 * b) % 9 != 1 for b in range(9)), "Z/9 is not F9")
    controls.append("integer_mod9_is_not_a_field")
    reject(lambda: require(determinant(A.matrix(A.columns([{(1, 0): 4}, {(0, 1): 1}])))
                           == power(4, 26), "mutated exponent"), "mutated exponent")
    controls.append("off_by_one_character_exponent")
    return {"schema": "f9-character-audit/v1", "source_head": source_head,
            "seed": SEED, "field": "F3[i]/(i^2+1); a+3b encodes a+b*i",
            "coverage": dict(counts), "substitution_maps": sum(counts.values()),
            "generator_basis_products": products_checked, "division_free_determinants": subset_checks,
            "restriction_of_scalars_determinants": norm_checks,
            "norm_ambiguity_witness": {"algebra": "F9[x]/x^9", "map": "identity",
                "actual_determinant": 1, "counterfeit_determinant": 3,
                "actual_norm": 1, "counterfeit_norm": 1,
                "exact_character_rejects_counterfeit": True},
            "determinant_spectra": {k: dict(sorted(v.items())) for k, v in spectra.items()},
            "transcript_sha256": transcript.hexdigest(), "negative_controls": controls,
            "scope": "Finite independent corroboration of automorphism characters; no new kappa or full theorem proof."}


def main():
    result = audit()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    require(not sys.argv[1:], "usage: verify.py [--emit]")
    require(result == json.loads((HERE / "RESULT.json").read_text()), "frozen result mismatch")
    print("PASS_F9_CHARACTER_AUDIT " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
