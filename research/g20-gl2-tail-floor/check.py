#!/usr/bin/env python3
"""Independent full-input interpreter; imports no census/predecessor code.

Charan/theon199 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, deque
from hashlib import sha1, sha256
from itertools import permutations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def xor_table(table, destination, source):
    return tuple(y ^ (((y >> source) & 1) << destination) for y in table)


def all_tables():
    """Enumerate every injective linear map by its four column images."""
    for columns in product(range(1, 16), repeat=4):
        values = [0]
        for column in columns:
            values += [x ^ column for x in values]
        if len(set(values)) == 16:
            yield tuple(values)


def full_input_distances():
    identity = tuple(range(16))
    distances = {identity: 0}
    todo = deque([identity])
    while todo:
        table = todo.popleft()
        for d in range(4):
            for s in range(4):
                if s == d:
                    continue
                nxt = xor_table(table, d, s)
                if nxt not in distances:
                    distances[nxt] = distances[table] + 1
                    todo.append(nxt)
    require(set(distances) == set(all_tables()), 'independent full GL4 domain')
    return distances


def table_from_rows(rows):
    return tuple(sum(((row & x).bit_count() % 2) << j for j, row in enumerate(rows))
                 for x in range(16))


def basis_table(a, b):
    # Independent block-diagonal S followed by the exchange R.
    out = []
    for x in range(16):
        lo, hi = x % 4, x // 4
        u = sum(((row & lo).bit_count() % 2) << i for i, row in enumerate(a))
        v = sum(((row & hi).bit_count() % 2) << i for i, row in enumerate(b))
        out.append(v + 4*u)
    return tuple(out)


def word_table(word, generators):
    table = tuple(range(16))
    for index in word:
        require(type(index) is int and 0 <= index < 12, 'truth-table gate index')
        d, s = generators[index]
        table = xor_table(table, d, s)
    return table


def candidate_check(cert, distances):
    bases = list(permutations((1, 2, 3), 2))
    expected = [(list(a), list(b)) for a in bases for b in bases]
    require([(c['A'], c['B']) for c in cert['candidates']] == expected,
            'truth-table complete candidates')
    histogram = Counter()
    for candidate in cert['candidates']:
        table = basis_table(candidate['A'], candidate['B'])
        require(word_table(candidate['word'], cert['generators']) == table,
                'truth-table candidate endpoint')
        require(candidate['cost'] == len(candidate['word']) == distances[table],
                'truth-table candidate cost')
        inverse = word_table(candidate['word'][::-1], cert['generators'])
        require(all(inverse[table[x]] == x and table[inverse[x]] == x for x in range(16)),
                'both arbitrary-input inverse compositions')
        histogram[candidate['cost']] += 1
    return dict(sorted(histogram.items()))


def source_check(controller, components):
    tested = 0
    for roles in components:
        positions = {r: i for i, r in enumerate(roles)}
        for side in ('left', 'right'):
            projected = []
            for op, d, s in controller['boundaries'][side + '_program']:
                if d in positions or s in positions:
                    require(d in positions and s in positions, 'truth-table isolated source')
                    projected.append((op, positions[d], positions[s]))
            for x in range(16):
                bits = [x >> i & 1 for i in range(4)]
                for op, d, s in projected:
                    if op == 'ADD':
                        bits[d] ^= bits[s]
                    else:
                        require(op == 'SWAP', 'truth-table source opcode')
                        bits[d], bits[s] = bits[s], bits[d]
                require(sum(b << i for i, b in enumerate(bits)) == (x >> 2) + 4*(x % 4),
                        'truth-table source exchange')
                tested += 1
    return tested


def main():
    raw = (HERE/'inputs/CONTROLLER.json').read_bytes()
    require(sha256(raw).hexdigest() ==
            '978536e852c0cfbc150f143e19d2cfddbb434bac6017d914974eb99f641593a8',
            'independent source SHA256')
    require(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() ==
            '73fa9f40a032f11dabf357eba69066fcf9bf0a02', 'independent source blob')
    cert = json.loads((HERE/'CERTIFICATE.json').read_bytes())
    require(cert['components'] == [[20, 21, 24, 25], [16, 17, 28, 29], [18, 19, 26, 27]],
            'independent component list')
    require(cert['generators'] == [[d, s] for d in range(4) for s in range(4) if d != s],
            'independent alphabet')
    distances = full_input_distances()
    require(len(cert['potential']) == len(distances) == 20160, 'independent potential size')
    represented = set()
    for state, d in cert['potential']:
        rows = [(state // (16**i)) % 16 for i in range(4)]
        table = table_from_rows(rows)
        require(table in distances and distances[table] == d, 'independent all-state distances')
        represented.add(table)
    require(represented == set(distances), 'independent potential coverage')
    histogram = candidate_check(cert, distances)
    require(histogram == {6: 2, 7: 8, 8: 24, 9: 2}, 'independent sharp histogram')
    source_inputs = source_check(json.loads(raw), cert['components'])
    # Deliberately wrong truth tables and an underpriced/omitted final XOR.
    controls = []
    for kind in ('endpoint', 'price', 'coverage'):
        bad = json.loads(json.dumps(cert))
        if kind == 'endpoint':
            bad['candidates'][0]['word'].pop()
        elif kind == 'price':
            bad['candidates'][0]['cost'] -= 1
        else:
            bad['candidates'].pop()
        try:
            candidate_check(bad, distances)
        except ValueError as error:
            expected = {'endpoint': 'truth-table candidate endpoint',
                        'price': 'truth-table candidate cost',
                        'coverage': 'truth-table complete candidates'}[kind]
            require(str(error) == expected, 'independent expected rejection')
            controls.append(kind)
        else:
            raise ValueError('independent control accepted')
    print(json.dumps(dict(status='PASS_INDEPENDENT_G20_GL2_TRUTH_TABLES',
                          states=len(distances), candidate_inputs=36*16,
                          source_inputs=source_inputs, candidate_cost_histogram=histogram,
                          negative_controls=controls), sort_keys=True))


if __name__ == '__main__':
    main()
