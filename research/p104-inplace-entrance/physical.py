#!/usr/bin/env python3
"""Independent local physical audit of the dirty-basis P104 entrance schedule.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.

No candidate or predecessor executable is imported. The canonical chart is
reconstructed from the retained PR3416 definition; the candidate is executed
from its explicit native recipes and serialized primitive program. This is a
finite 512-coordinate local comparison, not a new universal covariance proof,
a whole-WORD admission theorem, or a physical owner/routing/cost certificate.

verify_physical(word, completion, x_to_empty, empty_to_full,
                initial_fields=None, program=None)
returns actual_fields, expected_fields, initial_fields, endpoint frames, and a
compact receipt. Default inputs are the named dense fixture below. Every local
dirty field must be in B9 and every Y in 4B9. Arbitrary valid zero inputs are
accepted; primitive controls use separate fixed witnesses.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


N = 512
RANK = 9
FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)
INPUT_BITS = 8192
WORK_BITS = INPUT_BITS + 32
WORD_PIN = 'cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50'
COMPLETION_PIN = 'f68a2e6f3bd771b9692772909df200102350a80deda35532f3cc348b75d0c044'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def order(name):
    need(type(name) is str and len(name) >= 2 and name[0] in 'GNXY'
         and name[1:].isdigit() and str(int(name[1:])) == name[1:], 'bank name')
    return name[0], int(name[1:])


def integer(value, low, high, message):
    need(type(value) is int and low <= value <= high, message)
    return value


def vector(value, bits=WORK_BITS):
    need(isinstance(value, (list, tuple)) and len(value) == N, 'Gaussian field length')
    result = []
    for pair in value:
        need(isinstance(pair, (list, tuple)) and len(pair) == 2, 'Gaussian pair shape')
        need(all(type(v) is int and abs(v).bit_length() <= bits for v in pair),
             'Gaussian integer component bound')
        result.append((pair[0], pair[1]))
    return result


def phase(value, exponent):
    integer(exponent, 0, 3, 'phase exponent')
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent]


def add(left, right, sign=1):
    return [(a + sign*c, b + sign*d) for (a, b), (c, d) in zip(left, right)]


def scale(value, coefficient):
    return [(coefficient*a, coefficient*b) for a, b in value]


def half(value):
    for address, (a, b) in enumerate(value):
        need(a % 2 == b % 2 == 0, 'nonintegral source half at ' + str(address))
    return [(a//2, b//2) for a, b in value]


def encode(coefficients):
    result = vector(coefficients)
    for bit in range(RANK):
        mask = 1 << bit
        for low in range(N):
            if low & mask:
                continue
            a, b = result[low]
            c, d = result[low | mask]
            result[low | mask] = (a + c-d, b + c+d)
    return vector(result)


def newton(value):
    result = vector(value)
    for bit in range(RANK):
        mask = 1 << bit
        for high in range(N):
            if high & mask:
                a, b = result[high]
                c, d = result[high ^ mask]
                result[high] = (a-c, b-d)
    for address, (a, b) in enumerate(result):
        for _ in range(address.bit_count()):
            need((a+b) % 2 == (b-a) % 2 == 0,
                 'outside B9 at Newton mask ' + str(address))
            a, b = (a+b)//2, (b-a)//2
        result[address] = (a, b)
    return vector(result)


def domain(value, multiplier):
    coefficients = newton(value)
    need(all(a % multiplier == b % multiplier == 0 for a, b in coefficients),
         'outside ' + str(multiplier) + 'B9')
    return coefficients


def frame(value):
    need(isinstance(value, (list, tuple)) and len(value) <= RANK, 'frame dimension')
    span = {0}
    result = []
    for direction in value:
        integer(direction, 1, N-1, 'frame direction')
        need(direction not in span, 'dependent frame')
        span |= {x ^ direction for x in span}
        result.append(direction)
    return tuple(result)


def ideal_pair(left, right, inverse=False):
    a, b = left
    c, d = right
    dr, di = a-c, b-d
    tr, ti = ((di, -dr) if inverse else (-di, dr))
    numerators = (a+c+tr, b+d+ti, a+c-tr, b+d-ti)
    need(all(v % 2 == 0 for v in numerators), 'nonintegral ideal native pair')
    return (numerators[0]//2, numerators[1]//2), (numerators[2]//2, numerators[3]//2)


def literal_pair(left, right, inverse=False):
    expected = ideal_pair(left, right, inverse)
    a, b = left
    c, d = right
    dr, di = a-c, b-d
    tr, ti = ((di, -dr) if inverse else (-di, dr))
    mr, mi = c + dr//2, d + di//2
    second = (mr - tr//2, mi - ti//2)
    first = (second[0] + tr, second[1] + ti)
    need((first, second) == expected, 'literal/ideal native pair disagreement')
    return first, second


def coordinate(value, bit, inverse=False, literal=False):
    result = list(value)
    operation = literal_pair if literal else ideal_pair
    mask = 1 << bit
    for low in range(N):
        if not low & mask:
            result[low], result[low | mask] = operation(value[low], value[low | mask], inverse)
    return result


def monomial(value, permutation, phases, inverse=False):
    result = [(0, 0)] * N
    for source, target in enumerate(permutation):
        if inverse:
            result[source] = phase(value[target], (-phases[source]) % 4)
        else:
            result[target] = phase(value[source], phases[source])
    return result


class ChartOracle:
    """Direct canonical H_W^-1 C^-1 H_W, not an archived native recipe."""

    def __init__(self):
        self.plans = {}

    def plan(self, directions):
        directions = frame(directions)
        if directions in self.plans:
            return self.plans[directions]
        columns = list(directions)
        span = {0}
        for column in columns:
            span |= {x ^ column for x in span}
        for bit in range(RANK):
            column = 1 << bit
            if column not in span:
                columns.append(column)
                span |= {x ^ column for x in span}
        need(len(columns) == RANK and len(span) == N, 'completed canonical binary basis')
        inverse = [None] * N
        for mask in range(N):
            address = 0
            for bit, column in enumerate(columns):
                if (mask >> bit) & 1:
                    address ^= column
            need(inverse[address] is None, 'canonical basis bijection')
            inverse[address] = mask
        # Columns of A=G^-1, recovered by complete binary enumeration.
        a_columns = [inverse[1 << bit] for bit in range(RANK)]
        q = [[int(j == k) ^ ((a_columns[j] & a_columns[k]).bit_count() & 1)
              for k in range(RANK)] for j in range(RANK)]
        phases = []
        for address in range(N):
            bits = [j for j in range(RANK) if (address >> j) & 1]
            exponent = sum(q[j][j] for j in bits)
            exponent += 2*sum(q[j][k] for j in bits for k in bits if j < k)
            phases.append(exponent % 4)
        self.plans[directions] = (inverse, phases)
        return inverse, phases

    def apply(self, value, directions, inverse=False):
        directions = frame(directions)
        result = list(value)
        if not directions:
            return result
        if len(directions) < RANK:
            permutation, phases = self.plan(directions)
            result = monomial(result, permutation, phases)
        for bit in range(len(directions)):
            result = coordinate(result, bit, inverse=not inverse)
        if len(directions) < RANK:
            result = monomial(result, permutation, phases, inverse=True)
        return vector(result)


def wrapper_plan(record):
    need(type(record) is dict and set(record) ==
         {'matrix_rows', 'offset', 'quadratic_rows', 'linear_Z4', 'phase'}, 'native wrapper schema')
    rows, quadratic, linear = record['matrix_rows'], record['quadratic_rows'], record['linear_Z4']
    need(all(type(a) is list and len(a) == RANK for a in (rows, quadratic, linear)), 'native wrapper dimensions')
    for a in rows + quadratic:
        integer(a, 0, N-1, 'native binary row')
    for a in linear:
        integer(a, 0, 3, 'native linear phase')
    offset = integer(record['offset'], 0, N-1, 'native address offset')
    constant = integer(record['phase'], 0, 3, 'native constant phase')
    permutation, phases = [], []
    for address in range(N):
        target = offset
        for bit, row in enumerate(rows):
            target ^= ((row & address).bit_count() & 1) << bit
        exponent = constant + sum(linear[j] for j in range(RANK) if (address >> j) & 1)
        # The retained convention uses only strict upper-triangular entries.
        exponent += 2*sum(1 for j in range(RANK) for k in range(j+1, RANK)
                          if (address >> j) & 1 and (address >> k) & 1 and (quadratic[j] >> k) & 1)
        permutation.append(target)
        phases.append(exponent % 4)
    need(len(set(permutation)) == N, 'nonbijective native wrapper')
    return permutation, phases


class LiteralNative:
    def __init__(self):
        self.plans = {}
        self.counts = Counter()

    def apply(self, value, recipe):
        need(type(recipe) is dict and set(recipe) == {'rank', 'left', 'right'}, 'native recipe schema')
        rank = integer(recipe['rank'], 1, RANK, 'native rank')
        key = digest(recipe)
        if key not in self.plans:
            self.plans[key] = (wrapper_plan(recipe['right']), wrapper_plan(recipe['left']))
        right, left = self.plans[key]
        result = monomial(value, *right)
        for bit in range(rank):
            result = coordinate(result, bit, literal=True)
            self.counts['completed_floor_pairs'] += N//2
        result = monomial(result, *left)
        self.counts['native_calls'] += 1
        self.counts['native_rank_mass'] += rank
        self.counts['actual_wrappers'] += 2
        self.counts['actual_phase_applications'] += 2*N
        return vector(result)


def source_spec(word, completion):
    need(type(word) is dict and type(completion) is dict, 'source object schemas')
    A, C = completion['factor']['A'], completion['factor']['C']
    basis = completion['residual']['minor_rows']
    xs = sorted(C, key=order)
    ys = ['Y' + str(j) for j in range(104)]
    omitted = sorted(completion['unfilled_physical_frame_gaps'], key=order)
    ng = [name for name in omitted if name not in xs]
    need(len(A) == len(basis) == 8 and len(xs) == 52 and len(omitted) == 93 and len(ng) == 41,
         'actual local dimensions')
    need(len(set(basis)) == 8 and set(basis) <= set(xs), 'actual basis roles')
    need([C[b] for b in basis] == [[int(i == j) for j in range(8)] for i in range(8)], 'C basis identity')
    need(all(type(row) is dict and set(row) <= set(ys)
             and all(type(v) is int and -2 <= v <= 2 for v in row.values()) for row in A), 'integer A')
    need(all(type(row) is list and len(row) == 8
             and all(type(v) is int and -4 <= v <= 4 for v in row) for row in C.values()), 'integer C')
    need(all(name.startswith('X') for name in xs) and all(name[0] in 'NG' for name in ng), 'local role partition')
    need(not (set(omitted) & set(ys)), 'source/output role alias')
    for name in omitted:
        old, new = completion['unfilled_physical_frame_gaps'][name]
        need(frame(old) == frame(word['initial_frames'][name]), 'bound entrance frame ' + name)
        need(frame(new) == frame(word['final_frames'][name]) == FULL, 'bound endpoint frame ' + name)
        need(len(frame(old)) == (1 if name in xs else 0), 'entrance dimension ' + name)
    need(all(frame(word['initial_frames'][name]) == () for name in ys), 'common Y entrance frame')
    return A, C, basis, xs, ys, omitted, ng


def make_program(A, C, basis, xs, ys, ng):
    other = [x for x in xs if x not in basis]
    program = [['native', name, 'enter'] for name in xs]
    for target in other:
        for j, source in enumerate(basis):
            coefficient = -C[target][j]
            program += [['add', target, source, 1 if coefficient > 0 else -1]] * abs(coefficient)
    for source in ys:
        if not any(row.get(source, 0) for row in A):
            continue
        program.append(['half', source])
        for j, target in enumerate(basis):
            coefficient = A[j].get(source, 0)
            program += [['add', target, source, 1 if coefficient > 0 else -1]] * abs(coefficient)
        program.append(['double', source])
    for target in other:
        for j, source in enumerate(basis):
            coefficient = C[target][j]
            program += [['add', target, source, 1 if coefficient > 0 else -1]] * abs(coefficient)
    program += [['native', name, 'finish'] for name in xs + ng]
    return program


def dense_fields(roles, ys):
    result = {}
    for slot, name in enumerate(roles):
        coefficients = [(((37*slot + 17*k + 3*k.bit_count()) % 11)-5,
                         ((19*slot + 29*k + 5*k.bit_count()) % 13)-6) for k in range(N)]
        result[name] = scale(encode(coefficients), 4 if name in ys else 1)
    return result


def primitive_controls(empty_to_full):
    controls = {}
    need([phase((-3, 5), exponent) for exponent in range(4)] ==
         [(-3, 5), (-5, -3), (3, -5), (5, 3)], 'signed phase primitive')
    need(half([(-6, -10)]*N) == [(-3, -5)]*N, 'signed exact-half primitive')
    controls['signed_phase_cycle_and_exact_negative_half'] = 'PASS'

    def reject(name, operation, prefix):
        try:
            operation()
        except ValueError as error:
            need(str(error).startswith(prefix), 'wrong rejection for ' + name)
            controls[name] = str(error)
        else:
            raise ValueError('accepted negative control ' + name)

    reject('odd_source_half', lambda: half([(-3, 4)]*N), 'nonintegral source half')
    reject('nonintegral_ideal_pair', lambda: literal_pair((0, 0), (1, 0)), 'nonintegral ideal native pair')
    reject('outside_B9', lambda: domain([(1, 0)] + [(0, 0)]*(N-1), 1), 'outside B9')
    reject('inside_2B9_outside_required_4B9', lambda: domain([(2, 0)]*N, 4), 'outside 4B9')
    bad = json.loads(canonical(empty_to_full['recipe']))
    bad['left']['phase'] = True
    reject('boolean_native_phase', lambda: LiteralNative().apply([(1, 0)]*N, bad), 'native constant phase')
    probe = [(1, 0)]*N
    good = LiteralNative().apply(probe, empty_to_full['recipe'])
    wrong = json.loads(canonical(empty_to_full['recipe']))
    wrong['left']['phase'] = (wrong['left']['phase'] + 1) % 4
    changed = LiteralNative().apply(probe, wrong)
    expected = ChartOracle().apply(probe, FULL)
    need(good == expected and changed != expected, 'native phase endpoint control')
    first = next(k for k in range(N) if changed[k] != expected[k])
    controls['native_constant_phase_mutation'] = {
        'address': first, 'observed': changed[first], 'expected': expected[first],
        'mutated_wrapper': 'left', 'change': 'phase + 1 modulo 4',
    }
    return controls


def verify_physical(word, completion, x_to_empty, empty_to_full,
                    initial_fields=None, program=None):
    """Run one exact local fixture; whole-source authentication belongs to caller.

    The canonical dirty variable x is J_initial^-1 of the supplied physical X.
    H_Y in scalar row bounds means the actual, unhalved common-frame Y field.
    Each supplied native record is {old, new, recipe}; extra certificate keys
    are allowed at record level but never in executable recipe/wrapper schemas.
    A serialized program is executed exactly as supplied and additionally bound
    to this fixed ordered schedule, including all source returns.
    """
    input_digests = [digest(value) for value in (word, completion, x_to_empty, empty_to_full)]
    A, C, basis, xs, ys, omitted, ng = source_spec(word, completion)
    roles = sorted(omitted + ys, key=order)
    need(type(x_to_empty) is dict and set(x_to_empty) == set(xs), 'all52 entrance native records')
    need(type(empty_to_full) is dict and frame(empty_to_full['old']) == ()
         and frame(empty_to_full['new']) == FULL and empty_to_full['recipe']['rank'] == 9,
         'common full-frame native record')
    for name in xs:
        record = x_to_empty[name]
        need(type(record) is dict and frame(record['old']) == frame(word['initial_frames'][name])
             and frame(record['new']) == () and record['recipe']['rank'] == 1,
             'actual singleton entrance native record ' + name)
    fixed_program = make_program(A, C, basis, xs, ys, ng)
    if program is None:
        program = fixed_program
    need(type(program) is list and len(program) == 1238, 'serialized program length')
    need(canonical(program) == canonical(fixed_program), 'serialized fixed schedule mismatch')
    program_hash = digest(program)
    supplied_hash = digest(initial_fields) if initial_fields is not None else None
    if initial_fields is None:
        initial_fields = dense_fields(roles, ys)
    need(type(initial_fields) is dict and set(initial_fields) == set(roles), 'exact local initial bank set')
    initial = {name: vector(initial_fields[name], INPUT_BITS) for name in roles}
    for name in roles:
        domain(initial[name], 4 if name in ys else 1)

    oracle = ChartOracle()
    normalized_x = {name: oracle.apply(initial[name], word['initial_frames'][name], inverse=True) for name in xs}
    half_y = {name: half(initial[name]) for name in ys}
    readouts = [[(0, 0)]*N for _ in range(8)]
    for j, row in enumerate(A):
        for name in ys:
            coefficient = row.get(name, 0)
            if coefficient:
                readouts[j] = add(readouts[j], scale(half_y[name], coefficient))
    expected = {name: list(initial[name]) for name in ys}
    for name in xs:
        value = normalized_x[name]
        for j, coefficient in enumerate(C[name]):
            if coefficient:
                value = add(value, scale(readouts[j], coefficient))
        expected[name] = oracle.apply(value, FULL)
    for name in ng:
        expected[name] = oracle.apply(initial[name], FULL)

    state = {name: list(initial[name]) for name in roles}
    frames = {name: frame(word['initial_frames'][name]) for name in roles}
    native = LiteralNative()
    counts = Counter()
    pending_halves = set()
    entered, finished = set(), set()
    peak = max(abs(v) for value in state.values() for pair in value for v in pair)
    for step, op in enumerate(program):
        need(type(op) is list and len(op) in (2, 3, 4), 'program operation shape')
        kind, target = op[:2]
        need(target in state, 'program target role')
        if kind == 'native':
            need(len(op) == 3 and op[2] in ('enter', 'finish'), 'native operation shape')
            stage = op[2]
            if stage == 'enter':
                need(target in xs and target not in entered and target not in finished,
                     'entrance native lifetime')
                record = x_to_empty[target]
                entered.add(target)
            else:
                need(target in omitted and target not in finished and not pending_halves,
                     'finish native lifetime')
                record = empty_to_full
                finished.add(target)
            need(frames[target] == frame(record['old']), 'native old-frame mismatch')
            domain(state[target], 1)
            state[target] = native.apply(state[target], record['recipe'])
            frames[target] = frame(record['new'])
            domain(state[target], 1)
        elif kind == 'add':
            need(len(op) == 4 and target in xs and op[2] in xs + ys
                 and op[2] != target and type(op[3]) is int and op[3] in (-1, 1), 'unit ADD roles/alias/sign')
            source, sign = op[2:]
            need(frames[target] == frames[source] == (), 'unit ADD common frame')
            need(source not in ys or source in pending_halves, 'gather source half lifetime')
            state[target] = vector(add(state[target], state[source], sign))
        elif kind == 'half':
            need(len(op) == 2 and target in ys and target not in pending_halves and frames[target] == (),
                 'temporary source half lifetime')
            domain(state[target], 4)
            state[target] = half(state[target])
            pending_halves.add(target)
        else:
            need(kind == 'double' and len(op) == 2 and target in pending_halves and frames[target] == (),
                 'source restoration lifetime')
            state[target] = vector(scale(state[target], 2))
            pending_halves.remove(target)
            need(state[target] == initial[target], 'immediate source restoration')
        counts[kind] += 1
        peak = max(peak, max(abs(v) for pair in state[target] for v in pair))
    need(not pending_halves and entered == set(xs) and finished == set(omitted), 'all native/source lifetimes completed')
    need(dict(counts) == {'native': 145, 'add': 887, 'half': 103, 'double': 103}, 'literal operation inventory')
    need(native.counts['native_rank_mass'] == 889 and native.counts['completed_floor_pairs'] == 227584,
         'native pair/rank inventory')
    expected_frames = {name: FULL if name in omitted else () for name in roles}
    need(frames == expected_frames, 'all93 physical endpoint frames and104 source frames')
    for name in roles:
        need(state[name] == expected[name], 'complete physical endpoint mismatch ' + name)
        domain(state[name], 4 if name in ys else 1)
    controls = primitive_controls(empty_to_full)
    need(input_digests == [digest(value) for value in (word, completion, x_to_empty, empty_to_full)], 'source objects mutated')
    need(digest(program) == program_hash, 'program object mutated')
    if supplied_hash is not None:
        need(digest(initial_fields) == supplied_hash, 'supplied initial arrays mutated')
    receipt = {
        'status': 'PASS_INDEPENDENT_LOCAL_PHYSICAL_INPLACE_COMPLETION',
        'source_object_sha256': dict(zip(('word', 'completion', 'x_to_empty', 'empty_to_full'), input_digests)),
        'program_sha256': program_hash, 'basis_X': basis,
        'initial_fields_sha256': digest(initial), 'actual_fields_sha256': digest(state),
        'expected_fields_sha256': digest(expected), 'endpoint_frames_sha256': digest(frames),
        'array_equality': {'local_outputs': 93, 'restored_Y': 104, 'Gaussian_coordinates_per_field': N,
                           'full_Gaussian_entries_compared': len(roles)*N, 'all_dirty_offsets_preserved': True},
        'literal_program_counts': dict(counts), 'native_counts': dict(native.counts),
        'direct_scalar_real_primitives': {'ADD_SUB': 908288, 'exact_half': 105472, 'double': 105472},
        'initial_local_domain': '93 physical dirty fields in B9;104 physical Y fields in4B9.',
        'initial_fixture': 'caller supplied' if supplied_hash is not None else 'dense_E9_formula_v1',
        'fixture_role_order': roles, 'input_component_magnitude_bits_limit': INPUT_BITS,
        'work_component_magnitude_bits_limit': WORK_BITS, 'observed_peak_component_magnitude': peak,
        'observed_peak_component_magnitude_bits': peak.bit_length(),
        'observed_peak_sampling': 'Stored fields after complete serialized operations; native-pair internal temporaries are not sampled.',
        'canonical_oracle': 'Greedy binary-basis enumeration;Q=I+A^T A;H phases;J_W=H^-1 C^-1 H;canonical empty/full cases.',
        'native_oracle': 'Actual right wrapper, literal signed-floor C pairs with integral ideal comparison, actual left wrapper.',
        'controls': controls,
        'width_convention': 'H_Y denotes actual unhalved common-frame Y. The 8H_X+95H_Y row attains the equal-bound peak103H; it is not a uniform two-parameter bound. Use the primary Pareto envelope for independent H_X,H_Y. Native adapters and temporaries are additional.',
        'scope': 'One complete dense local physical fixture, exact primitive controls, and supplied schedule binding. Universal recipe covariance and B9 invariance are separate proof inputs. No full-WORD arbitrary-input admission, register-owner, routing, total width/cost or frontier claim.',
    }
    return {'receipt': receipt, 'initial_fields': initial, 'actual_fields': state,
            'expected_fields': expected, 'actual_frames': frames, 'expected_frames': expected_frames}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--recipes', type=Path, required=True,
                        help='JSON with x_to_empty and empty_to_full records')
    parser.add_argument('--program', type=Path)
    parser.add_argument('--output', type=Path, help='Exclusive-create compact receipt JSON')
    args = parser.parse_args()
    word_bytes = (args.repo / 'research/p104-rounded-collector/inputs/WORD.json').read_bytes()
    completion_bytes = (args.repo / 'research/p104-omitted-completion/CERTIFICATE.json').read_bytes()
    need(hashlib.sha256(word_bytes).hexdigest() == WORD_PIN, 'frozen WORD hash')
    need(hashlib.sha256(completion_bytes).hexdigest() == COMPLETION_PIN, 'frozen completion hash')
    records = json.loads(args.recipes.read_bytes())
    need(type(records) is dict and set(records) == {'schema_version', 'x_to_empty', 'empty_to_full'}
         and type(records['schema_version']) is int and records['schema_version'] == 1,
         'serialized NATIVE object schema')
    operations = json.loads(args.program.read_bytes()) if args.program else None
    if type(operations) is dict:
        need(type(operations.get('schema_version')) is int and operations['schema_version'] == 1
             and set(operations) == {'schema_version', 'program', 'retained_original_event_indices'},
             'serialized PROGRAM object schema')
        operations = operations['program']
    result = verify_physical(json.loads(word_bytes), json.loads(completion_bytes),
                             records['x_to_empty'], records['empty_to_full'], program=operations)
    encoded = json.dumps(result['receipt'], indent=2, sort_keys=True) + '\n'
    if args.output:
        with args.output.open('x') as output:
            output.write(encoded)
    print(encoded, end='')
