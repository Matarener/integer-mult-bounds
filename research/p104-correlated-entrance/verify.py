#!/usr/bin/env python3
"""Exact correlated P104 entrance rows and literal cancellation replay.

Nick Petalas. Apache-2.0. No predecessor executable is imported.
"""

import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

N = 512
BITS = 9
CUT = 2025
TARGETS = ('D31', 'D30', 'D29', 'D28', 'D27', 'Q7')
ZERO = (0, 0)
HASHES = {
    'WORD.json': 'cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50',
    'NATIVE.json.gz': 'ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d',
}
PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load_sources(root):
    values = []
    for name, expected in HASHES.items():
        path = root / 'research/p104-rounded-collector/inputs' / name
        need(path.is_file() and not path.is_symlink(), 'regular pinned source')
        with path.open('rb') as handle:
            raw = handle.read(4 * 1024 * 1024 + 1)
        need(len(raw) <= 4 * 1024 * 1024, 'source capacity')
        need(hashlib.sha256(raw).hexdigest() == expected, 'source digest ' + name)
        if name.endswith('.gz'):
            raw = gzip.decompress(raw)
            need(len(raw) <= 16 * 1024 * 1024, 'native expansion capacity')
        values.append(json.loads(raw))
    word, native = values
    need(len(word['program']) == 5398 and len(word['initial_frames']) == 358, 'literal word dimensions')
    return word, native


def producer_rows(word):
    program = word['program']
    needed, events = set(TARGETS), []
    for event in reversed(range(CUT)):
        row = program[event]
        if row[1] in needed:
            events.append(event)
            if row[0] == 'add':
                needed.add(row[2])
    events.reverse()
    need(len(events) == 257 and len(needed) == 58, 'producer cone dimensions')
    need(Counter(program[i][0] for i in events) == {'transport': 200, 'add': 57}, 'producer opcode counts')
    names = sorted(needed)
    rows = {name: {name: Fraction(1)} for name in names}
    frames = {name: word['initial_frames'][name][:] for name in names}
    need(all(frame == [] for frame in frames.values()), 'empty initial gauges')
    groups = {name: [] for name in TARGETS[:5]}
    for event in events:
        row = program[event]
        target = row[1]
        if row[0] == 'transport':
            need(frames[target] == row[2], 'chronological transport frame')
            frames[target] = row[3][:]
        else:
            need(row[0] == 'add', 'producer opcode')
            _, _, source, coefficient, frame = row
            need(frames[target] == frames[source] == frame, 'common ADD gauge')
            coefficient = Fraction(coefficient)
            for initial, value in rows[source].items():
                rows[target][initial] = rows[target].get(initial, Fraction(0)) + coefficient * value
            if source.startswith('Y'):
                need(target in groups and coefficient == Fraction(1, 4), 'quarter grouping')
                groups[target].append({'source': source, 'event': event})
            else:
                need(target == 'Q7' and source in TARGETS[:5] and coefficient == -1, 'query initial subtraction')
    validate_rows(rows, groups)
    need(all(frames[name] == [256, 136, 64, 40, 16, 4, 2, 1] for name in TARGETS[:5]), 'D cut frame')
    need(frames['Q7'] == [364], 'query cut frame')
    return {'events': events, 'dependencies': names, 'groups': groups,
            'rows': {name: {key: str(value) for key, value in sorted(rows[name].items()) if value}
                     for name in TARGETS}, 'final_frames': {name: frames[name] for name in TARGETS}}


def validate_rows(rows, groups):
    sources = [entry['source'] for group in groups.values() for entry in group]
    need(len(sources) == len(set(sources)) == 52, 'disjoint exhaustive Y partition')
    need([len(group) for group in groups.values()] == [3, 7, 7, 11, 24], 'group sizes')
    for target, group in groups.items():
        expected = {target: Fraction(1)}
        expected.update({entry['source']: Fraction(1, 4) for entry in group})
        need(rows[target] == expected, 'exact final D row')
    need(rows['Q7'] == {'Q7': Fraction(1), **{name: Fraction(-1) for name in TARGETS[:5]}}, 'query row')


