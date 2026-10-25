"""Bounded exact validation of a proposed nonadapted actual d3 fixture.

Research by conorholds with OpenAI Codex assistance. Apache-2.0.
Retains the E8/P112 source credits described in frame_pair_geometry.py.
The exact replay and limits are recorded in VERIFY.md.

Default mode checks dimensions, actual supports, actual dual expansions and
corrections. --certify-low additionally covers every binary rank-seven flat,
proving that the exhibited low space is the span of ALL low S-words.
The fixture is a positive control outside the raw 72/73 budget, not a
counterexample and not a sharpness assertion.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from types import ModuleType


# Python's isolated mode deliberately omits the script's directory from its
# import path. Load this one exact sibling by bytes, without relying on sys.path
# or creating/importing a cached bytecode file.
_geometry_path = Path(__file__).resolve().with_name("frame_pair_geometry.py")
_geometry = ModuleType("d3_actual_fixture_independent_geometry")
_geometry.__file__ = str(_geometry_path)
exec(compile(_geometry_path.read_bytes(), str(_geometry_path), "exec"), _geometry.__dict__)
binary_rank = _geometry.binary_rank
binary_span = _geometry.binary_span
inverse = _geometry.inverse
model = _geometry.model
require = _geometry.require


def rational_rank(rows, width=None):
    rows = [list(map(Fraction, row)) for row in rows]
    if not rows:
        return 0
    width = len(rows[0]) if width is None else width
    require(all(len(row) == width for row in rows), "rational rank matrix shape")
    pivots = {}
    for row in rows:
        for column in range(width):
            if not row[column]:
                continue
            if column in pivots:
                factor = row[column]
                row = [x - factor * y for x, y in zip(row, pivots[column])]
            else:
                scale = row[column]
                pivots[column] = [x / scale for x in row]
                break
        if len(pivots) == width:
            break
    return len(pivots)


def rank_mod(rows, width, prime=5):
    pivots = {}
    for original in rows:
        row = [value % prime for value in original]
        require(len(row) == width, "modular rank matrix shape")
        for column in range(width):
            if not row[column]:
                continue
            if column in pivots:
                factor = row[column]
                row = [(x - factor * y) % prime for x, y in zip(row, pivots[column])]
            else:
                scale = pow(row[column], -1, prime)
                pivots[column] = [(scale * x) % prime for x in row]
                break
        if len(pivots) == width:
            break
    return len(pivots)


def rational_nullspace(rows, width):
    rows = [list(map(Fraction, row)) for row in rows]
    require(all(len(row) == width for row in rows), "nullspace matrix shape")
    pivot_columns = []
    used = 0
    for column in range(width):
        pivot = next((i for i in range(used, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[used], rows[pivot] = rows[pivot], rows[used]
        scale = rows[used][column]
        rows[used] = [x / scale for x in rows[used]]
        for i in range(len(rows)):
            if i != used and rows[i][column]:
                factor = rows[i][column]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[used])]
        pivot_columns.append(column)
        used += 1
        if used == len(rows):
            break
    result = []
    for free in range(width):
        if free in pivot_columns:
            continue
        vector = [Fraction(0)] * width
        vector[free] = Fraction(1)
        for i, pivot in enumerate(pivot_columns):
            vector[pivot] = -rows[i][free]
        require(all(not sum(x * y for x, y in zip(original, vector)) for original in rows),
                "nullspace basis verification")
        result.append(vector)
    return result


def independent_columns(rows):
    selected = []
    columns = list(zip(*rows))
    for i, column in enumerate(columns):
        if rational_rank([columns[j] for j in selected] + [column]) > len(selected):
            selected.append(i)
            if len(selected) == len(rows):
                break
    require(len(selected) == len(rows), "actual basis is dependent")
    return selected


def restricted_duals(basis, code):
    sites = independent_columns(basis)
    evaluation = [[row[i] for i in sites] for row in basis]
    evaluation_inverse = inverse(evaluation)
    by_axis = []
    for target in code:
        values = [target[i] for i in sites]
        coefficients = [sum(values[k] * evaluation_inverse[k][j] for k in range(len(basis)))
                        for j in range(len(basis))]
        require(all(sum(c * row[i] for c, row in zip(coefficients, basis)) == value
                    for i, value in enumerate(target)), "actual restricted-dual expansion fails")
        by_axis.append(coefficients)
    duals = list(map(tuple, zip(*by_axis)))
    require(all(any(row) for row in duals), "an actual restricted dual vanishes")
    return duals


def annihilator_planes():
    """All rank-two RREF ordinary-dot annihilators in nine label bits."""
    for p, q in combinations(range(9), 2):
        free_a = [j for j in range(p + 1, 9) if j != q]
        free_b = list(range(q + 1, 9))
        for bits_a in range(1 << len(free_a)):
            a = (1 << p) | sum(((bits_a >> k) & 1) << j for k, j in enumerate(free_a))
            for bits_b in range(1 << len(free_b)):
                b = (1 << q) | sum(((bits_b >> k) & 1) << j for k, j in enumerate(free_b))
                yield a, b


def low_space_certificate(low, quotient, live_labels, max_exact_flats):
    """Prove ker(E_outside_H) lies in the low-coordinate subspace for every H.

    Full modular rank of the eleven-column evaluation matrix is already an
    integer-minor certificate over every characteristic-zero field. When it
    is not full, compute the rank of the six low columns exactly and require
    rank(E)>=rank(E_low)+5. The opposite inequality is automatic. This avoids
    the invalid inference from a modular rank DIFFERENCE alone, where the
    low-column rank might also rise over the rationals.
    """
    rows = low + quotient
    low_dimension, quotient_dimension = len(low), len(quotient)
    width = len(rows)
    evaluations = list(zip(*rows))
    counts = Counter()
    fingerprints = sha256()
    first_failure = None
    for a, b in annihilator_planes():
        counts["all_rank7_flats"] += 1
        # A rank-seven label flat contained in t=0 has no live labels and
        # admits only the zero S-word because the exhibited S-basis is
        # independent. The other flats have affine-six leading-one sections.
        if 1 in (a, b, a ^ b):
            counts["empty_leading_one_sections"] += 1
            continue
        outside = [i for i, label in enumerate(live_labels)
                   if ((a & label).bit_count() % 2) or ((b & label).bit_count() % 2)]
        evaluation = [evaluations[i] for i in outside]
        full_mod_rank = rank_mod(evaluation, width)
        counts["affine_six_sections"] += 1
        if full_mod_rank == width:
            counts["full_modular_minors"] += 1
            fingerprints.update(f"{a},{b},full;".encode())
            continue
        counts["exact_low_reductions"] += 1
        require(counts["exact_low_reductions"] <= max_exact_flats,
                "exact-flat budget exhausted; no complete low-space certificate")
        low_rank = rational_rank([row[:low_dimension] for row in evaluation], low_dimension)
        needed = low_rank + quotient_dimension
        require(needed <= width, "low/quotient dimension bookkeeping")
        if full_mod_rank >= needed:
            counts["quotient_modular_minors"] += 1
            full_rank = needed
        else:
            counts["exact_full_reductions"] += 1
            full_rank = rational_rank(evaluation, width)
        fingerprints.update(f"{a},{b},{low_rank},{full_rank};".encode())
        if full_rank != needed:
            coefficient = next((vector for vector in rational_nullspace(evaluation, width)
                                if any(vector[low_dimension:])), None)
            require(coefficient is not None, "rank defect did not yield a quotient kernel")
            word = [sum(c * row[i] for c, row in zip(coefficient, rows))
                    for i in range(len(live_labels))]
            witness_support = [i for i, value in enumerate(word) if value]
            witness_weight = binary_rank(live_labels[i] for i in witness_support)
            require(witness_support and witness_weight <= 7, "quotient kernel is not a low word")
            first_failure = {"annihilator": [a, b], "outside_sites": outside,
                             "low_rank": low_rank, "full_rank": full_rank,
                             "required_full_rank": needed,
                             "witness_coefficients_in_low_plus_quotient_basis":
                                 [str(x) for x in coefficient],
                             "witness_support_positions": witness_support,
                             "witness_binary_support_rank": witness_weight}
            break
    if first_failure is not None:
        return {"status": "failure", "counterexample_flat": first_failure,
                "counts": dict(sorted(counts.items()))}
    require(counts["all_rank7_flats"] == 43435, "incomplete rank-seven flat enumeration")
    require(counts["empty_leading_one_sections"] == 255
            and counts["affine_six_sections"] == 43180, "incomplete affine-six flat domain")
    return {"status": "pass", "counts": dict(sorted(counts.items())),
            "certificate_digest": fingerprints.hexdigest(),
            "characteristic_zero_transfer": "nonzero integer minors and exact rational ranks"}


def actual_decoder(basis, duals, code, live_ids, pairings):
    """An exact singleton-pivot consumer fixture, with its actual binary cost.

    The doubled roots have squared norm8, and code_i=<f_i,r>/4. Therefore
    N0(s,t)=<r_s,r_t>/8=(1/4) sum_i code_i(s)code_i(t).
    Add distinct multiples of delta_v to the projected rows and cancel
    them with one explicit pivot column. This preserves the actual nonpivot
    basis and hence the same true T certificate.
    """
    size = len(live_ids)
    pivot = [Fraction(i == 0) for i in range(size)]
    projected = [[sum(dual[i] * code[i][s] for i in range(8)) / 4
                  for s in range(size)] for dual in duals]
    omega = list(range(1, len(basis) + 1))
    rows = [[value + coefficient * unit for value, unit in zip(row, pivot)]
            for row, coefficient in zip(projected, omega)] + [pivot]
    pivot_column = [-sum(coefficient * row[s] for coefficient, row in zip(omega, basis))
                    for s in range(size)]
    columns = basis + [pivot_column]
    require(len(rows) == len(columns) == 12, "consumer term count")
    require(rational_rank(rows) == 9 and rational_rank(columns) == 11,
            "consumer actual ranks differ from (9,11)")
    require(all(any(row) for row in rows), "consumer has a zero actual row")
    require(all(rational_rank([a, b]) == 2 for a, b in combinations(rows, 2)),
            "consumer actual rows are proportional")

    def first_mismatch(selected_rows, selected_columns):
        for s in range(size):
            for t in range(size):
                actual = sum(row[s] * column[t]
                             for row, column in zip(selected_rows, selected_columns))
                expected = Fraction(pairings[live_ids[s]][live_ids[t]], 8)
                if actual != expected:
                    return [s, t, str(actual), str(expected)]
        return None

    require(first_mismatch(rows, columns) is None, "consumer exact Gram identity failed")
    wrong_sign = columns[:-1] + [[-value for value in pivot_column]]
    wrong_sign_witness = first_mismatch(rows, wrong_sign)
    omitted_term_witness = first_mismatch(rows[1:], columns[1:])
    require(wrong_sign_witness is not None, "wrong consumer pivot sign was not detected")
    require(omitted_term_witness is not None, "omitted consumer term was not detected")

    def term_cost(row, column):
        support_r = [live_ids[i] for i, value in enumerate(row) if value]
        support_c = [live_ids[i] for i, value in enumerate(column) if value]
        # beta(ell_s,ell_t)=1+B(s,t); its matrix rank on all generating
        # support labels equals its rank on the two support spans.
        binary_rows = [sum(((1 + pairings[s][t] // 4) % 2) << j
                           for j, t in enumerate(support_c)) for s in support_r]
        return binary_rank(binary_rows)

    costs = [term_cost(row, column) for row, column in zip(rows, columns)]
    total_cost = sum(costs)
    require(total_cost == 84, "actual consumer positive fixture cost differs from 84")
    return {"status": "pass", "terms": 12, "actual_ranks": [9, 11],
            "actual_rows_nonzero_pairwise_nonparallel": True,
            "singleton_pivot_live_site_position": 0,
            "same_nonpivot_actual_basis": True, "binary_term_costs": costs,
            "binary_cost": total_cost,
            "wrong_pivot_sign_counterexample": wrong_sign_witness,
            "omitted_term_counterexample": omitted_term_witness,
            "scope": "positive consumer fixture outside raw budget; no sharpness claim"}


def fixture(source_geometry, certify_low, max_exact_flats, check_omitted_low=False):
    roots, frame, frame_ids, live_ids, labels, pairings = model(source_geometry)
    live_labels = [labels[i] for i in live_ids]
    code = [[pairings[axis][site] // 4 for site in live_ids] for axis in frame_ids]
    require(rational_rank(code) == 8, "root code dimension")
    patterns = [tuple(int(code[axis][i] != 0) for axis in range(3)) for i in range(112)]
    declarations = ((1, {(1, 1, 1), (1, 1, 0)}),
                    (0, {(1, 1, 1), (1, 0, 1)}),
                    (2, {(1, 1, 1), (0, 1, 1)}),
                    (0, {(1, 1, 0), (1, 0, 0)}),
                    (2, {(1, 0, 1), (0, 0, 1)}),
                    (1, {(0, 1, 1), (0, 1, 0)}))
    low = [[code[axis][i] if pattern in allowed else 0 for i, pattern in enumerate(patterns)]
           for axis, allowed in declarations]
    require(all(code[0][i] == low[1][i] + low[3][i]
                and code[1][i] == low[0][i] + low[5][i]
                and code[2][i] == low[2][i] + low[4][i] for i in range(112)),
            "three frame-word decompositions")
    require(rational_rank(low) == 6, "six proposed low generators are dependent")
    require(rational_rank(code + low) == 11, "S dimension is not eleven")
    canonical_basis = low + code[3:]
    require(rational_rank(canonical_basis) == 11, "canonical S-basis")
    high_mix = [x + y for x, y in zip(low[5], code[3])]
    actual_basis = low[:5] + [high_mix] + code[3:]
    require(len(actual_basis) == 11 and rational_rank(actual_basis) == 11, "actual F is not a basis")

    def weight(row):
        return binary_rank(label for label, value in zip(live_labels, row) if value)

    low_weights = [weight(row) for row in low]
    require(all(1 <= value <= 7 for value in low_weights), "a proposed low generator is not low")
    actual_weights = [weight(row) for row in actual_basis]
    duals = restricted_duals(actual_basis, code)
    corrected = []
    for j, (dual, row) in enumerate(zip(duals, actual_basis)):
        active_axes = [i for i, value in enumerate(dual) if value]
        if len(active_axes) == 1:
            axis = active_axes[0]
            support_span = binary_span(label for label, value in zip(live_labels, row) if value)
            if labels[frame_ids[axis]] in support_span:
                corrected.append({"actual_index": j, "frame_axis": axis,
                                  "weight": actual_weights[j]})
    inside = [j for j, row in enumerate(actual_basis) if rational_rank(low + [row]) == 6]
    require(inside == list(range(5)), "actual F has unexpected membership in proposed T")
    output = {"status": "shape-pass", "scope": "nonempty actual d3 fixture; outside raw budget",
              "source_geometry_sha256": sha256(source_geometry.read_bytes()).hexdigest(),
              "dimension_S": 11, "proposed_dimension_T": 6,
              "proposed_code_intersection_dimension": 3,
              "low_weights": low_weights, "actual_weights": actual_weights,
              "actual_inside_proposed_T": inside, "proposed_r": 1,
              "all_restricted_duals_nonzero": True,
              "actual_duals_in_frame_code_coordinates": [[str(x) for x in row] for row in duals],
              "corrected": corrected, "raw_weight_sum": sum(actual_weights),
              "invoice": sum(actual_weights) - len(corrected),
              "true_T_certified": False}
    require(sum(actual_weights) > 73, "positive-control fixture unexpectedly enters raw budget")
    output["singleton_pivot_consumer"] = actual_decoder(actual_basis, duals, code,
                                                       live_ids, pairings)
    if certify_low:
        certificate = low_space_certificate(low, code[3:], live_labels, max_exact_flats)
        output["low_space_certificate"] = certificate
        if certificate["status"] == "pass":
            output["status"] = "pass"
            output["true_T_certified"] = True
            output["dimension_T"] = 6
            output["code_intersection_dimension"] = 3
            output["r"] = 1
        else:
            output["status"] = "low-space-failure"
        if check_omitted_low:
            # Keep the SAME eleven-dimensional S, but falsely declare only
            # five of the six low generators to span its full low space.
            # A real low word outside that declared space must be recovered.
            rejected = low_space_certificate(low[:5], [low[5]] + code[3:],
                                             live_labels, max_exact_flats)
            require(rejected["status"] == "failure",
                    "omitted genuine low generator was not detected")
            output["omitted_low_control"] = rejected
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-geometry", required=True, type=Path)
    parser.add_argument("--certify-low", action="store_true")
    parser.add_argument("--max-exact-flats", type=int, default=4096)
    args = parser.parse_args()
    require(args.max_exact_flats >= 0, "negative exact-flat budget")
    result = fixture(args.source_geometry, args.certify_low, args.max_exact_flats)
    print(json.dumps(result, sort_keys=True, indent=2))
    if result["status"] == "low-space-failure":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
