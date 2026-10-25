#!/usr/bin/env python3
"""Independent exact finite replay, using a second realization of E8.

This file does not import the primary verifier or its A8 realization.  It starts
with the 56 D8 root lines and 64 half-integral root lines in eight coordinates,
all multiplied by two.  It reconstructs the binary labels from their intrinsic
orthogonality table and checks every nonzero character and unordered pair.

``build_model()`` (also ``model()``) returns the doubled scalar roots, canonical
9-bit labels, and binary coordinate-transport data.  ``verify_all()`` (also
``run()``) returns a JSON-safe summary and writes nothing.  Running this file
prints PASS and that summary.  Only the Python standard library is required.

Full rank modulo 3 proves rank eight over Q, and hence over every characteristic
zero scalar field: the witnessing integer minor is nonzero.  A failed modular
rank is never used to prove deficiency.  In that case primitive integer row
elimination computes the exact rational rank.  No floating point or assertions
are used for correctness.

Model lineage: the E8 scalar alphabet and decoder setting in source PRs #1224
and #1248.  This is a separate AI implementation, not a human review.  Prepared
by conorholds under Apache-2.0; predecessor attribution belongs in SOURCES.json.
"""

from itertools import combinations, product
import json
from math import gcd


DIMENSION = 8
BINARY_DIMENSION = 9
OMEGA = (1 << BINARY_DIMENSION) - 1


class VerificationError(RuntimeError):
    """An exact finite identity or required control failed."""


def _require(condition, message):
    if not condition:
        raise VerificationError(message)


def _dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def _parity(value):
    return value.bit_count() & 1


