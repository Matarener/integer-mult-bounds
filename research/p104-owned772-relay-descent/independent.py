#!/usr/bin/env python3
"""Independent finite P104 relay check: binary elimination and integer dyadic rows.

The opcode/interface contract is the retained PR5827/PR6030 contract. This
implementation imports no predecessor replay, native or pricing routines.
It checks scalar/formal-coordinate identities, not the native Clifford lift.
Owned CLEAR is the inherited erasure operation; it need not erase a zero row.
Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def echelon(vectors):
    pivots = {}
    for value in vectors:
        check(type(value) is int and 0 < value < 512, 'binary frame vector')
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
        check(value != 0, 'linearly independent frame basis')
    return pivots


def contains(big, small):
    for value in small.values():
        while value:
            bit = value.bit_length() - 1
            if bit not in big:
                return False
            value ^= big[bit]
    return True


def reduce_row(row, exponent):
    row = {k: v for k, v in row.items() if v}
    if not row:
        return {}, 0
    if exponent:
        common = min((abs(v) & -abs(v)).bit_length() - 1 for v in row.values())
        shift = min(common, exponent)
        if shift:
            return {k: v >> shift for k, v in row.items()}, exponent - shift
    return row, exponent


def scaled_row(state, numerator, denominator_exp):
    row, exponent = state
    return reduce_row({k: v * numerator for k, v in row.items()}, exponent + denominator_exp)


def accumulated_row(left, right, numerator, denominator_exp):
    lr, le = left
    rr, re = right
    exponent = max(le, re + denominator_exp)
    out = {k: v << (exponent - le) for k, v in lr.items()}
    shift = exponent - re - denominator_exp
    for k, v in rr.items():
        out[k] = out.get(k, 0) + ((v * numerator) << shift)
    return reduce_row(out, exponent)


def replay(word):
    n, m = word['public'], word['owned_fields']
    check(type(n) is int and 767 <= n <= 770, 'public inventory')
    check(type(m) is int and 8 <= m <= 29, 'owned inventory')
    check(len(word['initial']) == len(word['final']) == n, 'boundary dimensions')
    check(len(word['program']) < 26000, 'retained event cap')
    frames = [echelon(v) for v in word['frames']]
    frame_count = len(frames)
    check(all(type(f) is int and 0 <= f < frame_count for f in word['initial'] + word['final']), 'boundary frame indices')
    rows = [({i: 1}, 0) for i in range(n + m)]
    at = list(word['initial']) + [None] * m
    allocated = set()
    paid, operations = Counter(), Counter()
    lifetimes = peak = scalar = 0
    for i, event in enumerate(word['program']):
        check(isinstance(event, list) and len(event) >= 2, f'event form at {i}')
        kind, target = event[:2]
        check(type(target) is int and 0 <= target < n + m, f'target at {i}')
        operations[kind] += 1
        if kind == 'MOVE':
            check(len(event) == 5, f'MOVE arity at {i}')
            old, new, private = event[2:]
            check(type(old) is int and type(new) is int and 0 <= old < frame_count and 0 <= new < frame_count, f'MOVE frame index at {i}')
            check(type(private) is bool and private == (target in allocated), f'MOVE ownership at {i}')
            check(at[target] == old, f'MOVE source chart at {i}')
            lower, upper = (new, old) if private else (old, new)
            check(len(frames[lower]) < len(frames[upper]) and contains(frames[upper], frames[lower]), f'MOVE strict nesting at {i}')
            paid[len(frames[upper]) - len(frames[lower])] += 1
            at[target] = new
        elif kind == 'INIT':
            check(len(event) == 3 and type(event[2]) is int and 0 <= event[2] < frame_count, f'INIT form at {i}')
            check(target >= n and target not in allocated and at[target] is None, f'INIT ownership at {i}')
            allocated.add(target)
            rows[target] = ({}, 0)
            at[target] = event[2]
            lifetimes += 1
            peak = max(peak, len(allocated))
            scalar += 2
        elif kind == 'CLEAR':
            check(len(event) == 3 and target in allocated and at[target] == event[2], f'CLEAR ownership/chart at {i}')
            allocated.remove(target)
            rows[target] = ({}, 0)
            at[target] = None
            scalar += 2
        else:
            check(kind in ('ADD', 'COPY', 'SCALE'), f'known opcode at {i}')
            check(len(event) == (4 if kind == 'SCALE' else 5), f'scalar arity at {i}')
            coefficient = Fraction(event[-2])
            num, den = coefficient.numerator, coefficient.denominator
            check(num != 0 and den & (den - 1) == 0 and abs(coefficient) + 1 < 2**16, f'dyadic bounded scalar at {i}')
            check(type(event[-1]) is int and at[target] == event[-1] and at[target] is not None, f'scalar target chart at {i}')
            exp = den.bit_length() - 1
            if kind == 'SCALE':
                check(abs(num) & (abs(num) - 1) == 0, f'dyadic unit SCALE at {i}')
                rows[target] = scaled_row(rows[target], num, exp)
                scalar += 2 * (abs(abs(num).bit_length() - den.bit_length()) + int(num < 0))
            else:
                source = event[2]
                check(type(source) is int and 0 <= source < n + m and source != target, f'scalar source role at {i}')
                check(at[source] == at[target], f'common chart at {i}')
                if kind == 'COPY':
                    check(target in allocated and not rows[target][0], f'COPY cleared owned destination at {i}')
                    rows[target] = scaled_row(rows[source], num, exp)
                else:
                    rows[target] = accumulated_row(rows[target], rows[source], num, exp)
                scalar += 2 * (3 + abs(num).bit_length() - 1 + abs(num).bit_count() + exp)
    check(not allocated and 0 < peak <= 13 and at[:n] == word['final'], 'complete return/storage contract')
    live = set(word['live'])
    check(len(live) == len(word['live']) == len(word['ports']) == 104 and all(type(r) is int and 0 <= r < 112 for r in live), 'main input inventory')
    main = live | {r + 112 for r in live}
    check(len(main) == 208, 'disjoint main roles')
    for target, row in enumerate(rows):
        expected = {target: 1} if target < n else {}
        if target - 112 in live:
            expected[target - 112] = 1
        check(row == (expected, 0), f'arbitrary-input endpoint row {target}')
    helpers = Counter()
    for r in range(n):
        if r not in main:
            a, b = frames[word['initial'][r]], frames[word['final'][r]]
            check(len(a) < len(b) and contains(b, a), f'helper {r} endpoint inclusion')
            helpers[len(b) - len(a)] += 1
    whole_paid = Counter({r: 18 * count for r, count in paid.items()})
    whole_targets = Counter({r: 18 * count for r, count in helpers.items()})
    whole_paid[1] += 1560
    whole_targets[145] += 208
    for length in (7, 8):
        for position in range(1, length + 1):
            whole_paid[8 * (position + 1)] += 208
            whole_targets[8 * (position + 1) + 1] += 208
    ordered = lambda counter: {str(k): v for k, v in sorted(counter.items())}
    return {
        'events': len(word['program']), 'operations': dict(sorted(operations.items())),
        'rows_checked': n + m, 'endpoint_coefficients': (n + m)**2,
        'public': n, 'owned_fields': m, 'owned_lifetimes': lifetimes,
        'peak_owned': peak, 'real_scalar_allowance': scalar,
        'local_paid': ordered(paid), 'local_helpers': ordered(helpers),
        'whole_paid': ordered(whole_paid), 'whole_targets': ordered(whole_targets),
        'paid_calls': sum(whole_paid.values()), 'productive_fields': sum(whole_targets.values()),
        'paid_rank_mass': sum(k * v for k, v in whole_paid.items()),
        'target_rank_mass': sum(k * v for k, v in whole_targets.items()),
    }


def audit(base, candidate, controls=True):
    old, new = replay(base), replay(candidate)
    check(base.keys() == candidate.keys(), 'same word schema fields')
    check(all(base[k] == candidate[k] for k in base if k != 'program'), 'unchanged boundary and frame metadata')
    delta = {k: new['local_paid'].get(k, 0) - old['local_paid'].get(k, 0) for k in set(new['local_paid']) | set(old['local_paid'])}
    delta = {k: v for k, v in delta.items() if v}
    check(delta == {'1': -1, '6': -1, '7': 1}, f'exact local paid delta: {delta}')
    check(new['whole_targets'] == old['whole_targets'], 'unchanged complete target profile')
    check(new['target_rank_mass'] - new['paid_rank_mass'] == 760, 'retained rank mass surplus')
    references_791 = [(i, e) for i, e in enumerate(candidate['program'])
                      if e[1] == 791 or (e[0] in ('ADD', 'COPY') and e[2] == 791)]
    check([e[0] for _, e in references_791] == ['INIT', 'COPY', 'ADD', 'COPY', 'CLEAR'],
          'complete retained owned-791 use sequence')
    check(references_791[-2][1] == ['COPY', 770, 791, '1', 549]
          and references_791[-1][0] == references_791[-2][0] + 1,
          'early owned-791 erasure immediately follows its final use')
    result = {'base': old, 'candidate': new, 'local_paid_delta': delta,
              'owned791_references': references_791}
    if controls:
        faults = {}
        def reject(label, changed):
            try:
                replay(changed)
            except (ValueError, ZeroDivisionError) as error:
                faults[label] = str(error)
            else:
                raise ValueError('Accepted negative control: ' + label)
        # Select the newly inserted public-input compensation without relying on
        # event indices or a generator's declarations.
        old_events = Counter(tuple(e) for e in base['program'])
        new_events = Counter(tuple(e) for e in candidate['program']) - old_events
        compensations = {e for e in new_events if e[0] == 'ADD' and e[2] == 731 and e[-1] == 3}
        check(compensations, 'new arbitrary-input compensation exists')
        position = next(i for i, e in enumerate(candidate['program']) if tuple(e) in compensations)
        word = deepcopy(candidate); del word['program'][position]; reject('omit_arbitrary_input_compensation', word)
        word = deepcopy(candidate); word['program'][position][-2] = str(-Fraction(word['program'][position][-2])); reject('reverse_compensation_sign', word)
        position = next(i for i, e in enumerate(candidate['program']) if e[0] == 'MOVE' and e[1] == 772)
        word = deepcopy(candidate); word['program'][position][-1] = False; reject('borrow_owned_move', word)
        word = deepcopy(candidate); word['program'][position][2] = 3; reject('wrong_move_source_chart', word)
        position = next(i for i, e in enumerate(candidate['program']) if e[0] == 'CLEAR' and e[1] == 772)
        word = deepcopy(candidate); del word['program'][position]; reject('omit_owned_return', word)
        position = next(i for i, e in enumerate(candidate['program']) if e[0] == 'COPY' and e[1] == 772)
        word = deepcopy(candidate); word['program'].insert(position, ['ADD', 772, word['program'][position][2], '1', word['program'][position][-1]]); reject('copy_into_dirty_owned', word)
        position = next(i for i, e in enumerate(candidate['program']) if e[0] == 'SCALE' and e[1] == 772)
        word = deepcopy(candidate); word['program'][position][-2] = '1/3'; reject('non_dyadic_scale', word)
        word = deepcopy(candidate); word['program'][position][-2] = '3/2'; reject('nonunit_scale', word)
        word = deepcopy(candidate); word['frames'][595].append(word['frames'][595][0]); reject('dependent_frame_basis', word)
        clear791 = references_791[-1][0]
        word = deepcopy(candidate)
        word['program'][clear791 - 1], word['program'][clear791] = word['program'][clear791], word['program'][clear791 - 1]
        reject('clear791_before_last_read', word)
        position = next(i for i, e in enumerate(candidate['program']) if e == ['ADD', 162, 146, '-1', 529])
        word = deepcopy(candidate); del word['program'][position]; reject('omit_top162_compensation', word)
        word = deepcopy(candidate)
        held = word['program'].pop(clear791)
        late = next(i for i, e in enumerate(word['program']) if e[0] == 'CLEAR' and e[1] == 772)
        word['program'].insert(late + 1, held)
        reject('hold791_across772_lifetime', word)
        result['negative_controls'] = faults
    return result


def new_summary(result):
    candidate = result['candidate']
    return {'rows': candidate['rows_checked'], 'paid_calls': candidate['paid_calls'], 'negative_controls': len(result['negative_controls'])}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('base', nargs='?', default=str(Path(__file__).resolve().parent / 'inputs/pr6143-WORD.json.gz'))
    parser.add_argument('candidate', nargs='?', default=str(Path(__file__).resolve().parent / 'WORD.json.gz'))
    parser.add_argument('--output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit(load(args.base), load(args.candidate))
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(raw)
    receipt = Path(__file__).resolve().parent / 'INDEPENDENT.json'
    if args.write:
        receipt.write_text(raw)
    else:
        check(receipt.read_text() == raw, 'exact independent receipt')
    print('PASS_INDEPENDENT_ROOT595_RELAY_AUDIT', new_summary(result))


if __name__ == '__main__':
    main()
