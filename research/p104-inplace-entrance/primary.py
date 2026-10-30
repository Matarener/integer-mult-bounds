"""Source-bound normalised matrix and admission proof for one entrance word.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
The projection and CA/2 factorisation are credited to Hiroki KUMAZAKI/PR3446
and Nick Petalas/PR3462. This module reconstructs their used implication from
WORD and checks the changed chronological program. No predecessor executable
is imported here. Native synthesis and literal Gaussian execution are separate.
"""

from collections import Counter
from fractions import Fraction
import hashlib
import json


BASIS = ('X0', 'X33', 'X101', 'X102', 'X11', 'X12', 'X15', 'X24')
FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)
PROJECTION = '66113bcd513a17eac24f43944a8759bdae1bb2a85e2b9900122f281c5c676dc8'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def order(name):
    return name[0], int(name[1:])


def row_add(target, source, coefficient):
    result = dict(target)
    for key, value in source.items():
        result[key] = result.get(key, Fraction()) + coefficient * value
        if not result[key]:
            del result[key]
    return result


def rows_record(rows):
    return {name: {key: str(value) for key, value in sorted(row.items())}
            for name, row in sorted(rows.items())}


def initial_state(word, weights=None):
    weights = weights or {}
    return {name: {name: Fraction(weights.get(name, 1))}
            for name in word['initial_frames']}


def projection(word):
    """Rebuild PR3446's closure with a dependency graph, not saved event bits."""
    names = sorted(word['initial_frames'])
    inputs = {-j-1: name for j, name in enumerate(names)}
    current = {name: key for key, name in inputs.items()}
    dependencies, allocation, cleanup = {}, {}, {}
    for event, op in enumerate(word['program']):
        kind, target = op[:2]
        if kind == 'zero':
            need(target not in current, 'closure private alias')
            dependencies[event] = ()
            allocation[target] = event
        else:
            need(target in current, 'closure live target')
            dependencies[event] = (current[target],)
            if kind == 'add':
                dependencies[event] += (current[op[2]],)
        current[target] = event
        if kind == 'erase':
            cleanup[allocation.pop(target)] = event
            del current[target]
    need(not allocation and len(cleanup) == 8, 'closure private lifecycle')
    roles = {'Y' + str(j) for j in (*range(22, 33), *range(63, 104))}
    roles |= {prefix + str(j) for prefix in ('D', 'G') for j in range(27, 32)} | {'Q7'}
    ports = [i for i, op in enumerate(word['program'])
             if i <= 4516 and op[0] == 'add' and op[2] in roles
             and op[1] not in roles | {'C'}]
    need(len(ports) == 675, 'closure observed ports')
    todo = ports + [current[b] for b in roles | {word['program'][i][1] for i in ports}]
    reached = set()
    while todo:
        node = todo.pop()
        if node in reached:
            continue
        reached.add(node)
        if node < 0:
            todo.append(current[inputs[node]])
        else:
            todo.extend(dependencies[node])
            if node in cleanup:
                todo.append(cleanup[node])
    selected = sorted(node for node in reached if node >= 0)
    need(len(selected) == 4027 and sum(node < 0 for node in reached) == 265,
         'actual terminal-history closure')
    need(digest(selected) == PROJECTION, 'independently reconstructed projection hash')
    return selected


