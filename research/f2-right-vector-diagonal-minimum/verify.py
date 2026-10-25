#!/usr/bin/env python3
"""Finite checks for the F2-right-vector diagonal minimum.

The uniform statement is PROOF.md. These checks compare two Klein-ring
multipliers, exhaust small words, and separate the chain-ring hypothesis.
They do not replace the written argument.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
import hashlib
from itertools import permutations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT = HERE / "RESULT.json"
KAPPA = "0.001672660197076918"
PASS = "PASS_F2_RIGHT_VECTOR_DIAGONAL_MINIMUM"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_json(text):
    def pairs(items):
        seen = set()
        out = {}
        for key, value in items:
            need(key not in seen, "duplicate JSON key: " + str(key))
            seen.add(key)
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=pairs)


def klein_bit(left, right):
    """Primary product on F2[z1,z2]/(z1^2,z2^2), bits 1, z1, z2, z1 z2."""
    out = 0
    for i in range(4):
        if ((left >> i) & 1) == 0:
            continue
        for j in range(4):
            if ((right >> j) & 1) == 0:
                continue
            if i == 0:
                out ^= 1 << j
            elif j == 0:
                out ^= 1 << i
            elif (i == 1 and j == 2) or (i == 2 and j == 1):
                out ^= 1 << 3
    return out


def klein_poly(left, right):
    """Independent dictionary product. Keys are exponent pairs (a,b) in {0,1}^2."""
    terms = {}
    for (a1, b1), coeff in left.items():
        for (a2, b2), weight in right.items():
            if a1 + a2 > 1 or b1 + b2 > 1:
                continue
            key = (a1 + a2, b1 + b2)
            terms[key] = terms.get(key, 0) ^ (coeff & weight)
            if terms[key] == 0:
                del terms[key]
    return terms


def bits_to_poly(value):
    terms = {}
    if value & 1:
        terms[(0, 0)] = 1
    if value & 2:
        terms[(1, 0)] = 1
    if value & 4:
        terms[(0, 1)] = 1
    if value & 8:
        terms[(1, 1)] = 1
    return terms


def poly_to_bits(terms):
    out = 0
    for (a, b), coeff in terms.items():
        need(coeff == 1 and a in (0, 1) and b in (0, 1), "bad polynomial term")
        out ^= 1 << (a + 2 * b)
    return out


def pack_column(low, high):
    return low | (high << 4)


def in_span(columns, vectors):
    basis = {}
    for column in columns:
        value = column
        while value:
            lead = value.bit_length() - 1
            if lead in basis:
                value ^= basis[lead]
            else:
                basis[lead] = value
                break
    for vector in vectors:
        value = vector
        while value:
            lead = value.bit_length() - 1
            if lead in basis:
                value ^= basis[lead]
            else:
                return False
    return True


def klein_images(matrix):
    # matrix = (p00, p01, p10, p11) of the product P.
    p00, p01, p10, p11 = matrix
    return (pack_column(p00 ^ 1, p10), pack_column(p01, p11 ^ 1))


def klein_step(matrix, u0, u1, y):
    p00, p01, p10, p11 = matrix
    c0 = klein_bit(p00, u0) ^ klein_bit(p01, u1)
    c1 = klein_bit(p10, u0) ^ klein_bit(p11, u1)
    if y & 1:
        p00 ^= c0
        p10 ^= c1
    if y & 2:
        p01 ^= c0
        p11 ^= c1
    return (p00, p01, p10, p11), pack_column(c0, c1)


def diagonal_count(matrix):
    p00, p01, p10, p11 = matrix
    if p01 or p10:
        return None
    return (p00 != 1) + (p11 != 1)


def exhaust_klein():
    eye = (1, 0, 0, 1)
    violations = 0
    span_failures = 0
    diagonal_hits = 0
    words = 0
    factors = [(u0, u1, y) for u0 in range(16) for u1 in range(16) for y in range(4)]
    need(len(factors) == 1024, "Klein factor count")
    partial = []
    for factor in factors:
        matrix, column = klein_step(eye, *factor)
        words += 1
        images = klein_images(matrix)
        if not in_span([column], images):
            span_failures += 1
        count = diagonal_count(matrix)
        if count is not None:
            diagonal_hits += 1
            if count > 1:
                violations += 1
        partial.append((matrix, column))
    for matrix, column in partial:
        for u0, u1, y in factors:
            nxt, second = klein_step(matrix, u0, u1, y)
            words += 1
            if not in_span([column, second], klein_images(nxt)):
                span_failures += 1
            count = diagonal_count(nxt)
            if count is not None:
                diagonal_hits += 1
                if count > 2:
                    violations += 1
    one = (1, 0)
    built = eye
    for value, slot in ((2, 0), (8, 1)):
        u0, u1 = (value, 0) if slot == 0 else (0, value)
        y = 1 << slot
        built, _column = klein_step(built, u0, u1, y)
    need(built == (1 ^ 2, 0, 0, 1 ^ 8), "coordinate word missed the Klein diagonal")
    need(diagonal_count(built) == 2, "coordinate word length")
    return {
        "words": words,
        "factors": len(factors),
        "violations": violations,
        "span_failures": span_failures,
        "diagonal_hits": diagonal_hits,
    }


def sharpness_witness():
    # u = (z1, z2), v = (z2, z1). Not an F2-valued right vector.
    u0, u1, v0, v1 = 2, 4, 4, 2
    off01 = klein_bit(u0, v1)
    off10 = klein_bit(u1, v0)
    diag0 = klein_bit(u0, v0)
    diag1 = klein_bit(u1, v1)
    need(off01 == 0 and off10 == 0, "witness has an off-diagonal")
    need(diag0 == 8 and diag1 == 8, "witness diagonal is not the socle pair")
    poly = klein_poly(bits_to_poly(u0), bits_to_poly(v0))
    need(poly_to_bits(poly) == 8, "dictionary multiplier rejected the socle product")
    # No single F2-valued right vector realizes two non-identity diagonal entries.
    saved = 0
    for u_0 in range(16):
        for u_1 in range(16):
            for y in range(4):
                matrix, _column = klein_step((1, 0, 0, 1), u_0, u_1, y)
                count = diagonal_count(matrix)
                if count is not None and count > 1:
                    saved += 1
    need(saved == 0, "F2 right vector realized t=2 in one factor")
    return {"saved_with_binary_right_vector": saved, "algebra_diagonal_t": 2, "factors": 1}


def s3_tables():
    perms = list(permutations(range(3)))
    index = {perm: i for i, perm in enumerate(perms)}
    mul = [[0] * 6 for _ in range(6)]
    for left in perms:
        for right in perms:
            composed = tuple(left[right[i]] for i in range(3))
            mul[index[left]][index[right]] = index[composed]
    return perms, mul, index[(0, 1, 2)]


def s3_mul(mul, left, right):
    out = 0
    for i in range(6):
        if ((left >> i) & 1) == 0:
            continue
        for j in range(6):
            if (right >> j) & 1:
                out ^= 1 << mul[i][j]
    return out


def exhaust_s3():
    perms, mul, identity = s3_tables()
    one = 1 << identity
    labels = []
    for pos, perm in enumerate(perms):
        if perm != (0, 1, 2):
            labels.append((1 << pos) ^ one)
    projectors = []
    for column in range(8):
        for row in range(8):
            dot = 0
            for bit in range(3):
                dot ^= ((column >> bit) & 1) & ((row >> bit) & 1)
            if dot:
                projectors.append((column, row))
    need(len(labels) == 5 and len(projectors) == 28, "S3 alphabet size")

    def step(matrix, step_value, column, row):
        # matrix is 3 tuples of 3 algebra masks, row-major via list of rows.
        image = [0, 0, 0]
        for bit in range(3):
            if (column >> bit) & 1:
                for source in range(3):
                    image[source] ^= s3_mul(mul, matrix[source][bit], step_value)
        updated = [list(line) for line in matrix]
        for target in range(3):
            if (row >> target) & 1:
                for source in range(3):
                    updated[source][target] ^= image[source]
        return tuple(tuple(line) for line in updated)

    eye = tuple(tuple(one if i == j else 0 for j in range(3)) for i in range(3))
    factors = [(label, column, row) for label in labels for column, row in projectors]
    words = 0
    violations = 0
    first = []
    for factor in factors:
        matrix = step(eye, *factor)
        words += 1
        count = s3_diagonal(matrix, one)
        if count is not None and count > 1:
            violations += 1
        first.append(matrix)
    for matrix in first:
        for factor in factors:
            nxt = step(matrix, *factor)
            words += 1
            count = s3_diagonal(nxt, one)
            if count is not None and count > 2:
                violations += 1
    transpositions = [(0, 2, 1), (1, 0, 2), (2, 1, 0)]
    built = eye
    for slot, perm in enumerate(transpositions):
        label = (1 << perms.index(perm)) ^ one
        built = step(built, label, 1 << slot, 1 << slot)
    need(s3_diagonal(built, one) == 3, "S3 coordinate word is not the three-transposition diagonal")
    return {"words": words, "factors": len(factors), "violations": violations, "coordinate_t": 3}


def s3_diagonal(matrix, one):
    count = 0
    for row in range(3):
        for column in range(3):
            if row != column and matrix[row][column]:
                return None
            if row == column and matrix[row][column] != one:
                count += 1
    return count


def pin_separation():
    chain = " ".join((ROOT / "research/bit-cyclic-root-barrier/PROOF.md").read_text(encoding="utf-8").split())
    torsion = " ".join(
        (ROOT / "research/bit-one-relation-any-registers/PROOF.md").read_text(encoding="utf-8").split()
    )
    selected = load_json((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    need("Let R = F2[z]/(z^q), where q is any positive integer." in chain,
         "pin lost the chain-ring hypothesis")
    need("The column lemma is not asserted for arbitrary group algebras." in chain,
         "pin lost the arbitrary-algebra boundary")
    need("F2[x,y]/(x^2,y^2)" in chain, "pin lost the Klein socle witness")
    need("every F2-algebra" not in chain, "chain-ring note already states this theorem")
    need("formal coefficients in a torsion-free group algebra" in torsion,
         "one-relation note is not the torsion-free model")
    need("A finite torsion representation cannot replace that hypothesis." in torsion,
         "one-relation note no longer declines torsion specializations")
    need(selected["decimal"] == KAPPA, "selected kappa moved")
    need(selected["kappa"] == "836330098538459/500000000000000000", "selected rational kappa moved")


def payload():
    pin_separation()
    engines = 0
    for left in range(16):
        for right in range(16):
            need(poly_to_bits(klein_poly(bits_to_poly(left), bits_to_poly(right))) == klein_bit(left, right),
                 "Klein multipliers disagree")
            engines += 1
    witness = sharpness_witness()
    klein = exhaust_klein()
    group = exhaust_s3()
    need(klein["violations"] == 0 and klein["span_failures"] == 0, "Klein exhaustion failed")
    need(group["violations"] == 0, "S3 exhaustion failed")
    body = {
        "status": PASS,
        "statement": "exact minimum t for every diagonal over every F2-algebra when right vectors are F2-valued",
        "kappa": KAPPA,
        "no_new_kappa": True,
        "klein_multiplier_pairs": engines,
        "klein_words": klein["words"],
        "klein_violations": klein["violations"],
        "klein_span_failures": klein["span_failures"],
        "klein_diagonal_hits": klein["diagonal_hits"],
        "sharp_binary_saves": witness["saved_with_binary_right_vector"],
        "sharp_algebra_t": witness["algebra_diagonal_t"],
        "sharp_algebra_factors": witness["factors"],
        "s3_words": group["words"],
        "s3_violations": group["violations"],
        "s3_coordinate_t": group["coordinate_t"],
        "group_corollary": "every finite group, exact non-identity count",
    }
    return body


def main():
    write = "--write-receipt" in sys.argv[1:]
    body = payload()
    encoded = json.dumps(body, indent=2) + "\n"
    if write:
        need(not RESULT.exists(), "will not overwrite receipt")
        RESULT.write_text(encoded, encoding="utf-8")
    else:
        need(RESULT.is_file(), "missing receipt")
        stored = load_json(RESULT.read_text(encoding="utf-8"))
        need(stored == body, "receipt mismatch")
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:12]
    print(
        PASS
        + " klein_words=" + str(body["klein_words"])
        + " s3_words=" + str(body["s3_words"])
        + " violations=0"
        + " sharp_factors=" + str(body["sharp_algebra_factors"])
        + " receipt=" + digest
        + " no_new_kappa"
    )


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
