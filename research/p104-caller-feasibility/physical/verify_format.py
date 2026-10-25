#!/usr/bin/env python3
"""Bounded, independent format transfer for the pinned PR3609 program.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
No predecessor executable is imported. This checks a scalar range certificate,
one actual 36-event dependency cone, and the required X0 endpoint. It is not
a whole-word numerical replay or a physical owner/controller certificate.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path

N = 512
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
HEAD = '13f974dae4af66027afb01f3ab42df9e830c2e90'
BASE = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
ROOT = Path(__file__).resolve().parent
PINS = {
    'research/p104-rounded-collector/inputs/WORD.json':
        'cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50',
    'research/p104-rounded-collector/inputs/NATIVE.json.gz':
        'ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d',
    'research/p104-inplace-entrance/PROGRAM.json':
        '608c5c66a6eb7af2fc75d32e2b353a8074a50ef0bdb848c7211c59f3b7a176e6',
    'research/p104-inplace-entrance/NATIVE.json':
        '795a8c4e096a42a2f2c5875c354a4d4b56515cf8ffdfd5767a82713cf7f84dbd',
}
LOCAL_FILES = dict(zip(PINS, ('WORD.json', 'ORIGINAL_NATIVE.json.gz',
                             'PR3609_PROGRAM.json', 'PR3609_NATIVE.json')))
DOCUMENT_PINS = {
    'inputs/PR3609_PROOF.md': 'e72a2a0a34ba1c3c226da1e99326ec14e2fb913a74788463bb7013aa8d4954af',
    'inputs/PR3382_PROOF.md': '1ca8c0e7e78f0f39de6cff7accc68ccd3901bfb50759bf7a2e2896bcf63bf081',
    'inputs/PR3416_PROOF.md': '0dc1c35158902299fc8748c8baf89205483562f041e9050580e6579c331ebeb5',
    'inputs/LICENSE': 'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4',
    'inputs/NOTICE': 'b49022cb4104d90b182e4c335f670faf45529025b15db77bf0291835083c28bd',
    'inputs/FRAME-SA504-NOTICE.md': 'a92f49c5ced455160fbedcc8954e3c9255e3605e88ad12ae5a84f1c4302986f1',
    'inputs/PR1862-NOTICE.md': 'd86f31a4c0bafd4271fe0c0e087a7fc1cd72d5b705e3739c4ba3e9241b7ba3f9',
    'inputs/PR1972-NOTICE.md': '2d9c60fdeda14a8609f2b210fe0873ee0318788130637db9e5e79d487243ab7d',
    'inputs/NATIVE-LINEAGE-NOTICE': 'ee0c73ca35877aad0e0b6adc560a3881cb82276dba4cf2d4fc58cd19e57cc420',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def read_inputs(root):
    data = {}
    for path, expected in DOCUMENT_PINS.items():
        source = root / path
        need(source.is_file() and source.stat().st_size < 100_000,
             'missing or oversized documentary premise: ' + path)
        need(hashlib.sha256(source.read_bytes()).hexdigest() == expected,
             'documentary premise hash: ' + path)
    for path, expected in PINS.items():
        source = root / 'inputs' / LOCAL_FILES[path]
        need(source.is_file() and source.stat().st_size < 1_000_000,
             'missing or oversized pinned input: ' + path)
        raw = source.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected, 'input hash: ' + path)
        if path.endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as compressed:
                raw = compressed.read(4_000_001)
            need(len(raw) <= 4_000_000, 'native decompression limit')
        data[path] = json.loads(raw, object_pairs_hook=unique)
    word, old_native, program, new_native = data.values()
    need(len(word['program']) == 5398 and len(word['initial_frames']) == 358,
         'original fixed domain')
    need(len(program['program']) == 1238, 'new entrance length')
    kept = program['retained_original_event_indices']
    need(len(kept) == 4027 and kept == sorted(set(kept)), 'projection indices')
    return word, old_native, program, new_native


def add_row(left, right, coefficient):
    answer = dict(left)
    for name, value in right.items():
        answer[name] = answer.get(name, Fraction(0)) + coefficient * value
        if not answer[name]:
            del answer[name]
    return answer


def scale_row(row, coefficient):
    return {key: coefficient*value for key, value in row.items() if coefficient*value}


def row_mass(row):
    return sum(map(abs, row.values()), Fraction(0))


def combined_events(word, program, native):
    result = []
    for index, event in enumerate(program['program']):
        if event[0] == 'native':
            _, bank, which = event
            item = native['x_to_empty'][bank] if which == 'enter' else native['empty_to_full']
            event = ['transport', bank, item['old'], item['new'], item['recipe']['rank']]
        result.append((index, None, event))
    for offset, original in enumerate(program['retained_original_event_indices']):
        result.append((len(result), original, word['program'][original]))
    need(len(result) == 5265, 'combined fixed event count')
    return result


def scalar_step(rows, frames, event):
    op, target = event[:2]
    product = Fraction(0)
    if op == 'zero':
        need(target not in rows, 'private allocation aliases a live field')
        rows[target], frames[target] = {}, event[2]
    elif op == 'erase':
        need(rows[target] == {} and frames[target] == event[2], 'literal zero row')
        del rows[target], frames[target]
    elif op == 'transport':
        need(frames[target] == event[2], 'transport entrance frame')
        frames[target] = event[3]
    elif op == 'add':
        source, coefficient = event[2], Fraction(event[3])
        need(frames[target] == frames[source], 'ADD common frame')
        if len(event) == 5:
            need(frames[target] == event[4], 'source ADD frame binding')
        product = abs(coefficient)*row_mass(rows[source])
        rows[target] = add_row(rows[target], rows[source], coefficient)
    elif op in ('half', 'double'):
        rows[target] = scale_row(rows[target], Fraction(1, 2) if op == 'half' else 2)
        product = row_mass(rows[target])
    elif op == 'sign':
        need(event[2] == '-1' and frames[target] == event[3], 'sign binding')
        rows[target] = scale_row(rows[target], -1)
    else:
        raise ValueError('unknown source operation')
    return product


def dyadic_valuation(value):
    a, b = abs(value.numerator), value.denominator
    need(a > 0 and b & (b-1) == 0, 'nonzero dyadic coefficient')
    return (a & -a).bit_length()-b.bit_length()


def note_guard(row, frame, extra, initial, category, index, guard):
    for source, coefficient in row.items():
        factors = len(frame)+len(initial[source])+extra
        bits = max(0, (factors+1)//2-dyadic_valuation(coefficient))
        guard['term_visits'][category] += 1
        guard['by_category'][category] = max(guard['by_category'][category], bits)
        if bits > guard['maximum']:
            guard['maximum'] = bits
            guard['first_maximum'] = {'event': index, 'source': source,
                                      'coefficient': str(coefficient), 'C_factors': factors,
                                      'category': category}


def prefix_guard_before(rows, frames, event, initial, index, guard):
    op, target = event[:2]
    if op == 'transport':
        note_guard(rows[target], frames[target], event[4], initial,
                   'native_internal_prefix', index, guard)
    elif op == 'add':
        source, coefficient = event[2], Fraction(event[3])
        note_guard(scale_row(rows[source], coefficient), frames[source], 0, initial,
                   'scalar_product', index, guard)
    elif op in ('half', 'double'):
        coefficient = Fraction(1, 2) if op == 'half' else 2
        note_guard(scale_row(rows[target], coefficient), frames[target], 0, initial,
                   'scalar_product', index, guard)


def witness_prefix_binding(rows, frames, initial, roles):
    for name in roles:
        need(rows[name] == {name: Fraction(1)}, 'new prefix changes a witness input')
        need(frames[name] == initial[name], 'new prefix changes a witness input frame')
    return {'roles': sorted(roles), 'all_value_rows_identity': True,
            'all_frames_restored': True, 'prefix_events': 1238}


def row_trace(word, program, native):
    rows = {name: {name: Fraction(1)} for name in word['initial_frames']}
    frames = {name: list(frame) for name, frame in word['initial_frames'].items()}
    peak, peak_record, product_peak = Fraction(1), None, Fraction(0)
    counts, witness_inputs, prefix_binding = Counter(), cone(word, program)[1], None
    guard = {'maximum': 0, 'by_category': Counter(), 'term_visits': Counter()}
    for index, original, event in combined_events(word, program, native):
        op, target = event[:2]
        counts[op] += 1
        if index < 1238:
            prefix_guard_before(rows, frames, event, word['initial_frames'], index, guard)
        product_peak = max(product_peak, scalar_step(rows, frames, event))
        if target not in rows:
            continue
        if index < 1238:
            note_guard(rows[target], frames[target], 0, word['initial_frames'],
                       'complete_operation', index, guard)
        mass = row_mass(rows[target])
        if mass > peak:
            peak, peak_record = mass, {'event': index, 'original_event': original,
                                      'bank': target, 'operation': event}
        if index == 1237:
            prefix_binding = witness_prefix_binding(rows, frames, word['initial_frames'], witness_inputs)
    need(frames == word['final_frames'], 'all 358 final frames')
    need(len(rows) == 358 and counts['zero'] == counts['erase'] == 8, 'public/private return')
    denominators = sorted({v.denominator for row in rows.values() for v in row.values()})
    need(denominators == [1, 2], 'final half-integer scalar rows')
    need(peak == 103 and product_peak <= peak, 'complete scalar range bound')
    need(rows['X0'].get('Y2') == Fraction(-1, 2), 'required X0/Y2 coefficient')
    initial_dimension = max(map(len, word['initial_frames'].values()))
    final_dimension = max(map(len, frames.values()))
    need(initial_dimension == 1 and final_dimension == 9, 'endpoint C-factor count')
    need(prefix_binding is not None, 'missing source-return witness binding')
    need(guard['maximum'] == 6, 'standalone local six-bit upper bound')
    guard['by_category'] = dict(guard['by_category'])
    guard['term_visits'] = dict(guard['term_visits'])
    return rows, {'events': 5265, 'opcode_counts': dict(sorted(counts.items())),
                  'maximum_row_l1': str(peak), 'first_maximum': peak_record,
                  'maximum_scalar_product_l1': str(product_peak),
                  'endpoint_scalar_denominators': denominators,
                  'maximum_initial_frame_dimension': initial_dimension,
                  'maximum_final_frame_dimension': final_dimension,
                  'witness_inputs_after_new_prefix': prefix_binding,
                  'standalone_prefix_guard': guard,
                  'final_frames_sha256': digest(frames)}


def native_occurrences(word, archive):
    need(len(archive['transports']) == 1245, 'old recipe inventory')
    result = {}
    for record in archive['transports']:
        for event in record['events']:
            need(type(event) is int and event not in result, 'unique native occurrence')
            item = word['program'][event]
            need(item[0] == 'transport' and item[2:4] == [record['old'], record['new']],
                 'old/native frame binding')
            need(item[4] == record['recipe']['rank'], 'old/native rank binding')
            result[event] = record['recipe']
    need(len(result) == 2070, 'old native occurrence coverage')
    return result


def cone(word, program):
    kept = set(program['retained_original_event_indices'])
    live, selected = {'D18'}, []
    for index in range(2142, -1, -1):
        event = word['program'][index]
        if index not in kept or event[1] not in live:
            continue
        need(event[0] in ('transport', 'add'), 'unexpected witness dependency')
        selected.append(index)
        if event[0] == 'add':
            live.add(event[2])
    selected.reverse()
    need(len(selected) == 36 and len(live) == 9, 'minimal witness dependency size')
    need(2142 in kept and 1238 + program['retained_original_event_indices'].index(2142) == 3000,
         'sharp witness survives at combined event 3000')
    return selected, live


def phase(value, exponent):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def wrapper(values, record):
    output, covered = [(0, 0)]*N, set()
    need(len(record['matrix_rows']) == len(record['linear_Z4']) == len(record['quadratic_rows']) == 9,
         'native wrapper dimension')
    for x, value in enumerate(values):
        y = record['offset']
        for j, row in enumerate(record['matrix_rows']):
            y ^= ((row & x).bit_count() & 1) << j
        need(0 <= y < N and y not in covered, 'native wrapper permutation')
        covered.add(y)
        bits = [j for j in range(9) if (x >> j) & 1]
        exponent = record['phase'] + sum(record['linear_Z4'][j] for j in bits)
        exponent += 2*sum((record['quadratic_rows'][j] >> k) & 1
                          for j in bits for k in bits if j < k)
        output[y] = phase(value, exponent)
    return output


def literal_pair(a, b):
    dr, di = a[0]-b[0], a[1]-b[1]
    tr, ti = -di, dr
    numerators = (a[0]+b[0]+tr, a[1]+b[1]+ti,
                  a[0]+b[0]-tr, a[1]+b[1]-ti)
    if any(v % 2 for v in numerators):
        return None, {'input': [list(a), list(b)], 'twice_ideal': list(numerators)}
    mr, mi = b[0]+dr//2, b[1]+di//2
    second = (mr-tr//2, mi-ti//2)
    first = (second[0]+tr, second[1]+ti)
    expected = ((numerators[0]//2, numerators[1]//2),
                (numerators[2]//2, numerators[3]//2))
    need((first, second) == expected, 'signed-floor/ideal equality')
    return (first, second), None


def native(values, recipe, location, counts):
    if not any(a or b for a, b in values):
        counts['zero_native_calls'] += 1
        return values, None
    counts['active_native_calls'] += 1
    values = wrapper(values, recipe['right'])
    for bit in range(recipe['rank']):
        for low in range(N):
            if low & (1 << bit):
                continue
            pair, error = literal_pair(values[low], values[low | (1 << bit)])
            if error is not None:
                error.update({'event': location, 'bit': bit, 'address': low,
                              'kind': 'nonintegral_ideal_C_output'})
                return None, error
            values[low], values[low | (1 << bit)] = pair
            counts['completed_literal_pairs'] += 1
    return wrapper(values, recipe['left']), None


def expected_full_column(multiplier):
    answer = []
    for address in range(N):
        a, b = 1, 0
        for bit in range(9):
            sign = 1 if (address >> bit) & 1 else -1
            a, b = a-sign*b, b+sign*a
        real, imag = Fraction(multiplier*a, N), Fraction(multiplier*b, N)
        need(real.denominator == imag.denominator == 1, 'expected integral column')
        answer.append((int(real), int(imag)))
    return answer


def run_witness(word, program, occurrences, guard):
    selected, inputs = cone(word, program)
    values = {name: [(0, 0)]*N for name in inputs}
    values['Y2'] = [(1 << guard, 0)] + [(0, 0)]*(N-1)
    frames = {name: word['initial_frames'][name] for name in inputs}
    counts = Counter()
    for index in selected:
        event = word['program'][index]
        op, bank = event[:2]
        if op == 'transport':
            need(frames[bank] == event[2], 'witness native entrance')
            result, error = native(values[bank], occurrences[index], index, counts)
            if error:
                return {'guard': guard, 'status': 'REJECT', 'failure': error,
                        'counts': dict(counts), 'completed_cone_events': counts['events']}
            values[bank], frames[bank] = result, event[3]
        else:
            source, coefficient = event[2], Fraction(event[3])
            need(frames[bank] == frames[source] == event[4], 'witness ADD frames')
            increment = [(coefficient*a, coefficient*b) for a, b in values[source]]
            need(all(a.denominator == b.denominator == 1 for a, b in increment),
                 'witness quarter increment')
            values[bank] = [(a+int(c), b+int(d))
                            for (a, b), (c, d) in zip(values[bank], increment)]
        counts['events'] += 1
    expected = expected_full_column(-(1 << guard)//4)
    need(values['D18'] == expected and frames['D18'] == FULL, 'actual sharp D18 column')
    return {'guard': guard, 'status': 'PASS', 'counts': dict(counts),
            'D18_sha256': digest(values['D18']), 'D18_coordinate_0': list(values['D18'][0]),
            'original_event': 2142, 'combined_event': 3000}


def endpoint_probe(word, program, new_native, guard):
    coefficients = {name: Fraction(int(name == 'Y2')) for name in word['initial_frames']}
    at_finish = None
    for event in program['program']:
        op, bank = event[:2]
        if op == 'add':
            coefficients[bank] += Fraction(event[3])*coefficients[event[2]]
        elif op in ('half', 'double'):
            coefficients[bank] *= Fraction(1, 2) if op == 'half' else 2
        elif event == ['native', 'X0', 'finish']:
            at_finish = coefficients[bank]
    need(at_finish == Fraction(-1, 2) and coefficients['Y2'] == 1,
         'actual prelude restores Y2 and forms required X0')
    need(all('X0' not in event[1:3] for index in program['retained_original_event_indices']
             for event in [word['program'][index]]), 'projection cannot change X0')
    multiplier = -(1 << guard)//2
    values = [(multiplier, 0)] + [(0, 0)]*(N-1)
    counts = Counter()
    output, error = native(values, new_native['empty_to_full']['recipe'], 'X0_finish', counts)
    if guard == 5:
        need(error is not None, 'five-bit endpoint must reject')
        return {'guard': guard, 'status': 'REJECT', 'failure': error, 'counts': dict(counts)}
    need(error is None and output == expected_full_column(multiplier), 'new literal X0 endpoint')
    need(output[0] == (-2**(guard-6), 2**(guard-6)), 'sharp six-bit physical output')
    if guard == 7:
        need(all(a % 2 == b % 2 == 0 for a, b in output), 'final exact one-bit compression')
    return {'guard': guard, 'status': 'PASS', 'X0_coordinate_0': list(output[0]),
            'X0_sha256': digest(output), 'literal_counts': dict(counts)}


def primitive_controls():
    pair, error = literal_pair((-1, 0), (0, 1))
    need(error is None and pair == ((0, 0), (-1, 1)), 'negative odd floor witness')
    # Actually substitute truncation toward zero in both midpoint halves.
    trunc = lambda v: v//2 if v >= 0 else -((-v)//2)
    mr, mi = trunc(-1), 1+trunc(-1)
    second = (mr-trunc(1), mi-trunc(-1))
    wrong = ((second[0]+1, second[1]-1), second)
    need(wrong != pair, 'wrong signed-half control')
    maximum_ratio = Fraction(0)
    tested = 0
    for ar in range(-2, 3):
        for ai in range(-2, 3):
            for br in range(-2, 3):
                for bi in range(-2, 3):
                    a, b = (ar, ai), (br, bi)
                    answer, error = literal_pair(a, b)
                    if error:
                        continue
                    dr, di = ar-br, ai-bi
                    tr, ti = -di, dr
                    mr, mi = br+dr//2, bi+di//2
                    peak = max(map(abs, (dr, di, tr, ti, mr, mi, *answer[0], *answer[1])))
                    bound = max(map(abs, (*a, *b, *answer[0], *answer[1])))
                    need(peak <= 2*bound, 'literal scratch exceeds twice stored values')
                    if bound:
                        maximum_ratio = max(maximum_ratio, Fraction(peak, bound))
                    tested += 1
    return {'integral_signed_pairs_checked': tested,
            'maximum_temporary_over_stored_ratio': str(maximum_ratio),
            'wrong_signed_truncation_rejected': True}


def verify(root=ROOT):
    word, archive, program, new_native = read_inputs(root)
    rows, scalar = row_trace(word, program, new_native)
    occurrences = native_occurrences(word, archive)
    positive = run_witness(word, program, occurrences, 7)
    negative = run_witness(word, program, occurrences, 6)
    need(positive['status'] == 'PASS' and positive['D18_coordinate_0'] == [-1, 1],
         'seven-bit actual witness')
    need(negative['status'] == 'REJECT' and negative['failure']['event'] == 2142,
         'six-bit actual witness failure')
    selected, inputs = cone(word, program)
    result = {'schema_version': 1, 'status': 'PASS_PR3609_FORMAT_TRANSFER',
              'source_head': HEAD, 'canonical_base': BASE, 'input_sha256': PINS,
              'documentary_input_sha256': DOCUMENT_PINS,
              'scalar_range': scalar, 'sharp_guard_positive': positive,
              'sharp_guard_negative': negative,
              'endpoint': {str(g): endpoint_probe(word, program, new_native, g) for g in (5, 6, 7)},
              'witness_cone': {'events': selected, 'initial_roles': sorted(inputs),
                               'events_sha256': digest(selected)},
              'primitive_controls': primitive_controls(),
              'format': {'standalone_prefix_fractional_guard': 6,
                         'fractional_guard': 7, 'output_fractional_guard': 6,
                         'stored_component_factor': 3296, 'literal_scratch_factor': 6592,
                         'input_magnitude_bits_b': 'raw original-grid integer components use <=b magnitude bits',
                         'sufficient_signed_stored_bits': 'b+20',
                         'sufficient_signed_literal_scratch_bits': 'b+21',
                         'standalone_signed_stored_bits': 'b+19',
                         'standalone_signed_literal_scratch_bits': 'b+20'},
              'scope': 'New-word finite-format transfer and bounded witness; no physical caller, owner map, tape controller, recursive invoice or historical numerical replay.'}
    need(rows['X0']['Y2'] == Fraction(-1, 2), 'endpoint source survives until receipt')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--receipt', type=Path, default=Path(__file__).with_name('FORMAT_RESULT.json'))
    parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args()
    result = verify(args.root)
    rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write_receipt:
        with args.write_receipt.open('x', encoding='utf-8') as stream:
            stream.write(rendered)
    else:
        need(args.receipt.is_file() and args.receipt.stat().st_size <= 1_000_000,
             'missing or oversized expected receipt')
        expected = json.loads(args.receipt.read_bytes(), object_pairs_hook=unique)
        strict_equal(result, expected)
        print('PASS_PR3609_FORMAT_TRANSFER: local source range; sharp seven-bit full guard; '
              'sharp six-bit output; exact receipt; no paid physical caller')


def strict_equal(actual, expected, location='receipt'):
    need(type(actual) is type(expected), 'receipt type mismatch at ' + location)
    if isinstance(actual, dict):
        need(actual.keys() == expected.keys(), 'receipt keys at ' + location)
        for key in actual:
            strict_equal(actual[key], expected[key], location + '.' + key)
    elif isinstance(actual, list):
        need(len(actual) == len(expected), 'receipt length at ' + location)
        for index, value in enumerate(actual):
            strict_equal(value, expected[index], location + '[' + str(index) + ']')
    else:
        need(actual == expected, 'receipt value at ' + location)


if __name__ == '__main__':
    main()