def original(word, selected, state=None, frames=None, admission=False):
    """Exact field-module coefficients; every scalar read has its actual frame."""
    state = initial_state(word) if state is None else {b: dict(v) for b, v in state.items()}
    frames = ({b: tuple(f) for b, f in word['initial_frames'].items()}
              if frames is None else dict(frames))
    counts = Counter()
    for event in selected:
        op = word['program'][event]
        kind, target = op[:2]
        if kind == 'zero':
            need(target not in state, 'private alias at ' + str(event))
            state[target], frames[target] = {}, tuple(op[2])
        elif kind == 'erase':
            need(not state[target], 'nonzero private erasure at ' + str(event))
            del state[target], frames[target]
        elif kind == 'transport':
            need(frames[target] == tuple(op[2]), 'old native frame at ' + str(event))
            frames[target] = tuple(op[3])
        elif kind == 'sign':
            state[target] = {b: -v for b, v in state[target].items()}
        else:
            need(kind == 'add', 'original opcode')
            source, coefficient = op[2], Fraction(op[3])
            need(target != source and frames[target] == frames[source] == tuple(op[4]),
                 'original ADD access at ' + str(event))
            increment = {b: coefficient * v for b, v in state[source].items()}
            if admission:
                need(all(v.denominator == 1 for v in increment.values()),
                     'non-module increment at ' + str(event))
            state[target] = row_add(state[target], increment, 1)
        if admission and target in state:
            need(all(v.denominator == 1 for v in state[target].values()),
                 'non-module state at ' + str(event))
        counts[kind] += 1
    need(set(state) == set(word['initial_frames']), 'original public-bank set')
    return state, frames, dict(sorted(counts.items()))


def program_for(word, certificate, adapters):
    A, C = certificate['factor']['A'], certificate['factor']['C']
    xs = sorted(C, key=order)
    omitted = {row['bank'] for row in adapters['omitted_banks']}
    other = sorted(omitted - set(xs), key=order)
    need(len(xs) == 52 and len(other) == 41 and len(omitted) == 93, 'omitted roles')
    need(tuple(certificate['residual']['minor_rows']) == BASIS, 'credited basis order')
    need([C[b] for b in BASIS] == [[int(i == j) for j in range(8)] for i in range(8)],
         'dirty output pivot identity')
    need(len(A) == 8 and all(len(row) == 8 for row in C.values()), 'factor dimensions')
    ys = ['Y' + str(j) for j in range(104)]
    need(all(set(row) <= set(ys) and all(type(v) is int for v in row.values()) for row in A),
         'integer gather')
    need(all(type(v) is int for row in C.values() for v in row), 'integer scatter')
    need(all(len(word['initial_frames'][x]) == 1 for x in xs), 'singleton X entrance')
    need(all(word['initial_frames'][b] == [] for b in other + ys), 'empty NG/Y entrance')
    need(all(tuple(word['final_frames'][b]) == FULL for b in omitted), 'full omitted exit')
    program = [['native', b, 'enter'] for b in xs]

    def scatter(sign):
        for target in xs:
            if target in BASIS:
                continue
            for j, source in enumerate(BASIS):
                coefficient = sign * C[target][j]
                program.extend([['add', target, source, 1 if coefficient > 0 else -1]
                                for _ in range(abs(coefficient))])

    scatter(-1)
    for y in ys:
        if not any(row.get(y, 0) for row in A):
            continue
        program.append(['half', y])
        for j, target in enumerate(BASIS):
            coefficient = A[j].get(y, 0)
            program.extend([['add', target, y, 1 if coefficient > 0 else -1]
                            for _ in range(abs(coefficient))])
        program.append(['double', y])
    scatter(1)
    program.extend([['native', b, 'finish'] for b in xs + other])
    need(len(program) == 1238, 'changed prelude length')
    return program


