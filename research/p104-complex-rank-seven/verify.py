#!/usr/bin/env python3
"""Exact complex rank-seven P104 witnesses; Python standard library only.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Retains Nick Petalas's Gram convention, Matarener's cited coordinates and
the predecessor attribution recorded in README.md. No optimality claim.
"""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


WITNESSES = {
    "small": {
        "z": [(5, -5), (3, 9), (5, -5), (7, 0),
              (5, -5), (-1, -4), (-7, 0), (-7, 0)],
        "norm_squared": 404,
        "maximum_squared": 800,
        "error": "25/101",
    },
    "stronger": {
        "z": [(14, -10), (6, 23), (14, -10), (17, 3),
              (14, -10), (-3, -10), (-17, -3), (-17, -3)],
        "norm_squared": 2456,
        "maximum_squared": 4820,
        "error": "1205/4912",
    },
}
SOURCE_DIRECTORY = "research/p104-contractive-gram-deflation"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def mul(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def conjugate(x):
    return x[0], -x[1]


def scale(a, x):
    return a * x[0], a * x[1]


def total(values):
    result = (0, 0)
    for value in values:
        result = add(result, value)
    return result


def dot(x, y):
    return sum(a * b for a, b in zip(x, y, strict=True))


def matrix_product(left, right):
    columns = list(zip(*right, strict=True))
    return [[total(mul(a, b) for a, b in zip(row, column, strict=True))
             for column in columns] for row in left]


def matrix_scale(a, matrix):
    return [[scale(a, value) for value in row] for row in matrix]


def hermitian(matrix):
    return all(matrix[i][j] == conjugate(matrix[j][i])
               for i in range(len(matrix)) for j in range(len(matrix)))


def rational_rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][column]
        rows[rank] = [value / divisor for value in rows[rank]]
        for i in range(rank + 1, len(rows)):
            coefficient = rows[i][column]
            rows[i] = [x - coefficient * y
                       for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


def authenticate_sources(package):
    repository = package.parents[1]
    manifest = json.loads((package / "SOURCES.json").read_text())
    inputs = [item for item in manifest["files"] if item["usage"] == "input"]
    required = {f"{SOURCE_DIRECTORY}/{name}" for name in
                ("MISSING.json", "PROOF.md", "README.md")}
    need(len(inputs) == 3 and {item["path"] for item in inputs} == required,
         "exact three declared predecessor inputs")
    payloads, hashes = {}, {}
    for item in inputs:
        path = (repository / item["path"]).resolve()
        need(path.is_relative_to(repository), "input path stays inside checkout")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        need(digest == item["sha256"], "input digest: " + item["path"])
        payloads[item["path"]] = data
        hashes[item["path"]] = digest
    return json.loads(payloads[f"{SOURCE_DIRECTORY}/MISSING.json"]), hashes


def roots_and_missing(data):
    signs = data["signs"]
    need(isinstance(signs, list) and len(signs) == 16, "sixteen omitted lines")
    missing = set()
    for text in signs:
        need(isinstance(text, str) and len(text) == 8
             and set(text) <= {"+", "-"}, "eight valid half-spin signs")
        need(text.count("-") % 2 == 1, "odd half-spin parity")
        row = tuple(1 if sign == "+" else -1 for sign in text)
        missing.add(row if row[0] > 0 else tuple(-x for x in row))
    need(len(missing) == 16, "sixteen distinct omitted lines")
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    half = [(1, *tail) for tail in itertools.product((-1, 1), repeat=7)
            if tail.count(-1) % 2 == 1]
    need(len(roots) == 56 and len(half) == 64 and missing <= set(half),
         "D8 and half-spin shell counts")
    roots.extend(row for row in half if row not in missing)
    need(len(roots) == len(set(roots)) == 104, "104 distinct retained lines")
    need(all(dot(row, row) == 8 for row in roots), "doubled root norms")
    return roots, sorted(missing)


def root_frame(roots):
    frame = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            frame.append(roots.index(tuple(row)))
    need(all(dot(roots[frame[i]], roots[frame[j]]) == 8 * int(i == j)
             for i in range(8) for j in range(8)), "full column rank frame")
    return frame


def projector_numerator(z, denominator, multiplier=1, use_conjugate=True):
    return [[add((denominator * int(i == j), 0),
                 scale(-multiplier, mul(z[i], conjugate(z[j])
                                        if use_conjugate else z[j])))
             for j in range(8)] for i in range(8)]


def projector_certificate(z):
    norm = sum(a * a + b * b for a, b in z)
    need(norm > 0, "nonzero deleted direction")
    matrix = projector_numerator(z, norm)
    need(hermitian(matrix), "Hermitian carrier filter")
    need(matrix_product(matrix, matrix) == matrix_scale(norm, matrix),
         "idempotent carrier filter")
    need(total(matrix[i][i] for i in range(8)) == (7 * norm, 0),
         "idempotent has rank-seven trace")
    need(all(total(mul(row[j], z[j]) for j in range(8)) == (0, 0)
             for row in matrix), "deleted direction lies in kernel")
    # Hermitian idempotence proves 0 <= D <= I. Rank is its trace.
    real, imag = [a for a, _ in z], [b for _, b in z]
    aa, bb, ab = dot(real, real), dot(imag, imag), dot(real, imag)
    determinant = aa * bb - ab * ab
    need(aa + bb == norm and determinant > 0, "independent real and imaginary parts")
    real_matrix = [[value[0] for value in row] for row in matrix]
    need(rational_rank(real_matrix) == 8, "real part restores real rank eight")
    return norm, matrix, {"real_norm_squared": aa, "imag_norm_squared": bb,
                          "real_imag_dot": ab, "gram_determinant": determinant}


def literal_matrix_certificate(roots, z, norm, matrix):
    products = [total(scale(a, b) for a, b in zip(row, z, strict=True))
                for row in roots]
    norms = [a * a + b * b for a, b in products]
    maximum = max(norms)
    left = [[total(scale(row[k], matrix[k][j]) for k in range(8))
             for j in range(8)] for row in roots]
    # With S the doubled roots, C has denominator 8*norm.
    candidate = [[total(scale(column[k], row[k]) for k in range(8))
                  for column in roots] for row in left]
    need(hermitian(candidate), "Hermitian complete Gram approximation")
    largest_squared = 0
    for i, row in enumerate(roots):
        for j, column in enumerate(roots):
            gram = (norm * dot(row, column), 0)
            error = add(gram, scale(-1, candidate[i][j]))
            need(error == mul(products[i], conjugate(products[j])),
                 "literal full-matrix rank-one error identity")
            size_squared = error[0] * error[0] + error[1] * error[1]
            need(size_squared <= maximum * maximum, "full-matrix entry bound")
            largest_squared = max(largest_squared, size_squared)
    need(largest_squared == maximum * maximum, "attained entry bound")
    trace = Fraction(sum(candidate[i][i][0] for i in range(len(roots))), 8 * norm)
    need(trace > 7, "C is not an ambient rank-seven positive contraction")
    return maximum, [i for i, value in enumerate(norms) if value == maximum], trace


def verify_witness(roots, fixture):
    z = fixture["z"]
    norm, matrix, real_imag = projector_certificate(z)
    maximum, attaining, trace = literal_matrix_certificate(roots, z, norm, matrix)
    error = Fraction(maximum, 8 * norm)
    need(norm == fixture["norm_squared"], "declared direction norm")
    need(maximum == fixture["maximum_squared"], "declared root maximum")
    need(str(error) == fixture["error"] and error < Fraction(1, 4),
         "declared strict complex-field separation")
    return {"z": z, "norm_squared": norm,
            "max_doubled_root_inner_product_squared": maximum,
            "error": str(error), "gap_from_one_quarter": str(Fraction(1, 4) - error),
            "attaining_root_indices": attaining, "carrier_complex_rank": 7,
            "candidate_complex_rank": 7, "real_part_rank": 8,
            "real_imag_certificate": real_imag, "candidate_trace": str(trace),
            "literal_matrix_entries": len(roots) ** 2}


def real_direction_error(roots, direction):
    norm = dot(direction, direction)
    need(norm > 0, "nonzero real direction")
    return Fraction(max(dot(row, direction) ** 2 for row in roots), 8 * norm)


def rejected_root_control(data, signs, diagnostic):
    try:
        roots_and_missing({**data, "signs": signs})
    except ValueError as error:
        need(str(error) == diagnostic, "specific malformed-root diagnostic")
    else:
        raise ValueError("malformed root data accepted")


def controls(data, roots, missing):
    omitted_errors = {real_direction_error(roots, row) for row in missing}
    need(omitted_errors == {Fraction(1, 4)}, "all omitted roots attain real quarter")
    retained_error = real_direction_error(roots, roots[56])
    need(retained_error == 1, "retained half-spin deletion has unit error")
    z = WITNESSES["small"]["z"]
    real_error = real_direction_error(roots, [a for a, _ in z])
    need(real_error >= Fraction(1, 4), "dropping imaginary coordinates loses escape")
    norm = sum(a * a + b * b for a, b in z)
    unconjugated = projector_numerator(z, norm, use_conjugate=False)
    need(not hermitian(unconjugated), "bilinear deletion is not Hermitian")
    need(matrix_product(unconjugated, unconjugated) != matrix_scale(norm, unconjugated),
         "bilinear deletion is not idempotent")
    reflection = projector_numerator(z, norm, multiplier=2)
    squared = matrix_product(reflection, reflection)
    identity = [[(norm * norm * int(i == j), 0) for j in range(8)] for i in range(8)]
    need(squared == identity, "misnormalized deletion is invertible of rank eight")
    need(squared != matrix_scale(norm, reflection), "misnormalized deletion is not idempotent")
    signs = data["signs"]
    rejected_root_control(data, ["++++++++", *signs[1:]], "odd half-spin parity")
    rejected_root_control(data, [signs[0], *signs[:-1]], "sixteen distinct omitted lines")
    rejected_root_control(data, signs[:-1], "sixteen omitted lines")
    error = Fraction(WITNESSES["small"]["error"])
    need(2 * error > Fraction(1, 4), "RR^T normalization cannot claim quarter escape")
    return {
        "omitted_half_spin_real_quarter": {"directions": len(missing), "error": "1/4"},
        "retained_half_spin_unit_error": str(retained_error),
        "dropping_imaginary_part": str(real_error),
        "missing_conjugation": "rejected: not Hermitian or idempotent",
        "wrong_projector_normalization": "rejected: rank-eight reflection, not idempotent",
        "wrong_half_spin_parity": "rejected",
        "duplicate_omitted_line": "rejected",
        "wrong_omitted_count": "rejected",
        "wrong_gram_normalization": {"error_for_doubled_target_and_candidate": str(2 * error)},
    }


def main():
    package = Path(__file__).resolve().parent
    data, hashes = authenticate_sources(package)
    roots, missing = roots_and_missing(data)
    frame = root_frame(roots)
    witnesses = {name: verify_witness(roots, fixture)
                 for name, fixture in WITNESSES.items()}
    control_results = controls(data, roots, missing)
    result = {"schema_version": 1, "claim_type": "exact finite complex-field separation",
              "metric": "maximum complex entry modulus", "root_order": "D8 pairs then odd half-spin",
              "d8_lines": 56, "retained_half_spin_lines": 48, "retained_lines": len(roots),
              "omitted_lines": len(missing), "root_frame_indices": frame,
              "source_sha256": hashes, "witnesses": witnesses,
              "literal_matrix_entries": sum(item["literal_matrix_entries"]
                                            for item in witnesses.values()),
              "control_count": len(control_results), "controls": control_results}
    print(json.dumps(result, sort_keys=True))
    print("PASS_P104_COMPLEX_RANK_SEVEN")


if __name__ == "__main__":
    main()
