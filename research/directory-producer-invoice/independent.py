#!/usr/bin/env python3
"""Closed action-count certificate; no predecessor/primary executable imports.

Costs are (reads,writes,unit_moves), derived from the exact methods in the
frozen source.  This is an external mathematical oracle, not runtime control.
Apache-2.0. ToikY with substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {
    'cardinality.py': '505d5e560c5a507e6184edcc19a87cf1fed243eb34a5cb21fbe1e4fe017e7f22',
    'counts.py': '00b476dbda0e8cc99886bf794439e1cb9e775f435f599a3557e99321fe084069',
    'directory.py': '4270e370b2bfe38ef73aadcd97d1b3496b56bd582115d74331eb9e5ceb90bec7',
    'records.py': '0c9c4b23e998597fb877bb1a29da69ac869b68262abe635b162b4dba9c69b372',
    'stream.py': 'c7dc7da5b00f27016982ada4c0416f8328568b00df16d97012f33d4b372d79b5',
    'words.py': '5c37f57708ba3131bdcb03139f9dbc29886bee44569c09cbba51b68f75acd7f9',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(*values):
    return tuple(sum(x[i] for x in values) for i in range(3))


def mul(n, value):
    return tuple(n * x for x in value)


def pop(n):
    return bin(n).count('1')


def record(cost):
    return dict(zip(('reads', 'writes', 'moves'), cost))


def unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, 'duplicate JSON key')
        value[key] = item
    return value


def rewind(head):
    return head, 0, head + 1


def clear(symbols):
    """A valid Tape at head1; backing capacity is not silently shrunk."""
    return 2 * symbols + 3, symbols, 2 * symbols + 4


def word_zero(L):
    return 4 * L + 5, L + 1, 4 * L + 6


def word_free(L):
    return 2 * L + 3, L + 1, 2 * L + 4


def word_literal(L, n):
    k = n.bit_length()
    need(k <= L, 'literal extent')
    return add(word_zero(L), (2 * k + 1, k, 2 * k + 2))


def word_copy(L):
    return add(word_zero(L), (4 * L + 4, L, 4 * L + 6))


def word_zero_test(L):
    return 2 * L + 3, 0, 2 * L + 4


def word_msb(L):
    return L + 2, 0, L + 3


def compare(L):
    return 5 * L + 6, 0, 4 * L + 8


def shift(L):
    return add(word_zero(L), (4 * L + 4, L, 4 * L + 6))


def subtract(L):
    return add(word_zero(L), (6 * L + 7, L, 6 * L + 10))


def divide(L, numerator, denominator):
    """Exact Unsigned.divmod cost; quotient 1-bits select subtraction paths."""
    need(0 < denominator < 1 << (L - 1), 'divisor high-bit margin')
    quotient = numerator // denominator
    return add(
        word_zero_test(L), word_msb(L), (1, 0, 0), rewind(L),
        word_copy(L), mul(2, word_zero(L)), mul(2, word_msb(L)),
        (2 * L + 1, 0, 0),
        mul(L, add(shift(L), word_free(L), compare(L), (0, 1, 2))),
        mul(pop(quotient), add(subtract(L), word_free(L))),
        (0, 0, 2), word_free(L))


def radix_word_cost(q, modulus, L):
    """One full radix_power traversal, including validation and final frees."""
    need(q >= 2 and modulus > 1, 'radix domain')
    value, exponent = modulus, 0
    cost = add(word_literal(L, q), word_copy(L))
    while value > 1:
        quotient, remainder = divmod(value, q)
        need(remainder == 0 and quotient > 0, 'source prime-power validation')
        cost = add(cost, compare(L), divide(L, value, q),
                   mul(2, word_zero_test(L)), mul(2, word_free(L)))
        value, exponent = quotient, exponent + 1
    cost = add(cost, mul(2, compare(L)), mul(2, word_free(L)))
    return cost, exponent


def countdown(n):
    """All Counter.decrement calls from n through0; construction/close separate."""
    if n == 0:
        return 0, 0, 0
    trailing_sum, extensions = n - pop(n), n.bit_length() - 1
    return (2 * trailing_sum + 5 * n + 1,
            trailing_sum + n + 2 * extensions + 3,
            2 * trailing_sum + 4 * n + 2 * extensions + 4)


def counter_constructor(width, value):
    """Return own Tape cost and separate source Tape/Word cost."""
    need(0 <= value < 1 << width, 'counter input extent')
    k = value.bit_length()
    if value:
        own = (2 * width + 3, width + 1 + 2 * (width - k),
               4 * width - 2 * k + 4)
    else:
        own = 2 * width + 5, 3 * width + 3, 4 * width + 8
    source = 3 * width + 3, 0, 2 * width + 4
    return own, source


def count_increments(n):
    """All Count.increment calls from0 ton, including new RIGHT delimiters."""
    if n == 0:
        return 0, 0, 0
    trailing_sum, extensions = n - pop(n), n.bit_length() - 1
    return (2 * trailing_sum + 5 * n,
            trailing_sum + n + extensions,
            2 * trailing_sum + 4 * n + 2 * extensions)


def count_multiply_chain(value, q, repetitions):
    cost = (0, 0, 0)
    for _ in range(repetitions):
        old_width = value.bit_length()
        value *= q
        new_width = value.bit_length()
        cost = add(cost, (2 * old_width + new_width + 2,
                          new_width + 1, 2 * new_width + 2))
    return value, cost


def invoice(*, d, q, modulus, L, I, Q, h, B, shared=False):
    """Exact successful-produce counts from a valid already-live Context.

    L: residue Word width; I: old_fields Word width; Q: finite code bit width;
    h: fields/old prefix; B: physical old-prefix count. All entry heads are1.
    """
    need(all(type(x) is int for x in (d, q, modulus, L, I, Q, h, B)), 'typed parameters')
    need(type(shared) is bool, 'typed shared-traversal flag')
    need(d > 0 and L >= 2 and I >= 2 and Q > 0 and B > 0 and h >= 0, 'parameter domain')
    need(h < 1 << I and modulus < 1 << (L - 1), 'declared word margins')
    need(L == modulus.bit_length() + 1, 'canonical source Ring word width')
    radix_cost, w = radix_word_cost(q, modulus, L)
    M, c = d * d, modulus // q
    H, F = c ** M, Q + 2 + d * d * (L + 1)
    new_count = B * H
    n, old_symbols, output_symbols = h * F, B * h * F, B * H * (h + 1) * F
    increments = M if c == 1 else c * (H - 1) // (c - 1)
    carries = M if c == 1 else (H - 1) // (c - 1)
    trailing_sum = carries * (c - pop(c))

    # Numerical words: high_power; one-at-a-time decoded old words; odometer.
    decoded_word = (16 * L + 19, 3 * L + 2, 14 * L + 24)
    digit_increment = (4 * increments + 2 * trailing_sum,
                       increments + trailing_sum,
                       4 * increments + 2 * trailing_sum)
    odometer = add(digit_increment, mul(increments + carries, compare(L)),
                   mul(carries, (2 * L + 2, L, 2 * L + 2)))
    residue_parts = {
        'high_power_validation': mul(1 if shared else M, radix_cost),
        'old_decode_validate_save': mul(B * h * M, decoded_word),
        'odometer_allocate_erase': mul(B * M, add(word_zero(L), word_free(L))),
        'new_digit_serialization': mul(B * H * M, (3 * L + 3, 0, 2 * L + 4)),
        'odometer_advance': mul(B, odometer),
    }

    # Record Tape traffic: input, one saved prefix at a time, append-only output.
    tape_parts = {
        'old_input': (2 * old_symbols + B * h * M * L + 3, 0, 2 * old_symbols + 4),
        'saved_prefixes': mul(B, (4 * n + 4 + H * (3 * n + 3), 2 * n,
                                 4 * n + 6 + H * (2 * n + 4))),
        'output': (2 * output_symbols + 1, output_symbols, 2 * output_symbols + 2),
    }
    kB = B.bit_length()
    outer_own, outer_source = counter_constructor(kB, B)
    field_own, field_source = counter_constructor(I, h)
    # Count(old_count): source read and new positive Count normalization.
    expected_init = add((4 * kB + 6, kB + 1, 4 * kB + 6), outer_source)
    multiplied, multiply_cost = count_multiply_chain(B, q, M * (w - 1))
    need(multiplied == new_count, 'source high_power value')
    emitted_literal_zero = (30, 10, 36)
    kN = new_count.bit_length()
    equal = 6 * kN + 7, 0, 4 * kN + 8
    tape_parts['expected_count'] = add(expected_init, multiply_cost, equal)
    tape_parts['emitted_count'] = add(emitted_literal_zero, count_increments(new_count), clear(kN + 1))
    tape_parts['outer_counter'] = add(outer_own, outer_source, countdown(B), clear(2))
    tape_parts['field_counters'] = mul(B, add(field_own, countdown(h), clear(2)))
    return {
        'parameters': {'d': d, 'q': q, 'modulus': modulus, 'L': L, 'I': I, 'Q': Q, 'h': h, 'B': B},
        'geometry': {'M': M, 'c': c, 'H': H, 'F': F, 'new_count': new_count,
                     'old_symbols': old_symbols, 'output_symbols': output_symbols,
                     'digit_increments_per_prefix': increments, 'digit_carries_per_prefix': carries,
                     'digit_trailing_ones_sum_per_prefix': trailing_sum},
        'record_tapes': record(add(*tape_parts.values())),
        'residue_words': record(add(*residue_parts.values())),
        'index_words': record(mul(B, field_source)),
        'record_parts': {k: record(v) for k, v in tape_parts.items()},
        'residue_parts': {k: record(v) for k, v in residue_parts.items()},
        'additional_residue_peak': max(M, 6),
        'shared_radix': shared,
        'radix_word_cost': record(radix_cost),
        'saved_residue_actions': record(mul(M - 1, radix_cost)),
        'heads': {'old': 1, 'output': 1, 'expected_count': 1, 'old_count': 1, 'old_fields': 1},
    }


def small_odometer(M, c):
    """Independent integer-state enumeration for bounded corroboration only."""
    need(M <= 9 and c ** M <= 10000, 'bounded odometer control')
    state, visited = [0] * M, []
    increments = carries = trailing = 0
    while True:
        visited.append(tuple(state))
        for j in range(M - 1, -1, -1):
            old = state[j]
            while old & 1:
                trailing += 1
                old >>= 1
            state[j] += 1
            increments += 1
            if state[j] < c:
                break
            need(state[j] == c, 'integer carry')
            state[j] = 0
            carries += 1
        else:
            break
    return visited, increments, carries, trailing


def controls():
    for M in (1, 4, 9):
        for c in (1, 2, 3):
            if c ** M > 10000:
                continue
            visited, increments, carries, trailing = small_odometer(M, c)
            H = c ** M
            expected_carries = M if c == 1 else (H - 1) // (c - 1)
            need(len(visited) == len(set(visited)) == H, 'all high fields exactly once')
            need(increments == c * expected_carries and carries == expected_carries, 'carry sums')
            need(trailing == expected_carries * (c - pop(c)), 'ripple sum')
            need(visited[0] == (0,) * M and visited[-1] == (c - 1,) * M, 'lexical endpoints')
    need(countdown(1) == (6, 4, 8), 'final Counter zero representation')
    need(count_increments(1) == (5, 1, 4), 'first emitted increment')
    need(count_increments(2) == (12, 4, 12), 'emitted delimiter extension')
    # PR2590 owns the earlier exact write law; all three new closed lanes agree.
    for L in range(3, 8):
        for numerator in (1, (1 << (L - 1)) - 1):
            for denominator in (1, 2, 3):
                if denominator >= 1 << (L - 1):
                    continue
                s = pop(numerator // denominator)
                closed = (15 * L * L + 44 * L + 33 + (12 * L + 15) * s,
                          3 * L * L + 8 * L + 4 + (3 * L + 2) * s,
                          14 * L * L + 50 * L + 44 + (12 * L + 20) * s)
                need(divide(L, numerator, denominator) == closed, 'complete closed division invoice')
    return 'PASS_BOUNDED_ODOMETER_AND_COUNT_CONTROLS'


def fixture_bytes(parameters):
    """Independent direct base-c oracle for the bounded fixtures, not runtime."""
    d, L, Q, c, B, h = (parameters[k] for k in ('d', 'L', 'Q', 'c', 'B', 'h'))
    M, H = d * d, c ** (d * d)
    need(H <= 10000, 'bounded byte oracle; no nontrivial dimension64 high cube')
    def field(code, digits):
        value = bytearray((code >> i) & 1 for i in range(Q))
        value.append(5)
        for digit in digits:
            value.extend((digit >> i) & 1 for i in range(L))
            value.append(5)
        value.append(6)
        return value
    old, output = bytearray([2]), bytearray([2])
    for outer in range(B):
        prefix = bytearray()
        for level in range(h):
            prefix.extend(field((outer + level) % (1 << Q),
                                ((outer + level + j) % c for j in range(M))))
        old.extend(prefix)
        for rank in range(H):
            number, digits = rank, [0] * M
            for j in range(M - 1, -1, -1):
                number, digits[j] = divmod(number, c)
            need(number == 0, 'complete base-c address')
            output.extend(prefix)
            output.extend(field(min(3, (1 << Q) - 1), digits))
    return hashlib.sha256(old).hexdigest(), hashlib.sha256(output).hexdigest()


def measured_audit(root):
    for name, digest in PINS.items():
        path = root / 'source' / name
        need(not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == digest,
             'frozen source bytes: ' + name)
    data = json.loads((root / 'RESULT.json').read_bytes(), object_pairs_hook=unique)
    need(isinstance(data, dict) and set(data) == {'schema_version', 'cases', 'scope'}, 'receipt root')
    need(type(data['schema_version']) is int and data['schema_version'] == 1, 'typed schema version')
    need(isinstance(data['cases'], list) and data['cases'], 'nonempty measured cases')
    for case in data['cases']:
        need(set(case) == {'config', 'original', 'shared_radix', 'saved_residue_actions'}, 'paired case schema')
        config = case['config']
        need(set(config) == {'name', 'd', 'q', 'w', 'B', 'h', 'Q', 'I'}, 'parameter schema')
        need(all(type(config[k]) is int for k in config if k != 'name'), 'typed fixture parameters')
        need(config['w'] >= 1 and isinstance(config['name'], str), 'fixture exponent and name')
        parameters = {k: config[k] for k in ('d', 'q', 'B', 'h', 'Q', 'I')}
        parameters['modulus'] = config['q'] ** config['w']
        parameters['L'] = parameters['modulus'].bit_length() + 1
        formula = invoice(**parameters)
        geometry = formula['geometry']
        expected_geometry = {'M': geometry['M'], 'modulus': parameters['modulus'],
                             'cap': geometry['c'], 'H': geometry['H'], 'L': parameters['L'],
                             'F': geometry['F'], 'old_body': geometry['old_symbols'],
                             'output_body': geometry['output_symbols']}
        input_hash, output_hash = fixture_bytes(dict(parameters, c=geometry['c']))
        for label, shared in (('original', False), ('shared_radix', True)):
            measured = case[label]
            model = invoice(**parameters, shared=shared)
            need(measured['config'] == config and measured['candidate_shared_radix'] is shared,
                 'exact paired mode and parameters')
            for lane in ('record_tapes', 'residue_words', 'index_words'):
                actual = measured[lane]
                need(isinstance(actual, dict) and set(actual) == {'reads', 'writes', 'moves'}
                     and all(type(value) is int for value in actual.values()), 'typed action lane')
                need(model[lane] == actual, 'complete measured action lane: ' + label + ':' + lane)
            need(all(type(value) is int for value in measured['geometry'].values()) and
                 expected_geometry == measured['geometry'], 'complete geometry')
            need(model['additional_residue_peak'] == measured['additional_residue_peak'], 'numeric peak')
            need(measured['created_record_tapes'] == 5 + 2 * parameters['B'], 'all created record tapes')
            need(measured['odometer_advances'] == geometry['new_count'] and
                 measured['odometer_increment_visits'] == parameters['B'] * geometry['digit_increments_per_prefix'],
                 'complete odometer visits')
            need(measured['input_sha256'] == input_hash and measured['output_sha256'] == output_hash,
                 'complete independently serialized bytes')
            need(measured['returned_prefix_count'] == geometry['new_count'] and
                 measured['output_head'] == measured['expected_head'] == 1, 'returned count and heads')
            need(measured['all_borrowed_bytes_heads_preserved'] is True and
                 measured['all_scratch_cleared'] is True and
                 measured['runtime_word_decoding_used'] is False and
                 measured['full_source_stock_admitted'] is False, 'preservation/scope flags')
        need(case['saved_residue_actions'] == formula['saved_residue_actions'], 'exact saved actions')
    return len(data['cases'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=HERE)
    parser.add_argument('--parameters', type=str, help='explicit JSON parameters for formula inspection')
    args = parser.parse_args()
    controls()
    if args.parameters:
        print(json.dumps(invoice(**json.loads(args.parameters)), sort_keys=True))
    else:
        count = measured_audit(args.root)
        print('PASS_INDEPENDENT_DIRECTORY_PRODUCER fixtures=' + str(count)
              + ' paired_exact_actions_and_bytes no_full_stock_admission')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        import sys
        print('FAIL_INDEPENDENT_DIRECTORY_PRODUCER ' + str(error), file=sys.stderr)
        raise SystemExit(1)
