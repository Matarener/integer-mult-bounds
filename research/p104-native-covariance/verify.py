"""Independent exact native covariance certificate. Nick Petalas, Apache-2.0."""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BITS = 9
SIZE = 1 << BITS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def same_json(actual, expected):
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def identity(bits):
    require(type(bits) is int and 1 <= bits <= BITS, 'Pauli width')
    return tuple((0, 1 << j, 0) for j in range(bits)) + tuple(
        (0, 0, 1 << j) for j in range(bits))


def multiply(a, b):
    """P(p,x,z)|v> = i^p (-1)^(z.v) |v xor x>."""
    p, x, z = a
    q, u, v = b
    return ((p + q + 2 * (z & u).bit_count()) % 4, x ^ u, z ^ v)


def image(table, pauli):
    bits = len(table) // 2
    p, x, z = pauli
    require(0 <= p < 4 and 0 <= x < 1 << bits and 0 <= z < 1 << bits,
            'Pauli argument')
    result = (p, 0, 0)
    for j in range(bits):
        if x >> j & 1:
            result = multiply(result, table[j])
    for j in range(bits):
        if z >> j & 1:
            result = multiply(result, table[bits + j])
    return result


def compose(after, before):
    require(len(after) == len(before) and 2 <= len(after) <= 2 * BITS,
            'tableau dimensions')
    return tuple(image(after, p) for p in before)


