#!/usr/bin/env python3
"""Replay a bounded matched-plane factorization of the selected P111 bit map.

The result is an exact local identity and a scoped rational copy-rank screen.
It does not provide a physical two-unpaid endpoint contract or change kappa.
"""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
EXPECTED = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
CEILING = "research/complex-local-word-ceiling/ceiling.py"
PREDECESSOR = "research/p111-parseval-copy-interface/RESULT.json"
PORTS = 111
CHANNELS = 9
REGISTERS = 661


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def combine(vectors, coefficients):
    value = 0
    for i, vector in enumerate(vectors):
        if coefficients >> i & 1:
            value ^= vector
    return value


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def decoder_map(target_factors, source_factors):
    """Return the 111 target rows as 661-bit masks over F2."""
    return [sum(parity(target & source) << j
                for j, source in enumerate(source_factors))
            for target in target_factors]


def outer9(left, right):
    return sum(1 << (9 * i + j)
               for i in range(9) if left >> i & 1
               for j in range(9) if right >> j & 1)


def identity9():
    return sum(1 << (10 * i) for i in range(9))


def matrix_rank(rows):
    """Exact rational row rank using Fraction elimination."""
    pivots = {}
    for raw in rows:
        row = [Fraction(value) for value in raw]
        for col, pivot in sorted(pivots.items()):
            coefficient = row[col]
            if coefficient:
                row = [a - coefficient * b for a, b in zip(row, pivot)]
        col = next((i for i, value in enumerate(row) if value), None)
        if col is not None:
            coefficient = row[col]
            pivots[col] = [value / coefficient for value in row]
    return len(pivots)


def factor_gram(binary_gram):
    """Build Q with QQ^T = B over F2, using a deterministic congruence basis."""
    n = len(binary_gram)
    row_bits = [sum(value << j for j, value in enumerate(row))
                for row in binary_gram]
    pivots = {}
    independent_rows = []
    for i, value in enumerate(row_bits):
        reduced = value
        while reduced:
            bit = reduced.bit_length() - 1
            if bit in pivots:
                reduced ^= pivots[bit]
            else:
                pivots[bit] = reduced
                independent_rows.append(i)
                break
    require(len(independent_rows) == CHANNELS, "P111 Gram rank changed")
    small = [[binary_gram[i][j] for j in independent_rows]
             for i in independent_rows]
    small_bits = [sum(value << j for j, value in enumerate(row))
                  for row in small]

    def bilinear(left, right):
        value = 0
        remaining = left
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            value ^= small_bits[bit.bit_length() - 1]
        return parity(value & right)

    def project(rows, vector):
        return [row ^ (vector if bilinear(row, vector) else 0)
                for row in rows]

    residual = [1 << i for i in range(CHANNELS)]
    basis = []
    while len(basis) < CHANNELS:
        anisotropic = [i for i, row in enumerate(residual)
                       if bilinear(row, row)]
        if anisotropic:
            vector = residual[anisotropic[0]]
            basis.append(vector)
            residual = project(residual, vector)
        else:
            nonzero = [row for row in residual if row]
            require(len(nonzero) >= 2, "degenerate residual form")
            left = nonzero[0]
            right = next((row for row in nonzero[1:]
                          if bilinear(left, row)), None)
            require(right is not None and basis, "no congruence pivot")
            old = basis.pop(0)
            basis.extend((old ^ left, old ^ right, old ^ left ^ right))
            residual = residual_after(basis, small_bits)

    require(all(bilinear(left, right) == int(i == j)
                for i, left in enumerate(basis)
                for j, right in enumerate(basis)),
            "orthonormal binary basis failed")
    result = []
    for row in binary_gram:
        coordinates = sum(row[index] << j
                          for j, index in enumerate(independent_rows))
        result.append(sum(parity(coordinates & basis[j]) << j
                          for j in range(CHANNELS)))
    require(all(parity(result[i] & result[j]) == binary_gram[i][j]
                for i in range(n) for j in range(n)),
            "binary Gram factorization failed")
    return result


