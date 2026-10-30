"""Independent exact certificate checks and scientific-boundary controls.

Prepared by Jonathan Capalbo (jon314159), with substantial OpenAI Codex
assistance. Apache-2.0. This is a second AI/code review, not a human review or
a formal proof. It does not recompute the carrier reachability enclosure.
"""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import permutations


def require(condition, message):
    if not condition:
        raise ValueError(message)


def determinant(matrix):
    """Direct permutation definition; no package elimination is imported."""
    size = len(matrix)
    require(size <= 7 and all(len(row) == size for row in matrix), 'Small square review minor')
    answer = Q(0)
    for order in permutations(range(size)):
        inversions = sum(order[i] > order[j] for i in range(size) for j in range(i + 1, size))
        term = Q(-1 if inversions % 2 else 1)
        for i, j in enumerate(order):
            term *= matrix[i][j]
        answer += term
    return answer


def independent_rows(rows):
    """Choose a row minor using dense elimination in the small column space."""
    echelon, selected = {}, []
    for label, original in rows:
        row = list(original)
        for pivot in sorted(echelon):
            coefficient = row[pivot]
            row = [x - coefficient * y for x, y in zip(row, echelon[pivot])]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            divisor = row[pivot]
            echelon[pivot] = [x / divisor for x in row]
            selected.append(label)
    return selected


def suffix_column(word, cut, pivot):
    """Independent dense scalar propagation of the uncorrected unit signal."""
    public = word['public']
    column = [Q(0)] * (public + word['owned_fields'])
    require(-1 <= cut < len(word['program']) and 0 <= pivot < public, 'Review injection bounds')
    column[pivot] = Q(1)
    for event in word['program'][cut + 1:]:
        operation, target = event[:2]
        if operation in ('INIT', 'CLEAR'):
            column[target] = Q(0)
        elif operation == 'COPY':
            column[target] = Q(event[3]) * column[event[2]]
        elif operation == 'ADD':
            column[target] += Q(event[3]) * column[event[2]]
        elif operation == 'SCALE':
            column[target] *= Q(event[2])
        else:
            require(operation == 'MOVE', 'Review suffix opcode')
    require(not any(column[public:]), 'Review terminal owned signal')
    return column[:public]


def affine_certificate(word, result):
    """Certify injective protected projection and membership of the offset."""
    case = result['case']
    basis = [{int(k): Q(v) for k, v in row.items()} for row in result['final_basis']]
    public, dimension = word['public'], len(basis)
    require(0 < dimension <= 7, 'Review terminal dimension')
    require(all(0 <= k < public for row in basis for k in row), 'Review basis public coordinates')
    protected = [r for r in range(public) if word['final'][r] != word['final'][case['pivot']]]
    selected = independent_rows((r, [row.get(r, Q(0)) for row in basis]) for r in protected)
    require(len(selected) == dimension, 'Review protected projection is not injective')
    matrix = [[row.get(r, Q(0)) for row in basis] for r in selected]
    divisor = determinant(matrix)
    require(bool(divisor), 'Review protected determinant is zero')
    offset = suffix_column(word, case['cut_after'], case['pivot'])
    # Cramer's rule deliberately differs from the carrier module's solve_square.
    coefficients = []
    for column in range(dimension):
        substituted = [[offset[r] if j == column else matrix[i][j]
                        for j in range(dimension)] for i, r in enumerate(selected)]
        coefficients.append(determinant(substituted) / divisor)
    for r in range(public):
        reconstructed = sum(q * row.get(r, Q(0)) for q, row in zip(coefficients, basis))
        require(reconstructed == offset[r], 'Review affine offset is not in correction span')
    return {'cut_after': case['cut_after'], 'pivot': case['pivot'],
            'protected_rows': selected, 'determinant': str(divisor),
            'baseline_coefficients': [str(q) for q in coefficients],
            'checked_public_coordinates': public,
            'projection_injective': True, 'baseline_in_span': True,
            'conclusion': 'The only protected-zero point of this reported affine set is zero.'}


