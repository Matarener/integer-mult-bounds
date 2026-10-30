"""Independent one-column replay and literal endpoint controls; standard library.
Prepared for JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
"""
from fractions import Fraction as F
import json
import verify as primary


def check(condition, message):
    if not condition:
        raise ValueError(message)


def independent_column(word):
    # A scalar input evaluation, with no sparse-row replay or span code reused.
    values = [F(int(r == 1)) for r in range(799)]
    charts = word['initial'][:] + [None] * 29
    checked = 0
    for slot in range(14851):
        frame = 3 if 7896 <= slot <= 14357 else 713 if 14418 <= slot <= 14850 else None
        if frame is not None:
            for role, chart in enumerate(charts):
                if chart == frame and role != 469:
                    check(values[role] == 0, 'Independent legal donor coordinate')
                    checked += 1
        if slot == 14357:
            check(values[469] == 0, 'Independent entry coordinate')
        if slot == 14418 or slot == 14850:
            check(values[469] == F(1, 2), 'Independent restored coordinate')
        if slot == 14850:
            break
        event = word['program'][slot]
        op, r = event[:2]
        if op == 'MOVE':
            check(charts[r] == event[2], 'Independent MOVE source')
            charts[r] = event[3]
        elif op == 'INIT':
            check(charts[r] is None, 'Independent INIT')
            values[r], charts[r] = F(0), event[2]
        elif op == 'CLEAR':
            check(charts[r] == event[2], 'Independent CLEAR')
            values[r], charts[r] = F(0), None
        elif op == 'SCALE':
            check(charts[r] == event[3], 'Independent SCALE chart')
            values[r] *= F(event[2])
        elif op in ('ADD', 'COPY'):
            check(charts[r] == charts[event[2]] == event[4], 'Independent ADD chart')
            if op == 'COPY':
                check(values[r] == 0, 'Independent COPY zero')
            values[r] += F(event[3]) * values[event[2]]
        else:
            raise ValueError('Unknown source operation')
    return checked


def literal_endpoint(operations, expected, donor=(0, 1), donor_chart=0):
    """Dense two-column receiver interpreter; ADD carries its donor version."""
    receiver, source, chart = [F(1), F(0)], list(map(F, donor)), 0
    for event in operations:
        if event[0] == 'SCALE':
            c = F(event[1])
            check(c != 0, 'Nonzero receiver multiplier')
            receiver = [c * x for x in receiver]
        elif event[0] == 'ADD':
            check(chart == donor_chart, 'Live donor chart')
            check(source == list(map(F, event[2])), 'Exact donor version')
            receiver = [x + F(event[1]) * y for x, y in zip(receiver, source)]
        elif event[0] == 'MOVE':
            check(chart == event[1], 'Receiver MOVE source')
            chart = event[2]
        else:
            raise ValueError('Unknown endpoint operation')
    check(chart == 1, 'Restored endpoint chart')
    check(receiver == list(map(F, expected)), 'Complete arbitrary-input restoration')
    return receiver


def rejected(callback, expected_error):
    try:
        callback()
    except ValueError as error:
        check(str(error) == expected_error, 'Expected rejection reason: ' + str(error))
    else:
        raise ValueError('Negative control was accepted')


def main():
    word = primary.load_word()
    visits = independent_column(word)
    good = [('SCALE', 2), ('ADD', 3, [0, 1]), ('MOVE', 0, 1)]
    check(literal_endpoint(good, [2, 3]) == [2, 3], 'Receiver recoding positive')
    # Delta=(1,3) is outside span{(0,1)}, but lambda=2 solves the affine problem.
    delta, donor = [F(1), F(3)], [F(0), F(1)]
    check(delta[0] != 0 and donor[0] == 0, 'Coordinate separates donor-only target')
    rejected(lambda: literal_endpoint([('SCALE', 0), ('MOVE', 0, 1)], [0, 0]),
             'Nonzero receiver multiplier')
    rejected(lambda: literal_endpoint(good, [2, 3], donor=(0, 2)), 'Exact donor version')
    rejected(lambda: literal_endpoint(good, [2, 3], donor_chart=1), 'Live donor chart')
    rejected(lambda: literal_endpoint(good, [2, 4]), 'Complete arbitrary-input restoration')
    rejected(lambda: literal_endpoint([('SCALE', 2), ('MOVE', 0, 1)], [2, 3]),
             'Complete arbitrary-input restoration')
    # Omitting the entry receiver from a generic span test loses valid recodings.
    check([2 * F(1), 3 * F(1)] == literal_endpoint(good, [2, 3]), 'Literal affine substitution')
    print(json.dumps({'status': 'PASS_INDEPENDENT_CONTROLS', 'legal_donor_slot_visits': visits,
                      'actual_input1_literal_replay': True, 'invertible_recoding_positive': True,
                      'zero_multiplier_rejected': True, 'wrong_donor_version_rejected': True,
                      'wrong_chart_rejected': True, 'changed_input_column_rejected': True,
                      'omitted_restoration_rejected': True}, sort_keys=True))


if __name__ == '__main__':
    main()