def quotient_basis(groups):
    """An explicit integral change of coordinates and its two-sided inverse."""
    sources = sorted(entry['source'] for group in groups.values() for entry in group)
    index = {name: i for i, name in enumerate(sources)}
    forward = [[int(i == j) for j in range(52)] for i in range(52)]
    inverse = [row[:] for row in forward]
    pivots = []
    for group in groups.values():
        p = index[group[0]['source']]
        pivots.append(p)
        for entry in group[1:]:
            q = index[entry['source']]
            forward[p][q] = 1
            inverse[p][q] = -1
    for left, right in ((forward, inverse), (inverse, forward)):
        product = [[sum(left[i][k] * right[k][j] for k in range(52)) for j in range(52)] for i in range(52)]
        need(product == [[int(i == j) for j in range(52)] for i in range(52)], 'integral inverse')
    return {'source_order': sources, 'pivot_sources': [sources[i] for i in pivots],
            'forward_sha256': digest(forward), 'inverse_sha256': digest(inverse),
            'unrestricted_B9_coordinates': 47, 'four_B9_coordinates': 5,
            'quotient_cardinality_log2': 5 * 512 * 4}


def rotate(value, exponent):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def wrapper(values, raw):
    rows = raw['matrix_rows']
    need(len(rows) == len(raw['linear_Z4']) == len(raw['quadratic_rows']) == BITS, 'wrapper dimensions')
    out = [ZERO] * N
    used = set()
    for x in range(N):
        y = sum(((x & row).bit_count() % 2) << j for j, row in enumerate(rows)) ^ raw['offset']
        need(0 <= y < N and y not in used, 'wrapper bijection')
        used.add(y)
        phase = raw['phase']
        for j in range(BITS):
            if (x >> j) & 1:
                phase += raw['linear_Z4'][j]
                phase += 2 * (raw['quadratic_rows'][j] & x & ~((1 << (j + 1)) - 1)).bit_count()
        out[y] = rotate(values[x], phase)
    return out


