"""Sharp source-local Newton entrance for the frozen P104 word. Apache-2.0."""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BITS = 9
SIZE = 1 << BITS
ZERO = ((0, 0),) * SIZE


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.is_file() and path.stat().st_size <= 4_000_000, 'input capacity')
    return json.loads(path.read_text(encoding='utf-8'))


def sources(root):
    for pin in read_json(HERE / 'SOURCES.json')['files']:
        if pin['usage'] == 'input':
            data = (root / pin['path']).read_bytes()
            require(len(data) <= 4_000_000, 'source byte capacity')
            require(hashlib.sha256(data).hexdigest() == pin['sha256'],
                    'source SHA256: ' + pin['path'])
    source = root / 'research/p104-rounded-collector'
    word = read_json(source / 'inputs/WORD.json')
    raw = gzip.decompress((source / 'inputs/NATIVE.json.gz').read_bytes())
    require(len(raw) <= 4_000_000, 'native expansion capacity')
    archive = json.loads(raw)
    require(len(word['program']) == 5398 and len(word['initial_frames']) == 358,
            'literal word dimensions')
    require(len(archive['transports']) == 1245, 'native inventory')
    return word, archive


def span(frame):
    require(len(frame) <= BITS, 'frame capacity')
    values = {0}
    for bit in frame:
        require(type(bit) is int and 0 < bit < SIZE and bit not in values,
                'independent binary frame')
        values |= {x ^ bit for x in values}
    return values


