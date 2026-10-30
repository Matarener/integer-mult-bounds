#!/usr/bin/env python3
"""Independent regular-action checks for the sharp orbit-call bound.

No compiler, historical geometry, or companion checker is imported.
Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


class AuditError(ValueError):
    pass


DISABLED = frozenset()


def need(value, guard):
    if not value and guard not in DISABLED:
        raise AuditError(guard)


def identity(size):
    return list(range(size))


def compose(left, right):
    return [left[index] for index in right]


def inverse(permutation):
    result = [0] * len(permutation)
    for index, value in enumerate(permutation):
        result[value] = index
    return result


def shift(address, axis, q, exponent=1):
    place = q ** axis
    old = address // place % q
    return address + ((old + exponent) % q - old) * place


def local(pairs, spectators, pair, q, x_inverse=False, all_common=False):
    fields, width = 6 * pairs + spectators, q ** 3
    result = identity(fields * width)
    for field in range(6 * pair, 6 * pair + 6):
        axis = (2, 0, 1)[field % 3]
        for address in range(width):
            value = address
            for selected in (range(3) if all_common else (axis,)):
                value = shift(value, selected, q,
                              q - 1 if x_inverse and selected == 0 else 1)
            result[field * width + address] = field * width + value
    return result


def port_cycle(pairs, spectators, pair, q):
    fields, width = 6 * pairs + spectators, q ** 3
    result = identity(fields * width)
    for field in range(6 * pair, 6 * pair + 6):
        target = 3 * (field // 3) + (field % 3 + 1) % 3
        for address in range(width):
            result[field * width + address] = target * width + address
    return result


def sharp_word(pairs, spectators, q, omit=None, wrong_cycle=False, x_inverse=False, reverse_order=False):
    size = (6 * pairs + spectators) * q ** 3
    answer, events, gates = identity(size), [], []
    for pair in range(pairs):
        p = port_cycle(pairs, spectators, pair, q)
        pp = compose(p, p)
        for step, adapter in enumerate((identity(size), p, pp)):
            if omit == (pair, step):
                continue
            if wrong_cycle and pair == 0 and step == 2:
                adapter = p
            d = local(pairs, spectators, pair, q,
                      x_inverse=x_inverse and pair == 0 and step == 0)
            gate = compose(adapter, compose(d, inverse(adapter)))
            gates.append(gate)
            events.append({'pair': pair, 'port_cycle_power': step,
                           'local_diagonal': ['z', 'x', 'y', 'z', 'x', 'y']})
    for gate in reversed(gates) if reverse_order else gates:
        answer = compose(gate, answer)
    return answer, events


def target(pairs, spectators, q):
    width = q ** 3
    result = identity((6 * pairs + spectators) * width)
    for field in range(6 * pairs):
        for address in range(width):
            value = address
            for axis in range(3):
                value = shift(value, axis, q)
            result[field * width + address] = field * width + value
    return result


def accept_endpoint(actual, pairs, spectators, q):
    need(actual == target(pairs, spectators, q), 'complete regular-action endpoint')


def columns(permutation):
    return [1 << row for row in permutation]


def linear_compose(left, right):
    result = []
    for value in right:
        out = 0
        while value:
            bit = value & -value
            out ^= left[bit.bit_length() - 1]
            value ^= bit
        result.append(out)
    return result


def field_add(cols, destination, source, width):
    mask = (1 << width) - 1
    return [value ^ (((value >> (width * source)) & mask) << (width * destination))
            for value in cols]


def accept_linear_endpoint(actual, pairs, spectators):
    need(actual == columns(target(pairs, spectators, 2)),
         'all public and arbitrary dirty spectator columns')


def rank2(rows):
    basis = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def derivative(cols, fields):
    # Read the coefficient at every C2^3 translation from the regular action
    # on address-zero inputs; then verify every other address column too.
    width, mask = 8, 255
    for source in range(fields):
        for address in range(width):
            expected = 0
            base = cols[source * width]
            while base:
                bit = base & -base
                index = bit.bit_length() - 1
                expected ^= 1 << (width * (index // width) + ((index % width) ^ address))
                base ^= bit
            need(cols[source * width + address] == expected, 'translation-module coefficient binding')
    ordinary, first = [0] * fields, [0] * fields
    for source in range(fields):
        base = cols[source * width]
        for destination in range(fields):
            terms = (base >> (width * destination)) & mask
            ordinary[destination] |= (terms.bit_count() & 1) << source
            first[destination] |= ((terms & 0b10101010).bit_count() & 1) << source
    return ordinary, first


def accept_local(cols, fields):
    ordinary, first = derivative(cols, fields)
    need(rank2(ordinary) == fields, 'local augmentation invertible')
    need(rank2(first) <= 2, 'charged local derivative rank at most two')


ZERO, ONE, IMAG = (F(0), F(0)), (F(1), F(0)), (F(0), F(1))


def gadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def gneg(a):
    return (-a[0], -a[1])


def gmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def ginv(a):
    norm = a[0] * a[0] + a[1] * a[1]
    return (a[0] / norm, -a[1] / norm)


def gmatrix(size):
    return [[ONE if row == col else ZERO for col in range(size)] for row in range(size)]


def gproduct(a, b):
    out = [[ZERO for _ in b[0]] for _ in a]
    for row in range(len(a)):
        for middle in range(len(b)):
            if a[row][middle] == ZERO:
                continue
            for col in range(len(b[0])):
                if b[middle][col] != ZERO:
                    out[row][col] = gadd(out[row][col], gmul(a[row][middle], b[middle][col]))
    return out


def grank(matrix):
    a = [list(row) for row in matrix]
    row = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(row, len(a)) if a[i][col] != ZERO), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        factor = ginv(a[row][col])
        a[row] = [gmul(value, factor) for value in a[row]]
        for i in range(len(a)):
            if i != row and a[i][col] != ZERO:
                scalar = a[i][col]
                a[i] = [gadd(x, gneg(gmul(scalar, y))) for x, y in zip(a[i], a[row])]
        row += 1
        if row == len(a):
            break
    return row


def difference(a, b):
    return [[gadd(x, gneg(y)) for x, y in zip(r, s)] for r, s in zip(a, b)]


def complex_eval(permutation, fields, vary):
    units = (ONE, IMAG, gneg(ONE), gneg(IMAG))
    out = [[ZERO for _ in range(fields)] for _ in range(fields)]
    for source in range(fields):
        destination = permutation[64 * source]
        out[destination // 64][source] = units[destination % 4] if vary else ONE
    return out


def accept_constant_bridge(a, b):
    need(a == b, 'free bridge is parameter independent')


def accept_covariance(o, x, y):
    inverse_o = gproduct(o, o)
    need(gproduct(o, gproduct(x, inverse_o)) == y, 'exact C3 source covariance')


def cover_record():
    o = [[ZERO, ZERO, ONE], [ONE, ZERO, ZERO], [ZERO, ONE, ZERO]]
    need(gproduct(o, gproduct(o, o)) == gmatrix(3), 'cover rotation order three')
    generators = []
    for axis in range(3):
        matrix = gmatrix(3)
        matrix[axis][axis] = IMAG
        generators.append(matrix)
    for axis in range(3):
        accept_covariance(o, generators[axis], generators[(axis + 1) % 3])
        need(gproduct(gproduct(generators[axis], generators[axis]),
                      gproduct(generators[axis], generators[axis])) == gmatrix(3),
             'C4 cover generator relation')
    product = gproduct(generators[0], gproduct(generators[1], generators[2]))
    need(product == [[IMAG if i == j else ZERO for j in range(3)] for i in range(3)],
         'xyz is i times cover identity')
    # The identical cyclic conjugation also permutes the three derivative
    # projectors over F2. Coefficient 2 vanishes, so (I+eE)^2=I.
    projectors = [[(1 << i) if i == axis else 0 for i in range(3)] for axis in range(3)]
    for axis in range(3):
        e = [[ONE if row == col == axis else ZERO for col in range(3)] for row in range(3)]
        following = [[ONE if row == col == (axis + 1) % 3 else ZERO
                      for col in range(3)] for row in range(3)]
        accept_covariance(o, e, following)
    need(all(rank2(e) == 1 for e in projectors), 'dual cover variation projectors')
    need(rank2([projectors[0][i] ^ projectors[1][i] ^ projectors[2][i]
                for i in range(3)]) == 3, 'dual cover target variation')
    return o, generators, {'complex_generator_variation_ranks': [grank(difference(x, gmatrix(3))) for x in generators],
                           'complex_target_variation_rank': grank(difference(product, gmatrix(3))),
                           'BIT_derivative_projectors': projectors,
                           'two_bank_local_cover_rank': 6,
                           'target_cover_rank_per_bank_pair': 18,
                           'cover_meaning': 'three-dimensional regular C3 cover, not a faithful representation of the entire semidirect group algebra'}


def rejected(name, action, guard):
    global DISABLED
    try:
        action()
    except AuditError as error:
        need(str(error) == guard, 'wrong rejection: ' + name)
    else:
        raise AuditError('mutation survived: ' + name)
    prior = DISABLED
    try:
        DISABLED = prior | {guard}
        action()
    finally:
        DISABLED = prior
    return {'name': name, 'intended_guard': guard, 'same_guard_deletion': 'ACCEPTED'}


def controls():
    out = []
    for label, kwargs in [('omitted local call', {'omit': (0, 2)}),
                           ('wrong cyclic port conjugation', {'wrong_cycle': True})]:
        bad, _ = sharp_word(1, 1, 2, **kwargs)
        out.append(rejected(label, lambda bad=bad: accept_endpoint(bad, 1, 1, 2),
                            'complete regular-action endpoint'))
    good = columns(target(1, 1, 2))
    dirty_leak = field_add(good, 0, 6, 8)
    need(dirty_leak[:48] == good[:48], 'clean spectator restriction misses dirt leak')
    out.append(rejected('dirty spectator leaks into public output',
                        lambda: accept_linear_endpoint(dirty_leak, 1, 1),
                        'all public and arbitrary dirty spectator columns'))
    private_residual = field_add(good, 6, 0, 8)
    out.append(rejected('spectator not returned literally',
                        lambda: accept_linear_endpoint(private_residual, 1, 1),
                        'all public and arbitrary dirty spectator columns'))
    forbidden = columns(local(1, 1, 0, 2, all_common=True))
    out.append(rejected('paid full common transform mislabeled one local call',
                        lambda: accept_local(forbidden, 7),
                        'charged local derivative rank at most two'))
    inverse_bit, _ = sharp_word(1, 1, 2, x_inverse=True)
    accept_endpoint(inverse_bit, 1, 1, 2)
    inverse_complex, _ = sharp_word(1, 1, 4, x_inverse=True)
    out.append(rejected('BIT inverse coincidence does not transfer to C4',
                        lambda: accept_endpoint(inverse_complex, 1, 1, 4),
                        'complete regular-action endpoint'))
    original = local(1, 1, 0, 4, all_common=True)
    out.append(rejected('parameter dependent transform mislabeled free bridge',
                        lambda: accept_constant_bridge(complex_eval(original, 7, False),
                                                       complex_eval(original, 7, True)),
                        'free bridge is parameter independent'))
    o, gs, _ = cover_record()
    out.append(rejected('source rotation with the one-character y specialization',
                        lambda: accept_covariance(o, gs[0], gmatrix(3)),
                        'exact C3 source covariance'))
    out.append(rejected('inverse cover rotation has wrong source covariance',
                        lambda: accept_covariance(gproduct(o, o), gs[0], gs[1]),
                        'exact C3 source covariance'))
    return out


def case(pairs, spectators):
    fields = 6 * pairs + spectators
    bit, events = sharp_word(pairs, spectators, 2)
    complex_word, complex_events = sharp_word(pairs, spectators, 4)
    accept_endpoint(bit, pairs, spectators, 2)
    accept_endpoint(complex_word, pairs, spectators, 4)
    for q in (2, 4):
        equivalent, _ = sharp_word(pairs, spectators, q, reverse_order=True)
        accept_endpoint(equivalent, pairs, spectators, q)
    need(events == complex_events and len(events) == 3 * pairs, 'exact sharp local call inventory')
    base, first = derivative(columns(bit), fields)
    need(rank2(base) == fields and rank2(first) == 6 * pairs, 'complete target derivative rank')
    generator = columns(local(pairs, spectators, 0, 2))
    accept_local(generator, fields)
    _, local_first = derivative(generator, fields)
    ce0, ce1 = complex_eval(complex_word, fields, False), complex_eval(complex_word, fields, True)
    complex_rank = grank(difference(ce1, ce0))
    local4 = local(pairs, spectators, 0, 4)
    local_rank = grank(difference(complex_eval(local4, fields, True), complex_eval(local4, fields, False)))
    need(complex_rank == 6 * pairs and local_rank == 2, 'complex two-evaluation ranks')
    mixed = None
    if spectators:
        s = field_add(columns(identity(fields * 8)), 1, 6 * pairs, 8)
        # This is an actual free invertible scalar bridge involving an
        # initially arbitrary spectator. In characteristic two S^-1=S.
        conjugate = linear_compose(s, linear_compose(generator, s))
        accept_local(conjugate, fields)
        m0, m1 = derivative(conjugate, fields)
        need(m1 != local_first, 'dirty spectator bridge changes the actual coefficient matrix')
        mixed = {'augmentation_rows': m0, 'derivative_rows': m1,
                 'derivative_rank': rank2(m1),
                 'complete_regular_columns': conjugate}
    return {'bank_pairs': pairs, 'data_rows': 6 * pairs, 'dirty_scalar_spectators': spectators,
            'local_calls': len(events), 'events': events,
            'BIT_complete_regular_operator_columns': bit,
            'C4_complete_regular_operator_columns': complex_word,
            'regular_input_columns': {'BIT': len(bit), 'C4': len(complex_word)},
            'target_augmentation_rows': base, 'target_derivative_rows': first,
            'target_derivative_rank': rank2(first), 'local_derivative_rows': local_first,
            'complex_target_difference_rank': complex_rank, 'complex_local_difference_rank': local_rank,
            'mixed_dirty_bridge_local': mixed,
            'cover_target_rank': 18 * pairs, 'cover_local_rank': 6,
            'all_spectator_input_columns_returned_identically': True,
            'reversed_product_positive_control': ['BIT', 'C4']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    need(args.output.is_absolute(), 'output must be absolute')
    need(not args.output.exists() and not args.output.is_symlink(), 'output must be new')
    need(not args.output.resolve().is_relative_to(Path(__file__).resolve().parent),
         'output must be external')
    cases = [case(b, h) for b in (1, 2, 4) for h in (0, 1, 3)]
    negative = controls()
    _, _, cover = cover_record()
    result = {'status': 'PASS_INDEPENDENT_SHARP_ORBIT_CALL_WITH_DIRTY_SPECTATORS',
              'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'cases': cases, 'cover': cover, 'controls': negative,
              'coverage': {'bank_pairs': [1, 2, 4], 'spectators': [0, 1, 3],
                           'cases': len(cases), 'BIT_regular_columns': sum(len(c['BIT_complete_regular_operator_columns']) for c in cases),
                           'C4_regular_columns': sum(len(c['C4_complete_regular_operator_columns']) for c in cases),
                           'semantic_rejections': len(negative), 'named_guard_deletions': len(negative),
                           'reversed_product_positive_controls': 2 * len(cases)},
              'scope': 'algebraic call grammar only; full literal spectator return, scalar invertible parameter-independent bridges; no native reduction, scan, source, precision, owner or recursive invoice admission',
              'source_rotation': 'scalar cyclic port permutation proves sharpness without renaming x,y,z; genuine source rotation uses the separate C3 regular cover',
              'no_new_kappa': True}
    with args.output.open('x') as destination:
        destination.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS independent sharp orbit call: 9 cases, 9 semantic rejections/deletions')


if __name__ == '__main__':
    main()