def entrance(word, program, weights=None):
    state = initial_state(word, weights)
    frames = {b: tuple(f) for b, f in word['initial_frames'].items()}
    scalar_peak = {'twice_equal_bound': 0}
    envelopes = {(1, 0): {'bank': 'initial X', 'after_prelude_operation': -1},
                 (0, 2): {'bank': 'initial Y', 'after_prelude_operation': -1}}
    counts = Counter()
    for index, op in enumerate(program):
        kind, target = op[:2]
        need(target in state, 'entrance live bank')
        if kind == 'native':
            if op[2] == 'enter':
                need(target.startswith('X') and len(frames[target]) == 1, 'entrance native frame')
                frames[target] = ()
            else:
                need(op[2] == 'finish' and frames[target] == (), 'exit native frame')
                frames[target] = FULL
        else:
            need(frames[target] == (), 'scalar target common frame')
            if kind == 'add':
                source, sign = op[2:]
                need(type(sign) is int and sign in (-1, 1), 'unit scalar coefficient')
                need(source != target and frames[source] == (), 'scalar source common frame')
                state[target] = row_add(state[target], state[source], sign)
            else:
                need(kind in ('half', 'double') and target.startswith('Y'), 'source scaling opcode')
                scale = Fraction(1, 2) if kind == 'half' else Fraction(2)
                state[target] = {b: scale * v for b, v in state[target].items()}
            if weights is not None:
                need(all(v.denominator == 1 for v in state[target].values()),
                     'entrance module admission at ' + str(index))
            else:
                x_weight = sum(abs(v) for b, v in state[target].items() if b.startswith('X'))
                y_weight = sum(abs(v) for b, v in state[target].items() if b.startswith('Y'))
                need(x_weight.denominator == 1 and (2*y_weight).denominator == 1,
                     'half-integral scalar envelope')
                envelopes.setdefault((int(x_weight), int(2*y_weight)),
                    {'bank': target, 'after_prelude_operation': index})
                bound = x_weight + y_weight
                if 2 * bound > scalar_peak['twice_equal_bound']:
                    scalar_peak = {'twice_equal_bound': int(2*bound), 'x_weight': int(x_weight),
                                   'twice_y_weight': int(2*y_weight), 'bank': target,
                                   'after_prelude_operation': index}
        counts[kind] += 1
    for b in state:
        if b.startswith('Y'):
            need(state[b] == initial_state(word, weights)[b], 'complete Y source restoration')
    pareto = [{'x_weight': x, 'twice_y_weight': y, **envelopes[(x, y)]}
              for x, y in sorted(envelopes)
              if not any(u >= x and v >= y and (u, v) != (x, y) for u, v in envelopes)]
    extreme = []
    if weights is None:
        need([(row['x_weight'], row['twice_y_weight']) for row in pareto]
             == [(8, 190), (9, 156), (11, 128), (12, 98), (13, 49), (14, 0)],
             'exact scalar Pareto rows')
        # The first omitted row is below a convex combination of the first
        # and third; the second is the midpoint of the last two extremes.
        need(Fraction(2, 3)*8 + Fraction(1, 3)*11 == 9
             and Fraction(2, 3)*190 + Fraction(1, 3)*128 >= 156,
             'first scalar convex domination')
        need(Fraction(12+14, 2) == 13 and Fraction(98+0, 2) == 49,
             'second scalar convex domination')
        extreme = [row for row in pareto if row['x_weight'] in (8, 11, 12, 14)]
    return state, frames, {'operations': dict(sorted(counts.items())),
                           'scalar_peak_after_entering_empty_frame': scalar_peak,
                           'two_bound_scalar_envelope': pareto,
                           'convex_reduced_scalar_envelope': extreme,
                           'width_interpretation': 'Maximum of the displayed x_weight*H_X + twice_y_weight*H_Y/2 rows;103H when H_X=H_Y=H. H_X is after entrance conversion and H_Y is unhalved. Native conversions/temporaries are additional.'}


