#!/usr/bin/env python3
"""Construct and exhaust the exact inverse of the actual multi-axis defect.

This supplies an algebraic correction, not a profitable native supplier.
It prices added recursive phase factors favorably and rejects that route.
The finite translation expansion is explicitly not a constant all-size tariff.
PR3220 supplies the retained additive allowance argument; PR3989 supplies the
related tensor-support warning. New literal multi-axis construction/gate uses
substantial OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import full_operator as F

HERE = Path(__file__).resolve().parent


def gsub(a, b):
    return a[0] - b[0], a[1] - b[1]


def gdiv(a, b):
    d = b[0] * b[0] + b[1] * b[1]
    return ((a[0] * b[0] + a[1] * b[1]) / d,
            (a[1] * b[0] - a[0] * b[1]) / d)


def rank(matrix):
    a = [[(Fraction(x), Fraction(y)) for x, y in row] for row in matrix]
    pivot = 0
    for column in range(8):
        chosen = next((i for i in range(pivot, 8) if a[i][column] != F.ZERO), None)
        if chosen is None:
            continue
        a[pivot], a[chosen] = a[chosen], a[pivot]
        factor = a[pivot][column]
        a[pivot] = [gdiv(x, factor) for x in a[pivot]]
        for row in range(pivot + 1, 8):
            factor = a[row][column]
            if factor != F.ZERO:
                a[row] = [gsub(x, F.gmul(factor, y)) for x, y in zip(a[row], a[pivot])]
        pivot += 1
    return pivot


def projector(record):
    prefix = record['prefix']
    inverse = F.identity()
    for event in reversed(record['history']):
        if event[0] != 'slot':
            F.scalar_action(inverse, event, inverse=True)
    F.require(F.matmul(prefix, inverse) == F.identity(), 'unimodular scalar prefix inverse')
    stream = record['stream']
    result = [[F.gmul(inverse[i][stream], prefix[stream][j]) for j in range(8)] for i in range(8)]
    F.require(rank(result) == 1 and F.matmul(result, result) == result, 'exact rank-one projector')
    return result


def factor(K, exponent):
    coefficient = gsub(F.UNITS[exponent % 4], F.ONE)
    return [[F.gadd(F.ONE if i == j else F.ZERO, F.gmul(coefficient, K[i][j]))
             for j in range(8)] for i in range(8)]


def physical(matrix, qphase):
    # R=D_initial N^-1 D_initial^-1; C_all commutes with every entry.
    out = deepcopy(matrix)
    for i in range(8):
        for j in range(8):
            exponent = qphase * (int(i % 2 == 0) - int(j % 2 == 0))
            out[i][j] = F.gmul(out[i][j], F.UNITS[exponent % 4])
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE / 'CORRECTION.json')
    args = parser.parse_args()
    F.authenticate()
    template, phases = F.read(F.TEMPLATE), F.read(F.PHASES)
    recipe = phases['recipes'][0]
    normal = F.normalize(template, recipe)
    moves = [(d, r, int(a)) for owner, port, d, r, a in F.read(F.MOVES)['moves'] if owner == port == 0]
    edits = F.phase_edits(moves)
    slots = [e[1] for e in normal['events'] if e[0] == 'slot' and e[1] in edits]
    projectors = {c: projector(normal['prefixes'][c]) for c in slots}
    axes = sorted({axis for _, _, axis in moves})
    states = F.tensor_phase_group(axes)
    ranks, wrong_inverse_failures, omitted_failures = Counter(), 0, Counter()
    for state in states:
        values = dict(zip(axes, state))
        original, inverse = F.normalized_replay(normal, edits, values, repair=True)
        delta = [[gsub(original[i][j], F.ONE if i == j else F.ZERO) for j in range(8)] for i in range(8)]
        ranks[rank(delta)] += 1
        corrected, wrong = F.identity(), F.identity()
        for child in reversed(slots):
            exponent = sum(sign * values[axis] for axis, sign in edits[child])
            corrected = F.matmul(factor(projectors[child], -exponent), corrected)
            wrong = F.matmul(factor(projectors[child], exponent), wrong)
        F.require(corrected == inverse, 'independent projector factorization of inverse')
        F.require(F.matmul(corrected, original) == F.identity(), 'arbitrary dirty correction')
        wrong_inverse_failures += F.matmul(wrong, original) != F.identity()
        for omitted in slots:
            partial = F.identity()
            for child in reversed(slots):
                if child != omitted:
                    exponent = sum(sign * values[axis] for axis, sign in edits[child])
                    partial = F.matmul(factor(projectors[child], -exponent), partial)
            omitted_failures[omitted] += F.matmul(partial, original) != F.identity()
    F.require(wrong_inverse_failures and all(omitted_failures.values()), 'meaningful correction controls')
    # A binary character already witnesses rank five, so the insertion lower
    # bound does not rely only on hypothetical higher tensor multiplicity.
    witness_character = (1 << 52) ^ (1 << 72)
    witness_values = {axis: (axis & witness_character).bit_count() % 2 for axis in axes}
    witness_operator = F.normalized_replay(normal, edits, witness_values)
    witness_delta = [[gsub(witness_operator[i][j], F.ONE if i == j else F.ZERO)
                      for j in range(8)] for i in range(8)]
    minor_indices = [1, 2, 3, 6, 7]
    minor = [[witness_delta[i][j] for j in minor_indices] for i in minor_indices]
    F.require(all(minor[i][j] == F.ZERO for i in range(5) for j in range(5) if i != j), 'diagonal rank-five minor')
    determinant = F.ONE
    for i in range(5):
        determinant = F.gmul(determinant, minor[i][i])
    F.require(determinant == (0, -8) and rank(witness_delta) == 5, 'exact rank-five counterexample')

    # Explicit finite binary matrix over translations X_v. This is a concrete
    # exact correction on the finite cube, while its all-size direct expansion
    # is not booked as constant tape overhead.
    all_axes = axes + [int(recipe['q'])]
    basis, coordinates = F.row_basis(all_axes)
    F.require(len(basis) == len(all_axes) == 6, 'literal independent six-form finite correction')
    table = []
    for assignment in range(1 << len(basis)):
        values = {axis: (assignment & coordinates[axis]).bit_count() % 2 for axis in axes}
        original, inverse = F.normalized_replay(normal, edits, values, repair=True)
        qphase = (assignment & coordinates[int(recipe['q'])]).bit_count() % 2
        R, E = physical(inverse, qphase), physical(original, qphase)
        F.require(F.matmul(R, E) == F.identity(), 'literal physical correction')
        table.append(R)
    coefficients = []
    for displacement in range(1 << len(basis)):
        matrix = [[F.ZERO for _ in range(8)] for _ in range(8)]
        for assignment, R in enumerate(table):
            sign = -1 if (assignment & displacement).bit_count() % 2 else 1
            for i in range(8):
                for j in range(8):
                    a, b = R[i][j]
                    matrix[i][j] = F.gadd(matrix[i][j], (sign * a, sign * b))
        vector = 0
        for bit, axis in enumerate(basis):
            if displacement >> bit & 1:
                vector ^= axis
        for i in range(8):
            for j in range(8):
                if matrix[i][j] != F.ZERO:
                    coefficients.append({'dst': i, 'src': j, 'translation': str(vector),
                                         'numerator': list(matrix[i][j]), 'denominator': len(table)})
    for assignment, expected in enumerate(table):
        observed = [[F.ZERO for _ in range(8)] for _ in range(8)]
        for record in coefficients:
            vector = int(record['translation'])
            _, coords = F.row_basis(basis + [vector])
            sign = -1 if (assignment & coords[vector]).bit_count() % 2 else 1
            value = tuple(sign * x for x in record['numerator'])
            i, j = record['dst'], record['src']
            observed[i][j] = F.gadd(observed[i][j], value)
        F.require(observed == [[(len(table) * a, len(table) * b) for a, b in row] for row in expected],
                  'independent inverse Walsh reconstruction')

    # Rank-one inverse phase children at distinct scalar slots can be grouped
    # into the five orthogonal coordinate phase factors [3,3,4,1,1]. Movement,
    # conjugating prefixes, q-gauge adapters and dirty restoration are granted
    # free in this favorable price. The comparison still loses decisively.
    repair_profile = Counter(len(edits[c]) for c in slots)
    F.require(repair_profile == {1: 2, 3: 2, 4: 1}, 'literal five-factor rank profile')
    a = Fraction(349, 200000)
    saving_upper = 20 * a * 51 * Fraction(3, 8)  # e>8/3 in PR3220 allowance.
    net_one_lower = 1 - saving_upper
    net_five_lower = 5 - saving_upper
    F.require(net_one_lower > 0 and net_five_lower > 0, 'strict exact favorable budget rejection')
    with localcontext() as ctx:
        ctx.prec = 60
        exponent = Decimal(1) - Decimal(a.numerator) / Decimal(a.denominator)
        repair_raw = sum(Decimal(count) * (exponent * Decimal(r).ln()).exp() for r, count in repair_profile.items())
    # A finite-only identity that would be admitted by the binary phase test
    # but fails under tensoring: (C-I)(C-iI)=0 has value 2+2i at C=-1.
    def polynomial(z):
        return F.gmul(gsub(z, F.ONE), gsub(z, (0, 1)))
    F.require(polynomial(F.ONE) == polynomial((0, 1)) == F.ZERO, 'finite-only positive control')
    F.require(polynomial((-1, 0)) == (2, 2), 'uniform tensor control rejects')

    controls = {}
    altered = deepcopy(recipe)
    altered['idle_children'][0]['translation_after'] = 0
    try:
        F.normalize(template, altered)
    except ValueError:
        controls['omit_actual_idle_translation'] = 'REJECTED'
    altered_template = deepcopy(template)
    altered_template['execution_schedule'] = [e for e in template['execution_schedule'] if e['kind'] != 'terminal_Y_translations']
    try:
        F.normalize(altered_template, recipe)
    except ValueError:
        controls['omit_terminal_Y_translation'] = 'REJECTED'
    try:
        F.tensor_phase_group([1, 2, 4], max_states=4)
    except ValueError:
        controls['incomplete_tensor_enumeration'] = 'REJECTED'
    F.require(len(controls) == 3, 'phase/global/state-cap controls')
    result = {
        'status': 'PASS_EXACT_CORRECTION_AND_SCOPED_UNPROFITABLE_REPAIR',
        'actual_moves': moves, 'owner': 0, 'port': 0,
        'normalized_correction_formula': 'E^-1=product in reverse chronological application order of [I+(i^(-delta_c)-1) M_c^-1 E_stream(c) M_c]',
        'physical_correction_formula': 'R=D_initial E^-1 D_initial^-1; R times moved_operator = C_all I_8',
        'ordered_affected_slots': slots,
        'exact_projectors': {str(c): projectors[c] for c in slots},
        'tensor_phase_states': len(states), 'defect_rank_distribution_over_Qi': dict(sorted(ranks.items())),
        'literal_binary_rank_five_witness': {'character': str(witness_character),
            'normalized_defect_matrix': witness_delta, 'minor_rows_and_columns': minor_indices,
            'minor_determinant': list(determinant), 'rank': 5,
            'consequence': 'At least five added completed single-stream Fourier-diagonal phase children are necessary at caller-level cuts in the retained character-block interface, even with free invertible8x8 prefix/suffix routing inside each character block. Each insertion changes a fixed-character operator by rank at most one; telescoping makes the total difference rank at most the number of insertions. Arbitrary adapters mixing different Fourier characters are outside this rank argument.'},
        'arbitrary_dirty_operator_correction_all_tensor_states': True,
        'wrong_inverse_nonidentity_states': wrong_inverse_failures,
        'omitted_factor_nonidentity_states': dict(sorted(omitted_failures.items())),
        'finite_physical_translation_terms': coefficients,
        'finite_physical_translation_nonzero_blocks': len(coefficients),
        'finite_physical_operator_characters_checked': len(table),
        'finite_translation_expansion_admitted_as_constant_tape_cost': False,
        'literal_recursive_correction_profile_lower_price': dict(sorted(repair_profile.items())),
        'literal_five_factor_raw_price_approximation_at_a_0_001745': str(repair_raw),
        'exact_price_scope': 'Original local/hosted profile, stock and residual rank mass retained; rank cap51; at most20 residual slots per group. Correction children are extra. Movement, conjugating scalar prefixes, q-gauge adapters and restoration are all granted free in this favorable rejection.',
        'maximum_residual_repacking_gain_strictly_below': str(saving_upper),
        'one_extra_child_net_raw_cost_strictly_above': str(net_one_lower),
        'five_extra_children_net_raw_cost_strictly_above': str(net_five_lower),
        'basis_of_price_proof': 'PR3220: sum(r^(1-a)-r*51^-a) <=20*a*51/e <20*a*51*3/8; any positive integer rank child costs >=1.',
        'finite_only_tensor_control': {'polynomial': '(C-I)(C-iI)', 'finite_eigenvalues': ['1','i'],
                                       'tensor_eigenvalue': '-1', 'nonzero_value': [2,2]},
        'additional_controls': controls,
        'new_supplier': False, 'new_kappa': False,
        'remaining_scope': ['Correction absorbed into existing paid children or a changed scalar/local graph',
                            'coordinate-dependent coupled native macro with a complete uniform tensor-volume bill',
                            'a changed bank/controller architecture that changes the retained mass/stock comparison'],
        'input_files': {str(p.relative_to(F.REPO)): F.sha(p) for p in [*F.PINS, Path(F.__file__), Path(__file__),
                       F.REPO / 'research/shared-phase-repair-rank/vendor/PR3220-PROOF.md',
                       HERE.parent / 'sources/initial-public/OPEN-PULLS-P1.json']},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], 'tensor_states', len(states), 'repair_profile', dict(repair_profile), 'translation_terms', len(coefficients))


if __name__ == '__main__':
    main()