def independent_terminal(word, carrier_result):
    dynamic = carrier_result['dynamic_screen']
    require(dynamic['tested'] == len(dynamic['results']) == 2, 'Review two terminal cases')
    checks = []
    for result in dynamic['results']:
        require(result['outcome'] == 'only_zero_signal', 'Review terminal outcome')
        require(result['final_correction_rank'] == result['protected_projection_rank'] == 5,
                'Review reported terminal ranks')
        require(result['zero_protected_dimension'] == 0 and not result['affine_remainder'],
                'Review reported affine conclusion')
        checks.append(affine_certificate(word, result))
    return {'status': 'PASS_INDEPENDENT_TERMINAL_MINOR', 'checks': checks,
            'scope': 'Rechecks the reported terminal bases, protected projection and independently '
                     'propagated suffix offsets. Carrier census, kernel completeness and dynamic '
                     'enclosure induction require the separate source replay and mathematical proof.'}


def rejected(function, expected):
    try:
        function()
    except ValueError as error:
        require(str(error) == expected, 'Unexpected control rejection: ' + str(error))
    else:
        raise ValueError('Boundary control was accepted: ' + expected)


def terminal_controls():
    # An actual scalar trace sends e0 to (1,1). Output 1 is protected.
    word = {'public': 2, 'owned_fields': 0, 'initial': [0, 1], 'final': [0, 1],
            'program': [['MOVE', 1, 1, 0, False], ['ADD', 1, 0, '1', 0],
                        ['MOVE', 1, 0, 1, False]]}
    result = {'case': {'cut_after': -1, 'pivot': 0}, 'final_basis': [{'0': '1', '1': '1'}]}
    require(affine_certificate(word, result)['baseline_in_span'], 'Review terminal positive')
    omission = deepcopy(result)
    omission['final_basis'] = [{'1': '1'}]
    rejected(lambda: affine_certificate(word, omission), 'Review affine offset is not in correction span')
    zero_projection = deepcopy(result)
    zero_projection['final_basis'] = [{'0': '1'}]
    rejected(lambda: affine_certificate(word, zero_projection), 'Review protected projection is not injective')
    duplicate = deepcopy(result)
    duplicate['final_basis'] *= 2
    rejected(lambda: affine_certificate(word, duplicate), 'Review protected projection is not injective')
    return {'terminal_positive': True, 'affine_offset_omission_rejected': True,
            'protected_kernel_rejected': True, 'dependent_basis_rejected': True}


def endpoint_boundary_controls(endpoints):
    # Each summand is unavailable at both endpoints, but their true net is zero.
    # A per-donor exclusion would incorrectly reject this cancellable interval.
    word = {'program': [['MOVE', 0, 0, 1, False], ['ADD', 0, 1, '1', 1],
                        ['ADD', 0, 1, '-1', 1], ['MOVE', 0, 1, 0, False]]}
    census, pairs, event_pair, requests = endpoints.enumerate_pairs(word)
    require(len(pairs) == 1 and pairs[0]['incoming_events'] == [1, 2], 'Review endpoint interval census')
    require(pairs[0]['windows'] == {'before': [0, 0], 'after': [4, 4]}, 'Review endpoint boundary slots')
    donor, bank = {1: Q(1)}, [('other', {2: Q(1)})]
    require(not endpoints.span_solve(donor, bank)['in_span'], 'Review unavailable individual donor')
    net = {}
    for i in pairs[0]['incoming_events']:
        endpoints.add(net, donor, Q(word['program'][i][3]))
    require(not net and endpoints.span_solve(net, bank)['in_span'], 'Review net cancellation is retained')
    read = deepcopy(word)
    read['program'].insert(2, ['ADD', 1, 0, '1', 1])
    require(not endpoints.enumerate_pairs(read)[1], 'Review intermediate receiver read must exclude interval')
    scale = deepcopy(word)
    scale['program'].insert(2, ['SCALE', 0, '2', 1])
    require(not endpoints.enumerate_pairs(scale)[1], 'Review receiver scaling must exclude interval')
    # Two equal role numbers at different times must remain independent labels.
    first, second = {0: Q(1), 1: Q(1)}, {1: Q(1)}
    require(not endpoints.span_solve({0: Q(1)}, [('early:4', first)])['in_span'], 'Review one bank negative')
    require(endpoints.span_solve({0: Q(1)}, [('early:4', first), ('late:4', second)])['in_span'],
            'Review accumulated distinct donor versions')
    return {'net_cancellation_positive_despite_unavailable_summands': True,
            'intermediate_receiver_read_excluded': True, 'receiver_scaling_excluded': True,
            'word_boundary_slots_included': True, 'accumulated_distinct_versions_positive': True}