def analyze(word, native, certificate, adapters, program):
    need(len(word['program']) == 5398 and len(word['initial_frames']) == 358, 'pinned word shape')
    selected = projection(word)
    need(certificate['closure']['events'] == len(selected), 'credited closure size')
    need(selected == sorted(set(selected)) and len(selected) == 4027 and digest(selected) == PROJECTION,
         'projection event binding')
    omitted = {row['bank'] for row in adapters['omitted_banks']}
    for i in selected:
        op = word['program'][i]
        need(op[1] not in omitted and (op[0] != 'add' or op[2] not in omitted),
             'retained projection accesses omitted bank')
    need(word['chart'] == native['chart'], 'actual native chart convention')
    bound = set()
    for record in native['transports']:
        for event in record['events']:
            need(event not in bound, 'duplicate native occurrence')
            bound.add(event)
            op = word['program'][event]
            need(op[0] == 'transport' and op[2:] == [record['old'], record['new'], record['recipe']['rank']],
                 'native occurrence old/new/rank binding')
    need(bound == {i for i, op in enumerate(word['program']) if op[0] == 'transport'}
         and len(bound) == 2070, 'complete native occurrence coverage')
    need(program == program_for(word, certificate, adapters), 'serialized entrance program differs')
    full, full_frames, full_counts = original(word, range(5398))
    sliced, sliced_frames, slice_counts = original(word, selected)
    A, C = certificate['factor']['A'], certificate['factor']['C']
    residual = {b: row_add(full[b], sliced[b], -1) for b in full}
    need({b for b, row in residual.items() if row} == set(C), 'exact residual support')
    for x in C:
        expected = {}
        for j in range(8):
            expected = row_add(expected, A[j], Fraction(C[x][j], 2))
        need(residual[x] == expected, 'source-reconstructed CA/2 residual')
    need(full_frames == {b: tuple(f) for b, f in word['final_frames'].items()}, 'original final frames')
    prelude, new_frames, prelude_counts = entrance(word, program)
    for b in full:
        need(prelude[b] == row_add({b: Fraction(1)}, residual[b], 1), 'actual entrance I+K')
    changed, changed_frames, _ = original(word, selected, prelude, new_frames)
    need(changed == full and changed_frames == full_frames, 'all358 final fields and frames')
    need(all(sliced[b] == {b: Fraction(1)} for b in omitted), 'omitted projection identity')
    need(all(sliced[b] == {b: Fraction(1)} for b in sliced if b.startswith('Y')), 'normalised Y preservation')

    # A common explicit sufficient domain, deliberately not claimed minimal.
    # Charts preserve B9 and each integer multiple of it by the pinned lemmas.
    weights = {b: (4 if b.startswith('Y') else 2 if b.startswith('N') else 1)
               for b in word['initial_frames']}
    admitted_full, _, _ = original(word, range(5398), initial_state(word, weights), admission=True)
    admitted_prelude, admitted_frames, _ = entrance(word, program, weights)
    admitted_changed, _, _ = original(word, selected, admitted_prelude, admitted_frames, admission=True)
    need(admitted_full == admitted_changed, 'common admitted full/changed endpoint map')

    controls = {}
    # A direct source omission is a genuine observable error, not a schema error.
    mutated = [op for op in program if op != ['double', 'Y0']]
    try:
        entrance(word, mutated)
    except ValueError as error:
        need(str(error) == 'complete Y source restoration', 'source-return control reason')
        controls['omit_Y0_redoubling'] = str(error)
    else:
        raise ValueError('source-return control was vacuous')
    weak = dict(weights)
    weak['N100'] = 1
    try:
        original(word, selected, initial_state(word, weak), admission=True)
    except ValueError as error:
        need(str(error) == 'non-module increment at 312', 'N100 boundary control reason')
        controls['weaken_N100_to_B9'] = str(error)
    else:
        raise ValueError('N100 admission control was vacuous')

    return {
        'status': 'PASS_SOURCE_BOUND_ENTRANCE_MATRIX_AND_ADMISSION',
        'normalised_endpoint_fields_checked': 358,
        'normalised_matrix_entries_checked': 358*358,
        'endpoint_matrix_sha256': digest(rows_record(full)),
        'residual_nonzero_rows': 52,
        'residual_nonzero_coefficients': sum(len(row) for row in residual.values()),
        'projection_event_sha256': digest(selected),
        'projection_never_reads_or_writes_omitted': True,
        'new_program_sha256': digest(program),
        'native_occurrences_bound': len(bound),
        'original_opcode_counts': full_counts,
        'retained_opcode_counts': slice_counts,
        'entrance': prelude_counts,
        'common_sufficient_admission': {'Y_in_4B9': sum(b.startswith('Y') for b in weights),
            'N_in_2B9': sum(b.startswith('N') for b in weights),
            'other_in_B9': sum(not b.startswith(('Y', 'N')) for b in weights),
            'minimality_claimed': False,
            'all_scalar_increments_module_integral': True,
            'native_and_chart_module_lemmas': 'Pinned PR3382 and PR3416 proofs, not re-proved by this matrix check.'},
        'controls': controls,
    }