def checked_pair(a, b):
    dr, di = a[0] - b[0], a[1] - b[1]
    sr, si = b[0] + dr // 2, b[1] + di // 2
    rr, ri = -di, dr
    low = sr - rr // 2, si - ri // 2
    literal = ((low[0] + rr, low[1] + ri), low)
    numerator = ((a[0] + b[0] - di, a[1] + b[1] + dr),
                 (a[0] + b[0] + di, a[1] + b[1] - dr))
    need(all(v % 2 == 0 for z in numerator for v in z), 'ideal pair integral')
    ideal = tuple((z[0] // 2, z[1] // 2) for z in numerator)
    need(literal == ideal, 'signed floors equal exact ideal pair')
    return literal


def native_apply(values, recipe, counts):
    out = wrapper(values, recipe['right'])
    rank = recipe['rank']
    need(type(rank) is int and 1 <= rank <= BITS, 'positive native rank')
    for j in range(rank):
        for x in range(N):
            if not x & (1 << j):
                out[x], out[x | (1 << j)] = checked_pair(out[x], out[x | (1 << j)])
                counts['exact_pair_comparisons'] += 1
    counts['active_native_occurrences'] += 1
    return wrapper(out, recipe['left'])


def lattice_failure(values, scalar=1):
    if any(v % scalar for z in values for v in z):
        return {'reason': 'component scalar divisibility', 'scalar': scalar}
    coeffs = [(a // scalar, b // scalar) for a, b in values]
    for j in range(BITS):
        for x in range(N):
            if x & (1 << j):
                a, b = coeffs[x], coeffs[x ^ (1 << j)]
                coeffs[x] = a[0] - b[0], a[1] - b[1]
    for mask, coefficient in enumerate(coeffs):
        a, b = coefficient
        for degree in range(mask.bit_count()):
            if (a + b) % 2:
                return {'mask': mask, 'degree': mask.bit_count(), 'coefficient': coefficient,
                        'first_failed_pi_division': degree + 1}
            a, b = (a + b) // 2, (b - a) // 2
    return None


def bind_native(native):
    bound = {}
    for item in native['transports']:
        for event in item['events']:
            need(event not in bound and 0 <= event < 5398, 'native occurrence uniqueness')
            bound[event] = item
    need(len(bound) == 2070, 'all native occurrences')
    return bound


def add_event(state, row):
    _, target, source, coefficient, _ = row
    p, q = Fraction(coefficient).as_integer_ratio()
    need(all(p * x % q == 0 for z in state[source] for x in z), 'actual fractional ADD integral')
    increment = [(p * a // q, p * b // q) for a, b in state[source]]
    state[target] = [(a[0] + b[0], a[1] + b[1]) for a, b in zip(state[target], increment, strict=True)]


def replay(word, native, amplitudes):
    state = {name: [ZERO] * N for name in word['initial_frames']}
    frames = {name: frame[:] for name, frame in word['initial_frames'].items()}
    for name, amplitude in amplitudes.items():
        need(name in state and type(amplitude) is int and abs(amplitude) <= 256, 'fixture boundary')
        state[name][0] = (amplitude, 0)
    need(all(lattice_failure(x) is None for x in state.values()), 'all 358 initial B9 banks')
    outside = [name for name in amplitudes if lattice_failure(state[name], 4) is not None]
    bound, first = bind_native(native), None
    counts = Counter(exact_pair_comparisons=0, active_native_occurrences=0, native_occurrences=0, adds=0)
    for event in range(CUT):
        row = word['program'][event]
        op, target = row[:2]
        if op == 'transport':
            item = bound[event]
            need((item['old'], item['new'], item['recipe']['rank']) == (row[2], row[3], row[4]), 'native binding')
            need(frames[target] == row[2], 'full-prefix old frame')
            frames[target] = row[3][:]
            counts['native_occurrences'] += 1
            if any(z != ZERO for z in state[target]):
                state[target] = native_apply(state[target], item['recipe'], counts)
        elif op == 'add':
            need(frames[target] == frames[row[2]] == row[4], 'full-prefix ADD frame')
            add_event(state, row)
            counts['adds'] += 1
        elif op == 'sign':
            need(row[2] == '-1' and frames[target] == row[3], 'literal sign/frame')
            state[target] = [(-a, -b) for a, b in state[target]]
            counts['signs'] += 1
        else:
            raise ValueError('unexpected prefix opcode ' + op)
        if first is None:
            failure = lattice_failure(state[target])
            if failure is not None:
                first = {'event': event, 'bank': target, 'witness': failure}
    outputs = {name: {'sha256': digest(state[name]), 'in_B9': lattice_failure(state[name]) is None,
                      'nonzero_entries': sum(z != ZERO for z in state[name]), 'frame': frames[name]}
               for name in TARGETS}
    return {'initial_amplitudes': amplitudes, 'initial_Y_outside_4B9': outside,
            'first_non_B9_event_output': first, 'counts': dict(counts), 'outputs': outputs}


def calculate(root):
    word, native = load_sources(root)
    rows = producer_rows(word)
    basis = quotient_basis(rows['groups'])
    cancellation = replay(word, native, {'Y27': 64, 'Y26': -64})
    need(all(row['in_B9'] for row in cancellation['outputs'].values()), 'correlated final-cut admission')
    need(all(row['nonzero_entries'] == 0 for row in cancellation['outputs'].values()), 'six literal zero cut states')
    need(cancellation['initial_Y_outside_4B9'] == ['Y27', 'Y26'], 'strictly weaker correlated entrance')
    need(cancellation['first_non_B9_event_output']['event'] == 1090, 'actual intermediate failure')
    broken = replay(word, native, {'Y27': 64})
    need(not broken['outputs']['D31']['in_B9'], 'broken cancellation rejects')
    positive = replay(word, native, {'Y27': 256})
    need(all(row['in_B9'] for row in positive['outputs'].values()), 'independent stronger entrance control')
    need(positive['first_non_B9_event_output'] is None, 'stronger control entire prefix invariant')
    return {'schema_version': 1, 'source_hashes': HASHES, 'producer': rows, 'quotient_basis': basis,
            'literal_cancellation': cancellation, 'broken_cancellation': broken, 'stronger_control': positive}


def main():
    need(sys.argv[1:] in ([], ['--emit']), 'usage: verify.py [--emit]')
    result = calculate(PACKAGE.parents[1])
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / 'RECEIPT.json').read_text())
        need(type(expected) is dict and digest(result) == digest(expected), 'complete receipt equality')
        print('PASS_P104_CORRELATED_ENTRANCE five_congruences literal_full_prefix_cancellation')


if __name__ == '__main__':
    main()