def _even_q(value):
    _require(_parity(value) == 0, "quadratic form requires an even vector")
    return (value.bit_count() // 2) & 1


def _standard_roots():
    roots = []
    for first, second in combinations(range(DIMENSION), 2):
        for sign in (-1, 1):
            row = [0] * DIMENSION
            row[first], row[second] = 2, 2 * sign
            roots.append(tuple(row))
    for signs in range(1 << (DIMENSION - 1)):
        if _parity(signs) == 0:
            roots.append((1,) + tuple(
                -1 if signs & (1 << index) else 1
                for index in range(DIMENSION - 1)
            ))
    roots = tuple(roots)
    _require(len(roots) == len(set(roots)) == 120,
             "standard E8 construction did not give 120 distinct lines")
    _require(all(_dot(row, row) == 8 for row in roots),
             "standard E8 roots have incorrect squared length")
    _require(all(next(value for value in row if value) > 0 for row in roots),
             "root-line signs are not canonical")
    return roots


def _intrinsic_table(roots):
    """One on the diagonal or an orthogonal pair; zero otherwise."""
    table = []
    for index, row in enumerate(roots):
        bits = 0
        for other_index, other in enumerate(roots):
            product = _dot(row, other)
            _require(index == other_index or product in (-4, 0, 4),
                     "distinct E8 lines have an unexpected scalar product")
            if index == other_index or product == 0:
                bits |= 1 << other_index
        table.append(bits)
    return tuple(table)


def _independent_indices(rows):
    echelon = {}
    indices = []
    for index, initial in enumerate(rows):
        row = initial
        while row:
            pivot = row.bit_length() - 1
            if pivot in echelon:
                row ^= echelon[pivot]
            else:
                echelon[pivot] = row
                indices.append(index)
                break
    return tuple(indices)


def _binary_inverse(rows):
    size = len(rows)
    left_mask = (1 << size) - 1
    work = [row | (1 << (size + index)) for index, row in enumerate(rows)]
    for column in range(size):
        pivot = next((index for index in range(column, size)
                      if work[index] & (1 << column)), None)
        _require(pivot is not None, "binary Gram matrix is singular")
        work[column], work[pivot] = work[pivot], work[column]
        for index in range(size):
            if index != column and work[index] & (1 << column):
                work[index] ^= work[column]
    _require(all((row & left_mask) == 1 << index
                 for index, row in enumerate(work)),
             "binary inverse elimination failed")
    return tuple(row >> size for row in work)


def _binary_solve(equations, size):
    """Solve a required unique system, rejecting inconsistent extra rows."""
    work = [mask | (right << size) for mask, right in equations]
    pivot_row = 0
    for column in range(size):
        pivot = next((index for index in range(pivot_row, len(work))
                      if work[index] & (1 << column)), None)
        _require(pivot is not None, "binary normalization is not uniquely fixed")
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        for index in range(len(work)):
            if index != pivot_row and work[index] & (1 << column):
                work[index] ^= work[pivot_row]
        pivot_row += 1
    mask = (1 << size) - 1
    _require(all(row & mask or not row >> size for row in work),
             "binary normalization equations are inconsistent")
    solution = sum(((work[index] >> size) & 1) << index
                   for index in range(size))
    _require(all(_parity(mask & solution) == right
                 for mask, right in equations),
             "binary normalization solution failed substitution")
    return solution


def _check_incidence(roots, labels):
    _require(len(roots) == len(labels) == 120,
             "root and label counts disagree")
    for index, root in enumerate(roots):
        for other_index, other in enumerate(roots):
            geometric = int(index == other_index or _dot(root, other) == 0)
            _require(_parity(labels[index] & labels[other_index]) == geometric,
                     "binary labels disagree with scalar orthogonality")


def build_model():
    """Return independently constructed roots, labels, and exact transport data.

    A raw label records one root's table entries against nine independent root
    columns.  Its bilinear form is G inverse, not the identity.  The returned
    labels have been transported to the identity form, then normalized so that
    the entire root set is exactly the 9-bit vectors of weights three and seven.
    Thus ordinary bit parity is beta on both labels and normal characters.
    """
    roots = _standard_roots()
    table = _intrinsic_table(roots)
    indices = _independent_indices(table)
    _require(len(indices) == BINARY_DIMENSION,
             "intrinsic binary orthogonality table does not have rank nine")
    raw_labels = tuple(sum(((row >> selected) & 1) << column
                           for column, selected in enumerate(indices))
                       for row in table)
    gram = tuple(raw_labels[index] for index in indices)
    inverse = _binary_inverse(gram)
    matrix_times = tuple(sum(_parity(row & value) << index
                             for index, row in enumerate(inverse))
                         for value in range(OMEGA + 1))

    def pairing(left, right):
        return _parity(left & matrix_times[right])

    for index, left in enumerate(raw_labels):
        for other_index, right in enumerate(raw_labels):
            _require(pairing(left, right) == ((table[index] >> other_index) & 1),
                     "inverse Gram form does not reconstruct the intrinsic table")

    # Choose an orthonormal basis without leaving an alternating residual form.
    # In an odd nonalternating space the characteristic vector can be a bad first
    # choice; checking the residual form avoids that binary Gram-Schmidt trap.
    subspace = list(range(OMEGA + 1))
    orthonormal = []
    for remaining in range(BINARY_DIMENSION, 0, -1):
        selected = None
        residual = None
        for candidate in subspace:
            if not pairing(candidate, candidate):
                continue
            complement = [value for value in subspace
                          if not pairing(candidate, value)]
            if remaining == 1 or any(pairing(value, value) for value in complement):
                selected, residual = candidate, complement
                break
        _require(selected is not None, "binary orthonormal basis construction failed")
        orthonormal.append(selected)
        subspace = residual
    _require(subspace == [0], "binary orthonormal basis does not span")
    _require(all(pairing(left, right) == int(i == j)
                 for i, left in enumerate(orthonormal)
                 for j, right in enumerate(orthonormal)),
             "transport basis is not orthonormal")
    labels = tuple(sum(pairing(label, vector) << index
                       for index, vector in enumerate(orthonormal))
                   for label in raw_labels)
    _check_incidence(roots, labels)

    # On the even subspace, the intrinsic E8 root quadratic form can differ
    # from wt/2 by a linear form.  Solve for its even representative b.  Since
    # q(b)=0, x -> x + (x.b)b is an orthogonal transvection correcting that form.
    equations = [(label ^ OMEGA, 1 ^ _even_q(label ^ OMEGA)) for label in labels]
    equations.append((OMEGA, 0))
    correction = _binary_solve(equations, BINARY_DIMENSION)
    _require(_even_q(correction) == 0,
             "root quadratic refinement has the wrong isometry type")
    labels = tuple(label ^ correction if _parity(label & correction) else label
                   for label in labels)
    expected = {value for value in range(OMEGA + 1)
                if value.bit_count() in (3, 7)}
    _require(set(labels) == expected and len(set(labels)) == 120,
             "canonical root labels are not exactly the weight-three/seven vectors")
    _check_incidence(roots, labels)
    return {
        "roots": roots,
        "labels": labels,
        "pairing_rows": table,
        "basis_root_indices": indices,
        "gram_rows": gram,
        "gram_inverse_rows": inverse,
        "raw_labels": raw_labels,
        "orthonormal_basis": tuple(orthonormal),
        "quadratic_correction": correction,
        "scalar_coordinate_scale": 2,
    }


model = build_model


def _rank_mod_three(support, rows):
    """Rank in F3; eight is a characteristic-zero certificate, less is not."""
    basis = [None] * DIMENSION
    rank = 0
    while support:
        bit = support & -support
        support ^= bit
        row = list(rows[bit.bit_length() - 1])
        for column in range(DIMENSION):
            coefficient = row[column]
            if not coefficient:
                continue
            old = basis[column]
            if old is None:
                if coefficient == 2:
                    for index in range(column, DIMENSION):
                        row[index] = (2 * row[index]) % 3
                basis[column] = row
                rank += 1
                if rank == DIMENSION:
                    return rank
                break
            for index in range(column + 1, DIMENSION):
                row[index] = (row[index] - coefficient * old[index]) % 3
            row[column] = 0
    return rank


def _rank_rational(support, roots):
    """Exact row rank over Q by primitive integer echelon elimination."""
    basis = [None] * DIMENSION
    rank = 0
    while support:
        bit = support & -support
        support ^= bit
        row = list(roots[bit.bit_length() - 1])
        for column in range(DIMENSION):
            coefficient = row[column]
            if not coefficient:
                continue
            old = basis[column]
            if old is None:
                content = 0
                for value in row[column:]:
                    content = gcd(content, value)
                if coefficient < 0:
                    content = -content
                basis[column] = tuple(value // content for value in row)
                rank += 1
                if rank == DIMENSION:
                    return rank
                break
            pivot = old[column]
            for index in range(column + 1, DIMENSION):
                row[index] = pivot * row[index] - coefficient * old[index]
            row[column] = 0
    return rank


def _supports(labels):
    return tuple(sum(_parity(normal & label) << index
                     for index, label in enumerate(labels))
                 for normal in range(OMEGA + 1))


def _binary_support_rank(support, labels):
    basis = [0] * BINARY_DIMENSION
    rank = 0
    while support:
        bit = support & -support
        support ^= bit
        row = labels[bit.bit_length() - 1]
        while row:
            pivot = row.bit_length() - 1
            if basis[pivot]:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                rank += 1
                if rank == BINARY_DIMENSION:
                    return rank
                break
    return rank


def verify_sparse_cosets(data=None):
    """Exhaust four sparse outside cosets of the F3 scalar root code.

    Each of the 3**8 vectors h is used once to evaluate the full codeword Rh.
    The nonzero codewords must have support-label rank nine.  Each chosen lambda
    has support-label rank at most two, proving it is outside that code.  The
    histograms exhaust every lambda + Rh, with no random choices or sampling.
    """
    if data is None:
        data = build_model()
    roots, labels = data["roots"], data["labels"]
    first = 0
    orthogonal = next(index for index in range(1, len(roots))
                      if _dot(roots[first], roots[index]) == 0)
    nonorthogonal = next(index for index in range(1, len(roots))
                         if _dot(roots[first], roots[index]) != 0)
    sparse = {
        "singleton": ((first, 1),),
        "nonorthogonal_11": ((first, 1), (nonorthogonal, 1)),
        "nonorthogonal_12": ((first, 1), (nonorthogonal, 2)),
        "orthogonal_11": ((first, 1), (orthogonal, 1)),
    }
    families = {}
    for name, entries in sparse.items():
        rank = _binary_support_rank(sum(1 << index for index, _ in entries), labels)
        _require(rank == len(entries) < BINARY_DIMENSION,
                 "sparse lambda support has unexpected binary rank")
        families[name] = {"sparse_lambda": [list(entry) for entry in entries],
                          "lambda_support_rank": rank,
                          "deficiency_histogram": {}, "deficiency_sum": 0}
    rows = tuple(tuple(value % 3 for value in row) for row in roots)
    normalizations = 0
    nonzero_codewords = 0
    for coefficients in product(range(3), repeat=DIMENSION):
        evaluations = tuple(sum(a * b for a, b in zip(row, coefficients)) % 3
                            for row in rows)
        support = sum(1 << index for index, value in enumerate(evaluations) if value)
        if any(coefficients):
            _require(_binary_support_rank(support, labels) == BINARY_DIMENSION,
                     "a nonzero scalar codeword has deficient binary support")
            nonzero_codewords += 1
        else:
            _require(support == 0, "zero coefficients gave a nonzero codeword")
        for name, entries in sparse.items():
            shifted = support
            for index, value in entries:
                if bool(evaluations[index]) != bool((evaluations[index] + value) % 3):
                    shifted ^= 1 << index
            rank = _binary_support_rank(shifted, labels)
            _require(rank > 0, "a sparse outside coset contained zero")
            deficiency = BINARY_DIMENSION - rank
            family = families[name]
            histogram = family["deficiency_histogram"]
            key = str(deficiency)
            histogram[key] = histogram.get(key, 0) + 1
            family["deficiency_sum"] += deficiency
        normalizations += 1
    _require(normalizations == 6561 and nonzero_codewords == 6560,
             "scalar code or sparse-coset exhaustion was incomplete")
    for family in families.values():
        _require(sum(family["deficiency_histogram"].values()) == normalizations,
                 "sparse-coset deficiency histogram was incomplete")
        _require(family["deficiency_sum"] <= BINARY_DIMENSION,
                 "a sparse outside coset exceeded total deficiency nine")
        family["normalizations_checked"] = normalizations
    _require(families["singleton"]["deficiency_sum"] == BINARY_DIMENSION,
             "singleton outside coset did not attain deficiency nine")
    return {"field_order": 3, "code_dimension": DIMENSION,
            "codewords_checked": normalizations,
            "nonzero_codewords_with_support_rank_nine": nonzero_codewords,
            "families": families}


def _certified_rank(support, roots, rows_mod_three):
    """Return exact rational rank and whether a full-rank F3 witness sufficed."""
    modular = _rank_mod_three(support, rows_mod_three)
    if modular == DIMENSION:
        return modular, True
    exact = _rank_rational(support, roots)
    _require(exact >= modular, "rational rank was smaller than modular rank")
    return exact, False


def _controls(roots, labels, supports):
    # Two distinct odd orthogonal normals are genuinely compatible; a normal
    # and its omega-complement have disjoint odd supports.
    cases = (
        ("orthogonal_coordinate_normals", 1, 2, 7),
        ("complementary_normals", 1, OMEGA ^ 1, 0),
        ("nonorthogonal_normals", 1, 3, 8),
        ("orthogonal_even_same_quadratic", 3, 12, 8),
    )
    results = {}
    for name, left, right, expected in cases:
        rank = _rank_rational(supports[left] & supports[right], roots)
        _require(rank == expected, "geometric control failed: " + name)
        results[name] = rank
    _require(_rank_rational(0, roots) == 0, "empty rational rank control failed")
    _require(_rank_rational(1, roots) == 1, "one-line rational rank control failed")
    # A determinant divisible by three is nonzero over Q even though it
    # vanishes modulo three.  Exercise that essential fallback distinction.
    diagonal = tuple(tuple((3 if index == DIMENSION - 1 else 1)
                           if index == column else 0
                           for column in range(DIMENSION))
                     for index in range(DIMENSION))
    diagonal_mod_three = tuple(tuple(value % 3 for value in row)
                               for row in diagonal)
    diagonal_support = (1 << DIMENSION) - 1
    modular_rank = _rank_mod_three(diagonal_support, diagonal_mod_three)
    rational_rank = _rank_rational(diagonal_support, diagonal)
    dispatched_rank, modular_witness = _certified_rank(
        diagonal_support, diagonal, diagonal_mod_three)
    _require(modular_rank == 7 and rational_rank == 8,
             "modular rank drop was incorrectly treated as rational deficiency")
    _require(dispatched_rank == 8 and not modular_witness,
             "rank dispatcher did not use its rational fallback")
    results["modular_rank_drop"] = {
        "mod_three_rank": modular_rank,
        "rational_rank": rational_rank,
        "dispatched_rank": dispatched_rank,
        "used_rational_fallback": not modular_witness,
    }
    # Replacing one line by its orthogonal neighbour preserves its norm but
    # invalidates the fixed labels.  Require the geometric predicate to notice.
    wrong_roots = (roots[1],) + roots[1:]
    rejected = False
    try:
        _check_incidence(wrong_roots, labels)
    except VerificationError:
        rejected = True
    _require(rejected, "deliberate geometry/predicate mismatch was accepted")
    results["geometry_predicate_mismatch_rejected"] = True
    return results


def verify_all():
    """Exhaust the finite one-coset rank lemma with bounded, streaming storage."""
    data = build_model()
    roots, labels = data["roots"], data["labels"]
    supports = _supports(labels)
    rows_mod_three = tuple(tuple(value % 3 for value in row) for row in roots)
    controls = _controls(roots, labels, supports)
    single_histogram = {}
    pair_histogram = {}
    modular_full_rank = 0
    rational_fallbacks = 0

    def scalar_rank(support):
        nonlocal modular_full_rank, rational_fallbacks
        rank, modular_witness = _certified_rank(support, roots, rows_mod_three)
        if modular_witness:
            modular_full_rank += 1
        else:
            rational_fallbacks += 1
        return rank

    for normal in range(1, OMEGA + 1):
        rank = scalar_rank(supports[normal])
        single_histogram[str(rank)] = single_histogram.get(str(rank), 0) + 1
        _require(rank == DIMENSION, "a nonzero character failed to span E8")

    compatible_pairs = 0
    forbidden_pairs = 0
    for left in range(1, OMEGA + 1):
        left_even = not _parity(left)
        left_q = _even_q(left) if left_even else None
        for right in range(left + 1, OMEGA + 1):
            rank = scalar_rank(supports[left] & supports[right])
            pair_histogram[str(rank)] = pair_histogram.get(str(rank), 0) + 1
            forbidden = bool(_parity(left & right)) or (
                left_even and not _parity(right) and left_q == _even_q(right)
            )
            if forbidden:
                forbidden_pairs += 1
                _require(rank == DIMENSION,
                         "a deficient pair violated a required binary condition")
            if rank < DIMENSION:
                compatible_pairs += 1

    pair_count = OMEGA * (OMEGA - 1) // 2
    _require(sum(single_histogram.values()) == 511,
             "single-character exhaustion was incomplete")
    _require(sum(pair_histogram.values()) == pair_count == 130305,
             "unordered-pair exhaustion was incomplete")
    _require(modular_full_rank + rational_fallbacks == 511 + pair_count,
             "rank-certificate accounting failed")
    return {
        "status": "PASS",
        "implementation": "independent standard D8 plus half-root E8 realization",
        "scalar_dimension": DIMENSION,
        "binary_dimension": BINARY_DIMENSION,
        "root_lines": len(roots),
        "scalar_coordinate_scale": data["scalar_coordinate_scale"],
        "canonical_label_weight_counts": {"3": 84, "7": 36},
        "nonzero_characters": 511,
        "single_rank_histogram": single_histogram,
        "unordered_distinct_nonzero_pairs": pair_count,
        "pair_rank_histogram": pair_histogram,
        "compatible_pairs": compatible_pairs,
        "forbidden_pairs_proved_full_rank": forbidden_pairs,
        "rank_evaluations": {
            "mod_three_full_rank_witnesses": modular_full_rank,
            "exact_rational_fallbacks": rational_fallbacks,
        },
        "controls": controls,
        "sparse_cosets": verify_sparse_cosets(data),
    }


run = verify_all


if __name__ == "__main__":
    summary = verify_all()
    print("PASS_E8_ONE_COSET_DEFICIENCY_INDEPENDENT")
    print(json.dumps(summary, sort_keys=True))