def residual_after(basis, small_bits):
    """Orthogonally project the fixed coordinate basis off each basis vector."""
    rows = [1 << i for i in range(CHANNELS)]

    def bilinear(left, right):
        value = 0
        remaining = left
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            value ^= small_bits[bit.bit_length() - 1]
        return parity(value & right)

    for vector in basis:
        rows = [row ^ (vector if bilinear(row, vector) else 0)
                for row in rows]
    return rows


def zero_dot_matching(binary_gram):
    """Deterministic MRV matching in the graph B[i,j]=0; leave one port."""
    n = len(binary_gram)
    adjacency = [sum(1 << j for j in range(n)
                     if j != i and binary_gram[i][j] == 0)
                 for i in range(n)]

    def complete(mask):
        if not mask:
            return []
        best = None
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            vertex = bit.bit_length() - 1
            options = adjacency[vertex] & mask
            degree = options.bit_count()
            if best is None or degree < best[0]:
                best = (degree, vertex, options)
            if degree <= 1:
                break
        if best is None or best[0] == 0:
            return None
        _degree, vertex, options = best
        choices = []
        while options:
            bit = options & -options
            options ^= bit
            partner = bit.bit_length() - 1
            rest = mask ^ (1 << vertex) ^ (1 << partner)
            choices.append(((adjacency[partner] & rest).bit_count(),
                            partner, rest))
        for _degree, partner, rest in sorted(choices):
            tail = complete(rest)
            if tail is not None:
                return [(vertex, partner)] + tail
        return None

    full = (1 << n) - 1
    for residual in sorted(range(n), key=lambda i: (adjacency[i].bit_count(), i)):
        pairs = complete(full ^ (1 << residual))
        if pairs is not None:
            normalized = tuple(sorted(tuple(sorted(pair)) for pair in pairs))
            return normalized, residual, adjacency
    raise ValueError("no 55-pair orthogonal matching found")


def solve_xor_columns(columns, target):
    """Solve a binary column system and return one coefficient bitmask."""
    elimination = {}
    for index, original in enumerate(columns):
        value = original
        combination = 1 << index
        while value:
            pivot = value.bit_length() - 1
            if pivot in elimination:
                value ^= elimination[pivot][0]
                combination ^= elimination[pivot][1]
            else:
                elimination[pivot] = value, combination
                break
    value = target
    solution = 0
    while value:
        pivot = value.bit_length() - 1
        if pivot not in elimination:
            return None
        value ^= elimination[pivot][0]
        solution ^= elimination[pivot][1]
    return solution


def solve_plane_coefficients(pairs, residual, labels):
    columns = []
    for i, j in pairs:
        for left_selector, right_selector in ((0, 0), (0, 1), (1, 0), (1, 1)):
            left = (labels[i], labels[j])[left_selector]
            right = (labels[i], labels[j])[right_selector]
            columns.append(outer9(left, right))
    target = identity9() ^ outer9(labels[residual], labels[residual])
    solution = solve_xor_columns(columns, target)
    if solution is None:
        return None
    matrices = []
    for pair_index in range(len(pairs)):
        matrices.append([[((solution >> (4 * pair_index + 2 * i + j)) & 1)
                          for j in range(2)] for i in range(2)])
    return matrices


def factor_2x2(matrix):
    determinant = ((matrix[0][0] * matrix[1][1]) ^
                   (matrix[0][1] * matrix[1][0]))
    rank = 2 if determinant else (1 if any(any(row) for row in matrix) else 0)
    if rank == 0:
        return []
    if rank == 1:
        for left in range(1, 4):
            for right in range(1, 4):
                product = [[((left >> i) & 1) * ((right >> j) & 1)
                            for j in range(2)] for i in range(2)]
                if product == matrix:
                    return [(left, right)]
        raise ValueError("rank-one plane matrix did not factor")
    return [(1, matrix[0][0] | (matrix[0][1] << 1)),
            (2, matrix[1][0] | (matrix[1][1] << 1))]


