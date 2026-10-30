#!/usr/bin/env python3
"""Exact factored-tensor audit at all actual P104 coordinates.

Imports no primary or predecessor executable. Literal-event certification is
the companion checker's obligation; this file proves the global block algebra.
Apache-2.0. ToikY with substantial OpenAI Codex assistance.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE_SHA256 = "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"
B2_SHA256 = "88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535"
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Dyadic:
    rows: tuple
    exponent: int = 0


def matrix(rows, exponent=0):
    rows = tuple(tuple(row) for row in rows)
    require(len(rows) == 104 and all(len(row) == 104 for row in rows), "actual matrix dimension")
    require(type(exponent) is int and exponent >= 0
            and all(type(value) is int for row in rows for value in row), "integer dyadic data")
    if not any(any(row) for row in rows):
        exponent = 0
    else:
        while exponent and all(value % 2 == 0 for row in rows for value in row):
            rows = tuple(tuple(value // 2 for value in row) for row in rows)
            exponent -= 1
    return Dyadic(rows, exponent)


def transpose(value):
    return matrix(zip(*value.rows), value.exponent)


@lru_cache(maxsize=None)
def sparse_rows(value):
    return tuple(tuple((index, entry) for index, entry in enumerate(row) if entry)
                 for row in value.rows)


@lru_cache(maxsize=None)
def times(left, right):
    result = []
    right_rows = sparse_rows(right)
    for row in sparse_rows(left):
        output = [0]*104
        for middle, value in row:
            for column, coefficient in right_rows[middle]:
                output[column] += value*coefficient
        result.append(output)
    return matrix(result, left.exponent+right.exponent)


def linear_combination(left, right, coefficient=1):
    exponent = max(left.exponent, right.exponent)
    a, b = 1 << (exponent-left.exponent), coefficient << (exponent-right.exponent)
    return matrix([[a*x+b*y for x, y in zip(row, other)]
                   for row, other in zip(left.rows, right.rows)], exponent)


@lru_cache(maxsize=None)
def frobenius(left, right):
    """Trace(left^t right), as an integer numerator and power-of-two denominator."""
    numerator = sum(x*y for row, other in zip(left.rows, right.rows) for x, y in zip(row, other))
    return numerator, left.exponent+right.exponent


def add_dyad(left, right):
    exponent = max(left[1], right[1])
    return ((left[0] << (exponent-left[1])) + (right[0] << (exponent-right[1])), exponent)


def norm_squared(terms):
    """Exact norm of sum sign*A tensor B, without a 10816-square matrix."""
    answer = (0, 0)
    for sign, row_factor, column_factor in terms:
        for other_sign, other_row, other_column in terms:
            left = frobenius(row_factor, other_row)
            right = frobenius(column_factor, other_column)
            answer = add_dyad(answer, (sign*other_sign*left[0]*right[0], left[1]+right[1]))
    require(answer[0] >= 0, "nonnegative exact Frobenius square")
    return answer


def tensor_product(left, right):
    return [(1, left, right)]


def tensor_times(left, right):
    return [(a*b, times(row, other_row), times(column, other_column))
            for a, row, column in left for b, other_row, other_column in right]


def tensor_minus(left, right):
    return left + [(-sign, row, column) for sign, row, column in right]


def zero_tensor(terms, message):
    require(norm_squared(terms)[0] == 0, message)


def block_times(left, right):
    return [[sum((tensor_times(left[i][k], right[k][j]) for k in range(2)), [])
             for j in range(2)] for i in range(2)]


def zero_blocks(left, right, message):
    for i in range(2):
        for j in range(2):
            zero_tensor(tensor_minus(left[i][j], right[i][j]), message+" block="+str((i, j)))


def nonzero_blocks(left, right, message):
    total = (0, 0)
    for i in range(2):
        for j in range(2):
            total = add_dyad(total, norm_squared(tensor_minus(left[i][j], right[i][j])))
    require(total[0] > 0, message)
    return {"numerator": total[0], "denominator_power_two": total[1]}


def geometry():
    path = ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json"
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256, "canonical fixture authentication")
    fixture = json.loads(raw)["section4_explicit_P104"]
    # Enumeration differs from the predecessor's pairs-plus-seven-sign loop.
    roots = set()
    for row in itertools.product((-2, 0, 2), repeat=8):
        support = [value for value in row if value]
        if len(support) == 2 and support[0] > 0:
            roots.add(row)
    for row in itertools.product((-1, 1), repeat=8):
        if row[0] == 1 and row.count(-1) % 2 == 0:
            roots.add(row)
    removed = {tuple(row) for row in fixture["F0"]+fixture["C"]}
    require(len(roots) == 120 and len(removed) == 16 and removed <= roots, "independent root domain")
    original = sorted(roots-removed)
    order = list(PIVOTS)+[i for i in range(104) if i not in PIVOTS]
    ports = [original[i] for i in order]
    gram = [[sum(x*y for x, y in zip(row, other)) for other in ports] for row in ports]
    require(all(gram[i][j] == 8*int(i == j) for i in range(8) for j in range(8)), "orthogonal pivots")
    require(all(gram[i][j] % 4 == 0 for i in range(8) for j in range(8, 104)), "half coefficient domain")
    b2 = [[gram[i][j]//4 for j in range(8, 104)] for i in range(8)]
    require(hashlib.sha256(json.dumps(b2, separators=(",", ":")).encode("ascii")).hexdigest()
            == B2_SHA256, "all 768 actual B2 entries")
    require(sum(value != 0 for row in b2 for value in row) == 384
            and all(value in (-1, 0, 1) for row in b2 for value in row), "actual B support/alphabet")
    require(all(sum(b2[i][k]*b2[j][k] for k in range(96)) == 48*int(i == j)
                for i in range(8) for j in range(8)), "actual BBt")
    identity = matrix([[int(i == j) for j in range(104)] for i in range(104)])
    pivot = matrix([[int(i == j and i < 8) for j in range(104)] for i in range(104)])
    upper_rows = [[2*int(i == j) for j in range(104)] for i in range(104)]
    inverse_rows = [row[:] for row in upper_rows]
    for i in range(8):
        upper_rows[i][8:] = b2[i][:]
        inverse_rows[i][8:] = [-value for value in b2[i]]
    upper, inverse = matrix(upper_rows, 1), matrix(inverse_rows, 1)
    actual_gram = matrix(gram, 3)
    return identity, pivot, upper, inverse, actual_gram, b2


def apply_numerator(value, vector):
    return [sum(coefficient*entry for coefficient, entry in zip(row, vector)) for row in value.rows]


def audit():
    identity, pivot, upper, inverse, gram, b2 = geometry()
    upper_t, inverse_t = transpose(upper), transpose(inverse)
    require(times(upper, inverse) == times(inverse, upper) == identity, "U two-sided inverse")
    require(times(times(upper_t, pivot), upper) == gram, "actual Gram congruence")
    moment = times(upper, upper_t)
    moment_inverse = times(inverse_t, inverse)
    require(times(moment, moment_inverse) == times(moment_inverse, moment) == identity, "M/N inverse")
    require(times(gram, gram) == matrix([[13*x for x in row] for row in gram.rows], gram.exponent),
            "A square equals 13A")
    require(times(times(inverse_t, gram), inverse) == pivot, "lower one-axis conjugation")

    unit = tensor_product(identity, identity)
    lower = [[unit, []], [tensor_product(gram, identity), unit]]
    upper_stage = [[unit, [(-1, identity, gram)]], [[], unit]]
    coded_lower = [[unit, []], [tensor_product(pivot, moment), unit]]
    coded_upper = [[unit, [(-1, moment, pivot)]], [[], unit]]
    # C=diag(U tensor U^-t, U^-t tensor U), with its explicit two-sided inverse.
    coding = [[tensor_product(upper, inverse_t), []], [[], tensor_product(inverse_t, upper)]]
    decoding = [[tensor_product(inverse, upper_t), []], [[], tensor_product(upper_t, inverse)]]
    block_identity = [[unit, []], [[], unit]]
    zero_blocks(block_times(decoding, coding), block_identity, "global decode/encode identity")
    zero_blocks(block_times(coding, decoding), block_identity, "global encode/decode identity")
    zero_blocks(block_times(block_times(coding, lower), decoding), coded_lower, "coded lower Gram stage")
    zero_blocks(block_times(block_times(coding, upper_stage), decoding), coded_upper, "coded upper Gram stage")

    reference_pair = block_times(upper_stage, lower)
    coded_pair = block_times(coded_upper, coded_lower)
    zero_blocks(block_times(block_times(decoding, coded_pair), coding), reference_pair, "decoded one-pair endpoint")
    reference_twice = block_times(reference_pair, reference_pair)
    coded_twice = block_times(coded_pair, coded_pair)
    zero_blocks(block_times(block_times(decoding, coded_twice), coding), reference_twice,
                "decoded two-pair all-coordinate endpoint")

    # Corrected identity shears have different, full-dimensional coefficients.
    plain_identity_lower = [[unit, []], [unit, unit]]
    plain_identity_upper = [[unit, [(-1, identity, identity)]], [[], unit]]
    completed_lower = [[unit, []], [tensor_product(moment_inverse, moment), unit]]
    completed_upper = [[unit, [(-1, moment, moment_inverse)]], [[], unit]]
    zero_blocks(block_times(block_times(coding, plain_identity_lower), decoding), completed_lower,
                "corrected identity lower coefficient")
    zero_blocks(block_times(block_times(coding, plain_identity_upper), decoding), completed_upper,
                "corrected identity upper coefficient")
    side = linear_combination(moment_inverse, pivot, -1)
    expected_side = times(times(inverse_t, linear_combination(identity, gram, -1)), inverse)
    require(side == expected_side, "identity completion side congruence")
    # (I-A)(I-A/12)=I follows from A^2=13A. The inverse is used over Q only;
    # this is an algebraic full-rank argument, not a dyadic primitive or tariff.
    square = times(gram, gram)
    require(linear_combination(square, gram, -13).rows == matrix([[0]*104 for _ in range(104)]).rows,
            "rational inverse witness for I-A")

    kernel = [-b2[i][0] for i in range(8)]+[2]+[0]*95
    require(any(kernel) and apply_numerator(gram, kernel) == [0]*104, "nonzero Gram-kernel residual")
    encoded_kernel = apply_numerator(upper, kernel)
    require(encoded_kernel[:8] == [0]*8 and encoded_kernel[8] != 0,
            "kernel information retained outside pivot query")
    require(apply_numerator(linear_combination(identity, gram, -1), kernel)
            == [entry << linear_combination(identity, gram, -1).exponent for entry in kernel],
            "omitted identity-side separating residual")

    wrong_moment = times(upper_t, upper)
    wrong_coded_lower = [[unit, []], [tensor_product(pivot, wrong_moment), unit]]
    controls = {
        "wrong_transpose_order": nonzero_blocks(coded_lower, wrong_coded_lower, "wrong M order must differ"),
        "reversed_stage_order": nonzero_blocks(reference_pair, block_times(lower, upper_stage),
                                                  "Gram stage order must differ"),
        "omitted_lower_identity_side": nonzero_blocks(completed_lower, coded_lower,
                                                        "Gram lower is not identity lower"),
        "omitted_upper_identity_side": nonzero_blocks(completed_upper, coded_upper,
                                                        "Gram upper is not identity upper"),
    }
    return {"actual_ports": 104, "data_coordinates": 21632, "bank_block_entries": 10816**2,
            "coefficient_domain": "real dyadic matrices; applies separately to Gaussian components",
            "global_block_identities": 8, "identity_side_rank_per_bank": 10816,
            "negative_control_norms": controls, "native_supplier_admitted": False, "new_kappa": False}


if __name__ == "__main__":
    print("PASS_INDEPENDENT_P104_TENSOR_WORD_AUDIT " + json.dumps(audit(), sort_keys=True))
