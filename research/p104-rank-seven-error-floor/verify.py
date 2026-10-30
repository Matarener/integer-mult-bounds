#!/usr/bin/env python3
"""Exact fixtures for the unrestricted P104 rank-seven error theorem.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas retains the attaining projection; Matarener the cited root data.
"""

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def transpose(matrix):
    return list(map(list, zip(*matrix, strict=True)))


def multiply(a, b):
    columns = transpose(b)
    return [[dot(row, column) for column in columns] for row in a]


def reduce_rows(matrix):
    rows = [[F(x) for x in row] for row in matrix]
    pivots = []
    for column in range(len(rows[0])):
        pivot = next((i for i in range(len(pivots), len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        row_index = len(pivots)
        rows[row_index], rows[pivot] = rows[pivot], rows[row_index]
        divisor = rows[row_index][column]
        rows[row_index] = [x / divisor for x in rows[row_index]]
        for i in range(len(rows)):
            if i != row_index and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[row_index], strict=True)]
        pivots.append(column)
    return rows, pivots


def rank(matrix):
    return len(reduce_rows(matrix)[1])


def kernel_vector(matrix):
    rows, pivots = reduce_rows(matrix)
    free = next((j for j in range(len(matrix[0])) if j not in pivots), None)
    need(free is not None, "kernel is required")
    vector = [F(j == free) for j in range(len(matrix[0]))]
    for i, pivot in enumerate(pivots):
        vector[pivot] = -rows[i][free]
    need(any(vector) and all(dot(row, vector) == 0 for row in matrix), "kernel residual")
    return vector


def canonical(vector):
    first = next((x for x in vector if x), 0)
    need(len(vector) == 8 and first != 0, "nonzero eight-coordinate vector")
    return tuple(x if first > 0 else -x for x in vector)


def build_roots(data):
    signs = data.get("signs")
    need(isinstance(signs, list) and len(signs) == 16, "sixteen omitted lines")
    omitted = set()
    for row in signs:
        need(isinstance(row, str) and len(row) == 8 and set(row) <= {"+", "-"}, "sign row")
        need(row.count("-") % 2 == 1, "odd half-spin parity")
        omitted.add(canonical(tuple(1 if s == "+" else -1 for s in row)))
    need(len(omitted) == 16, "distinct omitted lines")
    d8 = []
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, sign * 2
            d8.append(tuple(row))
    half = {(1, *tail) for tail in itertools.product((-1, 1), repeat=7)
            if tail.count(-1) % 2 == 1}
    need(omitted <= half, "omitted lines belong to shell")
    roots = sorted(set(d8) | (half - omitted))
    need(len(d8) == 56 and len(half - omitted) == 48 and len(roots) == 104, "shell sizes")
    need(all(dot(row, row) == 8 for row in roots), "doubled root norms")
    return d8, roots, sorted(omitted)


def paired_columns(roots):
    u = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[i + 1] = 1, sign
            u.append(row)
    indices = [roots.index(tuple(2 * x for x in row)) for row in u]
    need(multiply(u, transpose(u)) == [[2 * (i == j) for j in range(8)] for i in range(8)],
         "paired D8 basis orthogonality")
    return u, indices


def norm_fixture(vector, u, d8):
    absolute = sorted(map(abs, vector), reverse=True)
    h = absolute[0] + absolute[1]
    need(h > 0, "nonzero direction")
    coefficient_norm = sum(abs(dot(row, vector)) / F(2) for row in u)
    pair_max = sum(max(abs(vector[i]), abs(vector[i + 1])) for i in range(0, 8, 2))
    need(coefficient_norm == pair_max <= sum(absolute[:4]) <= 2 * h, "fixed-pair norm inequality")
    need(max(abs(dot(row, vector)) for row in d8) == 2 * h, "D8 support functional")


def direction_fixtures(u, d8):
    integer_count = 0
    for vector in itertools.product((-1, 0, 1), repeat=8):
        if any(vector):
            norm_fixture(vector, u, d8)
            integer_count += 1
    rational_count = 0
    for t in range(1, 129):
        vector = [F(((t + 3) * (j + 5) ** 2) % 37 - 18, 1 + (t + 2 * j) % 11) for j in range(8)]
        need(any(vector), "rational fixture nonzero")
        norm_fixture(vector, u, d8)
        rational_count += 1
    return integer_count, rational_count


def attaining_projectors(roots, omitted, indices):
    entries = 0
    for q in omitted:
        d = [[8 * (i == j) - q[i] * q[j] for j in range(8)] for i in range(8)]
        need(multiply(d, d) == [[8 * x for x in row] for row in d], "projector idempotence")
        need(rank(d) == 7 and all(dot(row, q) == 0 for row in d), "rank-seven projector")
        products = [dot(row, q) for row in roots]
        candidate = multiply(multiply(roots, d), transpose(roots))
        maximum = 0
        for i, left in enumerate(roots):
            for j, right in enumerate(roots):
                candidate_numerator = candidate[i][j]
                error_numerator = 8 * dot(left, right) - candidate_numerator
                need(error_numerator == products[i] * products[j], "literal entry identity")
                maximum = max(maximum, abs(error_numerator))
                entries += 1
        need(maximum == 16, "attained maximum error is 16/64")
        block = [[8 * dot(roots[i], roots[j]) - products[i] * products[j]
                  for j in indices] for i in indices]
        need(rank(block) == 7, "attaining 104-by-104 matrix has rank seven")
    return entries


def kernel_error_witness(candidate, a, roots, u, indices):
    need(all(sum(row[j] * a[k] for k, j in enumerate(indices)) == 0 for row in candidate),
         "selected-column null vector")
    z = [dot(column, a) for column in transpose(u)]
    need(any(z), "basis injectivity")
    need([dot(row, z) / F(2) for row in u] == a, "coefficient reconstruction")
    h = sum(sorted(map(abs, z), reverse=True)[:2])
    norm = sum(map(abs, a))
    need(norm <= 2 * h, "coefficient norm bound")
    error = max(abs(F(dot(left, right), 8) - candidate[i][j])
                for i, left in enumerate(roots) for j, right in enumerate(roots))
    residual = max(abs(dot(row, z) / F(4)) for row in roots)
    need(h / 2 <= residual <= error * norm and error >= F(1, 4), "unrestricted error witness")
    return {"max_entry_error": str(error), "kernel_l1": str(norm),
            "top_two_sum": str(h), "gram_residual_linf": str(residual)}


def carrier_fixtures(roots, omitted, u, indices):
    q = omitted[0]
    oblique = [[F(i == j) - F(q[i] * (j == 0), q[0]) for j in range(8)] for i in range(8)]
    expansive = [[F(2 * (i == j)) - F(q[i] * q[j], 4) for j in range(8)] for i in range(8)]
    indefinite = [[F((i == j) * (-1 if i == 0 else i < 7)) for j in range(8)] for i in range(8)]
    need(oblique != transpose(oblique), "oblique fixture is nonsymmetric")
    need(indefinite[0][0] < 0 < indefinite[1][1], "indefinite fixture signs")
    output = {}
    for name, d in (("nonsymmetric_oblique", oblique), ("noncontractive", expansive),
                    ("symmetric_indefinite", indefinite)):
        need(rank(d) == 7, "carrier fixture rank seven")
        raw = multiply(multiply(roots, d), transpose(roots))
        candidate = [[x / F(8) for x in row] for row in raw]
        a = kernel_vector(multiply(d, transpose(u)))
        output[name] = kernel_error_witness(candidate, a, roots, u, indices)
    return output


def unrestricted_fixture(roots, u, indices):
    a_factor = [list(row[:7]) for row in roots]
    b_factor = [list(row[:7]) for row in roots]
    a_factor[0][0] += 3
    b_factor[1][1] -= 5
    need(rank(a_factor) == rank(b_factor) == 7, "unrestricted factor ranks")
    augmented_a = [list(row) + [a_factor[i][0]] for i, row in enumerate(roots)]
    augmented_b = [list(row) + [b_factor[i][1]] for i, row in enumerate(roots)]
    need(rank(roots) == 8 and rank(augmented_a) == rank(augmented_b) == 9,
         "both factors leave carrier column space")
    raw = multiply(a_factor, transpose(b_factor))
    candidate = [[F(x, 8) for x in row] for row in raw]
    a = kernel_vector(transpose([b_factor[j] for j in indices]))
    result = kernel_error_witness(candidate, a, roots, u, indices)
    need(candidate != transpose(candidate), "unrestricted candidate is nonsymmetric")
    result.update({"left_factor_rank": 7, "right_factor_rank": 7,
                   "left_augmented_rank": 9, "right_augmented_rank": 9})
    return result


def controls(data, roots, u):
    results = []
    k = [[F(dot(left, right), 8) for right in roots] for left in roots]
    need(rank(multiply(u, transpose(u))) == 8 and all(k[i][i] == 1 for i in range(104)),
         "full-rank exact Gram control")
    results.append("rank_eight_exact_gram_has_zero_error")
    only_basis = [[F(i == j) - F(1, 8) for j in range(8)] for i in range(8)]
    need(rank(only_basis) == 7 and max(abs(F(i == j) - only_basis[i][j])
         for i in range(8) for j in range(8)) == F(1, 8), "incomplete-root control")
    results.append("orthogonal_eight_only_allows_one_eighth")
    q = roots[0]
    need(max(abs(dot(left, q) * dot(right, q)) for left in roots for right in roots) == 64,
         "retained-root projection has error one")
    results.append("retained_root_projection_error_one")
    need(F(dot(roots[0], roots[0]), 4) != 1, "wrong Gram normalization detected")
    results.append("wrong_coefficient_normalization_detected")
    mutants = [dict(data, signs=["++++++++", *data["signs"][1:]]),
               dict(data, signs=[data["signs"][0], *data["signs"][:-1]]),
               dict(data, signs=["bad", *data["signs"][1:]])]
    for index, mutant in enumerate(mutants):
        try:
            build_roots(mutant)
        except ValueError:
            results.append("malformed_missing_data_" + str(index))
        else:
            raise ValueError("malformed missing data accepted")
    return results


def source_inputs(package):
    repository = package.parents[1]
    manifest = json.loads((package / "SOURCES.json").read_text())
    verified = {}
    for entry in manifest["files"]:
        if entry.get("usage") == "input":
            path = Path(entry["path"])
            need(not path.is_absolute() and ".." not in path.parts, "relative source input")
            digest = hashlib.sha256((repository / path).read_bytes()).hexdigest()
            need(digest == entry["sha256"], "source digest: " + str(path))
            verified[str(path)] = digest
    missing_path = "research/p104-contractive-gram-deflation/MISSING.json"
    need(missing_path in verified, "omitted-root input is declared")
    return verified, json.loads((repository / missing_path).read_text())


def main():
    package = Path(__file__).resolve().parent
    sources, data = source_inputs(package)
    d8, roots, omitted = build_roots(data)
    u, indices = paired_columns(roots)
    integer_count, rational_count = direction_fixtures(u, d8)
    entries = attaining_projectors(roots, omitted, indices)
    result = {"schema_version": 1, "sharp_unrestricted_rank_seven_error": "1/4",
              "d8_root_lines": len(d8), "retained_root_lines": len(roots),
              "paired_root_columns": indices, "attaining_projectors": len(omitted),
              "literal_attaining_error_entries": entries,
              "ternary_nonzero_directions": integer_count, "rational_directions": rational_count,
              "carrier_fixtures": carrier_fixtures(roots, omitted, u, indices),
              "outside_carrier_fixture": unrestricted_fixture(roots, u, indices),
              "controls": controls(data, roots, u), "source_sha256": sources}
    print(json.dumps(result, sort_keys=True))
    print("PASS_P104_RANK_SEVEN_ERROR_FLOOR")


if __name__ == "__main__":
    main()