def c_table(table, bit, sign):
    require(sign in (-1, 1) and 0 <= bit < len(table) // 2, 'C stage argument')
    mask = 1 << bit
    # C X C^-1 = X and C Z C^-1 = -Y = i^3 XZ.
    return tuple(((p + (3 if sign == 1 else 1)) % 4, x ^ mask, z)
                 if z & mask else (p, x, z) for p, x, z in table)


def inverse_mapping(mapping):
    require(2 <= len(mapping) <= SIZE and len(mapping) & (len(mapping) - 1) == 0,
            'monomial dimension')
    require({y for y, _ in mapping} == set(range(len(mapping))),
            'bijective monomial')
    require(all(type(p) is int and 0 <= p < 4 for _, p in mapping),
            'Gaussian unit phase')
    result = [None] * len(mapping)
    for x, (y, p) in enumerate(mapping):
        result[y] = (x, -p % 4)
    return tuple(result)


def monomial_table(mapping):
    """Infer each image, then check its action on EVERY computational column."""
    inverse = inverse_mapping(mapping)
    bits = len(mapping).bit_length() - 1
    result = []
    for _, x, z in identity(bits):
        v0 = inverse[0][0]
        out_x = mapping[v0 ^ x][0]
        out_p = (mapping[v0 ^ x][1] - mapping[v0][1]
                 + 2 * (z & v0).bit_count()) % 4
        out_z = 0
        for j in range(bits):
            v = inverse[1 << j][0]
            phase = (mapping[v ^ x][1] - mapping[v][1]
                     + 2 * (z & v).bit_count() - out_p) % 4
            require(phase in (0, 2), 'Pauli derivative parity')
            out_z |= (phase // 2) << j
        for v, (y, phase) in enumerate(mapping):
            require(mapping[v ^ x][0] == y ^ out_x, 'Pauli address identity')
            actual = (mapping[v ^ x][1] - phase + 2 * (z & v).bit_count()) % 4
            require(actual == (out_p + 2 * (out_z & y).bit_count()) % 4,
                    'Pauli phase identity')
        result.append((out_p, out_x, out_z))
    return tuple(result)


def wrapper(record):
    require(set(record) == {'matrix_rows', 'offset', 'phase', 'linear_Z4',
                            'quadratic_rows'}, 'wrapper fields')
    rows, linear, quadratic = (record[k] for k in
                               ('matrix_rows', 'linear_Z4', 'quadratic_rows'))
    require(len(rows) == len(linear) == len(quadratic) == BITS, 'wrapper width')
    require(all(type(x) is int and 0 <= x < SIZE for x in rows + quadratic),
            'binary wrapper coefficients')
    require(all(type(x) is int and 0 <= x < 4 for x in linear), 'linear phases')
    require(type(record['offset']) is int and 0 <= record['offset'] < SIZE,
            'wrapper offset')
    require(type(record['phase']) is int and 0 <= record['phase'] < 4,
            'wrapper scalar phase')
    result = []
    for x in range(SIZE):
        y = record['offset'] ^ sum(((row & x).bit_count() % 2) << j
                                  for j, row in enumerate(rows))
        phase = record['phase'] + sum(linear[j] for j in range(BITS) if x >> j & 1)
        phase += 2 * sum((quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
                         for j in range(BITS) if x >> j & 1)
        result.append((y, phase % 4))
    inverse_mapping(result)
    return tuple(result)


def span(frame):
    require(len(frame) <= BITS, 'frame capacity')
    values = {0}
    for column in frame:
        require(type(column) is int and 0 < column < SIZE and column not in values,
                'independent frame')
        values |= {x ^ column for x in values}
    return values


def chart(frame):
    """Delta = H^-1 (product C_j^-1) H, from binary frame columns."""
    span(frame)
    if len(frame) in (0, BITS):
        return tuple(('C', j, -1) for j in range(len(frame)))
    columns, space = [], {0}
    for v in tuple(frame) + tuple(1 << j for j in range(BITS)):
        if v not in space:
            columns.append(v)
            space |= {x ^ v for x in space}
    require(len(columns) == BITS, 'completed chart basis')
    addresses = []
    for x in range(SIZE):
        value = 0
        for j in range(BITS):
            if x >> j & 1:
                value ^= columns[j]
        addresses.append(value)
    back = [0] * SIZE
    for x, y in enumerate(addresses):
        back[y] = x
    dual_columns = tuple(back[1 << j] for j in range(BITS))
    gram = tuple((1 << j) ^ sum(((a & b).bit_count() % 2) << k
                               for k, b in enumerate(dual_columns))
                 for j, a in enumerate(dual_columns))
    mapping = []
    for x in range(SIZE):
        phase = sum((gram[j] >> j) & 1 for j in range(BITS) if x >> j & 1)
        phase += 2 * sum((gram[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
                         for j in range(BITS) if x >> j & 1)
        mapping.append((back[x], phase % 4))
    h = tuple(mapping)
    return (('M', h),) + tuple(('C', j, -1) for j in range(len(frame))) + (
        ('M', inverse_mapping(h)),)


def adjoint(program):
    result = []
    for gate in reversed(program):
        if gate[0] == 'M':
            result.append(('M', inverse_mapping(gate[1])))
        else:
            require(gate[0] == 'C', 'adjoint alphabet')
            result.append(('C', gate[1], -gate[2]))
    return tuple(result)


def program_table(program, monomial_cache, bits=BITS):
    require(len(program) <= 2 * BITS + 4, 'program capacity')
    result = identity(bits)
    for gate in program:
        if gate[0] == 'C':
            result = c_table(result, gate[1], gate[2])
        else:
            require(gate[0] == 'M', 'program alphabet')
            mapping = gate[1]
            if mapping not in monomial_cache:
                require(len(monomial_cache) < 5000, 'monomial cache capacity')
                monomial_cache[mapping] = monomial_table(mapping)
            result = compose(monomial_cache[mapping], result)
    return result


def rotate(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def c_vector(vector, bit, sign):
    result, mask = list(vector), 1 << bit
    for x in range(len(vector)):
        if not x & mask:
            a, b = vector[x]
            c, d = vector[x | mask]
            result[x] = (a - sign * b + c + sign * d,
                         b + sign * a + d - sign * c)
            result[x | mask] = (a + sign * b + c - sign * d,
                               b - sign * a + d + sign * c)
    return tuple(result)


def apply(program, vector, denominator=0):
    require(len(vector) <= SIZE and 0 <= denominator <= 4 * BITS,
            'vector capacity')
    for gate in program:
        if gate[0] == 'C':
            vector = c_vector(vector, gate[1], gate[2])
            denominator += 1
        else:
            require(gate[0] == 'M' and len(gate[1]) == len(vector),
                    'monomial vector dimensions')
            result = [(0, 0)] * len(vector)
            for x, (y, phase) in enumerate(gate[1]):
                result[y] = rotate(vector[x], phase)
            vector = tuple(result)
    require(denominator <= 4 * BITS, 'dyadic denominator capacity')
    return vector, denominator


def canonical_vector(value):
    vector, denominator = value
    for _ in range(denominator):
        if any(a % 2 or b % 2 for a, b in vector):
            break
        vector = tuple((a // 2, b // 2) for a, b in vector)
        denominator -= 1
    return vector, denominator


def equal_certificate(actual, expected, cache, bits=BITS):
    a = program_table(actual, cache, bits)
    b = program_table(expected, cache, bits)
    require(a == b, 'signed Pauli covariance mismatch')
    e0 = ((1, 0),) + ((0, 0),) * ((1 << bits) - 1)
    x = canonical_vector(apply(actual, e0))
    y = canonical_vector(apply(expected, e0))
    require(any(u or v for u, v in x[0]), 'nonzero anchor')
    require(x == y, 'exact global phase mismatch')
    return digest(a), digest(x)


def read_sources(root):
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    data = {}
    for pin in pins:
        if pin['usage'] == 'input':
            path = root / pin['path']
            require(path.is_file() and path.stat().st_size <= 4_000_000,
                    'source missing or over capacity: ' + pin['path'])
            raw = path.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == pin['sha256'],
                    'source SHA256: ' + pin['path'])
            data[path.name] = raw
    raw = gzip.decompress(data['NATIVE.json.gz'])
    require(len(raw) <= 4_000_000, 'native expansion capacity')
    return json.loads(data['WORD.json']), json.loads(raw)


def bind(word, archive):
    require(word['chart'] == archive['chart'] ==
            'Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)', 'canonical chart name')
    require(len(word['program']) == 5398 and len(word['initial_frames']) == 358,
            'literal word dimensions')
    require(len(archive['transports']) == 1245, 'native inventory')
    frames, uses = dict(word['initial_frames']), {}
    for item in archive['transports']:
        require(set(item) == {'old', 'new', 'events', 'recipe'}, 'native fields')
        a, b = span(item['old']), span(item['new'])
        require(a < b or b < a, 'strict nested frames')
        rank = item['recipe']['rank']
        require(type(rank) is int and rank == abs(len(item['old']) - len(item['new'])),
                'positive native rank')
        require(1 <= len(item['events']) <= 5398, 'occurrence capacity')
        for index in item['events']:
            require(type(index) is int and 0 <= index < 5398 and index not in uses,
                    'unique native occurrence')
            event = word['program'][index]
            require(event == ['transport', event[1], item['old'], item['new'], rank],
                    'occurrence recipe binding')
            uses[index] = item
    for index, event in enumerate(word['program']):
        op, target = event[:2]
        if op == 'transport':
            require(index in uses and frames[target] == event[2], 'live transport frame')
            frames[target] = event[3]
        elif op == 'zero':
            require(target == 'C' and target not in frames, 'owned allocation')
            frames[target] = event[2]
        elif op == 'erase':
            require(target == 'C' and frames[target] == event[2], 'erasure frame')
            del frames[target]
        elif op == 'add':
            require(frames[target] == frames[event[2]] == event[4], 'common ADD frame')
        else:
            require(op == 'sign' and frames[target] == event[3], 'sign frame')
    require(frames == word['final_frames'] and len(uses) == 2070,
            'complete native occurrence coverage')
    return uses


def recipe_program(recipe):
    require(set(recipe) == {'rank', 'left', 'right'}, 'recipe fields')
    rank = recipe['rank']
    require(type(rank) is int and 1 <= rank <= BITS, 'native rank')
    return (('M', wrapper(recipe['right'])),) + tuple(
        ('C', j, 1) for j in range(rank)) + (('M', wrapper(recipe['left'])),)


def census(word, archive):
    uses = bind(word, archive)
    charts, cache, rows = {}, {}, []
    for ordinal, item in enumerate(archive['transports']):
        for frame in (tuple(item['old']), tuple(item['new'])):
            if frame not in charts:
                require(len(charts) < 500, 'chart cache capacity')
                charts[frame] = chart(frame)
        actual = recipe_program(item['recipe'])
        expected = adjoint(charts[tuple(item['old'])]) + charts[tuple(item['new'])]
        tableau, anchor = equal_certificate(actual, expected, cache)
        rows.append({'record': ordinal, 'old': item['old'], 'new': item['new'],
                     'events': item['events'], 'rank': item['recipe']['rank'],
                     'signed_pauli_sha256': tableau, 'exact_anchor_sha256': anchor})
    profile = Counter(item['recipe']['rank'] for item in uses.values())
    return {'schema_version': 1, 'claim': 'all archived native maps equal canonical Delta changes',
            'recipes': len(rows), 'occurrences': len(uses), 'distinct_charts': len(charts),
            'pauli_generators_per_recipe': 2 * BITS, 'anchor_entries_per_recipe': SIZE,
            'occurrence_profile': {str(k): v for k, v in sorted(profile.items())},
            'rank_mass': sum(k * v for k, v in profile.items()),
            'distinct_monomial_maps_checked': len(cache), 'certificates': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args()
    word, archive = read_sources(args.root)
    receipt = census(word, archive)
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    else:
        require(same_json(receipt, json.loads(
            (HERE / 'RECEIPT.json').read_text(encoding='utf-8'))),
                'complete receipt mismatch')
    print('PASS_P104_NATIVE_COVARIANCE', receipt['recipes'], receipt['occurrences'],
          'rank_mass=' + str(receipt['rank_mass']))


if __name__ == '__main__':
    main()
