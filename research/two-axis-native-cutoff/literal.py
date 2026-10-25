"""Independent literal checks for the two-axis native cutoff.

Hiroki KUMAZAKI, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor implementation or package verifier is imported. Arithmetic is
integer Gaussian arithmetic, with explicit rational normalization. Points are
00,10,01,11, encoded by 0,1,2,3; phases are evaluated at the input.
"""
from collections import Counter
from fractions import Fraction
from itertools import permutations, product


ROOTS = ((1, 0), (0, 1), (-1, 0), (0, -1))
LIMITS = (8, 9, 6, 7)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parity(permutation):
    inversions = sum(permutation[i] > permutation[j]
                     for i in range(4) for j in range(i+1, 4))
    return -1 if inversions % 2 else 1


def affine_and_phase_tables():
    affine = []
    for first, second, offset in product(range(1, 4), range(1, 4), range(4)):
        if first == second:
            continue
        table = tuple((((first & x).bit_count() % 2)
                       | (((second & x).bit_count() % 2) << 1)) ^ offset
                      for x in range(4))
        need(len(set(table)) == 4, 'Invertible literal affine map')
        affine.append(table)
    need(len(affine) == len(set(affine)) == 24, 'Twenty-four distinct affine maps')
    need(set(affine) == set(permutations(range(4))), 'AGL(2,2) is the full S4')
    affine.sort()
    for left, right in product(affine, repeat=2):
        composed = tuple(left[right[x]] for x in range(4))
        need(composed in affine and parity(composed) == parity(left)*parity(right),
             'Literal permutation sign is multiplicative')

    phases = []
    for c, a1, a2, b in product(range(4), range(4), range(4), range(2)):
        table = tuple((c+a1*(x & 1)+a2*((x >> 1) & 1)
                       +2*b*(x & 1)*((x >> 1) & 1)) % 4 for x in range(4))
        phases.append(((c, a1, a2, b), table))
    phase_functions = {table for _, table in phases}
    need(len(phases) == len(phase_functions) == 128, 'All phase recipes are distinct')
    for permutation, (_, table) in product(affine, phases):
        need(tuple(table[permutation[x]] for x in range(4)) in phase_functions,
             'Affine pullback preserves the literal phase family')
    return affine, phases


def fourier_numerator(points, residue, phases, *, omit_quadratic=False,
                      tensor_power_coefficients=False):
    """Sum all 128 terms of E_(residue,0,0,0), before normalization.

    U(h,q)=[h][d_q], so the phase acts on the original tuple, before h.
    The correct external Fourier coefficient i^(-residue*c)/128 occurs once.
    The tensor-power control intentionally raises that coefficient to |points|.
    """
    real, imaginary = 0, 0
    coefficient_power = len(points) if tensor_power_coefficients else 1
    for (c, a1, a2, _), table in phases:
        if omit_quadratic:
            phase = sum(c+a1*(x & 1)+a2*((x >> 1) & 1) for x in points)
        else:
            phase = sum(table[x] for x in points)
        value = ROOTS[(phase-coefficient_power*residue*c) % 4]
        real += value[0]
        imaginary += value[1]
    return real, imaginary


def projector(points, residue, phases, *, omit_quadratic=False):
    numerator = fourier_numerator(points, residue, phases,
                                  omit_quadratic=omit_quadratic)
    need(numerator in ((0, 0), (128, 0)), 'Normalized Fourier projector is zero or one')
    return numerator[0] // 128


def antisymmetrize(points, affine, *, omit_sign=False):
    output = Counter()
    for permutation in affine:
        destination = tuple(permutation[x] for x in points)
        output[destination] += 1 if omit_sign else parity(permutation)
    return {key: value for key, value in output.items() if value}


def evaluate(points, residue, affine, phases, *, omit_quadratic=False):
    # This order is the literal product (sum sign(h)[h]) E_chi.
    weight = projector(points, residue, phases, omit_quadratic=omit_quadratic)
    if not weight:
        return {}
    return {key: weight*value for key, value in antisymmetrize(points, affine).items()}


def compositions(total):
    for c0 in range(total+1):
        for c1 in range(total-c0+1):
            for c2 in range(total-c0-c1+1):
                yield c0, c1, c2, total-c0-c1-c2


def tuple_of_counts(counts):
    return tuple(point for point, count in enumerate(counts) for _ in range(count))


def stabilizer_checks(affine):
    reports = []
    identity = (0, 1, 2, 3)
    for mask in range(1, 16):
        subset = tuple(x for x in range(4) if (mask >> x) & 1)
        stabilizer = [p for p in affine if all(p[x] == x for x in subset)]
        odd = [p for p in stabilizer if parity(p) == -1]
        if len(subset) <= 2:
            need(odd and sum(parity(p) for p in stabilizer) == 0,
                 'Every small-support pointwise stabilizer contains odd cancellation')
            need(not antisymmetrize(subset, affine), 'All small-support coset sums vanish')
        else:
            need(stabilizer == [identity], 'Three distinct points have trivial stabilizer')
            need(len(antisymmetrize(subset, affine)) == 24,
                 'Full-span tuples have twenty-four distinct images')
        reports.append({'points': list(subset), 'stabilizer_size': len(stabilizer),
                        'odd_stabilizer_elements': len(odd)})
    return reports


