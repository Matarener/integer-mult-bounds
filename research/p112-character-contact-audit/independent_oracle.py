#!/usr/bin/env python3
"""Independent free noncommutative group-ring dirty-helper oracle.

No primary phase checker, original geometry checker, or source artifacts are
imported. Chronological column routing is over Z[free(P,Q,L,S,T)].
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def reduced(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def plus(left, right):
    answer = dict(left)
    for word, coefficient in right.items():
        answer[word] = answer.get(word, 0) + coefficient
        if answer[word] == 0:
            del answer[word]
    return answer


def scale(integer, value):
    return {word: integer * coefficient for word, coefficient in value.items() if integer * coefficient}


def times(left, right):
    answer = {}
    for a, x in left.items():
        for b, y in right.items():
            word = reduced(a + b)
            answer[word] = answer.get(word, 0) + x * y
            if answer[word] == 0:
                del answer[word]
    return answer


def inverse_group_word(word):
    return tuple(-letter for letter in reversed(word))


def mono(*letters):
    return {reduced(letters): 1}


I, Z = mono(), {}
P, Q, L, S, T = 1, 2, 3, 4, 5


def start():
    return [[dict(I if register == column else Z) for column in range(3)]
            for register in range(3)]


def transport(registers, target, operator):
    registers[target] = [times(operator, value) for value in registers[target]]


def add(registers, target, source, integer):
    registers[target] = [plus(a, scale(integer, b))
                         for a, b in zip(registers[target], registers[source])]


def helper(sign, fault=None):
    registers = start()
    if fault != 'omit_precompensation':
        add(registers, 1, 2, -sign)
    transport(registers, 0, mono(L, -P))
    transport(registers, 1, mono(L, -Q))
    transport(registers, 2, mono(L, -Q))
    add(registers, 2, 0, 1)
    add(registers, 1, 2, -sign if fault == 'wrong_delivery_sign' else sign)
    add(registers, 2, 0, -1)
    if fault == 'wrong_return_order':
        transport(registers, 2, mono(-L, Q))
    elif fault != 'omit_helper_return':
        operator = mono(Q, -L)
        if fault == 'helper_return_global_minus_phase':
            operator = scale(-1, operator)
        transport(registers, 2, operator)
    transport(registers, 0, mono(S, -L))
    transport(registers, 1, mono(T, -L))
    return registers


def expected(sign):
    return [[mono(S, -P), {}, {}],
            [scale(sign, mono(T, -P)), mono(T, -Q), {}],
            [{}, {}, I]]


def direct(sign, common_entrance=True):
    registers = start()
    add(registers, 1, 0, sign)
    transport(registers, 0, mono(S, -P))
    transport(registers, 1, mono(T, -P if common_entrance else -Q))
    return registers


def serialize(matrix):
    return [[[[coefficient, list(word)] for word, coefficient in sorted(value.items())]
             for value in row] for row in matrix]


def mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2))
                 for i in range(2))


def inverse(a):
    determinant = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    need(determinant != 0, 'singular numeric frame')
    return ((a[1][1] / determinant, -a[0][1] / determinant),
            (-a[1][0] / determinant, a[0][0] / determinant))


def mv(a, x):
    return tuple(sum(a[i][j] * x[j] for j in range(2)) for i in range(2))


def va(x, y, sign=1):
    return tuple(a + sign * b for a, b in zip(x, y))


def numeric_helper(raw, frames, sign, wrong_order=False):
    # Independent literal vector execution, without evaluating free-ring forms.
    p, q, l, s, t = frames
    x, y, h = raw
    y = va(y, h, -sign)
    x = mv(mm(l, inverse(p)), x)
    y = mv(mm(l, inverse(q)), y)
    h = mv(mm(l, inverse(q)), h)
    h = va(h, x)
    y = va(y, h, sign)
    h = va(h, x, -1)
    h = mv(mm(inverse(l), q) if wrong_order else mm(q, inverse(l)), h)
    x = mv(mm(s, inverse(l)), x)
    y = mv(mm(t, inverse(l)), y)
    return x, y, h


def numeric_expected(raw, frames, sign):
    p, q, _, s, t = frames
    x, y, h = raw
    return (mv(mm(s, inverse(p)), x),
            va(mv(mm(t, inverse(q)), y), mv(mm(t, inverse(p)), x), sign), h)


def numeric_direct(raw, frames, sign):
    p, q, _, s, t = frames
    x, y, h = raw
    y = va(y, x, sign)
    return mv(mm(s, inverse(p)), x), mv(mm(t, inverse(q)), y), h


def numeric_controls():
    frames = tuple(tuple(tuple(F(v) for v in row) for row in matrix) for matrix in (
        ((1, 1), (0, 1)), ((1, 0), (1, 1)), ((2, 1), (1, 1)),
        ((0, -1), (1, 0)), ((1, 2), (1, 3))))
    need(mm(frames[1], frames[2]) != mm(frames[2], frames[1]), 'numeric Q/L commute unexpectedly')
    scalar_frames = tuple(((F(v), F(0)), (F(0), F(v))) for v in (2, 3, 5, 7, 11))
    inputs = []
    for column in range(6):
        bits = tuple(F(int(i == column)) for i in range(6))
        inputs.append((bits[:2], bits[2:4], bits[4:]))
    inputs.append(((F(2), F(-3)), (F(5), F(7)), (F(-11), F(13))))
    counts = {'correct_noncommuting_basis_and_dirty_cases': 0,
              'wrong_order_noncommuting_failures': 0,
              'wrong_order_scalar_only_cases_that_pass': 0,
              'direct_common_entrance_cases': 0,
              'direct_mismatched_entrance_failures': 0}
    witness = None
    for sign in (-1, 1):
        for raw in inputs:
            want = numeric_expected(raw, frames, sign)
            need(numeric_helper(raw, frames, sign) == want, 'noncommuting literal helper identity failed')
            counts['correct_noncommuting_basis_and_dirty_cases'] += 1
            wrong = numeric_helper(raw, frames, sign, wrong_order=True)
            if wrong != want:
                counts['wrong_order_noncommuting_failures'] += 1
                if witness is None:
                    witness = {'sign': sign, 'raw': raw, 'wrong': wrong, 'expected': want}
            need(numeric_helper(raw, scalar_frames, sign, wrong_order=True)
                 == numeric_expected(raw, scalar_frames, sign), 'wrong-order scalar blindness control failed')
            counts['wrong_order_scalar_only_cases_that_pass'] += 1
            common = (frames[0], frames[0], *frames[2:])
            need(numeric_direct(raw, common, sign) == numeric_expected(raw, common, sign), 'direct common-frame identity failed')
            counts['direct_common_entrance_cases'] += 1
            if numeric_direct(raw, frames, sign) != want:
                counts['direct_mismatched_entrance_failures'] += 1
    need(counts['wrong_order_noncommuting_failures'] > 0 and counts['direct_mismatched_entrance_failures'] > 0,
         'numeric premise controls did not discriminate')
    return {'frames_P_Q_L_S_T': frames, 'counts': counts, 'wrong_order_witness': witness,
            'basis_checks_prove_this_numeric_linear_instance_for_all_raw_inputs': True,
            'scalar_only_testing_would_miss_wrong_order': True}


def run():
    # Mechanical normalizer controls are not themselves proof-kernel checks.
    need(reduced((P, -P)) == () and reduced((P, Q, -Q, -P)) == (), 'adjacent inverse normalization failed')
    need(reduced((P, Q, -P, -Q)) != (), 'normalizer incorrectly commuted free letters')
    need(inverse_group_word((P, Q, -L)) == (L, -Q, -P), 'inverse order normalizer failed')
    fault_names = ('wrong_return_order', 'omit_helper_return', 'omit_precompensation',
                   'wrong_delivery_sign', 'helper_return_global_minus_phase')
    rows = []
    for sign in (-1, 1):
        want = expected(sign)
        need(helper(sign) == want, 'universal noncommuting helper normal form failed')
        direct_want = [[mono(S, -P), {}, {}],
                       [scale(sign, mono(T, -P)), mono(T, -P), {}], [{}, {}, I]]
        need(direct(sign) == direct_want, 'direct same-entrance normal form failed')
        need(direct(sign, common_entrance=False) != want, 'direct unequal-entrance control was not detected')
        faults = {}
        for name in fault_names:
            wrong = helper(sign, name)
            need(wrong != want, 'fault escaped free-group oracle: ' + name)
            faults[name] = serialize(wrong)
        rows.append({'sign': sign, 'helper_endpoint': serialize(want),
                     'direct_endpoint_with_P_equals_Q': serialize(direct_want),
                     'detected_faults': faults})
    return {'status': 'PASS_FREE_NONCOMMUTATIVE_DIRTY_HELPER_IDENTITY',
            'ring': 'Z[free group on P,Q,L,S,T]; only adjacent inverse cancellation',
            'generator_order': ['P', 'Q', 'L', 'S', 'T'], 'signs': rows,
            'symbolic_wrong_programs_detected': 2 * len(fault_names),
            'numeric': numeric_controls(),
            'scope': 'Universal abstract linear-frame dirty-helper identity plus one exact GL2(Q) instantiation; direct case requires P=Q.',
            'limits': ['Mechanical free-word normalization is not a formal proof-kernel certificate.',
                       'No source P112 frame/phase binding, full port/circuit endpoint or physical invoice.',
                       'No native compiler, supplier/multiplication theorem or new kappa.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True, default=str) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(json.dumps({'status': result['status'], 'symbolic_wrong_programs_detected': result['symbolic_wrong_programs_detected'],
                      'numeric_counts': result['numeric']['counts']}, sort_keys=True))


if __name__ == '__main__':
    main()