def canonical_matching(pairs):
    return tuple(sorted(tuple(sorted(pair)) for pair in pairs))


def matching_neighbors(base, base_residual, binary_gram):
    candidates = {base: base_residual}
    for first, second in itertools.combinations(range(len(base)), 2):
        i, j = base[first]
        k, ell = base[second]
        for pair_a, pair_b in (((i, k), (j, ell)), ((i, ell), (j, k))):
            pair_a = tuple(sorted(pair_a))
            pair_b = tuple(sorted(pair_b))
            if binary_gram[pair_a[0]][pair_a[1]] != 0:
                continue
            if binary_gram[pair_b[0]][pair_b[1]] != 0:
                continue
            changed = [pair for index, pair in enumerate(base)
                       if index not in (first, second)] + [pair_a, pair_b]
            candidates[canonical_matching(changed)] = base_residual
    for edge, (i, j) in enumerate(base):
        for new_residual, new_pair in (
                (i, tuple(sorted((base_residual, j)))),
                (j, tuple(sorted((base_residual, i))))):
            if binary_gram[new_pair[0]][new_pair[1]] != 0:
                continue
            changed = [pair for index, pair in enumerate(base) if index != edge]
            changed.append(new_pair)
            candidates[canonical_matching(changed)] = new_residual
    return candidates


def make_pairing_pricer(labels, lines):
    """Cache exact support spans, then price their rational pairing rank."""
    @lru_cache(None)
    def support_basis(coefficient):
        support = [line for i, line in enumerate(lines)
                   if parity(labels[i] & coefficient)]
        return tuple(tuple(row) for row in rational_basis(support))

    @lru_cache(None)
    def price(left_label, right_label):
        left = support_basis(left_label)
        right = support_basis(right_label)
        pairing = [[sum(a * b for a, b in zip(u, v))
                    for v in right] for u in left]
        return matrix_rank(pairing)

    return price


def rational_basis(rows):
    """Incremental exact row reduction; no numerical rank tolerance."""
    pivots = {}
    for original in rows:
        row = [Fraction(value) for value in original]
        for col, pivot in sorted(pivots.items()):
            coefficient = row[col]
            if coefficient:
                row = [a - coefficient * b for a, b in zip(row, pivot)]
        col = next((i for i, value in enumerate(row) if value), None)
        if col is not None:
            coefficient = row[col]
            pivots[col] = [value / coefficient for value in row]
    return list(pivots.values())


def terms_and_invoice(pairs, residual, matrices, labels, price):
    terms = []
    for (i, j), matrix in zip(pairs, matrices):
        for left_selector, right_selector in factor_2x2(matrix):
            left = ((labels[i] if left_selector & 1 else 0) ^
                    (labels[j] if left_selector & 2 else 0))
            right = ((labels[i] if right_selector & 1 else 0) ^
                     (labels[j] if right_selector & 2 else 0))
            terms.append((left, right, price(left, right)))
    terms.append((labels[residual], labels[residual],
                  price(labels[residual], labels[residual])))
    return terms


def candidate_report(candidate_map, labels, price):
    scored = []
    solvable = 0
    for pairs, residual in sorted(candidate_map.items()):
        matrices = solve_plane_coefficients(pairs, residual, labels)
        if matrices is None:
            continue
        solvable += 1
        terms = terms_and_invoice(pairs, residual, matrices, labels, price)
        histogram = Counter(cost for _left, _right, cost in terms)
        scored.append((sum(histogram.elements()), tuple(sorted(histogram.items())),
                       len(terms), pairs, residual, matrices, terms))
    scored.sort(key=lambda item: item[:5])
    return solvable, scored