def run():
    affine, phases = affine_and_phase_tables()
    stabilizers = stabilizer_checks(affine)

    # Enumerate actual ordered tuples, not only count classes, at every
    # positive same-residue width below the alleged first nonzero width.
    below = []
    for residue, limit in enumerate(LIMITS):
        cases, widths = 0, []
        for width in range(1, limit):
            if width % 4 != residue:
                continue
            widths.append(width)
            for points in product(range(4), repeat=width):
                need(not evaluate(points, residue, affine, phases),
                     'Literal residual vanishes on every below-threshold tuple')
                cases += 1
        below.append({'residue': residue, 'first_nonzero_width': limit,
                      'enumerated_widths': widths, 'ordered_tuple_cases': cases})
    need(sum(row['ordered_tuple_cases'] for row in below) == 1364,
         'Complete declared ordered-tuple census')

    # Direct 128-term sums on all weak compositions corroborate the central
    # selection rule and all positive widths through nine. Tuple ordering
    # cannot change a sum of input phases. The all-width central-residue
    # statement is the elementary sum over c, not an inference from this bound.
    composition_cases, wrong_residue_cases = 0, 0
    accepted_by_width = {}
    for width in range(1, 10):
        accepted = [0]*4
        for counts in compositions(width):
            points = tuple_of_counts(counts)
            for residue in range(4):
                value = projector(points, residue, phases)
                composition_cases += 1
                if width % 4 != residue:
                    need(value == 0, 'All other central residues vanish')
                    wrong_residue_cases += 1
                accepted[residue] += value
        accepted_by_width[str(width)] = accepted
    need(composition_cases == 2856 and wrong_residue_cases == 2142,
         'All positive weak compositions through nine, in all four residues')

    witnesses = []
    for residue, width in enumerate(LIMITS):
        candidates = []
        for counts in compositions(width):
            if sum(count > 0 for count in counts) < 3:
                continue
            points = tuple_of_counts(counts)
            if projector(points, residue, phases):
                candidates.append((counts, points))
        need(candidates, 'A literal full-span first witness exists')
        counts, points = candidates[0]
        result = evaluate(points, residue, affine, phases)
        need(len(result) == 24 and result.get(points) == 1
             and set(result.values()) == {-1, 1},
             'First witness has diagonal entry one and twenty-four distinct signed outputs')
        witnesses.append({'residue': residue, 'width': width, 'counts': list(counts),
                          'input_tuple': list(points), 'diagonal_entry': '1',
                          'distinct_output_tuples': len(result),
                          'positive_output_coefficients': sum(v == 1 for v in result.values()),
                          'negative_output_coefficients': sum(v == -1 for v in result.values())})
    need(witnesses[1]['counts'] == [1, 0, 4, 4], 'Declared width-nine witness binding')

    no_sign = []
    for residue, limit in enumerate(LIMITS):
        width = residue or 4
        points = (0,)*width
        need(width < limit and projector(points, residue, phases) == 1,
             'Sign-removal control has an admitted phase below the cutoff')
        correct = evaluate(points, residue, affine, phases)
        wrong = antisymmetrize(points, affine, omit_sign=True)
        need(not correct and len(wrong) == 4 and set(wrong.values()) == {6},
             'Omitting permutation signs destroys the below-cutoff identity')
        no_sign.append({'residue': residue, 'width': width,
                        'wrong_output_count': 4, 'wrong_coefficients': '6'})

    quadratic_points = tuple_of_counts((0, 3, 3, 1))
    need(projector(quadratic_points, 3, phases) == 0
         and projector(quadratic_points, 3, phases, omit_quadratic=True) == 1
         and len(evaluate(quadratic_points, 3, affine, phases, omit_quadratic=True)) == 24,
         'Omitting the quadratic phase wrongly accepts an odd pair count')

    scalar_points = tuple_of_counts((0, 2, 2, 2))
    correct = fourier_numerator(scalar_points, 1, phases)
    wrong = fourier_numerator(scalar_points, 1, phases, tensor_power_coefficients=True)
    need(correct == (0, 0) and wrong == (128, 0)
         and len(antisymmetrize(scalar_points, affine)) == 24,
         'Tensoring an external Fourier coefficient creates a false residue witness')
    wrong_normalized = Fraction(wrong[0], 128**len(scalar_points))

    return {
        'method': 'literal affine permutations, all128 input-phase Fourier terms, signed tuple images',
        'arithmetic': 'integer Gaussian pairs and exact rational normalization; no floating point',
        'affine_maps': len(affine), 'phase_polynomials': len(phases),
        'native_group_elements': len(affine)*len(phases),
        'affine_composition_sign_checks': len(affine)**2,
        'phase_pullback_checks': len(affine)*len(phases),
        'projector_normalization': '1/128',
        'coefficient_order': '(sum_h sign(h)[h]) E_chi; input phases act first',
        'stabilizers': stabilizers, 'below_threshold_census': below,
        'weak_composition_phase_checks': composition_cases,
        'wrong_central_residue_checks': wrong_residue_cases,
        'accepted_compositions_by_width_and_residue': accepted_by_width,
        'first_witnesses': witnesses,
        'controls': {
            'omitted_sign': no_sign,
            'omitted_quadratic': {'residue': 3, 'counts': [0, 3, 3, 1],
                                  'correct_projector': '0', 'wrong_projector': '1',
                                  'wrong_output_count': 24},
            'tensor_powered_external_coefficients': {
                'residue': 1, 'counts': [0, 2, 2, 2], 'correct_projector': '0',
                'wrong_projector': str(wrong_normalized), 'wrong_output_count': 24}},
        'scope': 'Independent finite evidence for the written two-axis theorem; no physical supplier or all-n cutoff',
    }


if __name__ == '__main__':
    import json
    print(json.dumps(run(), sort_keys=True, indent=2))