def separating_functional(target, donors):
    """Return an explicit rational dual certificate; do not trust span_solve."""
    columns = sorted(set(target).union(*(set(row) for row in donors)))
    position = {column: i for i, column in enumerate(columns)}
    echelon = {}
    for original in donors:
        row = [original.get(column, Q(0)) for column in columns]
        for pivot in sorted(echelon):
            coefficient = row[pivot]
            row = [x - coefficient * y for x, y in zip(row, echelon[pivot])]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is not None:
            divisor = row[pivot]
            echelon[pivot] = [value / divisor for value in row]
    residue = [target.get(column, Q(0)) for column in columns]
    for pivot in sorted(echelon):
        coefficient = residue[pivot]
        residue = [x - coefficient * y for x, y in zip(residue, echelon[pivot])]
    free = next((i for i, value in enumerate(residue) if value), None)
    require(free is not None and free not in echelon, 'Review expected a separating functional')
    functional = [Q(0)] * len(columns)
    functional[free] = Q(1)
    for pivot in sorted(echelon, reverse=True):
        functional[pivot] = -sum(value * coefficient for value, coefficient
                                in zip(functional, echelon[pivot]))
    for row in donors:
        require(sum(value * functional[position[column]] for column, value in row.items()) == 0,
                'Review functional fails to annihilate donor')
    pairing = sum(value * functional[position[column]] for column, value in target.items())
    require(bool(pairing), 'Review functional fails to separate target')
    return {'functional': {str(column): str(functional[i]) for i, column in enumerate(columns) if functional[i]},
            'target_pairing': str(pairing), 'donors_annihilated': len(donors)}


def private_dual_checks(word, private_module):
    # Replaying this small module obtains the exact recorded row bank. The
    # independent part here is the checked dual witness, not donor enumeration.
    result = private_module.run(word)
    checks = []
    for case in result['cases']:
        target = {int(k): Q(v) for k, v in case['target_row'].items()}
        donors = [{int(k): Q(v) for k, v in row.items()} for row in case['donor_rows'].values()]
        certificate = separating_functional(target, donors)
        checks.append({'after_event_zero_based': case['after_event_zero_based'],
                       'role': case['role'], 'same_span_bank': certificate})
    rejected(lambda: separating_functional({0: Q(1)}, [{0: Q(1)}]),
             'Review expected a separating functional')
    positive = separating_functional({0: Q(1)}, [{0: Q(1), 1: Q(1)}])
    require(positive['target_pairing'] != '0', 'Review correlated dual positive')
    return {'status': 'PASS_FIVE_EXPLICIT_DUAL_CERTIFICATES', 'checks': checks,
            'self_as_donor_mutation_rejected': True, 'correlated_span_dual_positive': True,
            'scope': 'Each displayed rational functional annihilates every reported same-span donor '
                     'and pairs nontrivially with the target. Source replay and exhaustive bank '
                     'enumeration remain the private-query module responsibility.'}


def run(word, carrier_result, endpoints_module, private_module):
    return {'status': 'PASS_INDEPENDENT_CERTIFICATES_AND_BOUNDARY_CONTROLS',
            'terminal': independent_terminal(word, carrier_result),
            'terminal_controls': terminal_controls(),
            'endpoint_boundary_controls': endpoint_boundary_controls(endpoints_module),
            'private_dual_certificates': private_dual_checks(word, private_module),
            'review_type': 'Independent AI-assisted code and mathematical-scope review; not human or formal verification.'}
