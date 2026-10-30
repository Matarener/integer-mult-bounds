"""Source-program scalar ordering controls; no physical/frame verifier imported.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction


def scalar_controls(program, C, A):
    """Interpret all 1,238 operations on multiples of one normalized B9 vector u.

    Native operations preserve normalized coordinates and are skipped here.
    This does not assert native phase, physical width, or admission of other inputs.
    """
    def need(ok, message):
        if not ok:
            raise ValueError(message)

    basis = ('X0', 'X33', 'X101', 'X102', 'X11', 'X12', 'X15', 'X24')
    need(len(program) == 1238 and len(A) == 8 and len(C) == 52, 'source shape')
    first = next(i for i, op in enumerate(program) if op[0] == 'half')
    last = max(i for i, op in enumerate(program) if op[0] == 'double')
    need(first == 299 and last == 897, 'source phase boundaries')
    enter, pre = program[:52], program[52:first]
    gather, tail = program[first:last + 1], program[last + 1:]
    need(all(op[0] == 'native' for op in enter), 'initial native block')
    need(len(pre) == 247 and all(op[0] == 'add' for op in pre), 'precondition block')
    names = set(C) | {'Y' + str(i) for i in range(104)}
    names.update(op[1] for op in program)
    names.update(op[2] for op in program if op[0] == 'add')

    def execute(ops, initial):
        state = {b: Fraction(initial.get(b, 0)) for b in names}
        for op in ops:
            kind, target = op[:2]
            if kind == 'native':
                continue
            if kind == 'add':
                source, sign = op[2:]
                need(sign in (-1, 1), 'unit ADD required')
                state[target] += sign * state[source]
            else:
                need(kind in ('half', 'double'), 'unexpected scalar operation')
                state[target] *= Fraction(1, 2) if kind == 'half' else 2
            need(state[target].denominator == 1, 'witness lost scalar integrality')
        return state

    def expected(initial):
        out = {b: Fraction(initial.get(b, 0)) for b in names}
        delta = [sum(Fraction(v * initial.get(y, 0), 2) for y, v in row.items())
                 for row in A]
        for x, row in C.items():
            out[x] += sum(row[j] * delta[j] for j in range(8))
        return out

    need(C['X5'][basis.index('X11')] == 1, 'dirty witness source binding')
    need(sum(C['X5'][j] * A[j].get('Y3', 0) for j in range(8)) == -1,
         'signal witness source binding')
    fixtures = [('omit_precondition', {'X11': 1}, enter + gather + tail, 0, 1),
                ('late_precondition', {'Y3': 4}, enter + gather + pre + tail, -2, 0)]
    controls = []
    for label, initial, mutated, target_expected, target_observed in fixtures:
        want = expected(initial)
        good, bad = execute(program, initial), execute(mutated, initial)
        need(good == want, label + ': original program failed full-bank oracle')
        need(bad != want, label + ': mutation was not detected by its output')
        need(want['X5'] == target_expected and bad['X5'] == target_observed,
             label + ': exact X5 witness differs')
        need(all(bad[y] == want[y] for y in names if y.startswith('Y')),
             label + ': source-return confounder')
        differences = [{'bank': b, 'expected_multiple_of_u': str(want[b]),
                        'observed_multiple_of_u': str(bad[b])}
                       for b in sorted(names) if bad[b] != want[b]]
        controls.append({'control': label, 'status': 'REJECTED_BY_OUTPUT',
                         'input_multiples_of_u': initial,
                         'executed_program_operations': len(mutated),
                         'differing_banks': differences, 'all_Y_restored': True})
    return {'status': 'PASS', 'original_program_operations': len(program),
            'compared_banks': len(names), 'precondition_ADDs': len(pre),
            'oracle': 'X_initial + C*A*Y_initial/2; all other banks unchanged',
            'interpretation': 'Normalized multiples of one B9 vector u; native charts omitted',
            'original_full_bank_oracle_matches': 2, 'controls': controls}
