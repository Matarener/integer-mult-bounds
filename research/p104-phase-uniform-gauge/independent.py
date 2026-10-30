#!/usr/bin/env python3
"""Separate binary elimination and literal small-matrix gauge checks.

Apache-2.0. ToikY with substantial OpenAI Codex assistance. This checker
imports no primary or predecessor executable and is not human/native review.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_PINS = {
    "RESULT.json": "ce05a27ebc98677bec4febaa488fa03f5b6fc60216aa43b34298444d12f7ab6c",
    "README.md": "d13777b9065d4d575cbc0e41293b454f15ad0455d5047bb36c6b1ed527ff48e0",
    "PROOF.md": "bdc7d868e4411541a33179af683f48011e66d6446a45bef363f3f3dd5163f717",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def weight(value):
    return bin(value).count("1")


def dot(left, right):
    return weight(left & right) % 2


def authenticated_result():
    for name, pin in SOURCE_PINS.items():
        raw = (HERE / "source" / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin, "independent source: " + name)
    return json.loads((HERE / "source" / "RESULT.json").read_bytes())


def solve_character(labels, desired_weight):
    """RREF of the 104 equations, rather than enumeration of orthogonal maps."""
    equations = [[p, ((desired_weight - weight(p)) // 2) % 2] for p in labels]
    rank, pivots = 0, []
    for column in range(9):
        choice = next((r for r in range(rank, len(equations))
                       if equations[r][0] & (1 << column)), None)
        if choice is None:
            continue
        equations[rank], equations[choice] = equations[choice], equations[rank]
        for r in range(len(equations)):
            if r != rank and equations[r][0] & (1 << column):
                equations[r][0] ^= equations[rank][0]
                equations[r][1] ^= equations[rank][1]
        pivots.append(column)
        rank += 1
    require(all(mask or not rhs for mask, rhs in equations), "consistent gauge character")
    require(rank == 9, "published labels must span all nine coordinates")
    solution = sum(equations[r][1] << column for r, column in enumerate(pivots))
    require(all((weight(p) + 2*dot(p, solution)) % 4 == desired_weight for p in labels),
            "solved phase character")
    return solution, rank


def apply_columns(columns, value):
    output = 0
    for index, column in enumerate(columns):
        if value & (1 << index):
            output ^= column
    return output


def tensor(left, right):
    result = 0
    for i in range(9):
        for j in range(9):
            if left & (1 << i) and right & (1 << j):
                result |= 1 << (9*i+j)
    return result


def multiply(left, right):
    return [[sum(x*y for x, y in zip(row, column)) for column in zip(*right)]
            for row in left]


def permutation(size, index):
    return [[int(j == index(i)) for j in range(size)] for i in range(size)]


def small_literal_matrices():
    """Four-bit address matrices, including the necessary full-F defect."""
    size, selected = 16, 15
    mapping = lambda x: x ^ (selected if dot(x, selected) else 0)
    relabel = permutation(size, mapping)
    translation = permutation(size, lambda x: x ^ selected)
    alpha, beta = (1+1j)/2, (1-1j)/2
    full = [[alpha**(4-weight(x ^ y))*beta**weight(x ^ y)
             for y in range(size)] for x in range(size)]
    transformed = multiply(multiply(relabel, full), relabel)
    require(transformed == multiply(full, translation), "literal F conjugation")
    require(transformed != full, "gauge is not a free F-preserving relabel")
    exit_encoding = multiply(translation, relabel)
    require(multiply(full, relabel) == multiply(exit_encoding, full), "all-role entry/exit tags")
    require(multiply(full, exit_encoding) == multiply(relabel, full), "alternating completed-F tags")
    covariance = 0
    for u in range(size):
        modulation = [[int(x == y) * (-1)**dot(x, u) for y in range(size)]
                      for x in range(size)]
        wanted_modulation = [[int(x == y) * (-1)**dot(x, mapping(u)) for y in range(size)]
                             for x in range(size)]
        require(multiply(multiply(relabel, modulation), relabel) == wanted_modulation,
                "literal Z covariance")
        if weight(u) % 2:
            primitive = [[alpha*int(x == y)+beta*int(y == (x ^ u))
                          for y in range(size)] for x in range(size)]
            wanted = [[alpha*int(x == y)+beta*int(y == (x ^ mapping(u)))
                       for y in range(size)] for x in range(size)]
            require(multiply(multiply(relabel, primitive), relabel) == wanted,
                    "literal rank-one C covariance")
        covariance += 1
    # Every local role gets the same tag, including 72 nonzero independent dirty fixtures.
    left_operator = multiply(full, relabel)
    right_operator = multiply(exit_encoding, full)
    for role in range(280):
        payload = [complex((role+3)*(x+1), (role+1)*(3*x-7)) for x in range(size)]
        left = [sum(a*b for a, b in zip(row, payload)) for row in left_operator]
        right = [sum(a*b for a, b in zip(row, payload)) for row in right_operator]
        require(left == right, "arbitrary nonzero data/helper fixture")
    return covariance


def short_translation_words():
    """Finite three-bit corroboration; the universal lower bound is written."""
    labels = [u for u in range(8) if weight(u) % 2]
    gates = [tuple(sign*dot(s, u) % 4 for s in range(8))
             for u in labels for sign in (-1, 1)]
    targets = {a: tuple(2*dot(s, a) for s in range(8))
               for a in range(1, 8) if weight(a) % 2 == 0}
    checked = 0
    for length in range(4):
        for word in itertools.product(gates, repeat=length):
            phase = tuple(sum(gate[s] for gate in word) % 4 for s in range(8))
            require(phase not in targets.values(), "translation shorter than four")
            checked += 1
    for a, target in targets.items():
        first, second = 1, 1 ^ a
        require(weight(first) % 2 == weight(second) % 2 == 1, "four-call odd labels")
        phase = tuple((2*dot(s, first)+2*dot(s, second)) % 4 for s in range(8))
        require(phase == target, "four-call translation attainment")
    return checked, len(targets)


def main():
    source = authenticated_result()
    labels = source["physical_labels"]
    require(len(set(labels)) == 104 and all(type(p) is int and 0 < p < 512
                                          and weight(p) % 2 for p in labels), "source label domain")
    character, rank = solve_character(labels, 3)
    forbidden, _ = solve_character(labels, 1)
    require(character == 420 and forbidden == 91 and forbidden == (character ^ 511),
            "unique phase-uniform characters")
    require(weight(character) % 2 == 0 and weight(forbidden) % 2 == 1,
            "orthogonal characteristic-vector exclusion")
    columns = [1, 2, 416, 8, 16, 388, 64, 292, 164]
    transform = lambda value: apply_columns(columns, value)
    require(transform(511) == 511 and transform(character) == character, "fixed characteristic data")
    for x in range(512):
        require(transform(transform(x)) == x, "independent involution")
        require((weight(transform(x))-weight(x)-2*dot(x, character)) % 4 == 0,
                "independent quadratic refinement")
        for y in range(512):
            require(dot(transform(x), transform(y)) == dot(x, y), "independent orthogonality")
    # Exhaustive one-axis Fourier equality, not the predecessor's 512 port-phase census.
    for frequency in range(512):
        require((weight(transform(frequency))-weight(frequency)) % 4
                == 2*dot(character, frequency), "Fourier full-F translation defect")
    # A coordinate permutation after O leaves the input character unchanged but
    # changes its output image. This detects inverse/conjugation convention errors.
    def swap_zero_two(value):
        return value ^ (5 if ((value >> 0) ^ (value >> 2)) & 1 else 0)
    general = lambda value: swap_zero_two(transform(value))
    general_inverse = lambda value: transform(swap_zero_two(value))
    output_character = general(character)
    require(output_character == 417 and output_character != character,
            "non-involutive gauge output character")
    require(any(general(general(value)) != value for value in range(512)),
            "general-gauge convention control is not involutive")
    for frequency in range(512):
        require(general_inverse(general(frequency)) == frequency, "general inverse convention")
        require((weight(general(frequency))-weight(frequency)) % 4
                == 2*dot(character, frequency), "general input character")
        require((weight(general_inverse(frequency))-weight(frequency)) % 4
                == 2*dot(output_character, frequency), "general output character")
        require((weight(general(frequency))-weight(frequency)) % 4
                == 2*dot(output_character, general(frequency)), "general matched exit tag")
    changed = [transform(p) for p in labels]
    require(all(weight(p) % 4 == 3 for p in changed), "phase-uniform root gauge")
    product_checks = 0
    for old_left, new_left in zip(labels, changed):
        for old_right, new_right in zip(labels, changed):
            require(weight(tensor(new_left, new_right)) % 4 == 1, "uniform product phase")
            require(dot(old_left, old_right) == dot(new_left, new_right), "port pairing preservation")
            product_checks += 1
    tensor_columns = [tensor(columns[i], columns[j]) for i in range(9) for j in range(9)]
    tensor_map = lambda value: apply_columns(tensor_columns, value)
    correction = tensor(character, 511) ^ tensor(511, character)
    by_quadratic_columns = sum(((weight(column)-1)//2 % 2) << index
                               for index, column in enumerate(tensor_columns))
    require(correction == by_quadratic_columns == 430582246074561917307300,
            "universal tensor input character")
    require(weight(correction) == 40 and tensor_map(correction) == correction,
            "explicit tensor output character")
    # Basis and two-basis sums corroborate the written polarization argument in dimension81.
    for i in range(81):
        for j in range(i, 81):
            value = (1 << i) if i == j else (1 << i) | (1 << j)
            require((weight(tensor_map(value))-weight(value)-2*dot(value, correction)) % 4 == 0,
                    "tensor quadratic identity")
    covariance = small_literal_matrices()
    short_words, targets = short_translation_words()
    gate = source["gate"]
    roles = 2*104**2 + 2*104*72
    capacity = 81*roles
    required = capacity-104**2
    bill = 208*2576 + required-208*2312
    require((roles, capacity, bill, bill-capacity) == (36608, 2965248, 3009344, 44096),
            "unchanged favorable budget")
    require(gate["W"] == roles and gate["lower_mass"] == bill and gate["excess"] == 44096,
            "predecessor gate binding")
    print("PASS_INDEPENDENT_PHASE_UNIFORM_GAUGE", "label_rank="+str(rank),
          "orthogonality_pairs=262144", "product_lines="+str(product_checks),
          "literal_covariance_labels="+str(covariance), "all_role_fixtures=280",
          "short_words="+str(short_words), "even_targets="+str(targets),
          "unchanged_excess=44096", "no_new_kappa")


if __name__ == "__main__":
    main()