def inverse_matrix(rows):
    """Invert a nonsingular 9-by-9 binary matrix given as row bitmasks."""
    augmented = [rows[i] | (1 << (9 + i)) for i in range(9)]
    for column in range(9):
        pivot = next((i for i in range(column, 9)
                      if augmented[i] >> column & 1), None)
        require(pivot is not None, "target basis change is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        for i in range(9):
            if i != column and augmented[i] >> column & 1:
                augmented[i] ^= augmented[column]
    inverse = [row >> 9 for row in augmented]
    require(all(sum(((rows[i] >> k) & 1) * ((inverse[k] >> j) & 1)
                    for k in range(9)) % 2 == int(i == j)
                for i in range(9) for j in range(9)),
            "binary inverse check failed")
    return inverse


def transpose(rows):
    return [sum(((rows[i] >> j) & 1) << i for i in range(9))
            for j in range(9)]


def multiply_row(row, matrix_rows):
    columns = transpose(matrix_rows)
    return sum(parity(row & column) << j for j, column in enumerate(columns))


def align_full_dirty_sources(target_factors, source_factors, labels):
    """Change basis so target factors equal Q and preserve the full map."""
    target_columns = [sum(((row >> j) & 1) << i
                          for i, row in enumerate(target_factors))
                      for j in range(CHANNELS)]
    label_columns = [sum(((row >> j) & 1) << i
                         for i, row in enumerate(labels))
                     for j in range(CHANNELS)]
    transform_columns = []
    for column in label_columns:
        solution = solve_xor_columns(target_columns, column)
        require(solution is not None, "target factors do not span Gram labels")
        transform_columns.append(solution)
    transform_rows = [sum(((transform_columns[j] >> i) & 1) << j
                          for j in range(CHANNELS))
                      for i in range(CHANNELS)]
    require([multiply_row(row, transform_rows) for row in target_factors] == labels,
            "target basis transform does not align with Q")
    inverse_transpose = transpose(inverse_matrix(transform_rows))
    aligned_sources = [multiply_row(row, inverse_transpose)
                       for row in source_factors]
    require(aligned_sources[:PORTS] == labels,
            "aligned source port factors do not equal Q")
    return transform_rows, aligned_sources


def support_mask(labels, coefficient):
    return sum((parity(label & coefficient)) << i
               for i, label in enumerate(labels))


def term_decoder_map(terms, labels, aligned_sources):
    target_masks = [support_mask(labels, left) for left, _right, _price in terms]
    source_masks = [support_mask(aligned_sources, right)
                    for _left, right, _price in terms]
    result = [0] * PORTS
    for target, row in enumerate(result):
        for target_mask, source_mask_value in zip(target_masks, source_masks):
            if target_mask >> target & 1:
                row ^= source_mask_value
        result[target] = row
    return result


def dirty_digest(rows):
    width = (REGISTERS + 7) // 8
    return hashlib.sha256(b"".join(row.to_bytes(width, "little")
                                    for row in rows)).hexdigest()


def audit():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for entry in sources["files"]:
        if entry["usage"] == "input":
            actual = hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
            require(actual == entry["sha256"], "source pin mismatch: " + entry["path"])

    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    expected = json.loads((ROOT / EXPECTED).read_text())["word"]
    predecessor = json.loads((ROOT / PREDECESSOR).read_text())
    require((word["v"], 2 * word["v"] + word["R"], word["h"]) ==
            (PORTS, REGISTERS, 8), "selected P111 word dimensions changed")
    require(word["punctured"] == [10, 15, 51, 53, 56, 66, 72, 89, 111],
            "selected puncture changed")

    lines = word["lines"]
    full_gram = [[sum(a * b for a, b in zip(left, right))
                  for right in lines] for left in lines]
    require(all(value % 2 == 0 for row in full_gram for value in row),
            "root-line Gram has odd entry")
    binary_gram = [[(1 + value // 2) & 1 for value in row]
                   for row in full_gram]
    labels = factor_gram(binary_gram)
    require(binary_rank(labels) == CHANNELS, "label factor rank changed")

    base_pairs, base_residual, adjacency = zero_dot_matching(binary_gram)
    require(len(base_pairs) == 55, "base matching does not cover 110 ports")
    require(all(binary_gram[i][j] == 0 for i, j in base_pairs),
            "base matching contains a nonorthogonal edge")
    candidates = matching_neighbors(base_pairs, base_residual, binary_gram)
    require(len(candidates) == 751, "bounded matching neighborhood changed")
    price = make_pairing_pricer(labels, lines)
    solvable, scored = candidate_report(candidates, labels, price)
    require(solvable == len(candidates), "a neighborhood coefficient system is unsolvable")
    require(scored, "no candidate plane factorization")

    best_charge, best_hist, best_terms_count, best_pairs, best_residual, \
        best_matrices, best_terms = scored[0]
    require((best_charge, best_terms_count, best_hist) ==
            (112, 14, ((8, 14),)), "best local scalar-copy-rank charge changed")
    require(sum(1 for item in scored if item[0] == best_charge) == 2,
            "number of tied neighborhood minima changed")
    require(scored[2][0] == 128,
            "next local-neighborhood charge changed")
    active_matrix_ranks = Counter(
        2 if ((m[0][0] * m[1][1]) ^ (m[0][1] * m[1][0]))
        else (1 if any(any(row) for row in m) else 0)
        for m in best_matrices)
    require(dict(sorted(active_matrix_ranks.items())) == {0: 45, 1: 7, 2: 3},
            "best plane coefficient rank profile changed")

    coefficient_sum = 0
    for (i, j), matrix in zip(best_pairs, best_matrices):
        for left_selector in range(2):
            for right_selector in range(2):
                if matrix[left_selector][right_selector]:
                    coefficient_sum ^= outer9((labels[i], labels[j])[left_selector],
                                               (labels[i], labels[j])[right_selector])
    coefficient_sum ^= outer9(labels[best_residual], labels[best_residual])
    require(coefficient_sum == identity9(),
            "plane and residual coefficients do not sum to identity")

    # Recover the actual P111 word factors from its D/A schedule.
    values = [1 << i for i in range(REGISTERS)]
    for section in ("D", "A"):
        for _frame, destination, source_registers in word[section]:
            for source in source_registers:
                values[destination] ^= values[source]
    target_factors = [sum((channel in word["scatter"][i]) << channel
                          for channel in range(CHANNELS))
                      for i in range(PORTS)]
    source_factors = [values[index] for index in word["ret"]]
    source_factors_by_register = [sum(((channel >> register) & 1) << i
                                      for i, channel in enumerate(source_factors))
                                  for register in range(REGISTERS)]
    require(binary_rank(target_factors) == binary_rank(source_factors_by_register)
            == CHANNELS, "selected decoder factors are not full rank")
    old_map = decoder_map(target_factors, source_factors_by_register)
    require([row & ((1 << PORTS) - 1) for row in old_map] ==
            [sum(binary_gram[i][j] << j for j in range(PORTS))
             for i in range(PORTS)], "selected P111 source-port map changed")
    original_digest = dirty_digest(old_map)
    require(original_digest == predecessor["dirty_map_sha256"],
            "full dirty map differs from prior independent receipt")

    transform_rows, aligned_sources = align_full_dirty_sources(
        target_factors, source_factors_by_register, labels)
    new_map = term_decoder_map(best_terms, labels, aligned_sources)
    require(new_map == old_map,
            "matched-plane factorization differs on the 111-by-661 dirty map")
    require(len(new_map) == PORTS and
            all(row.bit_length() <= REGISTERS for row in new_map),
            "dirty map dimensions changed")
    require(term_decoder_map(best_terms[:-1], labels, aligned_sources) != old_map,
            "omitting residual-line control was not detected")
    require(term_decoder_map(best_terms[1:], labels, aligned_sources) != old_map,
            "omitting a plane-term control was not detected")

    local_profile = {int(rank): count
                     for rank, count in expected["local_histogram"].items()}
    for rank in expected["copy_ranks"]:
        local_profile[rank] -= 1
    for rank, count in Counter(term[2] for term in best_terms).items():
        local_profile[rank] = local_profile.get(rank, 0) + count
    require(sum(rank * count for rank, count in local_profile.items()) == 5178,
            "local paid rank mass changed")

    spec = importlib.util.spec_from_file_location("pinned_ceiling", ROOT / CEILING)
    ceiling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling)
    unpaid = Fraction(221, 111)
    target_a = Fraction(3, 997)
    candidate_relaxation = ceiling.relax(
        local_profile, 64, 888, 9, best_charge, target_a, R=42, unpaid=unpaid)
    require(candidate_relaxation[1] < 1,
            "conditional two-plane weighted screen no longer passes a=3/997")
    a_bracket = ceiling.ceiling(
        local_profile, 64, 888, 9, best_charge, R=42, unpaid=unpaid,
        grid=Fraction(1, 10**12))
    low, high = 0, 500
    while low < high:
        middle = (low + high + 1) // 2
        test = ceiling.relax(local_profile, 64, 888, 9,
                             best_charge + middle, target_a,
                             R=42, unpaid=unpaid)
        if test[1] < 1:
            low = middle
        else:
            high = middle - 1
    require(low == 29, "conditional screen's extra-center allowance changed")

    charge_histogram = Counter(item[0] for item in scored)
    charge_distribution = {str(charge): count
                           for charge, count in sorted(charge_histogram.items())}
    return {
        "status": "PASS_P111_SELECTED_PORT_PLANE_MATCHING",
        "scope": "Exact F2 dirty-map identity plus bounded rational copy-rank screen; no physical endpoint contract, supplier, or kappa claim.",
        "targets": PORTS,
        "dirty_input_columns": REGISTERS,
        "dirty_map_entries_checked": PORTS * REGISTERS,
        "dirty_map_sha256": original_digest,
        "binary_gram_rank": CHANNELS,
        "base_matching": {"pairs": [list(pair) for pair in base_pairs],
                           "residual_port": base_residual},
        "neighborhood": {"candidate_matchings": len(candidates),
                         "solvable_systems": solvable,
                         "price_histogram": charge_distribution},
        "minimum": {"scalar_copy_rank_charge": best_charge,
                    "ties": 2,
                    "next_charge": scored[2][0],
                    "term_count": best_terms_count,
                    "term_rank_histogram": {str(k): v for k, v in best_hist},
                    "plane_matrix_rank_histogram": {
                        str(k): v for k, v in sorted(active_matrix_ranks.items())},
                    "pairs": [list(pair) for pair in best_pairs],
                    "residual_port": best_residual,
                    "terms": [[left, right, price]
                              for left, right, price in best_terms]},
        "basis_change_rows": transform_rows,
        "full_dirty_map": "PASS",
        "mutations": {"missing_residual": "REJECTED",
                      "missing_scalar_plane_term": "REJECTED"},
        "conditional_screen": {
            "unpaid_input": str(unpaid),
            "meaning": "assumed average only; not a proved coverage law",
            "target_a": str(target_a),
            "relaxation_at_target_a_upper": str(candidate_relaxation[1]),
            "a_bracket": [str(a_bracket[0]), str(a_bracket[1])],
            "maximum_extra_center_units_at_target": low,
        },
    }


def main():
    report = audit()
    receipt = PACKAGE / "RESULT.json"
    if "--write" in __import__("sys").argv:
        receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(receipt.read_text()) == report,
                "RESULT.json differs from exact source-bound replay")
    minimum = report["minimum"]
    print(report["status"],
          "matchings=%d price=%d terms=%d dirty=%dx%d" % (
              report["neighborhood"]["candidate_matchings"],
              minimum["scalar_copy_rank_charge"], minimum["term_count"],
              report["targets"], report["dirty_input_columns"]))


if __name__ == "__main__":
    main()