def plan(record):
    require(set(record) == {'matrix_rows', 'offset', 'phase',
                            'linear_Z4', 'quadratic_rows'}, 'wrapper alphabet')
    rows, linear, quadratic = (record[k] for k in
                               ('matrix_rows', 'linear_Z4', 'quadratic_rows'))
    require(len(rows) == len(linear) == len(quadratic) == BITS, 'wrapper size')
    require(all(type(x) is int and 0 <= x < SIZE for x in rows + quadratic),
            'binary wrapper coefficients')
    require(all(type(x) is int and 0 <= x < 4 for x in linear), 'phase degree')
    require(type(record['offset']) is int and 0 <= record['offset'] < SIZE,
            'affine offset')
    require(type(record['phase']) is int and 0 <= record['phase'] < 4,
            'global phase')
    result = []
    for x in range(SIZE):
        y = record['offset'] ^ sum(((row & x).bit_count() % 2) << j
                                  for j, row in enumerate(rows))
        phase = record['phase'] + sum(linear[j] for j in range(BITS) if x >> j & 1)
        phase += 2 * sum((quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
                         for j in range(BITS) if x >> j & 1)
        result.append((y, phase % 4))
    require(len({y for y, _ in result}) == SIZE, 'invertible affine wrapper')
    return tuple(result)


def bind(word, archive):
    uses, wrapper_count = {}, 0
    for item in archive['transports']:
        recipe = item['recipe']
        require(set(recipe) == {'rank', 'left', 'right'}, 'native factorization')
        require(type(recipe['rank']) is int and 1 <= recipe['rank'] <= BITS,
                'native rank')
        left, right = plan(recipe['left']), plan(recipe['right'])
        wrapper_count += 2
        require(1 <= len(item['events']) <= 5398, 'occurrence capacity')
        for index in item['events']:
            require(type(index) is int and 0 <= index < 5398 and index not in uses,
                    'unique native event')
            event = word['program'][index]
            require(event == ['transport', event[1], item['old'], item['new'],
                              recipe['rank']], 'native occurrence binding')
            uses[index] = (recipe['rank'], left, right)
    expected = {i for i, e in enumerate(word['program']) if e[0] == 'transport'}
    require(set(uses) == expected, 'complete native event coverage')
    return uses, wrapper_count


def pi_valuation(value):
    require(value != 0, 'nonzero rational coefficient')
    numerator, denominator = abs(value.numerator), value.denominator
    require(denominator & (denominator - 1) == 0, 'dyadic denominator')
    return 2 * ((numerator & -numerator).bit_length() - 1
                - (denominator.bit_length() - 1))


def scalar_step(event, rows, frames):
    op, target = event[:2]
    require(op in {'add', 'transport', 'sign', 'zero', 'erase'}, 'event alphabet')
    if op == 'zero':
        require(target == 'C' and target not in rows, 'owned private allocation')
        rows[target], frames[target] = {}, event[2]
    elif op == 'erase':
        require(target == 'C' and not rows[target] and frames[target] == event[2],
                'exact private erasure')
        del rows[target], frames[target]
    elif op == 'transport':
        _, _, old, new, rank = event
        a, b = span(old), span(new)
        require(frames[target] == old and (a < b or b < a), 'nested native frames')
        require(rank == abs(len(old) - len(new)), 'frame rank')
        frames[target] = new
    elif op == 'sign':
        require(event[2] == '-1' and frames[target] == event[3], 'signed frame')
        rows[target] = {s: -v for s, v in rows[target].items()}
    else:
        _, _, source, coefficient, frame = event
        require(source != target and frames[target] == frames[source] == frame,
                'common ADD frame')
        coefficient = Fraction(coefficient)
        require(coefficient in {Fraction(x, y) for x in (-2, -1, 1, 2)
                                for y in (1, 2, 4)}, 'scalar alphabet')
        for initial_source, value in rows[source].items():
            result = rows[target].get(initial_source, Fraction(0)) + coefficient * value
            if result:
                rows[target][initial_source] = result
            else:
                rows[target].pop(initial_source, None)


def source_certificate(word):
    initial = word['initial_frames']
    require(Counter(s[0] for s in initial) ==
            {'X': 104, 'Y': 104, 'N': 78, 'D': 32, 'G': 32, 'Q': 8},
            'public role inventory')
    for frame in initial.values():
        span(frame)
    rows = {s: {s: Fraction(1)} for s in initial}
    frames, exponents, witnesses = dict(initial), dict.fromkeys(initial, 0), {}
    visits, erasures = 0, []
    for index, event in enumerate(word['program']):
        scalar_step(event, rows, frames)
        if event[0] == 'erase':
            erasures.append(index)
            continue
        for source, value in rows[event[1]].items():
            visits += 1
            needed = max(0, -pi_valuation(value))
            if needed > exponents[source]:
                exponents[source] = needed
                witnesses[source] = {'event': index, 'target': event[1],
                                     'coefficient': str(value)}
    require(frames == word['final_frames'] and len(erasures) == 8,
            'complete final frames and erasures')
    for target, row in rows.items():
        if target.startswith('X'):
            require(row.get(target) == 1 and all(s == target or s.startswith('Y')
                                                for s in row), 'public shear')
        else:
            require(row == {target: Fraction(1)}, 'dirty public restoration')
    require(all(k == (4 if s.startswith('Y') else 2 if s.startswith('N') else 0)
                for s, k in exponents.items()), 'sharp source exponents')
    require(len(witnesses) == 182, 'all restricted sources have lower witnesses')
    return {'pi_exponents': exponents, 'first_witnesses': witnesses,
            'erasure_events': erasures, 'coefficient_visits': visits}


def reverse_witness(word, source, witness):
    """Backward adjoint trace, separate from forward symbolic row propagation."""
    weights = {witness['target']: Fraction(1)}
    for index in range(witness['event'], -1, -1):
        event = word['program'][index]
        op, target = event[:2]
        value = weights.get(target, Fraction(0))
        if op == 'zero':
            weights.pop(target, None)
        elif op == 'sign' and value:
            weights[target] = -value
        elif op == 'add' and value:
            src = event[2]
            weights[src] = weights.get(src, Fraction(0)) + Fraction(event[3]) * value
        elif op == 'erase':
            require(target not in weights, 'adjoint private lifetime')
    require(weights.get(source, 0) == Fraction(witness['coefficient']),
            'independent reverse witness coefficient')


def rotate(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def monomial(vector, mapping):
    if vector == ZERO:
        return vector
    result = list(ZERO)
    for x, (y, phase) in enumerate(mapping):
        result[y] = rotate(vector[x], phase)
    return tuple(result)


def butterfly(vector, bit, sign=1):
    if vector == ZERO:
        return vector
    result, width = list(vector), 1 << bit
    for x in range(SIZE):
        if x & width:
            continue
        a, b = vector[x]
        c, d = vector[x | width]
        numerators = (a - sign * b + c + sign * d,
                      b + sign * a + d - sign * c,
                      a + sign * b + c - sign * d,
                      b - sign * a + d + sign * c)
        require(all(v % 2 == 0 for v in numerators), 'exact native half')
        p, q, r, s = (v // 2 for v in numerators)
        # Tekalign/PR3025 signed-floor pair, compared at every actual pair.
        difference = (a - c, b - d)
        middle = (c + difference[0] // 2, d + difference[1] // 2)
        difference = rotate(difference, sign)
        second = (middle[0] - difference[0] // 2,
                  middle[1] - difference[1] // 2)
        first = (second[0] + difference[0], second[1] + difference[1])
        require((first, second) == ((p, q), (r, s)), 'signed-floor ideal equality')
        result[x], result[x | width] = (p, q), (r, s)
    return tuple(result)


def encode(coefficients):
    result = list(coefficients)
    for bit in range(BITS):
        for x in range(SIZE):
            if not x >> bit & 1:
                a, b = result[x]
                c, d = result[x | (1 << bit)]
                result[x | (1 << bit)] = (a + c - d, b + c + d)
    return tuple(result)


def member(vector):
    if vector == ZERO:
        return vector
    result = list(vector)
    for bit in range(BITS - 1, -1, -1):
        for x in range(SIZE):
            if not x >> bit & 1:
                a, b = result[x]
                c, d = result[x | (1 << bit)]
                u, v = c - a, d - b
                require((u + v) % 2 == (v - u) % 2 == 0, 'Newton membership')
                result[x | (1 << bit)] = ((u + v) // 2, (v - u) // 2)
    return tuple(result)


def chart(vector, frame, inverse=False):
    """Canonical Delta chart formula retained from the credited P104 sources."""
    if not frame:
        return vector
    rank = len(frame)
    if rank != BITS:
        columns, space = [], {0}
        for candidate in tuple(frame) + tuple(1 << j for j in range(BITS)):
            if candidate not in space:
                columns.append(candidate)
                space |= {x ^ candidate for x in space}
        permutation = []
        for x in range(SIZE):
            y = 0
            for bit in range(BITS):
                if x >> bit & 1:
                    y ^= columns[bit]
            permutation.append(y)
        back = [0] * SIZE
        for x, y in enumerate(permutation):
            back[y] = x
        basis = [back[1 << bit] for bit in range(BITS)]
        quadratic = [(1 << bit) ^ sum(((a & b).bit_count() % 2) << j
                                     for j, b in enumerate(basis))
                     for bit, a in enumerate(basis)]
        phases = []
        for x in range(SIZE):
            phase = sum((quadratic[j] >> j) & 1 for j in range(BITS) if x >> j & 1)
            phase += 2 * sum((quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
                             for j in range(BITS) if x >> j & 1)
            phases.append(phase % 4)
        vector = monomial(vector, tuple((back[x], phases[x]) for x in range(SIZE)))
    for bit in range(rank):
        vector = butterfly(vector, bit, 1 if inverse else -1)
    if rank != BITS:
        vector = monomial(vector, tuple((permutation[x], -phases[permutation[x]])
                                       for x in range(SIZE)))
    return vector


def endpoint_oracle(word, initial):
    rows = {s: {s: Fraction(1)} for s in word['initial_frames']}
    frames = dict(word['initial_frames'])
    for event in word['program']:
        scalar_step(event, rows, frames)
    logical = {s: chart(v, word['initial_frames'][s], inverse=True)
               for s, v in initial.items()}
    expected = {}
    for name, row in rows.items():
        value = list(ZERO)
        for source, coefficient in row.items():
            for x, (a, b) in enumerate(logical[source]):
                require(a * coefficient.numerator % coefficient.denominator == 0
                        and b * coefficient.numerator % coefficient.denominator == 0,
                        'oracle exact scalar coefficient')
                c, d = value[x]
                value[x] = (c + a * coefficient.numerator // coefficient.denominator,
                            d + b * coefficient.numerator // coefficient.denominator)
        expected[name] = chart(tuple(value), frames[name])
    return expected


def physical_step(event, index, states, uses):
    op, target = event[:2]
    if op == 'transport':
        rank, left, right = uses[index]
        vector = monomial(states[target], right)
        member(vector)
        for bit in range(rank):
            vector = butterfly(vector, bit)
            member(vector)
        states[target] = monomial(vector, left)
    elif op == 'add':
        q = Fraction(event[3])
        result = []
        for (a, b), (c, d) in zip(states[target], states[event[2]], strict=True):
            require(c * q.numerator % q.denominator == 0
                    and d * q.numerator % q.denominator == 0, 'exact scalar division')
            result.append((a + c * q.numerator // q.denominator,
                           b + d * q.numerator // q.denominator))
        states[target] = tuple(result)
    elif op == 'sign':
        states[target] = tuple((-a, -b) for a, b in states[target])
    elif op == 'zero':
        require(target not in states, 'physical private allocation')
        states[target] = ZERO
    else:
        require(op == 'erase' and states[target] == ZERO, 'physical exact erasure')
        del states[target]


def full_fixture(word, uses, certificate):
    initial = {}
    for ordinal, name in enumerate(word['initial_frames']):
        scale = 1 << (certificate['pi_exponents'][name] // 2)
        coefficients = tuple((scale * (((x * 17 + ordinal * 11) % 7) - 3),
                              scale * (((x * 13 + ordinal * 7) % 11) - 5))
                             for x in range(SIZE))
        initial[name] = encode(coefficients)
    states = dict(initial)
    peak, checked = 0, 0
    for index, event in enumerate(word['program']):
        physical_step(event, index, states, uses)
        if event[0] != 'erase':
            vector = states[event[1]]
            member(vector)
            component_maximum = max(abs(v) for pair in vector for v in pair)
            peak = max(peak, component_maximum)
            checked += 1
    expected = endpoint_oracle(word, initial)
    require(states == expected, 'complete physical endpoint including changed frames')
    require('C' not in states and len(states) == 358, 'complete public endpoint')
    return {'dirty_inputs': 358, 'checked_event_outputs': checked,
            'peak_stored_component': peak, 'private_erasures': 8,
            'matched_public_outputs': len(expected)}


def lower_fixtures(word, uses, certificate):
    """Literal single-source failures require no chart-covariance assumption."""
    failures = {}
    for source, witness in certificate['first_witnesses'].items():
        value = (1, 0)
        for _ in range(certificate['pi_exponents'][source] - 1):
            a, b = value
            value = (a - b, a + b)
        states = dict.fromkeys(word['initial_frames'], ZERO)
        states[source] = (value,) * SIZE
        rejected = False
        for index in range(witness['event'] + 1):
            event = word['program'][index]
            try:
                physical_step(event, index, states, uses)
                if event[0] != 'erase':
                    member(states[event[1]])
            except ValueError as error:
                require(str(error) in {'Newton membership', 'exact scalar division',
                                       'exact native half'}, 'lower fixture failure reason')
                failures[source] = {'event': index, 'reason': str(error)}
                rejected = True
                break
        require(rejected, 'weaker actual source domain admitted: ' + source)
    return failures


def controls(word, certificate):
    failures = 0
    for source, witness in certificate['first_witnesses'].items():
        reverse_witness(word, source, witness)
        exponent = certificate['pi_exponents'][source]
        require(pi_valuation(Fraction(witness['coefficient'])) + exponent == 0,
                'sharp rational denominator witness')
        require(pi_valuation(Fraction(witness['coefficient'])) + exponent - 1 < 0,
                'one pi less fails the product criterion')
        failures += 1
    bad = list(ZERO)
    bad[0] = (1, 0)
    try:
        member(tuple(bad))
    except ValueError:
        pass
    else:
        raise ValueError('non-Newton unit array admitted')
    return {'reverse_source_witnesses': failures, 'nonmember_control': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args()
    word, archive = sources(args.repo.resolve())
    uses, wrappers = bind(word, archive)
    certificate = source_certificate(word)
    receipt = {'certificate': certificate, 'native_events': len(uses),
               'wrapper_records': wrappers, 'controls': controls(word, certificate)}
    receipt['full_fixture'] = full_fixture(word, uses, certificate)
    receipt['full_fixture']['native_prefix_checks'] = sum(r + 2 for r, _, _ in uses.values())
    receipt['weakened_source_failures'] = lower_fixtures(word, uses, certificate)
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    else:
        require(receipt == read_json(HERE / 'RECEIPT.json'), 'complete receipt equality')
    print(json.dumps({'status': 'PASS_P104_NEWTON_SOURCE_CONTRACT',
                      'restricted_sources': len(certificate['first_witnesses']),
                      'native_events': len(uses), 'wrapper_records': wrappers,
                      'full_fixture': receipt.get('full_fixture')}, sort_keys=True))


if __name__ == '__main__':
    main()
